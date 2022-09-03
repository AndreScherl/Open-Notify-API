import redis
import json
import requests
from datetime import datetime
from calendar import timegm
import os
import sys

REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r = redis.StrictRedis.from_url(REDIS_URL)

# NASA's station FDO updates this page with very precise data. Only using a
# small bit of it for now.
url = "https://api.wheretheiss.at/v1/satellites/25544/tles"


def update_tle():
    hdrs = {'User-Agent': 'Mozilla / 5.0 (X11 Linux x86_64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 52.0.2743.116 Safari / 537.36'}    
    response = requests.get(url, headers=hdrs)
    data = json.loads(response.content)

    tletime = datetime.fromtimestamp(data["tle_timestamp"])
    timeofrequest = datetime.fromtimestamp(data["requested_timestamp"])

    tle = json.dumps([data["header"], data["line1"], data["line2"]])

    r.set("iss_tle", tle)
    r.set("iss_tle_time", timegm(tletime.timetuple()))
    r.set("iss_tle_last_update", timegm(timeofrequest.timetuple()))


if __name__ == '__main__':
    print("Updating ISS TLE from JSC...")
    try:
        update_tle()
    except:
        exctype, value = sys.exc_info()[:2]
        print("Error:", exctype, value)
