import hashlib
import socket
import os
import datetime
import signal
import sys
import selectors
import struct
import time
from string import punctuation

# Constant for our buffer size

BUFFER_SIZE = 1024

MAX_STRING_SIZE = 512

# Selector for helping us select incoming data and connections from multiple sources.

sel = selectors.DefaultSelector()

# Client list for mapping connected clients to their connections.

client_list = []

# Signal handler for graceful exiting.  We let clients know in the process so
# they can disconnect too.

# ACK
ACK = "RECEIVED MESSAGE"

exp_seq = 0

waiting_ack = False

sent_ack = True

last_message = ''

# since we are working with only one client, keep track of this address
address = ''


def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message='DISCONNECT CHAT/1.0\n'
    for reg in client_list:
        send_message(message, reg[1], server_socket)
    sys.exit(0)


# function to send ack
def send_ack(addr, sock):
    global exp_seq
    global last_message
    global sent_ack
    last_message = ACK
    sent_ack = True
    ack_tuple = (ACK.encode(), 16, exp_seq)
    ack_packer = struct.Struct("16s i i")
    ack_packet = ack_packer.pack(*ack_tuple)
    checksum = bytes(hashlib.md5(ack_packet).hexdigest(), encoding="UTF-8")

    ack_tuple = (ACK.encode(), 16, exp_seq, checksum)
    ack_packer = struct.Struct("16s i i 32s")
    ack_packet = ack_packer.pack(*ack_tuple)

    # server socket sends it to the address that needs it
    sock.sendto(ack_packet, addr)
    # flipped the sequence number
    if exp_seq == 0:
        exp_seq = 1
    else:
        exp_seq = 0


def get_line_from_socket(sock):
    global sent_ack
    received_packet, addr = sock.recvfrom(BUFFER_SIZE)
    unpacker = struct.Struct(f'{MAX_STRING_SIZE}s i i 32s')
    UDP_packet = unpacker.unpack(received_packet)

    # separate the values so we can validate the checksum
    received_message = UDP_packet[0]
    received_size = UDP_packet[1]
    received_seq = UDP_packet[2]
    received_checksum = UDP_packet[3]

    values = (received_message, received_size, received_seq)
    packet_struct = struct.Struct(f'{MAX_STRING_SIZE}s i i')
    packet = packet_struct.pack(*values)
    checksum = bytes(hashlib.md5(packet).hexdigest(), encoding="UTF-8")
    # if the checksum is valid, we can continue to send the packet through
    if checksum == received_checksum:
        send_ack(addr, sock)
        return UDP_packet, addr
    else:
        sent_ack = False
        time.sleep(2)

# Search the client list for a particular user.


def client_search(user):
    for reg in client_list:
        if reg[0] == user:
            return reg[1]
    return None

# Search the client list for a particular user by their socket.


def client_search_by_addr(address):
    for reg in client_list:
        if reg[1] == address:
            return reg[0]
    return None

# Add a user to the client list.


def client_add(user, conn, follow_terms):
    registration = (user, conn, follow_terms)
    client_list.append(registration)

# Remove a client when disconnected.


def client_remove(user):
    for reg in client_list:
        if reg[0] == user:
            client_list.remove(reg)
            break

# Function to list clients.


def list_clients():
    first = True
    list = ''
    for reg in client_list:
        if first:
            list = reg[0]
            first = False
        else:
            list = f'{list}, {reg[0]}'
    return list

# Function to return list of followed topics of a user.


def client_follows(user):
    for reg in client_list:
        if reg[0] == user:
            first = True
            list = ''
            for topic in reg[2]:
                if first:
                    list = topic
                    first = False
                else:
                    list = f'{list}, {topic}'
            return list
    return None

# Function to add to list of followed topics of a user, returning True if added
# or False if topic already there.


def client_add_follow(user, topic):
    for reg in client_list:
        if reg[0] == user:
            if topic in reg[2]:
                return False
            else:
                reg[2].append(topic)
                return True
    return None

# Function to remove from list of followed topics of a user, returning True if
# removed or False if topic was not already there.


def client_remove_follow(user, topic):
    for reg in client_list:
        if reg[0] == user:
            if topic in reg[2]:
                reg[2].remove(topic)
                return True
            else:
                return False
    return None


# Function to read messages from clients.
def send_message(message, addr, server):
    global exp_seq
    global last_message
    global waiting_ack
    last_message = message
    waiting_ack = True
    packet_tuple = (message.encode(), len(message), exp_seq)
    packet_struct = struct.Struct(f'{MAX_STRING_SIZE}s i i')
    packet = packet_struct.pack(*packet_tuple)
    checksum = bytes(hashlib.md5(packet).hexdigest(), encoding="UTF-8")

    packet_tuple = (message.encode(), len(message), exp_seq, checksum)
    packet_struct = struct.Struct(f'{MAX_STRING_SIZE}s i i 32s')
    packet = packet_struct.pack(*packet_tuple)
    server.sendto(packet, addr)

    poss_ack = get_ack(server)
    # when we have an ack, we now need to change the sequence number that we
    # expect
    if poss_ack:
        if exp_seq == 0:
            exp_seq = 1
        else:
            exp_seq = 0
        return
    else:
        # this is where sequence numbers come in probably
        # send_message(message, addr, server)
        time.sleep(2)
        return


# function to receive file
def receive_packet(sock, addr):
    global exp_seq
    chunk_packet, addr = sock.recvfrom(BUFFER_SIZE)
    chunk_unpacker = struct.Struct(f'{MAX_STRING_SIZE}s i 32s')
    chunk = chunk_unpacker.unpack(chunk_packet)

    file_chunk = chunk[0]
    seq = chunk[1]
    checker = chunk[2]
    # creation of packet to validate checksum
    test_tuple = (file_chunk, seq)
    test_packer = struct.Struct(f'{MAX_STRING_SIZE}s i')
    test_packet = test_packer.pack(*test_tuple)
    checksum = bytes(hashlib.md5(test_packet).hexdigest(), encoding="UTF-8")

    if checksum == checker:
        send_ack(addr, sock)
        return chunk[0]
    else:
        time.sleep(2)
        return


def send_chunk(chunk, sock, address):
    chunk_packer = struct.Struct(f'{MAX_STRING_SIZE}s')
    chunk_packet = chunk_packer.pack(chunk)
    checksum = bytes(hashlib.md5(chunk_packet).hexdigest(), encoding="UTF-8")
    # send the chunk with the check sum
    chunk_tuple = (chunk, checksum)
    chunk_packer = struct.Struct(f'{MAX_STRING_SIZE}s 32s')
    chunk_packet = chunk_packer.pack(*chunk_tuple)
    sock.sendto(chunk_packet, address)
    return


def get_ack(sock):
    global waiting_ack
    ack_packet, addr = sock.recvfrom(BUFFER_SIZE)
    ack_unpacker = struct.Struct(f'{16}s i i 32s')
    ack_tuple = ack_unpacker.unpack(ack_packet)

    ack = ack_tuple[0]
    size = ack_tuple[1]
    seq = ack_tuple[2]
    check_tup = (ack, size, seq)

    check_tup_packer = struct.Struct(f'{16}s i i')
    check_pack = check_tup_packer.pack(*check_tup)
    checksum = bytes(hashlib.md5(check_pack).hexdigest(), encoding="UTF-8")

    # correct checksum means we can send the ack through
    if checksum == ack_tuple[3]:
        waiting_ack = False
        return ack
    else:
        return


def read_message(sock, mask, message, addr):

    if message == '':
        print('Closing connection')
        sel.unregister(sock)
        sock.close()

    # Receive the message.

    else:
        user = client_search_by_addr(addr)
        print(f'Received message from user {user}:  ' + message)
        words = message.split(' ')
        print(words)

        # Check for client disconnections.
        if words[0] == 'DISCONNECT':
            print('Disconnecting user ' + user)
            client_remove(user)

        # Check for specific commands.
        elif ((len(words) == 2) and ((words[1] == '!list') or
                                     (words[1] == '!exit') or
                                     (words[1] == '!follow?'))):
            if words[1] == '!list':
                response = list_clients() + '\n'
                send_message(response, addr, sock)
            elif words[1] == '!exit':
                print('Disconnecting user ' + user)
                response='DISCONNECT CHAT/1.0\n'
                send_message(response, addr, sock)
                client_remove(user)
            elif words[1] == '!follow?':
                response = client_follows(user) + '\n'
                send_message(response, addr, sock)

        # Check for specific commands with a parameter.

        elif ((len(words) == 3) and ((words[1] == '!follow') or (words[1] == '!unfollow'))):
            if words[1] == '!follow':
                topic = words[2]
                if client_add_follow(user, topic):
                    response = f'Now following {topic}\n'
                else:
                    response = f'Error:  Was already following {topic}\n'
                send_message(response, addr, sock)
            elif words[1] == '!unfollow':
                topic = words[2]
                if topic == '@all':
                    response = 'Error:  All users must follow @all\n'
                elif topic == '@'+user:
                    response = 'Error:  Cannot unfollow yourself\n'
                elif client_remove_follow(user, topic):
                    response = f'No longer following {topic}\n'
                else:
                    response = f'Error:  Was not following {topic}\n'
                send_message(response, addr, sock)

        # Check for user trying to upload/attach a file.  We strip the message
        # to keep the user and any other text to help forward the file.  Will
        # send it to interested users like regular messages.

        elif ((len(words) >= 3) and (words[1] == '!attach')):
            sock.setblocking(True)
            filename = words[2]
            words.remove('!attach')
            words.remove(filename)
            response = f'ATTACH {filename} CHAT/1.0\n'
            send_message(response, addr, sock)
            header_packet, addr = get_line_from_socket(sock)
            size = header_packet[1]
            header = header_packet[0].decode()[:size]
            print(header)
            header_words = header.split(' ')
            if (len(header_words) != 2) or (header_words[0] !=
                                            'Content-Length:'):
                response = f'Error:  Invalid attachment header\n'
            elif header_words[1] == '-1':
                response = f'Error:  Attached file {filename} could not ' \
                           f'be sent\n'
            else:
                interested_clients = []
                attach_size = header_words[1]
                attach_notice = f'ATTACHMENT {filename} CHAT/1.0\nOrigin: ' \
                                f'{user}\nContent-Length: {attach_size}\n'
                for reg in client_list:
                    if reg[0] == user:
                        continue
                    forwarded = False
                    for term in reg[2]:
                        for word in words:
                            if ((term == word.rstrip(punctuation)) and not
                            forwarded):
                                interested_clients.append(reg[1])
                                send_message(attach_notice, reg[1], sock)
                bytes_read = 0
                bytes_to_read = int(attach_size)
                file_download = open(filename, 'wb')
                bytes_left = int(attach_size)
                # start writing the file to a new file saved to the server
                while bytes_read < bytes_to_read:
                    if MAX_STRING_SIZE > bytes_left:
                        amount = bytes_left
                    else:
                        amount = MAX_STRING_SIZE
                    chunk = receive_packet(sock, addr)
                    file_download.write(chunk[:amount])
                    bytes_read += len(chunk)
                    bytes_left -= amount
                    for client in interested_clients:
                        send_chunk(chunk, sock, client)
                response = f'Attachment {filename} attached and distributed\n'
                file_download.close()
            send_message(response, addr, sock)

        # Look for follow terms and dispatch message to interested users.
        # Send at most only once, and don't send to yourself.  Trailing
        # punctuation is stripped.
        # Need to re-add stripped newlines here.

        else:
            for reg in client_list:
                if reg[0] == user:
                    continue
                forwarded = False
                for term in reg[2]:
                    for word in words:
                        if term == word.rstrip(punctuation) and not forwarded:
                            client_sock = reg[1]
                            forwarded_message = f'{message}\n'
                            client_sock.send(forwarded_message.encode())
                            forwarded = True


# Function to accept and set up clients.

def accept_client(sock, mask):
    global address
    # Sending and receiving with UDP sockets requires an address, and we send
    # and receive from said address
    con_tuple = get_line_from_socket(sock)
    addr = con_tuple[1]
    client_packet = con_tuple[0]
    size = client_packet[1]
    message = client_packet[0].decode()[:size]
    print('Accepted connection from client address:', addr)
    message_parts = message.split()

    client = client_search_by_addr(addr)
    if client:
        for user in client_list:
            if addr in user:
                read_message(sock, mask, message, addr)
                return
    # Check format of request.
    if ((len(message_parts) != 3) or (message_parts[0] != 'REGISTER') or
            (message_parts[2] != 'CHAT/1.0')):
        print('Error:  Invalid registration message.')
        print('Received: ' + message)
        print('Connection closing ...')
        response='400 Invalid registration\n'
        send_message(response, addr, sock)
    # If request is properly formatted and user not already listed, go ahead
    # with registration.

    else:
        user = message_parts[1]
        if user == 'all':
            print('Error:  Client cannot use reserved user name \'all\'.')
            print('Connection closing ...')
            response='402 Forbidden user name\n'
            send_message(response, addr, sock)

        elif (client_search(user) == None):
            follow_terms = []
            follow_terms.append(f'@{user}')
            follow_terms.append('@all')

            # Finally add the user.

            client_add(user, addr, follow_terms)
            print(f'Connection to client established, waiting to receive messages from user \'{user}\'...')
            response='200 Registration successful\n'
            address = addr
            send_message(response, addr, sock)

        # If user already in list, return a registration error.

        else:
            print('Error:  Client already registered.')
            print('Connection closing ...')
            response='401 Client already registered\n'
            send_message(response, addr, sock)


# Our main function.

def main():

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    global server_socket
    # Create the socket.  We will ask this to work on any interface and to pick
    # a free port at random.  We'll print this out for clients to use.

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', 0))
    print('Will wait for client connections at port ' +
          str(server_socket.getsockname()[1]))
    server_socket.setblocking(True)
    sel.register(server_socket, selectors.EVENT_READ, accept_client)
    print('Waiting for incoming client connections ...')
    # Keep the server running forever, waiting for connections or messages.

    while(True):
        events = sel.select(timeout=2)
        if not events:
            if last_message != ACK and waiting_ack:
                # retransmit the message
                send_message(last_message, address, server_socket)
            elif last_message == ACK and not sent_ack:
                # retransmit the ack
                send_ack(address, server_socket)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)

if __name__ == '__main__':
    main()

