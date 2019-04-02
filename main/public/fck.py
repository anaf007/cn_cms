#coding=utf-8
from flask import current_app
from .models import Category
from flask_login import current_user

from PIL import Image
import PIL,os,time,random,hashlib

def get_lower_id(id_list,category_id):
    category = Category.query.get_or_404(category_id)
    if category.children:
        for i in category.children:
            if i.state != 0:
                id_list.append(i.id)
                get_lower_id(id_list,i.id)
    else:
        return id_list


def create_thumbnail(f,base_width,file_dir,filename):
    try:
        base_width = base_width
        thumbnail_f = f
        img = Image.open(thumbnail_f)
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        # print current_app.config['THUMBNAIL_FOLDER']+file_dir+filename


        if not os.path.isdir(current_app.config['THUMBNAIL_FOLDER']+file_dir):
            os.makedirs(current_app.config['THUMBNAIL_FOLDER']+file_dir)
        img.save(os.path.join(current_app.config['THUMBNAIL_FOLDER'], file_dir+filename))
        
        return True
    except Exception as e:
        return False


def allowed_file(filename):
    if '.' in filename and \
        filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS_IMAGES'] :
        return True
    else:
        return False
           

def create_file_name(f):
    choice_str = 'ABCDEFGHJKLNMPQRSTUVWSXYZ'
    str_time =  time.time()
    username_str = str(int(str_time))
    for i in range(6):
        username_str += random.choice(choice_str)
    filename = hashlib.md5(username_str.encode('utf-8')).hexdigest()[:32]+'.'+f.filename.rsplit('.', 1)[1]
    return filename





