from time import sleep
from collections import deque
import MsgCodes
import wx, wx.animate
import time
import struct
def InvState():
    print 'Invalid State'

class SensorDialog(wx.Frame):

    class States():
        IDLE='IDLE'
        DISCONNECTED='Disconnected'
        Disconnecting='Disconnecting'
        CONNECTED ='Connected'
        Connecting='Connecting'
        Sending='Sending command'
        Waiting='Waiting for response'
        DOWNLOAD='Downloading'
        RESPONSE='Success'
        ERROR='Error'

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Contacting Logger")

        self.Sensor = None
        self.Command = None
        self.Data = None
        self.Packets = {}
        self.Savefile = None
        self.SaveFilePath=None
        self.Retries=0

        self.SetClientSize((450,150))

        self.MasterPanel= wx.Panel(self,pos=(0,0),size=(450,150))
        self.MasterPanel.SetBackgroundColour((255,255,255))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Spinner and connection status
        gif = wx.animate.GIFAnimationCtrl(self.MasterPanel, -1, "resources/loader.gif",
                                          pos=(30, 40), size=(10,10))
        gif.GetPlayer().UseBackgroundColour(True)
        self.gif = gif

        self.txtStatus  = wx.StaticText(self.MasterPanel, -1, label="Connecting",
                                        size=(200, -1), pos=(150,30))
        font = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.txtStatus.SetFont(font)

        self.ggProgress = wx.Gauge(self.MasterPanel, -1, 100, size=(200, 25), pos=(150,60))
        self.txtProgress = wx.StaticText(self.MasterPanel, -1, label="", size = (100,-1), pos=(200, 90))

        self.btnCancel = wx.Button(self.MasterPanel, -1, "Cancel", size=(60,25), pos=(225, 110))
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnClose)

        self.State = self.States.IDLE

        tid = wx.NewId()
        self.DownloadTimer = wx.Timer(self, id=tid)
        self.Bind(wx.EVT_TIMER, self.OnDownloadTimeout, id=tid)

        self.Hide()


    def OnCommandTimeout(self):
        print 'Timeout'
        self.Finish()


    def Execute(self, sensor, command, data):

        self.Sensor = sensor
        self.Command = command
        self.Data = data

        if command == MsgCodes.Command.TRANSFER:
            save_dialog = wx.FileDialog(self, message="Download data to csv",
                defaultFile="%X_%s.csv"% (
                    self.Sensor.BeaconData.ID, \
                    time.strftime("%Y%m%d_%H%M%S",time.localtime())),
                wildcard="CSV (*.csv)|*.csv", style=wx.SAVE)

            # Here saves to a csv
            if save_dialog.ShowModal() == wx.ID_OK:
                self.SaveFilePath = save_dialog.GetPath()
            else:
                print 'Cancelling'
                return

            self.Packets.clear()
            self.ggProgress.Show()
            self.ggProgress.SetValue(0);
            self.txtProgress.Show()
            self.txtProgress.SetLabel(" %d / %d (%0.1f%%)"%(len(self.Packets), self.Sensor.BeaconData.Count, float(len(self.Packets)) / self.Sensor.BeaconData.Count * 100))

        else:
            self.ggProgress.Hide()
            self.txtProgress.Hide()


        self.Sensor.SetResponseHandler(self.NotifyResponse)
        self.Sensor.SetDownloadHandler(self.NotifyDownload)

        self.CenterOnScreen()
        self.Show()
        self.gif.Play()

        if self.State == self.States.IDLE:
            self.txtStatus.SetLabel("Connecting")
            self.Sensor.Connect()
            self.Sensor.TX()
        else:
            if command == MsgCodes.Command.STOP:
                self.txtStatus.SetLabel("Stopping")
                self.Sensor.ForceStop()
            else:
                self.txtStatus.SetLabel("")
                InvState()

    def Finish(self):

        self.Sensor.SetDownloadHandler(None)
        self.Sensor.SetResponseHandler(None)

        self.Sensor.ForceDisconnect()
        self.Sensor = None
        self.State = self.States.IDLE
        self.gif.Stop()
        self.Hide()

    def SaveData(self):
        self.txtStatus.SetLabel("Saving")
        HeaderPacket = self.Packets.get(0)
        interval = (HeaderPacket['Interval'] & 0x7FFF)
        if HeaderPacket['Interval'] & 0x8000:
            st='ms'
            rate = float(interval) / 1000
        else:
            st = 's'
            rate = float(interval)



        print hex(self.Sensor.BeaconData.ID), \
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(HeaderPacket['Timestamp'])), \
                 HeaderPacket['Count'], \
                 HeaderPacket['Interval']

        Header1 = "Sensor ID, %X\nTimestamp,%s\nSamples,%d\nInterval,%d%s\n"% \
                  (self.Sensor.BeaconData.ID, \
                    time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(HeaderPacket['Timestamp'])), \
                    HeaderPacket['Count'], \
                    interval, st)

        Header2 = "\nSample #, Temperature, Humidity, Lux, Acc X, Acc Y, Acc Z\n"

        try:
            self.Savefile = open(self.SaveFilePath, "w")
        except Exception:
            wx.MessageBox("Error", "File error", wx.ICON_ERROR)
            return

        try:
            self.Savefile.write(Header1)
            self.Savefile.write(Header2)

            for i in range(1,len(self.Packets)):
                p = self.Packets.get(i)
                self.Savefile.write("%s,%0.1f,%0.1f,%0.1f,%.2f,%.2f,%.2f\n"%(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(HeaderPacket['Timestamp'] + round(i*rate))),
                    p['Temperature'],
                    p['Humidity'],
                    p['Light'],
                    p['Acc_X'],
                    p['Acc_Y'],
                    p['Acc_Z']))
            self.txtStatus.SetLabel("Complete")
        finally:
            self.Savefile.close()
            sleep(0.5)
            self.Finish()




    def NotifyResponse(self, response):

        if response == self.States.CONNECTED:
            self.State = response
            self.txtStatus.SetLabel(self.States.Sending)
            self.Sensor.SendCommand(self.Command, self.Data)

        elif response == SensorDialog.States.RESPONSE:
            self.State = response

            if self.Command != MsgCodes.Command.TRANSFER:
                self.txtStatus.SetLabel(response)
                self.Sensor.Disconnect()
            else:
                self.txtStatus.SetLabel("Downloading")

        elif response == SensorDialog.States.ERROR:
            self.txtStatus.SetLabel(response)
            sleep(1)
            self.Close()

        elif response == SensorDialog.States.DISCONNECTED:
            #self.txtStatus.SetLabel(response)
            sleep(1)
            self.Close()

    def NotifyDownload(self, packet):
        self.DownloadTimer.Stop()
        self.DownloadTimer.Start(milliseconds=1000, oneShot=True)
        self.Retries = 10
        print packet["Block"], " of ", self.Sensor.BeaconData.Count

        self.Packets[packet["Block"]] = packet
        progress = float(len(self.Packets)) / self.Sensor.BeaconData.Count * self.ggProgress.GetRange()
        self.ggProgress.SetValue(progress)
        self.txtProgress.SetLabel(" %d / %d (%0.1f%%)" % (len(self.Packets)-1, self.Sensor.BeaconData.Count, float(len(self.Packets)-1) / self.Sensor.BeaconData.Count * 100))

    def OnDownloadTimeout(self,evt):
        # Check data length
        if len(self.Packets) < self.Sensor.BeaconData.Count+1:
            print "Missing %d packets\n"%(self.Sensor.BeaconData.Count + 1 - len(self.Packets))
            for i in range(0,self.Sensor.BeaconData.Count + 1):
                try:
                    # Throws key exception if missing
                    if self.Packets[i]: pass
                except KeyError:
                    self.Retries -= 1
                    if self.Retries > 0:
                        # Try to download specific packet
                        print 'Retrying ', i
                        self.Sensor.SendCommand(MsgCodes.Command.TRANSFER, map(ord, struct.pack("<I",i)))
                        self.Sensor.TX()
                        self.DownloadTimer.Start(milliseconds=200, oneShot=True)
                        return
                    else:
                        # Download failed
                        self.txtStatus.SetLabel("Download failed")
                        sleep(1)
                        self.Finish()
        else:
            print "Download complete"
            self.txtProgress.SetLabel(" %d / %d (%0.1f%%)" % (self.Sensor.BeaconData.Count, self.Sensor.BeaconData.Count,
                                                              float(len(
                                                                  self.Packets) - 1) / self.Sensor.BeaconData.Count * 100))
            sleep(0.5)
            self.SaveData()

    def CancelDownload(self):
        self.Sensor.SendCommand(MsgCodes.Command.STOP, [])
        self.Sensor.TX()

    def OnClose(self, evt):
        self.Finish()


class Sensor(object):

    Intervals = [0x81F4, 1, 10, 30, 60, 120, 300, 900, 1800, 3600]
    IntervalStr = ['500ms','1s','10s','30s','1m','2m','5m','15m','30m','1h']

    Modes = [0, 1]

    def __init__(self, beacondata, ser_iface):
        self.State = 0
        self.BeaconData = beacondata
        self.Serial = ser_iface
        self.Commands = deque()
        self.CurrentCommand = {}
        self.ResponseCallback=None
        self.DownloadCallback=None

        an = self.BeaconData.ID
        self.AddressBytes = [(an) & 0xFF, (an >> 8) & 0xFF, (an >> 16) & 0xFF, (an >> 24) & 0xFF, (an >> 32) & 0xFF,
             (an >> 40) & 0xFF]

    @staticmethod
    def DisconnectAll(serial):
        serial.SendSBMessage(MsgCodes.Command.DISCONNECT, [])

    def Connect(self):
        self.Commands.append({'cmd':MsgCodes.Command.CONNECT,'data':self.AddressBytes})
        print 'Connecting'


    def Disconnect(self):
        print 'Disconnecting'
        self.Commands.append({'cmd': MsgCodes.Command.DISCONNECT, 'data': []})
        self.TX()

    # Clears the command queue and sends a disconnect request
    def ForceDisconnect(self):
        self.Commands.clear()
        self.Disconnect()

    def SendCommand(self, cmd, data):
        print 'Sending Command'
        self.Commands.append({'cmd':cmd,'data':data})

    # Clears the command queue and sends the stop command
    def ForceStop(self):
        self.Commands.clear()
        self.SendCommand(MsgCodes.Command.STOP, [])

    def TX(self):
        if self.Commands:
            self.CurrentCommand = self.Commands.popleft()
            self.Serial.SendSBMessage(self.CurrentCommand['cmd'], self.CurrentCommand['data'])

    def RX(self, response):
        notif = None

        # RESPONSE handling (state change allowed)
        if response.Type == MsgCodes.Response.RESPONSE:
            if response.Command == MsgCodes.Command.CONNECT:
                if response.Status == MsgCodes.Status.BLE_OK:
                    print "Connected to peripheral"
                    self.State = 1
                    notif = SensorDialog.States.CONNECTED
                else:
                    print "Error connecting to device"
                    notif = SensorDialog.States.DISCONNECTED

            elif response.Command == MsgCodes.Command.DISCONNECT:
                print "Disconnected from peripheral"
                self.State = 0
                notif = SensorDialog.States.DISCONNECTED

            else:
                if response.Status > 0:
                    print "BLE Error"
                    notif = SensorDialog.States.ERROR
                else:
                    notif = SensorDialog.States.RESPONSE

            # Notify caller that a response was received
            if self.ResponseCallback is not None:
                self.ResponseCallback(notif)
            self.TX()

        elif response.Type == MsgCodes.Response.DATA:
            if self.DownloadCallback is not None:
                self.DownloadCallback(response.Data)

    def SetResponseHandler(self, caller):
        self.ResponseCallback = caller

    def SetDownloadHandler(self, caller):
        self.DownloadCallback = caller



