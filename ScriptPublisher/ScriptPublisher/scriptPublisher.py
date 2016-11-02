# coding:utf-8

try:
    import PySide
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance
    PySide_Version = PySide.__version__
except:
    import PySide2
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
    PySide_Version = PySide2.__version__
    
import platform
import webbrowser
import os
import shutil
import py_compile

import maya.OpenMayaUI as OpenMayaUI



__version__ = '1.2.4'

def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QMainWindow)

def mayaToQtObject( inMayaUI ):
    ptr = OpenMayaUI.MQtUtil.findControl( inMayaUI )
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findLayout( inMayaUI )
    if ptr is None:
        ptr= OpenMayaUI.MQtUtil.findMenuItem( inMayaUI )
    if ptr is not None:
        return wrapInstance( long( ptr ), QWidget )

class ScriptPublisher(QMainWindow):
    
    def __init__(self, parent=None):
        super(ScriptPublisher, self).__init__(parent)
        
        self.rootPath  = ScriptPublisher.getRootPath()
        self.imagePath = ScriptPublisher.getImagePath()
        
        self.result = False
        self.isDeletePy = False
        
        self.initUi()
        
    def initUi(self):
        self.setWindowTitle('Alfred Script Publisher')
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayoyt = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayoyt)
        
        self.folderGroupBox = QGroupBox('Script Folder')
        folderLayout = QHBoxLayout()
        self.folderGroupBox.setLayout(folderLayout)
        self.folderLineEdit = QLineEdit()
        self.folderButton   = QPushButton()
        folderImage = QPixmap(os.path.join(self.imagePath,'folder.png'))
        folderIcon  = QIcon(folderImage)
        self.folderButton.setIcon(folderIcon)
        folderLayout.addWidget(self.folderLineEdit)
        folderLayout.addWidget(self.folderButton)
        
        self.titleGroupBox = QGroupBox('Title')
        titleLayout = QHBoxLayout()
        self.titleGroupBox.setLayout(titleLayout)
        self.titleLineEdit = QLineEdit()
        titleLayout.addWidget(self.titleLineEdit)
                
        self.classifyGroupBox = QGroupBox('Classify')
        classifyLayout = QGridLayout()
        self.classifyGroupBox.setLayout(classifyLayout)
        self.commonCheckBox   = QCheckBox('Common')
        self.modelCheckBox    = QCheckBox('Model')
        self.rigCheckBox      = QCheckBox('Rig')
        self.aniCheckBox      = QCheckBox('Animation')
        self.fxCheckBox       = QCheckBox('FX')
        self.lightCheckBox    = QCheckBox('Light')
        self.rndCheckBox      = QCheckBox('RnD')
        classifyLayout.addWidget(self.commonCheckBox, 0,0)
        classifyLayout.addWidget(self.modelCheckBox,  0,1)
        classifyLayout.addWidget(self.rigCheckBox,    0,2)
        classifyLayout.addWidget(self.aniCheckBox,    1,0)
        classifyLayout.addWidget(self.fxCheckBox,     1,1)
        classifyLayout.addWidget(self.lightCheckBox,  1,2)
        classifyLayout.addWidget(self.rndCheckBox,    2,0)
        self.classifyGroup = QButtonGroup()
        #self.classifyGroup.setExclusive(False)
        self.classifyGroup.addButton(self.commonCheckBox)
        self.classifyGroup.addButton(self.modelCheckBox)
        self.classifyGroup.addButton(self.commonCheckBox)
        self.classifyGroup.addButton(self.rigCheckBox)
        self.classifyGroup.addButton(self.aniCheckBox)
        self.classifyGroup.addButton(self.fxCheckBox)
        self.classifyGroup.addButton(self.lightCheckBox)
        self.classifyGroup.addButton(self.rndCheckBox)
        
        self.commandGroupBox = QGroupBox('Execute Command')
        commandLayout = QHBoxLayout()
        self.commandGroupBox.setLayout(commandLayout)
        self.commandText = QTextEdit()
        commandLayout.addWidget(self.commandText)
        
        publishButtonLayout = QHBoxLayout()
        self.publishButton = QPushButton('Publish')
        publishImage = QPixmap(os.path.join(self.imagePath,'upload.png'))
        publishIcon  = QIcon(publishImage)
        self.publishButton.setIcon(publishIcon)
        publishButtonLayout.addStretch()
        publishButtonLayout.addWidget(self.publishButton)
        
        self.mainLayoyt.addWidget(self.folderGroupBox)
        self.mainLayoyt.addWidget(self.titleGroupBox)
        self.mainLayoyt.addWidget(self.classifyGroupBox)
        self.mainLayoyt.addWidget(self.commandGroupBox)
        self.mainLayoyt.addLayout(publishButtonLayout)
        
        self.status = self.statusBar()
        
        #Set Window
        windowLogoImage = QPixmap(os.path.join(self.imagePath,'scriptPublisher.png'))
        windowLogoIcon  = QIcon(windowLogoImage)
        self.setWindowIcon(windowLogoIcon)
        self.setGeometry(750,300, 300,400)
        self.setFixedSize(300,400)
        
        #Option actions
        self.optionAction = self.createAction('Delete py', icon=None, slot=self.chekDeletePy, tip=None, checkable=True)
        #Option menu
        operationMenu = self.menuBar().addMenu('Option')
        self.addActions(operationMenu, [self.optionAction])
        
        #Help actions
        helpAboutAction = self.createAction("&About", icon='about' ,slot=self.helpAbout)
        helpHelpAction = self.createAction("&Help", icon='help', slot=self.helpHelp, shortcut= QKeySequence.HelpContents)
        
        #Help menu
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, [helpAboutAction, helpHelpAction]) 
    
        #Connection
        self.folderButton.clicked.connect(self.findScriptFolder)
        self.publishButton.clicked.connect(self.publish)
        
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon("images/{}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            getattr(action, signal).connect(slot) 
        if checkable:
            action.setCheckable(True)
        return action   
    
    def chekDeletePy(self):
        self.isDeletePy = self.optionAction.isChecked()
    
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)   

    def helpAbout(self):
        QMessageBox.about(self, "About Alfred Script Publisher",
                u"""<b>Alfred Script Publisher</b> v {0}
                <p>Copyright &copy; 2015-16 Alfred 
                All rights reserved.
                <p>{5}
                <p>Python {1} - Qt {2} - PySide {3} on {4}""".format(
                __version__, platform.python_version(),
                qVersion(), PySide_Version,
                platform.system(), u'이 프로그램은 Python 스크립트를 Maya Menue 등록 합니다.'))

    def helpHelp(self):
        url = 'http://vimeo.com/138493877'
        webbrowser.open(url)
        
    def findScriptFolder(self):
        selectedDir = QFileDialog.getExistingDirectory()
        self.folderLineEdit.setText(selectedDir)
        
    def progressSuccess(self):
        self.status.setStyleSheet("QStatusBar{color:green;font-weight:bold;}")
        self.status.showMessage(u'완료 되었습니다.', 3000)
        
    def progressFail(self):
        self.status.setStyleSheet("QStatusBar{color:red;font-weight:bold;}")
        self.status.showMessage(u'입력 정보를 확인해 주세요.', 3000)
    
    def getInputs(self):
        scriptDir  = self.folderLineEdit.text()
        title      = self.titleLineEdit.text()
        buttons    = self.classifyGroup.buttons()
        command    = self.commandText.toPlainText()
        
        checked    = []
        for btn in buttons:
            if btn.checkState():
                checked.append(btn.text())
        
        return [scriptDir, title, checked, command]
    
    # MC
    def publish(self):
        inputs    = self.getInputs()
        scriptDir = inputs[0]
        title     = inputs[1]
        checked   = inputs[2]
        command   = inputs[3]

        if scriptDir and title and checked and command:
            scriptFolder = scriptDir.rpartition('\\')[2]
            mayaMenuToolPath = self.getConfig()[0]
            appPath = os.path.join(mayaMenuToolPath, checked[0]) 
            appPath = os.path.join(appPath, scriptFolder)
            appName = scriptFolder
            
            self.copyDirectory(scriptDir, appPath)
            self.createInit(appPath, inputs)
            self.createRun(appPath, inputs, appName)
            self.createConfig(appPath, inputs, appName)
            self.compileFiles(appPath)
            if self.isDeletePy:
                self.filterDirectory(appPath)
            
            if self.result:
                self.progressSuccess()
            else:
                self.progressFail()
        else:
            self.progressFail()
    
    def getConfig(self):
        try:
            config = []
            f = open(__file__.rpartition('\\')[0] + '/config.ini', 'r')
            lines = f.read().splitlines()
            for line in lines:
                config.append(line.partition('=')[2].lstrip())
            f.close()
            return config
        except:
            return False
    
    def copyDirectory(self, src, dest):
        try:
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            self.result = True
        # Directories are the same
        except shutil.Error as e:
            print('Directory not copied. Error: %s' % e)
            self.result = False
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('Directory not copied. Error: %s' % e)
            self.result = False
    
    def compileFiles(self, src):
        for root, dirs, files in os.walk(src):
            for f in files:
                if f.endswith('.py'):
                    py_compile.compile(os.path.join(root, f))
    
    def filterDirectory(self, src):
        for root, dirs, files in os.walk(src):
            for f in files:
                if f.endswith('.qrc') or f.endswith('.py') or f.endswith('.project') or f.endswith('.pydevproject'):
                    os.remove(os.path.join(root, f))
            for d in dirs:
                if d == '.settings' or d == 'Test':
                    shutil.rmtree(os.path.join(root, d))
    
    def createConfig(self, path, inputs, appName):
        filePath = os.path.join(path, 'config.ini')
        if os.path.exists(filePath):
            os.remove(filePath)
        fileHandle = open(filePath, 'w')
        
        classify = inputs[2][0]
        title    = inputs[1]
        language = 'python'
        config = ['CLASSIFY = {}\n'.format(classify),
                  'TITLE = {}\n'.format(title),
                  'LANGUAGE = {}\n'.format(language),
                  'COMMAND = {}\n'.format(appName+'_run')]
        fileHandle.writelines(config)
        
        fileHandle.close()
    
    def createInit(self, path, inputs):
        filePath = os.path.join(path, '__init__.py')
        if os.path.exists(filePath):
            os.remove(filePath)
        fileHandle = open(filePath, 'w')        
        fileHandle.close()
        
    def createRun(self, path, inputs, appName):
        filePath = os.path.join(path, appName +'_run.py')
        if os.path.exists(filePath):
            os.remove(filePath)
        fileHandle = open(filePath, 'w')
        
        templateCode = ['# coding:utf-8\n\n',
                  'def run():\n',
                  '\ttry:\n',
                  '\t\tfilePath = __file__\n',
                  '\t\tappPath = filePath.rpartition("\\\\")[0]\n',
                  '\texcept:\n',
                  '\t\tprint "Application`s path not exist."\n\n',
                  '\telse:\n',
                  '\t\timport sys\n',
                  '\t\tpath = appPath\n\n',
                  '\t\tif not path in sys.path:\n',
                  '\t\t\tsys.path.append(path)\n\n', 
                   ]   
        
        addCode = inputs[3].split('\n')
        index = 0
        for line in addCode:
            newLine = '\t\t{}\n'.format(line)
            addCode[index] = newLine
            index += 1
        templateCode.extend(addCode)
         
        fileHandle.writelines(templateCode)
        fileHandle.close()
        
    @staticmethod
    def getRootPath():
        return os.path.dirname(__file__)

    @staticmethod
    def getImagePath():
        return os.path.join(ScriptPublisher.getRootPath(),'images')
            
        
def main():
    global win
    try:
        win.close()
        win.deleteLater()
    except: 
        pass
    win = ScriptPublisher()
    win.show()


if __name__ == 'scriptPublisher':
    main()