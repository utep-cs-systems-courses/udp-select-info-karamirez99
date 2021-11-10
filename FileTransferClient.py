#! /usr/bin/env python3

import sys
import time
from socket import *
from select import select

# default params
serverAddr = ('localhost', 50000)    

fileName = input("Enter the file to transfer: ")
data = None
lastSent = False
segmentNumber = 0
numberToCheck = 0
segment = None
state = "init"
startTime = 0
rtt = 0
alpha = 0.9

def sendData(socket: socket):
    global state
    global segmentNumber
    global numberToCheck
    global lastSent
    global segment

    continueNumber = 0
    segment = data.read(512)

    if not segment:
        segment = "END".encode()
        continueNumber = 1
        lastSent = True

    segment = continueNumber.to_bytes(1, 'little') + segmentNumber.to_bytes(2, 'little') + segment
    socket.sendto(segment, serverAddr)

    state = "transferVerify"
    numberToCheck = segmentNumber
    segmentNumber += 1


def resendData(socket:socket):
    if segment is None:
        return
    print("Timeout: resending segment #", numberToCheck)
    socket.sendto(segment, serverAddr)


def verifyReceive(socket:socket):
    global state
    global segmentNumber
    global startTime
    global rtt

    data, serverAddress = socket.recvfrom(2048)
    checkSegmentNumber = int.from_bytes(data[0:2], byteorder='little')
    
    if checkSegmentNumber == numberToCheck:
        rtt = rtt * alpha + (1 - alpha) * (time.time() - startTime)
        print("New RTT: ", rtt)
        startTime = time.time()

        if lastSent:
            state = "done"
            return

        state = "transfer"
        sendData(socket)
  

def verifyFileStart(socket:socket):
    global state
    global data
    global startTime
    msg, serverAddr = socket.recvfrom(2048)

    if msg.decode() == "OK":
        state = "transfer"
        data = open(fileName, "rb")
        startTime = time.time()
        sendData(socket)


# Initiate File Transfer
def sendFileStart(socket:socket, fileName: str, serverAddr):
    global state
    global segment
    global startTime

    protocol = 0
    msg = protocol.to_bytes(1, 'little') + fileName.encode()
    socket.sendto(msg, serverAddr)
    segment = msg
    state = "initVerify"
    startTime = time.time()


# Execute tasks for  State of Client on new MSG
def fileTransfer(socket):
    global state

    if state == "initVerify":
        verifyFileStart(socket)
    elif state == "transfer":
        sendData(socket)
    elif state == "transferVerify":
        verifyReceive(socket)

# map socket to function to call when socket is....
readSockFunc = {}               # ready for reading
writeSockFunc = {}              
errorSockFunc = {}              

timeout = 3                     # select delay before giving up, in seconds
remTries = 5

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(False)

readSockFunc[clientSocket] = fileTransfer

print("ready to receive")

sendFileStart(clientSocket, fileName, serverAddr)

while state != "done":
  readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                list(writeSockFunc.keys()), 
                                                list(errorSockFunc.keys()),
                                                timeout)

  if not readRdySet and not writeRdySet and not errorRdySet:
    remTries -= 1
    resendData(clientSocket)

  for sock in readRdySet:
    remTries = 5
    readSockFunc[sock](sock)

  if remTries <= 0:
    print("Too many tries: time to give up")
    state = "done"
