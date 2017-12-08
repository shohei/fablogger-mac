# -*- coding: sjis -*-
import wx
from SettingsFrame import SettingsFrame as SettingsFrame
from DownloadFrame import DownloadFrame as DownloadFrame
from SplashFrame import SplashFrame as SplashFrame
from SensorDataList import SensorDataList as SensorDataList

import time
import Serial_Control
import MsgCodes
from SensorController import Sensor, SensorDialog
import struct

# Main Frame Here

class DeviceData(object):
    def __init__(self, packet):
        #hex = ''.join(hex.split(" "))
        self.DownloadedPacket = {}

        commandcode = packet.pop(0)

        if commandcode == MsgCodes.Response.ADVERTISING:

            self.RXTime = time.time()   
            self.ID = packet.pop(0)+(packet.pop(0)<<8)+(packet.pop(0)<<16)+(packet.pop(0)<<24)+(packet.pop(0)<<32)+(packet.pop(0)<<40)
            self.Temperature = packet.pop(0)+(packet.pop(0)<<8)
            self.Humidity = packet.pop(0)+(packet.pop(0)<<8)
            self.Acceleration_X = packet.pop(0)+(packet.pop(0)<<8)
            self.Acceleration_Y = packet.pop(0)+(packet.pop(0)<<8)
            self.Acceleration_Z = packet.pop(0)+(packet.pop(0)<<8)
            self.Light = packet.pop(0)+(packet.pop(0)<<8)
            self.State = packet.pop(0)
            self.Mode = self.State & 0xF0
            self.State &= 0x0F
            self.Count = packet.pop(0)+(packet.pop(0)<<8)+(packet.pop(0)<<16)
            self.Battery = packet.pop(0)
            packet.pop(0)
            self.Interval =  packet.pop(0) + (packet.pop(0)<<8)


            #Do the conversion of temp and humidity
            self.Humidity = (125.0*float(self.Humidity))/65536.0-6.0
            self.Temperature = (175.72*float(self.Temperature))/65536.0 - 46.85

            #Convert the acceleration values
            if(self.Acceleration_X&0x8000):
                self.Acceleration_X=(0x10000-self.Acceleration_X)*-1
            if(self.Acceleration_Y&0x8000):
                self.Acceleration_Y=(0x10000-self.Acceleration_Y)*-1
            if(self.Acceleration_Z&0x8000):
                self.Acceleration_Z=(0x10000-self.Acceleration_Z)*-1
            self.Acceleration_X = float(self.Acceleration_X) * 0.061 / 980.0
            self.Acceleration_Y = float(self.Acceleration_Y) * 0.061 / 980.0
            self.Acceleration_Z = float(self.Acceleration_Z) * 0.061 / 980.0

        elif commandcode == MsgCodes.Response.DATA:
            # From here 2 bytes of block
            self.Block = packet.pop(0) | packet.pop(0) << 8
            self.DownloadedPacket["Block"]=self.Block
            # Header if block is 0
            if self.Block == 0x00:
                self.Interval = packet.pop(0) | packet.pop(0) << 8
                self.DownloadedPacket["Interval"]=self.Interval
                self.Mode = packet.pop(0)
                self.DownloadedPacket["Mode"]=self.Mode
                self.DownloadCount = packet.pop(0) | packet.pop(0) << 8 | packet.pop(0) << 16
                self.DownloadedPacket["Count"]=self.DownloadCount
                self.Timestamp = packet.pop(0) | packet.pop(0) << 8 | packet.pop(0) << 16 | packet.pop(0) << 24
                self.DownloadedPacket["Timestamp"] = self.Timestamp
            # Here is the data instead
            #         Add to the dictionary
            else:
                # Check if after this packet there is 2 sets of data or not
                self.Temperature = packet.pop(0) + (packet.pop(0) << 8)
                self.Humidity = packet.pop(0) + (packet.pop(0) << 8)
                self.Acceleration_X = packet.pop(0) + (packet.pop(0) << 8)
                self.Acceleration_Y = packet.pop(0) + (packet.pop(0) << 8)
                self.Acceleration_Z = packet.pop(0) + (packet.pop(0) << 8)
                self.Light = packet.pop(0) + (packet.pop(0) << 8)

                #Do the conversion of temp and humidity
                self.Humidity = (125.0*float(self.Humidity))/65536.0-6.0
                self.Temperature = (175.72*float(self.Temperature))/65536.0 - 46.85

                #Convert the acceleration values
                if(self.Acceleration_X&0x8000):
                    self.Acceleration_X=(0x10000-self.Acceleration_X)*-1
                if(self.Acceleration_Y&0x8000):
                    self.Acceleration_Y=(0x10000-self.Acceleration_Y)*-1
                if(self.Acceleration_Z&0x8000):
                    self.Acceleration_Z=(0x10000-self.Acceleration_Z)*-1
                self.Acceleration_X = float(self.Acceleration_X) * 0.061 / 980.0
                self.Acceleration_Y = float(self.Acceleration_Y) * 0.061 / 980.0
                self.Acceleration_Z = float(self.Acceleration_Z) * 0.061 / 980.0

                self.DownloadedPacket["Light"] = self.Light
                self.DownloadedPacket["Acc_Z"] = self.Acceleration_Z
                self.DownloadedPacket["Acc_Y"] = self.Acceleration_Y
                self.DownloadedPacket["Acc_X"] = self.Acceleration_X
                self.DownloadedPacket["Humidity"] = self.Humidity
                self.DownloadedPacket["Temperature"] = self.Temperature

            self.Type = commandcode
            self.Data = self.DownloadedPacket

        elif commandcode == MsgCodes.Response.RESPONSE:
            self.Type = commandcode
            self.Command = packet.pop(0)
            self.Status = packet.pop(0)

        else:
            print "Invalid cmd code"




class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Wireless Module Logger")
        self.Icon = wx.Icon('resources/App.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.Icon)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Setup panels and widgets and sizers
        self.BackgroundBMP = wx.Bitmap("resources/CoreScreen.png")
        panh = self.BackgroundBMP.GetHeight()
        panw = self.BackgroundBMP.GetWidth()

        self.MasterPanel = wx.Panel(self, wx.ID_ANY, size=(panw, panh))
        self.MasterPanel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Here pass the data to the master panel
        # Need to do some stuff
        self.DeviceList = SensorDataList(self.MasterPanel)
        self.DeviceList.SetPosition((12, 105))
        self.DeviceList.SetSize((880, 300))


        self.but_configure = wx.Button(self.MasterPanel, wx.ID_ANY, "Settings", size=(120, 40), pos=(310, 430))
        self.but_download = wx.Button(self.MasterPanel, wx.ID_ANY, "Download Data", size=(120, 40), pos=(470, 430))

        self.but_configure.Bind(wx.EVT_BUTTON,self.OnConfigure)
        self.but_download.Bind(wx.EVT_BUTTON, self.OnDownloadBut)

        self.SetSizeHints(920, 540, 920, 540)
        self.Fit()

        self.LatestDownloadedData = {}

        self.SensorHandler = SensorDialog(self)
        self.SettingsFrame = SettingsFrame(self, self.SensorHandler)
        self.SerialInterface=Serial_Control.Serial_Control()
        self.Sensor=None
        self.Hide()

        self.ScanningBase = 0

        self.CommandHandler = DownloadFrame(self)

        print "Main Frame"

        # self.CommandHandler.Show()
        self.FindBLEDongle()

        # self.Show()


    # Find the device from the COMS
    def FindBLEDongle(self,e=0):
        if(self.ScanningBase==0):
            self.Splash = SplashFrame(self)
            _, self.Ports = self.SerialInterface.ScanPorts()
            self.PortIndex = 0
            self.ScanningBase=1

            tid = wx.NewId()
            wx.RegisterId(tid)
            self.BaseSearchTimer = wx.Timer(self, id=tid)
            self.Bind(wx.EVT_TIMER, self.FindBLEDongle, id=tid)


        self.BaseSearchTimer.Stop()

        if(self.PortIndex<len(self.Ports)):
            self.CurrentPort = self.Ports[self.PortIndex]
            try:
                self.SerialInterface.Disconnect()
            except:
                pass
            self.Splash.Status.SetLabel("Trying port %s"%self.CurrentPort)
            self.Splash.Status.Update()
            self.SerialInterface.Connect(self.SerialRxDispatch,self.CurrentPort,115200)
            self.PortIndex+=1

            self.BaseSearchTimer.Start(milliseconds=100, oneShot=True)
            # Writes to check the device
            self.SerialInterface.SendSBMessage(0xA0,[])
            # Skip the checking and connect
            #self.BaseFound()

        else:
            wx.MessageBox("Could not find the BLE Dongle.  The following ports were checked:\n"+",".join(self.Ports)+"\n Please check the BLE Dongle connection.","Error",wx.ICON_ERROR)
            self.OnClose()

    # This function is called when the connected dongle is found
    def BaseFound(self):
        if(self.ScanningBase==0):
            return

        self.BaseSearchTimer.Stop()
        self.ScanningBase = 0
        #wx.MessageBox("Basestation found on %s"%self.CurrentPort,"Success")
        # self.Splash.Status.SetLabel("BLE Dongle found")
        # dial = wx.MessageDialog(self, "BLE Dongle found on %s.  Connect?"%self.CurrentPort,"Success", wx.YES | wx.NO)
        # ret = dial.ShowModal()
        # if (ret == wx.ID_NO):
        #     self.FindBLEDongle()
        #     return

        self.Splash.Hide()
        self.Splash.Destroy()
        self.CenterOnScreen()
        self.Show()
        Sensor.DisconnectAll(self.SerialInterface)

    def OnDownloadBut(self,e):

        beacon = self.GetSelectedDevice()
        # if(beacon==None):
        #     wx.MessageBox("Please select the module to download data from","Error",wx.ICON_ERROR)
        #     return

        # Change the default file name here
        # save_dialog = wx.FileDialog(self, message="Download data to csv",
        #                             defaultFile="Default_File" + time.strftime("%Y%m%d_%H%M%S.csv", time.localtime(time.time())),
        #                             wildcard="CSV (*.csv)|*.csv", style=wx.SAVE)
        #
        # # Here saves to a csv
        # if save_dialog.ShowModal() == wx.ID_OK:
        #     SaveFilePath = save_dialog.GetPath()
        # else:
        #     return

        # try:
        #     self.SaveFile = open(SaveFilePath,"w");
        # except:
        #     wx.MessageBox("Disk error","Error",wx.ICON_ERROR)

        # self.CommandBeacon = beacon
        # self.DownloadPackets={}
        # self.TotalRetries=0
        #
        # self.Hide()
        # # This is where the Downloader is called
        # # Here the data size needed here, need to pass the cancel function
        # self.CommandHandler.Display(0,5000, self.ProcessRxData, self.stopDownload)
        # self.CommandHandler.SetTimeout(5000,self.DownloadSettingTimeout)
        #
        # # self.SerialInterface.SendPacket(beacon.Source,beacon.channel,HOMECHANNEL,[APP_WIMSG_SENDALLTESTS])

        self.Sensor = Sensor(beacon, self.SerialInterface)
        self.CommandHandler=self.Sensor
        self.SensorHandler.Execute(self.Sensor, MsgCodes.Command.TRANSFER, map(ord, struct.pack("<I",0xFFFF)))

    # Timeout for the download Button
    def DownloadSettingTimeout(self):
        self.Show()
        self.CommandHandler.Finished()
        # self.SaveFile.close()
        print self.DownloadPackets
        wx.MessageBox("Could not download the modules data.  Please check it is in range","Error",wx.ICON_ERROR)

    # Do stuff for when the user cancels the download here
    def stopDownload(self):
        self.Show()
        self.CommandHandler.Finished()


    # Here the Downloaded Data is Processed
    def ProcessDownloadData(self):
        # self.SaveFile.write("Stored Test,Test Time,Test Interval,Start Date, Start Time,Source Module,Source TestNo,Channel,Power,Mode,Packet Interval,Total Packets,Avg Rssi,Lost Packets, PER, Cont Retries, Total Retries\n")
        pass

    # Here we get the packets that come from the UART
    # Need to update the Download bar
    # Sends commands via UART if the packets are lost
    # Packets here are strings
    # Process data here
    def ProcessRxData(self,packet):
        print repr(packet)
        self.CommandHandler.Notify()
        # self.CommandHandler.SetTimeout(5000,self.DownloadSettingTimeout)
        # self.CommandHandler.Status("Downloading (%03d/%03d)"%(len(self.DownloadPackets),self.CommandBeacon.StoredData))
        pass


    def AddNewPacket(self):
        pass

    # Called when the setting button is pressed
    def OnConfigure(self,e):
        beacon = self.GetSelectedDevice()
        # if(beacon==None):
        #     wx.MessageBox("Please select a module to configure","Error",wx.ICON_ERROR)
        #     return
        self.CommandHandler = SettingsFrame(self, self.SensorHandler)
        self.SettingsFrame.Display(beacon)

    # Get the selected device
    def GetSelectedDevice(self):
        target = self.DeviceList.GetSelectedItem()
        if (target == -1):
            return None
        else:
            return self.DeviceList.GetEntryObject(target)


    # This function will add the packet data to settings
    def DispatchAppPacket(self,source,dest,rssi,packet):
        #This is possible for ack packets
        self.CommandHandler.RXData(packet,source,dest,rssi)


    # The serial packets come through here from the Serial Library
    # Check all the data here and pass to the respective functions
    def SerialRxDispatch(self,packet):
        #print packet
        if not packet:
            return
        if packet[0] == 0xAD:
            device = DeviceData(packet)
            self.DeviceList.AddEntry(device)
        elif packet[1] == 0xDA:
            size = packet.pop(0)
            devicedata = DeviceData(packet)
            devicedata.Size=size
            self.LatestDownloadedData[devicedata.Block] = devicedata.DownloadedPacket
            try:
                self.CommandHandler.RX(devicedata)
            except AttributeError:
                pass
        elif packet[0] == 0xDD:
            devicedata = DeviceData(packet)
            if self.ScanningBase:
                self.BaseFound()
            try:
                self.CommandHandler.RX(devicedata)
            except AttributeError:
                pass

    def OnClose(self, e=0):
        try:
            self.SerialInterface.Disconnect()
        except:
            pass

        self.DestroyChildren()
        self.Destroy()

    def OnEraseBackground(self, evt):
        # yanked from ColourDB.py
        dc = evt.GetDC()

        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()

        dc.DrawBitmap(self.BackgroundBMP, 0, 0)

    def SendCommand(self, cmd, data):

        if cmd == MsgCodes.Command.CONNECT:
            if not hasattr(data,'ID'):
                return
            an = data.ID
            address = [(an)&0xFF, (an>>8)&0xFF, (an>>16)&0xFF, (an>>24)&0xFF, (an>>32)&0xFF, (an>>40) &0xFF]
            self.SerialInterface.SendSBMessage(MsgCodes.Command.CONNECT, address)

        elif cmd == MsgCodes.Command.DISCONNECT:
            self.SerialInterface.SendSBMessage(MsgCodes.Command.DISCONNECT,[])

        else:
            self.SerialInterface.SendSBMessage(cmd, data)
#*****************************MAIN PROGRAM**************************************


app = wx.App(False)
frame = MainFrame()

app.MainLoop()


