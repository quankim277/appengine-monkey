import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'appengine-monkey'))
import appengine_monkey
from webob import Request, Response
import urlparse
import httplib
import wsgiref.handlers


FORM = '''\
<html>
<head><title>Get a page</title></head>
<body>
<h1>Get a page!</h1>

<form action="" method="POST">

URL: <input type="text" name="url" value="http://"><br>

Library: <select name="library">
  <option value="httplib">httplib</option>
  <option value="urllib">urllib</option>
  <option value="urllib2">urllib2</option>
  </select> <br>

Method: <select name="method">
  <option value="GET">GET</option>
  <option value="POST">POST</option>
  <option value="PUT">PUT</option>
  <option value="DELETE">DELETE</option>
  <option value="HEAD">HEAD</option>
  </select> <br>

Headers: <textarea name="headers" cols=3 style="width: 100%"></textarea>
<br>

Body: <textarea name="body" cols=5 style="width: 100%"></textarea>
<br>

<input type="submit" value="Make The Request">

</form>
</body></html>
'''

def wrap_error(app):
    def wrapped(environ, start_response):
        try:
            return app(environ, start_response)
        except:
            import traceback
            start_response('200 OK', [('Content-type', 'text/plain')])
            from StringIO import StringIO
            out = StringIO()
            traceback.print_exc(file=out)
            return [out.getvalue()]
    return wrapped

def application(environ, start_response):
    req = Request(environ)
    if req.method == 'POST':
        func = getattr(fetcher, 'get_%s' % req.params['library'])
        headers = {}
        for line in req.params['headers']:
            line = line.strip()
            if not line:
                continue
            name, value = line.split(':', 1)
            headers[name] = value.strip()
        status, headers, body = func(req.params['url'], req.params['method'],
                                     headers, req.params['body'] or None)
        parts = ['%s\n' % status]
        for name, value in headers:
            parts.append('%s: %s\n' % (name, value))
        parts.append('\n')
        parts.append(body)
        wsgi_resp = Response(content_type='text/plain', body=''.join(parts))
        return wsgi_resp(environ, start_response)
    else:
        wsgi_resp = Response(body=FORM)
        return wsgi_resp(environ, start_response)

class Fetcher(object):

    def get_httplib(self, url, method, headers, body):
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        if query:
            path += "?" + query
        if scheme == 'http':
            Class = httplib.HTTPConnection
        else:
            Class = httplib.HTTPSConnection
        conn = Class(netloc)
        conn.request(method, path, body, headers)
        resp = conn.getresponse()
        return ('%s %s' % (resp.status, resp.reason),
                resp.getheaders(),
                resp.read())

    def get_urllib(self, url, method, headers, body):
        import urllib
        resp = urllib.urlopen(url, body)
        headers = resp.info().items()
        return ('200 OK I GUESS',
                headers,
                resp.read())

    def get_urllib2(self, url, method, headers, body):
        import urllib2
        req = urllib2.Request(url, body, headers)
        resp = urllib2.urlopen(req)
        return ('200 OK I GUESS',
                headers,
                resp.read())

fetcher = Fetcher()

def main():
    appengine_monkey.patch_modules()
    wsgiref.handlers.CGIHandler().run(wrap_error(application))

if __name__ == '__main__':
    main()
    
