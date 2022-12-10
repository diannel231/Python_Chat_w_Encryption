# Secure-Chat

Dianne Lopez    diannelopez231@gmail.com

## To run server:
  python server.py

## To run client:
  python client.py

## Client chat commands:

  ?users

    server will send a list of online users back to the client

  ?add users

    server will first attempt to add the client

    server will prompt client for the username to add

    type stop to end add routine

  ?send key

    client will send public key to server

    server will take client public key and encrypt symmetric key using public key

    server will send encrypted symmetric key back to client

    client will decrypt symmetric key using private key

    client will display symmetric key.

    *Garbled output from client indicates failed transaction. Please close the client program and run again.

