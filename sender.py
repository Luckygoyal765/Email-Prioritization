import socket
import json
import random  

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
WINDOW_SIZE = 4
TIMEOUT = 2 
PACKET_COUNT = 10

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender_socket.settimeout(TIMEOUT)

base = 0
next_seq_num = 0
packets = [
    json.dumps({"SeqNum": i, "Size": 1024, "Data": f"Packet {i}"}).encode('utf-8')
    for i in range(PACKET_COUNT)
]

while base < PACKET_COUNT:
    while next_seq_num < base + WINDOW_SIZE and next_seq_num < PACKET_COUNT:
        if random.random() > 0.2:  
            sender_socket.sendto(packets[next_seq_num], (SERVER_IP, SERVER_PORT))
            print(f"Sent: Packet {next_seq_num}")
        else:
            print(f"Packet {next_seq_num} lost (simulated).")
        next_seq_num += 1

    try:
        response, _ = sender_socket.recvfrom(1024)
        ack = json.loads(response.decode('utf-8'))
        print(f"Received ACK: {ack['ACKNum']}, Advertised Window: {ack['AdvertisedWindow']}")

        base = max(base, ack['ACKNum'] + 1)
    except socket.timeout:
        print("Timeout detected! ARQ triggered: Resending packets in the window...")
        next_seq_num = base

print("All packets sent and acknowledged.")
sender_socket.close()
