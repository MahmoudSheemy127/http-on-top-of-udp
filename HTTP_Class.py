from tcp import *

MSS = 4
GET = "GET"
POST = "POST"
PASS = 1
OTHER = -1
ERR = -1
SERVER = 0
CLIENT = 1

class http:
    def __init__(self, mode):
        """
        Initialize the HTTP protocol class.

        Args:
        - mode (int): Mode of operation, either SERVER or CLIENT.
        """
        self.MSS = MSS
        self.req_obj = {}  # Request object
        self.tcp_client = None
        self.mode = mode
        self.res_obj = {}  # Response object

    def http_send(self, req):
        """
        Send HTTP request.

        Args:
        - req (str): HTTP request to be sent.

        Returns:
        - int: Status of sending operation.
        """
        # Divide req into segments based on MSS
        # Every line in the request is a TCP segment
        return self.tcp_client.send(req)

    def http_listen(self):
        """
        Listen for incoming HTTP requests.

        Returns:
        - tuple: Tuple containing response data and address of the sender.
        """
        if self.mode == SERVER:
            print("Server is Listening at port 20001...")
        res = self.tcp_client.receive()
        return res

    def http_update_tcp_client(self, add):
        """
        Update TCP client IP and port.

        Args:
        - add (tuple): IP address and port.
        """
        self.tcp_client.ip = add[0]
        self.tcp_client.port = add[1]

    def http_init(self):
        """
        Initialize HTTP protocol.
        """
        if self.mode == SERVER:
            self.tcp_client = RUDP(UDP_IP, UDP_PORT)
            self.tcp_client.sock.bind((UDP_IP, UDP_PORT))
        elif self.mode == CLIENT:
            self.tcp_client = RUDP(self.req_obj["HOST"], UDP_PORT)

    def http_404(self):
        """
        Handle 404 Not Found error.
        """
        print("HTTP/1.1 404 Not Found")

    def http_parse(self, req):
        """
        Parse HTTP request.

        Args:
        - req (list): List of strings representing HTTP request lines.

        Returns:
        - int: Status of parsing operation.
        """
        if self.mode == CLIENT:
            # Check first line
            lineOne = req[0].split(' ')
            # Check method
            if lineOne[0] == 'GET':
                self.req_obj['method'] = GET
            elif lineOne[0] == 'POST':
                self.req_obj['method'] = POST
            else:
                print('Invalid HTTP command!')
                return ERR
            # Get URL
            self.req_obj['url'] = lineOne[1]
            # Check Header lines
            # Check for HOST header
            for line in req[1:]:
                if line.split(':')[0] == 'HOST':
                    self.req_obj['HOST'] = line.split(':')[1]
                    return PASS
            print('No HOST header!')
            return ERR

        elif self.mode == SERVER:
            # Get first line also
            lineOne = req[0].split(' ')
            if lineOne[0] == 'GET':
                self.res_obj['method'] = GET
                # Check message requested
                if lineOne[1] == '/index1.html':
                    self.res_obj['data'] = 1
                elif lineOne[1] == '/index2.html':
                    self.res_obj['data'] = 2
                else:
                    self.res_obj['data'] = 0

            elif lineOne[0] == 'POST':
                # Load index3.html with data posted by client
                self.res_obj['method'] = POST
                # Retrieve data
                for i, line in enumerate(req[1:]):
                    if not line.strip():
                        break
                # Write data retrieved from client to a text file
                fileName = lineOne[1]
                print(fileName)
                data = "".join(req[i+1:])
                with open(fileName, "w") as file:
                    file.write(data)
            return PASS

    def http_create_res(self):
        """
        Create HTTP response.

        Returns:
        - str: HTTP response.
        """
        if self.res_obj['method'] == GET:
            res = 'HTTP/1.1 200 OK\n\n'
            if self.res_obj['data'] == 1:
                with open("index1.html", "r") as file:
                    res += file.read()
            elif self.res_obj['data'] == 2:
                with open("index2.html", "r") as file:
                    res += file.read()
        if self.res_obj['method'] == POST:
            res = 'HTTP/1.1 201 Created\n'
        return res

    def http_getInput(self):
        """
        Get input for HTTP request.

        Returns:
        - str: HTTP request input.
        """
        lines = ""
        count = 0
        enter = 0
        MAX_COUNT = 10
        while count < MAX_COUNT:
            line = input()
            if line == "":
                if enter < 1:
                    enter += 1
                else:
                    return lines
            lines += line + '\n'
            count += 1
        return lines

    def http_print_summary(self):
        """
        Print HTTP request summary.
        """
        print("HTTP " + self.req_obj['method'] + " request to " + self.req_obj['HOST'] + self.req_obj['url'])
