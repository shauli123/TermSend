import customtkinter as ctk
import client_network
import client_util
import ipaddress
import socket
import threading
from ctk_markdown import CTkMarkdown

JWT = None
MESSAGE_LIST = []


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
            client_util.current_username = username
            client_util.current_password = password
            self.on_login()

class MessageSelect(ctk.CTkScrollableFrame):
    def __init__(self, master, on_select, **kwargs):
        super().__init__(master, **kwargs)
        self.on_select = on_select
        self.columnconfigure(0, weight=1)
        self.bind("<Configure>", self.on_frame_resize)
        
    def refresh_messages(self, message_list):
        for widget in self.winfo_children():
            widget.destroy()
                
        for i, msg in enumerate(message_list):
            len_of_showed_msg = 10
            if not len(msg['content']) > 10:
                len_of_showed_msg = len(msg['content'])
            
            select_btn = ctk.CTkButton(master=self,
                                       command=lambda m=msg: self.on_select(m['thread_id']), 
                                       text=f"{msg['sender']} | {msg['date']} | {msg['content'][:len_of_showed_msg]}...")
            select_btn._text_label.configure(wraplength=300)
            select_btn.add_to_grid = True 
            select_btn.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
    
    def on_frame_resize(self, event):
        self.update_buttons_wrap()

    def update_buttons_wrap(self):
        available_width = self.winfo_width() - 30
        if available_width > 0:
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget._text_label.configure(wraplength=available_width)

class ThreadView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.current_thread = -1
    
    def load_thread(self, thread_id, message_list):
        for widget in self.winfo_children():
            widget.destroy()
            
        thread_list = [msg for msg in message_list if msg['thread_id'] == thread_id][::-1]
        self.current_thread = thread_id
        for _, msg in enumerate(thread_list):
            is_me = msg["sender"] == client_util.current_username
            if is_me:
                bg_color = ("#d1e7dd", "#2b2b2b")
                border_color = ("#0f5132", "#1f6aa5") 
            else:
                bg_color = ("#f8f9fa", "#242424")     
                border_color = ("#dee2e6", "#3e3e3e")
            
            msg_frame = ctk.CTkFrame(
                master=self, 
                fg_color=bg_color, 
                border_color=border_color, 
                border_width=1,
                corner_radius=8
            )
            msg_frame.pack(fill="x", padx=10, pady=5, anchor="e" if is_me else "w")

            header_label = ctk.CTkLabel(
            master=msg_frame, 
            text=f"{msg['sender']} | {msg['date']}", 
            )
            header_label.pack(anchor="w", padx=10, pady=(5, 2))

            body_text = CTkMarkdown(
                        master=msg_frame, 
                        markdown_text=msg['content'],
                        width=400, 
                        fg_color="transparent", 
                        activate_scrollbars=False
                    )
            
            body_text.pack(fill="x", padx=10, pady=(0, 5))
            body_text.update_idletasks()
            bbox = body_text._textbox.bbox("end-1c")

            if bbox:
                x, y, width, height = bbox
                actual_pixel_height = y + height + 10
                body_text.configure(height=actual_pixel_height)
                    
class MainScreen(ctk.CTkFrame):
    def __init__(self, master, jwt_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.jwt_callback = jwt_callback
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        
        self.inner_frame_msgs = ctk.CTkFrame(master=self)
        self.inner_frame_msgs.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
               
        self.inner_frame_msgs.rowconfigure(0, weight=1)
        self.inner_frame_msgs.columnconfigure(0, weight=8)
        self.inner_frame_msgs.columnconfigure(1, weight=1)

        self.msg_select = MessageSelect(self.inner_frame_msgs, on_select=self.on_select_msg)
        self.msg_select.grid(row=0, column=1, sticky="nsew")
        
        self.thread_view = ThreadView(master=self.inner_frame_msgs)
        self.thread_view.grid(row=0, column=0, sticky="nsew")

    def refresh_message_list(self):
        fetch_thread = threading.Thread(target=self.fetch_msgs_wrapper)
        fetch_thread.start()
        
    def fetch_msgs_wrapper(self):
        global MESSAGE_LIST
        try:
            MESSAGE_LIST = client_util.fetch_and_get_all_msgs(JWT)[::-1]
        except:
            self.jwt_callback()
            return
        
        self.after(0, self.refresh_frames_with_msgs, MESSAGE_LIST)
        
    def refresh_frames_with_msgs(self, message_list):
        self.msg_select.refresh_messages(message_list)
    
    def on_select_msg(self, thread_id):
        self.thread_view.load_thread(thread_id, MESSAGE_LIST)
        
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x500")
        self.title("TermSend GUI")
        
        # Connect stage
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.connect_screen = ConnectScreen(self, self.on_connect_to_server)
        self.connect_screen.grid(row=0, column=0, sticky="nsew")

        # Login screen
        self.login_screen = LoginScreen(self, self.on_login)
        
        # Main screen
        self.main_screen = MainScreen(self, self.jwt_callback)
        
    def jwt_callback(self):
        self.main_screen.grid_forget()
        self.login_screen.grid(row=0, column=0, sticky="nsew")  
        
    def on_connect_to_server(self):
        self.connect_screen.grid_forget()
        self.login_screen.grid(row=0, column=0, sticky="nsew")

    def on_login(self):
        self.login_screen.grid_forget()
        self.main_screen.grid(row=0, column=0, sticky="nsew")
        self.main_screen.refresh_message_list()


if __name__ == '__main__':
    app = App()
    app.mainloop()