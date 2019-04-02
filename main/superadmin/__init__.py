#coding=utf-8

from flask import Blueprint

blueprint = Blueprint('superadmin', __name__,url_prefix='/superadmin')

from . import views
