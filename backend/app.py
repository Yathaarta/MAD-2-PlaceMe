from flask import Flask
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.core import Security
from models.dbmodel import db, User, Role
from flask_cors import CORS
from async_jobs.celery_factory import celery_init_app
import os
from dotenv import load_dotenv

app = Flask(__name__)

celery_app = celery_init_app(app) 

# --------------------- CORS & COOKIE CONFIGURATION ------------------------
load_dotenv()
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

CORS(app, supports_credentials=True, origins=[frontend_url])
# ------------------------------------------------------------------------------



# ----------------- cross-port local development --------------------

if os.environ.get('FLASK_ENV') == 'production':
    # Strict settings for Azure/Vercel (HTTPS)
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
else:
    # Relaxed settings for Local Development (HTTP)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False

app.config['SESSION_COOKIE_HTTPONLY'] = True 

# ------------------------------------------------------------------------------


import controllers.config

db.init_app(app)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


import controllers.routes


@app.cli.command("init-db")
def init_db_command():
    # Will initialize database only when 'flask init-db' command is run"
    from models.init_db import init_database
    init_database()
    print("Database successfully initialized!")


if __name__=='__main__':
    app.run()