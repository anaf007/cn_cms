#coding=utf-8
from flask_login import current_user
from .models import Banner,Category,StaticContext,Article,Photo
from . import blueprint
from sqlalchemy import desc
from flask import session

@blueprint.context_processor
def banner():
    def get():
        return Banner.query.filter_by(user=session['userid']).order_by('sort').all()
    return dict(banner=get)


#iparent_id = 1顶级栏目
@blueprint.context_processor
def navcat():
	def get():
		return Category.query.filter_by(user=session['userid']).order_by('sort').filter_by(parent_id=1).filter_by(state=1).all()
	return dict(navcat=get)



#首页展示文章列
@blueprint.context_processor
def main_article():
	def get(main_sort):
		category = Category.query.filter_by(user=session['userid']).filter_by(main_sort=main_sort).first()
		if category:
			return Article.query.filter_by(category=category.id).filter_by(attr_id=2).all()
		else:
			return []
	return dict(main_article=get)


#获得所有图集
@blueprint.context_processor
def get_all_photo():
	def get():
		photo = Photo.query.filter_by(user=session.get('userid')).order_by(desc(Photo.id)).all()
		return photo
	return dict(get_all_photo=get)



#面包屑
@blueprint.context_processor
def breadcrumb():
	def get(id):
		return []
	return dict(breadcrumb=get)

