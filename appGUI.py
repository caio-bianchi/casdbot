# app_gui.py
# pip install google-auth google-auth-oauthlib google-auth-httplib2

from bot import Bot
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import PIL


WINDOWS_SIZE = "1080x720"
ICON = "icon.ico"

# Set the appearance mode and theme
ctk.set_appearance_mode("System")  # "System", "Dark", or "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"

class WelcomeWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("CASDbot - Welcome")
        self.master.geometry(WINDOWS_SIZE)  # Size of the welcome window
        self.master.wm_iconbitmap(ICON)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(master, text="Bem vindo ao CASDbot,\n o enviador automático de mensagens do CASD!", font=("Montserrat", 20))
        self.welcome_label.pack(pady=20)

        # Proceed button
        self.proceed_button = ctk.CTkButton(master, text="Prosseguir para o Login", command=self.open_login_window)
        self.proceed_button.pack(pady=10)

    def open_login_window(self):
        self.master.destroy()  # Close the welcome window
        login_root = ctk.CTk()  # Create the login window
        login_window = LoginWindow(login_root)
        login_root.mainloop()

class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("CASDbot - Login")
        self.master.geometry(WINDOWS_SIZE)
        self.master.wm_iconbitmap(ICON)

        # Username Label and Entry
        self.username_label = ctk.CTkLabel(master, text="Username")
        self.username_label.pack(pady=10)
        self.username_entry = ctk.CTkEntry(master)
        self.username_entry.pack(pady=10)

        # Password Label and Entry
        self.password_label = ctk.CTkLabel(master, text="Password")
        self.password_label.pack(pady=10)
        self.password_entry = ctk.CTkEntry(master, show='*')
        self.password_entry.pack(pady=10)

        # Login Button
        self.login_button = ctk.CTkButton(master, text="Login", corner_radius=32, command=self.login)
        self.login_button.pack(pady=20)

    def login(self):
        # Simulated login check
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Here you can check the credentials
        if username == "admin" and password == "password":  # Example credentials
            messagebox.showinfo("Successo", "Login bem sucedido!")
            self.master.destroy()  # Close login window
            self.open_main_window()  # Open the main application window
        else:
            messagebox.showerror("Erro", "Usuário ou Senha incorretos.")

    def open_main_window(self):
        # Create the main application window
        main_window = ctk.CTk()
        bot = Bot()
        app = SelectionWindow(main_window, bot)
        main_window.mainloop()

class SelectionWindow:
    def __init__(self, master: ctk.CTk, bot: Bot):
        self.master = master
        self.bot = bot

        # Set up the GUI
        self.master.title("CASDbot")
        self.master.geometry(WINDOWS_SIZE)

        # Select the window

        self.welcome_label = ctk.CTkLabel(master, text="O que você deseja fazer hoje?", font=("Montserrat", 20))
        self.welcome_label.pack(pady=20)

        # Send messages button
        self.send_message_button = ctk.CTkButton(master, text="Enviar mensagens por planilha.", command=self.open_send_message_window)
        self.send_message_button.pack(pady=10)

        self.send_message_button = ctk.CTkButton(master, text="Enviar mensagens por template.", command=self.open_send_message_template_window)
        self.send_message_button.pack(pady=10)
    
    def open_send_message_window(self):
        # Create the main application window
        send_message_window = ctk.CTk()
        bot = Bot()
        app = SendMessageWindow(send_message_window, bot)
        self.master.destroy()
        send_message_window.mainloop()

    def open_send_message_template_window(self):
        # Create the main application window
        send_email_window = ctk.CTk()
        bot = Bot()
        app = SendMessageTemplateWindow(send_email_window, bot)
        self.master.destroy()
        send_email_window.mainloop()

class SendMessageWindow:
    def __init__(self, root: ctk.CTk, bot: Bot):
        self.root = root
        self.bot = bot
        self.sheet = None  # This will hold the DataFrame after loading the file

        # Set up the GUI
        self.root.title("CASDbot")
        self.root.geometry(WINDOWS_SIZE)

        # Create and place Load File button
        self.load_button = ctk.CTkButton(root, text="Load Excel File", command=self.load_file)
        self.load_button.pack(pady=20)

        # Create and place Send Messages button
        self.send_button = ctk.CTkButton(root, text="Send Messages", command=self.send_messages)
        self.send_button.pack(pady=20)

    def load_file(self):
        '''Open a file dialog to select an Excel file, which is saved as the current 'sheet' attribute.'''
        file_path = filedialog.askopenfilename(
            title="Select Excel File", filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
        )

        if file_path:
            try:
                # Load the Excel file into a DataFrame
                self.sheet = pd.read_excel(file_path)
                messagebox.showinfo("Success", "File loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def send_messages(self):
        '''Ensure a file is loaded before sending messages'''
        if self.sheet is not None:
            try:
                self.bot.send_messages(self.sheet)
                messagebox.showinfo("Success", "Messages sent successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send messages: {e}")
        else:
            messagebox.showwarning("Warning", "Please load a file first.")

class SendMessageTemplateWindow:
    def __init__(self, master: ctk.CTk, bot: Bot):
        self.master = master
        self.bot = bot
        self.sheet = None  # This will hold the DataFrame after loading the file

        # Set up the GUI
        self.master.title("CASDbot")
        self.master.geometry(WINDOWS_SIZE)

        self.welcome_label = ctk.CTkLabel(master, text="Não implementado.", font=("Montserrat", 20))
        self.welcome_label.pack(pady=20)
        

# Initialize the application
if __name__ == "__main__":
    welcome_root = ctk.CTk()  # Use customtkinter's CTk as the welcome window
    welcome_window = WelcomeWindow(welcome_root)
    welcome_root.mainloop()
