#!/usr/bin/env python

import wx
import time
import sys
import os

import gettext
from PIL import Image, ImageFilter


def prep_image(filename, width, height):
    with open(filename) as imagefile:
        # Copy the image in memory to avoid closed file errors later
        img = Image.open(imagefile)
        if img.size == wx.DisplaySize():
            print "No prep for {}".format(filename)
            return img.copy()
        background = img.copy()
    w, h = img.size

    print "prep_image({}) {} -> {}".format(filename,
                                           img.size,
                                           wx.DisplaySize())

    background = background.resize(wx.DisplaySize(), Image.ANTIALIAS)
    background = background.filter(ImageFilter.GaussianBlur(radius=20))

    new_height = width * h / w
    if new_height > height:
        new_width = height * w / h
        margin = (width - new_width) / 2
        new_image = img.resize((new_width, height), Image.ANTIALIAS)
        background.paste(new_image, (margin, 0))
        return background
    elif new_height < height:
        new_image = img.resize((width, new_height), Image.ANTIALIAS)
        top_margin = (height - new_height) / 2
        background.paste(new_image, (0, top_margin))
        return background
    else:
        return img.resize(wx.DisplaySize(), Image.ANTIALIAS)


class ImagePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        image_path = os.path.join(os.getcwd(), 'testimages')
        self.image_files = [os.path.join(image_path, f) for f in
                            os.listdir(image_path)]
        self.update_count = 0
        self.bitmap1 = None
        self.update_image()

    def update_image(self):
        try:
            image_index = self.update_count % len(self.image_files)
            filename = self.image_files[image_index]
            pil_image = prep_image(filename,
                                    *wx.DisplaySize())
            self.update_count += 1

            outfile = '/tmp/SuperDPF-image{}{}'.format(
                self.update_count,
                os.path.splitext(filename)[1])
            pil_image.save(outfile, optimize=False,
                           progressive=True, quality=100,
                           subsampling=0)

            bmp1 = wx.Image(outfile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

            # image = wx.EmptyImage(*wx.DisplaySize())
            # image.SetData(pil_image.convert("RGB").tostring())
            # bmp1 = wx.BitmapFromImage(image)

            if self.bitmap1:
                old_bmp = self.bitmap1.GetBitmap()
                self.bitmap1.SetBitmap(bmp1)
                old_bmp.Destroy()
            else:
                self.bitmap1 = wx.StaticBitmap(self, -1, bmp1, (0, 0))
        except IOError as e:
            print e
            raise SystemExit


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)

        self.width, self.height = wx.DisplaySize()
        print "Targeting images for {}x{}".format(self.width, self.height)

        self.client = ImagePanel(self)
        self.client.SetFocus()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.timer.Start(2000)

        self.ShowFullScreen(True, 0)

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)

    def update(self, event):
        print "Updated: {}".format(time.ctime())
        self.timer.Stop()
        self.client.update_image()
        self.timer.Start(2000)

    def OnKeyUP(self, event):
        code = event.GetKeyCode()
        print "keypress: {}".format(code)
        if code == wx.WXK_ESCAPE:
            sys.exit(0)


if __name__ == "__main__":
    gettext.install("super_dpf")

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, wx.ID_ANY, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
