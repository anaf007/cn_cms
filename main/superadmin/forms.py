# -*- coding: utf-8 -*-
"""SuperAdmin forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired

from .models import *


class AddTemplateForm(FlaskForm):
    
    title = StringField('模板名称', validators=[DataRequired()])


class AddTemplateContextForm(FlaskForm):

    main_sort = IntegerField(u'主页排序', validators=[DataRequired(message=u'请输入正确的排序')])

    html = TextAreaField(u'内容', validators=[DataRequired(message=u'请输入正确的内容')])


    def __init__(self, *args, **kwargs):

        """Create instance."""

        super(AddTemplateContextForm, self).__init__(*args, **kwargs)


    def validate(self):
        """Validate the form."""
        initial_validation = super(AddTemplateContextForm, self).validate()
        if not initial_validation:
            return False

        return True


#模板栏目谁能够
class AddTemplateCategoryAttrForm(FlaskForm):

	name = StringField(u'属性名称',validators=[DataRequired(message=u'请输入正确的属性名称')])
	summary = StringField(u'属性介绍',validators=[DataRequired(message=u'请输入正确的属性介绍')])
	mark = StringField(u'属性标记',validators=[DataRequired(message=u'请输入正确的属性标记')])
	url = SelectField(u'属性链接',choices=[('article','article'),('photo','photo'),('single','single'),('index','index')])
	templates = StringField(u'模板页',validators=[DataRequired(message=u'请输入正确的模板页')])
	user_template = SelectField(u'所属模板',coerce=int,validators=[DataRequired(message=u'请选择正确的模板')])

	def __init__(self, *args, **kwargs):
		"""Create instance."""
		super(AddTemplateCategoryAttrForm, self).__init__(*args, **kwargs)
		self.user_template.choices = [(obj.id, obj.name) for obj in UserTemplate.query.order_by('id').all()]
    
	def validate(self):
		"""Validate the form."""
		initial_validation = super(AddTemplateCategoryAttrForm, self).validate()
		if not initial_validation:
			return False

		return True




