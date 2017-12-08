# -*- coding: sjis -*-
import wx

# Download Frame
class DownloadFrame(wx.Frame):

    # Initializer
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Shaped Window", style = wx.FRAME_SHAPED | wx.BORDER_NONE | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)

        self.hasShape = False
        self.delta = (0,0)
        self.EVENT_TYPE = wx.NewEventType()
        self.FOUND_SERIAL = wx.PyEventBinder(self.EVENT_TYPE, 1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.bmp = wx.Image(name = "resources/downloadWin.gif")
        self.bmp=self.bmp.ConvertToBitmap()
        w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
        self.SetClientSize( (w, h) )

        self.SetWindowShape()

        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0,0, True)
        self.CenterOnScreen()
        self.Show()
        self.Update()

        # This panel is for text
        self.StatusPan= wx.Panel(self,pos=(130,60),size=(300,50))
        self.StatusPan.SetBackgroundColour((255,255,255))
        StatusFont = wx.Font(15, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False)


        # Not sure what this is for
        self.StatusLab = wx.StaticText(self.StatusPan,wx.ID_ANY,label="Scanning for BLE Dongle...",size=(300,20),pos=(0,0),style=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER|wx.ST_NO_AUTORESIZE)
        self.StatusLab.SetFont(StatusFont)


        # This panel is for the gauge
        self.MasterPanel = wx.Panel(self, pos=(80, 100), size=(450, 30))
        self.MasterPanel.SetBackgroundColour((255, 255, 255))

        self.gauge = wx.Gauge(self.MasterPanel, -1, 100, size=(400, 25))

        # This code if you want the loader
        # gif_fname = "resources/loader.gif"
        # gif = wx.animate.GIFAnimationCtrl(self.MasterPanel, -1, gif_fname, size=(54,55))
        # gif.GetPlayer().UseBackgroundColour(True)
        # self.gif = gif
        # self.gif.Play()
        # self.gif.Stop()
        self.ButtonPanel = wx.Panel(self, pos=(250, 150), size=(70, 30))
        self.ButtonPanel.SetBackgroundColour((255, 255, 255))

        self.StopBut = wx.Button(self.ButtonPanel, wx.ID_ANY, "Cancel", size=(60, 25))
        self.StopBut.Bind(wx.EVT_BUTTON,self.OnCancelBut)
        self.StopBut.Show()

        self.Callback = None
        self.RxDataCallback = None
        self.CancelCallback = None

        tid = wx.NewId()
        wx.RegisterId(tid)
        self.Commandtimer = wx.Timer(self, id=tid)
        self.Bind(wx.EVT_TIMER, self.OnCommandTimeout, id=tid)

        self.Hide()

    # On Cancel Button Press
    # Need to show the main frame
    def OnCancelBut(self,e):
        if(self.CancelCallback!=None):
            self.CancelCallback()



    def SetCancelCallback(self,callbackfunc):
        self.CancelCallback=callbackfunc

    # When the Download Finished
    def Finished(self):
        self.Commandtimer.Stop()
        self.Hide()
        self.Callback=None
        self.RxDataCallback=None

    def SetTimeout(self,time,callbackfunc):
        self.Callback=callbackfunc
        self.Commandtimer.Start(milliseconds=time, oneShot=True)

    def ClearTimeout(self):
        self.Commandtimer.Stop()

    def OnCommandTimeout(self,e):
        if(self.Callback!=None):
            self.Callback()

    # Displays the Download Frame
    def Display(self,startval,endval,rxdcallback,stopcb=None):

        self.CancelCallback = stopcb
        if(self.CancelCallback!=None):
            self.StopBut.Show()
        else:
            self.StopBut.Hide()
        self.RxDataCallback=rxdcallback
        self.Status(startval,endval)
        self.CenterOnScreen()
        self.Show()


    def RXData(self,packet,source,dest,rssi):
        if(self.RxDataCallback!=None):
            self.RxDataCallback(packet,source,dest,rssi)


    # Changes the text for the Downloader
    def Status(self,start,end):
        downloadmsg = "Downloading (%03d/%03d)"%(start,end)
        self.StatusLab.SetLabel(downloadmsg)
        self.StatusLab.Refresh()
        gaugeval = (float(start)/float(end))*100.0
        self.gauge.SetValue(gaugeval)



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
