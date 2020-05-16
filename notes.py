"""notes.py is the logic/data for my todo list"""
import pickle
import os
import re
import dbstuff as db
from journalentry import JournalEntry
from timestamp import TimeStamp
import fire


class NotebookManager(object):
    """the notebook manager keeps track of the currently selected journal"""
    def __init__(self):
        """Initialize the notebook manager"""
        self.current_notebook = 0
        self.load_notebooks()

    def save_state(self):
        """Save the state of the object"""
        pickle.dump(self.notebooks, open('notebooks', 'wb'))
        pickle.dump(self.current_notebook, open('current', 'wb'))

    def load_notebooks(self):
        """Open up the selected journal"""
        if os.path.exists('notebooks'):
            self.notebooks = pickle.load(open('notebooks', 'rb'))
            if os.path.exists('current'):
                self.current_notebook = pickle.load(open('current', 'rb'))
            else:
                self.current_notebook = 0
                pickle.dump(self.current_notebook, open('current', 'wb'))
        else:
            self.notebooks = [('journal', 'todos')]
            self.current_notebook = 0
            pickle.dump(self.notebooks, open('notebooks', 'wb'))
            pickle.dump(self.current_notebook, open('current', 'wb'))

    def add(self, new_notebook, new_todolist):
        """Add a new notebook. This is
        what has to be modified so that
        the new notebook is in the DB land."""
        self.notebooks.append((new_notebook, new_todolist))
        pickle.dump(self.notebooks, open('notebooks', 'wb'))

    def set_current(self, horizon=7, notebook_list_number=None, filter=None):
        """ set_current preforms double duty.
            1. If there is an index from the options, use that option to
            set the current notebook.
            2. Pull the notebooks from the DB land.
        """
        
        if filter is None:
            filter = None
            lastday = None
        if filter:
            lastday = TimeStamp(filter).tomorrow()
            filter = TimeStamp(filter).lt(horizon)
        if notebook_list_number is not None:
            self.current_notebook = notebook_list_number
            self.save_state()
        (j, t) = self.notebooks[self.current_notebook]
        #if os.path.exists(j):
        #    journal = pickle.load(open(j,'rb'))
        #else:
            #if filter:
            #    dk = filter
            #else:
            #    dk = TimeStamp().daypart() if j == 'journal' else None
        journal = db.loadjournal(jname=j, daykey=filter, lastday=lastday)
        #if not os.path.exists(t):
        td = db.loadtodo(j)
        todo = td if td else None
        if todo is None and os.path.exists(t):
            todo = pickle.load(open(t,'rb'))
        else:
            todo = {}
        return (journal, todo)

    def save_current(self,journal, todo):
        current_journal_name, current_todo_name = self.notebooks[self.current_notebook]
        if os.path.exists(current_journal_name) and os.path.isfile(current_journal_name):
            print(current_journal_name)
            pickle.dump(journal, open(current_journal_name,'wb'))
        pickle.dump(todo, open(current_todo_name,'wb'))


def load_journal(filter=None):
    nm0 = NotebookManager()
    journal, todos = nm0.set_current(filter=filter)
    return journal, todos, nm0

def create_journal_entry(entry, time, interval):
    
    (journals, todos, nm0) = load_journal()
    (j, _) = nm0.notebooks[nm0.current_notebook]
    E=entry
    T=time
    jn0=JournalEntry(entry, time)
    if entry[0:7].lower()=="tag as ":
        exp = re.compile('^[a-z]+')
        tag = exp.match(entry[7:].lower())
        if tag:
            taggel = tag.group()[0:]
            lpit = len(taggel)+7
            tail = entry[lpit:]
            E = "#{} {}".format(taggel,tail)

    tag = tagextractor(E)
    if tag:
        if tag=='datetime':
            dt = E[10:24]
            E = E[25:]
            T=dt
        elif tag[0:3]=='dub':
            graphic=None
            container='<div style="height:100%;width:100%;display:flex">'
            picgrid = '<div style="display:inline-block;verticle-align:top;width:50%">'
            typ = tag[4:7]
            for _ in range(100):
                print(tag,typ)
            if typ=='img':
                graphic = '<img src="/static/{}" width="100%"/>'
            elif typ=='vid':
                graphic = '<video width="320" height="240" controls><source src="/static/{}" type="video/mp4">'
                graphic += 'Your browser sucks </video>'
            if graphic is not None:
                indexso = E.find('|!^^')                                 
                indexos = E.find('^^!|')
                namoing = E[indexso+4:indexos]
                verbage = E[indexos+4:]
                cloztag = '</div>'
                blockin = container+picgrid+graphic.format(namoing)+cloztag+verbage+cloztag+cloztag
                print(blockin)
                
                E = blockin
                T = time
            else:
                E='error adding --> '+entry
                T=time
        else:
            E = E[len(tag)+1:]
            T =time
    else:
        E=entry
        T=time
    print("{}:{}".format(E,T))
    if tag:
        suffix = tag[0].upper()
        newkey = jn0.title + suffix
        jnC = JournalEntry(entry=E, time=newkey)
        db.addentry(tag, jnC.title, jnC.entry, interval)
    jn0 = JournalEntry(entry=E, time=T)
    todos[jn0.title] = False
    journals[jn0.title] = jn0
    return db.addentry(j, jn0.title, jn0.entry, interval)
    #nm0.save_current(journals, todos)
        


def mark_done(key):
    (journal, todos, notebooks) = load_journal()
    (jornalname, _) = notebooks.notebooks[notebooks.current_notebook]
    rightnow = TimeStamp()
    elapsed_hours = rightnow.elapsed_hours(key)
    journal_entry = journal.pop(key)
    db.removeentry(key)
    journal_entry.title = rightnow.timestamp()
    old_entry = journal_entry.entry
    new_entry = "{}<br>@{}+{:.4f}".format(old_entry, key, elapsed_hours)
    journal_entry.entry = new_entry
    journal[journal_entry.title] = journal_entry
    db.updateentry(journal_entry.title, new_entry)
    db.addentry(jornalname, journal_entry.title, new_entry)
    todos.pop(key)
    notebooks.save_current(journal, todos)

def undo(key):
    (journal, todos, notebooks) = load_journal()
    #journal.pop(key)
    db.removeentry(key)
    if key in todos:
        todos.pop(key)
    notebooks.save_current(journal, todos)

def edit(key, value):
    (journal, todos, notebooks) = load_journal()
    if key in journal:
        journal[key].entry = value
        notebooks.save_current(journal, todos)
    db.updateentry(key, value)

def wordcloud(key):
    def isint(value):
        try:
            int(value)
            return True
        except:
            return False
    
    def isfloat(value):
        try:
            float(value)
            return True
        except:
            return False
    
    words = db.get_daily_words(key)
    word_list = words.split(" ")    
    word_cloud = {}
    for word in word_list:
        word = word.strip()
        if word == '':
            continue
        if isint(word):
            continue
        if isfloat(word):
            continue
        if len(word) < 3:
            continue
        if word in word_cloud:
            word_cloud[word]=word_cloud[word]+1
        else:
            word_cloud[word] = 1
    return word_cloud


def findimages():
    ilist={}
    je = db.listjournals()
    for key in sorted(je.keys()):
        if  '<img' in je[key]:
            ilist[key]=je[key]
    return ilist

def summary():
    return db.get_journal_summary()

def copy(key):
    tag = gettag(key)
    if tag:
        return db.copyto(key, tag)


def search(searchterm):
    return db.search(searchterm)


def gettag(key):
    entry = db.getentryfor(key)
    return tagextractor(entry)

def tagextractor(entry):
    expression = re.compile('#[a-z]+')
    tag = expression.match(entry)
    if tag:
        return tag.group()[1:]
    else:
        return None

if __name__ == "__main__":
    fire.Fire()

