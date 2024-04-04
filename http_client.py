from HTTP_Class import *

def main():
    # Initialize HTTP client
    http_client = http(CLIENT)
    # Get input for HTTP request
    req = http_client.http_getInput()
    # Parse the HTTP request
    status = http_client.http_parse(req.split('\n'))
    # Check parsing status
    if status == ERR:
        return
    # Initialize a TCP client
    http_client.http_init()
    # Send HTTP request
    status = http_client.http_send(req)
    # Check sending status
    if status == ERR:
        # Handle 404 error
        http_client.http_404()
        return
    # Receive HTTP response
    res = http_client.http_listen()
    # Check if response received
    if not res:
        # Handle 404 error
        http_client.http_404()
        return
    # Print HTTP response
    print(res[0])

if __name__ == "__main__":
    main()
