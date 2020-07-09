from flask import Flask

app = Flask(__name__)

#from ChinesePokerLib.modules.Webservice.app import routes
from app import routes
