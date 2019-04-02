# -*- coding: utf-8 -*-
"""User views."""

import os,datetime,hashlib,time,random,json

from flask import Blueprint, render_template,request,flash,redirect,\
	url_for, send_from_directory, current_app, session,abort
from flask_login import login_required,login_user,logout_user,current_user
from werkzeug.utils import secure_filename
from sqlalchemy import desc

from .forms import LoginForm,AllCategoryForm,AllCategoryAttrForm,AllBannerForm, \
	AllStaticContextForm,ArticleForm,PhotoForm,RegisterForm,WebConfigForm

from . import blueprint
from .models import User
from main.superadmin.models import UserUrlAndTemplate
from main.public.models import *
from main.superadmin.models import CategoryAttr,TemplatesDefault

from main.extensions import db
from main.utils import flash_errors
from main.extensions import ckeditor

from main.fck import render
from main.public.fck import create_thumbnail,allowed_file,create_file_name



@blueprint.route('/')
@login_required
def members():
    """List members."""
    return render_template('users/members.html')

@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))

@blueprint.route('/login/',methods=["GET","POST"])
def login():
	form = LoginForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			login_user(form.user)
			flash(u'您已登录.', 'success')
			redirect_url = request.args.get('next') or url_for('user.members')
			return redirect(redirect_url)
		else:
			flash_errors(form)
	
	return render_template('users/login.html',form=form)

@blueprint.route('/all_banner/',methods=['GET'])
@login_required
def all_banner():
	form = AllBannerForm(request.form)

	banner = Banner.query.filter_by(user=current_user.id).order_by('sort').all()
	return render('users/all_banner.html',form=form,
		banner=banner)

@blueprint.route('/all_banner/',methods=['POST'])
@login_required
def all_banner_post():
	form = AllBannerForm(request.form)

	if form.validate_on_submit():
		f = request.files['image']

		filename = secure_filename(f.filename)
		if not filename:
			flash(u'请选择图片','error')
			return redirect(url_for('.all_banner'))
		if not allowed_file(f.filename):
			flash(u'图文件名或格式错误。','error')
			return redirect(url_for('.all_banner'))

		dataetime = datetime.datetime.today().strftime('%Y%m%d')
		file_dir = 'users/%s/banner/%s/'%(current_user.id,dataetime)
		if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
			os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)
		f.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)

		Banner.create(
			title = form.title.data,
			summary = form.summary.data,
			alt = form.alt.data,
			sort = form.sort.data,
			image = file_dir+filename,
			user = current_user.id
		)
		flash(u'添加成功！','success')
	else:
		flash_errors(form)

	return redirect(url_for('.all_banner'))

#所有栏目
@blueprint.route('/all_category/',methods=["GET"])
@login_required
def all_category():
	form = AllCategoryForm(request.form)

	category = Category.query.filter_by(users=current_user).filter_by(state=1).order_by('sort').all()
	return render('users/all_category.html',form=form,
		category=category)


@blueprint.route('/all_category/',methods=["POST"])
@login_required
def all_category_post():
	form = AllCategoryForm(request.form)
	if form.validate_on_submit():
		if form.pid.data == -1:
			form.pid.data = 1
		category = Category.create(
			title = form.title.data,
			summary = form.summary.data,
			key = form.key.data,
			word = form.word.data,
			sort = form.sort.data,
			main_sort = form.main_sort.data,
			is_enable = form.is_enable.data,
			user = current_user.id,
			attr_id = form.attr.data,
			parent_id = form.pid.data,
		)
		templates_default = TemplatesDefault.query.filter_by(user_template_category=form.attr.data).all()
		fake_static_context = []
		#创建栏目默认内容
		for i in templates_default:
			fake_static_context.append(
				StaticContext(
					html = i.html,
					default_html = i.html,
					main_sort = i.main_sort,
					users = current_user,
					categorys = category
				)
			)
			
		db.session.add_all(fake_static_context)
		db.session.commit()

		flash(u'添加成功！','success')
	else:
		flash_errors(form)

	return redirect(url_for('.all_category'))
  

#所有栏目属性
@blueprint.route('/all_category_attr/',methods=["GET"])
@login_required
def all_category_attr():
	form = AllCategoryAttrForm(request.form)
	category_attr = CategoryAttr.query.filter_by(usertemplate_id=current_user.templates).all()
	return render('users/all_category_attr.html',form=form,
		category_attr=category_attr)


@blueprint.route('/edit_category/<int:id>',methods=["GET"])
@login_required
def edit_category(id=0):
	category = Category.query.get_or_404(id)
	form = AllCategoryForm()
	form.title.data = category.title
	form.summary.data = category.summary
	form.key.data = category.key
	form.word.data = category.word
	form.sort.data = category.sort
	form.is_enable.data = category.is_enable
	form.main_sort.data = category.main_sort

	return render('users/edit_category.html',form=form,id=category.id)


@blueprint.route('/edit_category',methods=["POST"])
@login_required
def edit_category_post():
	form = AllCategoryForm(request.form)
	id = request.form.get('id','0')
	category = Category.query.get_or_404(id)
	print(form)
	if form.validate_on_submit():
		category.update(
			title = form.title.data,
			summary = form.summary.data,
			key = form.key.data,
			word = form.word.data,
			sort = form.sort.data,
			main_sort = form.main_sort.data,
			is_enable = form.is_enable.data,
			attr_id = form.attr.data,
		)
		flash(u'更新成功！','success')
	else:
		flash_errors(form)

	return redirect(url_for('.all_category'))


@blueprint.route('/del_banner/<int:id>',methods=["GET"])
@login_required
def del_banner(id=0):
	banner = Banner.query.get_or_404(id)
	banner.delete()
	flash(u'删除完成')
	return redirect(url_for('.all_banner'))



@blueprint.route('/all_static_context/',methods=["GET"])
@login_required
def all_static_context():
	context = StaticContext.query \
		.join(Category,Category.id==StaticContext.category) \
		.filter(Category.state!=0) \
		.filter(StaticContext.users==current_user) \
		.order_by(StaticContext.category,StaticContext.main_sort) \
		.all()
	form = AllStaticContextForm()
	return render_template('users/all_static_context.html',context=context,form=form)

#用户不能添加删除
@blueprint.route('/all_static_context/',methods=["POST"])
@login_required
def all_static_context_post():
	form = AllStaticContextForm(request.form)
	if form.validate_on_submit():
		"""
		StaticContext.create(
			main_sort = form.main_sort.data,
			html = form.html.data,
			user = current_user.id
		)
		"""
		flash(u'添加成功！','success')
	else:
		flash_errors(form)

	return redirect(url_for('.all_static_context'))


#用户不能删除
@blueprint.route('/del_static_context/<int:id>',methods=["GET"])
@login_required
def del_static_context(id=0):
	staticcontext = StaticContext.query.get_or_404(id)
	"""
	staticcontext.delete()
	"""
	flash(u'删除完成')
	return redirect(url_for('.all_static_context'))

@blueprint.route('/edit_static_context/<int:id>',methods=["GET"])
@login_required
def edit_static_context(id=0):
	context = StaticContext.query.filter_by(user=current_user.id).order_by('category,main_sort').all()
	one_context = StaticContext.query.get_or_404(id)
	if one_context.users !=current_user:
		abort(404)
	form = AllStaticContextForm()
	form.main_sort.data = one_context.main_sort
	form.html.data = one_context.html
	hidden_id = one_context.id
	return render_template('users/all_static_context.html',context=context,form=form,hidden_id=hidden_id)


@blueprint.route('/edit_static_context',methods=["POST"])
@login_required
def edit_static_context_post(id=0):
	form = AllStaticContextForm(request.form)
	if form.validate_on_submit():
		staticcontext = StaticContext.query.get_or_404(request.form.get('id','0'))
		if staticcontext.users !=current_user:
			abort(404)
		staticcontext.update(
			main_sort = form.main_sort.data,
			html = form.html.data
		)
		flash(u'更新成功！','success')
	else:
		flash_errors(form)

	return redirect(url_for('.all_static_context'))



@blueprint.route('/all_article',methods=['GET'])
@login_required
def all_article():
	form = ArticleForm()
	return render_template('users/all_article.html',form=form)


@blueprint.route('/all_article',methods=['POST'])
@login_required
def add_article_post():
	form = ArticleForm(request.form)

	if form.validate_on_submit():

		f = request.files['image']
		
		if not f:
			flash(u'请选择缩略图。','error')
			return redirect(url_for('.all_article'))
		if not allowed_file(f.filename):
			flash(u'缩略图文件名或格式错误。','error')
			return redirect(url_for('.all_article'))

		#32位哈希名
		filename = create_file_name(f)

		dataetime = datetime.datetime.today().strftime('%Y%m%d')
		file_dir = 'users/%s/article/%s/'%(current_user.id,dataetime)
		
		if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
			os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)

		f.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)
		create_thumbnail(f,80,file_dir,filename)


		Article.create(
			title = form.title.data,
			author = form.author.data,
			source = form.source.data,
			summary = form.summary.data,
			key = form.key.data,
			word = form.word.data,
			is_enable = form.is_enable.data,
			content = form.content.data,
			count = form.count.data,
			image_alt = form.alt.data,
			image = file_dir+filename,
			user = current_user.id,
			attr_id = form.attr.data,
			category = form.category.data,
			static_context = form.static_context.data
		)
		flash(u'添加成功！','success')
	else:
		flash_errors(form)

	return redirect(url_for('.all_article'))


@blueprint.route('/all_photo',methods=['GET'])
@login_required
def all_photo():
	form = PhotoForm()
	return render_template('users/all_photo.html',form=form)


@blueprint.route('/add_photo',methods=['POST'])
@login_required
def add_photo_post():
	form = PhotoForm(request.form)

	if form.validate_on_submit():
		f = request.files['image']

		if not f:
			flash(u'请选择缩略图。','error')
			return redirect(url_for('.all_photo'))
		if not allowed_file(f.filename):
			flash(u'缩略图文件名或格式错误。','error')
			return redirect(url_for('.all_photo'))
		photos_date = request.form.get('photos_date','')
		from datetime import datetime as dt
		if not photos_date:
			photos_date = datetime.datetime.today().strftime('%Y-%m-%d')
		else:
			try:
				photos_date = dt.strptime(photos_date,'%Y-%m-%d')			
			except Exception as e:
				flash(u'拍摄时间格式填写错误。%s'%str(e),'error')
				return redirect(url_for('.all_photo'))
			


		filename = create_file_name(f)

		dataetime = datetime.datetime.today().strftime('%Y%m%d')
		file_dir = 'users/%s/photos/%s/'%(current_user.id,dataetime)

		if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
			os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)

		f.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)
		create_thumbnail(f,80,file_dir,filename)



		Photo.create(
			title = form.title.data,
			summary = form.summary.data,
			key = form.key.data,
			word = form.word.data,
			count = form.count.data,
			image_alt = form.image_alt.data,
			image = file_dir+filename,
			user = current_user.id,
			attr_id = form.attr.data,
			category = form.category.data,
			photos_date = photos_date,
			static_context = form.static_context.data
		)
		flash(u'添加成功！','success')
	else:
		flash_errors(form)
	return redirect(url_for('.all_photo'))


@blueprint.route('/usermark',methods=['GET'])
@login_required
def usermark():
	user_mark = UserMark.query.filter_by(users=current_user).order_by(desc(UserMark.creation_date)).all()

	return render_template('users/user_mark.html',user_mark=user_mark)


@blueprint.route('/add_photo_image/<int:id>',methods=['GET'])
@login_required
def add_photo_image(id=0):
	photo = Photo.query.get_or_404(id)
	if photo.users != current_user:
		flash(u'操作失败，非法操作','error')
		return redirect(url_for('user.members'))

	return render_template('users/add_photo_image.html',
		photo=photo)


@blueprint.route('/add_photo_image',methods=['POST','GET'])
@login_required
def add_photo_image_post(id=0):
	files = request.files['file']
	if files:
		try:
			filename = secure_filename(files.filename)

			filename = create_file_name(files)
			dataetime = datetime.datetime.today().strftime('%Y%m%d')
			file_dir = 'users/%s/photos_list/%s/'%(current_user.id,dataetime)

			if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
				os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)

			# mime_type = files.content_type
			if  allowed_file(files.filename):
				
				files.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)

				PhotoImage.create(
					path = file_dir+filename,
					photo = request.form.get('id','')
				)
				
				return json.dumps({'initialPreview':['%s<br>上传成功。'%files.filename]})
	
		except Exception as e:

			return json.dumps({'error':str(e)})
	return json.dumps({'error':u'上传失败'})


@blueprint.route('/delete_photo_image/<int:id>',methods=['GET'])
@login_required
def delete_photo_image(id=0):
	photoimage = PhotoImage.query.get_or_404(id)
	if photoimage.photo_images.users !=current_user:
		flash(u'删除失败，非法操作','error')
		return redirect(url_for('user.members'))
	returnid = photoimage.photo
	photoimage.delete(True)
	flash(u'删除成功','success')
	return redirect(url_for('user.add_photo_image',id=returnid))


@blueprint.route('/delete_photo/<int:id>',methods=['GET'])
@login_required
def delete_photo(id=0):
	photo =Photo.query.get_or_404(id)
	if photo.users != current_user:
		flash(u'删除失败，非法操作','error')
		return redirect(url_for('user.members'))
	for i in photo.photo_image:
		i.delete(False)
	photo.delete(True)
	flash(u'删除成功','success')
	return redirect(url_for('user.all_photo'))


@blueprint.route('/delete_category/<int:id>',methods=['GET'])
@login_required
def delete_category(id=0):
	category =Category.query.get_or_404(id)
	if category.users != current_user:
		flash(u'删除失败，非法操作','error')
		return redirect(url_for('user.members'))
	category.update(state=0)
	flash(u'删除成功','success')
	return redirect(url_for('user.all_category'))


@blueprint.route('/delete_article/<int:id>',methods=['GET'])
@login_required
def delete_article(id=0):
	article = Article.query.get_or_404(id)
	if article.users != current_user:
		flash(u'删除失败，非法操作','error')
		return redirect(url_for('user.members'))
	article.delete()
	flash(u'删除成功','success')
	return redirect(url_for('user.all_article'))



@blueprint.route('/edit_article/<int:id>',methods=['GET'])
@login_required
def edit_article(id=0):
	article = Article.query.get_or_404(id)

	form = ArticleForm()
	form.title.data = article.title
	form.author.data = article.author
	form.source.data = article.source
	form.summary.data = article.summary
	form.key.data = article.key
	form.word.data = article.word
	form.is_enable.data = article.is_enable
	form.count.data = article.count
	form.alt.data = article.image_alt
	form.attach_key.data = article.attach_key
	form.attach_value.data = article.attach_value
	form.content.data = article.content
	form.static_context.data = article.static_context


	form.attr.choices.insert(0, (article.content_attrs.id,article.content_attrs.name))
	form.category.choices.insert(0, (article.categorys.id,article.categorys.title))

	if not article.image:
		image = 'not_article_image'
	else:
		image = article.image

	return render_template('users/edit_article.html',form=form,id=article.id,image=image)


@blueprint.route('/edit_save_article_post',methods=['POST'])
@login_required
def edit_save_article_post():
	form = ArticleForm(request.form)
	article = Article.query.get_or_404(request.form.get('id',0))
	if article.users != current_user:
		abort(404)

	if form.validate_on_submit():

		f = request.files['image']
		
		if f:
			if not allowed_file(f.filename):
				flash(u'缩略图文件名或格式错误。','error')
				return redirect(url_for('.edit_article',id=request.form.get('id',0)))

			#32位哈希名
			filename = create_file_name(f)

			dataetime = datetime.datetime.today().strftime('%Y%m%d')
			file_dir = 'users/%s/article/%s/'%(current_user.id,dataetime)
			
			if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
				os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)

			f.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)
			if not form.img_width.data:
				form.img_width.data = 80
			create_thumbnail(f,int(form.img_width.data),file_dir,filename)

			article.update(image=file_dir+filename)


		article.update(
			title = form.title.data,
			author = form.author.data,
			source = form.source.data,
			summary = form.summary.data,
			key = form.key.data,
			word = form.word.data,
			is_enable = form.is_enable.data,
			content = form.content.data,
			count = form.count.data,
			image_alt = form.alt.data,
			user = current_user.id,
			attr_id = form.attr.data,
			category = form.category.data,
			static_context = form.static_context.data,
		)
		flash(u'更新成功！','success')
	else:
		flash_errors(form)

	return redirect(url_for('.edit_article',id=request.form.get('id',0)))


@blueprint.route('/user_config',methods=['GET'])
@login_required
def user_config():
	form = WebConfigForm()
	form.web_name.data = current_user.web_name
	form.web_key.data = current_user.web_key
	form.web_word.data = current_user.web_word
	form.article_page.data = current_user.article_page
	form.photo_page.data = current_user.photo_page
	form.web_logo_word.data = current_user.web_logo_word
	form.article_context.data = current_user.article_context
	form.photo_context.data = current_user.photo_context
	if not current_user.web_logo_img:
		image = 'not_logo_image'
	else:
		image = current_user.web_logo_img

	return render_template('users/user_config.html',form=form,image=image)


@blueprint.route('/user_config',methods=['POST'])
@login_required
def user_config_post():
	form = WebConfigForm()
	if form.validate_on_submit():
		if request.form.get('state'):
			state = True
		else:
			state = False

		f = request.files['image']
		
		if f:
			if not allowed_file(f.filename):
				flash(u'LOGO文件名或格式错误。','error')
				return redirect(url_for('.user_config'))

			#32位哈希名
			filename = create_file_name(f)

			dataetime = datetime.datetime.today().strftime('%Y%m%d')
			file_dir = 'users/%s/logo/%s/'%(current_user.id,dataetime)
			
			if not os.path.isdir(current_app.config['UPLOADED_PATH']+file_dir):
				os.makedirs(current_app.config['UPLOADED_PATH']+file_dir)

			f.save(current_app.config['UPLOADED_PATH'] +file_dir+filename)
			

			current_user.update(web_logo_img=file_dir+filename)

		current_user.update(
			web_name = form.web_name.data,
			web_key = form.web_key.data,
			web_word = form.web_word.data,
			article_page = form.article_page.data,
			photo_page = form.photo_page.data,
			web_logo_word = form.web_logo_word.data,
			article_context = form.article_context.data,
			photo_context = form.photo_context.data,
			web_state = state
		)
		flash(u'更新成功！','success')

	else:
		flash_errors(form)

	return redirect(url_for('.user_config'))



@blueprint.route('/adduser/',methods=["GET"])
def register_user():
	form = RegisterForm()
	return render_template('users/adduser.html',form=form)


@blueprint.route('/adduser/',methods=["POST"])
def register_user_post():
	form = RegisterForm(request.form)

	if form.validate_on_submit():

		userurl = UserUrlAndTemplate.query.filter_by(user_url=request.url_root).first()

		user = User.create(
			username = form.username.data,
			password = form.password.data,
			first_name = form.first_name.data,
			phone = form.phone.data,
			memory_capacity = userurl.usertemplate.memory_capacity,
			usertemplate = userurl.usertemplate,
		)
		userurl.update(users=user)

		flash(u'保存设置成功！','success')		

	else:
		flash_errors(form)
		return render_template('users/adduser.html',form=form)

	return render_template('users/register_success.html',index=request.url_root)



