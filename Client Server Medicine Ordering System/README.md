# Medicine Ordering System

A Python client-server application that simulates a medicine ordering system for pharmacists using TCP socket communication.

The project demonstrates network programming, business logic implementation, session management, and persistent order logging.

## Features

- Client-server architecture using Python sockets
- Multiple medicine orders in a single client session
- Real-time order validation
- Order confirmation with booking number, quantity and total cost
- Automatic discount calculation
- Persistent booking log stored in a text file

## How it Works

The system consists of two programs:

### Server

The server runs continuously and waits for incoming client connections.

For each order it:

- Validates the medicine request
- Checks medicine availability
- Calculates the order cost
- Applies any applicable discounts
- Returns an order confirmation
- Records successful bookings in `booking_log.txt`

### Client

The client connects to the server and allows a pharmacist to place multiple orders during a single session.

The client:

- Collects order information
- Sends requests to the server
- Displays order confirmations
- Tracks the number of orders and running total
- Automatically qualifies for a 20% discount when:
  - Total spend exceeds **£12,000**, or
  - More than **4 medications** are ordered during the session

## Technologies

- Python
- TCP Sockets
- File Handling
- Client-Server Architecture

## Files

- `client.py` — Client application
- `server.py` — Server application
- `booking_log.txt` — Log of processed orders

## Skills Demonstrated

- Network programming
- Socket communication
- Client-server application design
- Session management
