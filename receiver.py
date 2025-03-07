import socket
import json

RECEIVER_IP = "127.0.0.1"
RECEIVER_PORT = 12345
BUFFER_SIZE = 4  
PACKET_COUNT = 10  

receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind((RECEIVER_IP, RECEIVER_PORT))

buffer = {}
expected_seq_num = 0

print("Receiver ready to receive packets.")

while True:
    packet, sender_address = receiver_socket.recvfrom(1024)
    data = json.loads(packet.decode('utf-8'))
    seq_num = data['SeqNum']

    if seq_num == expected_seq_num:
        print(f"Received: {data['Data']}")
        buffer[seq_num] = data
        expected_seq_num += 1

        while expected_seq_num in buffer:
            expected_seq_num += 1

        ack = {
            "ACKNum": expected_seq_num - 1,
            "AdvertisedWindow": BUFFER_SIZE - len(buffer),
        }
        receiver_socket.sendto(json.dumps(ack).encode('utf-8'), sender_address)
        print(f"Sent ACK for Packet {expected_seq_num - 1}")
    elif seq_num > expected_seq_num and len(buffer) < BUFFER_SIZE:
        print(f"Buffered out-of-order packet: {seq_num}")
        buffer[seq_num] = data

        ack = {
            "ACKNum": expected_seq_num - 1,
            "AdvertisedWindow": BUFFER_SIZE - len(buffer),
        }
        receiver_socket.sendto(json.dumps(ack).encode('utf-8'), sender_address)
        print(f"Sent ACK for Packet {expected_seq_num - 1}")
    else:
        print(f"Discarded packet {seq_num} (buffer full or out of range).")
        ack = {
            "ACKNum": expected_seq_num - 1,
            "AdvertisedWindow": BUFFER_SIZE - len(buffer),
        }
        receiver_socket.sendto(json.dumps(ack).encode('utf-8'), sender_address)
        print(f"Sent ACK for Packet {expected_seq_num - 1}")

    if expected_seq_num == PACKET_COUNT:
        print("All packets received.")
        break

receiver_socket.close()
