#Makes it possible to store import code into ownLib
import sys
import os

curDir = os.path.dirname(os.path.realpath(__file__))
print(curDir+'/ownLib/')
sys.path.insert(0,curDir+'/ownLib/')
from flask import Flask
#Starts flask
#Loads config file
#Sets static folder so that if you call someting from the static folder you don't need to make a special app.path. This is easy for .css, .js or images

app = Flask(__name__)
app.config.from_object('config')
app.static_folder = 'static'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

#from app import views
import views
