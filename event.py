"""
Defines a mix-in class for events.
"""
import threading, traceback

class EventSource(object):
    """
    This is a mix-in for classes that want to produce events for other modules 
    to subscribe to.
    """
    __calls = None
    def __init__(self, *p, **kw):
        super(EventSource, self).__init__(*p, **kw)
        self.__calls = {}
    
    def connect(self, event, func, thread=True):
        """es.connect(str, callable, [bool])
        Registers your callback against the named event. If thread is True, the 
        callback will be called in a new thread.
        """
        event = str(event)
        e = self.__calls.setdefault(event, {})
        e[func] = thread
    
    def disconnect(self, event, func):
        """es.disconnect(str, callable)
        Removes the given callback from the named event. If it's not there, 
        ValueError is raised.
        """
        try:
            del self.__calls[event][func]
        except KeyError:
            raise ValueError
    
    def emit(self, event, *p, **kw):
        """es.emit(str, ...)
        Throws the event and calls the callbacks for it. Any additional 
        parameters are passed to the callbacks.
        """
        try:
            calls = self.__calls[event]
        except KeyError:
            return
        
        for func, thread in calls.items():
            if thread:
                t = threading.Thread(target=func, args=p, kwargs=kw)
                t.setDaemon(True)
                t.start()
            else:
                try:
                    func(*p, **kw)
                except KeyboardInterrupt:
                    raise
                except:
                    print >> sys.stderr, "Error in event %s, ignored" % event
                    traceback.print_exc()
