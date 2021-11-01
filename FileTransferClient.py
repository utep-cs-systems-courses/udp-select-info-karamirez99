#! /usr//bin/env python3
# udp demo client.  Modified from Kurose/Ross by Eric Freudenthal 2016

from socket import *


# default params
serverAddr = ('localhost', 50000)       

import sys, re                          

def sendData(socket: socket, data):
    segmentNumber = 0
    continueNumber = 0
    terminate = False

    while True:
        segment = data.read(512).encode()

        if not segment:
            if terminate:
                break
            segment = "END".encode()
            continueNumber = 1
            terminate = True

        segment = continueNumber.to_bytes(1, 'little') + segmentNumber.to_bytes(2, 'little') + segment

        socket.sendto(segment, serverAddr)


        verifyReceive(socket, segmentNumber)
        segmentNumber += 1

    
def verifyReceive(socket:socket, numberToCheck):
    while True:
        data, serverAddress = socket.recvfrom(2048)
        segmentNumber = int.from_bytes(data[0:2], byteorder='little')
        if segmentNumber == numberToCheck:
            break

    

def usage():
    print("usage: %s [--serverAddr host:port]"  % sys.argv[0])
    sys.exit(1)

try:
    args = sys.argv[1:]
    while args:
        sw = args[0]; del args[0]
        if sw in ("--serverAddr", "-s"):
            addr, port = re.split(":", args[0]); del args[0]
            serverAddr = (addr, int(port)) # addr can be a string (yippie)
        else:
            print("unexpected parameter %s" % args[0])
            usage()
except:
    usage()

print("serverAddr = %s" % repr(serverAddr))

clientSocket = socket(AF_INET, SOCK_DGRAM)
fileName = input("Enter the file to transfer")
data = open(fileName, "r", encoding='utf-8')
sendData(clientSocket, data)

# clientSocket.sendto(message.encode(), serverAddr)
# modifiedMessage, serverAddrPort = clientSocket.recvfrom(2048)
# print('Modified message from %s is "%s"' % (repr(serverAddrPort), modifiedMessage.decode()))
