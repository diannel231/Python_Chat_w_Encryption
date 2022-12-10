# Python program to implement server side of chat room.
import socket
import select
import sys
from thread import *

import os, random, struct
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode

#Create Server Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Bind to the port
IP = "127.0.0.1"
PORT = 12345
server.bind((IP, PORT))

#Listen for up to 100 connections
server.listen(100)

#List of usernames and passwords
list_of_credentials = {"cow":"password", "milk":"password", "potato":"password"}

#This list would be used for who is online
list_of_clients = {}

#List used for clients to be in a chat room
room_clients = {}

#The public key
key = {}

#Key to distribute to all users
symmetric_key = b'0123456789ABCDEF'

#Thread for each client
def client_thread(conn, addr):
    while True:
            try:
                message = conn.recv(2048).strip()
                if message:

                    #Print who the message is from
                    print "< " + str(list_of_clients[conn]) + " > " + message

                    #Using ? to denote commands to server. Messages from server
                    #to client will also use "?" to let client know it is the server
                    if message[0] == "?":

                        #Keyword "users" for obtaining list of users
                        if message[1:] == "users":
                            print "?sending", list_of_clients[conn], "all the users"

                            #List out who is online besides the user
                            for user in list_of_clients:
                                if user != conn:
                                    message_to_send = "?" + list_of_clients[user] + "\n"
                                    conn.send(message_to_send)

                        #Keyword "add users" to add other online users to a chat room
                        elif message[1:] == "add users":
                            print "?Adding users to room"

                            #The user is added to the room
                            if add_to_room(conn):
                                conn.send("?You have successfully been added to the room\n")
                            else:
                                conn.send("?You are already in the room\n")

                            #Get who to add from the user and add them to the room
                            conn.send("?Who would you like to add? (start names with ?. type ?stop to end)\n")
                            user = ""
                            while user != "?stop":
                                user = conn.recv(2048).strip()
                                for client in list_of_clients:
                                    if list_of_clients[client] == user[1:]:
                                        if add_to_room(client):
                                            conn.send("?Sucessfully added user\n")
                                            client.send("?You have been added to the room\n")
                                        else:
                                            conn.send("?Failed to add user\n")
                            conn.send("?Adding users to room ended\n")

                        #Keyword "send key" to receive users' public key
                        elif message[1:] == "send key":
                            print "Recieving key from", list_of_clients[conn]
                            public_key = conn.recv(2048).strip()
                            key[conn] = RSA.importKey(public_key)

                            #Encrypt symmetric key with public key then send to the user
                            conn.send("?sending encrypted key")
                            temp = symmetric_key
                            encrypted_key = RSA.importKey(public_key).encrypt(temp, 32)
                            conn.send(encrypted_key[0])

                        else:
                            conn.send("?Invalid command\n")

                    #Print who sent the message and broadcast it to other users
                    #who are in the chat room
                    else:
                        message_to_send = "?< " + str(list_of_clients[conn]) + " > "
                        for client in room_clients:
                            if conn == client:
                                broadcast_room(message_to_send, conn)
                                broadcast_room(message, conn)

                #Remove user if connection is broken
                else:
                    remove(conn)
            except:
                continue

#Broadcast to all users
def broadcast(message, connection):
    for client in list_of_clients:
        if client != connection:
            try:
                client.send(message)
            except:
                client.close()
                remove(client)

#Broadcast to all users in room
def broadcast_room(message, connection):
    for client in room_clients:
        if client != connection:
            try:
                client.send(message)
            except:
                client.close()
                remove(client)

#Remove user from list of clients
def remove(client):
    if client in list_of_clients:
        del list_of_clients[client]

#Validate login creditials
def login(conn, addr):
    conn.send("Please Enter your username\n")
    username = conn.recv(2048).strip()

    conn.send("Please Enter your password\n")
    password = conn.recv(2048).strip()

    for name in list_of_credentials:
        if name == username:

            #Prevent multiple logins to same username
            for client in list_of_clients:
                if list_of_clients[client] == name:
                    print username, "already logged in"
                    conn.send("User is already logged in, closing connection\n")
                    remove(conn)
                    return False

            if list_of_credentials[name] == password:
                print username, "has been authorized"
                list_of_clients[conn] = username
                conn.send("User authorized\n")
                return True

            else:
                print addr[1], "Invalid credentials"
                conn.send("Invalid credentials, closing connection\n")
                remove(conn)
                return False

    print username, "does not exist"
    conn.send("User does not exist, closing connection\n")
    remove(conn)
    return False

#Add users to chat room
def add_to_room(client):
    for user in room_clients:
        if user == client:
            print "unable to add", list_of_clients[client]
            return False
    room_clients[client] = list_of_clients[client]
    print "Successfully added", list_of_clients[client]
    return True


while True:

    #Accepts connection requests
    conn, addr = server.accept()
    print str(addr[1]) + " connected"

    #Creates thread for user if they successfully log in
    if login(conn, addr):
        start_new_thread(client_thread,(conn,addr))

conn.close()
server.close()
