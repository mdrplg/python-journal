import os
owd = os.getcwd()
os.chdir('jefe/')
import dbstuff
from journalentry import JournalEntry
import fire



def doit():
		mj = dbstuff.loadjournal('journal',daykey='20190227000000', lastday='20190305999999')
		for key in mj:
			data=mj[key]
			print(data)

if __name__ == '__main__':
	fire.Fire()
	os.chdir(owd)
