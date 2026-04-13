# SDN-Based Firewall using Mininet + Ryu Controller

**Student:** Devopam Pal (PES2UG24CS152)  
**Course:** Computer Networks (UE24CS252B)  

## Problem Statement
The objective of this project is to develop an SDN-based firewall using the Ryu Controller and Mininet. The firewall dynamically enforces traffic filtering based on specific rules (IP, MAC, and TCP port level). It actively monitors incoming packets and installs OpenFlow drop rules into the virtual switch for traffic that matches the blocked parameters, while allowing permitted traffic to flow normally. Validated outcomes and dropped packets are logged persistently.

## Topology Design
The simulation uses a custom Star Topology (`topo.py`) with:
*   1 Open vSwitch (`s1`) acting as the forwarding layer.
*   4 Hosts (`h1` - `h4`) with static MACs (Ending in 01 to 04) and IPs (`10.0.0.1/24` to `10.0.0.4/24`).

## Setup and Execution

### 1. Environment Setup
Due to Ryu's legacy dependencies, it requires Python 3.9. Use the following commands to install dependencies:
```bash
# Set up Python 3.9 Virtual Environment
python3.9 -m venv venv
source venv/bin/activate

# Install strictly compatible versions of Ryu and Eventlet
pip install setuptools==59.5.0
pip install eventlet==0.30.2
pip install ryu
```

### 2. Running the Firewall
Open two separate terminal windows.

**Terminal 1 (Ryu Controller):**
```bash
source venv/bin/activate
ryu-manager firewall.py
```

**Terminal 2 (Mininet):**
```bash
sudo python3 topo.py
```

## Firewall Rules & Expected Output

The `firewall.py` controller enforces the following rules at Priority 10 (overriding standard forwarding):

1.  **MAC Block (L2):** Blocks traffic between `h1` and `h3` (`00:00:00:00:00:01` ↔ `00:00:00:00:00:03`).
    *   *Expected:* `ping` between h1 and h3 fails.
2.  **IP Block (L3):** Blocks all traffic to/from `10.0.0.4` (`h4`).
    *   *Expected:* `ping` from anywhere to h4 fails, completely isolating it.
3.  **Port Block (L4):** Blocks HTTP traffic over TCP Port 80.
    *   *Expected:* Running a web server on `h1` and curling it from `h2` drops the connection.
4.  **Packet Logging:** All blocked packets trigger an isolated log entry saved to `firewall_blocked.log` with a timestamp and reason.

## Proof of Execution
*(Embed the screenshots of the Mininet `pingall` and the Ryu Controller logs here)*

*Replace these placeholders with your actual screenshot images.*
> ![Ryu Controller Logs](./images/controller_output.png)
> ![Mininet Pingall Output](./images/mininet_pingall.png)

## References
*   [Mininet Documentation](http://mininet.org/walkthrough/)
*   [Ryu SDN Framework](https://ryu.readthedocs.io/en/latest/) 
*   PES University Computer Networks Guidelines (UE24CS252B)
