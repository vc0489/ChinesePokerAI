#from ChinesePokerLib.modules.Webservice.app import app
from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
