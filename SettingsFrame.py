# -*- coding: sjis -*-

from SensorController import *
# This is for the Settings Frame
class SettingsFrame(wx.Frame):

    def __init__(self,parent, sensdialog):

        wx.Frame.__init__(self, parent, title="Configure Node",size=(400,360))
        self.Icon = wx.Icon('resources/App.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.Icon)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.WinParent=parent
        self.SensorDlg = sensdialog
        self.Sensor=None
        self.MasterPan = wx.Panel(self)

        #Create the title, HERE CHANGE TO SPECIFIC MODULE NAME
        TitleFont = wx.Font(12, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False)
        self.ConfigModuleTitle = wx.StaticText(parent=self.MasterPan, label="Module: ", style=wx.ST_NO_AUTORESIZE)
        self.ConfigModule = wx.StaticText(parent=self.MasterPan, label="xxxxxxxx", style=wx.ST_NO_AUTORESIZE)
        self.ConfigModeTitle = wx.StaticText(parent=self.MasterPan, label="Current Mode:", style=wx.ST_NO_AUTORESIZE)
        self.ConfigMode = wx.StaticText(parent=self.MasterPan, label="-------")
        # Setting the Font
        self.ConfigModuleTitle.SetFont(TitleFont)
        self.ConfigModule.SetFont(TitleFont)
        self.ConfigModeTitle.SetFont(TitleFont)
        self.ConfigMode.SetFont(TitleFont)


        #Create the list of controls
        self.WidgetsPan = wx.Panel(self.MasterPan)
        self.WidgetList = {}
        self.BuildWidgetList(self.WidgetsPan)

        #Create the buttons
        ButPan = wx.Panel(self.MasterPan)
        self.BuildButtons(ButPan)

        #Add to sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        modulebox = wx.BoxSizer(wx.HORIZONTAL)
        modebox = wx.BoxSizer(wx.HORIZONTAL)

        modulebox.Add(self.ConfigModuleTitle,0,wx.ALL, 2)
        modulebox.Add(self.ConfigModule, 0, wx.ALL, 2)

        modebox.Add(self.ConfigModeTitle, 0, wx.ALL, 2)
        modebox.Add(self.ConfigMode, 0, wx.ALL, 2)

        sizer.Add((5,10),0)
        sizer.Add(modulebox,0,wx.ALIGN_CENTER|wx.TOP,10)
        sizer.Add(modebox,0,wx.ALIGN_CENTER|wx.TOP,10)
        sizer.Add(self.WidgetsPan,0,wx.ALL,20)
        sizer.Add(ButPan,0,wx.ALIGN_CENTER | wx.TOP, 10)
        self.MasterPan.SetSizer(sizer)

        self.CurrentDisplay = None
        self.CurrentBeacon = None
        self.Hide()

    # Use to disable the widgets in the settings panel
    def disableSettings(self):
        for widget in self.WidgetsPan.GetChildren():
            widget.Enable(False)


    # Function to display the data for the Settings
    def Display(self,beacondata):

        print "Setting Display"
        print "********************"

        self.CurrentBeacon = beacondata
        self.Sensor = Sensor(beacondata, self.Parent.SerialInterface)
        self.WinParent.CommandHandler = self.Sensor

        # Here set values for the different widgets, set start/stop button label and event
        self.ConfigModule.SetLabel("%X"%beacondata.ID)
        if beacondata.State == 1:
            self.ConfigMode.SetLabel("Idle")
            self.but_start.SetLabel("Start")
            self.but_start.Bind(wx.EVT_BUTTON, self.but_start_evt)
        elif beacondata.State == 2:
            self.ConfigMode.SetLabel("Measuring")
            self.but_start.SetLabel("Stop")
            self.but_start.Bind(wx.EVT_BUTTON, self.but_stop_evt)
        elif beacondata.State == 3:
            self.ConfigMode.SetLabel("Downloading")
            self.but_start.SetLabel("Stop")
            self.but_start.Bind(wx.EVT_BUTTON, self.but_stop_evt)

        # Reload values based on sensor beacon
        try:
            txt = Sensor.IntervalStr[Sensor.Intervals.index(beacondata.Interval)]
            self.drop_interval.widget.SetValue(txt)
        except ValueError:
            txt = Sensor.IntervalStr[2]
            self.drop_interval.widget.SetValue(txt)


        self.Refresh()
        self.CenterOnScreen()
        self.Show()
        self.SetFocus()



    # Function that builds Buttons for the Settings Panel
    def BuildButtons(self,panel):

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        but_blink = wx.Button(panel, wx.ID_ANY, "Blink LED", size=(100, 40))
        but_blink.Bind(wx.EVT_BUTTON, self.blink_evt)
        self.but_start = wx.Button(panel,wx.ID_ANY,"Start",size=(100,40))
        self.but_start.Bind(wx.EVT_BUTTON,self.but_start_evt)
        but_cancel = wx.Button(panel,wx.ID_ANY,"Cancel",size=(100,40))
        but_cancel.Bind(wx.EVT_BUTTON,self.OnClose)

        sizer.Add(but_blink, 0, wx.ALL, 10)
        sizer.Add(self.but_start, 0, wx.ALL, 10)
        sizer.Add(but_cancel,0,wx.ALL,10)


        panel.SetSizer(sizer)

    # Here initialize the buttons actions
    def but_start_evt(self,e):

        interval = Sensor.Intervals[self.drop_interval.widget.GetCurrentSelection()]
        #mode = Sensor.Modes[self.drop_mode.widget.GetCurrentSelection()]
        mode = 0
        samples = self.samples.GetValue()
        now = int(time.time())
        settings = bytearray([interval & 0xFF, (interval >> 8) & 0xFF, mode, samples & 0xFF, (samples >> 8) & 0xFF, (samples >> 16) & 0xFF, (samples >> 24) & 0xFF, now & 0xFF, now >> 8 & 0xFF, now >> 16 & 0xFF, now >> 24 & 0xFF])
        self.SensorDlg.Execute(self.Sensor, MsgCodes.Command.MEASURE, settings)
        self.Close()

    def but_stop_evt(self, e):
        self.SensorDlg.Execute(self.Sensor, MsgCodes.Command.STOP, [])
        self.Close()

    def blink_evt(self, e):
        self.SensorDlg.Execute(self.Sensor, MsgCodes.Command.BLINK, [])
        self.Close()


    def SettingTimeout(self):
        self.WinParent.Show()
        self.Show()
        self.WinParent.CommandHandler.Finished()
        wx.MessageBox("Could not update settings of the module.  Please check it is in range","Error",wx.ICON_ERROR)

    # Building widgets for the Settings Page
    def BuildWidgetList(self,panel):

        textwidth = 100
        widgetwidth = 100
        unitwidth = 50
        pad = 10

        self.drop_interval = WidgetWithText(panel, widget=wx.ComboBox,
                                        opts={'choices':["500 ms", "1s", "10s", "30s", "1 min", "2 min", "5 min", "15 min", "30 min", "1 hour"],
                                        'size':(widgetwidth, -1),'style':wx.CB_READONLY, 'value':"1s"},
                                        pre_text="Measure Interval", pre_text_size=(textwidth,-1), post_text="", post_text_size=(unitwidth,-1), pad=pad)


        # self.drop_mode = WidgetWithText(panel, widget=wx.ComboBox,
        #                                 opts={'choices':["Normal", "Event"],
        #                                 'size':(widgetwidth, -1),'style':wx.CB_READONLY, 'value':'Normal'},
        #                                 pre_text="Measure Mode", pre_text_size=(textwidth,-1), post_text="", post_text_size=(unitwidth,-1), pad=pad)

        # This needs to be only number
        self.samples = WidgetWithText(panel, widget=wx.SpinCtrl,
                                        opts={'initial':10, 'min':0, 'max': (2000000 / 12),'size':(widgetwidth, -1)},
                                        pre_text="Measure Samples", pre_text_size=(textwidth, -1), post_text="",
                                        post_text_size=(unitwidth, -1), pad=pad)

        # self.lblPower = WidgetWithText(panel, widget=wx.StaticText,
        #                                opts={'size':(widgetwidth, -1)},
        #                                pre_text='Battery Use: ', pre_text_size=(textwidth, -1),
        #                                post_text="", post_text_size=(unitwidth, -1), pad=pad)

        # Make the checkboxes
        # self.sensortitle = wx.StaticText(parent=panel, label="Sensors:", style=wx.ST_NO_AUTORESIZE)
        # self.temp_checkbox = wx.CheckBox(parent=panel, label = 'Temperature')
        # self.humid_checkbox = wx.CheckBox(parent=panel, label='Humidity')
        # self.light_checkbox = wx.CheckBox(parent=panel, label='Light')
        # self.acc_checkbox = wx.CheckBox(parent=panel, label='Acceleration')

        vpad = 5

        sizer = wx.BoxSizer(wx.VERTICAL)
        # checksizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        # checksizer.AddSpacer((20,0))
        # checksizer.Add(self.temp_checkbox, 0, wx.ALL, 2)
        # checksizer.Add(self.humid_checkbox, 0, wx.ALL, 2)
        # checksizer.Add(self.light_checkbox, 0, wx.ALL, 2)
        # checksizer.Add(self.acc_checkbox, 0, wx.ALL, 2)



        sizer.AddSpacer((0,15))
        sizer.Add(self.drop_interval, 0, wx.TOP, vpad)
        # sizer.Add(self.drop_mode, 0, wx.TOP, vpad)
        sizer.Add(self.samples,0,wx.TOP,vpad)
        # sizer.Add(self.sensortitle,0,wx.TOP,2)
        # sizer.Add(checksizer,0,wx.TOP,2)
        #sizer.Add(self.lblPower, 0, wx.TOP, 2*vpad)

        panel.SetSizer(sizer)

    def OnClose(self,e):
        self.Hide()
        self.WinParent.Show()


# This here creates the widgets for the Settings Panel
class WidgetWithText(wx.Panel):

    def __init__(self,parent,widget,**kwargs):

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        maxy = -1
        nextpos = 0

        self.pre_text = None
        self.post_text = None
        pad = kwargs.get('pad',0)

        if('pre_text' in kwargs):
            self.pre_text = wx.StaticText(parent=self,id=wx.ID_ANY,label=kwargs['pre_text'],size=kwargs.get('pre_text_size',(-1,-1)),style=wx.ST_NO_AUTORESIZE,pos=(nextpos,0))
            width,height = self.pre_text.GetSize()
            maxy = height if height>maxy else maxy
            nextpos+=width+pad

        opts = kwargs.get('opts',{})
        opts['parent']=self
        opts['id']=wx.ID_ANY
        opts['pos']=(nextpos,0)
        self.widget = widget(**opts)
        width,height = self.widget.GetSize()
        maxy = height if height > maxy else maxy
        nextpos += width + pad

        if('post_text' in kwargs):
            self.post_text = wx.StaticText(parent=self,id=wx.ID_ANY,label=kwargs['post_text'],size=kwargs.get('post_text_size',(-1,-1)),style=wx.ST_NO_AUTORESIZE,pos=(nextpos,0))
            width,height = self.post_text.GetSize()
            maxy = height if height>maxy else maxy
            nextpos+=width

        if('size' in kwargs):
            self.SetSize(kwargs['size'])
        else:
            self.SetSize((nextpos,maxy))

        self.Refresh()

    def GetValue(self):
        return self.widget.GetValue()