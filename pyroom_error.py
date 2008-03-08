import traceback
class PyroomError (Exception):
    def __init__(self, message):
        self.value = 'ERROR: ' + message
        self.traceback = traceback.format_exc()
    def __str__(self):
         return repr(self.value)
