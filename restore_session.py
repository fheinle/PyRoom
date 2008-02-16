
def save_session(self):
    """saves open filenames to a file called session"""
    name = open("session", "w")
    for buffer in self.buffers:
        text = buffer.filename
        name.write(buffer.filename + "\n")
    name.close()

def open_session(self, ret):
    """opens session from session file"""
    if ret:
        opensession = open("session", "r")
        files_open = []
        for line in opensession:
            if line != "* Unnamed *\n":
                files_open.append(line)


        buffer = self.new_buffer()
        for c in files_open:
            n = 0
            filename = files_open[n][:-1]
            n = n+1
            buffer.filename = filename
            try:
                f = open(buffer.filename, 'r')
                buffer = self.buffers[self.current]
                buffer.begin_not_undoable_action()
                utf8 = unicode(f.read(), 'utf-8')
                buffer.set_text(utf8)
                buffer.end_not_undoable_action()
                f.close()
                self.status.set_text(_('File %s open')
                            % buffer.filename)
            except IOError, (errno, strerror):
                errortext = '''Unable to open %(filename)s.''' % {'filename': buffer.filename}
                if errno == 2:
                    errortext += ' The file does not exist.'
                elif errno == 13:
                    errortext += ' You do not have permission to open the file.'
                buffer.set_text(_(errortext))
                if verbose:
                    print ('''Unable to open %(filename)s. %(traceback)s'''
                        % {'filename': buffer.filename, 'traceback': traceback.format_exc()})
                self.status.set_text(_('Failed to open %s')
                    % buffer.filename)
                buffer.filename = FILE_UNNAMED
            except:
                buffer.set_text(_('Unable to open %s\n'
                                    % buffer.filename))
                if verbose:
                    print ('''Unable to open %(filename)s. %(traceback)s'''
                        % {'filename': buffer.filename,
                        'traceback': traceback.format_exc()})
                buffer.filename = FILE_UNNAMED

        
