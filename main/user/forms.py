# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField,TextField,IntegerField,BooleanField, \
    SelectField,TextAreaField,DateField,HiddenField,RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length,Required
from flask_wtf.file import FileField,FileRequired,FileAllowed
from flask_ckeditor import CKEditorField
from wtforms.ext.appengine.db import model_form
from flask import session
from .models import User
from main.public.models import Category,ContentAttr
from main.superadmin.models import CategoryAttr
from flask_login import current_user

import random,datetime

class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField(u'用户名',
        validators=[DataRequired(), Length(min=6, max=25)])
    password = PasswordField(u'密码',
        validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField(u'确认密码',
        [DataRequired(), EqualTo('password', message=u'密码不匹配')])
    first_name = StringField(u'真实姓名',
        validators=[DataRequired(), Length(min=2, max=10)])
    phone = StringField(u'联系号码',
        validators=[DataRequired(), Length(min=11, max=11)])


    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append(u'该用户名已存在，请重新输入。')
            return False
        
        return True


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(u'用户名',validators=[DataRequired(),Length(1,64)])
    password = PasswordField(u'密码',validators=[DataRequired(),Length(3, 20, message=u'密码长度在3到12为')])
    verification_code = StringField(u'验证码', validators=[DataRequired(), Length(4, 4, message=u'填写4位验证码')])


    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None


    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        try:
            if self.verification_code.data.upper() != session['verify']:
                self.verification_code.errors.append(u'输入不错误')
                return False
        except Exception as e:
            self.verification_code.errors.append(u'输入不错误')
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append(u'没有该用户')
            return False
        else:
            if not self.user.check_password(self.password.data):
                self.password.errors.append(u'密码不正确')

        return True


class AllCategoryAttrForm(FlaskForm):
    name =   StringField(label=u'属性标题',validators=[DataRequired(message=u''),Length(2,30)])
    mark = StringField(label=u'属性代码',validators=[DataRequired(message=u''),Length(max=200)])
    url = StringField(u'属性链接',validators=[DataRequired(message=u''),Length(max=80)])
    tampaltes = StringField(u'属性模板',validators=[DataRequired(message=u''),Length(max=50)])

   
class AllCategoryForm(FlaskForm):
    
    title =   StringField(label=u'栏目标题',validators=[DataRequired(message=u''),Length(2,30)])
    summary = StringField(label=u'栏目概述')
    key = StringField(u'关键词')
    word = StringField(u'描述')
    attach_value = TextAreaField(u'附加值，多个值用“|”隔开')
    sort = IntegerField(u'排序',validators=[DataRequired(message=u'请输入正确的排序')])
    main_sort = IntegerField(u'首页展示顺序',validators=[DataRequired(message=u'请输入正确的首页展示顺序')])
    is_enable = BooleanField(u'是否显示(默认显示)',validators=[DataRequired()])
    attr = SelectField(u'栏目属性',coerce=int)
    pid = SelectField(u'上级栏目',choices=[(-1,'顶级栏目')],coerce=int)
    # content = CKEditorField(u'栏目内容(单页选填)')

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(AllCategoryForm, self).__init__(*args, **kwargs)
        self.attr.choices = [(obj.id, obj.name) for obj in CategoryAttr.query.filter_by(usertemplate_id=current_user.templates).all()]
        self.pid.choices = self.pid.choices+[(obj.id, obj.title) for obj in Category.query.filter_by(users=current_user).filter(Category.state==1).order_by('sort').all()]
        


class AllBannerForm(FlaskForm):

    title =   StringField(label=u'横幅标题',validators=[DataRequired(message=u'请输入正确的横幅标题'),Length(2,100)])
    summary = StringField(label=u'横幅描述',validators=[DataRequired(message=u'请输入正确的横幅描述'),Length(2,200)])
    alt =   StringField(label=u'图片描述',validators=[DataRequired(message=u'请输入正确的图片描述'),Length(2,30)])
    sort =   IntegerField(label=u'排序',validators=[DataRequired()])
    #神奇的  获取不到file文件  只好取消
    # image = FileField(label=u'横幅图片',validators=[FileRequired(),FileAllowed(['jpg','png'],u'仅jpg,png图片')])
    
    

class AllStaticContextForm(FlaskForm):

    main_sort = HiddenField(label=u'排序',validators=[DataRequired()])
    html = TextAreaField(u'静态内容(HTML)')

       

class ArticleForm(FlaskForm):

    title =   StringField(label=u'文章标题',validators=[DataRequired(message=u'标题输入不正确'),Length(2,30)])
    author =   StringField(label=u'作者')
    source =   StringField(label=u'来源')
    summary =   StringField(label=u'文章描述')
    key =   StringField(label=u'关键字')
    word =   StringField(label=u'搜索描述')
    is_enable = BooleanField(u'是否显示(默认显示)',validators=[DataRequired()])
    count = IntegerField(label=u'浏览次数',validators=[DataRequired()])
    alt =   StringField(label=u'图片alt')
    img_width = IntegerField(u'缩略图宽度(默认80)',default=80)
    attach_key = TextAreaField(u'附加字段,用“|”分隔')
    attach_value = TextAreaField(u'附加值,用“|”分隔')
    static_context = TextAreaField(u'静态内容，用“|”隔开')

    attr = SelectField(u'文章属性',coerce=int)
    category = SelectField(u'所属栏目',coerce=int)

    content = CKEditorField(u'文章内容')


    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.attr.choices = [(obj.id, obj.name) for obj in ContentAttr.query.all()]
        self.category.choices = [(obj.id, obj.title) \
            for obj in Category.query \
            .filter_by(user=session.get('userid')) \
            .join(CategoryAttr,CategoryAttr.id==Category.attr_id) \
            .filter(CategoryAttr.mark=='article') \
            .filter(Category.state!=0) \
            .order_by(Category.sort).all()]



class PhotoForm(FlaskForm):

    title =   StringField(label=u'图集标题',validators=[DataRequired(message=u'标题输入不正确'),Length(2,30)])
    summary =   StringField(label=u'图集描述')
    key =   StringField(label=u'关键字')
    word =   StringField(label=u'搜索描述')
    #神奇的总是 Not a valid date value，已经取消校验了还提示。只好去掉
    # photos_date = DateField(label=u'拍摄时间')
    count = IntegerField(label=u'浏览次数',validators=[DataRequired()],default=random.randint(50,200))
    
    attr = SelectField(u'图集属性',coerce=int)
    category = SelectField(u'所属栏目',coerce=int)

    attach_key = TextAreaField(u'附加字段,用“|”分隔')
    attach_value = TextAreaField(u'附加值,用“|”分隔')
    static_context = TextAreaField(u'静态内容，用“|”隔开')
    image_alt = StringField(label=u'展示图alt')
    img_width = IntegerField(u'缩略图宽度(默认80)')
    is_enable = BooleanField(u'是否显示(默认显示)',validators=[DataRequired()])
    

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.attr.choices = [(obj.id, obj.name) for obj in ContentAttr.query.all()]
        self.category.choices = [(obj.id, obj.title) \
            for obj in Category.query \
            .filter_by(user=session.get('userid')) \
            .join(CategoryAttr,CategoryAttr.id==Category.attr_id) \
            .filter(CategoryAttr.mark=='photo') \
            .filter(Category.state!=0) \
            .order_by(Category.sort).all()]

        

class WebConfigForm(FlaskForm):

    web_name =   StringField(label=u'网站名称',validators=[DataRequired(message=u'名称输入不正确'),Length(2,30)])

    web_key =   StringField(label=u'关键字')
    web_word =   StringField(label=u'关键描述')

    #网站分页数据
    article_page = IntegerField(u'文章分页')
    photo_page = IntegerField(u'图集分页')

    #logo字
    web_logo_word = StringField(u'网站LOGO文字')
    # web_logo_img = StringField(u'网站logo图片')

    #文章展示和图集展示静态内容
    article_context = TextAreaField(u'文章展示静态内容')
    photo_context = TextAreaField(u'图集展示静态内容')

    # state = RadioField(u'网站属性',choices=[(0,u'关闭'),(1,u'开启')],coerce=int)


    




