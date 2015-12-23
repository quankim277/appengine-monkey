# Introduction #

This describes the steps, using appengine-monkey, to get Pylons working on appengine.

# Details #

This is an updated guide to setting up a Pylons environment on appengine.  This is based on the [testable guide](http://appengine-monkey.googlecode.com/svn/trunk/docs/pylons.txt); that guide is a little hard to read, but can be used to confirm (or deny) that this process works.

Here's the basic instructions:

## 1. Acquire the code ##

Check out the source code for appengine-monkey, like:

```
svn checkout http://appengine-monkey.googlecode.com/svn/trunk/ appengine-monkey
```

## 2. Create an environment for your code ##

This will create a [virtualenv](http://pypi.python.org/pypi/virtualenv) environment ready for your application:

```
$ python2.5 appengine-homedir.py --gae <google_path> MyApp
```

Note that `<google_path>` should be the path where you have unpacked the appengine SDK.

This will set up an environment in `MyApp/`, with some tools installed in `MyApp/bin`.  There will also be a directory `MyApp/app` which is the directory you would upload to appengine.  You may want to edit `MyApp/app/app.yaml` to change the application ID.

## 3. Start installing things, like Pylons ##

This virtualenv environment has been setup to install packages into `MyApp/app/lib/python`.  You can install packages like this:

```
$ cd MyApp
$ ./bin/pip install Pylons
```

Note that the [pip installer](http://pip.openplans.org/) (a replacement for easy\_install) is in `MyApp/bin`, but other scripts (like `paster`) will be in `MyApp/app/bin`.

The current Pylons release, and its component libraries (e.g., Beaker, Mako) all work with appengine.  (When appengine first came out, you'd have to install the development versions of several libraries.  This is no longer the case.)

## 4. Create your application ##

We'll use the standard way to create an application, but we'll have to move some files around when we are done.

```
$ cd MyApp/app
# Delete the old Hello World application:
$ rm -r myapp
$ paster create --template=pylons MyApp sqlalchemy=false
```

You will choose your template engine.  Mako works fine.  Then some files have to be moved around:

```
$ mv MyApp/myapp .
$ rm -r MyApp
```

The appengine-monkey pattern does not use Setuptools or [Paste Deploy](http://pythonpaste.org/deploy/) for the configuration.  Instead the application is instantiated directly, using `MyApp/app/runner.py`, with parameters located in `MyApp/app/config.py`.

## 5. Edit environment.py ##

In `MyApp/app/myapp/config/environment.py` find this line and remove it:

```
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
```

## 6. Edit config.py ##

Put this in `MyApp/app/config.py`:

```
APP_NAME = 'myapp.config.middleware:make_app'
APP_ARGS = ({},)
APP_KWARGS = dict()
APP_KWARGS.update({'beaker.session.type': 'google', 'beaker.session.table_name': 'beaker_session',
                   'beaker.session.key': 'pylonstestapp', 'beaker.session.secret': 'secret',
                   'beaker.cache.type': 'google', 'beaker.cache.table_name': 'beaker_cache'})
# You can overwrite these separately for different dev/live settings:
DEV_APP_ARGS = APP_ARGS
DEV_APP_KWARGS = APP_KWARGS
REMOVE_SYSTEM_LIBRARIES = ['webob']
```

Note that `APP_NAME` has to be updated with the module name of your application (`myapp` in this example).  The beaker.**options are all standard for appengine.  You could include other options specific to your application in `APP_KWARGS`.**

The `REMOVE_SYSTEM_LIBRARIES` value will cause `runner.py` to remove some appengine-provided libraries at runtime, so you can use your own versions of the libraries.  [WebOb](http://pythonpaste.org/webob/) specifically has a newer version out that Pylons uses.  You could also put `'django'` here to disable Django, or disable yaml.

## 7. Running you application ##

Your application should be ready to run under the SDK or on App Engine itself.  To run it in the SDK:

```
/usr/bin/python2.5 dev_appserver.py MyApp/app/
```

Note that you should **not** use the virtualenv python `MyApp/bin/python` to run dev\_appserver.py.  If you get an error about importing `site` then you probably started it in the virtualenv.  Note you can run `deactivate` on the shell to disable the virtualenv (if you used `source bin/activate`).

To upload the application:

```
/usr/bin/python2.5 appcfg.py update MyApp/app
```

If you have many libraries you might find that you hit a [1000 file limit](http://code.google.com/p/googleappengine/issues/detail?id=161&q=reporter:ianbicking&colspec=ID%20Type%20Status%20Priority%20Stars%20Owner%20Summary).  This limit has been improved so that static and code files don't share the same limit, but it's still problematic.  Please go star that ticket to learn when it will go away, and to indicate that you want Google to raise the limit to something less limiting (at 10,000 files probably everyone will be happy).  Sometimes unnecessary packages will be in `my-app/lib/python2.5/site-packages`, which you can delete to get under 1000 files.

Sometimes failures will be intermittent.  If it fails, try again.

## 8. Looking at the system interactively ##

In addition to running your application, you can run code in the Google environment, importing your code, and interacting with models.  If you run `MyApp/bin/python` the environment will get setup.  (You'll notice you will constantly get warnings about this setup, advice on how to suppress those without suppressing all warnings would be appreciated.)

One thing you can do is use this for testing.  The package that Pylons uses, [WebTest](http://pythonpaste.org/webtest/), can be used for any system (Django, web.py, etc).  Using it looks like this:

```
# If you haven't installed Pylons or WebTest:
$ MyApp/bin/pip install WebTest
$ MyApp/bin/python
>>> import webtest
>>> from runner import application
>>> app = webtest.TestApp(application)
>>> print app.get('/')
```

This will show you the response you get from fetching the root page (including headers and status).  There are many methods to help you test your application in this context.  `runner.application` is the WSGI application that is run, and in this example `app` is a handy wrapper for that application.

## 9. Making the system more compact (getting around the 1000 file limit) ##

If you are encountering problems getting your system under the maximum number of files, there are two tools to help.

The first is in appengine\_monkey, [appengine\_count\_skip.py](http://appengine-monkey.googlecode.com/svn/trunk/appengine_count_skip.py).  You can run this like:

```
$ cd MyApp/app
$ ../bin/python /path/to/appengine_count_skip.py
```

This will show you a long summary of all the files in your application, and if they are or are not skipped using the `skip_files` setting in `app.yaml`.  If you don't have a skip\_files setting the output will appear to indicate everything is skipped.  Note that this is somewhat limited, as there's actually just one gigantic regular expression, and this script tries to split the regex on newlines and interpret each item as an individual regex; you might have to edit the expression to make this work.

Another tool is in pip, which will show you packages and let you zip and unzip packages.  To see your packages:

```
$ cd MyApp/
$ ./bin/pip zip -l
```

You can see your zipped packages (by default, none) and your unzipped packages.  You can zip a package with:

```
$ ./bin/pip zip mako
```

Use `pip unzip` to undo this.