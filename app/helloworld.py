from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from app import data_handler
from sockets.client_socket import ClientSocket
# from classes.user import User
import re
# import getpass
# import sys

VERSION = "0.0.1"

BANNER = """Protected Shelf v%s""" % VERSION

HOST = "localhost"
PORT = 2222


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

        if rule.fullmatch(username) is not None:
            request = data_handler.format_username(username)
            if client.send_message(request) != "None":
                print("Username already existed. Please use another one.")
            # else:
        #     psw = getpass.getpass("Type your password: ").strip()
        #     confirm_psw = getpass.getpass("Do it again (just making sure you're not forgetting it): ").strip()
        #
        #     if psw == confirm_psw:
        #         user = User(username, psw)
        #         print("User successfully created.")
        #         print("Type 'shelf login' to login")
        #     else:
        #         print("Password does not match. Try again.")
        #
        else:
            print("Username invalid. Try again.")
        # client.close_connection()

    # Activate prompt
    @expose(help="Open session")
    def login(self):
        self.app.log.info("Inside BaseController.login()")


class App(CementApp):
    class Meta:
        label = 'shelf'
        extensions = ['json']
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
