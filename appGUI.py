# app_gui.py
# pip install google-auth google-auth-oauthlib google-auth-httplib2

from bot import Bot
import customtkinter as ctk
from tkinter import filedialog, messagebox, Text, ttk
import pandas as pd

WINDOWS_SIZE = "1080x720"
ICON = "icon.ico"

# Set the appearance mode and theme
ctk.set_appearance_mode("System")  # "System", "Dark", or "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"


class BaseWindow:
    def __init__(self, master, title, size=WINDOWS_SIZE, bg_color="lightblue", report=None):
        self.master = master
        self.master.title(title)
        self.master.geometry(size)
        self.master.wm_iconbitmap(ICON)
        self.master.configure(fg_color=bg_color)
        self.report = report  # This will hold the DataFrame after loading the file

        # Central frame for content
        self.center_frame = ctk.CTkFrame(master, fg_color=bg_color)
        self.center_frame.pack(expand=True)

    def close_window(self):
        self.master.destroy()


class MessageWindow:
    def __init__(self, root: ctk.CTk, bot: Bot, bg_color="lightblue"):
        self.root = root
        self.bot = bot
        self.sheet = None  # This will hold the DataFrame after loading the file
        self.report = None  # This will hold the DataFrame after loading the file

        # Set up the GUI
        self.root.title("CASDbot")
        self.root.geometry(WINDOWS_SIZE)
        self.root.configure(fg_color=bg_color)

        # Top frame for buttons
        self.top_frame = ctk.CTkFrame(root, fg_color=bg_color)
        self.top_frame.pack(pady=10)

        # Bottom frame for Treeview display
        self.bottom_frame = ctk.CTkFrame(root, fg_color=bg_color)
        self.bottom_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Load File button
        self.load_button = ctk.CTkButton(self.top_frame, text="Load Excel File", command=self.load_file)
        self.load_button.pack(pady=5)

        # Send Messages button
        self.send_button = ctk.CTkButton(self.top_frame, text="Send Messages", command=self.send_messages)
        self.send_button.pack(pady=5)

        # Treeview widget for displaying the DataFrame
        self.df_display = ttk.Treeview(self.bottom_frame, show="headings")
        self.df_display.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar to Treeview
        self.scrollbar = ttk.Scrollbar(self.bottom_frame, orient="vertical", command=self.df_display.yview)
        self.df_display.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

    def display_dataframe(self):
        # Clear any existing content in the Treeview
        self.df_display.delete(*self.df_display.get_children())

        # Set up columns if DataFrame is loaded
        if self.sheet is not None:
            # Configure columns and headings in Treeview
            self.df_display["column"] = list(self.sheet.columns)
            for col in self.sheet.columns:
                self.df_display.heading(col, text=col)
                self.df_display.column(col, anchor="center", width=100)

            # Insert each row of the DataFrame into the Treeview
            for _, row in self.sheet.iterrows():
                self.df_display.insert("", "end", values=list(row))
        else:
            messagebox.showinfo("Info", "No data loaded to display.")

    def load_file(self):
        '''Open a file dialog to select an Excel file, which is saved as the current 'sheet' attribute.'''
        file_path = filedialog.askopenfilename(
            title="Select Excel File", filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
        )

        if file_path:
            try:
                # Load the Excel file into a DataFrame
                self.sheet = pd.read_excel(file_path)
                self.display_dataframe()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def send_messages(self):
        pass

    def close_window(self):
        self.root.destroy()

    def open_review_window(self):
        self.close_window()
        review = ctk.CTk()
        ReviewWindow(review, self.report)
        review.mainloop()


class WelcomeWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master, title="CASDbot - Welcome")

        # Welcome message
        self.welcome_label = ctk.CTkLabel(self.center_frame,
                                          text="Bem vindo ao CASDbot,\n o enviador automático de mensagens do CASD!",
                                          font=("Montserrat", 20))
        self.welcome_label.pack(pady=20)

        # Proceed button
        self.proceed_button = ctk.CTkButton(self.center_frame, text="Prosseguir para o Login",
                                            command=self.open_login_window)
        self.proceed_button.pack(pady=10)

    def open_login_window(self):
        self.close_window()
        login_root = ctk.CTk()
        LoginWindow(login_root)
        login_root.mainloop()


class LoginWindow(BaseWindow):
    def __init__(self, master, bg_color="lightblue"):
        super().__init__(master, title="CASDbot - Login")

        self.master.bind("<Return>", lambda event: self.login())

        # Username Label and Entry
        self.username_frame = ctk.CTkFrame(self.center_frame, fg_color=bg_color)
        self.username_frame.pack(pady=10, fill="x")

        self.username_label = ctk.CTkLabel(self.username_frame, text="Username")
        self.username_label.pack(pady=(0, 5))
        self.username_entry = ctk.CTkEntry(self.username_frame)
        self.username_entry.pack()

        # Password Label and Entry
        self.password_frame = ctk.CTkFrame(self.center_frame, fg_color=bg_color)
        self.password_frame.pack(pady=10, fill="x")

        self.password_label = ctk.CTkLabel(self.password_frame, text="Password")
        self.password_label.pack(pady=(0, 5))
        self.password_entry = ctk.CTkEntry(self.password_frame, show='*')
        self.password_entry.pack()

        # Login Button
        self.login_button = ctk.CTkButton(self.center_frame, text="Login", corner_radius=32, command=self.login)
        self.login_button.pack(pady=20)

    def login(self):
        # Simulated login check
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Here you can check the credentials
        if username == "admin" and password == "password":  # Example credentials
            self.close_window()  # Close login window
            self.open_main_window()  # Open the main application window
        else:
            messagebox.showerror("Erro", "Usuário ou Senha incorretos.")

    def open_main_window(self):
        # Create the main application window
        main_window = ctk.CTk()
        bot = Bot()
        app = SelectionWindow(main_window, bot)
        main_window.mainloop()


class SelectionWindow(BaseWindow):
    def __init__(self, master: ctk.CTk, bot: Bot):
        super().__init__(master, title="CASDbot")
        self.master = master
        self.bot = bot

        # Select the window
        self.welcome_label = ctk.CTkLabel(self.center_frame, text="O que você deseja fazer hoje?", font=("Montserrat", 20))
        self.welcome_label.pack(pady=20)

        # Send messages button
        self.send_message_button = ctk.CTkButton(self.center_frame, text="Enviar mensagens por planilha.", command=self.open_send_message_window)
        self.send_message_button.pack(pady=10)

        self.send_message_button = ctk.CTkButton(self.center_frame, text="Enviar mensagens por template.", command=self.open_send_message_template_window)
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


class SendMessageWindow(MessageWindow):
    def __init__(self, root: ctk.CTk, bot: Bot):
        super().__init__(root, bot)

    def send_messages(self):
        '''Ensure a file is loaded before sending messages'''
        if self.sheet is not None:
            try:
                self.report = self.bot.send_messages(self.sheet)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send messages: {e}")

            self.open_review_window()
        else:
            messagebox.showwarning("Warning", "Please load a file first.")


class SendMessageTemplateWindow(MessageWindow):
    def __init__(self, root: ctk.CTk, bot: Bot):
        super().__init__(root, bot)
        # Template Text input
        template_label = ctk.CTkLabel(self.top_frame, text="Enter Template Text:")
        template_label.pack(pady=(10, 0))

        self.template_text = ctk.CTkTextbox(self.top_frame, height=100, width=800)
        self.template_text.pack(pady=(5, 15), padx=20)

    def send_messages(self):
        '''Ensure a file is loaded before sending messages'''
        if self.sheet is not None:
            try:
                # Update template_content
                self.template_content = self.template_text.get("1.0", "end-1c")

                sheet_with_messages = self.bot.generate_messages_from_template(self.sheet, self.template_content)

                self.report = self.bot.send_messages(sheet_with_messages)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send messages: {e}")

            self.open_review_window()
        else:
            messagebox.showwarning("Warning", "Please load a file first.")


class ReviewWindow(BaseWindow):
    def __init__(self, master, report=None):
        super().__init__(master, title="CASDbot", report=report)

        # Treeview widget for displaying the DataFrame
        self.df_display = ttk.Treeview(self.center_frame, show="headings")
        self.df_display.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar to Treeview
        self.scrollbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.df_display.yview)
        self.df_display.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Download Report button
        self.download_button = ctk.CTkButton(master, text="Download Report", command=self.download_report)
        self.download_button.pack(pady=10)

        self.display_dataframe()

    def display_dataframe(self):
        # Clear any existing content in the Treeview
        self.df_display.delete(*self.df_display.get_children())

        # Set up columns if DataFrame is loaded
        if self.report is not None:
            # Configure columns and headings in Treeview
            self.df_display["column"] = list(self.report.columns)
            for col in self.report.columns:
                self.df_display.heading(col, text=col)
                self.df_display.column(col, anchor="center", width=100)

            # Insert each row of the DataFrame into the Treeview
            for _, row in self.report.iterrows():
                self.df_display.insert("", "end", values=list(row))
        else:
            messagebox.showinfo("Info", "No data loaded to display.")

    def download_report(self):
        # Check if the report is loaded
        if self.report is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Report"
            )

            if file_path:
                try:
                    self.report.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", "Report downloaded successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save report: {e}")
        else:
            messagebox.showwarning("Warning", "No report data to save.")

# Initialize the application
if __name__ == "__main__":
    welcome_root = ctk.CTk()  # Use customtkinter's CTk as the welcome window
    welcome_window = WelcomeWindow(welcome_root)
    welcome_root.mainloop()
