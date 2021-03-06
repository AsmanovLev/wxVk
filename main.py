from re import A, T
import wx
import vk_api
import webbrowser
import sqlite3
from threading import Thread

from .locales import locale


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
    

    sqlite_create_table_query = '''CREATE TABLE USERINFO (
                                id INTEGER PRIMARY KEY,
                                username TEXT NOT NULL);'''
    
    DBcursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='USERINFO' ''')
    if DBcursor.fetchone()[0]==1:
        print('Table found!')
    else:
        print('Table not found! Creating new table.')
        DBcursor.execute(sqlite_create_table_query)
        conn.commit()
        print("Table USERINFO has been created")
def getUserInfo(userid):
    raw = DBcursor.execute(''' SELECT username FROM USERINFO WHERE id = {}; '''.format(userid)).fetchall()
    return raw
def setUserInfo(id,username):
    id = str(id)
    username = str(username)
    DBcursor.execute(''' INSERT INTO 'USERINFO' (id, username) VALUES ('{}', '{}') ON CONFLICT(id) DO UPDATE SET username='{}' '''.format(id, username, username))
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
                if str(error_msg) == "Bad password":
                    statusbar.SetStatusText(locale['badpass'])
                else:
                    statusbar.SetStatusText(locale['error'])
                #print(error_msg)
                authStatus = False
            
            if authStatus == True:
                mainwindow = MainWindow(None, -1, 'wx.SplitterWindow')
                mainwindow.vk_session = vk_session
                self.Close()
                mainwindow.Start()
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
        vk = self.vk_session.get_api()
        def getName(peerid):
            raw = getUserInfo(peerid)
            ischat = False
            if len(raw) == 0:
                raw = None
                if peerid < 2000000000:
                    raw = vk.users.get(user_ids=peerid)[0]
                    raw = raw['first_name']+" "+raw['last_name']
                else:
                    raw = vk.messages.getChat(chat_id=peerid-2000000000)['title'] + " ????"
                setUserInfo(peerid,raw)
                conn.commit()
            else:
                raw = raw[0]
            if peerid >= 2000000000:
                ischat = True
            return raw, ischat

        def getMessengerNames(conversations): # Left listbox
            ischats = []
            names = []
            usernames = []
            chatnames = []
            groupnames = []
            groupids = []
            userids = []
            ids=[]
            for conversation in conversations['items']:
                self.statusbar.SetStatusText(locale['loading'] + " {}/{}".format(conversations['items'].index(conversation),len(conversations['items']))) 
                if conversation['conversation']['peer']['type'] == 'chat':
                    ischats.append(1)
                    chatnames.append(conversation['conversation']['chat_settings']['title'])
                    ids.append(conversation['conversation']['peer']['id'])
                elif conversation['conversation']['peer']['type'] == 'user':
                    ischats.append(0)
                    userids.append(conversation['conversation']['peer']['id'])
                    ids.append(conversation['conversation']['peer']['id'])
                elif conversation['conversation']['peer']['type'] == 'group':
                    ischats.append(2)
                    groupids.append(-conversation['conversation']['peer']['id'])
                    ids.append(conversation['conversation']['peer']['id'])
            for userdata in vk.users.get(user_ids=userids):
                usernames.append(userdata['first_name']+" "+userdata['last_name'])
            for groupdata in vk.groups.getById(group_ids=groupids):
                groupnames.append(groupdata['name'])
            for ischat in ischats:
                if ischat == 1:
                    names.append(chatnames.pop(0))
                elif ischat == 0:
                    names.append(usernames.pop(0))
                elif ischat == 2:
                    names.append(groupnames.pop(0))
            return [names,ids]
        def getUsernamesInChat(uids):
            names = []
            usernames = []
            groupnames = []
            groupids = []
            userids = []
            ids=[]
            for uid in uids:
                self.statusbar.SetStatusText(locale['loading']+" "+locale['messages'] + " {}/{}".format(uids.index(uid),len(uids))) 
                if uid > 0 and userids.count(uid) == 0:
                    userids.append(uid)
                elif uid < 0 and groupids.count(-uid) == 0:
                    groupids.append(-uid)
            
            if len(userids) != 0:
                for userdata in vk.users.get(user_ids=userids):
                    usernames.append(userdata['first_name']+" "+userdata['last_name'])
            
            if len(groupids) != 0:
                for groupdata in vk.groups.getById(group_ids=groupids):
                    groupnames.append(groupdata['name'])
                for groupid in groupids:
                    ids.append(-groupid)
                names.extend(groupnames)

            ids.extend(userids)
            names.extend(usernames)
            return dict(zip(ids, names))

        def getMessages(id):
            messages=[]
            uids = [] 
            text = []
            self.statusbar.SetStatusText(locale['loading']+" "+locale['messages'])
            messagesHistory = vk.messages.getHistory(count=200,peer_id=id, fields=[])
            for message in messagesHistory['items']:
                messages.append(message['text'])
                uids.append(message['from_id'])
            usernames = getUsernamesInChat(uids)
            #print("usernames = ",usernames,"\nuids = ",uids)
            for i in range(0,len(uids)):
                uids[i] = usernames[uids[i]]
            self.statusbar.SetStatusText('')
            for i in range(0,len(messages)):
                text.append(uids[i]+": "+messages[i])
            return text
        
        idbase = []
        def onSelectChat(self):
            obj = self.GetSelection()
            if messagesList.Count != 0:
                for id in range(0, messagesList.Count):
                    messagesList.Delete(0) 
            text = getMessages(idbase[obj])
            text.reverse()
            messagesList.Append(text)
            messagesList.SetSelection(messagesList.Count-1)
        
        splitter = wx.SplitterWindow(self, -1)
        splitter.SetMinimumPaneSize(50)


        panel1 = wx.Panel(splitter, wx.ID_ANY)
        panel2 = wx.Panel(splitter, wx.ID_ANY)
        
        chatsSizer = wx.BoxSizer(wx.VERTICAL)  
        chatsList = wx.ListBox(panel1,wx.ID_ANY,(0,0),(100,-1),[],wx.LB_SINGLE | wx.LB_ALWAYS_SB)
        chatsList.Bind(wx.EVT_LISTBOX, onSelectChat)
        chatsSizer.Add(chatsList, wx.ID_ANY, wx.EXPAND | wx.ALL, 2)
        panel1.SetSizer(chatsSizer)


        messagesSizer = wx.BoxSizer(wx.VERTICAL)  
        messagesList = wx.ListBox(panel2,wx.ID_ANY,(0,0),(100,-1),[],wx.LB_SINGLE | wx.LB_ALWAYS_SB)
        messagesSizer.Add(messagesList, wx.ID_ANY, wx.EXPAND | wx.ALL, 2)
        panel2.SetSizer(messagesSizer)
        
        #usernameText = wx.StaticText(panel,-1,"")
        #sizerMain = wx.FlexGridSizer(cols=1, hgap=6, vgap=6)
        #sizerGeneral = wx.BoxSizer(wx.HORIZONTAL)
        #sizerMain.AddMany([usernameText,listFrame])
        
        #sizerGeneral.Add(chatsList, wx.ID_ANY, wx.EXPAND | wx.ALL, 5)
        #sizerGeneral.Add(messagesList, wx.ID_ANY, wx.EXPAND | wx.ALL, 5)

        #panel.SetSizer(sizerGeneral)
        
        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText(locale['loading'] + "...") 
        
        splitter.SplitVertically(panel1, panel2)
        
        self.SetSize((600, 300))
        self.SetTitle('wxVK')
        self.Centre()
        self.Show()

        profileInfo=vk.account.getProfileInfo()
        #usernameText.SetLabel(profileInfo['first_name']+" "+profileInfo['last_name'])
        conversations = vk.messages.getConversations(count=0)
        conversationCount = conversations['count']
        #statusbar.SetStatusText(locale['loading'] + " 0/{}".format(str(conversationCount))) 
        chatsCounter = 0
        while chatsCounter < conversationCount:
            tempconv = vk.messages.getConversations(count=200,offset=chatsCounter)['items']
            for i in tempconv:
                self.statusbar.SetStatusText(locale['loading'] + " {}/{}".format(str(tempconv.index(i)),str(conversationCount))) 
                conversations['items'].append(i)
            chatsCounter = chatsCounter + 200
        namebase, idbase = getMessengerNames(conversations)
        self.statusbar.SetStatusText("")
        chatsList.Append(namebase)

    
    def OnQuit(self, e):
        self.Close()

def main():

    app = wx.App()
    loginwindow = LoginWindow(None,style=wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
    loginwindow.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()