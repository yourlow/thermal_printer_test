from datetime import datetime
import pytz

def convert_utc_to_sydney(utc_time_str):
    try:
        utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_time = utc_time.replace(tzinfo=pytz.UTC)
        sydney_tz = pytz.timezone('Australia/Sydney')
        sydney_time = utc_time.astimezone(sydney_tz)
        return sydney_time.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    except:
        return "unknown"

  