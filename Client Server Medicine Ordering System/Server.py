# This server runs continuously, waiting for requests from Client.py 
import socket
import random

medication = {
    'Tramadol': {'price': 10, 'stock': 500},
    'Aspirin': {'price': 1, 'stock': 1000},
    'Aptiom': {'price': 1000, 'stock': 20},
    'Carbatrol': {'price': 113, 'stock': 50},
    'Indapamide': {'price': 21, 'stock': 150}
}

price = {
    'Pounds': 1,
    'Dollars': 1.25,
    'Euros': 1.15
}

def processOrder(order):
    try:
        name, number, med, quantity, currency = order.split() # splits input into each feild
        quantity = int(quantity)

        if med not in medication:
            return "Error: Medicine not available."
        if currency not in price:
            return "Error: Unsupported currency."

        available = medication[med]['stock']
        pricePerBox = medication[med]['price']
        quantitySupplied = min(quantity, available)
        medication[med]['stock'] -= quantitySupplied

        cost = quantitySupplied * pricePerBox * price[currency]
        bookingNumber = random.randint(10000, 99999) # assigns a random booking number

        with open("booking_log.txt", "a") as file: # adds booking to file
            file.write(f"{bookingNumber} {number} {med} {quantitySupplied} {cost:.2f} {currency}\n")

        return f"{bookingNumber} {number} {med} {quantitySupplied} {cost:.2f} {currency}"
    except Exception as e:
        return f"Error: Invalid input format. {str(e)}"

server = socket.socket() # makes server
server.bind(('localhost', 9999))
server.listen(1)
print("Server ready. Waiting for connection...")

conn, addr = server.accept() # for when client connects
print("Connected with", addr)

while True: # runs forever
    order = conn.recv(1024).decode()
    if order.lower() == 'exit':
        break
    response = processOrder(order)
    conn.send(response.encode())

conn.close()
