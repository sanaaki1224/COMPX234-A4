 COMPX234 Assignment 4 - UDP File Transfer System

Student Info:
Name: Changyang Ding
Student ID: 20233006385
GitHub Repo: [https://github.com/sanaaki1224/COMPX234-A4](https://github.com/sanaaki1224/COMPX234-A4)


Description:

This project implements a reliable file transfer system using **UDP** in **Python** for Assignment 4 of COMPX234.

The system consists of:
 A **multi-threaded server** that listens for file download requests and sends files in blocks.
 A **sequential client** that reads a list of filenames and downloads them one by one from the server.

 File Structure:
COMPX234-A4/
├── Client/
│ └── UDPclient.py # Client code
│ └── files.txt # List of filenames to download
├── Server/
│ └── UDPserver.py # Server code
└── README.md # This file
