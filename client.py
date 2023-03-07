import socket
import time
import argparse


def runTCPStopWait(HOST, PORT, BUFFER_SIZE, MESSAGE_SIZE):
    sent_bytes = 0
    number_of_messages = 0
    data = b'0' * MESSAGE_SIZE
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(MESSAGE_SIZE.to_bytes(8, byteorder='big'))
    start_time = time.time()
    while sent_bytes < MESSAGE_SIZE:
        bytes_to_send = min(BUFFER_SIZE, MESSAGE_SIZE - sent_bytes)
        client_socket.send(data[sent_bytes:sent_bytes+bytes_to_send])
        sent_bytes += bytes_to_send
        number_of_messages += 1
        response = client_socket.recv(BUFFER_SIZE)
        while response != b'OK':
            client_socket.send(data[sent_bytes-bytes_to_send:sent_bytes])
            response = client_socket.recv(BUFFER_SIZE)
    elapsed_time = time.time() - start_time
    print(
        f"Time: {elapsed_time}, Messages sent: {number_of_messages}, Bytes sent: {sent_bytes}")
    client_socket.close()


def runTCPStreaming(HOST, PORT, BUFFER_SIZE, MESSAGE_SIZE):
    sent_bytes = 0
    number_of_messages = 0
    data = b'0' * MESSAGE_SIZE
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(MESSAGE_SIZE.to_bytes(8, byteorder='big'))
    start_time = time.time()
    while sent_bytes < MESSAGE_SIZE:
        bytes_to_send = min(BUFFER_SIZE, MESSAGE_SIZE - sent_bytes)
        client_socket.send(data[sent_bytes:sent_bytes+bytes_to_send])
        sent_bytes += bytes_to_send
        number_of_messages += 1
    response = client_socket.recv(BUFFER_SIZE)
    elapsed_time = time.time() - start_time
    print(
        f"Time: {elapsed_time}, Messages sent: {number_of_messages}, Bytes sent: {sent_bytes}")
    client_socket.close()


def runUDPStopWait(HOST, PORT, BUFFER_SIZE, MESSAGE_SIZE):
    sent_bytes = 0
    number_of_messages = 0
    data = b'0' * MESSAGE_SIZE
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()
    for i in range(0, len(data), BUFFER_SIZE):
        chunk = data[i:i+BUFFER_SIZE]
        while True:
            client_socket.sendto(chunk, (HOST, PORT))
            sent_bytes += len(chunk)
            number_of_messages += 1
            response, server_address = client_socket.recvfrom(BUFFER_SIZE)
            if response == b"ACK":
                break
        time.sleep(0.01)
    elapsed_time = time.time() - start_time
    client_socket.sendto(b'done', (HOST, PORT))
    print(
        f"Time: {elapsed_time}, Messages sent: {number_of_messages}, Bytes sent: {sent_bytes}")
    client_socket.close()


def runUDPStreaming(HOST, PORT, BUFFER_SIZE, MESSAGE_SIZE):
    received_bytes = 0
    number_of_messages = 0
    data_to_send = b'0' * MESSAGE_SIZE
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()
    for i in range(0, MESSAGE_SIZE, BUFFER_SIZE):
        packet = data_to_send[i:i+BUFFER_SIZE]
        client_socket.sendto(packet, (HOST, PORT))
        number_of_messages += 1
        received_bytes += len(packet)
    elapsed_time = time.time() - start_time
    client_socket.sendto(b'done', (HOST, PORT))
    print(
        f"Time: {elapsed_time}, Messages sent: {number_of_messages}, Bytes sent: {received_bytes}")
    client_socket.close()


def main():

    runTCPStopWait('localhost', 1235, 32500, 1000 * 1024 * 1024)
    # runTCPStreaming('localhost', 1235, 32500, 50 * 1024 * 1024)
    runUDPStopWait('localhost', 1235, 32500, 1000 * 1024 * 1024)
    runUDPStreaming('localhost', 1235, 32500, 1000 * 1024 * 1024)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Server')
    parser.add_argument('-c', '--connection', type=str, choices=[
                        'TCP', 'UDP'], required=True, help='Conexion type: TCP or UDP')
    parser.add_argument('-ip', '--ip_address', type=str,
                        required=True, help='IP address of the server')
    parser.add_argument('-p', '--port', type=int, required=True,
                        help='PORT of the server')
    parser.add_argument('-t', '--transfer_mode', type=str, choices=[
                        'streaming', 'stop-and-wait'], required=True, help='Transfer mechanism: streaming or stop-and-wait')
    parser.add_argument('-b', '--buffer', type=int, required=True,
                        help='The size of buffer')
    parser.add_argument('-m', '--message_size', type=int,
                        required=True, help='The size of the message')
    args = parser.parse_args()

    if args.connection == 'TCP':
        protocol = 'TCP'
        if args.transfer_mode == 'streaming':
            runTCPStreaming(args.ip_address, args.port,
                            args.buffer, args.message_size)
        elif args.transfer_mode == 'stop-and-wait':
            runTCPStopWait(args.ip_address, args.port,
                           args.buffer, args.message_size)
    elif args.connection == 'UDP':
        protocol = 'UDP'
        if args.transfer_mode == 'streaming':
            runUDPStreaming(args.ip_address, args.port,
                            args.buffer, args.message_size)
        elif args.transfer_mode == 'stop-and-wait':
            runUDPStopWait(args.ip_address, args.port,
                           args.buffer, args.message_size)
