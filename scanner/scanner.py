from scapy.all import *
import sys
conf.verb = 0

def load_ports_from_file(filename):
    ports_file = open("./nmap-top1000.txt")
    ports = ports_file.read().split(",")
    return [int(port) for port in ports]

def is_ping_reply(ping):
    return ping[1][ICMP].type == 0

def is_tcp_synack(packet):
    return packet[1][TCP].flags == "SA"

if len(sys.argv) != 2:
    print("potrzebne 2 argumenty")

target = sys.argv[1]

print("[+] Stage: Host discovery")
pings, unans = sr(IP(dst=target)/ICMP(), timeout = 2)

hosts = []
for ping in pings:
    if is_ping_reply(ping) == False:
        continue
    hosts.append({
        "ip": ping[0].dst,
        "services": []
    })

print("[+] Stage: Service discovery")

nmap_top1000_int = load_ports_from_file("./nmap-top1000.txt")

for host in hosts:
    tcp_results, unans = sr(IP(dst=host["ip"])/TCP(dport=nmap_top1000_int), timeout = 1)
    print(f'Host: {host["ip"]}')
    for tcp_conn in tcp_results:
        if is_tcp_synack(tcp_conn) == False:
            continue
        host["services"].append(tcp_conn[0][TCP].dport)
        print(f"\t- Open port: {tcp_conn[0][TCP].dport}")