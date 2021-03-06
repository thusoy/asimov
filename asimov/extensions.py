# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

bcrypt = Bcrypt()
csrf_protect = CsrfProtect()
login_manager = LoginManager()
#TODO: expire_on_commit is mostly relevant for testing, maybe not set in prod?
db = SQLAlchemy(session_options={'expire_on_commit': False})
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
