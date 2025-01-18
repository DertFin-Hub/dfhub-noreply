import smtplib
import dotenv
from flask import Flask

dotenv.load_dotenv()

app = Flask("dfhub-noreply")

@app.route("/")
def index():
    return "DFHub-NoReply active"

app.run()