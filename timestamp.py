import datetime
import pandas
import fire

class TimeStamp(object):
    """A Timestamp"""
    def __init__(self, for_timestamp=None):
        self.this_datetime=datetime.datetime.now()
        """Initializes the timestamp to either the current date or the given day"""
        if for_timestamp is not None:
            if len(for_timestamp)==8:
                self.this_datetime = datetime.datetime.strptime(for_timestamp+"000000","%Y%m%d000000")
            elif len(for_timestamp)==14:
                self.this_datetime = datetime.datetime.strptime(for_timestamp, "%Y%m%d%H%M%S")
            else:
                self.this_datettime = datetime.datetime.now()
        else:
            self.this_datetime = datetime.datetime.now()

    def timestamp(self):
        """the timestamp"""
        return datetime.datetime.strftime(self.this_datetime, format="%Y%m%d%H%M%S")

    def daypart(self):
        """just the day part of the timestamp"""
        return datetime.datetime.strftime(self.this_datetime, format="%Y%m%d")

    def lt(self, ran):
        """return the timestamp exactly 'ran' days before today"""
        delta = datetime.timedelta(days=ran)
        earlier = self.this_datetime - delta
        return datetime.datetime.strftime(earlier,format="%Y%m%d%H%M%S")
        
    def yesterday(self):
        delta = datetime.timedelta(days=1)
        yesterday = self.this_datetime - delta;
        return datetime.datetime.strftime(yesterday,format="%Y%m%d%H%M%S")

    def tomorrow(self):
        delta = datetime.timedelta(days=1)
        tomorrow=self.this_datetime + delta
        return datetime.datetime.strftime(tomorrow,format="%Y%m%d%H%M%S")

    def elapsed_hours(self, to_timestamp):
        """how many hours between timestamps"""
        stime = str(to_timestamp)
        start_date = TimeStamp(stime)
        diff = self.this_datetime - start_date.this_datetime
        return diff.total_seconds() / 3600

    def elapsed_time(self):
        ahora = datetime.datetime.now()
        diff = ahora - self.this_datetime
        return str(diff)

def daterange(fromTimeStamp):
    today = pandas.datetime.today()
    delta = today-fromTimeStamp.this_datetime
    sd=fromTimeStamp.this_datetime.strftime("%Y/%m/%d")
    #print(sd)
    DR = pandas.date_range(sd, periods=delta.days, freq='D')
    return DR

def dates(fromdate,todate):
    fd = TimeStamp(str(fromdate))
    td = TimeStamp(str(todate))
    delta = td.this_datetime - fd.this_datetime
    sd = fd.this_datetime.strftime("%Y/%m/%d")
    DR = pandas.date_range(sd,periods=delta.days, freq='D')
    RV = []
    for R in DR:
        RV.append(R)
    return DR



if __name__ == "__main__":
    fire.Fire()
