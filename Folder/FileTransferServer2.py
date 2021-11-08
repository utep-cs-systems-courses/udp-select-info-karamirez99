#! /usr/bin/env python3
# udp demo -- simple select-driven uppercase server

# Eric Freudenthal with mods by Adrian Veliz

import sys
from socket import *
from select import select

file = None
segmentNum = 0
state = "newConnection"
serverAddr = ("", 50000)  
serverSocket = socket(AF_INET, SOCK_DGRAM) # new datagram socket for communicating to an IP addr
serverSocket.bind(serverAddr)
serverSocket.setblocking(False)

  
def getProtocol(socket):
    global state
    global file
    message, clientAddrPort = socket.recvfrom(2048)
    protocol = int.from_bytes(message[0:1], "little")
    fileName = message[1:].decode()
    if protocol == 0:
        socket.sendto(b"OK", clientAddrPort)
        state = "transferReceive"
        file = open(fileName, "w")
    elif protocol == 1:
        #TODO Implement recv file
        pass
    else:
        print("ohno")
    

def fileTransfer(socket):
    global state
    global segmentNum
    global file

    if state != "transferReceive":
        return

    message, clientAddrPort = socket.recvfrom(2048)
    isEnd = int.from_bytes(message[0:1], "little")
    segmentNumFrom = int.from_bytes(message[1:3], "little")

    if isEnd == 1:
        state = "done"
        socket.sendto(segmentNum.to_bytes(2, "little"), clientAddrPort)
        file.close()
        return

    if(segmentNumFrom != segmentNum):
        pass
        #Ignore Invalid packets
    else:
        file.write(message[3:].decode("utf-8"))
        socket.sendto(segmentNum.to_bytes(2, "little"), clientAddrPort)
        segmentNum += 1
        

def readData(socket):
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
    print("timeout: no events")
  for sock in readRdySet:
    readSockFunc[sock](sock)

