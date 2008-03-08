import gobject
import os
import tempfile
import string
import sys
from pyroom_error import PyroomError

elapsaed_time=0 #seconds elapsed couner
autosave_time=3 #the timeout time in minutes
temp_folder= "/var/tmp/pyroom" #the temp folder
timeout_id = 0

FILE_UNNAMED = _('* Unnamed *')  ##repeted definition delete if possible

#def autosave_init(self,mill=1000,autosavetime=3, tempfolder="/var/tmp/pyroom"):
def autosave_init(self, agui, mill=1000):
    """Init the internal autosave timer"""
    global elapsed_time
    #global autosave_time
    #global temp_folder

    global timeout_id
    global gui
    gui = agui
    timeout_id=gobject.timeout_add(mill,timeout, self)
    elapsed_time=0  ## init the elapsed_time_var
    #temp_folder=tempfolder
    #autosave_time=autosavetime

def save_file(filename, text):
    try:
        out_file = open(filename,"w")
        out_file.write(text)
        out_file.close()
    except:
        x = PyroomError(_("Could not autosave file %s") % filename)
        self.error.set_text(str(x)) 
        if self.verbose:
            print str(e)
            print e.traceback

def autosave_quit(self):
    """dispose the internal timer"""
    gobject.source_remove(timeout_id)

def autosave_file(self, buffer_id):
	"""AutoSave the Buffer to temp folder"""
	buffer=self.buffers[buffer_id]
	if not os.path.exists(temp_folder):  #chech if the path exists
	    os.mkdir(temp_folder)    

	if buffer.tmp_filename==None:
	    if buffer.filename==FILE_UNNAMED:
		buffer.tmp_filename=tempfile.mkstemp(suffix="",prefix="noname_"+"tmp_",dir=temp_folder,text=True)[1]
	    else:
		buff_path,buff_name=os.path.split(buffer.filename)
		#print buff_path, buff_name #(debug)
		buffer.tmp_filename=tempfile.mkstemp(suffix="",prefix=buff_name+"_tmp_",dir=temp_folder,text=True)[1]
	save_file(buffer.tmp_filename, buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())) #really saves the fil
	self.status.set_text(_('AutoSaving Buffer %d, to temp file %s') % (buffer_id, buffer.tmp_filename)) #inform the user of the saving operation

def timeout(self):
    "the Timer Function"
    global elapsed_time
    global autosave_time

    if (int(autosave_time)!=0):
        elapsed_time=elapsed_time+1
        #less exam  print "elapsed time = %d , autosave_time = %d" % (elapsed_time, int(autosave_time)*60)   #(debug)
        if (elapsed_time>=(int(autosave_time)*60)):
            for buffer in self.buffers:
                #print "saving buffer" + str(buffer)
                autosave_file(self,self.buffers.index(buffer))
            elapsed_time=0
        return True # coninue repeat timeout event
    else:
        print "Autosave Feature Disabled"
        self.status.set_text(_('AutoSaving Feature disabled')) #inform the user of the autosave disabled
        return False #stop timeout event

def kill_tempfile(killfile):
    global temp_folder
    print "removing File :", os.path.join(temp_folder,killfile)
    try:
        os.remove(os.path.join(temp_folder,killfile))
    except:
        print " ** is not possible to remove %s" % str(os.path.join(temp_folder,killfile))


def kill_all_tempfile():
    """Kills all the temporary files"""
    global temp_folder
    print "Cleaning Pyroom Temp Folder : ",temp_folder
    response=raw_input("proceed [Yes/No]?")
    if string.lower(response)=="yes":
	killlist = os.listdir(temp_folder)
	if len(killlist)==0 : sys.exit(0)
        for killfile in killlist:
            kill_tempfile(killfile)
    else:
	    print "Nothing deleted..."
    #sys.exit(0) 
    
#EOF
