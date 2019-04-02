# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for,current_app,session,send_from_directory, abort
from flask_login import login_required, login_user, logout_user,current_user
from flask_themes2 import get_themes_list
from sqlalchemy import desc

from main.extensions import login_manager
from main.public.forms import LoginForm
from main.public.models import *
from main.user.forms import RegisterForm
from main.user.models import User
from main.utils import flash_errors
from main.extensions import ckeditor,csrf_protect
from main.superadmin.models import CategoryAttr,UserUrlAndTemplate,UserTemplate
from main.public.fck import create_file_name


from main.fck import render,templates_required

from . import blueprint
from .fck import get_lower_id

import os,datetime



@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/')
@blueprint.route('/index')
@blueprint.route('/index/<int:id>')
@templates_required
def home(id=0):
    """Home page."""
    static_context = StaticContext.query \
        .filter_by(user=session['userid']) \
        .join(Category,Category.id==StaticContext.category) \
        .join(CategoryAttr,CategoryAttr.id==Category.attr_id) \
        .filter(CategoryAttr.url=='index') \
        .order_by(StaticContext.main_sort) \
        .all()
    return render('public/home.html',static_context=static_context)


@blueprint.route('/single')
@blueprint.route('/single/<int:id>')
@templates_required
def single(id=0):
    category = Category.query.get_or_404(id)
    static_context = StaticContext.query \
        .filter_by(user=session['userid']) \
        .join(Category,Category.id==StaticContext.category) \
        .join(CategoryAttr,CategoryAttr.id==Category.attr_id) \
        .filter(Category.id==id) \
        .order_by(StaticContext.main_sort) \
        .all()
    return render('{template}'.format(template=category.categorys_attr.templates)
            ,category=category,static_context=static_context)


@blueprint.route('/article/<int:id>')
@templates_required
def article(id=0):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    static_context = StaticContext.query \
        .filter_by(user=session['userid']) \
        .join(Category,Category.id==StaticContext.category) \
        .join(CategoryAttr,CategoryAttr.id==Category.attr_id) \
        .filter(Category.id==id) \
        .order_by(StaticContext.main_sort) \
        .all()
    id_list = [category.id]
    get_lower_id(id_list,category.id)
    pagination = Article.query.filter(Article.category.in_(id_list)).paginate(page,session['article_page'],error_out=False)
    return render('{template}'.format(template=category.categorys_attr.templates)
            ,category=category,static_context=static_context,article=pagination.items,pagination=pagination)



@blueprint.route('/photo/<int:id>')
@templates_required
def photo(id=0):
    category = Category.query \
        .filter(Category.state!=0) \
        .filter(Category.id==id) \
        .first()
    static_context = StaticContext.query \
        .filter_by(user=session['userid']) \
        .join(Category,Category.id==StaticContext.category) \
        .join(CategoryAttr,CategoryAttr.id==Category.attr_id) \
        .filter(Category.id==id) \
        .order_by(StaticContext.main_sort) \
        .all()
    #获取所有子孙栏目id
    id_list = [category.id]
    get_lower_id(id_list,category.id)
    photo = Photo.query.filter(Photo.category.in_(id_list)).all()
    #end


    return render('{template}'.format(template=category.categorys_attr.templates)
            ,category=category,static_context=static_context,photo=photo)


@blueprint.route('/show_photo/<int:id>')
@templates_required
def show_photo(id=0):
    photo=Photo.query.get_or_404(id)
    #静态内容
    static_context = []
    if photo.static_context:
        _context = photo.static_context.split('|')
    else:
        _context = session.get('photo_context','').split('|')
    for i in _context:
        static_context.append({'html':i})
    photo.update(count=photo.count+1)
    return render('show_photo.html',photo=photo,static_context=static_context)

@blueprint.route('/show_article/<int:id>')
@templates_required
def show_article(id=0):
    article = Article.query.get_or_404(id)
    static_context = []
    if article.static_context:
        _context = article.static_context.split('|')
    else:
        _context = session.get('article_context','').split('|')
    for i in _context:

        static_context.append({'html':i})

    return render('show_article.html',article=article,static_context=static_context)


@blueprint.route('/add_user_mark',methods=['POST'])
def add_user_mark():
    pageid = request.form.get('pageid','')
    name = request.form.get('name','')
    phone = request.form.get('phone','')
    content = request.form.get('message','')
    user_mark_type = request.form.get('user_mark_type','')
    url_root = request.url_root
    if not user_mark_type:
        user_mark_type  = UserMarkType.query.filter_by(user=session.get('userid')).first()
    else:
        user_mark_type  = UserMarkType.query.filter_by(user=session.get('userid')).filter_by(id=user_mark_type).first()
    
    if not name or not phone or not content:
        flash(u'请输入完整的内容.','success')
        return redirect(url_for('public.home'))

    UserMark.create(
        name=name,
        phone=phone,
        content=content,
        user=session.get('userid'),
        user_marks=user_mark_type
    )
    flash(u'内容提交成功.','success')
    if pageid:
        return redirect(url_for('.single',id=int(pageid)))
    else:
        return redirect(url_for('public.home'))



#获取缩略图
@blueprint.route("/thumbnail/<path:filename>", methods=['GET'])
def get_thumbnail(filename):
    path = os.getcwd()+'/'+current_app.config['THUMBNAIL_FOLDER']
    return send_from_directory(path, filename)



#获取原图
@blueprint.route("/images_file/<path:filename>", methods=['GET'])
def get_images_file(filename):
    path = os.getcwd()+'/'+current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)



"""
@blueprint.route("/refresh")
def refresh():
    current_app.theme_manager.refresh()
    return redirect(url_for('themes'))
"""



@blueprint.route('/files/<filename>',methods=('GET', 'POST'))
@csrf_protect.exempt
def files(filename):
    path = os.getcwd()+'/'+current_app.config['CKEDITOR_FILE_UPLOADER']
    return send_from_directory(path, filename)


@blueprint.route('/upload', methods=['GET','POST'])
@csrf_protect.exempt
@ckeditor.uploader
def upload():
    f = request.files.get('upload')
    f.filename = create_file_name(f)

    dataetime = datetime.datetime.today().strftime('%Y%m%d')
    f.filename = dataetime+'_'+f.filename
    f.filename = str(current_user.id)+'_'+f.filename

    if not os.path.isdir(current_app.config['CKEDITOR_FILE_UPLOADER']):
        os.makedirs(current_app.config['CKEDITOR_FILE_UPLOADER'])
    f.save(current_app.config['CKEDITOR_FILE_UPLOADER']+f.filename)
    url = url_for('.files', filename=f.filename)
    return url


