# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_themes2 import Themes
from flask_ckeditor import CKEditor


bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
themes = Themes()
ckeditor = CKEditor()


login_manager.login_view = 'user.login'
login_manager.login_message = u"请登录后访问该页面."
#自定义消息类别
login_manager.login_message_category = "info"
#回话过期页面刷新
login_manager.refresh_view = 'user.login'
login_manager.needs_refresh_message = (u"访问超时，请重新登录")
login_manager.needs_refresh_message_category = "info"

