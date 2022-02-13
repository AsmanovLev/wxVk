import wx
import vk_api
import webbrowser
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
    "enter_credentials" : "Enter your credentials"
}
locale = {}
if language == "en_US.UTF-8":
    locale = locale_en_US_UTF_8

global login, password, token 
login = ""
password = ""
token_page = "https://vkhost.github.io/"
token = ""
def auth_handler():
    key = input("Введите код для двухфакторной аутификации: ")
    remember_device = True
    return key, remember_device


class LoginWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(LoginWindow, self).__init__(*args, **kwargs)
        self.InitUI()
    def InitUI(self):
        panel = wx.Panel(self, wx.ID_ANY)
        LoginLabel = wx.StaticText(panel, -1, locale['login']+":")
        LoginText = wx.TextCtrl(panel, -1, "+7", size=(175, -1))
        LoginText.SetInsertionPoint(0)
        
        PasswordLabel = wx.StaticText(panel, -1, locale['password']+":")
        PasswordText = wx.TextCtrl(panel, -1, "", size=(175, -1),style=wx.TE_PASSWORD)
        PasswordText.SetInsertionPoint(0)
        
        TokenLabel = wx.StaticText(panel, -1, locale['token']+":")
        TokenText = wx.TextCtrl(panel, -1, "", size=(175, -1),style=wx.TE_PASSWORD)
        TokenText.SetInsertionPoint(0)
        
        statusbar = self.CreateStatusBar(1)
        statusbar.SetStatusText(locale['enter_credentials']) 
        
        def onButton(self):
            login = LoginText.GetLineText(0)
            password = PasswordText.GetLineText(0)
            token = TokenText.GetLineText(0)
            print(login, password, token)
            statusbar.SetStatusText("Trying to login...")

        def gettoken(self):
            webbrowser.open(token_page)
        gettokenButton = wx.Button(panel, wx.ID_ANY, locale['gettoken'], (10, 10))
        gettokenButton.Bind(wx.EVT_BUTTON, gettoken)
        button = wx.Button(panel, wx.ID_ANY, locale['login'], (10, 10))
        button.Bind(wx.EVT_BUTTON, onButton)
        
        sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        sizer.AddMany([ LoginLabel, LoginText,
                        PasswordLabel, PasswordText,
                        TokenLabel, TokenText,
                        button, gettokenButton])
        panel.SetSizer(sizer) 
        self.Fit()
        self.SetSize((280, 180))
        self.SetTitle("wxVk "+locale['login'])
        self.Centre()

    def OnQuit(self, e):
        self.Close()


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        listFrame = wx.ListBox(self,wx.ID_ANY,(0,0),(100,-1),['test','list'],wx.LB_SINGLE)
        self.SetSize((600, 300))
        self.SetTitle('wxVK')
        self.Centre()

    def OnQuit(self, e):
        self.Close()

def main():

    app = wx.App()
    loginwindow = LoginWindow(None,style=wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
    loginwindow.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()