# Python program to implement client side of chat room.
import socket
import select
import sys

import os, random, struct
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect to server socket
IP= "127.0.0.1"
PORT = 12345
server.connect((IP, PORT))

#Generate an RSA key pair. Each key length is 2048
key = RSA.generate(2048)
public_key = key.publickey().exportKey("PEM")
symmetric_key = ""

while True:
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

    #Read receiving messages
    for socket in read_sockets:
        if socket == server:
            message = socket.recv(2048)

            #If the client already has the symmetric key and not a message from
            #server, decrypt the message with symmetric key
            if len(symmetric_key) > 0 and message[0] != "?":

                #Initialization Vector
                iv = message[:AES.block_size]

                #Creating AES cipher
                cipher = AES.new(symmetric_key, AES.MODE_CFB, iv)

                #Decrypt and print message received from other users
                plain = cipher.decrypt(message[AES.block_size:])
                print plain

            else:

                #Check if receiving symmetric key from server
                if message.strip() == "?sending encrypted key":
                    message = socket.recv(2048)

                    #Decrypt symmetric key using private key
                    temp = tuple([message])
                    symmetric_key = key.decrypt(temp)
                    print symmetric_key

                else:
                    print message

        else:
            if len(symmetric_key) > 0:
                message = sys.stdin.readline()

                #If user already has the symmetric key and is not entering a
                #command, encrypt message with symmetric key
                if message[0] != "?":

                    #Initialization Vector
                    iv = Random.new().read(AES.block_size)

                    #Creating AES cipher
                    cipher = AES.new(symmetric_key,AES.MODE_CFB, iv)

                    #Encrypt message
                    message = iv + cipher.encrypt(message)

                server.send(message)
                sys.stdout.write("<You> ")
                sys.stdout.write(message)
                sys.stdout.write("\n")
                sys.stdout.flush()

            else:
                message = sys.stdin.readline()
                server.send(message)
                sys.stdout.write("<You> ")
                sys.stdout.write(message)
                sys.stdout.flush()

                #Send public key to server
                if message == "?send key\n":
                    server.send(public_key)

server.close()
