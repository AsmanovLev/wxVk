import wx
import os
from random import randint
language = os.getenv('LANG')
del os
print(language)
locale_en_US_UTF_8 = {
    "quit": "Quit",
}
locale = {}
if language == "en_US.UTF-8":
    locale = locale_en_US_UTF_8
class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.InitUI()

    def InitUI(self):
        frame = []
        def onButton(event):
            frame.append(wx.Frame(None, -1, 'ITS Just A TEST'))
            n = len(frame) - 1
            frame[n].SetSize(200, 0, 200, 200)
            panel = wx.Panel(frame[n], wx.ID_ANY)
            frame[n].Show()
        menubar = wx.MenuBar()
        panel = wx.Panel(self, wx.ID_ANY)
        button = wx.Button(panel, wx.ID_ANY, 'Test', (10, 10))
        button.Bind(wx.EVT_BUTTON, onButton)
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, locale['quit'], 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

        self.SetSize((300, 200))
        self.SetTitle('Simple menu')
        self.Centre()

    def OnQuit(self, e):
        self.Close()

def main():

    app = wx.App()
    mainwindow = MainWindow(None)
    mainwindow.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()