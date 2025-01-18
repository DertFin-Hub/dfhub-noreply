import sys
import dotenv
import os

import smtplib
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from flask import Flask, request, abort
import json

from requests.exceptions import InvalidHeader

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
        smtp.sendmail(os.getenv("DFHUB_NOREPLY_APP_MAIL"), json_body["to"], f"Subject: {json_body["subject"]}\n\n{json_body["context"]}".encode("utf-8"))
        return "Message request sent!"
    except SMTPException:
        return abort(500, "An internal error occurred while sending a message")

@app.route("/api/v1/send-html-url", methods=["POST"])
def send_html_url():
    """
    Send a message with HTML-content that is delivered via a link
    """
    json_body = request.json

    if not "to" in json_body:
        abort(400, description="JSON param \"to\" is not specified!")
    if not "subject" in json_body:
        abort(400, description="JSON param \"subject\" is not specified!")
    if not "attachment-url" in json_body:
        abort(400, description="JSON param \"attachment-url\" is not specified!")

    msg = MIMEMultipart("message")
    msg["Subject"] = json_body["subject"]
    msg["From"] = os.getenv("DFHUB_NOREPLY_APP_MAIL")
    msg["To"] = json_body["to"]

    try:
        html = requests.get(json_body["attachment-url"]).content.decode("utf-8")
    except Exception:
        abort(500, "Cannot get the specified resource (attachment_url)!")
    attachment = MIMEText(html, "html")
    msg.attach(attachment)
    smtp.send_message(msg)

    return "Message request sent!"

@app.route("/api/v1/send-html", methods=["POST"])
def send_html():
    """
    Send a message with HTML-content specified in json param
    """
    json_body = request.json

    if not "to" in json_body:
        abort(400, description="JSON param \"to\" is not specified!")
    if not "subject" in json_body:
        abort(400, description="JSON param \"subject\" is not specified!")
    if not "context" in json_body:
        abort(400, description="JSON param \"context\" is not specified!")

    msg = MIMEMultipart("message")
    msg["Subject"] = json_body["subject"]
    msg["From"] = os.getenv("DFHUB_NOREPLY_APP_MAIL")
    msg["To"] = json_body["to"]

    attachment = MIMEText(json_body["context"], "html")
    msg.attach(attachment)
    smtp.send_message(msg)

    return "Message request sent!"

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
        if config["is-ssl"]:
            smtp = smtplib.SMTP_SSL(config["smtp-address"], config["smtp-port"])
            smtp.ehlo()
        else:
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
