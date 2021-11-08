#! /usr/bin/env python3
# udp demo -- simple select-driven uppercase server

# Eric Freudenthal with mods by Adrian Veliz

import time
import sys
from socket import *
from select import select

# default params
serverAddr = ('localhost', 50000)    

fileName = input("Enter the file to transfer")
data = open(fileName, "r", encoding='utf-8')

done = False
lastSent = False
segmentNumber = 0
numberToCheck = 0
terminate = False
segment = None
state = "init"

def sendData(socket: socket):
    global state
    if state == "init":
        sendFileStart(socket, fileName, serverAddr)
        state = "initVerify"
        return

    if state != "transfer":
        return

    print("here")

    global segmentNumber
    global numberToCheck
    global lastSent
    global segment

    continueNumber = 0
    segment = data.read(512).encode()


    if not segment:
        segment = "END".encode()
        continueNumber = 1
        lastSent = True

    segment = continueNumber.to_bytes(1, 'little') + segmentNumber.to_bytes(2, 'little') + segment
    socket.sendto(segment, serverAddr)

    state = "transferVerify"
    numberToCheck = segmentNumber
    #verifyReceive(socket, segmentNumber)
    print("here")

def resendData(socket:socket):
    socket.sendto(segment, serverAddr)


def verifyReceive(socket:socket):
    global state
    global segmentNumber
    if state == "initVerify":
        verifyFileStart(socket)
    elif state == "transferVerify":
        data, serverAddress = socket.recvfrom(2048)
        checkSegmentNumber = int.from_bytes(data[0:2], byteorder='little')
        print(numberToCheck)
        print(checkSegmentNumber)
        if checkSegmentNumber == numberToCheck:
            if lastSent:
                state = "done"
                return
            state = "transfer"
            segmentNumber += 1
  
def verifyFileStart(socket:socket):
    global state
    msg, serverAddr = socket.recvfrom(2048)
    if msg.decode() == "OK":
        state = "transfer"
    else:
        #make error
        state = "denied"


def sendFileStart(socket:socket, fileName: str, serverAddr):
    protocol = 0
    msg = protocol.to_bytes(1, 'little') + fileName.encode()
    socket.sendto(msg, serverAddr)

# map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              # ready for writing
errorSockFunc = {}              # broken

timeout = 3                     # select delay before giving up, in seconds


clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(False)

# function to call when upperServerSocket is ready for reading
readSockFunc[clientSocket] = verifyReceive
writeSockFunc[clientSocket] = sendData

print("ready to receive")
timer = time.time()

while state != "done":
  readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                list(writeSockFunc.keys()), 
                                                list(errorSockFunc.keys()),
                                                timeout)

  if not readRdySet and time.time() - timer > 5:
      timer = time.time()
      resendData(clientSocket)

  if not readRdySet and not writeRdySet and not errorRdySet:
    print("here")
    resendData(clientSocket)

  for sock in readRdySet:
    readSockFunc[clientSocket](sock)
  for sock in writeRdySet:
    writeSockFunc[clientSocket](sock)
  
