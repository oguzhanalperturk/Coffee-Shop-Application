from socket import *
from threading import *
import time

threadLock = RLock()

class ClientThread(Thread):
    def __init__(self, cSocket, cAddress):
        Thread.__init__(self)
        self.cSocket = cSocket
        self.cAddress = cAddress
        print("Connection successful from ", self.cAddress)


    def run(self):
        # Connection establish
        serverMsg = "CONNECTION SUCCESSFUL".encode()
        self.cSocket.send(serverMsg)
        clientMsg = ""
        #Connection will continue as long as it is not broken by the client
        while clientMsg != "!DISCONNECT":
            clientMsg = self.cSocket.recv(1024).decode()
            if("login" in clientMsg):
                print("loginsuccess -----")
                self.userLogin(clientMsg)
            elif("order" in clientMsg):
                self.calculateOrderPrice(clientMsg)
            elif("report" in clientMsg):
                if clientMsg == "report1":
                    self.prepareReport1()
                elif clientMsg == "report2":
                    self.prepareReport2()
                elif clientMsg == "report3":
                    self.prepareReport3()
                elif clientMsg == "report4":
                    self.prepareReport4()


        print("Disconnected from ", self.cAddress)
        self.cSocket.close()

    #This function for reading file
    def readFile(self,filename):
        try:
            file = open(filename, "r")
            records = file.readlines()
            file.close()
            return records
        except:
            print("Error happened in opening the file")
            exit(1)
    #Login authentication, checking if username and password is in the db
    def userLogin(self,clientMsg):
        users = self.readFile("users.txt")
        clientMsg_list = clientMsg.split(";")
        username = clientMsg_list[1]
        password = clientMsg_list[2]
        flag = 0
        role = ""
        for user in users:
            user_info = user.split(";")
            if (user_info[0] == username):
                if (user_info[1] == password):
                    flag = 1
                    role = user_info[2]
                    break

        response = str(flag) + ";" + str(role)
        response = response.encode()
        self.cSocket.send(response)
    # This function for calculating order price based on discount if there is any.
    def calculateOrderPrice(self, clientMsg):

        order_list = clientMsg.split(";")
        discountcodes = self.readFile("discountcodes.txt")
        prices = self.readFile("prices.txt")

        total_price = 0
        for order_count in range(3, len(order_list)):
            for price in prices:
                if order_list[order_count].split("-")[0] == price.split(";")[0]:
                    cleanprice = int(price.split(";")[1].replace('\n', ''))
                    total_price += int(order_list[order_count].split("-")[1]) * int(cleanprice)
                    break

        dname = order_list[1]
        discount = 0
        if(dname != "nodiscountcode"):
            for i in discountcodes:
                dcode_list = i.split(";")
                dcode = dcode_list[0]
                if (dcode == dname):
                    discount = int(dcode_list[1].replace('\n', ''))
                    break

        price_after_discount = total_price - discount

        write_order = "\n" + str(total_price) + ";" + str(discount)
        for i in range(2, len(order_list)):
            write_order += ";" + order_list[i]

        threadLock.acquire()
        file = open("orders.txt", "a")
        file.writelines(write_order)
        file.close()
        threadLock.release()

        threadLock.acquire()
        file = open("discountcodes.txt", "w")
        for i in discountcodes:
            temp = i.split(";")
            if (temp[0] != dname):
                file.writelines(i)
        file.close()
        threadLock.release()

        order_confirmation = "orderconfirmation;" + str(price_after_discount)
        self.cSocket.send(order_confirmation.encode())

    #This function for report 1 which is What is the most popular coffee overall?
    def prepareReport1(self):

        orders = self.readFile("orders.txt")

        if orders == []:
            serverMsg = "report1"

        else:
            coffees = "lattecappuccinoamericanoexpresso"
            coffees_list = [["latte", 0], ["cappuccino", 0], ["americano", 0], ["expresso", 0]]

            for order in orders:

                order_list = order.split(";")

                for i in range(3, len(order_list)):
                    coffee_name = order_list[i].split("-")[0]
                    if (coffee_name in coffees):
                        coffee_amount = int(order_list[i].split("-")[1].strip())

                        for coffee in coffees_list:
                            if (coffee[0] == coffee_name):
                                coffee[1] += coffee_amount


            popular_coffees = []
            max = 0
            for coffee in coffees_list:
                if coffee[1] > max:
                    max = coffee[1]

            for coffee in coffees_list:
                if (max == coffee[1]):
                    popular_coffees.append(coffee[0])

            serverMsg = "report1;"

            for coffee in popular_coffees:
                serverMsg += coffee + ";"

            serverMsg = serverMsg[:-1]

        self.cSocket.send(serverMsg.encode())

    #This function for report 2 which is Which barista has the highest number of orders?
    def prepareReport2(self):
        orders = self.readFile("orders.txt")
        baristas = []

        if orders == []:
            serverMsg = "report2"

        else:

            for order in orders:

                order_list = order.split(";")
                flag = 0

                for barista in baristas:
                    if (barista[0] == order_list[2]):
                        flag = 1
                        break
                if (flag == 0):
                    baristas.append([order_list[2], 0])

                for i in range(3, len(order_list)):

                    order_name = order_list[i].split("-")[0]
                    order_amount = int(order_list[i].split("-")[1])

                    for barista in baristas:
                        if (order_list[2] == barista[0]):
                            barista[1] += order_amount

            highest_order_baristas = []
            max = 0
            for barista in baristas:
                if barista[1] > max:
                    max = barista[1]

            for barista in baristas:
                if (max == barista[1]):
                    highest_order_baristas.append(barista[0])

            serverMsg = "report2;"

            for barista in highest_order_baristas:
                serverMsg += barista + ";"

            serverMsg = serverMsg[:-1]

        self.cSocket.send(serverMsg.encode())

    # This function for report 3 which is What is the most popular product for the orders with the discount code?
    def prepareReport3(self):
        orders = self.readFile("orders.txt")

        if orders == []:
            serverMsg = "report3"

        else:

            products = [["latte", 0], ["cappuccino", 0], ["americano", 0], ["expresso", 0], ["sansebastian", 0],
                        ["mosaic", 0], ["carrot", 0]]

            for order in orders:

                order_list = order.split(";")

                if (order_list[1] != 0):
                    for i in range(3, len(order_list)):
                        product_name = order_list[i].split("-")[0]
                        product_amount = int(order_list[i].split("-")[1])
                        for product in products:
                            if (product[0] == product_name):
                                product[1] += product_amount

            total_amount = 0
            for product in products:
                total_amount += product[1]
            if (total_amount == 0):
                serverMsg = "report3"
            else:
                popular_products = []
                max = 0
                for product in products:
                    if product[1] > max:
                        max = product[1]

                for product in products:
                    if (max == product[1]):
                        popular_products.append(product[0])

                serverMsg = "report3;"

                for product in popular_products:
                    serverMsg += product + ";"

                serverMsg = serverMsg[:-1]

        self.cSocket.send(serverMsg.encode())

    # This function for report 4 which is What is the most popular cake that is bought with expresso?
    def prepareReport4(self):
        orders = self.readFile("orders.txt")

        if orders == []:
            serverMsg = "report4"

        else:

            cakes_str = "sansebastianmosaiccarrot"
            cakes = [["sansebastian", 0], ["mosaic", 0], ["carrot", 0]]

            for order in orders:

                order_list = order.split(";")
                expresso_flag = 0
                for i in range(3, len(order_list)):
                    product_name = order_list[i].split("-")[0]
                    if (product_name == "expresso"):
                        expresso_flag = 1
                        break

                if (expresso_flag == 1):
                    for i in range(3, len(order_list)):
                        product_name = order_list[i].split("-")[0]
                        if (product_name in cakes_str):
                            product_amount = int(order_list[i].split("-")[1])
                            for cake in cakes:
                                if (cake[0] == product_name):
                                    cake[1] += product_amount

            total_cake_amount = 0
            for cake in cakes:
                total_cake_amount += cake[1]

            if (total_cake_amount == 0):
                serverMsg = "report4;noexpresso"

            else:
                popular_cakes = []

                max = 0
                for cake in cakes:
                    if cake[1] > max:
                        max = cake[1]

                for cake in cakes:
                    if (max == cake[1]):
                        popular_cakes.append(cake[0])

                serverMsg = "report4;"

                for cake in popular_cakes:
                    serverMsg += cake + ";"

                serverMsg = serverMsg[:-1]

        self.cSocket.send(serverMsg.encode())



if __name__ == "__main__":
    HOST="127.0.0.1"
    PORT = 5000

    socket = socket(AF_INET, SOCK_STREAM)
    socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socket.bind((HOST, PORT))
    while True:
        socket.listen()
        cSocket, cAddress = socket.accept()
        newClient = ClientThread(cSocket, cAddress)
        newClient.start()