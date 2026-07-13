import customtkinter as ctk
import client_network
import client_util
import ipaddress
import socket

JWT = None

class ConnectScreen(ctk.CTkFrame):
    def __init__(self, master, on_connect, **kwargs):
        super().__init__(master, **kwargs)
        self.on_connect = on_connect
        
        self.center_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.center_frame.pack(expand=True, anchor="center")
        
        # IP Entry
        self.ip_label = ctk.CTkLabel(master=self.center_frame,text='IP Address:' )
        self.ip_entry = ctk.CTkEntry(master=self.center_frame, placeholder_text="127.0.0.1", corner_radius=8)
        
        self.ip_label.pack(side="top", pady=(0, 5))
        self.ip_entry.pack(side="top", pady=(0, 15))
        self.ip_entry.insert(0, '127.0.0.1')

     
        # Port Entry
        self.port_label = ctk.CTkLabel(master=self.center_frame,text='Port:' )
        self.port_entry = ctk.CTkEntry(master=self.center_frame, placeholder_text="5050", corner_radius=8)
        
        self.port_label.pack(side="top", pady=(0, 5))
        self.port_entry.pack(side="top", pady=(0, 15))
        self.port_entry.insert(0, '5050')
        
        # Connect Button & Status Label
        self.connect_btn = ctk.CTkButton(master=self.center_frame, text='Connect to server', command=self.try_to_connect)
        self.status_label = ctk.CTkLabel(master=self.center_frame, text='')
        self.connect_btn.pack(side="top", pady=(0, 5))
        self.status_label.pack(side="top", pady=(0, 15))
        
    def try_to_connect(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        print(f"Details: {ip}:{port}")

        try:
            ipaddress.IPv4Address(ip)
        except ValueError:
            try:
                    ipaddress.IPv6Address(ip)
            except ValueError:
                    self.status_label.configure(text="Not a valid ip!", text_color='red')
                    return
            else:
                    client_network.SERVER_IP = ip
                    client_network.SOCK_FAMILY = socket.AF_INET6
        else:
            client_network.SERVER_IP = ip
            client_network.SOCK_FAMILY = socket.AF_INET
        
        try:
            port = int(port)
            if not 0 <= port <= 65535:
                raise ValueError
        except:
            self.status_label.configure(text="Not a valid port!", text_color='red')
            return
        client_network.SERVER_PORT = port
        
        if client_util.check_connection(client_network.SERVER_IP, client_network.SERVER_PORT, client_network.SOCK_FAMILY):
            self.status_label.configure(text="Connected Successfully!", text_color='green')
            self.on_connect()
        else:
            self.status_label.configure(text="Cannot Connect!", text_color='red')
            return

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login, **kwargs):
        super().__init__(master, **kwargs)
        self.on_login = on_login
        
        self.center_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.center_frame.pack(expand=True, anchor="center")
        
        # Username Entry
        self.username_label = ctk.CTkLabel(master=self.center_frame,text='Username:' )
        self.username_entry = ctk.CTkEntry(master=self.center_frame, placeholder_text="username", corner_radius=8)
        
        self.username_label.grid(row = 0, column = 0, padx = 10, pady = 5)
        self.username_entry.grid(row = 0, column = 1, padx = 10, pady = 5)
        
        # Password Entry
        self.password_label = ctk.CTkLabel(master=self.center_frame,text='Password:' )
        self.password_entry = ctk.CTkEntry(master=self.center_frame, placeholder_text="password", corner_radius=8, show='*')
        
        self.password_label.grid(row = 1, column = 0, padx = 10, pady = 5)
        self.password_entry.grid(row = 1, column = 1, padx = 10, pady = 5)
        
        # Buttons
        self.login_btn = ctk.CTkButton(master=self.center_frame, text='Login', command=lambda: self.on_submit('login'))
        self.signup_btn = ctk.CTkButton(master=self.center_frame, text='Sign Up',  command=lambda: self.on_submit('signup'))
        self.signup_btn.grid(row = 2, column = 0, padx = 10, pady = 5)
        self.login_btn.grid(row = 2, column = 1, padx = 10, pady = 5)
        
        # Status Label
        self.status_label = ctk.CTkLabel(master=self.center_frame,text='')
        self.status_label.grid(row = 3, column = 0, padx = 10, pady = 5)

    def on_submit(self, type: str):
        global JWT
        username = self.username_entry.get()  
        password = self.password_entry.get()  

        if type == 'signup':
            try:
                client_network.register(username, password)
            except Exception as e:
                self.status_label.configure(text = f"Error: {e}", text_color='red') 
                return
        try:
            JWT, client_util.private_key = client_network.login(username, password)
        except Exception as e:
            self.status_label.configure(text = f"Error: {e}", text_color='red') 
        else:
            self.status_label.configure(text = f"Logged in!", text_color='green')
            self.on_login()

                
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        
        # Connect stage
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.connect_screen = ConnectScreen(self, self.on_connect_to_server)
        self.connect_screen.grid(row=0, column=0, sticky="nsew")

        # Login screen
        self.login_screen = LoginScreen(self, self.on_login)
        
        
        
    def on_connect_to_server(self):
        self.connect_screen.grid_forget()
        self.login_screen.grid(row=0, column=0, sticky="nsew")

    def on_login(self):
        pass

if __name__ == '__main__':
    app = App()
    app.mainloop()