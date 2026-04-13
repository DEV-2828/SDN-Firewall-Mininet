import datetime
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp

class ProjectFirewall(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectFirewall, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        
        # DEFINED FIREWALL RULES (Modify these for testing)
        self.blocked_ips = ["10.0.0.4"] # Block all traffic to/from h4
        self.blocked_macs = [("00:00:00:00:00:01", "00:00:00:00:00:03")] # Block h1 to h3
        self.blocked_ports = [80] # Block HTTP traffic

    def log_blocked_packet(self, src, dst, reason):
        """Append blocked packet events to a local log file with timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] BLOCKED: src={src}, dst={dst}, reason={reason}\n"
        with open("firewall_blocked.log", "a") as f:
            f.write(log_entry)
        self.logger.info("!! FIREWALL: %s", log_entry.strip())

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # Install table-miss flow entry (Priority 0)
        # This routes any unmatched packets to the Ryu controller so we can inspect them.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        inst = [datapath.ofproto_parser.OFPInstructionActions(
                datapath.ofproto.OFPIT_APPLY_ACTIONS, actions)]
        # Add idle_timeout and hard_timeout to prevent flow table bloating
        mod = datapath.ofproto_parser.OFPFlowMod(
                datapath=datapath, priority=priority,
                idle_timeout=idle_timeout, hard_timeout=hard_timeout,
                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)

        # 1. RULE-BASED FILTERING (LOGGING & DROP RULES)
        # We use Priority=10 for drop rules so they overrule standard forwarding rules (Priority=1).
        
        # Check MAC Rules
        if (eth.src, eth.dst) in self.blocked_macs:
            self.log_blocked_packet(eth.src, eth.dst, "MAC Rule Match")
            match = parser.OFPMatch(eth_src=eth.src, eth_dst=eth.dst)
            self.add_flow(datapath, 10, match, [], idle_timeout=60) # Install Drop Rule
            return

        # Check IP Rules
        if ip_pkt and (ip_pkt.src in self.blocked_ips or ip_pkt.dst in self.blocked_ips):
            blocked_target = ip_pkt.src if ip_pkt.src in self.blocked_ips else ip_pkt.dst
            self.log_blocked_packet(ip_pkt.src, ip_pkt.dst, f"IP Rule Match ({blocked_target})")
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst)
            self.add_flow(datapath, 10, match, [], idle_timeout=60) # Install Drop Rule
            return

        # Check TCP Port Rules (e.g. Block Port 80 HTTP)
        if ip_pkt and tcp_pkt and tcp_pkt.dst_port in self.blocked_ports:
            self.log_blocked_packet(ip_pkt.src, ip_pkt.dst, f"TCP Port Rule Match ({tcp_pkt.dst_port})")
            match = parser.OFPMatch(eth_type=0x0800, ip_proto=6, 
                                    ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst, 
                                    tcp_dst=tcp_pkt.dst_port)
            self.add_flow(datapath, 10, match, [], idle_timeout=60) # Install Drop Rule
            return

        # 2. NORMAL FORWARDING
        # Priority=1
        dst, src = eth.dst, eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        out_port = self.mac_to_port[dpid].get(dst, datapath.ofproto.OFPP_FLOOD)
        
        actions = [parser.OFPActionOutput(out_port)]
        if out_port != datapath.ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # Normal forwarding rules get an idle_timeout so they don't stay forever
            self.add_flow(datapath, 1, match, actions, idle_timeout=10)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)
