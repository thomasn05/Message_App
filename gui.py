import tkinter as tk
import ds_messenger as dm
from Profile import Profile
import time as t

class Friends:
    def __init__(self, name : str, messages : list[dict]) -> None:
        self.name = name
        self.messages = []
        for msg in messages:
            self.messages.append(dm.DirectMessage(recipient= msg['to'], sender= msg['from'], message= msg['message'], timestamp= msg['time']))


class Direct_Messenger_GUI:
    def __init__(self, master : tk.Tk) -> None:
        self.master = master
        self.ip = "168.235.86.101"

        #creating login screen
        self.master.withdraw()
        self.login_wn = tk.Toplevel(master= self.master)
        self.login_wn.title('Login')
        self.login_wn.resizable(0,0)
        self.login_wn.geometry('200x120')
        self.login_wn.bind('<Escape>', func= lambda _: self.master.quit())

        #Creating widget
        self.name = tk.Label(self.login_wn, text= 'Username: ')
        self.password = tk.Label(self.login_wn, text= 'Password: ')
        self.name_entry = tk.Entry(self.login_wn, )
        self.password_entry = tk.Entry(self.login_wn, show= '*')
        self.login_button = tk.Button(self.login_wn, text= 'Login', command= self.create_user)

        #placing widget
        widget : tk.Widget
        count : int
        for count, widget in enumerate(self.login_wn.winfo_children()):
            widget.grid(row= count % 2, column= count //2)
        self.login_button.grid(row= 2, column= 0, columnspan= 2)

    def create_user(self): #Getting the info from login screen and create messenger and profile 
        username, password = self.name_entry.get(), self.password_entry.get()
        self.name_entry.delete(0, tk.END) 
        self.password_entry.delete(0, tk.END)
        self.user_messenger = dm.DirectMessenger(dsuserver= self.ip, username= username, password= password)

        if self.user_messenger.error: #Show error msg if cannot create direct messenger
            self.error_msg = tk.Label(self.login_wn, text= self.user_messenger.error, wraplength= 200)
            self.error_msg.grid(row= 3, column= 0, columnspan= 2)
            return

        self.user_profile = Profile(dsuserver= self.ip, username= username, password= password) #Create a user profile and load it
        self.user_profile.load_profile()
        self.start_chat()#Starts up the actual GUI

    def start_chat(self): #Actual chat GUI
        #GUI Config
        self.master.deiconify()
        self.login_wn.destroy()
        self.master.title('Direct Meseenger Chat')
        self.master.geometry("720x480")
        self.master.rowconfigure((0, 1, 2, 3), weight= 5)
        self.master.rowconfigure(4, weight= 1)
        self.master.columnconfigure(0, weight= 1)
        self.master.columnconfigure(1, weight= 2)

        #scrollbars
        self.list_box_scrollbard = tk.Scrollbar(self.master, orient= 'vertical', width= 30)
        self.msg_scrollbard = tk.Scrollbar(self.master, orient= 'vertical', width= 30)
        self.list_box_scrollbard.grid(row=0, rowspan= 4, column= 0, sticky='nsw')
        self.msg_scrollbard.grid(row= 0, rowspan= 3, column= 1, sticky= 'nse')

        #friend list
        self.friend_listbox = tk.Listbox(self.master, selectmode= tk.SINGLE, width= 30, 
                                        borderwidth= 3, relief= 'raised', yscrollcommand= self.list_box_scrollbard.set)
        self.friend_listbox.grid(row= 0, rowspan= 4, column= 0, 
                                sticky= 'nes', pady= 5)
        self.friend_listbox.bind('<<ListboxSelect>>', lambda _ : self.show_history())

        for friend in self.user_profile.friends:
            self.friend_listbox.insert(tk.END, friend)

        #messages history
        self.msg_history = tk.Text(self.master, wrap= tk.WORD, height= 5, width= 60, 
                                borderwidth= 3, relief= 'raised', yscrollcommand= self.msg_scrollbard.set)
        self.msg_history.grid(row= 0, rowspan= 3, column= 1, 
                            sticky= 'ns',padx= 2,  pady= 5)
        self.msg_history.config(state= tk.DISABLED)

        #message box
        self.msg_box = tk.Text(self.master, wrap= tk.WORD, height= 5, width= 40,
                                borderwidth= 3, relief= 'raised')
        self.msg_box.grid(row= 3, column= 1,
                        sticky= 'news', padx= 5, pady= 5)

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
        name = self.friend_listbox.get(self.friend_listbox.curselection())
        self.msg_history.config(state= tk.NORMAL)
        self.msg_history.delete('1.0', tk.END)
        for msgs in self.user_profile.friends[name]:
            msg = msgs['message']
            sender = msgs['from']
            self.msg_history.insert(tk.END, f'{sender}: {msg}\n\n')
        self.msg_history.config(state= tk.DISABLED)

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
        if friend not in self.user_profile.friends:
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
        if self.friend_listbox.curselection(): #update the current msg_history if any is selected
            self.show_history()

def main():
    wn = tk.Tk()
    gui = Direct_Messenger_GUI(wn)
    wn.bind('<Escape>', lambda _: wn.quit())
    wn.mainloop()
