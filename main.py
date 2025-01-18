import smtplib
import sys
from smtplib import SMTPException

import dotenv
from flask import Flask, request, abort
import json

import os

app: Flask = Flask("dfhub-uptime")
config: dict = {}
DEBUG = False
smtp = smtplib.SMTP()

@app.route("/")
def index():
    if not is_accessed_ip(request.remote_addr): abort(403, description="Your IP address is not in allowed IPs list")
    return "DFHub-NoReply active"

# API v1

@app.route("/api/v1/send-raw", methods=["POST"])
def send_raw():
    """
    Send raw message. Check required request args in README.md
    :return:
    """
    json_body = request.json

    if not "to" in json_body:
        abort(400, description="JSON param \"to\" is not specified!")
    if not "subject" in json_body:
        abort(400, description="JSON param \"subject\" is not specified!")
    if not "context" in json_body:
        abort(400, description="JSON param \"context\" is not specified!")

    try:
        smtp.sendmail(os.getenv("DFHUB_NOREPLY_APP_MAIL"), json_body["to"], f"Subject: {json_body["subject"]}\n\n{json_body["context"]}")
        return "Message request sent!"
    except SMTPException:
        return abort(500, "An internal error occurred while sending a message")

# Other methods

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

def init_smtp() -> bool:
    global smtp
    global config
    """
    Initialize SMTP-server connection
    :return: Status (success/error)
    """
    if os.getenv("DFHUB_NOREPLY_APP_MAIL") in [None, ""]:
        print("Environment \"DFHUB_NOREPLY_APP_MAIL\" is not specified!")
        return False

    if os.getenv("DFHUB_NOREPLY_APP_TOKEN") in [None, ""]:
        print("Environment \"DFHUB_NOREPLY_APP_TOKEN\" is not specified!")
        return False

    if not "smtp-address" in config or config["smtp-address"] == "":
        print("Config param \"smtp-address\" is not specified!")
        return False

    if not "smtp-port" in config:
        print("Config param \"smtp-port\" is not specified!")
        return False

    try:
        smtp = smtplib.SMTP(config["smtp-address"], config["smtp-port"])
        smtp.ehlo()
        smtp.starttls()
    except SMTPException:
        print("Can't connect to SMTP server")
        return False

    try:
        smtp.login(os.getenv("DFHUB_NOREPLY_APP_MAIL"), os.getenv("DFHUB_NOREPLY_APP_TOKEN"))
    except SMTPException:
        print("The SMTP server rejected authorization. The information may be incorrect")
        return False

    return True

if __name__ == "__main__":
    print("Loading .env file")
    dotenv.load_dotenv()

    print("Reading config.json")
    load_config()

    print("Connecting to SMTP server...")
    if not init_smtp():
        sys.exit(0)

    print("Initializing Flask server")
    app.run(
        config["public-address"],
        config["port"],
        DEBUG
    )
