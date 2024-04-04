import socket
import time
import struct

ERR = -1

buffer_size = 1024
localIP = "127.0.0.1"

localPort = 20001
UDP_IP = "127.0.0.1"  # IP address to bind to
UDP_PORT = 20001  # Port to bind to

class RUDP:
    def __init__(self, ip, port):
        """
        Initialize the Reliable UDP client class.

        Args:
        - ip (str): IP address of the server.
        - port (int): Port number of the server.
        """
        self.ip = ip
        self.port = port
        self.seq_num = 0
        self.ack_num = 0
        self.window_size = 10
        self.packet_buffer = []  # Buffer to hold packets waiting to be sent
        self.unacked_packets = []  # Unacknowledged packets
        self.last_ack_received = None
        self.last_seq_num_sent = None
        self.last_ack_num_received = None
        self.last_packet_received = None
        self.last_packet_sent = None
        self.time_out = 1.0  # Timeout for retransmission
        self.conn_state = "CLOSED"  # Connection state
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send(self, data):
        """
        Send data using Reliable UDP protocol.

        Args:
        - data (str): Data to be sent.
        """
        trial_connection = 0
        if self.conn_state != "establish":
            # Send SYN packet to initiate connection establishment
            syn = self.header() + self.flags(1, 0, 0).to_bytes(1, 'big')
            self.sock.sendto(syn, (self.ip, self.port))
            SYN_ACK_RECEIVED = False
            while not SYN_ACK_RECEIVED:
                try:
                    packet = self.sock.recvfrom(buffer_size)[0]
                except:
                    if trial_connection < 3:
                        trial_connection += 1
                        pass
                    return ERR
                if packet[-1] == 3:
                    SYN_ACK_RECEIVED = True
                    # Send ACK to acknowledge SYN-ACK
                    ack = self.header() + self.flags(0, 1, 0).to_bytes(1, 'big')
                    self.sock.sendto(ack, (self.ip, self.port))
                    self.conn_state = "establish"

        # Encapsulate data into packets and send
        packet = self.encapsulate(data)
        self.packet_buffer.append(packet)
        self.last_seq_num_sent = self.seq_num
        self.seq_num += 1
        self.send_packet()  # Send the packet

        ack = False
        self.sock.settimeout(1)
        # Wait for ACK
        while not ack:
            try:
                packet, address = self.sock.recvfrom(buffer_size)
            except:
                packet = self.encapsulate(data)
                self.packet_buffer.append(packet)
                self.send_packet()
            if packet[-1] == 1:
                ack = True

    def receive(self):
        """
        Receive data using Reliable UDP protocol.

        Returns:
        - tuple: Tuple containing data and address of the sender.
        """
        if self.conn_state != "establish":
            syn = False
            while not syn:
                packet, add = self.sock.recvfrom(buffer_size)
                if packet[-1] == 2:
                    synack = self.header() + self.flags(1, 1, 0).to_bytes(1, 'big')
                    self.sock.sendto(synack, add)
                    syn = True
            ack = False
            while not ack:
                packet, address = self.sock.recvfrom(buffer_size)
                if packet[-1] == 1:
                    ack = True
                    self.conn_state = "establish"

        packet, add = self.sock.recvfrom(buffer_size)
        if packet[8] == self.calc_checksum(self.seq_num.to_bytes(4, 'big') + self.ack_num.to_bytes(4, 'big')):
            self.last_packet_received = packet
            self.last_ack_received = self.get_seqnum(packet)
            self.last_ack_num_received = self.last_ack_received
            if self.last_ack_received >= self.last_ack_num_received:
                # Remove ACKED PACKETS WHICH SEQ NUMBER > LAST ACK NUMBER
                self.unacked_packets = [p for p in self.unacked_packets if self.get_seqnum(p) > self.last_ack_num_received]
            if self.last_packet_received is not None and self.get_seqnum(self.last_packet_received) == self.last_ack_num_received:
                data = self.decapsulate(self.last_packet_received)
            ack = self.header() + self.flags(0, 1, 0).to_bytes(1, 'big')
            self.sock.sendto(ack, add)
            self.ack_num += 1
            return (data, add)
        else:
            return None

    def encapsulate(self, data):
        """
        Encapsulate data into packet.

        Args:
        - data (str): Data to be encapsulated.

        Returns:
        - bytes: Encapsulated packet.
        """
        rudp_header = self.header()
        packet = rudp_header + struct.pack('d', time.time()) + data.encode()
        return packet

    def decapsulate(self, packet):
        """
        Decapsulate packet to extract data.

        Args:
        - packet (bytes): Packet to be decapsulated.

        Returns:
        - str: Decapsulated data.
        """
        data = packet[17:].decode()
        return data

    def get_seqnum(self, packet):
        """
        Extract sequence number from packet.

        Args:
        - packet (bytes): Packet from which sequence number to be extracted.

        Returns:
        - int: Sequence number.
        """
        return int.from_bytes(packet[:4], "big")

    def get_acknum(self, packet):
        """
        Extract acknowledgment number from packet.

        Args:
        - packet (bytes): Packet from which acknowledgment number to be extracted.

        Returns:
        - int: Acknowledgment number.
        """
        return int.from_bytes(packet[4:8], 'big')

    def parse_HTTP(self, data):
        """
        Parse HTTP response.

        Args:
        - data (str): HTTP response data.
        """
        pass

    def send_packet(self):
        """
        Send packets from packet buffer.
        """
        while len(self.packet_buffer) > 0:
            if len(self.unacked_packets) >= self.window_size:  # check if window size is reached
                break
            packet = self.packet_buffer.pop(0)
            self.unacked_packets.append(packet)
            self.sock.sendto(packet, (self.ip, self.port))

        now = time.time()
        send_time = struct.unpack('d', packet[9:17])[0]
        for packet in self.unacked_packets:
            if now - send_time > self.time_out:
                self.sock.sendto(packet, (self.ip, self.port))

    def header(self):
        """
        Construct packet header.

        Returns:
        - bytes: Packet header.
        """
        h = self.seq_num.to_bytes(4, 'big') + self.ack_num.to_bytes(4, 'big')
        checksum = self.calc_checksum(h)
        h += checksum.to_bytes(1, 'big')
        return h

    def calc_checksum(self, data):
        """
        Calculate checksum of data.

        Args:
        - data (bytes): Data for which checksum to be calculated.

        Returns:
        - int: Checksum value.
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum

    def flags(self, syn, ack, fin):
        """
        Construct packet flags.

        Args:
        - syn (bool): SYN flag.
        - ack (bool): ACK flag.
        - fin (bool): FIN flag.

        Returns:
        - int: Packet flags.
        """
        f = 0
        if ack:
            f |= 0b00000001
        if syn:
            f |= 0b00000010
        if fin:
            f |= 0b00000100
        return f
