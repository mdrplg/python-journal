"""server.py -- cherrypy server on port 9097"""
import os
from pid import PidFile
import cherrypy
#from cherrypy.lib import auth_basic
import notes as notes
import datetime
import config as config
from timestamp import TimeStamp
#import bcrypt
import pickle
import dbstuff as db
import simplejson
#from cryptacular.bcrypt import BCRYPTPasswordManager as pwman

#from hmac import compare_digest
#from crypt import crypt

#Users = {'Eno':'fIIk4/x60YM8c', 'jef':b'$2b$12$KVX65QCQZzpTflFEShKwIO79Ka07epydxF08.686v1v4Y2oI4BzFK'}

def encrypt_pwd(realm, user, token):
        Users = pickle.load(open('Users.pic','rb'))
        fie = Users[user]
        return pwman().check(fie,token)

METAHDR = """
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-store, must-revalidate">
        <script src="bootstrap/js/bootstrap.min.js">
        </script>
        <script>
            function forget(akey){{
                window.location.replace("undo?key="+akey);
            }}
            function ritemenu(akey){{
                window.location.replace("copy?key="+akey);
            }}
            function editme(akey) {{
                window.location.replace("edit?key="+akey);
            }}
            function setpath(){{
                var pathpart = location.pathname;
                var prefix = pathpart.substring(1,4);
                console.debug(prefix)
                if (prefix == 'add') {{
                    location.href = "/done";
                }}
            }}
            function getet(){{
                var divi = document.getElementById("REC1");
                var timestamp = divi.innerText;
                var year = timestamp.substr(0,4);
                var month = timestamp.substr(4,2)-1;
                var day = timestamp.substr(6,2);
                var hour = timestamp.substr(8,2);
                var minute = timestamp.substr(10,2);
                var second = timestamp.substr(12,2);
                var drdt = new Date(year,month,day,hour,minute,second,0);
                var crct = new Date();
                var diff = crct - drdt;
                var examp = new Date(diff);
                var h = examp.getUTCHours();
                var m = padd(examp.getUTCMinutes());
                var sera = h + ":" + m ;
                return sera;
            }}
            function et(){{
                var sera = getet();
                console.log(sera);
                document.getElementById("TimeSincePost").innerHTML = sera;
            }}
            function padd(n) {{
                n = n + '';
                return n.length >= 2 ? n : '0'+n;
            }}
            function domeaction(){{
                //var rq = new XMLHttpRequest()
                //rq.open("GET","updateperiod?interval="+tera,true)
                //rq.send()
                var sera = getet()
                document.getElementById("interval").value = sera
                console.log(sera)
                //window.alert(document.getElementById("interval").value)
                var dome = document.getElementById("dome").submit();
            }}

            function diddle() {{
                window.setInterval("et()", 60000);
                et();
                setpath();
            }}
            function day(searchday) {{
                var url = "day?d2g=\\""+str(searchday)+"\\""
                window.location.replace();
            }}
        </script>
        
        <title>Jef's Journal</title>
        <link rel="stylesheet" href="bootstrap/bootstrap.min.css">
        <link href="static/style.css" rel="stylesheet">
        </head>

        """

THEHTML = """
        <body onload="diddle()">
        <div class="container">
        <a href="/">Home</a>&nbsp;<a href="all">ALL</a>&nbsp;<a href="done?filter={dayfilter}">DONE</a>&nbsp;
        <a href="choose_notebook">NOTEBOOKS</a>&nbsp;<a href="summary">Summary</a>
        &nbsp;<a href="search?term=">Search</a>&nbsp;<a href="upload">Upload a picture</a>
        <hr>
        <h1>{TITLE}</h1>
        <div class=\"container\" id=\"TimeSincePost\" ></div>
        <div>{BODY}</div>
        </div>
        </body>
        </html>
        """

BASEHTML = METAHDR + THEHTML

DLINE = "<tr><td><div id=\"REC{COUNT}\"><button type=\"button\" onclick=\"editme({DATETIME});\">{DATETIME}</button></div></td><td><div style=\"width:58vw;\">{ENTRY}</div></td></tr>"
ELINE = """
<tr>
    <td><button onclick=\"forget({DATETIME});\">Forget</button></td>
    <td><a href=\"mpyarkdone?key={DATETIME}\">{DATETIME}</a></td>
    <td>{ENTRY}</td>
</tr>
"""
QLINE = """<tr><td><a href=\"day?d2g={DAYKEY}\">{DAYKEY}</a></td><td>{COUNT}</td></tr>"""
FLINE = """<tr><td><a href=\"day?d2g={DATETIME}\">{DATETIME}</a></td><td>{ENTRY}</td></tr>"""

class Notes(object):
    @cherrypy.expose
    def index(self, filter=''):
        return self.done()

    @cherrypy.expose
    def add(self, entry, dayfilter=None, interval=None):
        if dayfilter==None:
            dayfilter = TimeStamp().timestamp()
        
        notes.create_journal_entry(entry, dayfilter,  interval)
        return self.done(filter=dayfilter)

    @cherrypy.expose
    def ins(self, dayfilter, entry, interval=None):
        if notes.create_journal_entry(entry, dayfilter, interval):
            return "keepgoing"
        else:
            return "stop"


    @cherrypy.expose
    def all(self ):
        _, _, notebook = notes.load_journal()
        body = "<form method=\"GET\" action=\"undo\"><input type=\"text\" name=\"key\"><button type=\"submit\">UNDO</button></form><hr>"
        body += "<table><tr><th>timestamp</th><th><Entry></th></tr>"
        global BASEHTML, DLINE
        title = 'All Journal Entries'
        journal, _, _ = notes.load_journal()
        for i in reversed(sorted(journal.keys())):
            body = body + FLINE.format(DATETIME=journal[i].title, ENTRY=journal[i].entry )
        body = body + "</table>"
        return BASEHTML.format(journal=notebook.notebooks[notebook.current_notebook], TITLE=title, BODY=body, dayfilter=TimeStamp().daypart())


    @cherrypy.expose
    def done(self, filter='', entry=''):
        cherrypy.response.headers['Cache-Control']='no-cache, no-store, must-revalidate'     
        c = 0
        body = "<div class=\"container\"><div class=\"col-sm-7\">"
        body += "<form name=\"dome\" id=\"dome\" method=\"GET\" action='add'>"
        body += "<textarea rows=\"5\" cols=\"49\" name=\"entry\"></textarea>"
        body += "<input type=\"hidden\" name=\"interval\" id=\"interval\"/>"
        body += "<button type=\"button\" onclick=\"domeaction();\">Enter</button>"
        #body += """<button type="submit"></button>"""
        body += "</form></div><div class=\"col-sm-5\"><h3>{VERSIONNUM}</h3><h4>{PWD}</h4></div></div>"
        body = body + "<table><tr><th>timestamp</th><th>Entry</th></tr>"
        global BASEHTML, DLINE
        if filter is None or filter == '':
            dayfilter=TimeStamp().daypart()
        else:
            dayfilter = TimeStamp(filter).daypart()
        title = 'Done entries'
        journal, todo_dict, notebook = notes.load_journal(filter=dayfilter)
        for i in reversed(sorted(journal.keys())):
            #if filter == '' or filter in i:
            if i in todo_dict.keys():
                if todo_dict[i] == True:
                    pass
                else:
                    c=c+1
                    body = body + DLINE.format(COUNT=c,DATETIME=journal[i].title, ENTRY=journal[i].entry.replace('""','"').replace("''","'") )
            else:
                c=c+1
                body = body + DLINE.format(COUNT=c,DATETIME=journal[i].title, ENTRY=journal[i].entry.replace('""','"').replace("''","'"))             
        body = body + "</table>"
        #print(body)
        VN=config.version()
        CD=os.getcwd()
        print(VN)
        print(CD)
        body = body.format(VERSIONNUM=VN, PWD=CD)
        return BASEHTML.format(TITLE=title, BODY=body, dayfilter=TimeStamp().daypart())

    @cherrypy.expose
    def day(self, d2g, offset=0):
        global METAHDR
        offset=int(offset)
        body=""
        if d2g is not None and len(d2g) > 0:
            when = TimeStamp(d2g)
            if offset < 0 :
                then = when.yesterday()
                ts=then[0:8]
                return self.day(ts)
                #window.location.replace("day?d2g="+ts+"&offset=-1");
            elif offset > 0:
                then = when.tomorrow()[0:8]
                return self.day(then)
                #window.location.replace("day?d2g="+then+"&offset=1");
            else:
                then = TimeStamp(d2g)
                body = """
                <title>{dayfilter}</title>
                <link rel="stylesheet" href="bootstrap/bootstrap.min.css">
                <link href="static/style.css" rel="stylesheet">
                <script>
                function dstr2date(dstr) {{ 
                    var year = timestamp.substr(0,4);
                    var month = timestamp.substr(4,2)-1;
                    var day = timestamp.substr(6,2);
                    var drdt = new Date(year,month,day,0,0,0,0);
                }}
                function oops(timestamp) {{
                    var temp = String(timestamp);
                    var tslc = temp.slice(0,8);
                    document.getElementById("d2g").text=tslc;
                    document.getElementById("offset").value=-1;
                    //window.location.replace("day?d2g="+tslc+"&offset=-1");
                    document.getElementById("nomen").submit();
                }}
                function goback(dstr) {{
                    var temp = String(dstr);
                    var ts = temp.slice(0,8);
                    document.getElementById("d2g").text=ts;
                    document.getElementById("offset").value=1;
                    //window.location.replace("day?d2g="+ts+"&offset=1");    
                    document.getElementById("nomen").submit();
                }}    
                </script>
                </head>
                <body>
                <a href="/">Home</a>&nbsp;
                <form name="nome" id="nomen" method="get" action="day">
                <input type="hidden" id="offset" name="offset">
                <input type="button" value="Previous" onclick="oops({dayfilter});">
                <label for="d2g">DATE: </label>
                <input type="text" id="d2g" name="d2g" value="{dayfilter}">
                <input type="button" value="Next" onclick="goback({dayfilter});">
                </form>            
                """
                bodylist = aday(d2g)            
                for line in bodylist:
                    body += line
                if type(then) == type(body):
                    return METAHDR+body.format(dayfilter=then)
                else:
                    return METAHDR+body.format(dayfilter=then.timestamp())
        else:
            body = """
            <title>Jef's Journal</title>
            <link rel="stylesheet" href="bootstrap/bootstrap.min.css">
            <link href="static/style.css" rel="stylesheet">
            </head>
            <body>
            <a href="/">Home</a>&nbsp;
            <form name="dome" id="dome" method="get" action="day">
            <input type="text" id="d2g" name="d2g">
            <input type="submit" value="Find">
            </form>
            """
            return METAHDR+body
            
    @cherrypy.expose
    def todo(self):
        body = ""
        body = body + "<form method=\"GET\" action='add'>"
        body = body + "<textarea rows=\"5\" cols=\"49\" name=\"entry\"></textarea>"
        body += "<input type=\"checkbox\" name=\"todo\"/>"
        body += "<button type=\"submit\">Enter</button>"
        body += "</form>"

        body += "<table><tr><th>timestamp</th><th><Entry></th></tr>"
        global BASEHTML, DLINE
        title = 'To do entries'
        journal, todo_dict, notebook = notes.load_journal()
        if todo_dict:
            for i in reversed(sorted(todo_dict.keys())):
                if todo_dict[i]==True and i in journal:
                    body = body + ELINE.format(DATETIME=journal[i].title, ENTRY=journal[i].entry)
        body = body + "</table>"
        return BASEHTML.format(journal=notebook.notebooks[notebook.current_notebook], TITLE=title, BODY=body, dayfilter=TimeStamp().daypart())

    @cherrypy.expose
    def choose_notebook(self):
        global BASEHTML
        title = "Available Notebooks"
        sumz = db.sumarize()
        #_, _, notebooks = notes.load_journal()
        body = """
        <form method="GET" action="pick_notebook">
        <select name="notebook_name">
        """
        x = 0
        for j in sumz:
            body = body + "<option value=\""+j[0]+"\">"+j[0]+'='+str(j[1])+"</option>"
            x = x + 1
        body = body + "</select><br><button type=\"submit\">Select</button></form>"
        body = body + "<form method=\"GET\" action=\"addnotebook\">"
        body = body + "<input type=\"text\" name=\"newname\"><button type=\"submit\" >Add</button>"
        body = body + "</form>"
        return BASEHTML.format(journal='journals', TITLE=title, BODY=body, dayfilter='')

    @cherrypy.expose
    def showtag(self,tag):
        Qrs = db.showtag(tag)
        html = """
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-store, must-revalidate">
        <title>{Titular}</title>
        <link rel="stylesheet" href="bootstrap/bootstrap.min.css">
        <link href="static/style.css" rel="stylesheet">
        </head>
        <body>
        <a href="/">Home</a>
        <h2>Notebook Name: {NotebookName}</h2>
        <hr>
        {bodyOfTags}
        </body>
        </html>
        """
        bot=""
        bot+="<div class=\"container\">"
        for iq in Qrs:            
            bot+="<div class=\"col-sm-3\">"
            bot+=iq[0]
            bot+="</div><div class=\"col-sm-9\">"
            bot+=iq[1]
            bot+="</div>"
        bot+="</div>"

        page=html.format(Titular=tag, NotebookName=tag, bodyOfTags=bot)
        return page


    @cherrypy.expose
    def edit(self, key):
        if key == '':
            return self.done()
        journal, _, notebooks = notes.load_journal()
        event = journal[key].entry.replace('""','"').replace("''","'")

        global BASEHTML
        title = "Editing {}".format(key)
        body = """
            <form method="GET" action="editkey">
            <textarea rows="5" cols="49" name="entry">{}</textarea>
            <input type="hidden" name="key" value="{}">
            <button type="submit">Save</button>
            </form>
        """
        form = body.format(event, key)
        return BASEHTML.format(journal=notebooks.notebooks[notebooks.current_notebook], TITLE=title, BODY=form, dayfilter='')

    @cherrypy.expose
    def summary(self):
        global BASEHTML, QLINE
        dictSummary = notes.summary()
        body = "<table><tr><th>Day</th><th>Count</th></tr>"
        keys = sorted(dictSummary.keys(), reverse=True)
        
        for key in keys:
            body += QLINE.format(DAYKEY=key,COUNT=dictSummary[key])
        body += "</table>"
        return BASEHTML.format(journal='hightlights', TITLE='Choose a day', BODY=body, dayfilter='')

    @cherrypy.expose
    def see(self, daykey):
        return "NYI <br> <a  href=\"/done\">Home</a>"

    @cherrypy.expose
    def sum(self):
        ds = notes.summary()
        countall = 0
        for key in ds.keys():
            countall += ds[key]
        return countall



    @cherrypy.expose
    def markdone(self, key):
        notes.mark_done(key)
        return self.todo()

    @cherrypy.expose
    def undo(self, key):
        notes.undo(key)
        return self.all()

    @cherrypy.expose
    def copy(self, key):
        eventcomplete = notes.copy(key)
        if eventcomplete is not None:
            notes.edit(key, eventcomplete)
        return self.done()

    @cherrypy.expose
    def search(self, term):
        global METAHDR, FLINE
        searches = notes.search(term)
        body = METAHDR
        body += """
        <body>
        <h5><a href="/">HOME</a></h5>
        <h1>Search Term</h1>
        <form method="GET" action="search">
        <label for="txt6">Search term</label>
        <input type="text" name="term" id="txt6" />
        <input type="submit" value="Submit" />
        </form>
        <table><tr><th>Day</th><th>Events</th></tr>
        """
        if searches:
            keys = sorted(searches.keys(), reverse=True)
        else:
            keys=[]
        
        for k in keys:
            body += FLINE.format(DATETIME=k, ENTRY=searches[k].entry)
        body += "</table></body></html>"
        return body

    @cherrypy.expose
    def upload(self):
        return """
            <html><body><h2>Upload</h2>
            <form action="_upload" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="myFile" /><br />
            <input type="submit" />
            </form></body></html>
        """

    @cherrypy.expose
    def pick_notebook(self, notebook_name):
        
        return self.showtag(notebook_name)

    @cherrypy.expose
    def addnotebook(self, newname):
        _, _, notebooks = notes.load_journal()
        notebooks.add(newname, newname+".tds")
        return self.index()

    @cherrypy.expose
    def editkey(self, entry, key):
        notes.edit(key, entry)
        return self.done()
    
    @cherrypy.expose
    def kill(self, key):
        notes.undo(key)
        return self.all()

    @cherrypy.expose
    def _upload(self, myFile):
        filename = os.path.join(os.path.join(os.path.abspath(os.getcwd()),'static'),myFile.filename)
        outfile=open(filename,'wb')
        outfile.write(myFile.file.read())
        return self.done()

    @cherrypy.expose
    def updateperiod(self,interval):
        with open("INTERVAL","wt") as put:
            print(interval, put)
        return ""
        #j= ''
        #for q in cherrypy.request.headers:
        #    j=j+'--'+q
        #return j

def favicon():
    weekdaynumber = datetime.date.weekday(datetime.datetime.now())
    weekdays = ['moon.jpg','teusday.jpg','odin.jpg','lightning.jpg','fiday.jpg','saturday.jpg','sunday.jpg']
    pathofavico = os.path.join(os.path.join(os.path.abspath(os.getcwd()),'static'),weekdays[weekdaynumber])
    return pathofavico


def run():    
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.caching.on': False,
#            'tools.auth_basic.on': True,
#            'tools.auth_basic.realm':'admin',
#            'tools.auth_basic.checkpassword':encrypt_pwd,
            'tools.staticdir.root': config._ROOT_DIR_
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': config._STATIC_DIR_
        },
        '/bootstrap': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': config._STATIC_DIR_+'bootstrap/css/'
        },
        '/favicon.ico':
        {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': favicon()
        }
    }

    with PidFile('server.pid') as spid:
        print(spid.pidname)
        print(spid.piddir)
        portNumber = config.port()
        cherrypy.config.update({'server.socket_host':'0.0.0.0', 'server.socket_port': portNumber,})
        cherrypy.quickstart(Notes(), '/', conf)


if __name__=="__main__":
    run()
