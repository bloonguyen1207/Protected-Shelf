# README #
---
## Requirements ##
- Linux OS
- Python3 with pip installed
- Postgres
## Setup ##
- Go to project's folder
### Server ###
- Open Postgres and create a db name ```shelf```
- Open and run ```CREATE_TABLE.sql``` inside your db
- Go to ```data_io.py``` and replace your ***dbname, username and password*** into the first function
- Start the server: ```python -m server.server_socket```

### Client ###
- Run ```python setup.py```
- Run the client app ```python -m app.helloworld```
- Help is available at ```python -m app.helloworld -h``` or ```python -m app.helloworld --help```