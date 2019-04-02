#coding=utf-8

import time
from datetime import datetime, timedelta
from flask import session, abort, current_app, request, flash, redirect, url_for
from flask_themes2 import render_theme_template


from functools import wraps

from main.superadmin.models import UserUrlAndTemplate


#:themes templates 
def templates_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if request.url_root!=session['url']:
                raise
            if session['theme']:
                pass
        except Exception as e:
            userurl = UserUrlAndTemplate.query.filter_by(user_url=request.url_root).first()
            if not userurl:
                flash(u'该网址未绑定！请联系管理员！','danger')
                abort(401)

            if userurl.usertemplate.name not in current_app.theme_manager.themes:
                flash(u'模板名称不正确！请联系管理员！','danger')
                abort(401)
            if userurl.end_time_at<datetime.now():
                flash(u'该网站的服务时间已到期！请续费后再访问。详情访问：www.anaf.cn','danger')
                abort(401)

            if not userurl.user:
                return redirect(url_for('user.register_user'))
            user = userurl.users
            session['theme'] = userurl.usertemplate.name
            #这里不能使用user_id而使用了userid,因为会自动登录导致后台自动登录了
            session['userid'] = user.id
            #网站相关配置
            session['url'] = userurl.user_url
            session['article_page'] = user.article_page
            session['photo_page'] = user.photo_page
            session['web_logo_word'] = user.web_logo_word
            session['web_logo_img'] = user.web_logo_img
            session['web_key'] = user.web_key
            session['web_word'] = user.web_word
            session['article_context'] = user.web_word
            session['pgoto_context'] = user.web_word

        return f(*args, **kwargs)
    return decorated_function


#:themes render
def render(template, **context):
    theme = session.get('theme', current_app.config['DEFAULT_THEME'])
    return render_theme_template(theme, template, **context)


