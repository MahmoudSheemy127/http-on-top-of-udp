from HTTP_Class import *

def main():
    while True:
        # Initialize HTTP server
        http_server = http(SERVER)
        # Initialize TCP client
        http_server.http_init()
        # Server listens for incoming requests
        req = http_server.http_listen()
        # Print connection establishment details
        print("Connection Established with IP: {} and PORT: {}".format(req[1][0], req[1][1]))
        print("\n")
        print("Client request: ")
        print(req[0])
        if not req:
            print("Received error")
            return
        # Parse the received request
        if http_server.http_parse(req[0].split('\n')) == ERR:
            print("False response")
            return
        # Based on the request from client, server prepares response
        res = http_server.http_create_res()
        # Update client IP and port
        http_server.http_update_tcp_client(req[1])
        # Send response to the client
        http_server.http_send(res)
        # Print server response
        print("Server response: ")
        print(res)

if __name__ == "__main__":
    main()
