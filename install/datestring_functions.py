import datetime

def datestring(datetime_datetime):
    """
    Given a datetime.datetime, returns the current time in the format 
    YmdHMSf:
    Y: Year
    m: month (2 places)
    d: day (2 places)
    H: hour (2 places)
    M: minute (2 places)
    S: second (2 places)
    f: microsecond (6 places)
    Raises a TypeError if datetime_datetime is not a datetime.datetime object

    Parameters:
        1. datetime_datetime: A datetime.datetime object.
    """
    if (datetime_datetime is not datetime.datetime):
        raise TypeError("In function \"datestring\": %s is not a datetime object." % datetime_datetime)
    else:
       now = datetime_datetime.now()
       time = now.strftime("%Y%m%d%H%M%S%f")
       return time
