import bcrypt
from Crypto.PublicKey import RSA
import socket
import os.path

# s = "Hello world"
# new_key = RSA.generate(2048)
# public_key = new_key.publickey()
# private_key = new_key.exportKey("PEM")
#
# print(public_key.encrypt('Hello'.encode(), 32)[0])


class User:
    def __init__(self, name, salt, psw):
        self.name = name
        self.salt = salt
        self.psw = bcrypt.hashpw(psw.encode(), self.salt.encode()).decode()

    def set_current_user(self):
        f = open('appdata/.current_user', 'w')
        f.write(self.name + '\n' + self.salt + '\n' + self.psw)
        f.close()

    def gen_key(self):
        new_key = RSA.generate(2048)
        public_key = new_key.publickey().exportKey("PEM")
        private_key = new_key.exportKey("PEM")

        key_dir = "appdata/keystore/{}_{}/".format(self.name, socket.gethostname())
        pubkey_path = key_dir + "public.key"
        key_path = key_dir + "private.key"
        if not os.path.exists(key_dir):
            os.makedirs(key_dir)
            if not os.path.isfile(pubkey_path) and not os.path.isfile(key_path):
                pub_file = open(pubkey_path, 'w')
                pub_file.write(public_key.decode())
                pub_file.close()

                key_file = open(key_path, 'w')
                key_file.write(private_key.decode())
                key_file.close()

    def publickey(self):
        key_dir = "appdata/keystore/{}_{}/".format(self.name, socket.gethostname())
        key_file = open(key_dir + "public.key", 'r')
        key = key_file.read()
        key_file.close()
        return key

    @staticmethod
    def load_key(key):
        k = RSA.importKey(key)
        return k
