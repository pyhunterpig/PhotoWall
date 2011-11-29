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

random.seed()
BASE_DIR = os.path.dirname(__file__)

def load_images(enable_types=["image/jpeg", "image/png", "image/gif"]):
    PHOTO_PATH = os.path.join(BASE_DIR, "photos/logos")
    files = [file for file in os.listdir(PHOTO_PATH) if not os.path.isdir(os.path.join(PHOTO_PATH, file))]
    images = []
    for file in files:
        types = mimetypes.guess_type(os.path.join(PHOTO_PATH, file))
        if types and types[0] in enable_types:
            images.append(file)

    return images

def load_namelist(file='photos/namelist.xls'):
    book = xlrd.open_workbook(os.path.join(BASE_DIR, file))
    namelist = []
    sh = book.sheet_by_index(0)
    for rx in range(sh.nrows):
        row = sh.row(rx)
        namelist.append(('%s.png' % row[0].value, row[1].value))
        
    return namelist

filenames, namelist, timerspeed, event_title = \
    load_images(), load_namelist(), 90, "PyCon 2011 China"

TIMER_ID1 = 2000
TIMER_ID2 = 2001

class WallWindow(wx.Window):
    def __init__(self, parent, cols=14):
        wx.Window.__init__(self, parent)
        self.photos = filenames
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeypress)
        self.cols = cols
        self.cur = 0
        self.bg_timer = wx.Timer(self, id=TIMER_ID1)
        self.lettory_timer = wx.Timer(self, id=TIMER_ID2)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.bg_timer)
        self.Bind(wx.EVT_TIMER, self.on_lettory, self.lettory_timer)
        self.cur_bg = {}
        self._image_cache = {}
        self.bg_timer.Start(3000)
        self.lettory_timer.Start(30)
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
    
        while n < (self.cols*rows):
            if n >= (self.cols*2 + 5) and \
                n < (self.cols*6 + 5) and \
                ((n-5)%self.cols == 0 or \
                 (n-6)%self.cols == 0 or \
                 (n-7)%self.cols == 0 or\
                 (n-8)%self.cols == 0):
                pass
            else:
                image =  self._image_cache.get(self.photos[self.cur], None)
                if not image:
                    image = Image.open(os.path.join(BASE_DIR, "photos/logos", self.photos[self.cur]))
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
                
        val = imgutil._crop((w*4, w*4), Image.open(os.path.join(BASE_DIR, "photos", "main.png")))
        background.paste(Image.open(cStringIO.StringIO(val)), (left+5*w, top+2*w))
        return background
    
    def next_people(self):
        image, name =  random.choice(namelist)
        avatar_path = os.path.join(BASE_DIR, "photos/peoples", image)
        if os.path.exists(avatar_path):
            dw, dh = wx.DisplaySize()
            w = int(math.ceil(((dw-self.cols*2)*1.0)/(self.cols*1.0)))
            background = Image.new('RGBA', (w*4, w*4), (199, 215, 255, 0))
            image = Image.open(avatar_path)
            val = imgutil._crop((w*2, w*2), image)
            background.paste(Image.open(cStringIO.StringIO(val)), (1*w, 1*w))
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

    def on_paint(self, evt):
        self.draw_backgroud()
    
    def on_timer(self, evt):
        if self.bg_start:
            self.draw_backgroud()

    def on_lettory(self, evt):
        if self.lettory_start:
            dw, dh = wx.DisplaySize()
            w = int(math.ceil(((dw-self.cols*2)*1.0)/(self.cols*1.0)))
            dc = wx.PaintDC(self)
            top = ((dh%w)/4)
            left = ((dw%w)/2)
            bmp = wx.BitmapFromImage(wx.ImageFromStream( cStringIO.StringIO(self.next_people())))
            dc.DrawBitmap(bmp, 5*w+left, 2*w+top, True)
    
    def OnKeypress(self, evt):
        code = evt.GetRawKeyCode()
        # 按空格键抽奖
        if code == 32:
            self.lettory_start = not self.lettory_start
            self.bg_start = False
        # 按回车键启动或暂停更换背景
        elif code == 65293:
            self.bg_start = not self.bg_start
        
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