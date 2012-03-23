#!/usr/bin/python
# encoding:utf-8

import math
import os
import json
import random
import sys
import wx
import xlrd
import mimetypes
import shutil
from cStringIO import StringIO
import Image, ImageFont, ImageDraw

QUALITY = 100

def to_data(image):
    buf = StringIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buf, image.format or "JPEG", quality=QUALITY)
    val = buf.getvalue()
    return val

def rcd(x):
    return int(math.ceil(x))

def _crop(size, image, data=True, squre=False, bg_color="#fff"):
    width, height = size
    w, h = image.size
    
    if (w, h) == (width, height):
        return data and to_data(image) or image

    def wrap(image, w, h):
        background = Image.new('RGBA', (w, h), bg_color) 
        background.paste(image, (rcd((w - image.size[0]) / 2.0), rcd((h - image.size[1]) / 2.0)))
        return background

    if not squre and (w <= width or h <= height):
        image.thumbnail(size, Image.ANTIALIAS)
        image = wrap(image, *size)
        return data and to_data(image) or image

    n = None
    if w < width and h <= height:
        n = image
    if w < width and h > height:
        #left upper right lower
        n = image.crop((0, (h - height) / 2 , w, h - (h - height) / 2))
    if w >= width and h <= height:
        n = image.crop(((w - height) / 2, 0 , w - (w - height) / 2, h))
        
    #小图也要有个大背景
    if n:
        n = wrap(n, *size)

    #缩略图比原图小的, 先缩放效果会更好
    if w >= width and h >= height:
        if w * 1.0 / width >= h * 1.0 / height:
            thum = (int(w * height * 1.0 / h), height)
            image.thumbnail(thum, Image.ANTIALIAS)
            n = image.crop((rcd((thum[0] - width)*1.0 / 2.0), 0 , thum[0] - rcd((thum[0] - width)*1.0 / 2.0), thum[1]))
        else:
            thum = (width, int(h * width * 1.0 / w))
            image.thumbnail(thum, Image.ANTIALIAS)
            n = image.crop((0, rcd((thum[1] - height)*1.0 / 2.0) , thum[0], thum[1] - rcd((thum[1] - height)*1.0 / 2.0)))
    
    return data and to_data(n) or n

def draw_word_wrap(img, text, xpos=0, ypos=0, max_width=130,
                   fill=(0,0,0), font=ImageFont.load_default()):
    '''Draw the given ``text`` to the x and y position of the image, using
    the minimum length word-wrapping algorithm to restrict the text to
    a pixel width of ``max_width.``
    '''
    draw = ImageDraw.Draw(img)
    text_size_x, text_size_y = draw.textsize(text, font=font)
    remaining = max_width
    space_width, space_height = draw.textsize(' ', font=font)
    # use this list as a stack, push/popping each line
    output_text = []
    # split on whitespace...    
    for word in text:
        word_width, word_height = draw.textsize(word, font=font)
        if word_width + space_width > remaining:
            output_text.append(word)
            remaining = max_width - word_width
        else:
            if not output_text:
                output_text.append(word)
            else:
                output = output_text.pop()
                output += '%s' % word
                output_text.append(output)
            remaining = remaining - (word_width + space_width)

    for text in output_text:
        draw.text((xpos, ypos), text, font=font, fill=fill)
        ypos += (text_size_y + 6)
        

def load_images(base_dir):
    """加载图片"""
    logo_path = os.path.join(base_dir, "photos/logos")
    avatar_path = os.path.join(base_dir, "photos/peoples")
    photo_path = os.path.join(base_dir, "photos")
    logos = ["logos/%s" % file for file in os.listdir(logo_path) if not os.path.isdir(os.path.join(logo_path, file))]
    avatars = ["peoples/%s" % file for file in os.listdir(avatar_path) if not os.path.isdir(os.path.join(avatar_path, file))]
    files = (logos + avatars)
    random.shuffle(files)
    images = []
    for file in files:
        types = mimetypes.guess_type(os.path.join(photo_path, file))
        if types and types[0] and types[0].split("/")[0] == "image":
            images.append(file)

    return images

def load_namelist(base_dir, file='photos/namelist.xls'):
    book = xlrd.open_workbook(os.path.join(base_dir, file))
    namelist = []
    sh = book.sheet_by_index(0)
    for rx in range(sh.nrows):
        row = sh.row(rx)
        namelist.append(row[0].value)

    return set(namelist)

def generate_avatars():
    app = wx.App(redirect=False)
    width, height = wx.DisplaySize()
    base_dir = os.path.dirname(__file__).replace("\\", "/")
    avatar_path = os.path.join(base_dir, "avatar")
    config = json.load(open(os.path.join(base_dir, "photos", "config.json"), "rb"))
    cols =  config.get('wall_cols', 15)
    w = rcd(((width - cols*2)*1.0)/(cols*1.0))
    # 清空头像目录
    if os.path.exists(avatar_path):
        shutil.rmtree(avatar_path)
    os.makedirs(avatar_path)
    photo_paths =  load_images(base_dir)
    # 处理有头像的
    current_avatar_index = 0
    for photo_path in photo_paths:
        src_path = os.path.join(base_dir, "photos", photo_path)
        photo = _crop((w, w), Image.open(src_path), squre=True, data=False)
        desc_path = os.path.join(base_dir, "avatar", "%s.jpg" % current_avatar_index)
        photo.save(desc_path)
        current_avatar_index += 1
    # 处理无头像的
    names = load_namelist(base_dir)
    default_avatar_path = os.path.join(base_dir, "photos", "default_avatar.jpg")
    default_avatar = Image.open(default_avatar_path)
    default_avatar = _crop((w, w), default_avatar, squre=True, data=False)
    font = ImageFont.truetype(os.path.join(base_dir, "xxk.ttf"), 20)
    for name in names:
        photo = default_avatar.copy()
        draw_word_wrap(photo, name, 0, 50, fill="#fff", font=font)
        desc_path = os.path.join(base_dir, "avatar", "%s.jpg" % current_avatar_index)
        photo.save(desc_path)
        print current_avatar_index
        current_avatar_index += 1 

if __name__ == "__main__":
    option = sys.argv[1]
    if option == "avatar":
        generate_avatars()