#!/usr/bin/python
# encoding:utf-8

import sys
import os
import math
import re
import web
import hashlib
from cStringIO import StringIO
import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

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

def _crop(size, image):
    width, height = size
    w, h = image.size
    if (w, h) == (width, height):
        return to_data(image)

    def wrap(image, w, h):
        background = Image.new('RGBA', (w, h), (255, 255, 255, 0)) 
        background.paste(image, rcd((w - image.size[0]) / 2.0), rcd((h - image.size[1]) / 2.0))
        return background

    n = None
    if w < width and h <= height:
        n = image
    if w < width and h > height:
        #left upper right lower
        n = image.crop((0, (h - height) / 2 , w, h - (h - height) / 2))
    if w >= width and h <= height:
        n = image.crop(((w - height) / 2, 0 , w - (w - height) / 2, h))
#    #小图也要有个大背景
#    print size, n
#    if n: n = wrap(n, *size)
#    
#
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
            
    return to_data(n)