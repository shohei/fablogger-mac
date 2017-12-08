import  wx.lib.mixins.listctrl  as  listmix
import wx

try:
    from agw import ultimatelistctrl as ULC
except ImportError: # if it's not there locally, try the wxPython lib.
    from wx.lib.agw import ultimatelistctrl as ULC


class TestUltimateListCtrl(ULC.UltimateListCtrl):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, agwStyle=0):

        ULC.UltimateListCtrl.__init__(self, parent, id, pos, size, style, agwStyle)


class TestListCtrl(wx.ListCtrl):

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class TestListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent, cols,selectable=1):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.WANTS_CHARS)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.list = TestUltimateListCtrl(self, wx.ID_ANY,
                                         agwStyle=wx.LC_REPORT
                                         #| wx.BORDER_SUNKEN
                                         | wx.BORDER_NONE
                                         | ULC.ULC_BORDER_SELECT
                                         #| wx.LC_EDIT_LABELS
                                         #| wx.LC_SORT_ASCENDING
                                         #| wx.LC_NO_HEADER
                                         | wx.LC_VRULES
                                         | wx.LC_HRULES
                                         | wx.LC_SINGLE_SEL)
                                         #| ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)


        sizer.Add(self.list, 1, wx.EXPAND|wx.GROW)

        wxImgAu = wx.EmptyBitmap( 1, 1 )     # Create a bitmap container
        wxImgAu.LoadFile( "resources/icons/ArrowUp.png", wx.BITMAP_TYPE_ANY )

        wxImgAd = wx.EmptyBitmap( 1, 1 )     # Create a bitmap container
        wxImgAd.LoadFile( "resources/icons/ArrowDown.png", wx.BITMAP_TYPE_ANY )

        self.selen = selectable

        self.il = wx.ImageList(16, 16)

        self.sm_up = self.il.Add(wxImgAu)
        self.sm_dn = self.il.Add(wxImgAd)
        #self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
        #self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())

        self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self.Columns = cols
        self.ColWidths = []
        self.CreateColumns(cols)
        self.itemDataMap = {}
        self.objectdata = {}
        listmix.ColumnSorterMixin.__init__(self, len(self.Columns))

        self.SetSizer(sizer)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)

        self._ListDataFormatter = self.DataFormatter


    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)


    #this disables item selection
    def OnItemSelected(self,event):
        if(self.selen==0):
            currentItem = event.m_itemIndex
            self.list.SetItemState(currentItem, 0, wx.LIST_STATE_SELECTED)

    def DataFormatter(self,data):
        Fdata = []
        for e in data:
            Fdata.append(str(e))
        return Fdata

    def SetListDataFormatter(self,formatter):
        self._ListDataFormatter = formatter




    def CreateColumns(self,columns):

        for c in range(len(columns)):
            info = ULC.UltimateListItem()
            info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONTCOLOUR
            info._image = []
            info._format = 0
            info._kind = 1
            info._text = columns[c]
            self.list.InsertColumnInfo(c, info)

    def SetColumWidths(self,widths):
        self.ColWidths = widths
        for w in range(len(widths)):
            self.list.SetColumnWidth(w,widths[w])




    #The coloring paramter should be a list, with each entry being a tuple containing
    #the column to color and the color.  Eg. Coloring = [(0,wx.RED),(2,wx.GREEN)] etc.
    def AddNewEntry(self,key,data,objdata=None,coloring=None):

        if(key in self.itemDataMap):
            raise Exception("The specified key is allready in the list!")

        if(len(data)==0):
            raise Exception("Must specify atleast 1 data point")

        FormattedData = self._ListDataFormatter(data,objdata)

        self.objectdata[key]=objdata;
        self.itemDataMap[key]=data
        index = self.list.GetItemCount()
        index = self.list.InsertStringItem(index,FormattedData[0])

        print "New device @ ", index

        for i in range(1,len(FormattedData)):
            self.list.SetStringItem(index,i,FormattedData[i])

        self.list.SetItemData(index, key)

        if(coloring!=None):
            #print "SETTING COLOR"
            for c in coloring:
                item = self.list.GetItem(index, c[0])
                item.SetMask(ULC.ULC_MASK_FONTCOLOUR)
                item.SetTextColour(c[1])
                self.list.SetItem(item)

                if(c[0]==0):
                    for rc in range(1,len(self.Columns)):
                        item = self.list.GetItem(index, rc)
                        item.SetMask(ULC.ULC_MASK_FONTCOLOUR)
                        item.SetTextColour(wx.BLACK)
                        self.list.SetItem(item)
                #self.list.SetItem(item)
        #return index






    def ReplaceExistingEntry(self,key,data,objdata=None,coloring=None):

        if(not key in self.itemDataMap):
            raise Exception("The specified key is not in the list!")

        if(len(data)==0):
            raise Exception("Must specify atleast 1 data point.  Use RemoveData to remove an item from the list")

        index = self.list.FindItemData(-1,key)

        if(index==-1):
            raise Exception("The specified key is not in the list!")

        self.objectdata[key]=objdata;
        self.itemDataMap[key]=data

        FormattedData = self._ListDataFormatter(data,objdata)
        for i in range(len(FormattedData)):
            self.list.SetStringItem(index,i,FormattedData[i])

        if(coloring!=None):
            #print "SETTING COLOR"
            for c in coloring:
                item = self.list.GetItem(index, c[0])
                item.SetMask(ULC.ULC_MASK_FONTCOLOUR)
                item.SetTextColour(c[1])
                self.list.SetItem(item)

                if(c[0]==0):
                    for rc in range(1,len(self.Columns)):
                        item = self.list.GetItem(index, rc)
                        item.SetMask(ULC.ULC_MASK_FONTCOLOUR)
                        item.SetTextColour(wx.BLACK)
                        self.list.SetItem(item)

        print "Updated dev", index

    def GetEntryObject(self,key):
        if(not key in self.objectdata):
            raise Exception("The specified key is not in the list!")
        return self.objectdata[key]

    def RemoveEntry(self,key):
        if(not key in self.itemDataMap):
            raise Exception("The specified key is not in the list!")
        index = self.list.FindItemData(-1,key)
        if(index==-1):
            raise Exception("The specified key is not in the list!")

        self.list.DeleteItem(index)
        del self.itemDataMap[key]
        del self.objectdata[key]

    def GetEntryData(self,key):
        if(not key in self.itemDataMap):
            raise Exception("The specified key is not in the list!")
        return self.itemDataMap[key]

    def IsDataInList(self,key):
        index = self.list.FindItemData(-1,key)
        return index

    def ClearList(self):
        self.list.ClearAll()
        self.itemDataMap = {}
        self.objectdata = {}
        self.CreateColumns(self.Columns)
        self.SetColumWidths(self.ColWidths)

    def GetSelectedItem(self):
        if(self.list.GetFirstSelected()==-1):
            return -1

        return self.list.GetItemData(self.list.GetFirstSelected())

    def GetDataObjects(self):
      return self.objectdata.copy()

    def GetSelectedRowNo(self):
        return self.list.GetFirstSelected()

    def GetRowNoData(self,RowNo):
        return self.GetEntryData(self.list.GetItemData(RowNo))

    def GetTotalRows(self):
        return self.list.GetItemCount()

    def SetRowSelection(self,RowNo):
        self.list.SetItemState(RowNo, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)



class RoundRobinList(TestListCtrlPanel):
    def __init__(self, parent, cols, maxentries=100):
        super(RoundRobinList, self).__init__(parent,cols);
        self.KeyOrderTracker = []
        self.MaxEntries = maxentries


    def AddNewEntry(self,key,data,coloring=None):
        super(RoundRobinList, self).AddNewEntry(key,data,coloring)
        self.KeyOrderTracker.append(key)

        while(len(self.KeyOrderTracker)>self.MaxEntries):
            PopKey = self.KeyOrderTracker.pop(0)
            self.RemoveEntry(PopKey)

    def ClearList(self):
        super(RoundRobinList, self).ClearList()
        self.KeyOrderTracker = []

    def RemoveEntry(self,key):
        super(RoundRobinList, self).RemoveEntry(key)
        if(key in self.KeyOrderTracker):
            self.KeyOrderTracker.remove(key)


import time

class TimeControlledRoundRobinList(TestListCtrlPanel):
    def __init__(self, parent, cols, maxtime=3600):
        super(TimeControlledRoundRobinList, self).__init__(parent,cols);
        self.TimeOrderTracker = []
        self.KeyOrderTracker = []
        self.MaxTime = maxtime

    def SetMaxTime(self,mtime):
        self.MaxTime=mtime

    def AddNewEntry(self,key,data):
        super(TimeControlledRoundRobinList, self).AddNewEntry(key,data)
        Ctime = int(time.time())
        self.KeyOrderTracker.append(key)
        self.TimeOrderTracker.append(Ctime)

        Oldest = self.TimeOrderTracker[0]
        while((Ctime-Oldest)>self.MaxTime):
            PopKey  = self.KeyOrderTracker.pop(0)
            PopTime = self.TimeOrderTracker.pop(0)
            Oldest = self.TimeOrderTracker[0]
            self.RemoveEntry(PopKey)

    def ClearList(self):
        super(TimeControlledRoundRobinList, self).ClearList()
        self.KeyOrderTracker = []
        self.TimeOrderTracker = []

    def RemoveEntry(self,key):
        super(TimeControlledRoundRobinList, self).RemoveEntry(key)
        if(key in self.KeyOrderTracker):
            keyind = self.KeyOrderTracker.index(key)
            self.KeyOrderTracker.pop(keyind)
            self.TimeOrderTracker.pop(keyind)
