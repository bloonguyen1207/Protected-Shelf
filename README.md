# README #
---

## Overview ##

This project is called **Protected Shelf**. It is an end-to-end encryption terminal chat application. It uses RSA encryption to encrypt users' messages before sending it to the server for exchange. Only the user's public keys are stored on the server, not their private keys. Therefore, their messages are secured with this application.

---

## Requirements ##

- Python3 with pip installed
- Postgres with pgAdmin
---

## Setup ##
- Open your terminal and go to project's folder.
- Run ```alias shelf='python3 -m app.helloworld'```. Now you will be able to call the client app using the keyword **shelf**. 
- Run ```python3 setup.py```.

### Server ###
- Create a new database
- Open and run ```CREATE_TABLE.sql``` inside your database
- Go to ```data_io.py``` and replace your **dbname, username and password** into the ```connect_to_db()``` function
- Start the server: ```python3 -m server.server_socket```

### Can this thing run on LAN? ###
- Yes, yes it can. 
- To run on LAN, you just need to re-config the ```host``` in ```server/config.json``` and ```app/config.json``` from its default setting (localhost) to **your ip**. Super simple, right? ᕕ( ᐛ )ᕗ
- You don't know how to get you IP address? (눈_눈) There are things that must be learnt by yourself. Fight on!!! ( •̀ᄇ• ́)ﻭ✧

---

## Getting started ##

- After finish the setup, you can now run the client app using this command `shelf`

- Help is available at `shelf -h` or `shelf --help` 

- First, you'll want to register for an account using `shelf register`

- Then use `shelf login` to login to the account

- You can send a request to start a conversation with `shelf start-conv [username]`

- The other user must accept the request before starting the conversation, you can check the status request using `shelf sent-req`

- Check for incoming requests using `shelf recv-req` and answer it with `shelf request -r [request id] -a [your answer (y/n)]`

- Once the request is accepted, you will see it in the conversation list available at `shelf my-conv`

- To enter a conversation, use `shelf enter-conv -c [conversation id]`

- See more commands using the help command above.

---
**Note:** The message history function is not available yet due to server's lack of bandwidth. Codes related to this part are commented out.

--- 
Feel free to explore the project but don't be surprised if you encounter a bug. I did try my best to fix all the bug but after all, nothing is bug free in this world, right? ┐(￣ヮ￣)┌
