from cement.utils.shell import Prompt

import sys


class Session(Prompt):
    class Meta:
        text = """>>>"""
        max_attempts = 10

    def process_input(self):
        commands = {
            "connect": "Connecting...",
            "help": "Helping...",
            "exit": "Exiting...Bye bye."
        }
        if self.input.lower() in commands:
            print commands[self.input.lower()]
            if self.input.lower() == "exit":
                return False
        else:
            print "Invalid input. Exiting..."
            return False

Session()
