#coding=utf-8

import datetime as dt

from main.database import Column, Model, SurrogatePK, db, reference_col, relationship


class CategoryAttr(SurrogatePK, Model):
	"""默认的三个类型选项
	用户无法更改，mark标记唯一，
	管理员更改，外键模板 模板可添加多个文章页等
	数据库读取mark标记
	"""

	__tablename__ = 'category_attrs'

	name = Column(db.String(80), nullable=False)
	summary = Column(db.String(80), nullable=False)
	mark = Column(db.String(80),nullable=False)
	#链接地址
	url = Column(db.String(80), nullable=False)
	#模板页
	templates = Column(db.String(80), nullable=False)

	#用户分类
	category = relationship('Category', backref='categorys_attr',lazy='select')
	#默认内容
	static_context = relationship('TemplatesDefault', backref='category_attrs')

	#模板
	usertemplate_id = reference_col('user_templates')

	#: 栏目页 ，(文章页，图集页，内容页 )

	def __repr__(self):
		return '<({name!r})>'.format(name=self.name)


#用户前台模板
class UserTemplate(SurrogatePK, Model):

	__tablename__ = 'user_templates'

	name = Column(db.String(80), nullable=False)
	#是否完结默认模板内容，完结列表不在显示，以后模板多了会有很多列表所以在此设置
	is_end = Column(db.Boolean,default=False)
	#模板容量，用户选择该模板注册后所拥有的容量
	memory_capacity = Column(db.Integer,default=0)

	#默认模板主页内容
	# template_default = relationship('TemplatesDefault', backref='template',lazy='select')

	categoryattr = relationship('CategoryAttr', backref='usertemplate')

	user_id = relationship('User', backref='usertemplate',uselist=False)
	#用户网址模板关联
	user_url_and_template = relationship('UserUrlAndTemplate', backref='usertemplate')
    

#默认模板主页内容
class TemplatesDefault(SurrogatePK,Model):

	__tablename__ = 'template_defaults'

	main_sort  = Column(db.Integer,nullable=False)
	html = Column(db.UnicodeText)

	#所属模板
	# user_template = reference_col('user_templates')
	#所属模板属性分类
	user_template_category = reference_col('category_attrs')


#用户网址和模板关联链接 用户的配置
class UserUrlAndTemplate(SurrogatePK,Model):

	__tablename__ = 'user_url_and_templates'

	user_url = Column(db.String(100), nullable=False)

	user = reference_col('users')
	template = reference_col('user_templates')

	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)
	end_time_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)



#系统更新版本号
class SystemVersion(SurrogatePK,Model):

	__tablename__ = 'system_versions'
	#版本号
	number = Column(db.String(20))
	#标题
	title = Column(db.String(100))
	#描述
	summary = Column(db.String(200))
	#内容
	context = Column(db.UnicodeText)

	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.now)


#系统消息，给用户查看，优惠券发放模板添加等等各种信息
class SystemMsg(SurrogatePK,Model):

	__tablename__ = 'system_msger'

	#标题
	title = Column(db.String(100))
	#内容
	context = Column(db.UnicodeText)
	#状态
	static  = Column(db.Integer,default=0)

	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)










