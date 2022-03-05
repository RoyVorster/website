#!/usr/bin/python3
import re, requests, gzip
from datetime import datetime, timedelta
from pathlib import Path

URL = re.escape('royvorster.nl')

# The big bad regex
visits = re.compile(r"(?:%s|www\.%s):\d{1,4} (?P<ip>(?:\d{1,3}\.){3}\d{1,3}) - - \[(?P<date>\S*):(?P<time>\d{2}:\d{2}:\d{2}) \S*\] \"GET / HTTP/1.1\" \d{1,4} \d{1,4} \"-\" \"(?P<os>.+)\"" % (URL, URL))

def parse_log():
    dat = []
    for path in Path('/var/log/apache2/').glob('other_vhosts_access*'):
        f_open = gzip.open if path.suffix == '.gz' else open

        with f_open(path, mode='rt') as f:
            dat.extend([l.strip() for l in f.readlines()])

    # Get matches
    matches = (visits.match(d) for d in dat)
    matches = [m for m in matches if m is not None]

    # Parse date and time
    dts = [datetime.strptime(f"{m['date']} {m['time']}", '%d/%b/%Y %H:%M:%S') for m in matches]
    dts = [dt + timedelta(hours=1) for dt in dts] # To my time

    # Parse date and time
    return [{**m.groupdict(), 'dt': dt} for (m, dt) in zip(matches, dts)]

# Quick helper for 'subnets'
def div_ip(ip, n=3):
    return '.'.join(ip.split('.')[:n])

if __name__ == '__main__':
    matches = parse_log()

    # Get unique IPs
    all_ips = [m['ip'] for m in matches]

    ips = list(set(all_ips))
    ips_grouped = [[m for m in matches if m['ip'] == ip] for ip in ips]

    dts = [max([g['dt'] for g in group]) for group in ips_grouped] # Get latest date associated with IP
    oss = [[g['os'] for g in group][0] for group in ips_grouped] # Get OS associated with IP

    # And sort by date
    data = [{'dt': dt, 'ip': ip, 'os': os} for dt, ip, os in sorted(zip(dts, ips, oss))]

    # Just for fun, get some locations on the most recent ones
    loc_requests = [{"query": d['ip']} for d in data[-100:]] # API only allows 100
    locs = [f"({loc['country']}, {loc['city']})" for loc in requests.post("http://ip-api.com/batch", json=loc_requests).json()]

    idx_diff = len(data) - len(locs)
    data = [{**d, 'loc': "" if i <= idx_diff else locs[i - idx_diff]} for i, d in enumerate(data)]

    # Add ip counts
    data = [{**d, 'n': all_ips.count(d['ip'])} for d in data]

    # And sub ip counts
    data = [{**d, 'nsub': sum([int(ip.startswith(div_ip(d['ip']))) for ip in all_ips])} for d in data]

    # And pretty print
    s = '\n'.join([f"{d['dt'].strftime('%d %b %Y - %H:%M')}: {d['ip']} ({d['n']} hits, {d['nsub']} on subnet {div_ip(d['ip'])}), ({d['os']}) {d['loc']}" for d in data])
    s += f"\n\nTotal of {len(ips)} unique IP addresses"

    print(s)
