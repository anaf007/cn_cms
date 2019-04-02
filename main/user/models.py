# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from main.database import Column, Model, SurrogatePK, db, reference_col, relationship
from main.extensions import bcrypt
from main.public.models import Category


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    username = Column(db.String(80), nullable=False)
    #: The hashed password
    password = Column(db.Binary(128), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30),nullable=True)
    last_name = Column(db.String(30),nullable=True)
    active = Column(db.Boolean(), default=True)
    is_admin = Column(db.Boolean(), default=False)
    phone =  Column(db.String(20))


    memory_capacity = Column(db.Integer,default=0)  #用户内存容量

    #网站名称
    web_name =Column(db.String(200))

    #网站关键词字
    web_key = Column(db.String(200))
    web_word = Column(db.String(500))

    #网站分页数据
    article_page = Column(db.Integer,default=20)
    photo_page = Column(db.Integer,default=20)

    #logo字
    web_logo_word = Column(db.String(50))
    web_logo_img = Column(db.String(200))

    #文章展示和图集展示静态内容
    article_context = Column(db.UnicodeText)
    photo_context = Column(db.UnicodeText)

    #网站状态,1正常 0前台关闭
    web_state = Column(db.Integer,default=1) 


    category = relationship('Category', backref='users',lazy='dynamic')
    banner = relationship('Banner', backref='banners',lazy='dynamic')
    static_context = relationship('StaticContext', backref='users',lazy='dynamic')
    article = relationship('Article', backref='users',lazy='dynamic')
    photo = relationship('Photo', backref='users',lazy='dynamic')
    user_url_and_template = relationship('UserUrlAndTemplate', backref='users')
    user_mark = relationship('UserMark', backref='users')
    user_mark_type = relationship('UserMarkType', backref='users')
    
    #用户模板表
    templates = reference_col('user_templates')

    def __init__(self, username, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username,**kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)

    def __str__(self):
        return 'users:%s'%self.username

    #管理员
    def is_administrator(self):
        return self.is_admin 
    def is_superadmin(self):
        return self.is_admin 





