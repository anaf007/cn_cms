#coding=utf-8

from flask import Blueprint, flash, redirect, render_template, request, url_for, session, send_from_directory, abort
from sqlalchemy import desc

from . import blueprint

from .models import *
from main.superadmin.forms import AddTemplateForm,AddTemplateContextForm,AddTemplateCategoryAttrForm
from main.utils import flash_errors
from main.decorators import admin_required

from flask_login import login_required
from main.public.models import StaticContext
from main.user.models import User
from main.extensions import db

@blueprint.route('/')
@admin_required
def home():
    return render_template('superadmin/home.html')


@blueprint.route('/usertemplates')
@admin_required
def usertemplates():
    return render_template('superadmin/usertemplates.html')


@blueprint.route('/addtemplates')
@admin_required
def addtemplates():
    form = AddTemplateForm()
    return render_template('superadmin/addtemplates.html',form=form)

@blueprint.route('/addtemplates', methods=['POST'])
@admin_required
def addtemplates_post():
    form = AddTemplateForm(request.form)
    if form.validate_on_submit():
        UserTemplate.create(
            name=form.title.data
        )
        flash(u'添加成功！')
    else:
        flash_errors(form)

    return redirect(url_for('.addtemplates'))

@blueprint.route('/addtemplates_context', methods=["GET"])
def addtemplates_context():
    form = AddTemplateContextForm()
    usertemplate = UserTemplate.query.filter_by(is_end=False).order_by('id').all()
    return render_template('superadmin/addtemplates_context.html',form=form,usertemplate=usertemplate)


@blueprint.route('/addtemplates_context/', methods=["POST"])
@login_required
def addtemplates_context_post():
    form = AddTemplateContextForm(request.form)
    category = 	CategoryAttr.query.get_or_404(request.form.get('category','0'))
    if form.validate_on_submit():
        TemplatesDefault.create(
            main_sort = form.main_sort.data,
            html = form.html.data,
            # template = usertemplate,
            category_attrs = category
        )
        flash(u'添加成功！模板栏目：%s,排序：%s,内容：“%s”'%(category.name,form.main_sort.data,form.html.data),'success')
    else:
        flash_errors(form)
    # form.category.data = (usertemplate.id,usertemplate.name)
    return redirect(url_for('.addtemplates_context'))


#添加模板栏目属性：文章、图集、内容页
@blueprint.route('/addtemplates_attr',methods=["GET"])
def addtemplates_attr():
	form = AddTemplateCategoryAttrForm()	
	return render_template('superadmin/addtemplates_attr.html',form=form)



@blueprint.route('/addtemplates_attr/',methods=["POST"])
@login_required
def addtemplates_attr_post():

	form = AddTemplateCategoryAttrForm(request.form)
	usertemplate = UserTemplate.query.get_or_404(form.user_template.data)
	if form.validate_on_submit():
		CategoryAttr.create(
			name = form.name.data,
			summary = form.summary.data,
			mark = form.mark.data,
			url = form.url.data,
			templates = form.templates.data,
			usertemplate = usertemplate
		)
		flash(u'添加成功！','success')
	else:
		flash_errors(form)
	form.user_template.data = (usertemplate.id,usertemplate.name)
	return redirect(url_for('.addtemplates_attr'))


#栏目默认内容
@blueprint.route('/templates_context',methods=["GET"])
def templates_context():
	form = AddTemplateContextForm()
	usertemplate = UserTemplate.query.filter_by(is_end=False).order_by('id').all()
	template_default =  TemplatesDefault.query.order_by('user_template_category,main_sort').all()
	return render_template('superadmin/templates_context.html',
		form=form,usertemplate=usertemplate,
		template_default=template_default)


#更新模板内容到用户模板内容
@blueprint.route('/updatecontext',methods=["GET"])
def updatecontext():
	templatedefault = TemplatesDefault.query.all()
	
	for i in templatedefault:
		static_user = StaticContext()
		static_user.html = i.html
		static_user.main_sort = i.main_sort
		static_user.default_html = i.html
		static_user.user = 2
		db.session.add(static_user)
	db.session.commit()

	return  'ok'


@blueprint.route('/usermanager',methods=["GET"])
def usermanager():

	return render_template('superadmin/usermanager.html')


@blueprint.route('/all_users',methods=["GET"])
def all_users():

    return render_template('superadmin/all_users.html',all_users=User.query.all())


@blueprint.route('/user_url_template', methods=["GET"])
def user_url_template():
	all_users_url_templates = UserUrlAndTemplate.query.order_by(desc(UserUrlAndTemplate.id)).all()
	return render_template('superadmin/user_url_template.html',all_users_url_templates=all_users_url_templates)


@blueprint.route('/add_user_url_templates', methods=["GET"])
def add_user_url_templates():
	return render_template('superadmin/add_user_url_templates.html')


@blueprint.route('/add_user_url_templates', methods=["POST"])
def add_user_url_templates_post():
	username =  request.form.get('username')
	user_templates =  request.form.get('user_templates')
	user_url =  request.form.get('user_url')
	add_dic = {}
	if username:
		user = User.query.filter(username=username).first()
		if user:
			add_dic['username'] = user
	else:
		add_dic['username'] = None
	add_dic['template'] = user_templates
	add_dic['user_url'] = user_url
	user_templates = user_templates
	user_url = user_url
	if not username:
		username = None
	else:
		username = User.query.filter_by(username=username).first()
	user_templates = UserTemplate.query.filter_by(name=user_templates).first()

	
	UserUrlAndTemplate.create(
		user=username,
		usertemplate=user_templates,
		user_url=user_url,
		end_time_at= request.form.get('end_time_at') ,
	)
	flash(u'添加完成','success')
	return redirect(url_for('superadmin.add_user_url_templates'))


@blueprint.route('/edit_user_url_templates/<int:id>', methods=["GET"])
def edit_user_url_templates(id=0):
	uut = UserUrlAndTemplate.query.get_or_404(id)
	return render_template('superadmin/edit_user_url_templates.html',user_url_template=uut)


@blueprint.route('/edit_user_url_templates', methods=["POST"])
def edit_user_url_templates_post(id=0):
	username =  request.form.get('username')
	user_templates =  request.form.get('user_templates')
	user_url =  request.form.get('user_url')
	user_url_template_id =  request.form.get('id')

	if not username:
		username = None
	else:
		username = User.query.filter_by(username=username).first()
	user_templates = UserTemplate.query.filter_by(name=user_templates).first()

	user_url_template = UserUrlAndTemplate.query.get_or_404(user_url_template_id)
	
	user_url_template.update(
		user_url=user_url,
		users=username,
		usertemplate=user_templates,	
		end_time_at= request.form.get('end_time_at'),	
	)
	# username.update(usertemplate = user_url_template)
	flash(u'更新完成','success')
	return redirect(url_for('superadmin.edit_user_url_templates',id=user_url_template_id)) 


@blueprint.route('/all_version')
def all_version():
	return render_template('superadmin/all_version.html',version=SystemVersion.query.order_by(desc('id')).all())


@blueprint.route('/add_version',methods=['GET'])
def add_version():
	version = SystemVersion.query.order_by(desc('id')).first()
	return render_template('superadmin/add_version.html',version=version)


@blueprint.route('/add_version',methods=['POST'])
def add_version_post():
	
	SystemVersion.create(
		number=request.form.get('number',' '),
		title=request.form.get('title',' '),
		summary=request.form.get('summary',' '),
		context=request.form.get('context',' '),	
	)
	flash(u'添加完成.','success')
	return redirect(url_for('.all_version'))












