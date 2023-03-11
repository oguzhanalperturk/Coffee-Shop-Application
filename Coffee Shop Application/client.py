from tkinter import *
from tkinter import messagebox
from socket import *



class Authentication(Frame):
    def __init__(self, socket):
        Frame.__init__(self)
        #GUI Design
        self.pack()
        self.master.title("Login")

        self.cSocket = socket

        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.username = Label(self.frame1, text="Username: ")
        self.username.pack(padx=5, pady=5, side=LEFT)

        self.username_entry = Entry(self.frame1)
        self.username_entry.pack(padx=5, pady=5)

        self.frame2 = Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.password = Label(self.frame2, text="Password: ")
        self.password.pack(padx=5, pady=5, side=LEFT)

        self.password_entry = Entry(self.frame2)
        self.password_entry.pack(padx=5, pady=5)

        self.frame3 = Frame(self)
        self.frame3.pack(padx=5, pady=5)
        self.login_button = Button(self.frame3, text ="Login", command = self.userLogin)
        self.login_button.pack(padx=5, pady=5)

    def userLogin(self):
        # Taking username and password from user
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.cSocket = socket
        # Creating message with data recieved from user
        clientMsg = "login;" + username + ";" + password
        # Sending message to the server
        self.cSocket.send(clientMsg.encode())
        # Taking response from the server
        response = self.cSocket.recv(1024).decode()

        # If Username and password match with db then flag is 1.
        flag = response.split(";")[0]
        role = response.split(";")[1]
        role = role.replace('\n','')

        # Showing the message on the screen
        # Redirect to the relevant panel depending on the user's role
        if (flag == '1'):
            messagebox.showinfo("Message", "Login succesfully:  " + username + "-" + role)

            if (role == "barista"):
                self.destroy()
                window = BaristaPanel(socket,username)
                window.mainloop()
            elif (role == "manager"):
                self.destroy()
                window = ManagerPanel(socket)
                window.mainloop()
        else:
            messagebox.showinfo("Message", "Login failure!!!")


# Barista panel
class BaristaPanel(Frame):
    def __init__(self, socket, username):
        self.username = username
        Frame.__init__(self)

        #GUI Design
        self.master.title("Barista Panel")
        self.cSocket = socket
        self.grid()
        self.columnconfigure((0,1), weight=1, uniform="column")

        coffee_title = Label(self, text="COFFEES")
        coffee_title.grid(row=0, columnspan=2)

        self.coffee_types = [["Latte", BooleanVar(), "latte"], ["Cappuccino", BooleanVar(),"cappuccino"], ["Americano", BooleanVar(),"americano"], ["Expresso", BooleanVar(),"expresso"]]
        i=1
        coffee_no = 0
        for coffee_type in self.coffee_types:
            self.coffee_type_checkbox = Checkbutton(self, text=coffee_type[0], variable= coffee_type[1])
            self.coffee_type_checkbox.grid(row = i, column = 0, sticky=W)
            self.coffee_quantity = Entry(self)
            self.coffee_quantity.grid(row = i, column=1, sticky="news", padx=5,pady=2)
            self.coffee_types[coffee_no].append(self.coffee_quantity)
            coffee_no += 1
            i+= 1
        i += 1
        cakes_title = Label(self, text="CAKES")
        cakes_title.grid(row=i, columnspan=2)
        self.cake_types = [["San Sebastian Cheesecake", BooleanVar(),"sansebastian"], ["Mosaic Cake", BooleanVar(),"mosaic"], ["Carrot Cake", BooleanVar(),"carrot"]]
        i+=1

        cake_no = 0
        for cake_type in self.cake_types:
            self.cake_type_checkbox = Checkbutton(self, text=cake_type[0], variable=cake_type[1])
            self.cake_type_checkbox.grid(row=i, column=0, sticky=W)
            self.cake_quantity = Entry(self)
            self.cake_quantity.grid(row=i, column=1, sticky="news", padx=5,pady=2)
            self.cake_types[cake_no].append(self.cake_quantity)
            cake_no += 1
            i+=1

        self.discount_code_text = Label(self, text="Discount code, if any:",)
        self.discount_code_text.grid(row=i, column=0, sticky=W, padx=20)
        self.discount_code = Entry(self)
        self.discount_code.grid(row=i, column=1, sticky="news", padx=5,pady=2)
        i += 1

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(i, weight=1)

        self.create_button = Button(self,text ="Create", command = self.createOrder)
        self.create_button.grid(row = i, column = 0,sticky="news",padx=(5,2.5),pady=2)

        self.create_button = Button(self, text="Close", command = self.closeWindow)
        self.create_button.grid(row=i, column=1, sticky="news", padx=(2.5,5),pady=2)

    # Close button
    def closeWindow(self):
        self.cSocket.send("!DISCONNECT".encode())
        self.master.destroy()

    # Create order button
    def createOrder(self):
        clientMsg = "order;"
        if (self.discount_code.get() == ""):
            clientMsg += "nodiscountcode;"
        else:
            clientMsg += self.discount_code.get()
            clientMsg += ";"

        clientMsg += self.username

        errorflag = 0
        empty_count = 0
        quantity_error_flag = 0

        for coffee_type in self.coffee_types:
            if(not (coffee_type[1].get()) and coffee_type[3].get() == ""):
                empty_count += 1
            elif(not (coffee_type[1].get()) and coffee_type[3].get() != ""):
                quantity_error_flag = 1

        for cake_type in self.cake_types:
            if(not(cake_type[1].get()) and cake_type[3].get() == ""):
                empty_count += 1
            elif(not(cake_type[1].get()) and cake_type[3].get() != ""):
                quantity_error_flag = 1

        if(empty_count == (len(self.coffee_types) + len(self.cake_types))):
            messagebox.showinfo("Message", "Please enter an order")
        else:

            for coffee_type in self.coffee_types:
                if(coffee_type[1].get()):
                    clientMsg += ";"
                    clientMsg += coffee_type[2]
                    clientMsg += "-"
                    if(coffee_type[3].get() == ""):
                        errorflag = 1
                    else:
                        clientMsg += coffee_type[3].get()

            for cake_type in self.cake_types:
                if(cake_type[1].get()):
                    clientMsg += ";"
                    clientMsg += cake_type[2]
                    clientMsg += "-"
                    if(cake_type[3].get() == ""):
                        errorflag = 1
                    else:
                        clientMsg += cake_type[3].get()


            if(errorflag == 0 and quantity_error_flag == 0):
                # Sending message
                self.cSocket.send(clientMsg.encode())
                # Recieving message
                order_confirmation = self.cSocket.recv(1024).decode()

                #Showing the message on the screen
                order_confirmation = order_confirmation.split(";")
                messagebox.showinfo("Message", order_confirmation[0] +": Total price is "+order_confirmation[1])

            elif(errorflag == 1):
                messagebox.showinfo("Message", "Please fill necessary the quantity box(es)")

            elif(quantity_error_flag == 1):
                messagebox.showinfo("Message", "Please select necessary checkbox(ex)")

        for coffee_type in self.coffee_types:
            coffee_type[1].set(0)
            coffee_type[3].delete(0, 'end')
        for cake_type in self.cake_types:
            cake_type[1].set(0)
            cake_type[3].delete(0, 'end')
        self.discount_code.delete(0, 'end')


# Manager Panel
class ManagerPanel(Frame):
    def __init__(self, socket):
        Frame.__init__(self)

        #GUI Design
        self.master.title("Manager Panel")
        self.cSocket = socket
        self.grid()

        coffee_title = Label(self, text="REPORTS")
        coffee_title.grid(row=0)

        self.reports = [
                        ["report1","(1) What is the most popular coffee overall?"],
                        ["report2","(2) Which barista has the highest number of orders?"],
                        ["report3","(3) What is the most popular product for the orders with the discount code?"],
                        ["report4","(4) What is the most popular cake that is bought with expresso?"]
                                                                                                        ]

        self.strReport = StringVar()
        self.strReport.set(None)

        i = 1
        for report in self.reports:
            self.report_radiobutton = Radiobutton(self, text = report[1], value = report[0], variable=self.strReport)
            self.report_radiobutton.grid(row=i, column=0, sticky=W)
            i += 1

        self.create_button = Button(self, text="Create", command = self.showReport)
        self.create_button.grid(row=i, column=0, sticky="news", padx=(2.5, 1.25), pady=2)

        self.create_button = Button(self, text="Close", command=self.closeWindow)
        self.create_button.grid(row=i, column=1, sticky="news", padx=(1.25, 2.5), pady=2)

    # Close Button
    def closeWindow(self):
        self.cSocket.send("!DISCONNECT".encode())
        self.master.destroy()

    #Show Button
    def showReport(self):
        if(self.strReport.get() != None):
            clientMsg = self.strReport.get()
            self.cSocket.send(clientMsg.encode())
            # Checking which radio button is selected.
            # Inside of the if else statements receiving data from the server.
            if(clientMsg == "report1"):
                most_popular_coffees = self.cSocket.recv(1024).decode()
                if (len(most_popular_coffees.split(";")) == 1):
                    messagebox.showinfo("Message", "report1: There is no order")
                else:
                    most_popular_coffees = most_popular_coffees.split(";")
                    message = most_popular_coffees[0] + ": Most popular coffee overall is "
                    for i in range(1,len(most_popular_coffees)):
                        message += most_popular_coffees[i]
                        message += ", "
                    message = message[:-2]
                    messagebox.showinfo("Message", message)


            elif(clientMsg == "report2"):
                highest_order_baristas = self.cSocket.recv(1024).decode()
                if (len(highest_order_baristas.split(";")) == 1):
                    messagebox.showinfo("Message", "report2: There is no order")
                else:
                    highest_order_baristas = highest_order_baristas.split(";")
                    message = highest_order_baristas[0] + ": "
                    for i in range(1, len(highest_order_baristas)):
                        message += highest_order_baristas[i]
                        message += ", "
                    message = message[:-2]
                    message += " has the highest number of orders"
                    messagebox.showinfo("Message", message)


            elif (clientMsg == "report3"):
                most_popular_products = self.cSocket.recv(1024).decode()

                if(len(most_popular_products.split(";")) == 1):
                    messagebox.showinfo("Message", "report3: There is no order")
                else:
                    most_popular_products = most_popular_products.split(";")
                    message = most_popular_products[0] + ": Most popular product(s) for the orders with the discount code is: "
                    for i in range(1, len(most_popular_products)):
                        message += most_popular_products[i]
                        message += ", "
                    message = message[:-2]
                    messagebox.showinfo("Message", message)

            elif (clientMsg == "report4"):
                most_popular_cakes = self.cSocket.recv(1024).decode()

                if(len(most_popular_cakes.split(";")) == 1):
                    messagebox.showinfo("Message", "report4: There is no order")
                elif(most_popular_cakes.split(";")[1] == "noexpresso"):
                    messagebox.showinfo("Message", "report4: No expresso ordered yet")
                else:
                    most_popular_cakes = most_popular_cakes.split(";")
                    message = most_popular_cakes[0] +": Most popular cake that is bought with expresso is "
                    for i in range(1, len(most_popular_cakes)):
                        message += most_popular_cakes[i]
                        message += ", "
                    message = message[:-2]
                    messagebox.showinfo("Message", message)



if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5000
    socket = socket(AF_INET, SOCK_STREAM)
    socket.connect((HOST, PORT))
    serverMsg = socket.recv(1024).decode()

    # When the connection successful, login screen will be displayed.
    if(serverMsg == "CONNECTION SUCCESSFUL"):
        window = Authentication(socket)
        window.mainloop()





