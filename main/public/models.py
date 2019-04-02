# -*- coding: utf-8 -*-
"""Public models."""
import datetime as dt

from main.database import Column, Model, SurrogatePK, db, reference_col, relationship
from main.extensions import bcrypt


class Category(SurrogatePK,Model):

	__tablename__ = 'categorys'
	#:栏目标题
	title = Column(db.String(80),nullable=False)
	#:栏目描
	summary = Column(db.String(100))
	#:关键字
	key =  Column(db.String(80))
	#:关键描述
	word = Column(db.String(500))
	#:创建时间
	creation_date = Column(db.DateTime(),default=dt.datetime.now)
	#:排序
	sort = Column(db.Integer,default=100)
	#:是否显示
	is_enable = Column(db.Boolean,default=True)
	#:首页展示顺序
	main_sort = Column(db.Integer,default=100)
	#:栏目静态内容
	static_content = Column(db.UnicodeText)
	#:附加内容
	attach_value = Column(db.UnicodeText)
	#状态  0用户删除不做正式删除   1正常
	state = Column(db.Integer,default=1)

	attr_id = reference_col('category_attrs')
	#:所属用户栏目
	user = reference_col('users')
	#:引用自身无限级分类
	parent_id = reference_col('categorys')
	children = relationship("Category",lazy="joined",join_depth=2,post_update=True)

	#所属文章
	article = relationship('Article', backref='categorys',lazy='dynamic')
	#所属图集
	photo = relationship('Photo', backref='categorys',lazy='dynamic')
	#栏目静态内容
	static_context = relationship('StaticContext', backref='categorys',lazy='dynamic')
	 

	def __repr__(self):
		return '<CategoryAttr({name!r})>'.format(name=self.title)


class ContentAttr(SurrogatePK, Model):
	"""内容属性，
	默认的三个类型选项，mark标记唯一
	用户无法更改
	数据库 读取mark标记  #普通common 首页home  热门hot  推荐recd
	"""

	__tablename__ = 'content_attrs'

	name = Column(db.String(80), nullable=False)

	mark = Column(db.String(80),unique=True,nullable=False)
	#文章
	article = db.relationship('Article', backref='content_attrs',lazy='dynamic')
	#图集
	photo = db.relationship('Photo', backref='content_attrs',lazy='dynamic')
	
	def __repr__(self):
		return '<ArticeAttr({name!r})>'.format(name=self.name)


#文章
class Article(SurrogatePK,Model):

	__tablename__ = 'articles'

	#:文章标题
	title = Column(db.String(80),nullable=False)
	#:作者
	author =  Column(db.String(80))
	#:来源
	source =  Column(db.String(80))
	#:文章描述
	summary = Column(db.String(500))
	#:关键字
	key =  Column(db.String(80))
	#:关键描述
	word = Column(db.String(500))
	#:创建时间
	creation_date = Column(db.DateTime(),default=dt.datetime.now)
	#:是否显示
	is_enable = Column(db.Boolean,default=True)
	#:内容
	content = Column(db.UnicodeText)
	#:浏览次数
	count = Column(db.Integer,default=100)
	#缩略图 #保存路径
	image = Column(db.String(200))
	image_alt = Column(db.String(80))
	#文章属性
	#附加字段,附加字段值
	attach_key = Column(db.String(200))
	attach_value = Column(db.String(500))
	#静态内容，用“|”号隔开
	static_context = Column(db.UnicodeText)


	attr_id = reference_col('content_attrs')
	category = reference_col('categorys')
	user = reference_col('users')
	


class Photo(SurrogatePK,Model):
	__tablename__ = 'photos'
	#:图集标题
	title = Column(db.String(80),nullable=False)
	#:图集描述
	summary = Column(db.String(500))
	#:关键字
	key =  Column(db.String(80))
	#:关键描述
	word = Column(db.String(500))
	#:拍摄时间
	photos_date = Column(db.DateTime(),default=dt.datetime.now)
	#:创建时间
	creation_date = Column(db.DateTime(),default=dt.datetime.now)
	#缩略图 #保存路径
	image = Column(db.String(200))
	image_alt = Column(db.String(80))
	#:浏览次数
	count = Column(db.Integer,default=100)
	#:是否显示
	is_enable = Column(db.Boolean,default=True)
	

	#图集属性
	attr_id = db.Column(db.Integer,db.ForeignKey('content_attrs.id'))
	#图集照片
	photo_image = db.relationship('PhotoImage', backref='photo_images',lazy='dynamic')	

	#附加字段,附加字段值
	attach_key = Column(db.String(200))
	attach_value = Column(db.String(500))

	#静态内容，用“|”号隔开
	static_context = Column(db.UnicodeText)

	user = reference_col('users')
	category = reference_col('categorys')
	
	
#:图集照片
class PhotoImage(SurrogatePK,Model):
	__tablename__ = 'photo_images'
	path = Column(db.String(200)) 
	photo = Column(db.Integer, db.ForeignKey('photos.id'))

	
#:横幅
class Banner(SurrogatePK,Model):
	__tablename__ = 'banners'
	#:横幅标题
	title = Column(db.String(100))
	#:横幅描述
	summary = Column(db.String(200))
	image = Column(db.String(200))
	alt = Column(db.String(80))
	sort = Column(db.Integer())

	user = Column(db.Integer, db.ForeignKey('users.id'))
	

class StaticContext(SurrogatePK,Model):
	__tablename__ = 'static_contexts'
	html = Column(db.UnicodeText)
	
	default_html = Column(db.UnicodeText)
	main_sort = Column(db.Integer,default=100)


	user = reference_col('users')
	category = reference_col('categorys')


#用户留言预约
class UserMark(SurrogatePK,Model):

	__tablename__ = 'usermarks'
	#用户姓名
	name = Column(db.String(80))
	#联系电话
	phone = Column(db.String(20))
	#留言内容
	content = Column(db.UnicodeText)
	#用户头像
	image = Column(db.String(200))
	#:附加段、值
	attach_key = Column(db.String(200))
	attach_value = Column(db.String(500))

	creation_date = Column(db.DateTime(),default=dt.datetime.now)

	user_mark_type = Column(db.Integer, db.ForeignKey('user_mark_types.id'))
	
	user = reference_col('users')

#:留言类型， 用户留言   用户评价，用户预约等初始化设置
class UserMarkType(SurrogatePK,Model):

	__tablename__ = 'user_mark_types'

	name = Column(db.String(80))

	user_mark = db.relationship('UserMark', backref='user_marks',uselist=False)	

	user = reference_col('users')









	





