# This client sends a medicine order to the server. It first connects to the server, then sends an order with the necessary fields and  waits for the server's reply to confirm the order. 
import socket

client = socket.socket()
client.connect(('localhost', 9999))  # connects to server

print("Welcome to the International Pharmaceutical Ordering System")
print("Expected format: [Pharmacy Name] [Pharmacy Number] [Medicine Required] [Number of Boxes] [Currency Wish to Pay With].")
print("Example format: Hamzepur 12345 Tramadol 100 Dollars")

try:
    totalOrders = int(input("How many orders would you like to place: ")) # asks how many orders the pharmacist wants to place

except ValueError:
    print("Invalid number. Exiting.")
    client.close()
    exit()

sessionTotal = 0
sessionCount = 0

for _ in range(totalOrders): # gets order details the amount of times needed
    order = input("Enter your order or 'exit': ")
    client.send(order.encode())

    if order.lower() == 'exit':
        break

    response = client.recv(1024).decode()
    print("Server Response:", response)

    try:
        parts = response.split() # tracks if cost is valid
        if len(parts) == 6:
            cost = float(parts[4])
            sessionTotal += cost
            sessionCount += 1
    except:
        pass

if sessionTotal > 12000 or sessionCount > 4: # checks if discount needed
    discount = sessionTotal * 0.20 # calluclates discount 
    finalTotal = sessionTotal - discount 
    print(f"\nYou get a 20% discount, Discount amount: {discount:.2f}")
    print(f"Total after discount: {finalTotal:.2f}")
else:
    print(f"\nTotal cost for this session: {sessionTotal:.2f}")

client.close()
