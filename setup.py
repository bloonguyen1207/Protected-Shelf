from subprocess import run

# Install dependencies

DEPENDENCIES = [
    "bcrypt",
    "cement",
    "colorlog",
    "psycopg2",
    "pycrypto",
    "tabulate"
]

for i in DEPENDENCIES:
    run(["pip3", "install", i])
