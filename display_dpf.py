#!/usr/bin/env python

import wx
import time

import gettext


class ImagePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.image_files = [
            "/home/skruger/Desktop/Screenshot.png",
            "/home/skruger/Desktop/Screenshot-1.png"
        ]
        self.update_count = 0
        self.bitmap1 = None
        self.update_image()

    def update_image(self):
        try:
            image_index = self.update_count % len(self.image_files)
            image_file = self.image_files[image_index]
            self.update_count += 1
            bmp1 = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

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

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.timer.Start(5000)

        self.ShowFullScreen(True, 0)

    def update(self, event):
        print "Updated: {}".format(time.ctime())
        self.client.update_image()


if __name__ == "__main__":
    gettext.install("super_dpf")

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, wx.ID_ANY, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
