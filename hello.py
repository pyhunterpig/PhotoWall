#coding=utf-8
"""Photo Wall for PyCon China"""

import wx
import random
import xlrd
import os, mimetypes
import imgutil
import Image
import cStringIO
import math
import json
import ImageFont

random.seed()
BASE_DIR = os.path.dirname(__file__).replace("\\", "/")
PHOTO_PATH = os.path.join(BASE_DIR, "photos").replace("\\", "/")
config = json.load(open(os.path.join(BASE_DIR, "photos", "speed.ini"), "rb"))
wall_cols, bg_change_speed, letteroy_change_speed, main_logo, event_title, lottery_people, avatar_format = \
    config.get('wall_cols', 15), \
    config.get('bg_change_speed', 3000), \
    config.get('lottery_change_speed', 78), \
    config.get('main_logo',  {"postion":[6, 3, 4], "bg_color":"#eee"}), \
    config.get('event_title', "PyCon 2011 China"), \
    config.get('lottery_people_name', {"font_size": 30, "position":[100, 280]}), \
    config.get('avatar_format', 'png')

def load_images():
    LOGO_PATH = os.path.join(BASE_DIR, "photos/logos")
    AVATAR_PATH = os.path.join(BASE_DIR, "photos/peoples")
    logos = ["logos/%s" % file for file in os.listdir(LOGO_PATH) if not os.path.isdir(os.path.join(LOGO_PATH, file))]
    avatars = ["peoples/%s" % file for file in os.listdir(AVATAR_PATH) if not os.path.isdir(os.path.join(AVATAR_PATH, file))]
    files = (logos + avatars)
    random.shuffle(files)
    images = []
    for file in files:
        types = mimetypes.guess_type(os.path.join(PHOTO_PATH, file))
        if types and types[0] and types[0].split("/")[0] == "image":
            images.append(file)

    return images

def load_namelist(file='photos/namelist.xls'):
    book = xlrd.open_workbook(os.path.join(BASE_DIR, file))
    namelist = []
    sh = book.sheet_by_index(0)
    for rx in range(sh.nrows):
        row = sh.row(rx)
        image, id, name, email = '%s.%s' % (row[0].value, avatar_format), row[1].value, row[2].value, row[3].value
        if image and os.path.exists(os.path.join(PHOTO_PATH, "peoples", image)):
            namelist.append((image, id, name, email))
            
    return namelist

namelist =  load_namelist()


class WallWindow(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.photos = load_images()
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeypress)
        self.cols = wall_cols
        self.cur = 0
        self.bg_timer = wx.Timer(self, id=2000)
        self.lettory_timer = wx.Timer(self, id=2001)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.bg_timer)
        self.Bind(wx.EVT_TIMER, self.on_lettory, self.lettory_timer)
        self.cur_bg = {}
        self._image_cache = {}
        self.bg_timer.Start(bg_change_speed)
        self.lettory_timer.Start(letteroy_change_speed)
        self.lettory_start = False
        self.bg_start  = True

    def next_background(self):
        n = 0
        dw, dh = wx.DisplaySize()
        w = int(math.ceil(((dw-self.cols*2)*1.0)/(self.cols*1.0)))
        y = top = ((dh%w)/4)
        x = left = ((dw%w)/2)
        rows = dh/w
        
        background = Image.new('RGBA', (dw, dh), (255, 255, 255, 0))
    
        while n < (self.cols*rows) and self.photos:
            need_paste = True
            if n >= (self.cols*main_logo['postion'][1] + 5) and n < (self.cols*(main_logo['postion'][0]+1) + 5):
                for i in range(main_logo['postion'][2]):
                    if (n - (main_logo['postion'][0]+i))%self.cols == 0:
                        need_paste = False
            if need_paste and self.photos:
                image =  self._image_cache.get(self.photos[self.cur], None)
                if not image:
                    image = Image.open(os.path.join(BASE_DIR, "photos", self.photos[self.cur]))
                    self._image_cache[self.photos[self.cur]] = image
                val = imgutil._crop((w-2, w-2), image)
                background.paste(Image.open(cStringIO.StringIO(val)), (x, y))
            n += 1
            self.cur += 1
            if n % self.cols == 0:
                x = left
                y += w
            else:
                x += w
            if self.cur >= len(self.photos):
                self.cur = 0
                
        val = imgutil._crop((w*main_logo['postion'][2], w*main_logo['postion'][2]), Image.open(os.path.join(BASE_DIR, "photos", "main.png")))
        background.paste(Image.open(cStringIO.StringIO(val)), (left+main_logo['postion'][0]*w, top+main_logo['postion'][1]*w))
        return background
    
    def next_people(self):
        image, id, name, email =  random.choice(namelist)
        avatar_path = os.path.join(BASE_DIR, "photos/peoples", image)
        if os.path.exists(avatar_path):
            dw, dh = wx.DisplaySize()
            w = int(math.ceil(((dw-self.cols*2)*1.0)/(self.cols*1.0)))
            background = Image.new('RGBA', (w*main_logo['postion'][2], w*main_logo['postion'][2]), main_logo['bg_color'])
            image = Image.open(avatar_path)
            val = imgutil._crop((w*2, w*2), image)
            background.paste(Image.open(cStringIO.StringIO(val)), (1*w, 1*w))
            body_font = ImageFont.truetype(os.path.join(BASE_DIR, "xxk.ttf"), lottery_people['font_size'])
            imgutil.draw_word_wrap(
                    background,
                    "%s:%s" % (id, name), 
                    lottery_people['position'][0], 
                    lottery_people['position'][1], 
                    max_width=1000,
                    fill=lottery_people['font_color'],
                    font=body_font
                )
            return imgutil.to_data(background)

    def get_background(self):
        self.cur_bg = {'background':self.next_background(), 'opacity':1.0}
        background = self.cur_bg['background']
        bg = cStringIO.StringIO()
        background.save(bg, "png", quality=100)
        bg = bg.getvalue()
        return bg

    def draw_backgroud(self):
        dc = wx.PaintDC(self)
        bmp = wx.BitmapFromImage(wx.ImageFromStream( cStringIO.StringIO(self.get_background())))
        dc.DrawBitmap(bmp, 0, 0, True)
    
    def draw_people(self):
        dw, dh = wx.DisplaySize()
        w = int(math.ceil(((dw-self.cols*2)*1.0)/(self.cols*1.0)))
        top = ((dh%w)/4)
        left = ((dw%w)/2)
        bmp = wx.BitmapFromImage(wx.ImageFromStream( cStringIO.StringIO(self.next_people())))
        dc = wx.PaintDC(self)
        dc.DrawBitmap(bmp, main_logo['postion'][0]*w+left, main_logo['postion'][1]*w+top, True)
        
    def on_paint(self, evt):
        if self.bg_start:
            self.draw_backgroud()
        elif self.lettory_start:
            self.draw_people()

    def on_timer(self, evt):
        print 'on change bg %s ' % self.bg_start
        if self.bg_start:
            self.Refresh()

    def on_lettory(self, evt):
        #print 'on lettory %s' % self.lettory_start
        if self.lettory_start:
            self.Refresh()

    def OnKeypress(self, evt):
        code = evt.GetRawKeyCode()
        print code
        # 按空格键抽奖
        if code == 32:
            self.lettory_start = not self.lettory_start
            self.bg_start = False
        # 按回车键启动或暂停更换背景
        elif code in [65293, 13]:
            self.bg_start = not self.lettory_start and not self.bg_start
            if self.bg_start:
                self.Refresh()
        
class WallFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title=event_title,  size=wx.DisplaySize())
        win = WallWindow(self)

class App(wx.App):  #5 wx.App子类
    """Application class."""

    def OnInit(self):
        self.frame = WallFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':   
    app = App(redirect=False)     
    app.MainLoop()  