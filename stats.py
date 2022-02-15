#!/usr/bin/python3
import re, requests
from datetime import datetime

LOG_FILE = '/var/log/apache2/other_vhosts_access.log' 
URL = 'www.royvorster.nl'

# Get locations for final 5 IP addresses, can't get all due to request speed
N_LOCS = 20

# The big bad regex
visits = re.compile(r"%s:\d{1,4} (?P<ip>(?:\d{1,3}\.){3}\d{1,3}) - - \[(?P<date>\S*):(?P<time>\d{2}:\d{2}:\d{2}) \S*\] \"GET / HTTP/1.1\" \d{1,4} \d{1,4} \"-\" \"(?P<os>.+)\"" % re.escape(URL))

def ip_loc(ip):
    loc = requests.get(f"https://geolocation-db.com/json/{ip}&position=true").json()
    return f"({loc['city']}, {loc['country_name']})"

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

    # Get unique IPs
    ips = list(set([m['ip'] for m in matches]))
    ips_grouped = [[m for m in matches if m['ip'] == ip] for ip in ips]

    dts = [max([g['dt'] for g in group]) for group in ips_grouped] # Get latest date associated with IP
    oss = [[g['os'] for g in group][0] for group in ips_grouped] # Get OS associated with IP

    # And sort by date
    data = [{'dt': dt, 'ip': ip, 'os': os} for dt, ip, os in sorted(zip(dts, ips, oss))]

    # Just for fun, get some locations on the most recent ones
    locs = [ip_loc(d['ip']) for d in data[-N_LOCS:]]
    locs = [""]*(len(data) - len(locs)) + locs

    data = [{**d, 'loc': loc} for d, loc in zip(data, locs)]

    # And pretty print
    s = '\n'.join([f"{d['dt'].strftime('%d %b %Y - %H:%M')}: {d['ip']} ({d['os']}) {d['loc']}" for d in data])
    s += f"\n\nTotal of {len(ips)} unique IP addresses"

    print(s)
