import config
import sqlite3
import pickle
import re
from timestamp import TimeStamp
from journalentry import JournalEntry
import fire

#def importjournal(journalname):
"""
    conx = sqlite3.connect('journal.db')
    cursor = conx.cursor()
    cucumber = pickle.load(open(journalname, 'rb'))
    for itemkey in cucumber:
        item = cucumber[itemkey]
        entry = item.entry.replace("'","''").replace('"','""')
        sql_statement = " INSERT INTO journal VALUES('{}', "{}", '{}') "
        insert = sql_statement.format(item.title, entry, journalname)
        cursor.execute(insert)
    conx.commit()
    conx.close()
"""
#def importtodo(todoname):
"""We need a table to collect the todo stuff.
    Try key,  done,   completedon
    If an item is in this list and it's not marked as done then show it.
    If an item is marked as done then store the timestamp it was completed on
    """
"""    with sqlite3.connect('journal.db') as conx:
        tomato = pickle.load(open(todoname, 'rb'))
        cursor = conx.cursor()
        for key in tomato:
            todo = tomato[key]
            isdone = 1 if todo else 0
            sql = "INSERT INTO todo VALUES('{}', {}, NULL, '{}')".format(key, isdone, todoname)
            cursor.execute(sql)
        conx.commit()
"""
def addentry(journalname, daykey, entry, interval):
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        entry_cooked = entry.replace("'","''").replace('"','""')
        sql_statement = """INSERT INTO journal VALUES('{}','{}','{}')""".format(daykey, entry_cooked, journalname)
        rv=True
        try:
            cursor.execute(sql_statement)
            conx.commit()
        except:
            return False
        else:
            return True

def removeentry(daykey):
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        sql = "DELETE FROM journal WHERE title == '{}'".format(daykey)
        cursor.execute(sql)
        record = cursor.execute("SELECT journalid FROM period WHERE journalid == '{}'".format(daykey))
        if record is not None and (record is not [] or record is not {}):
            cursor.execute("DELETE FROM period WHERE journalid == '{}'".format(daykey))
        conx.commit()

def updateentry(timestamp, editedtext):
    with sqlite3.connect('journal.db') as conx:
        editedtext_cooked = editedtext.replace("'","''").replace('"','""')
        cursor = conx.cursor()
        sql = "UPDATE journal SET entry = '{}' WHERE title == {}".format(editedtext_cooked, timestamp)
        cursor.execute(sql)
        conx.commit()

def listjournals():
    alist = {}
    conx = sqlite3.connect('journal.db')
    cursor = conx.cursor()
    for row in cursor.execute('''SELECT * FROM journal ORDER BY title DESC'''):
        print(row[0], row[1])
        alist[row[0]]=row[1]
    conx.close()
    return alist

def loadjournal(jname, daykey=None, lastday=None):
    conx = sqlite3.connect('journal.db')
    cursor = conx.cursor()
    if daykey:
        selectquery = """SELECT title, entry FROM journal WHERE journal == '{}' AND title  BETWEEN '{}' AND '{}'"""
        filled = selectquery.format(jname, daykey, lastday)
        print("****************************************************************************************************")
        print(filled), 
        query = cursor.execute(filled)
    else:
        selectquery = """
        SELECT title, entry FROM journal WHERE journal == '{}'
        """
        query = cursor.execute(selectquery.format(jname))    
    myjournal = {}
    for row in query:
        title = row[0]
        entry = row[1]
        myjournal[title]=JournalEntry(entry, title)
    conx.close()
    return myjournal

def loadtodo(jname):
    if 1:
        return None
    with sqlite3.connect('journal.db') as conx:
        todo = {}
        sql = """
        SELECT key FROM todo WHERE journal == '{}' AND done == 1
        """
        query = sql.format(jname)
        cursor = conx.cursor()
        for row in cursor.execute(query):            
            if len(row)>0:
                todo[row[0]] = True
    if not todo:
        return None
    else:
        return None

def testloadjournal(jname, daykey):
    journal = loadjournal(jname, daykey)
    for jnote in journal:
        item = journal[jnote]
        print(item.entry)

def getjournalentry(key):
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        sql = """
        SELECT title, entry FROM journal WHERE title == {}
        """
        rows = cursor.execute(sql.format(key))
        je = rows.fetchone()
        if je:
            return JournalEntry(je[1],je[0])
        else:
            return None

def pop(key):
    je = getjournalentry(key)
    removeentry(key)
    return je

def istodo(key):
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        sql = """
        SELECT done FROM todo WHERE key == '{}' AND done == 1
        """
        query = sql.format(key)
        resultset = cursor.execute(query)
        result = resultset.fetchone()
        if result:
            return True
        else:
            return False

def get_journal_summary():
    sql = """
    SELECT dkey, count(dkey) AS ckeycc FROM (
        SELECT SUBSTR(title,1,8) as dkey, entry FROM journal
    ) as jophi 
    GROUP BY dkey
    ORDER BY dkey DESC
    """
    journal_highlight = {}
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        for row in cursor.execute(sql):
            key = row[0]
            count = row[1]
            journal_highlight[key] = count
    return journal_highlight

def get_daily_words(daykey):
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    sql = """
    SELECT entry FROM journal WHERE SUBSTR(title,1,8) = '{DK}'
    """
    query = sql.format(DK=daykey)
    words = ""
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        for row in cursor.execute(query):
            ytext = cleanhtml(row[0])
            ztext = ' '.join(ytext.splitlines())
            words += (" {} ".format(ztext)).lower().replace('<','').replace('>','').replace('.','').replace(',',' ').replace('"',' ').replace("'",'').replace('@',' ').replace('/','').replace('+','')
    return words

def search(search_term):
    sql = """
    SELECT title, entry FROM journal WHERE INSTR(LOWER(entry),'{0}')>0 AND journal LIKE 'journal'
    """
    query=sql.format(search_term.lower())
    myjournal = {}
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        execz = cursor.execute(query)
        for row in execz:
            title = row[0]
            entry = row[1]
            myjournal[title]=JournalEntry(entry, title)
    if myjournal:
        return myjournal
    else:
        return None
    

def copyto(daykey, journalname):
    today = TimeStamp()
    sql0 = """
    SELECT entry as entry FROM journal WHERE title LIKE '{}'
    """
    query0 = sql0.format(daykey)
    with sqlite3.connect('journal.db') as conz:
        cur = conz.cursor()
        execor = cur.execute(query0)
        for row in execor:
            entry = row[0]
    start = 1 + len(journalname)
    newentry = entry[start:]
    newkey = today.timestamp()    
    sql = """
    INSERT INTO journal VALUES('{}' , "{}" , '{}' )
    """
    query = sql.format(newkey, newentry, journalname )
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        cursor.execute(query)
    return newentry

def getentryfor(key):
    sql = """
    SELECT entry FROM journal WHERE title LIKE '{}'
    """
    query = sql.format(key)
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        cursor.execute(query)
        listo = cursor.fetchone()
        if listo:
            return listo[0]
        else:
            return None

def exportJournal(aftertime):
    fup = str(aftertime) +'.pic'
    sql = """
    SELECT * FROM journal WHERE title > '{}'
    """
    query=sql.format(aftertime)
    with sqlite3.connect('journal.db') as conx:
        cursor=conx.cursor()
        cursor.execute(query)
        exportlist = cursor.fetchall()
        pickle.dump(exportlist,open(fup, 'wb'))

def isin(key):
    sql = """
    SELECT title FROM journal WHERE title = {}
    """
    query =  sql.format(key)
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        cursor.execute(query)
        hattr = cursor.fetchone()
        return hattr is not None

def importfragment(fragment):
    jfrag = pickle.load(open(fragment,'rb'))
    for item in jfrag:
        (key, entry, book) = item
        if not isin(key):
            addentry(book,key,entry)

def undone_todos():
    undones={}
    todo_list = pickle.load(open('todos','rb'))
    for todo in todo_list:
        if todo_list[todo]:
            sql = "SELECT * FROM journal WHERE title = {}"
            query = sql.format(todo)
            with sqlite3.connect('journal.db') as conx:
                cursor = conx.cursor()
                cursor.execute(query)
                Record = cursor.fetchone()
                if Record is not None:
                    undones[Record[0]]=Record
    keys = undones.keys()
    for k in sorted(keys):
        print(undones[k])

def journal_names():
    Js = []
    SQL = """
    SELECT DISTINCT journal FROM journal ORDER BY journal ASC
    """
    with sqlite3.connect('journal.db') as Cn:
        cursor = Cn.cursor()
        records = cursor.execute(SQL)
        for record in records:
            record = record[0]
            if record == "journal":
                todo = 'todos'
            else:
                todo = "{}.tds".format(record)
            Tuple = (record,todo)
            Js.append(Tuple)
    return Js


def timeNoted(key):
  SQL = """
  SELECT * FROM journal WHERE title == {NewDay}
  """
  with sqlite3.connect('journal.db') as Cnx:
    cursor = Cnx.cursor()
    records = cursor.execute(SQL.format(NewDay=key))
    count=0
    for _ in records:
      count=count+1
    
    retval=True if count > 0 else False
    return retval

def count_entries(journalName):
    SQL = """
    SELECT COUNT(*) FROM journal WHERE journal == '{JournalToCount}'
    """
    with sqlite3.connect('journal.db') as CNX:
        cursor = CNX.cursor()
        records = cursor.execute(SQL.format(JournalToCount=journalName))
        (c,) = records.fetchone()
        return(c)
        
def sumarize():
    h = []
    listOfNames = journal_names()
    for L in listOfNames:
        name = L[0]
        h.append((name,count_entries(name)))
    return h

def showtag(name):
    SQL = """
    SELECT title, entry FROM journal WHERE journal == '{JournalName}'
    """
    with sqlite3.connect('journal.db') as cnx:
        cursor = cnx.cursor()
        records = cursor.execute(SQL.format(JournalName=name))
        x = records.fetchall()
    return x


def entries_between(fromdaky,todaky,jname='journal'):
    SQL= """
    SELECT title, entry FROM journal WHERE journal='{JournalName}' AND
           title > '{fromdaky}' AND title < '{stopdaky}'
    """
    Query = SQL.format(JournalName=jname,fromdaky=fromdaky,stopdaky=todaky)
    print(Query)
    with sqlite3.connect('journal.db') as conx:
        cursor = conx.cursor()
        records = cursor.execute(Query)
        period = records.fetchall()
    for day in period:
        print(day)


if __name__ == "__main__":
    fire.Fire()



