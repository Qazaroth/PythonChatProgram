import socket
import base64
import sys
import threading

from _thread import *

clients = []
threads = []

# data = conn.recv(2048).decode()
#         dataList = data.split("::")

#         username = dataList[0]
#         ip = dataList[1]
#         message = dataList[2]

def remove(connection):
    if connection in clients:
        connection.close()
        clients.remove(connection)

def broadcastToAll(msg):
    for c in clients:
        try:
            c.send(str(msg).encode())
        except:
            c.close()
            remove(c)

def broadcast(msg, conn):
    for c in clients:
        if c != conn:
            try:
                c.send(str(msg).encode())
            except:
                c.close()
                remove(c)

def clientThread(conn, addr):
    dcCommands = ["/dc", "/DC", "/Dc", "/dC", "/disconnect", "/Disconnect", "/bye", "/Bye"]
    while True:
        try:
            rawData = conn.recv(2048).decode()
            data = base64.b64decode(rawData).decode()

            dataList = data.split("::")

            username = dataList[0]
            ip = dataList[1]
            msg = dataList[2]
            #print(msg == "")

            if msg == "":
                sendData = base64.b64encode("".encode())
                conn.send(sendData)
            elif msg not in dcCommands:
                # print(data)
                print("{} ({}): {}".format(username, ip, msg))
                msgToSend = base64.b64encode("c::{}::{}".format(username, msg).encode())
                broadcast(msgToSend, conn)
            else:
                remove(conn)
                break
        except:
            continue

if __name__ == "__main__":
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.setblocking(0)

    if len(sys.argv) <= 2:
        print("Correct usage: script <IP address> <port>")
        exit()

    ipAddress = str(sys.argv[1])
    port = int(sys.argv[2])

    serverSocket.bind((ipAddress, port))
    serverSocket.listen(100)

    while True:
        try:
            conn, addr = serverSocket.accept()
            
            if conn not in clients:
                sendData = base64.b64encode("s::Server::Welcome to the chat room!".encode())
                conn.send(sendData)
                clients.append(conn)

                print("{}:{} connected.".format(addr[0], addr[1]))

                start_new_thread(clientThread, (conn, addr))
        except:
            broadcastToAll("")

    serverSocket.close()