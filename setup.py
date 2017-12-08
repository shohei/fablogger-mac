from distutils.core import setup
import py2exe
import glob

#,



setup(
    name="SFC Logger",
    console=['SFCLogger.py'],
    options={
             'py2exe': {
                        'packages' : ['pytz'],"dll_excludes": ["MSVCP90.dll","libgdk_pixbuf-2.0-0.dll","libgobject-2.0-0.dll",'libgdk-win32-2.0-0.dll'],
                       }
            },
    windows=[{'script':'SFCLogger.py','icon_resources':[(1,'resources/App.ico')]}],

)
