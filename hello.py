#!/usr/bin/env python
#coding=utf-8
"""Photo Wall for PyCon China"""

import wx
import random
import xlrd
random.seed()

filenames = ['01.jpg', '02.jpg', '03.jpg', '04.jpg', '05.jpg', '06.jpg', '07.jpg', '08.jpg', '09.jpg', '10.jpg', '11.jpg', '12.jpg', '13.jpg', '14.jpg', '15.jpg', '16.jpg', '17.jpg', '18.jpg', '19.jpg', '20.jpg', '21.jpg', '22.jpg', '23.jpg', '24.jpg', '25.jpg', '26.jpg', '27.jpg', '28.jpg', '29.jpg', '30.jpg', '31.jpg', '32.jpg', '33.jpg', '34.jpg', '35.jpg', '36.jpg', '37.jpg', '38.jpg', '39.jpg', '40.jpg', '41.jpg', '42.jpg', '43.jpg', '44.jpg', '45.jpg', '46.jpg', '47.jpg', '48.jpg', '49.jpg', '50.jpg']
fname = 'photos/namelist.xls'
book = xlrd.open_workbook(fname)
namelist = []
sh = book.sheet_by_index(0)
for rx in range(sh.nrows):
    row = sh.row(rx)
    namelist.append(('%s.jpg' %row[0].value,row[1].value))

try:
    timerspeed = eval(open('photos/speed.ini'))
except:
    timerspeed = 90


class RandomImagePlacementWindow(wx.Window):
    def __init__(self, parent, image):
        wx.Window.__init__(self, parent)
        self.photos = []
        for filename,employeename in namelist:
            img1 = wx.Image('photos/'+filename.replace(u'\u2018',u''), wx.BITMAP_TYPE_ANY)
            #img1 = img1.Scale(800,600)
            self.photos.append((img1,employeename))
        self.backgroundimags = [item[0].Scale(148/2,170/2) for item in self.photos]*3
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN,self.OnKeypress)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        brush = wx.Brush("sky blue")
        dc.SetBackground(brush)
        dc.Clear()
        x = 0
        y = 0
        n = 0
        w = 148/2
        h = 170/2
        
        for image in self.backgroundimags:
            dc.DrawBitmap(image.ConvertToBitmap(), x, y, True)
            n += 1
            if (n) % 14 == 0:
                x = 0
                y += h
            else:
                x += w
            
        
        
    def OnKeypress(self, evt):
        
        self.frame = Frame(self.photos, self)
        self.frame.Show()
            
class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="PyCon 2011 China",
                           size=(1024,768))
        img = wx.Image("photos/01.jpg")
        win = RandomImagePlacementWindow(self, img)


class Frame(wx.Frame):   #2 wx.Frame子类
    """Frame class that displays an image."""

    def __init__(self, images, parent=None, id=-1,  
                 pos=wx.DefaultPosition,
                 title='猜猜我是WHO！'):     #3图像参数
        """Create a Frame instance and display image."""
    #4 显示图像
        self.images = images
        self.start = True
        image = random.choice(self.images)
        temp = image[0].ConvertToBitmap()                          
        size = 800, 600
        wx.Frame.__init__(self, parent, id, title, pos, size)
        self.panel = wx.Panel(self,-1)
        self.photo = wx.StaticBitmap(parent=self.panel)
        self.photo.SetBitmap(temp)
        self.nametext = wx.StaticText(self.panel, -1, "", (400, 300), 
                (400, 100), wx.ALIGN_CENTER)
        font = wx.Font(24, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.nametext.SetFont(font)
        self.timer = wx.Timer(self)#创建定时器
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)#绑定一个定时器事件
        self.timer.Start(timerspeed)#设定时间间隔
        
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
        
    
    def changebmp(self,evt):
        if self.start:
            self.cimage = random.choice(self.images)
            image = self.cimage[0]
            x = (800-image.GetWidth())/2
            y = (600-image.GetHeight())/2
            temp = image.ConvertToBitmap()
            self.photo.SetBitmap(temp)
            self.photo.SetPosition(wx.Point(x, y)) 
            self.panel.Refresh()


    
    def OnTimer(self,evt):
        if self.start and len(self.images) > 0:
            self.changebmp(evt)
        
            
            
            
            
    def OnKeyDown(self, evt):
        #print evt.KeyCode
        if self.start:
            self.start = False
            self.timer.Stop()
            try:
                self.images.remove(self.cimage)
                
            except ValueError:
                pass
            
        else:
            if self.nametext.GetLabel() == '':
                self.nametext.SetLabel(self.cimage[1])
                #print self.cimage[1].encode('cp936')
                self.panel.Refresh()
            else:
                self.nametext.SetLabel('')
                self.timer.Start(timerspeed)
                self.start = True
                
            
class PhotoWallFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Loading Images")
        p = wx.Panel(self)
        fgs = wx.FlexGridSizer(cols=6, hgap=1, vgap=1)
        for name in filenames:
            img1 = wx.Image('photos/'+name, wx.BITMAP_TYPE_ANY)
            w = img1.GetWidth()
            h = img1.GetHeight()
            sb1 = wx.StaticBitmap(p, -1, wx.BitmapFromImage(img1))
            fgs.Add(sb1)

        p.SetSizerAndFit(fgs)
        self.Fit()

                

class App(wx.App):  #5 wx.App子类
    """Application class."""

    def OnInit(self):
    #6 图像处理
        #image = wx.Image('/home/pyhunterpig/workspace/91office/house1.png', wx.BITMAP_TYPE_PNG)  
        #self.frame = Frame(image)
        #self.frame = PhotoWallFrame()
        self.frame = TestFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

def main():  #7       
    app = App(redirect=False)     
    app.MainLoop()  

if __name__ == '__main__':   
     main()
