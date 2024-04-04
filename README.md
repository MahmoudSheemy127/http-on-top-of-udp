# ReliableUDP-HTTP-TCP-Simulation

## Description
This project implements a simulation of TCP packets using a UDP connection while maintaining reliability and supporting the HTTP protocol on top of UDP. UDP is a connectionless protocol that does not guarantee the delivery or order of packets, presenting challenges for reliable data transfer. To address this, the system includes mechanisms for error detection and correction, packet retransmission, and flow control.

## Features
- **Reliability Mechanisms**: Error detection and correction are achieved using checksums, and packet retransmission is implemented using acknowledgments and timeouts.
- **Flow Control**: Flow control is achieved using sliding window protocols.
- **Support for HTTP Protocol**: The system parses HTTP requests and responses, handling various methods and headers defined by the protocol.
- **Performance Considerations**: Trade-offs between performance and reliability are considered to handle packet loss, duplication, and reordering while maintaining reasonable performance.

## Components
The project consists of the following components:
- **RUDP (Reliable UDP)**: Implementation of a reliable UDP protocol that handles error detection, correction, retransmission, and flow control.
- **TCP Simulation**: Extension of the user space application to simulate TCP packets using RUDP.
- **HTTP Layer**: Implementation of the HTTP application layer protocol that runs above TCP, supporting various HTTP methods and headers.
- **Client Script**: Script for the client side, which sends HTTP requests using the implemented HTTP protocol.
- **Server Script**: Script for the server side, which listens for incoming HTTP requests, processes them, and sends appropriate responses.

## Usage
1. Clone the repository: `git clone https://github.com/your-username/ReliableUDP-HTTP-TCP-Simulation.git`
2. Navigate to the project directory: `cd ReliableUDP-HTTP-TCP-Simulation`
3. Run the client script: `python client.py`
4. Run the server script: `python server.py`
5. Follow the prompts to send HTTP requests from the client and receive responses from the server.

## HTTP Client Request prompt sample
```
GET /index1.html
HOST:127.0.0.1
```
```
POST index.html
HOST:127.0.0.1

This is a post message
```
## HTTP Server Response sample
```
HTTP/1.1 200 OK

Hello people
```

```
HTTP/1.1 201 Created
```


## Dependencies
- Python 3.x
- [socket](https://docs.python.org/3/library/socket.html)
- [struct](https://docs.python.org/3/library/struct.html)

