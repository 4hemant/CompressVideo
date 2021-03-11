import os, sys, subprocess, datetime
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QGroupBox, QLineEdit, QMainWindow, QRadioButton, QSlider, QStatusBar, QTextBrowser, QLabel, QPushButton, QFileDialog, QMessageBox

fps = 30
crf = 24
sfwr = "handbrake"
filename = ""

def selectFile():
    global filename
    filename = QFileDialog.getOpenFileName()
    filename = filename[0]
    leFname.setText(filename)
    # probe the file
    probeFile(filename)

def rb24pushed():
    global fps
    fps = 24
    statusbar.clearMessage()
    statusbar.showMessage("24 fps selected")
    statusbar.show()

def rb30pushed():
    global fps
    fps = 30
    statusbar.clearMessage()
    statusbar.showMessage("30 fps selected")
    statusbar.show()

def rbhandbrakepushed():
    global sfwr
    sfwr = "handbrake"
    statusbar.clearMessage()
    statusbar.showMessage("'handbrake' selected")
    statusbar.show()

def rbffmpegpushed():
    global sfwr
    sfwr = "ffmpeg"
    statusbar.clearMessage()
    statusbar.showMessage("'ffmpeg' selected")
    statusbar.show()

def crfChanged():
    global crf
    crf=hsVQ.value()
    lblCRF.setText(str(crf))
    statusbar.showMessage(str(crf) + " CRF")

def probeFile(myfyl):
    probecmd = 'ffprobe "' + myfyl + '"'

    try:
        x = subprocess.getoutput(probecmd)
    except Exception as e:
        box = QMessageBox()
        box.setText(str("Probe Error " + e.message))
        box.setWindowTitle("ERROR")
        box.exec_()

    i = x.find("Input #0")      # locate text to drop
    if (i <= 0):
        box = QMessageBox()
        box.setText(str("No multimedia stream detected!"))
        box.setWindowTitle("ERROR")
        box.exec_()
    else:
        y = x[i:]          #drop preceeding text
        textBrowser.clear()
        textBrowser.append(y)
    return x

def compress():
    global fps
    global crf
    global filename
    global sfwr
    curname = ""
    newname = ""
    logfile = ""
    compresscmd = ""
    starttm = 0
    stoptm = 0
    deltatm = 0

    # has a file been selected
    if (len(filename) == 0):
        box = QMessageBox()
        box.setText("Must select file to compress first")
        box.setWindowTitle("ERROR")
        box.exec_()
        return

    # find name without file extension (ext)
    i=0
    i = filename.find(".")
    nameNoExt = filename[:i]

    # rename file, with "_ORIGINAL" appended
    newname = filename
    newname = newname.replace(".m", "_ORIGINAL.m")
    os.rename(filename, newname)
    box = QMessageBox()
    box.setText("Please note \n" + filename + " has been renamed to " + newname)
    box.setWindowTitle("CompressVideo") 
    box.exec_()

    # create new (compressed) & log filenames
    curname = nameNoExt + ".mp4"
    logfile = nameNoExt + ".log"

    # print run parameters & probe input video
    mylog = open(logfile, 'w')
    mylog.write("=========================================================== \n")
    mylog.write("=========================================================== \n")          
    x = "\n File to Compress = " + curname + "\n"
    x = x + "\n   fps = " + str(fps) + "\n"
    x = x + "\n   crf = " + str(crf) + "\n"
    x = x + "\n   software = " + sfwr + "\n"
    x = x + "=========================================================== \n"
    x = x + "=========================================================== \n\n"
    x = x + "Input file probe: \n"
    mylog.writelines(x)
    x = probeFile(newname)
    mylog.writelines(x)
    mylog.writelines ("\n=========================================================== \n")        
    mylog.writelines ("=========================================================== \n Run Log:\n")

    # compress  
    starttm = datetime.datetime.now()

    try:
        if (sfwr == "ffmpeg"):
            compresscmd = 'ffmpeg -i "' + newname + '" -crf ' + str(crf) + ' -r ' + str(fps) + ' "' + curname + '"'
        else:
            compresscmd = 'HandBrakeCLI -i "' + newname + '" -o "' + curname + '" -e x264 -q ' + str(crf) + ' -r ' + str(fps) + ' --pfr'
        subprocess.run(compresscmd, shell=True, capture_output=False)
        statusbar.showMessage("Compression complete")
    except Exception as e:
        x = "\n ERROR -> \n" +  e.args[0] + "\n"   
    finally:    
        mylog.writelines(x) 

    stoptm = datetime.datetime.now()
    deltatm = stoptm - starttm

    # probe output video
    mylog.write("\n\n=========================================================== \n") 
    mylog.write("=========================================================== \n") 
    mylog.write("Output file probe: \n")   
    x = probeFile(curname)
    mylog.writelines(x)
    mylog.write ("\n\n=========================================================== \n")
    mylog.write ("=========================================================== \n\n")

    # print job duration
    x = "Job took " + str(deltatm) + " long \n" 
    mylog.write (x)
    mylog.write ("=========================================================== \n") 
    mylog.write ("=========================================================== \n") 
    mylog.close()

    box = QMessageBox()
    box.setText("Done \n" + filename + " has been compressed ")
    box.setWindowTitle("CompressVideo")
    box.exec_()

# Main Window
app = QApplication(sys.argv)
MainWindow = QMainWindow()
MainWindow.resize(914,636)
MainWindow.setWindowTitle('CompressVideo')
bold_underline_75 = QtGui.QFont()
bold_underline_75.setBold(True)
bold_underline_75.setUnderline(True)
bold_underline_75.setWeight(75)
MainWindow.setFont(bold_underline_75)
MainWindow.setToolTip("Video Quality (QRF) - 22=higher, 30=lower")

# File Explorer Button
btnBrowse = QPushButton(MainWindow)
btnBrowse.setText('Select File')
btnBrowse.setGeometry(770, 10, 111, 31)
bold_italic_14 = QtGui.QFont()
bold_italic_14.setBold(True)
bold_italic_14.setPointSize(14)
bold_italic_14.setWeight(75)
bold_italic_14.setUnderline(False)
bold_italic_14.setItalic(True)
btnBrowse.setFont(bold_italic_14)
btnBrowse.setToolTip("Locate video to compress")
btnBrowse.clicked.connect(selectFile)

# File Location Panel
leFname = QLineEdit(MainWindow)
leFname.setGeometry(10, 10, 751, 28)
bold_75 = QtGui.QFont()
bold_75.setWeight(75)
bold_75.setBold(True)
bold_75.setUnderline(False)
leFname.setFont(bold_75)
leFname.setToolTip("Video to compress")
leFname.setText("Please select file")

# FPS Options
groupBox = QGroupBox(MainWindow)
groupBox.setGeometry(220, 500, 121, 91)
groupBox.setTitle("Frames / Second")
groupBox.setFont(bold_underline_75)

# 24 FPS
rb24 = QRadioButton(groupBox)
rb24.setGeometry(10, 30, 101, 21)
rb24.setText("24 fps")
rb24.clicked.connect(rb24pushed)

# 30 FPS
rb30 = QRadioButton(groupBox)
rb30.setGeometry(10, 60, 111, 21)
rb30.setText("30 fps")
rb30.setProperty("checked", True)
rb30.clicked.connect(rb30pushed)

# Quality Slider
hsVQ = QSlider(Qt.Horizontal, MainWindow)
hsVQ.setGeometry(450, 530, 121, 20)
hsVQ.setMinimum(22)
hsVQ.setMaximum(30)
hsVQ.setSingleStep(2)
hsVQ.setValue(24)
hsVQ.setTickInterval(2)
hsVQ.setTickPosition(QSlider.TicksBelow)
hsVQ.valueChanged.connect(crfChanged)

# Video Quality
label = QLabel(MainWindow)
label.setGeometry(440, 500, 131, 21)
label.setText("Video Quality")
label.setFont(bold_underline_75)

# Slider Quality Labels
label_2 = QLabel(MainWindow)
label_2.setGeometry(440, 550, 141, 20)
label_2.setText("22                                    30")
label_2.setFont(bold_75)

# Slider Current Value Label
lblCRF = QLabel(MainWindow)
lblCRF.setGeometry(490, 550, 31, 31)
bold_75_20 = QtGui.QFont()
bold_75_20.setPointSize(20)
bold_75_20.setWeight(75)
bold_75_20.setBold(True)
bold_75_20.setUnderline(False)
lblCRF.setFont(bold_75_20)
lblCRF.setText("24")

# Compress Button
btnCompress = QPushButton(MainWindow)
btnCompress.setGeometry(670, 470, 161, 101)
btnCompress.setText("Compress")
btnCompress.clicked.connect(compress)

# Usage Label
lblLabel = QLabel(MainWindow)
lblLabel.setGeometry(60, 460, 561, 31)
lblLabel.setFont(bold_75)
lblLabel.setText("Please set/verify parameters and then press button to compress")

# Software Options
groupBox_2 = QGroupBox(MainWindow)
groupBox_2.setGeometry(60, 500, 131, 111)
groupBox_2.setTitle("Software")

# Handbrake
rbHandBrake = QRadioButton(groupBox_2)
rbHandBrake.setGeometry(0, 30, 104, 21)
rbHandBrake.setText("handbrake")
rbHandBrake.setProperty("checked", True)
rbHandBrake.clicked.connect(rbhandbrakepushed)

# ffmpeg
rbHandBrake = QRadioButton(groupBox_2)
rbHandBrake.setGeometry(0, 70, 104, 21)
rbHandBrake.setText("ffmpeg")
rbHandBrake.clicked.connect(rbffmpegpushed)

# Text Browser
textBrowser = QTextBrowser(MainWindow)
textBrowser.setGeometry(10, 50, 871, 401)
normal20 = QFont()
normal20.setBold(False)
normal20.setUnderline(False)
normal20.setItalic(False)
normal20.setPointSize(14)
textBrowser.setFont(normal20)

# Status Bar
statusbar = QStatusBar(MainWindow)
statusbar.move(0, 600)
statusbar.showMessage("Ready")

# Display Everything
MainWindow.show()

sys.exit(app.exec_())