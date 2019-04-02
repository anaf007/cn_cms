# -*- coding: utf-8 -*-
"""The user module."""
from flask import render_template,current_app
import random,string
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO

from datetime import datetime
try:
	from PIL import Image,ImageDraw,ImageFont,ImageFilter
except Exception as e:
	import Image,ImageDraw,ImageFont,ImageFilter
from flask import Blueprint,session,make_response

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')

from main.public.models import Category
from . import views,context_process  # noqa

# 随机字母:
def rndChar():
	str = ''
	for i in range(4):
		str += chr(random.randint(65, 90))
	return str

# 随机颜色1:
def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

# 随机颜色2:
def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

@blueprint.route('/genverify')
def generate_verification_code(nowtime =''):
	output = BytesIO()
	width = 70
	height = 30
	image = Image.new('RGB',(width,height),(255,255,255))
	#字体对象
	font = ImageFont.truetype(current_app.config['VERIFICATION_CODE_FONT'], 18)
	draw = ImageDraw.Draw(image)
	for x in range(width):
		for y in range(height):
			draw.point((x, y), fill=rndColor())
	verify_str = rndChar() 

	draw.text((10, 5),verify_str, font=font, fill=rndColor2())

	#模糊
	# image = image.filter(ImageFilter.BLUR)
	# li = []
	# for i in range(10):
	# 	temp = random.randrange(65,90)
	# 	c = chr(temp)
	# 	li.append(c)
	
	image.save(output,"JPEG")
	img_data = output.getvalue()
	session['verify'] = verify_str
	response = make_response(img_data)
	response.headers['Content-Type'] = 'image/jpeg'
	return response


#请求上下文 ，获取验证码
@blueprint.context_processor
def get_verify():
    def get():
    	return generate_verification_code()
    return dict(get_verify=get)


#父级导航名称
@blueprint.context_processor
def get_category_parent_title():
    def get(id):
        return Category.query.get(id).title
    return dict(get_category_parent_title=get)


#文件过大413
@blueprint.errorhandler(413)
def page_max_file(e):
	return render_template('users/413.html'), 413


@blueprint.errorhandler(404)
def page_not_found(e):
	return render_template('users/404.html'), 404
