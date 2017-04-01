from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from app import data_handler
from sockets.client_socket import ClientSocket
from classes.user import User
import bcrypt
import getpass
import re
import sys

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

CURRENT_USER_DATA = open('appdata/.current_user', 'r').read().split('\n')
if CURRENT_USER_DATA != ['']:
    CURRENT_USER = User(CURRENT_USER_DATA[0], CURRENT_USER_DATA[1], CURRENT_USER_DATA[2])
else:
    CURRENT_USER = None

NAME_RULE = re.compile("[a-z0-9_]{4,}")


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
            (['-u', '--user'], dict(action='store', metavar='name',
                                    help='specify username when start new conversation.'))
            # (['--start-conv', dict],
            #     dict(action='store', help='Create new user')),
            ]

    @expose(hide=True)
    def default(self):
        self.app.log.info('Inside BaseController.default()')
        print("Welcome to " + BANNER)
        print("Type 'shelf --help' to see available commands.")

    # New user sign up
    @expose()
    def register(self):
        client = ClientSocket()
        client.open_connection(HOST, PORT)

        self.app.log.info("Inside BaseController.register()")

        print("Username must be at least 4 chars, only including alphanumeric & underscore")

        username = input("Type your name (any name you like): ").strip()
        # TODO: why tf is this always receive None - fixed
        if NAME_RULE.fullmatch(username) is not None:
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
    @expose()
    def login(self):
        self.app.log.info("Inside BaseController.login()")
        client = ClientSocket()
        client.open_connection(HOST, PORT)

        username = input("Username: ").strip()
        if NAME_RULE.fullmatch(username) is not None:
            psw = getpass.getpass("Password: ")
            request = data_handler.format_username(username)
            response = client.send_message(request)
            if response != "None":
                user = User(username, response, psw)
                request = data_handler.format_login(user)
                auth = client.send_message(request)
                if auth == "True":
                    user.gen_key()
                    user.set_current_user()
                    self.app.log.info("Logged in successfully as " + user.name)
                else:
                    self.app.log.error("Username or password is incorrect. Please try again.")
            else:
                self.app.log.error("Username or password is incorrect. Please try again.")

    @expose()
    def logout(self):
        self.app.log.info("Inside BaseController.logout()")
        f = open("appdata/.current_user", "w")
        f.write("")
        f.close()
        self.app.log.info("Logged out.")

    @expose()
    def current_user(self):
        self.app.log.info("Inside BaseController.current_user()")
        if CURRENT_USER is None:
            self.app.log.info("No user is currently logged in.")
            print("Type 'shelf login' to login.")
        else:
            self.app.log.info(CURRENT_USER.name + " is the current user.")

    # TODO: Check if request existed.
    @expose(help="Start a new conversation")
    def start_conv(self):
        self.app.log.info("Inside BaseController.start_conv()")
        if CURRENT_USER is not None:
            if len(sys.argv) < 3:
                print("usage: 'shelf start-conv -u [username]'")
            else:
                client = ClientSocket()
                client.open_connection(HOST, PORT)

                target = self.app.pargs.user
                if NAME_RULE.fullmatch(target) is not None:
                    request = data_handler.format_username(target)
                    response = client.send_message(request)
                    if response == "None":
                        print("User " + target + " does not exist.")
                    else:
                        print("Sending request to start conversation with " + target + "...")
                        request = data_handler.format_req(CURRENT_USER.name, target, CURRENT_USER.publickey())
                        response = client.send_message(request)
                        if response is not None:
                            self.app.log.info("Request sent. Please wait for the other user to accept.")
                        else:
                            print("Something went wrong. Please try again later.")
                else:
                    self.app.log.error("Invalid username.")
        else:
            self.app.log.error("Please login before starting a conversation.")
            print("Type 'shelf login' to login.")


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
