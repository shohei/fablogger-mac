# -*- coding: sjis -*-
import serial
import time
import glob
import wx
from threading import *
import Queue
from sys import platform as _platform


# Thread class that executes processing
class SerialReader(Thread):

    OrdLookup={}


    """Worker Thread Class."""
    def __init__(self, serialconnection, DataQ, notifyfunc):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._want_abort = 0
        self.ser= serialconnection

        self.ser.flush()
        self.ser.flushInput()

        for a in range(256):
          self.OrdLookup[chr(a)]=a;

        self.stop_collection=0
        self.delim_code = [0xFA,0x5A]

        self.SerialDataQ=DataQ

        self.Readlist=['']*200
        self.ReadBytes=0
        self.ReadIndex=0

        self._NotifyFunction_ = notifyfunc

        self.start()

    def get_Next_chunk(self):
        if(self.ser!=None):
            try:
                # Function Read up to len(b) bytes into bytearray b and return the number of bytes read.
                temp_read = self.ser.readinto(self.Readlist)
            except:
                return 0

        #print "READIN ",temp_read
        while(temp_read==0 and self.stop_collection==0):
            time.sleep(0.005)
            try:
                temp_read = self.ser.readinto(self.Readlist)
            except:
                return 0

        #print "READ A CHUNK!",temp_read

        for i in range(temp_read):
          self.Readlist[i]=self.OrdLookup[self.Readlist[i]]
        #print self.Readlist
        return temp_read

    def get_Next_byte(self):
        #print "GET NEXT BYTE!"
        # ReadBytes are how many bytes there are
        if(self.ReadIndex<self.ReadBytes):
          #print "RETURNING", self.ReadIndex
          bt=self.Readlist[self.ReadIndex]
          self.ReadIndex+=1
          return bt
        else:
          #print "nothing left in chunk, get next chunk:::",
          self.ReadIndex=1
          #print "Reading..",
          self.ReadBytes=self.get_Next_chunk()
          #print "Read ",self.ReadBytes
          return self.Readlist[0]

    def run(self):

        print "Thread started!"
        temp = []
        delimsearch=[0,0]
        self.ser.flushInput()

        while(self.stop_collection==0):

                delimsearch=[0,0]
                while delimsearch!=self.delim_code and self.stop_collection==0:
                    # Searches for the Starting bytes
                    delimsearch[0]=delimsearch[1]
                    #nextbyte = self.get_Next_byte()
                    #print nextbyte
                    delimsearch[1]=self.get_Next_byte()
                    #print self.ser.inWaiting()
                try:
                    # Gets the packet lenght
                    packet_length = self.get_Next_byte()
                    #temp.append(packet_length)
                    checksum = packet_length

                    # Gets the actual packet data
                    for a in range(packet_length):
                        nextbyte = self.get_Next_byte()
                        temp.append(nextbyte)
                        checksum^=nextbyte
                    #actualcheck = self.get_Next_byte()

                except:
                    print "Serial Error"

                # print temp
                #try:
                #    if(actualcheck==checksum):
                self.SerialDataQ.put(temp[:])
                wx.CallAfter(self._NotifyFunction_)
                #    else:
                #        print "Checksum Error"
                #except:
                #    pass

                del temp[:]

                #del delimsearch[:]
        print "Thread Complete!"

    def StopCollection(self):
        self.ser = None
        self.stop_collection=1




class Serial_Control(object):

    def __init__(self, delimcode=['\xF5','\x5F']):
        #self.type='serial'
        self.delimcode=delimcode
        self.stop_collection=1
        self.connected=0
        self.ser=None
        self.SerialDataQ = Queue.Queue(0) # arg1 means "No item limit"

    def Init_Serial(self,comport,baudrate):

        self.ser = serial.Serial(comport, baudrate, timeout=0)
        self.ser.flushInput()
        self.stop_collection = 0

    def write_to_serial(self,byteString):
        for i in range(len(byteString)):
            self.ser.write(chr(byteString[i]))

    def SendPacket(self,TargetID,StartChannel,EndChannel,Payload):

        TargetList = [(TargetID >> (0*8))&0xFF,
                  (TargetID >> (1*8)) & 0xFF,
                  (TargetID >> (2*8)) & 0xFF,
                  (TargetID >> (3*8)) & 0xFF,
                  (TargetID >> (4*8)) & 0xFF,
                  (TargetID >> (5*8)) & 0xFF]


        UartMsg = [StartChannel,EndChannel,0]+TargetList+Payload


        self.SendSBMessage(0x11, UartMsg)


    def SendSBMessage(self,MsgCode,Payload):
        pass #Legacy definition
        Length = len(Payload)+1

        Checksum = MsgCode^Length

        for byte in Payload:
            Checksum^=byte

        sendpacket = [0xFA,0x5A,Length,MsgCode]
        sendpacket += Payload
        sendpacket.append(Checksum)

        print "SENDING: ",sendpacket

        self.write_to_serial(sendpacket)


    def ScanLinux(self):
      port_names = glob.glob('/dev/ttyUSB*')
      port_nums = port_names[:]
      return port_nums,port_names

    def ScanMac(self):
      port_names = glob.glob('/dev/tty.usbserial*')
      port_nums = port_names[:]
      return port_nums,port_names

    def ScanPorts(self):
        #return [],[]
        return self.ScanMac()
        """ never reached """

        if _platform == "linux" or _platform == "linux2":
          return self.ScanLinux()

        port_nums= []
        port_names=[]

        print "Scanning"
        for port in range(256):
            try:
                connected_port = serial.Serial("COM%i"%port)
                port_nums.append("COM%i"%port)
                port_names.append(connected_port.portstr)
                connected_port.close()
            except:
                pass

        return port_nums,port_names


    def Disconnect(self):
        self.connected=0
        try:
          self.sreader.StopCollection()
          self.ser.close()
          self.ser=None
          self.sreader = None
        except:
          pass

    def Connect(self, callback, com, rate):
        try:
          self.sreader.StopCollection()
          self.schecker.StopThread()
        except:
          pass
        self.Init_Serial(com,rate)
        self.connected=1
        self.__notifyfunc__=callback
        self.sreader = SerialReader(self.ser,self.SerialDataQ,self.on_serial_rxpacket)
        return 1

    def SetCallback(self,callback):
        self.__notifyfunc__=callback;

    def GetNextPacket(self):
      pack = -1
      try:
          pack = self.SerialDataQ.get(False)
      except:
          pass

      return pack;

    def IsConnected(self):
        return self.connected

    def on_serial_rxpacket(self):
      packet = self.GetNextPacket()
      #print "PCK"
      while(packet!=-1):
        self.__notifyfunc__(packet)
        packet = self.GetNextPacket()
