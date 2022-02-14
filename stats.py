#!/usr/bin/python3
import re
from datetime import datetime

LOG_FILE = '/var/log/apache2/other_vhosts_access.log' 
URL = 'www.royvorster.nl'

# The big bad regex
visits = re.compile(r"%s:\d{1,4} (?P<ip>(?:\d{1,3}\.){3}\d{1,3}) - - \[(?P<date>\S*):(?P<time>\d{2}:\d{2}:\d{2}) \S*\]" % re.escape(URL))

def parse_log():
    with open(LOG_FILE, 'r') as f:
        dat = [l.strip() for l in f.readlines()]

    # Get matches
    matches = (visits.match(d) for d in dat)
    matches = [m for m in matches if m is not None]

    # Parse date and time
    return [{**m.groupdict(), 'dt': datetime.strptime(f"{m['date']} {m['time']}", '%d/%b/%Y %H:%M:%S')} for m in matches]

if __name__ == '__main__':
    matches = parse_log()

    # Get unique IPs and corresponding latest dates
    ips = list(set([m['ip'] for m in matches]))
    dts = [max([m['dt'] for m in matches if m['ip'] == ip]) for ip in ips]

    # And sort by date
    ips = [(dt, ip) for dt, ip in sorted(zip(dts, ips))]

    # And pretty print
    s = '\n'.join([f"{d[0].strftime('%m %b %Y - %H:%M')}: {d[1]}" for d in ips])
    s += f"\n\nTotal of {len(ips)} unique IP addresses"

    print(s)
