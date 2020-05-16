
def aNewDay():
  import datetime
  import dbstuff as db
  import timestamp as ts
  rightNow = datetime.datetime.now()
  dow = rightNow.weekday()
  if dow == 0:
    filename='monday.jpg'
  elif dow==1:
    filename='teusday.jpg'
  elif dow==2:
    filename = 'odin.jpg'
  elif dow==3:
    filename='lightning.jpg'
  elif dow==4:
    filename='friday.jpg'
  elif dow==5:
    filename='saturday.jpg'
  elif dow==6:
    filename='sunday.jpg'
  else:
    filename='wheel.jpg'
  imgTag = '<img src="static/{picname}" width="25%" align="center"/>'
  imgLine = imgTag.format(picname=filename)
  timetag=rightNow.strftime("%A, %b %d, %Y")
  outstr = """
  <h2> Good morning it is {daytag} </h2>
  {pictag}
  """

  myStamp = ts.TimeStamp()
  newDay = myStamp.daypart() + "000000"
  if db.timeNoted(newDay):
    db.removeentry(newDay)
  db.addentry('journal',newDay,outstr.format(daytag=timetag,pictag=imgLine),"-----")

if __name__=="__main__":
  aNewDay()
 
   
