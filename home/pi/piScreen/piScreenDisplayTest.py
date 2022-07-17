#!/usr/bin/python
import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 28888  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(input("What soll ich senden? ").encode("utf-8"))
    print(s.recv(1024).decode("utf-8"))
    s.close()
