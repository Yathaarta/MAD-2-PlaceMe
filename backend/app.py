from flask import Flask
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.core import Security
from models.dbmodel import db, User, Role
from flask_cors import CORS
from celery_factory import celery_init_app

app = Flask(__name__)


# --------------------- CORS & COOKIE CONFIGURATION ------------------------
CORS(app, 
     supports_credentials=True, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173"])
# ------------------------------------------------------------------------------



# ----------------- cross-port local development --------------------
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
app.config['SESSION_COOKIE_SECURE'] = False 
app.config['SESSION_COOKIE_HTTPONLY'] = True 
# ------------------------------------------------------------------------------


import controllers.config


# ---------------------------- CELERY CONFIGURATION ----------------------------
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/1",
        include=['tasks'] # tells celery where to find @shared_tasks
    ),
)
celery_app = celery_init_app(app)
# ------------------------------------------------------------------------------


db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from models.init_db import init_database
init_database()


import controllers.routes

if __name__=='__main__':
    app.run()