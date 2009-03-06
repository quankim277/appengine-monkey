import doctest
import os
try:
    import google
except ImportError:
    print 'You must make sure the GAE SDK is on PYTHONPATH'
    raise

__file__ = os.path.abspath(__file__)
base_path = os.path.join(os.path.dirname(__file__), 'scratch')
root_path = os.path.dirname(os.path.dirname(__file__))
google_path = os.path.dirname(google.__file__)

if __name__ == '__main__':
    doctest.testfile('pylons.txt',
                     optionflags=doctest.ELLIPSIS,
                     extraglobs=dict(base_path=base_path,
                                     root_path=root_path,
                                     google_path=google_path))

    
