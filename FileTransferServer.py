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

segmentNum = 0
newFile = open("temp.txt", "w", encoding="utf-8")
while 1:
    message, clientAddrPort = serverSocket.recvfrom(2048)
    isEnd = int.from_bytes(message[0:1], "little")
    segmentNumFrom = int.from_bytes(message[1:3], "little")

    if isEnd == 1:
        serverSocket.shutdown(0)
        break

    newFile.write(message[3:].decode("utf-8"))
    serverSocket.sendto(segmentNum.to_bytes(2, "little"), clientAddrPort)
    segmentNum += 1

    print("from %s: rec'd <%s>" % (repr(clientAddrPort), repr(message)))
    
                
newFile.close()