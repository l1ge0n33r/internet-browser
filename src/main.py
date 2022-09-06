import sys
import os
import glob
import bs4
import requests
from datetime import *
from PyQt5 import QtWidgets
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore
from PyQt5 import QtNetwork
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

#TODO:
# 
#
#
#
# #

#LOW PRIORITY:
#
#   -make videos play in fullscreen
#   -redraw gui #self.setWindowFlags(QtCore.Qt.Window |QtCore.Qt.CustomizeWindowHint)
#   -add ability to make own webapps(adblock, video downloader, etc.)
#   -move stylesheets to separate file
#   -make icon shown in taskbar
#   -add different color themes
#   -add posibility to change themes
# #


#DONE:
# 
#   -new tab button
#   -close tab button
#   
#  
#   - make webengineviews in seperate array
#   -make add from history
#   -fix ghost site bug
#   -make about to quit handler
#   -make search history 
#   -change app icon
#   -url update
#   -tab update
#   -default searcher as duckduckgo 
#   -add shortcuts to buttons
# 
# #

defaultSearchSite = "https://duckduckgo.com"
historyPath = "history"
historyDirs = glob.glob(historyPath+'/*/*.txt')
cachePath = "cache"

class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(150,110,200,600)
        layout = QGridLayout()
        self.setWindowTitle("History")
        self.setWindowIcon(QIcon(os.path.join('config/images','ouroboros.ico')))
        self.setWindowFlags(QtCore.Qt.Window |QtCore.Qt.CustomizeWindowHint |QtCore.Qt.WindowTitleHint |QtCore.Qt.WindowCloseButtonHint |QtCore.Qt.WindowStaysOnTopHint)
        self.menu = QMenu()
        self.hopen = QAction("Open")
        self.menu.addAction(self.hopen)
        self.hdelete = QAction("Delete")
        self.menu.addAction(self.hdelete)
        self.setLayout(layout)
        self.listwidget = QListWidget()
        self.listwidget.installEventFilter(self)
        layout.addWidget(self.listwidget)
        self.sites = list()

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.listwidget:
            if self.menu.exec_(event.globalPos()):
                item= source.itemAt(event.pos())
            return True
        return super().eventFilter(source,event)
        
    def addSite(self, title,url):
        self.sites = url
        self.listwidget.clear()
        for t in title:
            self.listwidget.addItem(t)

class Browser(QMainWindow):

    def __init__(self,*args,**kwargs):
        super(Browser, self).__init__(*args, **kwargs)
        self.tabs = QTabWidget()
        self.webviews = list()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tabs.currentChanged.connect(self.currentTabChanged)
        self.setCentralWidget(self.tabs)
        self.setWindowIcon(QIcon(os.path.join('config/images','ouroboros.ico')))
        
        self.exitDialog = QDialog()
        self.exitDialog.setWindowIcon(QIcon(os.path.join('config/images','ouroboros.ico')))
        self.exitDialog.setWindowTitle("Exit")
        self.exitDialog.setGeometry(500,400, 200,100)
        self.labelExitDialog = QLabel("Do you want to save history?",self.exitDialog)
        self.labelExitDialog.move(30,30)
        self.yesExitDialog = QPushButton("Yes",self.exitDialog)
        self.yesExitDialog.move(20,55)
        self.yesExitDialog.clicked.connect(lambda: self.ybtnclck())
        self.noExitDialog = QPushButton("No",self.exitDialog)
        self.noExitDialog.move(100,55)
        self.noExitDialog.clicked.connect(lambda: self.nbtnclck())

        self.hw = HistoryWindow()
        
        self.tabs.setStyleSheet("""
            QTabBar {
                
                background: #c2c2c2;
                margin: 30px;          
            }
            QTabBar::tab {
                background: #c2c2c2;
                color: #3b3b3b;
                width:200px;
                height: 30px;
                padding-left:10px;
                text-align:left;
                border: 1px solid #a3a0a3;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom-left-radius: -4px;
                border-bottom-right-radius: -4px;
               
            } 
            QTabBar::tab:selected {
                background-color:  #F1F1F1;
                color: #000000;
                border: 1px solid #a3a0a3;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom-left-radius: -4px;
                border-bottom-right-radius: -4px;
                
                
            }
            QTabBar::close-button {
                
                image: url('config/images/close.png');
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                image: url('config/images/close-hover.png');
            }
            QTabBar::tab QLable {
                background-color: #23272a;
                font-size: 22px;
                padding-left: 3px;
                color: white;
            }
           
        """)

        navTab = QToolBar("Navigation")
        navTab.setIconSize(QSize(20,20))
        navTab.setFloatable(False)
        navTab.setMovable(False)
        self.addToolBar(navTab)
        navTab.setStyleSheet("""
        QToolButton
        {
            border: 2px;
            padding: 1px, 4px;
            background: transparent;
        }
        QToolButton:hover
        {
            border:1px;
            background:rgba(100,100,100,20)
        }
        QToolButton:selected
        {
            background: #a8a8a8
        }
        QToolButton:pressed
        {
            background:#888
        }
        
        """)

        backButton = QAction(QIcon(os.path.join('config/images', 'arrow-180.png')), "Back", self)
        backButton.setStatusTip("Previous page")
        backButton.triggered.connect(lambda: self.tabs.currentWidget().back())
        backButton.setShortcut(QKeySequence("Ctrl+Z"))
        navTab.addAction(backButton)

        forwardButton = QAction(QIcon(os.path.join('config/images', 'arrow-000.png')), "Forward", self)
        forwardButton.setStatusTip("Next page")
        forwardButton.triggered.connect(lambda: self.tabs.currentWidget().forward())
        forwardButton.setShortcut(QKeySequence("Ctrl+Y"))
        navTab.addAction(forwardButton)

        reloadButton = QAction(QIcon(os.path.join('config/images', 'arrow-circle-315.png')), "Reload", self)
        reloadButton.setStatusTip("Reload page")
        reloadButton.triggered.connect(lambda: self.tabs.currentWidget().reload())
        reloadButton.setShortcut(QKeySequence('Ctrl+R'))
        reloadButton.setShortcut(QKeySequence('F5'))
        navTab.addAction(reloadButton)
        
        addNewTab = QAction(QIcon(os.path.join('config/images', 'ui-tab--plus.png')), "New tab", self)
        addNewTab.setToolTip("Open new tab")
        addNewTab.triggered.connect(lambda: self.newTab())
        addNewTab.setShortcut(QKeySequence('Ctrl+T'))
        navTab.addAction(addNewTab)

        openHistory = QAction(QIcon(os.path.join('config/images','clock.ico')),'History',self)
        openHistory.setToolTip("Open history")
        openHistory.triggered.connect(lambda: self.showHistory())
        openHistory.setShortcut(QKeySequence('Ctrl+H'))
        navTab.addAction(openHistory)

        closeTabShortcut = QShortcut(QKeySequence("Ctrl+W"), self,self.closeTab)  
        

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navUrl)
        navTab.addWidget(self.urlbar)

        self.urlbar.setStyleSheet("""
        border: 1px;
        border-radius:10px;
        padding: 3;
        background: #fff;
        selection-background-color: darkgray;
        left: 5px;
        right: 13px;
        font:12px/14px sans-serif        
        """)

        self.newTab()
        
        self.tabs.currentWidget().urlChanged.connect(self.currentTabChanged)
        self.tabs.currentWidget().loadFinished.connect(self.currentTabChanged)        

        self.show()        

    def newTab(self, qurl = None, label = None):

        if label is None:
            label = "Blank"
        if qurl is None:
            qurl = defaultSearchSite

        tab = QWebEngineView()
        #tab.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        
        tab.setUrl(QUrl(qurl))
        

        self.webviews.append(tab)

        i = self.tabs.addTab(tab, label)

        self.tabs.setCurrentIndex(i)

        


        self.updateIcon() 
        tab.urlChanged.connect(lambda qurl, browser=tab:
                                    self.updateUrl(qurl, browser))
                                    
        tab.loadFinished.connect(lambda _, i=i, tab=tab:
                                    self.tabs.setTabText(i, tab.page().title()))

    def _setIconFromReply(self, reply):
        p = QPixmap()
        p.loadFromData(reply.readAll(), format="ico")
        self.tabs.setTabIcon(self.tabs.currentIndex(),QIcon(p))

    def navUrl(self):
        qurl = QUrl(self.urlbar.text())
        if qurl.scheme() == '':
            qurl.setScheme('http')
        rqurl = qurl.toString()
        rnewqurl = rqurl[:5]+"//"+rqurl[5:]
        print(rnewqurl)
        newqurl = QUrl(rnewqurl)
        print(newqurl.toString())
        self.tabs.currentWidget().setUrl(newqurl)

    def closeTab(self, i=None):
        if i is None:
            i = self.tabs.currentIndex()
        if self.tabs.count()<2:
            self.hw.destroy()
            closeHandle(self)
            sys.exit()
            return
        self.updateHistory(self.tabs.currentWidget())
        self.webviews[i].close()
        self.webviews.pop(i)
        self.tabs.removeTab(i)

    def updateUrl(self, url, tab = None):
        if tab != self.tabs.currentWidget():
            return
        
        self.urlbar.setText(url.toString())
        self.urlbar.setCursorPosition(999)

    def currentTabChanged(self, i):
        qurl = self.tabs.currentWidget().url()
        self.updateTitle(self.tabs.currentWidget())
        self.updateUrl(qurl, self.tabs.currentWidget())
        if len(self.tabs.currentWidget().page().title()) > 24 :
            self.tabs.setTabText(self.tabs.currentIndex(), self.tabs.currentWidget().page().title()[:26]+"...")
        else :
            self.tabs.setTabText(self.tabs.currentIndex(), self.tabs.currentWidget().page().title())
        self.updateIcon()
        self.updateHistory(self.tabs.currentWidget())

    def updateTitle(self, tab):
        if tab != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        #print(title)
        self.setWindowTitle("%s Orobo"%title)
    
    def updateIcon(self):
        pUrl = self.findIco(self.tabs.currentWidget().url())

        if pUrl is False:
            return
            
        manager = QtNetwork.QNetworkAccessManager(self)
        manager.finished.connect(self._setIconFromReply)
        manager.get(QtNetwork.QNetworkRequest(pUrl))
        # load icon with ico parsed from page code

    def findIco(self,url):
        picUrl = QUrl()
        if isinstance(url,QUrl):
            url = url.toString()
        page = requests.get(url)
        

        soup = bs4.BeautifulSoup(page.text,features="html.parser")

        a = soup.find('link', type='image/x-icon')
        if not a['href'].startswith('http'):
            picUrl = QUrl(url+a['href'])
        else:
            picUrl = QUrl(a['href'])
        return picUrl

        #finds icon with beautiful soup 
        #returns found icon

    def updateHistory(self, tab = None):
        if tab != self.tabs.currentWidget():
            return
        if historyDirs.__len__ == 0:
            return
        self.addToHistory()

    def addToHistory(self):
        currentDate = str(date.today())
        pathCD = os.path.join(historyPath,currentDate)
        if not os.path.isdir(pathCD):
            os.makedirs(pathCD, 0o755)
   
        with open(os.path.join(pathCD,'%s.txt'%str(datetime.now().time()).replace(' ','').replace(':','.')), 'w+') as fw:
            tabIndex = self.tabs.currentIndex()
            tabName = self.tabs.tabText(tabIndex)
            tabUrl =  str(self.tabs.currentWidget().page().url())[19:-2]
            fw.write('%s\n%s\n%s'%(tabIndex,tabName,tabUrl))
        fw.close()

    def addFromHistory(self):
        url = self.hw.sites[self.hw.listwidget.row(self.hw.listwidget.currentItem())]
        self.newTab(url)
        
    def deleteHistory(self):
        pt = glob.glob(historyPath+"/*/*.txt")
        ppt = glob.glob(historyPath+"/*")
        for f in pt:
            print("Deleted: "+f)
            os.remove(f)
        for p in ppt:
            print("Deleted: "+p)
            os.rmdir(p)

    def deleteFromHistory(self):
        i = self.hw.listwidget.row(self.hw.listwidget.currentItem())
        os.remove(historyDirs[i])
        print("Deleted: "+historyDirs[i])
        historyDirs.pop(i)

    def showHistory(self):
        self.hw.listwidget.clear()
        self.hw.show()
        
        if self.hw.listwidget.count() != 0:
            return
        self.hw.hopen.triggered.connect(lambda : self.addFromHistory())
        self.hw.hdelete.triggered.connect(lambda: self.deleteFromHistory())
        historyDirs = glob.glob(historyPath+'/*/*.txt')
        historyDirs = historyDirs[::-1]
        historyData = dict()

        for p in historyDirs:
            with open(p,'r') as fp:
                historyData[p] = str(p).replace('.txt','')[-26:] + fp.read()
            fp.close()
        
        lurl = list()
        ltitle = list()
        for h in historyDirs:
            if  str(historyData[h]).split('\n')[1] != "":
                title = str(historyData[h]).split('\n')[1]
                url = str(historyData[h]).split('\n')[2]
                ltitle.append(title)
                lurl.append(url)  
        self.hw.addSite(ltitle,lurl)
    
    def nbtnclck(self):
        self.deleteHistory()
        sys.exit()

    def ybtnclck(self):
        sys.exit()

    def downloadIcon(self):
        i = self.tabs.currentIndex()

            
        
def closeHandle(object):
    object.exitDialog.exec_()
   
if __name__ =="__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.showMaximized()
    app.aboutToQuit.connect(lambda obj = window: closeHandle(obj))
    sys.exit(app.exec_())    