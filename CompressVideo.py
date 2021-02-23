##################################################################################################
#
# CompressVideo - compress a video to a smaller file size using H264 encoding standard    
#
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, os, subprocess, datetime
#
#globals
fps = 30
crf = 24
sfwr = "handbrake"
x = ""
filename = " "
#
##################################################################################################
#
class Ui(QtWidgets.QMainWindow):

    global fps
    global crf
    global filename
    global sfwr   # handbrake or ffmpeg
#
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('CompressVideo.ui', self)
        
        self.lblCRF.setText(str(crf))
        self.statusbar = self.statusBar()

        # Adding a temporary message
        self.statusbar.showMessage("Ready")
        self.show() 

        self.rbHandbrake.clicked.connect(self.rbhandbrakepushed)

        self.rbFfmpeg.clicked.connect(self.rbffmpegpushed)

        self.rb24.clicked.connect(self.rb24pushed)

        self.rb30.clicked.connect(self.rb30pushed)

        self.hsVQ.valueChanged.connect(self.crfChanged)

        self.btnBrowse.clicked.connect(self.selectFile)

        self.btnCompress.clicked.connect(self.compress)
#
#
    def rb24pushed (self):        
        fps=24
        self.statusbar.showMessage("24 fps selected")
        self.show()
        return
#
#
    def rb30pushed (self):
        fps=30
        self.statusbar.showMessage("30 fps selected")
        self.show()
        return
#
#
    def rbhandbrakepushed (self):
        sfwr = "handbrake"
        self.statusbar.showMessage("'handbrake' selected")
        self.show()
        return
#
#
    def rbffmpegpushed (self):
        sfwr = "ffmpeg"
        self.statusbar.showMessage("'ffmpeg' selected")
        self.show()
        return
#
#
    def crfChanged (self):
        global crf
        crf=self.hsVQ.value()
        self.lblCRF.setText(str(crf)) 
        return
#
#
    def selectFile (self):
        global filename 
        fname = QFileDialog.getOpenFileName(self, 'Select file', "/")
        filename = fname[0]
        self.leFname.setText(filename)
        return
#
#
    def probeFile (self, myfyl):
        inprobecmd = 'ffprobe "' + myfyl + '"'
        x = subprocess.getoutput(inprobecmd)
        return x
#
#
    def compress (self):
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
        # find name without file extension (ext)
        i=0
        i = filename.find(".")
        nameNoExt = filename[:i]

    # rename file, with "_ORIGINAL" appended
        newname = filename
        newname = newname.replace(".m", "_ORIGINAL.m")
        os.rename(filename, newname)

    # create new (compressed) & log filenames
        curname = nameNoExt + ".mp4"
        logfile = nameNoExt + ".log"
#
    # probe input video
        mylog = open(logfile, 'w')
        mylog.write ("=========================================================== \n") 
        mylog.write ("Input file probe: \n")
        x = self.probeFile (newname)
        mylog.writelines(x)
        mylog.write ("\n\n=========================================================== \n")        
    #
    # compress  
        starttm = datetime.datetime.now()
        
        if (sfwr == "ffmpeg"):
            compresscmd = 'ffmpeg -i "' + newname + '" -crf ' + str(crf) + ' -r ' + str(fps) + ' "' + curname + '"'
        else:
            compresscmd = 'HandBrakeCLI -i "' + newname + '" -o "' + curname + '" -e x264 -q ' + str(crf) + ' -r ' + str(fps) + ' --vfr'

        x = subprocess.run(compresscmd,shell=True,capture_output=False)
        stoptm = datetime.datetime.now()
        deltatm = stoptm - starttm

    # probe output video
        mylog.write ("=========================================================== \n") 
        mylog.write ("Output file probe: \n")   
        x = self.probeFile (curname)
        mylog.writelines(x)
        mylog.write ("\n\n=========================================================== \n")

    # print job duration
        x = "Job took " + str(deltatm) + " long \n" 
        mylog.write (x)
        mylog.write ("=========================================================== \n") 
        mylog.close()
#
        self.statusbar.showMessage("All done", 300000)
#
        return
#
##################################################################################################
#
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
#
##################################################################################################

