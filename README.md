# README #
---
## Requirements ##
- Linux OS
- Python3 with pip installed
- Postgres
---

## Setup ##
- Go to project's folder
### Server ###
- Open Postgres and create a db name ```shelf```
- Open and run ```CREATE_TABLE.sql``` inside your db
- Go to ```data_io.py``` and replace your ***dbname, username and password*** into the first function
- Start the server: ```python3 -m server.server_socket```

### Client ###
- Run ```python3 setup.py```

---

## Getting started ##

***Note***: From here on, the word `shelf` is short of `python3 -m app.helloworld`

- After finish the setup, you can now run the client app using this command `shelf`

- Help is available at `shelf -h` or `shelf --help` 

- First, you'll want to register for an account using `shelf register`

- Then use `shelf login` to login to the account

- You can send a request to start a conversation with `shelf start-conv [username]`

- The other user must accept the request before starting the conversation, you can check the status request using `shelf sent-req`

- Check for incoming requests using `shelf recv-req` and answer it with `shelf request -r [request id] -a [your answer (y/n)]`

- Once the request is accepted, you will see it in the conversation list available at `shelf my-conv`

- To enter a conversation, use `shelf enter-conv -c [conversation id]`