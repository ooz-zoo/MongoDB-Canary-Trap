## About
### A very simple basic monitoring tool designed to detect potential ransomware-like activity targeting databases. It is based on several assumptions, therefore not highly efficient, but it serves as a starting point for building better solutions.

### The project focuses on identifying suspicious scans and alerting administrators before these scans escalate into full-blown attacks.

### The inspiration came from the increasing threat of ransomware attacks, which can compromise critical information in a short period of time. MongoDB Canary Trap acts as an early warning system, helping to mitigate risks and protect databases.

### But it still needs a lot of work in heuristics and understanding real world ransomware scanning patterns 

## Features
### 1) Real-Time Detection - Monitors changes to the last_accessed field in database documents. Tracks and logs suspicious activity instantly.

### 2) Decoy Generation - Utilizes Gemini to create realistic decoy documents that mislead attackers and flag malicious scans.

### 3) Live Alert Dashboard: Built with Rich library for terminal-based UI and Matplotlib for graphical visualizations. Displays real-time alerts and scan frequencies in an engaging and intuitive manner.

### 4) Dynamic Alerts: Includes actionable details such as collection name, document ID, timestamp, and attacker IP address.

## Technologies:
### MongoDB - Change Streams 
### Python - backend scripting
### Gemini - decoy generation
