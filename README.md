# Distributed-File-System
torrent like distributed file storage system across multiple machines

# P2P File Sharing System

Mid-term project for CST-8114

project team members    [Myo Thein Chit](https://github.com/myotheinchit) , 
                        [Htet Arkar Oo](https://github.com/10D0U) , 
                        [Khine Zin Nyunt](https://github.com/KhineZinNyunt) , 
                        [Paing Zay Khant](https://github.com/PaingZayK) , 
                        [Yell Swann Yee](https://github.com/yellswannyee) , 
                        [May Shun Lae Naing](https://github.com/mayshunlaenaing) , 

A distributed peer-to-peer (P2P) file sharing system implemented in Python. This project enables multiple clients (peers) and a central server (tracker) to share files efficiently and securely. The system emphasizes scalability and optimized file distribution.

---

## Features

- **Distributed File Sharing:** Files are divided into chunks, which peers can download simultaneously from multiple sources.
- **Central Tracker:** Tracks file chunks and peers that possess them, enabling efficient file discovery.
- **Persistent Connections:** Maintains stable connections between peers and the tracker for reliable communication.
- **Temporary Peer-to-Peer Connections:** Facilitates efficient chunk downloads without unnecessary long-term connections.
- **Dynamic Port Allocation:** Avoids port conflicts by allowing the operating system to assign ports dynamically.

---

## Architecture

1. **Central Tracker:**
   - Acts as a server to manage file and peer metadata.
   - Keeps track of available file chunks and their respective owners.

2. **Peers:**
   - Act as both clients (to request files) and servers (to share file chunks).
   - Connect to the tracker for registration and file sharing.

3. **File Chunking:**
   - Files are divided into chunks (e.g., 1MB each) for efficient transfer.
   - Chunk names follow the format `filename.chunk_number` (e.g., `example.txt.1`).

---

## System Workflow

1. **File Registration:**
   - A peer informs the tracker about the files it wants to share. The tracker updates its metadata with the file's chunk details.

2. **File Request:**
   - A peer requests a file from the tracker.
   - The tracker provides a list of peers that have the required file chunks.

3. **Chunk Download:**
   - The requesting peer downloads chunks from multiple peers simultaneously.

---

## Technologies Used

- **Programming Language:** Python
- **Networking:** `asyncio`, `StreamWriter`, and `StreamReader` for asynchronous communication.
- **Data Serialization:** JSON for metadata storage and transmission.
- **UI:** Desktop GUI built with CustomTkinter.

---

## Installation and Usage

### Prerequisites

- Python 3.8 or higher 
- No `requirements.txt` file is provided as the only package u need to install is CustomTkinter CTK , the rest is built in packages for python 

### Installation

1. Clone the repository:
   ```bash
   https://github.com/myotheinchit/Distributed-File-System.git
   
