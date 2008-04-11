import os
import imp
import sys

class Missing(object):
    def __init__(self, name):
        self.name = name
    def __call__(self, *args, **kw):
        raise NotImplemented('%s is not implemented' % self.name)
    def __repr__(self):
        return '<Missing function %s>' % self.name

os.utime = Missing('os.utime')
os.rename = Missing('os.rename')
os.unlink = Missing('os.unlink')
os.open = Missing('os.open')

def can_access(path):
    try:
        os.listdir(path)
        return True
    except OSError:
        return False

sys.path = [p for p in sys.path if can_access(p)]

def imp_acquire_lock():
    pass
imp.acquire_lock = imp_acquire_lock

def imp_release_lock():
    pass
imp.release_lock = imp_release_lock

def imp_load_module(fullname, fp, filename, etc):
    pass
imp.load_module = imp_load_module

def imp_find_module(subname, path):
    for p in path:
        full_py = os.path.join(p, subname + '.py')
        full_dir = os.path.join(p, subname, '__init__.py')
        for full in full_py, full_dir:
            if os.path.exists(full):
                return open(full), full, None
    return None, '', None
imp.find_module = imp_find_module
