import bcrypt
import getpass
import re

# pword = "I'm awesome"
# salt = bcrypt.gensalt()
# hash_psw = bcrypt.hashpw(pword.encode(), salt)
#
# test = getpass.getpass("Password: ")
# if bcrypt.checkpw(test.encode(), hash_psw):
#     print("Matched")
# else:
#     print("Nope")


class User:
    def __init__(self, name, psw):
        self.name = name
        self.salt = bcrypt.gensalt()
        self.psw = bcrypt.hashpw(psw.encode(), self.salt)


def register():
    rule = re.compile("[a-z0-9_]{4,}")
    print("Username must be at least 4 chars, only including alphanumeric & underscore")
    username = input("Type your name (any name you like): ").strip()
    if rule.fullmatch(username) is not None:
        psw = getpass.getpass("Type your password: ").strip()
        confirm_psw = getpass.getpass("Do it again (just making sure you're not forgetting it): ").strip()
        if psw == confirm_psw:
            user = User(username, psw)
            print("User created: " + str(user.name))
        else:
            print("Password does not match. Try again.")
    else:
        print("Username invalid. Try again.")

register()
