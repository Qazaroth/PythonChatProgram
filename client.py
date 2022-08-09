import socket
import base64
import threading

serverHost = "127.0.0.1"
serverPort = 5000

dcCommands = ["/dc", "/disconnect", "/bye"]

dataCache = []
endAllThreads = False
endBGThreads = False

def bgDataHandler(clientSocket : socket.socket):
    global endBGThreads, endAllThreads

    oldData = None

    while not endBGThreads and not endAllThreads:
        try:
            rawData = clientSocket.recv(2048).decode()

            data = base64.b64decode(rawData).decode()
            
            dataCache.append(data)
        except:
            pass

        if len(dataCache) > 0:
            data = dataCache[-1]

            dataList = data.split("::")

            isClient = dataList[0].lower() == "c"
            dataUsername = dataList[1]
            dataMsg = dataList[2]

            if oldData != data:
                print("{}: {}".format(dataUsername, dataMsg))
                oldData = data


def main():
    global endBGThreads, endAllThreads

    threads = []

    username = input("What's your username? ")

    oldData = None

    clientSocket = socket.socket()
    clientSocket.connect((serverHost, serverPort))
    clientSocket.setblocking(0)

    bgThread = threading.Thread(target=bgDataHandler, args=(clientSocket, ))
    
    threads.append(bgThread)

    for i in threads:
        i.start()

    while True:
        message = input(" -> ")
        lwrStripMsg = message.lower().strip()
        dataToSend = "{}::{}".format(username, serverHost)
        
        if lwrStripMsg in dcCommands:
            endBGThreads = True
            endAllThreads = True

            dataToSend += "::{}".format("/disconnect")
            encodedData = base64.b64encode(dataToSend.encode())

            clientSocket.send(encodedData)

            break
        
        dataToSend += "::{}".format(message)
        encodedData = base64.b64encode(dataToSend.encode())

        clientSocket.send(encodedData)
        # while message.lower().strip() != "bye":
        #     sendData = "{}::{}::{}".format(username, serverHost, message)
        #     clientSocket.send(sendData.encode())
        #     data = clientSocket.recv(2048).decode()

        #     print("Received from server: {}".format(data))

        #     message = input(" -> ")

    for i in threads:
        i.join()

    clientSocket.close()

if __name__ == "__main__":
    main()
    