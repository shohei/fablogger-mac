# -*- coding: sjis -*-
import KMLists
import time
import datetime

# This is the main data for the main panel
class SensorDataList(KMLists.TestListCtrlPanel):

    def __init__(self, masterpan):
        super(SensorDataList, self).__init__(masterpan, ["RX Time", "Sensor ID", "State", "Interval","Lux" , "Accelerometer X,Y,Z", "Temp", "Humid","Battery","Count"])
        self.SetColumWidths([120, 110, 50, 50, 50, 150, 70, 100,100,150])
        #self.Set
        self.SetListDataFormatter(self.BeaconListFormatter)

    # Add the stuff to the List
    def AddEntry(self, bdata):
        datakey = bdata.ID
        extractdata =[bdata.RXTime, bdata.ID, bdata.State, bdata.Interval, bdata.Light, bdata.Acceleration_X, bdata.Temperature , bdata.Humidity,  bdata.Battery, bdata.Count]
        if (self.IsDataInList(datakey) != -1):
            self.ReplaceExistingEntry(datakey, extractdata,objdata=bdata)  # coloring=[(5, BS_StatColourLut[bdata.CurrentState])]
        else:
            self.AddNewEntry(datakey, extractdata, objdata=bdata)


        # A dirty dirty hack to get the masters and slaves to update when they cant send beacons
        # if(bdata.State==2):
        #     pairo = None
        #     try:
        #         pairo = self.GetEntryObject(bdata.Dest)
        #     except:
        #         pass
        #     if(pairo!=None):
        #         if(pairo.State==1 and pairo.channel == bdata.channel and pairo.Dest==bdata.Source):
        #             pairo.CurrentPacket = pairo.TotalPacket
        #             pairo.State=10
        #             pairext = [pairo.Source, pairo.rxtime, pairo.Rssi, pairo.channel, pairo.State, 0,pairo.TotalPacket,pairo.NextTestCD,pairo.StoredData]
        #             self.ReplaceExistingEntry(pairo.Source, pairext, objdata=pairo) #coloring=[(5, BS_StatColourLut[bdata.CurrentState])]
        # if(bdata.State==1):
        #     pairo = None
        #     try:
        #         pairo = self.GetEntryObject(bdata.Dest)
        #     except:
        #         pass
        #     if(pairo!=None):
        #         if((pairo.State==0 or pairo.State==2) and pairo.channel == bdata.channel):
        #             if((int(time.time())-pairo.rxtime)>2):
        #                 pairo.State=20
        #                 pairo.Dest=bdata.Source
        #                 pairo.CurrentPacket=0
        #                 pairext = [pairo.Source, pairo.rxtime, pairo.Rssi, pairo.channel, pairo.State, 0,pairo.TotalPacket,pairo.NextTestCD,pairo.StoredData]
        #                 self.ReplaceExistingEntry(pairo.Source, pairext, objdata=pairo) #coloring=[(5, BS_StatColourLut[bdata.CurrentState])]
        #
        #     for key,val in self.objectdata.iteritems():
        #         if(val.channel == bdata.channel and val.State==0):
        #             if((int(time.time())-val.rxtime)>2):
        #                 val.Dest=bdata.Source
        #                 val.State=20
        #                 pairext = [val.Source, val.rxtime, val.Rssi, val.channel, val.State, 0,val.TotalPacket,val.NextTestCD,val.StoredData]
        #                 self.ReplaceExistingEntry(key, pairext, objdata=val) #coloring=[(5, BS_StatColourLut[bdata.CurrentState])]
        #
        #
        # extractdata = [bdata.Source, bdata.rxtime, bdata.Rssi, bdata.channel, bdata.State, 0,bdata.CurrentTestNo,bdata.NextTestCD,bdata.StoredData]
        #
        # key = bdata.Source
        #
        # if(self.IsDataInList(key) != -1):
        #     self.ReplaceExistingEntry(key, extractdata, objdata=bdata) #coloring=[(5, BS_StatColourLut[bdata.CurrentState])]
        # else:
        #     self.AddNewEntry(key, extractdata, objdata=bdata)

    def Reset(self):
        self.ClearList()

    # Append so it shows on the List
    # Do all the calculations here
    def BeaconListFormatter(self, data, objdata):
        Fdata = []

        Fdata.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(objdata.RXTime)))
        Fdata.append("0x%X"%objdata.ID)
        Fdata.append(["Off","Idle","Sensing","Download"][objdata.State])
        if objdata.Interval & 0x8000:
            Fdata.append("%ims" % (objdata.Interval & 0x7FFF))
        else:
            Fdata.append("%is"%objdata.Interval)
        Fdata.append("%i"%objdata.Light)
        Fdata.append("%0.2f ,%0.2f, %0.2f"%(objdata.Acceleration_X,objdata.Acceleration_Y,objdata.Acceleration_Z))
        Fdata.append("%0.1f"%objdata.Temperature)
        Fdata.append("%0.1f"%objdata.Humidity)
        Fdata.append("%i%%"%objdata.Battery)
        Fdata.append("%i"%objdata.Count)

        return Fdata

