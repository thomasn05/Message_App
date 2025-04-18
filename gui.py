import tkinter as tk
import ds_messenger as dm
from Profile import Profile
import time as t

class Friends:
    def __init__(self, name : str, messages : list[dict]) -> None:
        self.name = name
        self.messages = []
        for msg in messages:
            self.messages.append(dm.DirectMessage(
                recipient= msg['to'], 
                sender= msg['from'], 
                message= msg['message'], 
                timestamp= msg['time']))


class Direct_Messenger_GUI:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.ip = "168.235.86.101"

        self.master.withdraw()
        self.auth_window = tk.Toplevel(master=self.master)
        self.auth_window.title('Welcome')
        self.auth_window.geometry('250x150')
        self.auth_window.resizable(False, False)

        tk.Label(self.auth_window, text="Welcome to Direct Messenger!", font=("Arial", 12)).pack(pady=10)

        tk.Button(self.auth_window, text="Login", width=15, command=self.__login_screen).pack(pady=5)
        tk.Button(self.auth_window, text="Create Account", width=15, command=self.__create_account_screen).pack(pady=5)

        self.auth_window.bind('<Escape>', lambda _: self.master.quit())
        self.auth_window.protocol("WM_DELETE_WINDOW", self.master.quit)

    def __login_screen(self):
        self.auth_window.destroy()
        self.login_wn = tk.Toplevel(master=self.master)
        self.login_wn.title('Login')
        self.login_wn.geometry('250x130')
        self.login_wn.resizable(False, False)
        self.login_wn.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.login_wn.bind('<Escape>', lambda _: self.master.quit())

        tk.Label(self.login_wn, text='Username:').grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.login_wn)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.login_wn, text='Password:').grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_wn, show='*')
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_wn, text='Login', command=self.check_login).grid(row=2, column=0, columnspan=2, pady=10)

    def __create_account_screen(self):
        self.auth_window.destroy()
        self.create_wn = tk.Toplevel(master=self.master)
        self.create_wn.title('Create Account')
        self.create_wn.geometry('280x200')
        self.create_wn.resizable(False, False)
        self.create_wn.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.create_wn.bind('<Escape>', lambda _: self.master.quit())

        tk.Label(self.create_wn, text='Username:').grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_username = tk.Entry(self.create_wn)
        self.new_username.grid(row=0, column=1, padx=5)

        tk.Label(self.create_wn, text='Password:').grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_password = tk.Entry(self.create_wn, show='*')
        self.new_password.grid(row=1, column=1, padx=5)

        tk.Label(self.create_wn, text='Confirm Password:').grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.confirm_password = tk.Entry(self.create_wn, show='*')
        self.confirm_password.grid(row=2, column=1, padx=5)

        self.error_msg = tk.Label(self.create_wn, text="", fg="red")
        self.error_msg.grid(row=3, column=0, columnspan=2)

        tk.Button(self.create_wn, text='Create', command=self.check_create_user).grid(row=4, column=0, columnspan=2, pady=10)

    def check_create_user(self): #Check if the username is already taken and if the password is valid
        username = self.new_username.get()
        password = self.new_password.get()
        confirm_password = self.confirm_password.get()

        if password != confirm_password:
            self.error_msg.config(text="Passwords do not match")
            self.new_password.delete(0, tk.END)
            self.confirm_password.delete(0, tk.END)
            return

        if self.create_profile(username=username, password=password):

            self.create_wn.destroy()
            self.start_chat()
        else:
            self.error_msg.config(text="Username already taken")
            self.new_username.delete(0, tk.END)
            self.new_password.delete(0, tk.END)
            self.confirm_password.delete(0, tk.END)
            return

    def check_login(self): #Getting the info from login screen and create messenger and profile 
        username, password = self.name_entry.get(), self.password_entry.get()
        
        if (self.create_profile(username= username, password= password)):
            self.login_wn.destroy()
            self.start_chat()
        else:
            self.error_msg = tk.Label(self.login_wn, text= 'Invalid password', fg= 'red')
            self.error_msg.grid(row= 3, column= 0, columnspan= 2)
            self.password_entry.delete(0, tk.END)

    def create_profile(self, username, password) -> bool: #Create a profile for the user
        self.user_messenger = dm.DirectMessenger(dsuserver= self.ip, username= username, password= password)
        if self.user_messenger.error:
            return False
        
        else:
            self.user_profile = Profile(dsuserver= self.ip, username= self.user_messenger.username, password= self.user_messenger.password)
            self.user_profile.load_profile()
            return True

    def start_chat(self): #Actual chat GUI
        #GUI Config
        self.master.deiconify()
        self.master.title(f'Login in as: {self.user_profile.username}')
        self.master.geometry("720x480")
        self.master.rowconfigure((0, 4), weight= 1)
        self.master.rowconfigure((1, 2, 3), weight= 4)
        self.master.columnconfigure(0, weight= 1)
        self.master.columnconfigure(1, weight= 2)

        #Labels for friend list and chat log
        self.friend_list_label = tk.Label(self.master, text='Friends', font= ('Arial', 12, 'bold'))
        self.friend_list_label.grid(row=0, column=0, sticky='n', padx=5, pady=5)
        self.chat_log_label = tk.Label(self.master, text='Chat Log', font= ('Arial', 12, 'bold'))
        self.chat_log_label.grid(row=0, column=1, sticky='n', padx=5, pady=5)

        #scrollbars
        self.list_box_scrollbard = tk.Scrollbar(self.master, orient= 'vertical', width= 30)
        self.msg_scrollbard = tk.Scrollbar(self.master, orient= 'vertical', width= 30)
        self.list_box_scrollbard.grid(row=1, rowspan= 3, column= 0, sticky='nsw')
        self.msg_scrollbard.grid(row= 1, rowspan= 2, column= 1, sticky= 'nse')

        #friend list
        self.friend_listbox = tk.Listbox(self.master, selectmode= tk.SINGLE, width= 30, height= 30,
                                        borderwidth= 3, relief= 'raised', yscrollcommand= self.list_box_scrollbard.set)
        self.friend_listbox.grid(row= 1, rowspan= 3, column= 0, 
                                sticky= 'nes', pady= 5)
        self.friend_listbox.bind('<<ListboxSelect>>', lambda _ : self.show_history())

        #Adding friends to the listbox
        for friend in self.user_profile.friends:
            self.friend_listbox.insert(tk.END, friend)

        #messages history
        self.msg_history = tk.Text(self.master, wrap= tk.WORD, height= 5, width= 60, 
                                borderwidth= 3, relief= 'raised', yscrollcommand= self.msg_scrollbard.set)
        self.msg_history.grid(row= 1, rowspan= 2, column= 1, 
                            sticky= 'ns',padx= 2,  pady= 5)
        self.msg_history.config(state= tk.DISABLED)

        #message box
        self.msg_box = tk.Text(self.master, wrap= tk.WORD, height= 5, width= 40,
                                borderwidth= 3, relief= 'raised')
        self.msg_box.grid(row= 3, column= 1,
                        sticky= 'news', padx= 5, pady= 5)

        #Scrollbars config
        self.list_box_scrollbard.config(command= self.friend_listbox.yview)
        self.msg_scrollbard.config(command= self.msg_history.yview)

        #buttons
        self.add_button = tk.Button(self.master, text= 'Add Friend', width= 10, command= self.add_friend_popup)
        self.add_button.grid(row= 4, column= 0, sticky= 'nes', padx= 5, pady= 3)
        self.send_button = tk.Button(self.master, text= 'Send', width= 15, command= self.send_msg)
        self.send_button.grid(row= 4, column= 1, sticky= 'nes', padx= 5, pady= 3)

        self.master.after(1000, self.__update_new_msg)

    def show_history(self): #Show the msg history when user's friend is selected
        if self.friend_listbox.size() == 0: return

        selection = self.friend_listbox.curselection()
        if not selection: return #check if there is a selection
        name = self.friend_listbox.get(selection)
        self.chat_log_label.config(text= f'Chatting with {name}')

        curr_scroll = self.msg_history.yview() #use to keep scrollbar in the same place

        self.msg_history.config(state= tk.NORMAL)
        self.msg_history.delete('1.0', tk.END)

        msgs : dm.DirectMessage
        for msgs in self.user_profile.friends[name]: #Show the chat logs
            msg = msgs.message
            sender = msgs.sender
            time = t.strftime('%Y-%m-%d %I:%M %p', t.localtime(msgs.timestamp)) #Convert timestamp to readable format
            line = f"{time} {sender}: {msg}\n\n"

            self.msg_history.insert(tk.END, line)

        self.msg_history.config(state= tk.DISABLED)

        self.msg_history.yview_moveto(curr_scroll[0])

    def add_friend_popup(self): #Create a pop for user to enter friend's usernamme
        self.add_friend_wn = tk.Toplevel(master= self.master)
        self.add_friend_wn.title('Add a Friend')
        self.add_friend_wn.resizable(0,0)
        self.add_friend_label = tk.Label(master= self.add_friend_wn, text= 'Friend: ')
        self.add_friend_label.grid(row= 0, column= 0)

        self.add_friend_entry = tk.Entry(master= self.add_friend_wn)
        self.add_friend_entry.grid(row= 0, column= 1)

        self.add_friend_button = tk.Button(master= self.add_friend_wn, text= 'Add', command= self.add_friend)
        self.add_friend_button.grid(row= 1, column= 0, columnspan= 2)

    def add_friend(self): #Add the friend to profile and listbox
        friend = self.add_friend_entry.get()
        self.add_friend_entry.delete(0, tk.END)

        if friend == self.user_profile.username: #Check if user is trying to add themself
            error_popup = tk.Toplevel(master= self.master)
            error_label = tk.Label(master=error_popup, text= 'Cannot add yourself')
            error_label.grid(row= 0, column= 0)
            ok_button = tk.Button(master= error_popup, text= 'OK', command= error_popup.destroy)
            ok_button.grid(row= 1, column= 0, columnspan= 2)
            return

        if friend not in self.user_profile.friends: #Add New friend
            self.add_friend_wn.destroy()
            self.friend_listbox.insert(tk.END, friend)
        self.user_profile.add_friend(username= friend)
    
    def send_msg(self): #send the msg to other user
        msg = self.msg_box.get('1.0', 'end-1c')
        selection = self.friend_listbox.curselection()
        if msg and selection:#Check if a friend is selected and user is not sending an empty string
            friend = self.friend_listbox.get(selection)
            success = self.user_messenger.send(message= msg, recipient= friend)

            if success: #If msg is sent successfully
                self.msg_history.config(state= tk.NORMAL)
                self.msg_history.insert(tk.END, f'{self.user_profile.username}: {msg}\n\n')
                direct_msg = dm.DirectMessage(recipient= friend, sender= self.user_profile.username, message= msg, timestamp= t.time())
                self.user_profile.add_direct_message(direct_msg= direct_msg)
                self.msg_history.config(state= tk.DISABLED)

            else: #Create error popup
                error_popup = tk.Toplevel(master= self.master)
                error_label = tk.Label(master=error_popup, text= 'Cannot send message')
                error_label.grid(row= 0, column= 0)
                ok_button = tk.Button(master= error_popup, text= 'OK', command= error_popup.destroy)
                ok_button.grid(row= 1, column= 0, columnspan= 2)
        
        self.msg_box.delete('1.0', tk.END)

    def __update_new_msg(self): #Get new messages to update
        new_msgs = self.user_messenger.retrieve_new()
        self.__add_DirectMessage(direct_msgs= new_msgs)
        self.master.after(1000, self.__update_new_msg) #recursive call the function to keep getting new msg

    
    def __add_DirectMessage(self, direct_msgs : list[dm.DirectMessage]): #Add new msg to user profile
        for msg in direct_msgs:
            self.user_profile.add_friend(username= msg.sender)
            self.user_profile.add_direct_message(direct_msg= msg)
        self.show_history()

def main():
    wn = tk.Tk()
    gui = Direct_Messenger_GUI(wn)
    wn.bind('<Escape>', lambda _: wn.quit())
    wn.mainloop()