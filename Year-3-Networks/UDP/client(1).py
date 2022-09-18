import hashlib
import socket
import os
import signal
import struct
import sys
import argparse
import time
from urllib.parse import urlparse
import selectors

# Define a constant for our buffer size

BUFFER_SIZE = 1024

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# User name for tagging sent messages.

user = ''

# Signal handler for graceful exiting.  Let the server know when we're gone.

address = ''

MAX_STRING_SIZE = 512

# this number gets changed to 1 after it gets the ack with seq 0
# changes back to 0 in the same way
exp_seq = 0

# keep track of the last message in case of retransmission
last_message = ""

# IF waiting for ACK, true, else false
waiting_ack = False

# IF sent ACK, false, else True
sent_ack = True

# IF sent file chunk True, else False
sent_file = True


def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message = f'DISCONNECT {user} CHAT/1.0\n'
    send_message(message, address)
    sys.exit(0)


# Simple function for setting up a prompt for the user.


def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)


# Read a single line (ending with \n) from a socket and return it.
# We will strip out the \r and the \n in the process.

# Function to send a chunk from a file
def send_file(chunk):
    global exp_seq
    global last_message
    global waiting_ack
    global sent_file
    chunk_tuple = (chunk, exp_seq)
    chunk_packer = struct.Struct(f'{MAX_STRING_SIZE}s i')
    chunk_packet = chunk_packer.pack(*chunk_tuple)
    # compute checksum for the values of the packet
    checksum = bytes(hashlib.md5(chunk_packet).hexdigest(), encoding="UTF-8")

    chunk_tuple = (chunk, exp_seq, checksum)
    # packet contains a max of a 512 byte object, integer and another 32 bytes
    chunk_packer = struct.Struct(f'{MAX_STRING_SIZE}s i 32s')
    chunk_packet = chunk_packer.pack(*chunk_tuple)
    client_socket.sendto(chunk_packet, address)
    sent_file = True  # have now sent a file
    poss_ack = get_ack(client_socket)  # get the ACK for this chunk
    last_message = chunk
    waiting_ack = True  # received chunk
    if poss_ack:
        # change up the sequence number for the next packets
        if exp_seq == 0:
            exp_seq = 1
        else:
            exp_seq = 0
        return
    else:
        # no ACK, timeout to retransmit
        sent_file = True
        time.sleep(2)
        return


# function to receive a message from the server
def get_line_from_socket(sock):
    received_packet, addr = sock.recvfrom(BUFFER_SIZE)
    unpacker = struct.Struct(f'{MAX_STRING_SIZE}s i i 32s')
    UDP_packet = unpacker.unpack(received_packet)
    # extract values to compute checksum
    received_message = UDP_packet[0]
    received_size = UDP_packet[1]
    received_seq = UDP_packet[2]
    received_check = UDP_packet[3]

    test_tuple = (received_message, received_size, received_seq)
    test_packer = struct.Struct(f'{MAX_STRING_SIZE}s i i')
    test_packet = test_packer.pack(*test_tuple)
    checksum = bytes(hashlib.md5(test_packet).hexdigest(), encoding="UTF-8")
    # if checksum is the same, we can return this packet
    if checksum == received_check:
        return UDP_packet
    else:
        return


# Funciton to send acknowledgement
def send_ack():
    global exp_seq
    global last_message
    global sent_ack
    ack_tuple = ("RECEIVED MESSAGE".encode(), 16, exp_seq)
    ack_packer = struct.Struct("16s i i")
    ack_packet = ack_packer.pack(*ack_tuple)
    checksum = bytes(hashlib.md5(ack_packet).hexdigest(), encoding="UTF-8")

    ack_tuple = ("RECEIVED MESSAGE".encode(), 16, exp_seq, checksum)
    ack_packer = struct.Struct("16s i i 32s")
    ack_packet = ack_packer.pack(*ack_tuple)
    # set last_message to ACK so it is known that an ACK was sent
    last_message = "ACK"
    client_socket.sendto(ack_packet, address)
    sent_ack = True  # indicate that we have now sent an acknowledgment
    if exp_seq == 0:
        exp_seq = 1
    else:
        exp_seq = 0


# Function to handle incoming messages from server.  Also look for disconnect
# messages to shutdown and messages for sending and receiving files.
def handle_message_from_server(sock, mask):
    global exp_seq
    global sent_ack
    packet = get_line_from_socket(sock)
    size = packet[1]
    message = packet[0].decode()[:size]  # message is not the whole thing, smaller
    words = message.split(' ')
    print()
    if registered:
        send_ack()
    elif not packet:
        sent_ack = False
        time.sleep(2)
        return

    # Handle server disconnection.

    if words[0] == 'DISCONNECT':
        print('Disconnected from server ... exiting!')
        sys.exit(0)

    # Handle file attachment request.

    elif words[0] == 'ATTACH':
        filename = words[1]
        if (os.path.exists(filename)):
            filesize = os.path.getsize(filename)
            header = f'Content-Length: {filesize}\n'
            send_message(header, address)  # send header content
            with open(filename, 'rb') as file_to_send:
                while True:
                    chunk = file_to_send.read(MAX_STRING_SIZE)
                    if chunk:
                        send_file(chunk)
                    else:
                        break
        else:
            header = f'Content-Length: -1\n'
            send_message(header, address)

    # Handle file attachment request.

    elif words[0] == 'ATTACHMENT':
        filename = words[1]
        sock.setblocking(True)
        print(f'Incoming file: {filename}')
        origin = get_line_from_socket(sock)[0]
        print(origin)
        contentlength = get_line_from_socket(sock)[0]
        print(contentlength)
        length_words = contentlength.split(' ')
        if (len(length_words) != 2) or (length_words[0] != 'Content-Length:'):
            print('Error:  Invalid attachment header')
        else:
            bytes_read = 0
            bytes_to_read = int(length_words[1])
            with open(filename, 'wb') as file_to_write:
                while (bytes_read < bytes_to_read):
                    chunk = sock.recv(BUFFER_SIZE)  # get the chunk
                    bytes_read += len(chunk)  # increment byte counter
                    file_to_write.write(chunk)  # write to file
        do_prompt()

    # Handle regular messages.

    else:
        print(message)
        do_prompt()


# function to get acknowledgement from sender
def get_ack(sock):
    global waiting_ack
    ack_packet, addr = sock.recvfrom(BUFFER_SIZE)
    # ACK is of 16 bytes, integer for size, integer for sequence  number and
    # chekcsum
    ack_unpacker = struct.Struct('16s i i 32s')
    ack_tuple = ack_unpacker.unpack(ack_packet)

    ack = ack_tuple[0]
    size = ack_tuple[1]
    seq = ack_tuple[2]
    check_tup = (ack, size, seq)

    check_tup_packer = struct.Struct('16s i i')
    check_pack = check_tup_packer.pack(*check_tup)
    checksum = bytes(hashlib.md5(check_pack).hexdigest(), encoding="UTF-8")
    # verify check sum
    if checksum == ack_tuple[3]:
        waiting_ack = False  # received the ack therefore this can go to false
        return ack
    else:
        return ""


# Function for UDP socket to send a message
def send_message(message, address):
    global exp_seq
    global last_message
    global waiting_ack
    packet_tuple = (message.encode(), len(message), exp_seq)
    packet_struct = struct.Struct(f'{MAX_STRING_SIZE}s i i')
    packet = packet_struct.pack(*packet_tuple)
    checksum = bytes(hashlib.md5(packet).hexdigest(), encoding="UTF-8")

    # package the data into a tuple to be sent
    packet_tuple = (message.encode(), len(message), exp_seq, checksum)
    packet_struct = struct.Struct(f'{MAX_STRING_SIZE}s i i 32s')
    packet = packet_struct.pack(*packet_tuple)
    client_socket.sendto(packet, address)
    last_message = message
    waiting_ack = True  # we are now waiting for an ACK
    poss_ack = get_ack(client_socket)
    # if we got an ack, then we can change the sequence numbers
    if poss_ack:
        if exp_seq == 0:
            exp_seq = 1
        else:
            exp_seq = 0
        return
    else:
        # timeout because of no acknowledgement / wrong sequence number ack
        time.sleep(2)


# Function to handle incoming messages from server.
def handle_keyboard_input(file, mask):
    line = sys.stdin.readline()
    message = f'@{user}: {line}'
    send_message(message[:-1], address)
    do_prompt()


# Our main function.
def main():
    global user
    global client_socket
    global address
    global registered
    global exp_seq

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("user",
                        help="user name for this user on the chat service")
    parser.add_argument("server",
                        help="URL indicating server location in form of chat://host:port")
    parser.add_argument('-f', '--follow', nargs=1, default=[],
                        help="comma separated list of users/topics to follow")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    try:
        server_address = urlparse(args.server)
        if ((server_address.scheme != 'chat') or (
                server_address.port == None) or (
                server_address.hostname == None)):
            raise ValueError
        host = server_address.hostname
        port = server_address.port
    except ValueError:
        print(
            'Error:  Invalid server.  Enter a URL of the form:  chat://host:port')
        sys.exit(1)
    user = args.user
    follow = args.follow

    # UDP doesn't do connecting to server nonsense
    registered = False

    print('Connection to server established. Sending intro message...\n')
    message = f'REGISTER {user} CHAT/1.0\n'
    address = (host, port)
    send_message(message, address)
    # If we have terms to follow, we send them now.  Otherwise, we send an empty
    # line to indicate we're done with registration.

    # Receive the response from the server and start taking a look at it

    response_packet = get_line_from_socket(client_socket)
    if not response_packet:
        time.sleep(2)
    else:
        send_ack()
    response_line = response_packet[0].decode()
    response_list = response_line.split(' ')

    # If an error is returned from the server, we dump everything sent and
    # exit right away.

    if response_list[0] != '200':
        print(
            'Error:  An error response was received from the server.  Details:\n')
        print(response_line)
        print('Exiting now ...')
        sys.exit(1)
    else:
        print('Registration successful.  Ready for messaging!')

    # Set up our selector.

    client_socket.setblocking(True)
    sel.register(client_socket, selectors.EVENT_READ,
                 handle_message_from_server)
    sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)
    registered = True

    # Prompt the user before beginning.

    do_prompt()

    # Now do the selection.

    while (True):
        events = sel.select(timeout=2)
        if not events:
            # retransmit normal message
            if last_message != "ACK" and waiting_ack and type(message) == type(str):
                send_message(last_message, address)
            # retransmit ack
            elif last_message == "ACK" and not sent_ack:
                send_ack()
            # retransmit file chunk
            elif not sent_file and last_message != "ACK":
                send_file(last_message)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


if __name__ == '__main__':
    main()
