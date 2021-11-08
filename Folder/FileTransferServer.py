#! /usr/bin/env python3
# udp demo server.  Modified from Kurose/Ross by Eric Freudenthal 2016
import sys

from socket import *

# default params
serverAddr = ("", 50000)        # (ip address, port#) where "" represents "any" 


def usage():
    print("usage: %s [--serverPort <port>]"  % sys.argv[0])
    sys.exit(1)

try:                       # attempt to parse parameters
    args = sys.argv[1:]    # argv[0] is program name (not a parameter)
    while args:
        sw = args[0]; del args[0]
        if sw == "--serverPort" or sw == "-s":
            serverAddr = ("", int(args[0])); del args[0]
        else:
            print("unexpected parameter %s" % args[0])
            usage()
except:
    usage()


serverSocket = socket(AF_INET, SOCK_DGRAM) # new datagram socket for communicating to an IP addr


print("binding datagram socket to %s" % repr(serverAddr))
serverSocket.bind(serverAddr)

print("ready to receive")

def getProtocol(socket):
    message, clientAddrPort = socket.recvfrom(2048)
    protocol = int.from_bytes(message[0:1], "little")
    fileName = message[1:].decode()
    if protocol == 0:
        socket.sendto(b"OK", clientAddrPort)
        fileTransfer(fileName, socket)
    elif protocol == 1:
        #TODO Implement recv file
        pass
    else:
        print("ohno")
    

def fileTransfer(fileName, socket):
    segmentNum = 0
    newFile = open(fileName, "w", encoding="utf-8")
    print("here")
    contin = True
    while contin:
        message, clientAddrPort = socket.recvfrom(2048)
        try:
            isEnd = int.from_bytes(message[0:1], "little")
            if isEnd == 1:
                print("YES")
            segmentNumFrom = int.from_bytes(message[1:3], "little")
            #print(segmentNumFrom)

            if isEnd == 1:
                contin = False
                return
                break

            if(segmentNumFrom != segmentNum):
                pass
                #Ignore Invalid packets
            else:
                newFile.write(message[3:].decode("utf-8"))
                socket.sendto(segmentNum.to_bytes(2, "little"), clientAddrPort)
                segmentNum += 1

            if clientAddrPort is not None:
                print("from %s: rec'd <%s>" % (repr(clientAddrPort), repr(message)))
        except:
            #Assumption: we got here from valid message, but client still trying to initiate protocol
            socket.sendto(b"OK", clientAddrPort)
        
                    
    newFile.close()

while 1:
    getProtocol(serverSocket)
