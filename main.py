from re import A, T
import wx
import vk_api
import webbrowser
import sqlite3
import os
language = os.getenv('LANG')
del os


print(language)
locale_en_US_UTF_8 = {
    "quit": "Quit",
    "login": "Login",
    "password": "Password",
    "gettoken": "Get token",
    "token": "Token",
    "enter_credentials" : "Enter your credentials",
    "sumbit" : "Sumbit",
    '2fa' : "Enter 2FA code",
    "tryauth": "Trying to authorize...",
    "success" : "Success!",
    "error" : "Error: ",
    "savecreds": "Remember credentials"
}
locale = {}

if language == "en_US.UTF-8":
    locale = locale_en_US_UTF_8

token_page = "https://vkhost.github.io/"

conn = sqlite3.connect('main.db')
print("Database successfully initialized")
DBcursor = conn.cursor()

def initDB():
    sqlite_create_table_query = '''CREATE TABLE PERSONALINFO (
                                param TEXT PRIMARY KEY,
                                value TEXT NOT NULL);'''
    DBcursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='PERSONALINFO' ''')

    if DBcursor.fetchone()[0]==1:
        print('Table found!')
    else:
        print('Table not found! Creating new table.')
        DBcursor.execute(sqlite_create_table_query)
        conn.commit()
        print("Table PERSONALINFO has been created")
def getPersonalInfo():
    raw = DBcursor.execute("SELECT param, value FROM PERSONALINFO; ").fetchall()
    returnDict = {}
    for i in raw:
        returnDict[i[0]] = i[1]
    return returnDict
def setPersonalInfo(param,value):
    param = str(param)
    value = str(value)
    DBcursor.execute(''' INSERT INTO 'PERSONALINFO' (param, value) VALUES ('{}', '{}') ON CONFLICT(param) DO UPDATE SET value='{}' '''.format(param, value,value))
def deletePersonalInfo(param):
    DBcursor.execute(''' DELETE FROM PERSONALINFO WHERE param='{}' '''.format(param))
initDB()
conn.commit()
#print(getPersonalInfo()) #WARNING! IF YOUR CREDENTIALS IS SAVED, THEY WILL APPER IN CONSOLE OUTPUT
class LoginWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(LoginWindow, self).__init__(*args, **kwargs)
        self.InitUI()
    def InitUI(self):
        rememberedLogin = ""
        rememberedPassword = ""
        rememberedToken = ""
        rememberedSaveCreds = False
        SavedCredentials = getPersonalInfo()
        if 'login' in SavedCredentials.keys() and 'password' in SavedCredentials.keys() and 'usertoken' in SavedCredentials.keys():
            rememberedLogin=SavedCredentials['login']
            rememberedPassword=SavedCredentials['password']
            rememberedToken=SavedCredentials['usertoken']
            rememberedSaveCreds=True
        panel = wx.Panel(self, wx.ID_ANY)
        LoginLabel = wx.StaticText(panel, -1, locale['login']+":")
        LoginText = wx.TextCtrl(panel, -1, rememberedLogin, size=(175, -1))
        LoginText.SetInsertionPoint(0)
        
        PasswordLabel = wx.StaticText(panel, -1, locale['password']+":")
        PasswordText = wx.TextCtrl(panel, -1, rememberedPassword, size=(175, -1),style=wx.TE_PASSWORD)
        PasswordText.SetInsertionPoint(0)
        
        TokenLabel = wx.StaticText(panel, -1, locale['token']+":")
        TokenText = wx.TextCtrl(panel, -1, rememberedToken, size=(175, -1),style=wx.TE_PASSWORD)
        TokenText.SetInsertionPoint(0)

        savecreds = wx.CheckBox(panel, -1, locale['savecreds'])
        savecreds.SetValue(rememberedSaveCreds)

        statusbar = self.CreateStatusBar(1)
        statusbar.SetStatusText(locale['enter_credentials']) 
        
        def onButton(frame):
            login = LoginText.GetLineText(0)
            password = PasswordText.GetLineText(0)
            token = TokenText.GetLineText(0)
            if savecreds.GetValue():
                setPersonalInfo('login',login)
                setPersonalInfo('password',password)
                setPersonalInfo('usertoken', token)
                conn.commit()
            else:
                deletePersonalInfo('login')
                deletePersonalInfo('password')
                deletePersonalInfo('usertoken')
                conn.commit()
            statusbar.SetStatusText(locale["tryauth"])
            def auth_handler():
                key = self.twoFactor()
                remember_device = True
                return key, remember_device
            vk_session = vk_api.VkApi(
                login, password, token=token, app_id="2685278",
                auth_handler=auth_handler
            )
            authStatus = False
            try:
                vk_session.auth()
                statusbar.SetStatusText(locale['success'])
                authStatus = True    
            except vk_api.AuthError as error_msg:
                statusbar.SetStatusText(locale['error'])
                print(error_msg)
                authStatus = False
            
            if authStatus == True:
                mainwindow = MainWindow(None)
                mainwindow.vk_session = vk_session
                mainwindow.Start()
                self.Close()
        def gettoken(self):
            webbrowser.open(token_page)

        gettokenButton = wx.Button(panel, wx.ID_ANY, locale['gettoken'], (10, 10))
        gettokenButton.Bind(wx.EVT_BUTTON, gettoken)
        button = wx.Button(panel, wx.ID_ANY, locale['login'], (10, 10))
        button.Bind(wx.EVT_BUTTON, onButton)
        sizerTexts = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        sizerTexts.AddMany([ LoginLabel, LoginText,
                        PasswordLabel, PasswordText,
                        TokenLabel, TokenText])
        sizerButtons = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        sizerButtons.AddMany([button, gettokenButton])
        sizerMain = wx.FlexGridSizer(cols=1, hgap=6, vgap=6)
        sizerMain.AddMany([sizerTexts,savecreds,sizerButtons])
        panel.SetSizer(sizerMain) 
        self.SetSize((255, 200))
        self.SetTitle("wxVk "+locale['login'])
        self.Centre()
    def twoFactor(self):
            dlg = wx.TextEntryDialog(self,locale['2fa'],'',style=wx.OK)
            dlg.SetValue("")
            dlg.SetMaxLength(6)
            while len(dlg.GetValue()) < 6 or not dlg.GetValue().isdecimal():
                dlg.ShowModal()
            toReturn = dlg.GetValue()
            dlg.Destroy()
            return toReturn
    def OnQuit(self, e):
        self.Close()
    def reenable(self):
        self.Enable()
        print("done")


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.vk_session = None
    
    def Start(self):
        #print(self.vk_session.)
        panel = wx.Panel(self, wx.ID_ANY)
        listFrame = wx.ListBox(panel,wx.ID_ANY,(0,0),(100,-1),['test','list'],wx.LB_SINGLE)
        self.SetSize((600, 300))
        self.SetTitle('wxVK')
        self.Centre()
        self.Show()
    
    def OnQuit(self, e):
        self.Close()

def main():

    app = wx.App()
    loginwindow = LoginWindow(None,style=wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
    loginwindow.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()