#coding=utf-8
from flask_login import current_user
from . import blueprint
import os
from flask import current_app
from sqlalchemy import desc

from cn_cms.public.models import Article,Photo,Category


@blueprint.context_processor
def article():
    def get():
        return Article.query.filter_by(user=current_user.id)\
        	.join(Category,Category.id==Article.category)\
        	.filter(Category.state!=0)\
        	.order_by(desc(Article.id)).all()
    return dict(articles=get)


@blueprint.context_processor
def photo():
    def get():
        return Photo.query.filter_by(user=current_user.id) \
        	.join(Category,Category.id==Photo.category)\
        	.filter(Category.state!=0)\
        	.order_by(desc(Photo.id)).all()
    return dict(photos=get)



