import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
WEB_HOST = os.environ["WEB_HOST"]
WEB_PORT = os.environ["WEB_PORT"]

app = Flask('')

@app.route('/')
def home():
    return "Discord bot ok", 200

def run():
    app.run(host=WEB_HOST, port=WEB_PORT)

def keep_alive():
    t = Thread(target=run)
    t.start()