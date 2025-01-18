import smtplib

import dotenv
from flask import Flask
import json

app: Flask = Flask("")
config: dict = {}
DEBUG = False

@app.route("/")
def index():
    return "DFHub-NoReply active"

def load_config():
    global config
    with open("config.json", 'r', encoding="utf-8") as config_file:
        config = json.loads(config_file.read())

    if not "public-address" in config:
        config["public-address"] = "127.0.0.1"
    if not "port" in config:
        config["port"] = 587

    if config["public-address"] in ["127.0.0.1", "localhost"]:
        print(f"WARNING! Server running on {config['public-address']} and can't be accessed from external network!")

if __name__ == "__main__":
    print("Loading .env file")
    dotenv.load_dotenv()
    print("Initializing Flask server")
    app = Flask("dfhub-uptime")
    print("Reading config.json")
    load_config()

    app.run(
        config["public-address"],
        config["port"],
        DEBUG
    )
