# -*- coding: sjis -*-
import wx
import wx.animate

# This is the starting loader page
# This tries the COM Ports to check for the BLE Dongle
class SplashFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Shaped Window", style = wx.FRAME_SHAPED | wx.BORDER_NONE | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)

        self.hasShape = False
        self.delta = (0,0)
        self.EVENT_TYPE = wx.NewEventType()
        self.FOUND_SERIAL = wx.PyEventBinder(self.EVENT_TYPE, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.bmp = wx.Image(name = "resources/splash_2.gif")
        self.bmp=self.bmp.ConvertToBitmap()
        w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
        self.SetClientSize( (w, h) )

        self.SetWindowShape()

        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0,0, True)
        self.CenterOnScreen()
        self.Show()
        self.Update()

        # GIF Loader Panel
        self.MasterPanel= wx.Panel(self,pos=(180,410),size=(70,70))
        self.MasterPanel.SetBackgroundColour((255,255,255))

        gif_fname = "resources/loader.gif"
        gif = wx.animate.GIFAnimationCtrl(self.MasterPanel, -1, gif_fname, size=(54,55))
        gif.GetPlayer().UseBackgroundColour(True)
        self.gif = gif
        self.gif.Play()

        # The text Panel
        self.StatusPan= wx.Panel(self,pos=(60,500),size=(300,20))
        self.StatusPan.SetBackgroundColour((255,255,255))
        StatusFont = wx.Font(12, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False)

        self.Status = wx.StaticText(self.StatusPan,wx.ID_ANY,label="Scanning for BLE Dongle...",size=(300,20),pos=(0,0),style=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)

        self.Status.SetFont(StatusFont)


    def SetWindowShape(self, *evt):
        # Use the bitmap's mask to determine the region
        r = wx.RegionFromBitmap(self.bmp)
        self.hasShape = self.SetShape(r)


    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

    def CloseSplash(self):
        self.OnExit()
        self.Close()


    def OnExit(self,e):
        self.DestroyChildren()
        self.Destroy()
