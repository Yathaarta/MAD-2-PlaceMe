from flask import Flask
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.core import Security
from models.dbmodel import db, User, Role
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

import controllers.config



db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from models.init_db import init_database
init_database()

import controllers.routes

if __name__=='__main__':
    app.run()