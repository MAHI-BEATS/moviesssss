from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Jisshu bots"
    
    # Load plugins
from plugins import load_plugins
plugins = load_plugins(app)

# Start premium checker
import asyncio
from webapp import check_expired_premium
asyncio.create_task(check_expired_premium(app))
