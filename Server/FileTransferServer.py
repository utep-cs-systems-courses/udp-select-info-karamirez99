#! /usr/bin/env python3

from socket import *
from select import select

clients = {}
serverAddr = ("", 50001)  
serverSocket = socket(AF_INET, SOCK_DGRAM) # new datagram socket for communicating to an IP addr
serverSocket.bind(serverAddr)
serverSocket.setblocking(False)

  
class serverState:
    def __init__(self):
        self.file = None
        self.segmentNum = 0
        self.state = "newConnection"
        self.tries = 3

def getProtocol(socket):
    client = clients[socket]

    message, clientAddrPort = socket.recvfrom(2048)
    protocol = int.from_bytes(message[0:1], "little")
    fileName = message[1:].decode()

    if protocol == 0:
        socket.sendto(b"OK", clientAddrPort)
        client.state = "transferReceive"
        client.file = open(fileName, "wb")
    elif protocol == 1:
        #TODO Implement recv file
        pass
    else:
        print("ohno")
    

def fileTransfer(socket):
    client = clients[socket]
    state = client.state
    segmentNum = client.segmentNum
    file = client.file

    if state != "transferReceive":
        return

    message, clientAddrPort = socket.recvfrom(2048)
    isEnd = int.from_bytes(message[0:1], "little")
    segmentNumFrom = int.from_bytes(message[1:3], "little")

    if isEnd == 1:
        client.state = "done"
        socket.sendto(segmentNum.to_bytes(2, "little"), clientAddrPort)
        file.close()
        return

    if(segmentNumFrom != segmentNum):
        lastSent = segmentNum - 1
        socket.sendto(lastSent.to_bytes(2, "little"), clientAddrPort)
        #Ignore Invalid packets
    else:
        file.write(message[3:])
        socket.sendto(segmentNum.to_bytes(2, "little"), clientAddrPort)
        client.segmentNum += 1
        

def readData(socket):
    client = clients[socket]
    state = client.state
    segmentNum = client.segmentNum

    print(state)

    if state == "newConnection":
        getProtocol(socket)
    elif state == "transferReceive":
        fileTransfer(socket)
    elif state == "done":
        print(segmentNum)
        message, clientAddrPort = socket.recvfrom(2048)
        socket.sendto(segmentNum.to_bytes(2, "little"), clientAddrPort)
        

# map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

timeout = 3                     # select delay before giving up, in seconds

readSockFunc[serverSocket] = readData

print("ready to receive")
while 1:
  readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                list(writeSockFunc.keys()), 
                                                list(errorSockFunc.keys()),
                                                timeout)
  if not readRdySet and not writeRdySet and not errorRdySet:
    clientsToRemove = []
    for sock, status in clients.items():
        status.tries -= 1
        if status.tries <= 0:
            clientsToRemove.append(sock)
    for client in clientsToRemove:
        clients.pop(client)

    print("timeout: no events")
    
  for sock in readRdySet:
    if sock not in clients:
        clients[sock] =  serverState()
    clients[sock].tries = 3
    readSockFunc[sock](sock)
