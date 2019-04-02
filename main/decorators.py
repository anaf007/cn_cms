#coding=utf-8

from functools import wraps
from flask import redirect,url_for,abort,request,current_app
from flask_login import current_user


def admin_required(func):
	@wraps(func)
	def decorator(*args, **kwargs):
		if request.url_root != current_app.config['SUPERADMIN_WEB_URL']:
			abort(404)
		if not current_user.is_authenticated:
			return redirect(url_for('user.login',next='/superadmin/'))
		else:
			if not current_user.is_administrator() or not current_user.is_superadmin():
				abort(404)
		return func(*args, **kwargs)

	return decorator

