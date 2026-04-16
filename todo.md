# SDN-Based Firewall – Project TODO List

**Student:** PES2UG24CS152 – Devopam Pal  
**Course:** Computer Networks (UE24CS252B)  
**Project:** SDN-Based Firewall using Mininet + Ryu Controller  

---

## 1. Environment Setup (from Installation Guide PDF & Best Practices)

### System Requirements
- [ ] Ensure Ubuntu VM (20.04 / 22.04) is running with sudo privileges & internet
- [ ] Update system: `sudo apt update && sudo apt upgrade -y`
- [ ] Install Mininet: `sudo apt install mininet -y`
- [ ] Install Open vSwitch: `sudo apt install openvswitch-switch -y`
- [ ] Install supporting tools: Wireshark, iperf (`sudo apt install wireshark iperf -y`)
- [ ] Verify Mininet works: `sudo mn` → `pingall` → `exit`
- [ ] Clean up any stale configs: `sudo mn -c`

### Python Virtual Environment Setup
*It is best practice to use a virtual environment so you do not corrupt global dependencies. Here is the workflow you need to follow:*
- [ ] Create the virtual environment: `python3 -m venv venv`
- [ ] Activate the virtual environment: `source venv/bin/activate` *(Note: you must do this in every new terminal you open before running Ryu)*
- [ ] Install Ryu Controller inside the venv: `pip install ryu`
- [ ] Track dependencies: When you install packages, save them using `pip freeze > requirements.txt`
- [ ] Use Git properly: Add the line `venv/` to a `.gitignore` file so you do not commit thousands of environment files to your repo.

---

## 2. Topology (`topo.py`) — (4 marks: Problem Understanding & Setup)

- [ ] Review current topology: single switch `s1` + 4 hosts (h1–h4)
- [ ] Add proper comments explaining topology design choices
- [ ] Add docstrings to `FirewallTopo` class
- [ ] Verify hosts have correct IPs (10.0.0.1–4) and MACs
- [ ] Confirm `RemoteController` connects to Ryu on the correct IP/port (default `127.0.0.1:6633`)

---

## 3. Firewall Controller (`firewall.py`) — (6 marks: SDN Logic & Flow Rules)

### 3a. Existing Logic – Review & Fix
- [ ] Review `packet_in` handler for correctness
- [ ] Verify MAC-based blocking works (h1 → h3 currently blocked)
- [ ] Verify IP-based blocking works (h4 currently blocked)
- [ ] Add TCP/port-based blocking logic (port 80 is defined but **not enforced** in `_packet_in_handler` — this is a bug)

### 3b. Enhancements Required
- [ ] **Fix missing port-blocking rule:** Add check for `tcp_pkt.dst_port in self.blocked_ports` and install a drop flow
- [ ] Add flow rule **priorities** explanation in comments (currently: miss=0, forward=1, block=10)
- [ ] Add **idle/hard timeouts** to flow rules where applicable
- [ ] Add **logging of blocked packets** — write blocked packet info (timestamp, src, dst, reason) to a log file
- [ ] Ensure modular, clean code with proper comments throughout

---

## 4. Testing & Validation — (6 marks: Functional Correctness)

### Scenario 1: Allowed vs. Blocked Traffic
- [ ] Start Ryu controller: `ryu-manager firewall.py` *(ensure your venv is activated!)*
- [ ] Start topology: `sudo python3 topo.py`
- [ ] **Test 1 – Allowed:** `h1 ping h2` → should succeed
- [ ] **Test 2 – IP Block:** `h1 ping h4` → should be blocked (h4 is in `blocked_ips`)
- [ ] **Test 3 – MAC Block:** `h1 ping h3` → should be blocked (h1→h3 MAC pair blocked)
- [ ] **Test 4 – Port Block:** `h1` runs HTTP server, `h2` tries `curl h1:80` → should be blocked
- [ ] **Test 5 – Allowed after block:** `h2 ping h3` → should succeed (not in any block list)

### Scenario 2: Normal vs. Failure Behaviour
- [ ] Demonstrate normal forwarding between allowed hosts
- [ ] Show what happens when the controller is disconnected (switch behaviour)
- [ ] Demonstrate the learning switch behaviour (MAC-to-port table)

---

## 5. Performance Observation & Analysis — (5 marks)

- [ ] **Latency:** Run `ping` between allowed hosts → record RTT values
- [ ] **Throughput:** Run `iperf` between h1 and h2 → record bandwidth
- [ ] **Flow Tables:** Dump flow tables using `sudo ovs-ofctl dump-flows s1` → capture output
- [ ] **Packet Stats:** Use `sudo ovs-ofctl dump-ports s1` → capture port statistics
- [ ] **Wireshark Capture:** Capture OpenFlow messages between controller and switch
- [ ] Interpret and explain all observed metrics clearly in documentation

---

> [!IMPORTANT]
> **REQUIRED FINAL DELIVERABLES**
> *The following MUST be produced and submitted to complete the project.*

## 6. Deliverable 1: GitHub Repository & Source Code
- [ ] **Create a Public GitHub Repository**
- [ ] **Clean Source Code:** Push your updated `firewall.py` and `topo.py`. Code must be modular and documented.
- [ ] **Dependency Tracking:** Push your `.gitignore` and `requirements.txt`.
- [ ] **Proof of Execution:** Include screenshots and logs in the repository (e.g., in a `docs/` folder). Must include Wireshark flow tables and Ping/iperf results.

## 7. Deliverable 2: README Documentation (On GitHub)
- [ ] **Problem Statement:** Explain the goal and objective of the SDN Firewall.
- [ ] **Setup/Execution steps:** Step-by-step instructions on creating the venv, installing dependencies, and running Mininet/Ryu.
- [ ] **Expected Output:** Outline what traffic is blocked/allowed and why.
- [ ] **Inline Images:** Embed the Proof of Execution screenshots directly in the README.
- [ ] **References:** Cite all sources clearly.

## 8. Deliverable 3: Live Demonstration & Viva (4 marks)
- [ ] **Functional Correctness:** Execute the live demo in Mininet showing allowed vs blocked traffic.
- [ ] **Understanding:** Explain controller-switch interaction, OpenFlow protocols, and flow rules (match + action logic).
- [ ] **Validation:** Be able to modify a rule on the spot and demonstrate its effect. Provide answers clearly to viva questions.

---

## Evaluation Summary (Total: 25 marks)

| Component | Marks | Status |
|---|---|---|
| 1. Problem Understanding & Setup | 4 | [ ] |
| 2. SDN Logic & Flow Rule Implementation | 6 | [ ] |
| 3. Functional Correctness (Demo) | 6 | [ ] |
| 4. Performance Observation & Analysis | 5 | [ ] |
| 5. Explanation, Viva & Validation | 4 | [ ] |
| **Total** | **25** | |
