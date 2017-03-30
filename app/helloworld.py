from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from app import data_handler
from sockets.client_socket import ClientSocket
from classes.user import User
import bcrypt
import re
import getpass
# import sys

VERSION = "0.0.1"

BANNER = """Protected Shelf v%s""" % VERSION

HOST = "localhost"
PORT = 2222

COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}

CURRENT_USER = open('appdata/.current_user', 'r').read()


# define any hook functions here
# Bloo: No idea wtf is this
def my_cleanup_hook(app):
    pass


class BaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Application does amazing things!"
        arguments = [
            (['-v', '--version'], dict(action='version', version=BANNER)),
            # (['-c', '--create-user'],
            #     dict(action='store', help='Create new user')),
            ]

    @expose(hide=True)
    def default(self):
        self.app.log.info('Inside BaseController.default()')
        print("Welcome to " + BANNER)
        print("Type 'shelf --help' to see available commands.")

    # New user sign up
    @expose(help="Create new user")
    def register(self):
        client = ClientSocket()
        client.open_connection(HOST, PORT)

        self.app.log.info("Inside BaseController.register()")

        rule = re.compile("[a-z0-9_]{4,}")
        print("Username must be at least 4 chars, only including alphanumeric & underscore")

        username = input("Type your name (any name you like): ").strip()
        # TODO: why tf is this always receive None - fixed
        if rule.fullmatch(username) is not None:
            request = data_handler.format_username(username)
            response = client.send_message(request)

            if response != "None":
                self.app.log.warning("Username already existed. Please use another one.")
            else:
                salt = bcrypt.gensalt().decode()
                psw = getpass.getpass("Type your password: ")
                confirm_psw = getpass.getpass("Do it again (just making sure you're not forgetting it): ")

                if psw == confirm_psw:
                    user = User(username, salt, psw)
                    request = data_handler.format_register_user(user)

                    if client.send_message(request) is not None:
                        self.app.log.info("User successfully created.")
                        print("Type 'shelf login' to login")
                else:
                    self.app.log.error("Password does not match. Try again.")
        else:
            self.app.log.error("Username invalid. Try again.")

    # Activate prompt
    @expose(help="Login")
    def login(self):
        self.app.log.info("Inside BaseController.login()")
        client = ClientSocket()
        client.open_connection(HOST, PORT)
        flag = True

        rule = re.compile("[a-z0-9_]{4,}")
        print("Username must be at least 4 chars, only including alphanumeric & underscore")

        username = input("Username: ").strip()
        if rule.fullmatch(username) is not None:
            if flag is True:
                psw = getpass.getpass("Password: ")
                request = data_handler.format_username(username)
                response = client.send_message(request)
                if response != "None":
                    user = User(username, response, psw)
                    request = data_handler.format_login(user)
                    auth = client.send_message(request)
                    if auth == "True":
                        self.app.log.info("Logged in successfully as " + user.name)
                        f = open('appdata/.current_user', 'w')
                        f.write(user.name)
                        f.close()
                    else:
                        self.app.log.error("Username or password is incorrect. Please try again.")
                else:
                    self.app.log.error("Username or password is incorrect. Please try again.")
            else:
                self.app.log.error("Username or password is incorrect. Please try again.")

    @expose(help="Logout")
    def logout(self):
        self.app.log.info("Inside BaseController.logout()")
        f = open("appdata/.current_user", "w")
        f.write("")
        f.close()
        self.app.log.info("Logged out.")

    @expose(help="Get current user")
    def current_user(self):
        self.app.log.info("Inside BaseController.current_user()")
        if CURRENT_USER is "":
            self.app.log.info("No user is currently logged in.")
            print("Type 'shelf login' to login.")
        else:
            self.app.log.info(CURRENT_USER)


class App(CementApp):
    class Meta:
        label = 'shelf'
        extensions = ['json', 'colorlog']
        log_handler = 'colorlog'
        hooks = [
            ('pre_close', my_cleanup_hook),
        ]
        base_controller = 'base'
        handlers = [BaseController]


with App() as app:
    # log stuff
    app.log.debug("About to run " + BANNER)

    # run the application
    app.run()
