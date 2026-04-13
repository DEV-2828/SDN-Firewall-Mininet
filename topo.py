from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

class FirewallTopo(Topo):
    """
    Custom SDN Topology for Firewall Project.
    
    Topology Design:
    - 1 Open vSwitch (s1) acting as the central firewall/forwarding device.
    - 4 Hosts (h1 to h4) connected in a star topology to the switch.
    - Each host has statically assigned MAC and IP addresses to make exact 
      rule matching (MAC/IP filtering) predictable in the Ryu controller.
    """
    def build(self):
        # Add a single OpenFlow switch to act as our SDN datapath
        s1 = self.addSwitch('s1')

        # Add 4 hosts with specific predictability for testing:
        # IPs are in the 10.0.0.0/24 subnet.
        # MACs are strictly assigned so MAC-based blocking works consistently.
        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/24')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip='10.0.0.2/24')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03', ip='10.0.0.3/24')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04', ip='10.0.0.4/24')

        # Connect all hosts to the switch (Star Topology)
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)

if __name__ == '__main__':
    # Set Mininet to output informative logs
    setLogLevel('info')
    
    # Initialize the custom topology
    topo = FirewallTopo()
    
    # Create the network:
    # - Using RemoteController to allow our external Ryu app to control the switch
    # - Default RemoteController connects to 127.0.0.1 on port 6653/6633 perfectly
    net = Mininet(topo=topo, controller=RemoteController, switch=OVSSwitch, build=True)
    
    # Start network and drop into the Mininet Command Line Interface (CLI)
    net.start()
    CLI(net)
    
    # Clean up the network safely when the user exits the CLI
    net.stop()
