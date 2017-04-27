import signal

from cement.core.exc import CaughtSignal
from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from cement.ext.ext_tabulate import tabulate
from app import data_handler
from classes.client_socket import ClientSocket
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
try:
    CURRENT_USER_DATA = open('appdata/.current_user', 'r').read().split('\n')
    if CURRENT_USER_DATA != ['']:
        CURRENT_USER = User(CURRENT_USER_DATA[0], CURRENT_USER_DATA[1], CURRENT_USER_DATA[2])
    else:
        CURRENT_USER = None
except FileNotFoundError:
    CURRENT_USER = None

NAME_RULE = re.compile("[a-z0-9_]{4,}")

ANSWERS = ['y', 'n', 'yes', 'no']

SIGNALS = [signal.SIGTERM, signal.SIGINT, signal.SIGHUP]


# define any hook functions here
def my_cleanup_hook(app):
    pass


class BaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Application does amazing things!"
        arguments = [
            (['-v', '--version'], dict(action='version', version=BANNER)),
            (['-u', '--user'], dict(action='store', metavar='name',
                                    help='specify username when start new conversation.')),
            (['-r', '--request'],
                dict(action='store', metavar='id', help='specify request id to response to.')),

            (['-a', '--answer'],
             dict(action='store', metavar='ans', help='specify answer to request')),

            (['-c', '--conv'],
             dict(action='store', metavar='id', help='specify conversation id in command'))
            ]

    @expose(hide=True)
    def default(self):

        """Run 'python3 -m app.helloworld' to get here"""

        self.app.log.info('Inside BaseController.default()')
        print("Welcome to " + BANNER)
        print("Type 'shelf --help' to see available commands.")

    # New user sign up
    @expose(help="Create a new account")
    def register(self):

        """Create new user"""

        client = ClientSocket()
        client.open_connection(HOST, PORT)

        self.app.log.info("Inside BaseController.register()")

        print("Username must be at least 4 chars, only including alphanumeric & underscore")

        username = input("Type your name (any name you like): ").strip()

        # Username must matched with the name rules
        if NAME_RULE.fullmatch(username) is not None:
            # Data will be sent and processed on the server
            request = data_handler.format_username(username)
            response = client.send_message(request)

            if response != "None":
                self.app.log.warning("Username already existed. Please use another one.")

            else:   # If username is not duplicated, proceed
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
    @expose(help="Log in to your account")
    def login(self):

        """
        Authenticate username and password
        Set current user if all matched
        """

        self.app.log.info("Inside BaseController.login()")
        client = ClientSocket()
        client.open_connection(HOST, PORT)

        username = input("Username: ").strip()

        # Username must matched with the name rules
        if NAME_RULE.fullmatch(username) is not None:
            psw = getpass.getpass("Password: ")

            request = data_handler.format_username(username)
            response = client.send_message(request)

            # If user existed, proceed
            if response != "None":
                user = User(username, response, psw)
                request = data_handler.format_login(user)
                auth = client.send_message(request)

                if auth == "True":
                    user.gen_key()
                    user.set_current_user()
                    self.app.log.info("Logged in successfully as " + user.name)
                    CURRENT_USER = user

                else:   # Wrong password
                    self.app.log.error("Username or password is incorrect. Please try again.")

            else:   # Username not registered in db
                self.app.log.error("Username or password is incorrect. Please try again.")

    @expose(help="Log out of your account")
    def logout(self):

        """Remove data from local current user file"""

        self.app.log.info("Inside BaseController.logout()")
        f = open("appdata/.current_user", "w")
        f.write("")
        f.close()
        CURRENT_USER = None
        self.app.log.info("Logged out.")

    @expose(help="See the current user")
    def current_user(self):

        """Display current user"""

        self.app.log.info("Inside BaseController.current_user()")
        if CURRENT_USER is None:
            self.app.log.info("No user is currently logged in.")
            print("Type 'shelf login' to login.")
        else:
            self.app.log.info(CURRENT_USER.name + " is the current user.")

    @expose(help="Send request to start a new conversation")
    def start_conv(self):

        """
        Send a request to start a conversation with another user
        Conversation won't be created until the request is accepted
        """

        self.app.log.info("Inside BaseController.start_conv()")
        if CURRENT_USER is not None:
            if len(sys.argv) < 3:
                print("usage: 'shelf start-conv -u [username]'")
            else:
                client = ClientSocket()
                client.open_connection(HOST, PORT)

                target = self.app.pargs.user
                if NAME_RULE.fullmatch(str(target)) is not None:
                    request = data_handler.format_username(target)
                    response = client.send_message(request)
                    if response == "None":
                        print("User " + target + " does not exist.")
                    else:
                        print("Sending request to start conversation with " + target + "...")
                        request = data_handler.format_req(CURRENT_USER.name, target, CURRENT_USER.publickey())
                        response = client.send_message(request)
                        if response == "Success":
                            self.app.log.info("Request sent. Please wait for the other user to accept.")
                        else:
                            print("Something went wrong. Please try again later.")
                else:
                    self.app.log.error("Invalid username or invalid argument.")
        else:
            self.app.log.error("Please login before starting a conversation.")
            print("Type 'shelf login' to login.")

    @expose(help="Fetch your public key")
    def my_key(self):

        """Display user's public key"""

        self.app.log.info("Inside BaseController.my_key()")
        if CURRENT_USER is not None:
            print(CURRENT_USER.publickey())
        else:
            self.app.log.error("You have not logged in yet.")
            print("Type 'shelf login' to login.")

    @expose(help="Fetch invitations you sent to others")
    def sent_req(self):

        """Display under table format sent requests fetched from the server"""

        self.app.log.info("Inside BaseController.sent_request()")
        if CURRENT_USER is not None:
            client = ClientSocket()
            client.open_connection(HOST, PORT)

            request = data_handler.format_sent_request(CURRENT_USER)
            response = client.send_message(request)
            if response == "None":
                print("You have not sent any request.")
            else:
                reqs = response.split(", ")
                table_data = []
                for i in reqs:
                    table_data.append(i.split(' '))
                print(tabulate(table_data, ["ID", "Receiver", "Status"], tablefmt="psql"))
        else:
            self.app.log.error("You have not logged in yet.")
            print("Type 'shelf login' to login.")

    @expose(help="Fetch received invitations from others")
    def recv_req(self):

        """Display under table format incoming requests fetched from the server"""

        self.app.log.info("Inside BaseController.received_request()")
        if CURRENT_USER is not None:
            client = ClientSocket()
            client.open_connection(HOST, PORT)

            request = data_handler.format_received_request(CURRENT_USER)
            response = client.send_message(request)
            if response == "None":
                print("You don't have any request.")
            else:
                reqs = response.split(", ")
                table_data = []
                for i in reqs:
                    table_data.append(i.split(' '))
                print(tabulate(table_data, ["ID", "Sender", "Status"], tablefmt="psql"))
        else:
            self.app.log.error("You have not logged in yet.")
            print("Type 'shelf login' to login.")

    @expose(help="Accept or decline pending invitations")
    def request(self):

        """
        Answer incoming requests
        Conversation will be created if request is accepted
        """

        self.app.log.info("Inside BaseController.request()")
        if len(sys.argv) < 3 or len(sys.argv) < 5:
            print("usage: 'shelf request -r [request id] -a [answer(y/n)]'")
        else:
            client_res = self.app.pargs.answer
            if client_res.lower().strip() in ANSWERS:
                if CURRENT_USER is not None:
                    client = ClientSocket()
                    client.open_connection(HOST, PORT)

                    request = data_handler.format_answer(CURRENT_USER,
                                                         self.app.pargs.request,
                                                         client_res.lower())
                    response = client.send_message(request)
                    if response == "True" and client_res.lower() == 'y' or client_res.lower() == 'yes':
                        self.app.log.info("Conversation request accepted.")
                        print("Type 'shelf my-conv' to see available conversations")
                    elif response == "True" and client_res.lower() == 'n' or client_res.lower() == 'no':
                        self.app.log.info("Conversation request declined.")
                    else:
                        self.app.log.error("You are not authenticated to access this conversation "
                                           "or conversation not found.")
                else:
                    self.app.log.error("You have not logged in yet.")
                    print("Type 'shelf login' to login.")
            else:
                self.app.log.error("Invalid answer.")

    @expose(help="Fetch available conversations")
    def my_conv(self):

        """
        Display under table format available conversations 
        of the user fetched from the server
        """

        self.app.log.info("Inside BaseController.my_conv()")
        if CURRENT_USER is not None:
            client = ClientSocket()
            client.open_connection(HOST, PORT)

            request = data_handler.format_fetch_conv(CURRENT_USER)
            response = client.send_message(request)
            if response == "None":
                print("You don't have any conversation.")
            else:
                reqs = response.split(", ")
                table_data = []
                for i in reqs:
                    table_data.append(i.split(' '))
                print(tabulate(table_data, ["ID", "User 1", "User 2"], tablefmt="psql"))
        else:
            self.app.log.error("You have not logged in yet.")
            print("Type 'shelf login' to login.")

    @expose(help="Enter a conversation")
    def enter_conv(self):

        """Enter a conversation to exchange messages"""

        self.app.log.info("Inside BaseController.enter_conv()")
        if CURRENT_USER is not None:
            if len(sys.argv) < 3:
                print("usage: 'shelf enter-conv -c [conversation id]'")
            else:
                client = ClientSocket()
                client.open_connection(HOST, PORT)
                conv_id = self.app.pargs.conv
                if conv_id.isdigit():
                    request = data_handler.format_enter_conv(CURRENT_USER,
                                                             self.app.pargs.conv)
                    response = client.send_message(request)
                    if response == "False":
                        self.app.log.error("Something went wrong. Make sure you entered the correct conversation id.")
                        print("Type 'shelf my-conv' to see available conversations")
                    else:
                        f_key = None
                        conv_data = data_handler.parse_json(response.replace("'", '"'))
                        for k in conv_data.keys():
                            if k != "room" and k != CURRENT_USER.name + "_key":
                                f_key = User.load_key(conv_data[k])

                        print("Connected. You can now start sending messages")
                        print("Type 'exit.' or press 'Ctrl + C' to disconnect.")

                        sys.stdout.write('>> ')
                        sys.stdout.flush()
                        client.in_conversation(CURRENT_USER, conv_data['room'], f_key)
                else:
                    self.app.log.error("Invalid conversation ID.")
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


def main():
    with App() as app:
        # log stuff
        app.log.debug("About to run " + BANNER)
        # run the application
        try:
            app.run()
        except CaughtSignal as e:
            if e.signum == signal.SIGTERM:
                print("\nCaught SIGTERM...")
            elif e.signum == signal.SIGINT:
                print("\nExiting...")

if __name__ == '__main__':
    main()
