##simple_http
```shell
header, cookie, content = simple_http.get("https://github.com") 
In [11]: pprint.pprint(header)
{'Cache-Control': 'private, max-age=0, must-revalidate',
 'Content-Encoding': 'gzip',
 'Content-Security-Policy': "default-src *; script-src 'self' https://github.global.ssl.fastly.net https://ssl.google-analytics.com https://collector-cdn.github.com https://analytics.githubapp.com https://embed.github.com https://raw.github.com; style-src 'self' 'unsafe-inline' https://github.global.ssl.fastly.net; object-src 'self' https://github.global.ssl.fastly.net",
 'Content-Type': 'text/html; charset=utf-8',
 'Date': 'Thu, 02 Jan 2014 08:21:01 GMT',
 'ETag': '"57e6cfb59a5805bc99dc31df0030b0d4"',
 'Server': 'GitHub.com',
 'Set-Cookie': 'logged_in=no; domain=.github.com; path=/; expires=Mon, 02-Jan-2034 08:21:01 GMT; secure; HttpOnly\r\n_gh_sess=BAh7BzoPc2Vzc2lvbl9pZCIlN2ZkNzQxMmU0MTAwNDVjMDE3ZjI5NGE2YjQxZmZkMTM6EF9jc3JmX3Rva2VuSSIxaGhPKzg2b1ptSGpTRFphYjJCd0ZBYS9IbXVIZWR4THhzUjZibTNUN0tFcz0GOgZFRg%3D%3D--8681a13f25ede942ba66551b0c065eb1c31529fa; path=/; secure; HttpOnly',
 'Status': '200 OK',
 'Strict-Transport-Security': 'max-age=2592000',
 'Transfer-Encoding': 'chunked',
 'Vary': 'Accept-Encoding',
 'X-Frame-Options': 'deny',
 'X-GitHub-Request-Id': 'B7D13607:5774:4AB6EAC:52C5216C',
 'X-Runtime': '5',
 'message': 'OK',
 'protocol': 'HTTP/1.1',
 'status': 200}

In [12]: pprint.pprint(cookie)
[OrderedDict([('cookie', 'logged_in=no'), ('domain', '.github.com'), ('path', '/'), ('expires', 'Mon, 02-Jan-2034 08:21:01 GMT'), (' secure', ''), (' HttpOnly', '')]),
 OrderedDict([('cookie', '_gh_sess=BAh7BzoPc2Vzc2lvbl9pZCIlN2ZkNzQxMmU0MTAwNDVjMDE3ZjI5NGE2YjQxZmZkMTM6EF9jc3JmX3Rva2VuSSIxaGhPKzg2b1ptSGpTRFphYjJCd0ZBYS9IbXVIZWR4THhzUjZibTNUN0tFcz0GOgZFRg%3D%3D--8681a13f25ede942ba66551b0c065eb1c31529fa'), ('path', '/'), (' secure', ''), (' HttpOnly', '')])]

In [14]: pprint.pprint(content[:1024])
'<!DOCTYPE html>\n<html>\n  <head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# githubog: http://ogp.me/ns/fb/githubog#">\n    <meta charset=\'utf-8\'>\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n        <title>GitHub \xc2\xb7 Build software better, together.</title>\n    <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="GitHub" />\n    <link rel="fluid-icon" href="https://github.com/fluidicon.png" title="GitHub" />\n    <link rel="apple-touch-icon" sizes="57x57" href="/apple-touch-icon-114.png" />\n    <link rel="apple-touch-icon" sizes="114x114" href="/apple-touch-icon-114.png" />\n    <link rel="apple-touch-icon" sizes="72x72" href="/apple-touch-icon-144.png" />\n    <link rel="apple-touch-icon" sizes="144x144" href="/apple-touch-icon-144.png" />\n    <link rel="logo" type="image/svg" href="https://github-media-downloads.s3.amazonaws.com/github-logo.svg" />\n    <meta property="og:image" content="https://github.global.ssl.fastly.net/images/modules/logos_page/O'
...
```
###Proxy: HTTP and SOCKS5
####socks5
```shell 
In [8]: simple_http.get("https://google.com", proxy='socks5://127.0.0.1:8888')
Out[8]: 
({'Alternate-Protocol': '443:quic',
  'Cache-Control': 'public, max-age=2592000',
  'Content-Length': '220',
  'Content-Type': 'text/html; charset=UTF-8',
  'Date': 'Wed, 08 Jan 2014 13:28:59 GMT',
  'Expires': 'Fri, 07 Feb 2014 13:28:59 GMT',
  'Location': 'https://www.google.com/',
  'Server': 'gws',
  'X-Frame-Options': 'SAMEORIGIN',
  'X-XSS-Protection': '1; mode=block',
  'message': 'Moved Permanently',
  'protocol': 'HTTP/1.1',
  'status': 301},
 None,
 '<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">\n<TITLE>301 Moved</TITLE></HEAD><BODY>\n<H1>301 Moved</H1>\nThe document has moved\n<A HREF="https://www.google.com/">here</A>.\r\n</BODY></HTML>\r\n')
```
####http
```shell 
In [46]: simple_http.get("https://google.com", proxy='http://127.0.0.1:8088')
Out[46]: 
({'Alternate-Protocol': '443:quic',
  'Cache-Control': 'public, max-age=2592000',
  'Content-Encoding': 'deflate',
  'Content-Length': '172',
  'Content-Type': 'text/html; charset=UTF-8',
  'Date': 'Wed, 08 Jan 2014 13:46:57 GMT',
  'Expires': 'Fri, 07 Feb 2014 13:46:57 GMT',
  'Location': 'https://www.google.com/',
  'Server': 'gws',
  'Via': 'HTTP/1.1 GWA',
  'X-Frame-Options': 'SAMEORIGIN',
  'X-Xss-Protection': '1; mode=block',
  'message': '',
  'protocol': 'HTTP/1.1',
  'status': 301},
 None,
 '<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">\n<TITLE>301 Moved</TITLE></HEAD><BODY>\n<H1>301 Moved</H1>\nThe document has moved\n<A HREF="https://www.google.com/">here</A>.\r\n</BODY></HTML>\r\n')
``` 
###http request simulator
```shell 
#python http_request_simulator.py "www.baidu.com"
=========
page done: www.baidu.com
timeout: 5s
=========
url done: http://www.baidu.com/cache/global/img/gs.gif
url done: http://www.baidu.com/img/bdlogo.gif
url done: http://s1.bdstatic.com/r/www/cache/static/user/js/u_7b0ea87f.js
url done: http://s1.bdstatic.com/r/www/cache/static/global/js/home_254ecbb1.js
url done: http://s1.bdstatic.com/r/www/cache/static/global/js/tangram-1.3.4c1.0_07038476.js
url done: http://s1.bdstatic.com/r/www/cache/static/jquery/jquery-1.10.2.min_f2fb5194.js
request done
```
```py
#! /usr/bin/env python
import os
import pdb
import json
import signal
import _proc
import umysql
import nonblocking
import os.path

myport = 8800
mycpu = 0

mycon = umysql.Connection() 
#default connection

def sigusr1_handler(signum, frame):
    print "cons: ", len(nonblocking.cons) 
    print "worker at %d on cpu %d" % (myport, mycpu)

def home_get(request, response): 
    response.update({ 
            "header": {
                "STATUS": 403,
                "Content-Encoding": "gzip",
                "Content-Type": "text/html", 
                },
            "stream": ""
            })

def home_post(request, response): 
    request_stream = request["stream"] 
    if "host" in request_stream:
        try:
            host, port, user, passwd, db = request_stream.values()
        except:
            raise Exception((nonblocking.HTTP_LEVEL, 400))
        if mycon.is_connected():
            mycon.close()
        try:
            mycon.connect(host, port, user, passwd, db)
            result = ""
        except Exception, err:
            result = json.dumps(err.args)
        response.update({
            "header": {
                "STATUS": 200,
                "Content-Encoding": "gzip",
                "Content-Type": "application/json"
                },
            "stream": result
            })
        return 
    if "sql" in request_stream: 
        if not mycon.is_connected():
            mycon.connect("localhost", 3306, "root", "!20111992ma", "mysql")
        sql = request_stream["sql"] 
        try:
            query = mycon.query(sql)
            if isinstance(query, tuple):
                result = json.dumps(query)
            else:
                fields = json.dumps(query.fields)
                rows = json.dumps(query.rows) 
                result = json.dumps({"field": fields, "row": rows})
        except Exception, err:
            result = json.dumps(err.args)
        response.update({
            "header": {
                "STATUS": 200,
                "Content-Encoding": "gzip",
                "Content-Type": "application/json" 
                },
            "stream": result
                }) 
    else: 
        raise Exception((nonblocking.HTTP_LEVEL, 400)) 

home_application = {
        "url": r"^/query$",
        "GET": home_get,
        "POST": home_post 
        }

nonblocking.install(home_application)
nonblocking.install_statics("ui", os.path.abspath("./statics"), nonblocking.STATICS_MMAP)

try:
    _proc.setrlimit(_proc.RLIMIT_NOFILE, (20480, 40960))
except OSError, err:
    print "setrlimit failed, quit: %s" % str(err)
    exit(0)

signal.signal(signal.SIGUSR1, sigusr1_handler)
nonblocking.log_level = nonblocking.LOG_ALL

nonblocking.run_as_user("richard_n")
nonblocking.server_config() 
nonblocking.daemonize() 

nonblocking.poll_open(("localhost", 8800)) 
print "worker at %d on cpu %d" % (8800, 0)
nonblocking.poll_wait()
```
