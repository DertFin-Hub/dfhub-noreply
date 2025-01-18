import smtplib

import dotenv
from flask import Flask, request, abort
import json

app: Flask = Flask("dfhub-uptime")
config: dict = {}
DEBUG = False

@app.route("/")
def index():
    if not is_accessed_ip(request.remote_addr): abort(403)
    return "DFHub-NoReply active"

def load_config():
    """Load config and fill required fields if empty"""
    global config
    with open("config.json", 'r', encoding="utf-8") as config_file:
        config = json.loads(config_file.read())

    if not "public-address" in config:
        config["public-address"] = "127.0.0.1"
    if not "port" in config:
        config["port"] = 587

    if config["public-address"] in ["127.0.0.1", "localhost"]:
        print(f"WARNING! Server running on {config['public-address']} and can't be accessed from external network!")

def is_accessed_ip(ip: str) -> bool:
    """Check is IP address in accessed IPs list"""
    return ip in config["accessed-ips"]

if __name__ == "__main__":
    print("Loading .env file")
    dotenv.load_dotenv()
    print("Reading config.json")
    load_config()

    print("Initializing Flask server")
    app.run(
        config["public-address"],
        config["port"],
        DEBUG
    )
