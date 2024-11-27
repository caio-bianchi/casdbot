# app_gui.py
# pip install google-auth google-auth-oauthlib google-auth-httplib2
import os
from bot import Bot
import customtkinter as ctk
from tkinter import filedialog, messagebox, Text, ttk
import pandas as pd
from PIL import Image, ImageTk

WINDOWS_SIZE = "1080x720"
bg_color = "#26657b"
button_color = "#ffb444"
border_color = "#e69500"  # Border color (this should match the background or complement it)
hover_color = "#ff9800"
if "nt" == os.name:
    ICON = "icon.ico"    # for windows
else:
    ICON = "@icon.xbm"   # for linux
# Set the appearance mode and theme
ctk.set_appearance_mode("Light")  # "System", "Dark", or "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"


class BaseWindow:
    def __init__(self, master, title, size=WINDOWS_SIZE, report=None):
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
    def __init__(self, root: ctk.CTk, bot: Bot):
        self.root = root
        self.bot = bot
        self.sheet = None  # This will hold the DataFrame after loading the file
        self.report = None  # This will hold the DataFrame after loading the file

        # Set up the GUI
        self.root.title("CASDbot")
        self.root.geometry(WINDOWS_SIZE)
        self.root.configure(fg_color=bg_color)
        self.root.wm_iconbitmap(ICON)

        # Button common style
        button_style = {
            "corner_radius": 8,  # Slightly rounded corners for a smoother look
            "fg_color": button_color,  # Background color
            "height": 30,  # Height of the button
            "font": ("Montserrat", 20, "bold"),  # Bold text with Montserrat font
            "text_color": "white",  # Text color
            "border_width": 2,  # Border width to create the raised effect
            "border_color": border_color,  # Border color (this should match the background or complement it)
            "hover_color": hover_color
        }

        # "Back" button in the top-left corner
        self.back_button = ctk.CTkButton(
            root, text="← Voltar", command=self.go_back, **button_style
        )
        self.back_button.pack(anchor="nw", padx=10, pady=10)

        # Top frame for buttons
        self.top_frame = ctk.CTkFrame(root, fg_color=bg_color)
        self.top_frame.pack(pady=10)

        # Bottom frame for Treeview display
        self.bottom_frame = ctk.CTkFrame(root, fg_color=bg_color)
        self.bottom_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Load File button
        self.load_button = ctk.CTkButton(self.top_frame, text="Carregar Excel", command=self.load_file, **button_style)
        self.load_button.pack(pady=5)

        # Send Messages button
        self.send_button = ctk.CTkButton(self.top_frame, text="Enviar Mensagens", command=self.send_messages, **button_style)
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
                messagebox.showerror("Error", f"Falha ao carregar arquivo: {e}")

    def send_messages(self):
        pass

    def close_window(self):
        self.root.destroy()

    def open_review_window(self):
        self.close_window()
        review = ctk.CTk()
        ReviewWindow(review, self.report)
        review.mainloop()

    def go_back(self):
        # Closes current window and returns to the SelectionWindow
        self.close_window()
        main_window = ctk.CTk()
        bot = Bot()
        SelectionWindow(main_window, bot)
        main_window.mainloop()


class WelcomeWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master, title="CASDbot")
        self.master.attributes("-fullscreen", False)  # Start in windowed mode

        # Load the original image
        self.original_image = Image.open("imagens/welcome_window.jpg")

        # Resize the image to match the window size initially
        self.bg_image = ctk.CTkImage(self.original_image, size=(1080, 720))

        # Add the image as the background
        self.background_label = ctk.CTkLabel(self.master, image=self.bg_image, text="")
        self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        button_style = {
            "corner_radius": 8,  # Slightly rounded corners for a smoother look
            "fg_color": button_color,  # Background color
            "height": 60,  # Height of the button
            "font": ("Montserrat", 20, "bold"),  # Bold text with Montserrat font
            "text_color": "white",  # Text color
            "border_width": 2,  # Border width to create the raised effect
            "border_color": border_color,  # Border color (this should match the background or complement it)
            "hover_color": hover_color
        }

        # Place the button directly on the master, ensuring it's on top
        self.proceed_button = ctk.CTkButton(
            self.master,
            text="Começar a mandar mensagens!", command=self.open_main_window, **button_style)
        self.proceed_button.place(relx=0.5, rely=0.6, anchor="center")
        
        self.help_button = ctk.CTkButton(self.master, text="Ajuda", **button_style, command=self.show_help_popup)
        self.help_button.place(relx=0.5, rely=0.75, anchor="center")  # Adjust position for the help button

        # Bind the resize event to adjust the image size dynamically
        self.master.bind("<Configure>", self.resize_background)
    
    def show_help_popup(self):
        # Create a popup window for the help section
        help_popup = ctk.CTkToplevel(self.master)
        help_popup.title("Ajuda")

        # Set the icon for the popup window
        help_popup.iconbitmap(ICON)

        # Bring the popup to the front
        help_popup.attributes('-topmost', 1)  # This ensures that the popup is always on top

        # Set up the content of the popup
        help_text = """
        Bem-vindo ao CASDbot! Aqui está como você pode usar o sistema:

        1. Selecione envio por Whatsapp ou por e-mail.
        2. Envie as mensagens/e-mail por planilha ou criar um template.
        3. No caso de enviar por template, você pode usar {Header da Coluna} para escrever a célula da coluna
        4. No caso de criar template, é possível selecionar imagens para envio.
        5. Para inserir uma imagem basta escrever o caminho da imagem entre dois elementos '[file]'.
        6. Outra forma, é de utilizar o botão de buscar imagem e selecionar o arquivo e, após isso, utilizar um elemento '[queue]' para selecionar onde na mensagem aparecerá a imagem
        7. Acompanhe o progresso e baixe os relatórios ao final.
        """

        help_label = ctk.CTkLabel(help_popup, text=help_text, justify="left", font=("Montserrat", 14))
        help_label.pack(padx=20, pady=20)

        # Add a "Close" button to close the help popup
        close_button = ctk.CTkButton(help_popup, text="Fechar", command=help_popup.destroy)
        close_button.pack(pady=(0, 10))

    def resize_background(self, event):
        """Resize the background image to fit the window."""
        new_width = event.width
        new_height = event.height
        resized_image = self.original_image.resize((new_width, new_height), Image.ANTIALIAS)
        self.bg_image = ctk.CTkImage(resized_image, size=(new_width, new_height))
        self.background_label.configure(image=self.bg_image)

    def open_main_window(self):
        # Create the main application window
        self.close_window()
        main_window = ctk.CTk()
        bot = Bot()
        app = SelectionWindow(main_window, bot)
        main_window.mainloop()


class SelectionWindow(BaseWindow):
    def __init__(self, master: ctk.CTk, bot: Bot):
        super().__init__(master, title="CASDbot")
        self.master = master
        self.bot = bot

        # Load the original image for background
        try:
            self.original_image = Image.open("imagens/main_window.jpg")
            print("Image loaded successfully.")
        except Exception as e:
            print(f"Failed to load image: {e}")
            return

        # Resize the image to match the window size initially
        self.bg_image = ctk.CTkImage(self.original_image, size=(1080, 720))

        # Add the image as the background using a label
        self.background_label = ctk.CTkLabel(self.master, image=self.bg_image, text="")
        # Set the background image at the very back of the window
        self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Button common style
        button_style = {
            "corner_radius": 8,  # Slightly rounded corners for a smoother look
            "fg_color": button_color,  # Background color
            "height": 60,  # Height of the button
            "font": ("Montserrat", 20, "bold"),  # Bold text with Montserrat font
            "text_color": "white",  # Text color
            "border_width": 2,  # Border width to create the raised effect
            "border_color": border_color,  # Border color (this should match the background or complement it)
            "hover_color": hover_color
        }

        # Create and place buttons directly on the master window (on top of the background image)
        self.send_message_button = ctk.CTkButton(self.master, text="Enviar mensagens por planilha",
                                                 command=self.open_send_message_window, **button_style)
        self.send_message_button.place(relx=0.5, rely=0.4, anchor="center")

        self.send_message_template_button = ctk.CTkButton(self.master, text="Enviar mensagens por template",
                                                          command=self.open_send_message_template_window,
                                                          **button_style)
        self.send_message_template_button.place(relx=0.5, rely=0.5, anchor="center")

        self.send_email_button = ctk.CTkButton(self.master, text="Enviar e-mails por planilha",
                                               command=self.open_send_email_window, **button_style)
        self.send_email_button.place(relx=0.5, rely=0.6, anchor="center")

        self.send_email_template_button = ctk.CTkButton(self.master, text="Enviar e-mails por template",
                                                        command=self.open_send_email_template_window, **button_style)
        self.send_email_template_button.place(relx=0.5, rely=0.7, anchor="center")
        
        self.help_button = ctk.CTkButton(self.master, text="Ajuda", **button_style, command=self.show_help_popup)
        self.help_button.place(relx=0.5, rely=0.8, anchor="center")  # Adjust position for the help button

        # Bind the resize event to adjust the background image size dynamically
        self.master.bind("<Configure>", self.resize_background)
    
    def show_help_popup(self):
        # Create a popup window for the help section
        help_popup = ctk.CTkToplevel(self.master)
        help_popup.title("Ajuda")

        # Set the icon for the popup window
        help_popup.iconbitmap(ICON)

        # Bring the popup to the front
        help_popup.attributes('-topmost', 1)  # This ensures that the popup is always on top

        # Set up the content of the popup
        help_text = """
                Bem-vindo ao CASDbot! Aqui está como você pode usar o sistema:

                1. Selecione envio por Whatsapp ou por e-mail.
                2. Envie as mensagens/e-mail por planilha ou criar um template.
                3. No caso de enviar por template, você pode usar {Header da Coluna} para escrever a célula da coluna
                4. No caso de criar template, é possível selecionar imagens para envio.
                5. Para inserir uma imagem basta escrever o caminho da imagem entre dois elementos '[file]'.
                6. Outra forma, é de utilizar o botão de buscar imagem e selecionar o arquivo e, após isso, utilizar um elemento '[queue]' para selecionar onde na mensagem aparecerá a imagem
                7. Acompanhe o progresso e baixe os relatórios ao final.
                """

        help_label = ctk.CTkLabel(help_popup, text=help_text, justify="left", font=("Montserrat", 14))
        help_label.pack(padx=20, pady=20)

        # Add a "Close" button to close the help popup
        close_button = ctk.CTkButton(help_popup, text="Fechar", command=help_popup.destroy)
        close_button.pack(pady=(0, 10))

    def resize_background(self, event):
        """Resize the background image to fit the window."""
        new_width = event.width
        new_height = event.height
        resized_image = self.original_image.resize((new_width, new_height), Image.ANTIALIAS)
        self.bg_image = ctk.CTkImage(resized_image, size=(new_width, new_height))
        self.background_label.configure(image=self.bg_image)

    def open_send_message_window(self):
        # Create the main application window
        send_message_window = ctk.CTk()
        bot = Bot()
        app = SendMessageWindow(send_message_window, bot)
        self.master.destroy()
        send_message_window.mainloop()

    def open_send_message_template_window(self):
        # Create the main application window
        send_message_window = ctk.CTk()
        bot = Bot()
        app = SendMessageTemplateWindow(send_message_window, bot)
        self.master.destroy()
        send_message_window.mainloop()

    def open_send_email_window(self):
        # Create the main application window
        send_email_window = ctk.CTk()
        app = EmailLoginWindow(send_email_window, False)
        self.master.destroy()
        send_email_window.mainloop()

    def open_send_email_template_window(self):
        # Create the main application window
        send_email_window = ctk.CTk()
        app = EmailLoginWindow(send_email_window, True)
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
                messagebox.showerror("Error", f"Falha ao enviar mensagens: {e}")

            self.open_review_window()
        else:
            messagebox.showwarning("Warning", "Carregue o arquivo Excel primeiro")


class SendMessageTemplateWindow(MessageWindow):
    def __init__(self, root: ctk.CTk, bot: Bot):
        super().__init__(root, bot)
        self.bot.clear_queue()
        # Template Text input
        template_label = ctk.CTkLabel(self.top_frame, text="Insira o Texto do Template:", font=("Montserrat", 20), text_color="white")
        template_label.pack(pady=(10, 0))

        self.template_text = ctk.CTkTextbox(self.top_frame, height=100, width=800)
        self.template_text.pack(pady=(5, 15), padx=20)

        # Button common style
        button_style = {
            "corner_radius": 8,  # Slightly rounded corners for a smoother look
            "fg_color": button_color,  # Background color
            "height": 30,  # Height of the button
            "font": ("Montserrat", 20, "bold"),  # Bold text with Montserrat font
            "text_color": "white",  # Text color
            "border_width": 2,  # Border width to create the raised effect
            "border_color": border_color,  # Border color (this should match the background or complement it)
            "hover_color": hover_color
        }

        self.add_file_button = ctk.CTkButton(self.top_frame, text="Adicionar Arquivo", command=self.load_files, **button_style)
        self.add_file_button.pack(pady=10)

        # Bottom frame for Treeview display
        self.other_frame = ctk.CTkFrame(root, fg_color=bg_color)
        self.other_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview widget for displaying the DataFrame
        self.files_display = ttk.Treeview(self.other_frame, show="headings")
        self.files_display.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar to Treeview
        self.scrollbar2 = ttk.Scrollbar(self.other_frame, orient="vertical", command=self.df_display.yview)
        self.files_display.configure(yscroll=self.scrollbar2.set)
        self.scrollbar2.pack(side="right", fill="y")
    
    def display_files(self):
        # Clear any existing content in the Treeview
        self.files_display.delete(*self.files_display.get_children())

        # Set up columns if DataFrame is loaded
        files_sheet = pd.DataFrame(self.bot.file_queue, columns=["Arquivos"])

        if files_sheet is not None:
            # Configure columns and headings in Treeview
            self.files_display["column"] = list(files_sheet.columns)
            for col in files_sheet.columns:
                self.files_display.heading(col, text=col)
                self.files_display.column(col, anchor="center", width=100)

            # Insert each row of the DataFrame into the Treeview
            for _, row in files_sheet.iterrows():
                self.files_display.insert("", "end", values=list(row))
        else:
            messagebox.showinfo("Info", "No data loaded to display.")

    def load_files(self):
        '''Open a file dialog to select the file to be sent.'''
        file_path = filedialog.askopenfilename(
            title="Select File", filetypes=(("Image Files", "*.png"), ("All files", "*.*"))
        )

        if file_path:
            try:
                self.bot.add_to_queue(file_path)
                self.display_files()
            except Exception as e:
                messagebox.showerror("Error", f"Falha ao carregar arquivo: {e}")

    def send_messages(self):
        '''Ensure a file is loaded before sending messages'''
        if self.sheet is not None:
            try:
                # Update template_content
                self.template_content = self.template_text.get("1.0", "end-1c")

                sheet_with_messages = self.bot.generate_messages_from_template(self.sheet, self.template_content, whatsapp_flag=True)

                self.report = self.bot.send_messages(sheet_with_messages)
            except Exception as e:
                messagebox.showerror("Error", f"Falha ao enviar as mensagens: {e}")

            self.open_review_window()
        else:
            messagebox.showwarning("Warning", "Por favor carregar o Excel primeiro")

class EmailLoginWindow(BaseWindow):
    def __init__(self, master, template_flag: bool, bg_color="lightblue"):
        super().__init__(master, title="Email - Login")
        self.template_flag = template_flag
        self.username: str
        self.password: str

        self.master.bind("<Return>", lambda event: self.login())
        
        button_style = {
            "corner_radius": 32,  # Rounded corners
            "fg_color": button_color,  # Button background color
            "height": 30,  # Button height
            "font": ("Montserrat", 16, "bold"),  # Font style
            "text_color": "white",  # Text color
            "border_width": 2,  # Border width
            "border_color": border_color,  # Border color
            "hover_color": hover_color  # Hover color
        }

        # Back button in the top-left corner
        self.back_button = ctk.CTkButton(
            master, text="← Voltar", command=self.go_back, **button_style
        )
        self.back_button.place(x=10, y=10)

        # Username Label and Entry
        self.username_frame = ctk.CTkFrame(self.center_frame, fg_color=bg_color)
        self.username_frame.pack(pady=10, fill="x")

        self.username_label = ctk.CTkLabel(self.username_frame, text="Email de envio", font=("Montserrat", 14), text_color="black")
        self.username_label.pack(pady=(0, 5))
        self.username_entry = ctk.CTkEntry(self.username_frame)
        self.username_entry.pack()

        # Password Label and Entry
        self.password_frame = ctk.CTkFrame(self.center_frame, fg_color=bg_color)
        self.password_frame.pack(pady=10, fill="x")

        self.password_label = ctk.CTkLabel(self.password_frame, text="Senha de 16 caracteres", font=("Montserrat", 14), text_color="black")
        self.password_label.pack(pady=(0, 5))
        self.password_entry = ctk.CTkEntry(self.password_frame, show='*')
        self.password_entry.pack()

        # Login Button
        self.login_button = ctk.CTkButton(self.center_frame, text="Login", command=self.login, **button_style)
        self.login_button.pack(pady=20)

    def login(self):
        # Simulated login check
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Here you can check the credentials
        if '@gmail.com' not in username:  # Example credentials
            messagebox.showerror("Erro", "Usuário Inválido")
        elif len(password) != 19 or len(password.split(' ')) != 4:
            messagebox.showerror("Erro", "Senha Inválida")
        else:
            self.close_window()  # Close login window
            self.open_main_window(username, password)  # Open the main application window

    def open_main_window(self, username, password):
        # Create the main application window
        main_window = ctk.CTk()
        bot = Bot(sender_email=username, email_password=password)
        if self.template_flag:
            app = SendEmailTemplateWindow(main_window, bot)
        else:
            app = SendEmailWindow(main_window, bot)
        main_window.mainloop()
    
    def go_back(self):
        # Closes current window and returns to the SelectionWindow
        self.close_window()
        main_window = ctk.CTk()
        bot = Bot()
        SelectionWindow(main_window, bot)
        main_window.mainloop()


class SendEmailWindow(MessageWindow):
    def __init__(self, root: ctk.CTk, bot: Bot):
        super().__init__(root, bot)

    def send_messages(self):
        '''Ensure a file is loaded before sending emails'''
        if self.sheet is not None:
            try:
                self.report = self.bot.send_emails(self.sheet)
            except Exception as e:
                messagebox.showerror("Error", f"Falha ao enviar os emails: {e}")

            self.open_review_window()
        else:
            messagebox.showwarning("Warning", "Carregar o arquivo Excel primeiro")


class SendEmailTemplateWindow(MessageWindow):
    def __init__(self, root: ctk.CTk, bot: Bot):
        super().__init__(root, bot)
        # Template Text input
        self.bot.clear_queue()
        template_label = ctk.CTkLabel(self.top_frame, text="Insira o Texto do Template:", font=("Montserrat", 20), text_color="white")
        template_label.pack(pady=(10, 0))

        self.template_text = ctk.CTkTextbox(self.top_frame, height=100, width=800)
        self.template_text.pack(pady=(5, 15), padx=20)
        
        button_style = {
            "corner_radius": 32,  # Rounded corners
            "fg_color": button_color,  # Button background color
            "height": 30,  # Button height
            "font": ("Montserrat", 16, "bold"),  # Font style
            "text_color": "white",  # Text color
            "border_width": 2,  # Border width
            "border_color": border_color,  # Border color
            "hover_color": hover_color  # Hover color
        }
        
        self.add_file_button = ctk.CTkButton(self.top_frame, text="Adicionar Arquivo", command=self.load_files, **button_style)
        self.add_file_button.pack(pady=10)
        
        # Bottom frame for Treeview display
        self.other_frame = ctk.CTkFrame(root, fg_color=bg_color)
        self.other_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview widget for displaying the DataFrame
        self.files_display = ttk.Treeview(self.other_frame, show="headings")
        self.files_display.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar to Treeview
        self.scrollbar2 = ttk.Scrollbar(self.other_frame, orient="vertical", command=self.df_display.yview)
        self.files_display.configure(yscroll=self.scrollbar2.set)
        self.scrollbar2.pack(side="right", fill="y")
    
    def display_files(self):
        # Clear any existing content in the Treeview
        self.files_display.delete(*self.files_display.get_children())

        # Set up columns if DataFrame is loaded
        files_sheet = pd.DataFrame(self.bot.file_queue, columns=["Arquivos"])

        if files_sheet is not None:
            # Configure columns and headings in Treeview
            self.files_display["column"] = list(files_sheet.columns)
            for col in files_sheet.columns:
                self.files_display.heading(col, text=col)
                self.files_display.column(col, anchor="center", width=100)

            # Insert each row of the DataFrame into the Treeview
            for _, row in files_sheet.iterrows():
                self.files_display.insert("", "end", values=list(row))
        else:
            messagebox.showinfo("Info", "No data loaded to display.")

    
    def load_files(self):
        '''Open a file dialog to select the file to be sent.'''
        file_path = filedialog.askopenfilename(
            title="Select File", filetypes=(("All files", "*.*"), ("Image Files", "*.png"))
        )

        if file_path:
            try:
                self.bot.add_to_queue(file_path)
                self.display_files()
            except Exception as e:
                messagebox.showerror("Error", f"Falha ao carregar arquivo: {e}")
      
    def send_messages(self):
        '''Ensure a file is loaded before sending emails'''
        if self.sheet is not None:
            try:
                # Update template_content
                self.template_content = self.template_text.get("1.0", "end-1c")

                sheet_with_messages = self.bot.generate_messages_from_template(self.sheet, self.template_content, whatsapp_flag=False)

                self.report = self.bot.send_emails(sheet_with_messages)
            except Exception as e:
                messagebox.showerror("Error", f"Falha ao enviar as mensagens: {e}")

            self.open_review_window()
        else:
            messagebox.showwarning("Warning", "Carregar o arquivo Excel primeiro")


class ReviewWindow(BaseWindow):
    def __init__(self, master, report = None):
        super().__init__(master, title="CASDbot", report=report)
        # Button common style
        button_style = {
            "corner_radius": 8,  # Slightly rounded corners for a smoother look
            "fg_color": button_color,  # Background color
            "height": 30,  # Height of the button
            "font": ("Montserrat", 20, "bold"),  # Bold text with Montserrat font
            "text_color": "white",  # Text color
            "border_width": 2,  # Border width to create the raised effect
            "border_color": border_color,  # Border color (this should match the background or complement it)
            "hover_color": hover_color
        }
        # "Back" button in the top-left corner
        self.back_button = ctk.CTkButton(
            master, text="← Voltar", command=self.go_back, **button_style
        )
        self.back_button.place(x=0, y=0)

        # Treeview widget for displaying the DataFrame
        self.df_display = ttk.Treeview(self.center_frame, show="headings")
        self.df_display.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar to Treeview
        self.scrollbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.df_display.yview)
        self.df_display.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Download Report button
        self.download_button = ctk.CTkButton(master, text="Baixar Relatório", command=self.download_report, **button_style)
        self.download_button.pack(pady=10)
        
        # Download Report button
        self.failed_button = ctk.CTkButton(master, text="Baixar Linhas Falhas", command=self.failed_report, **button_style)
        self.failed_button.pack(pady=10)

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
            messagebox.showinfo("Info", "Nenhum dado carregado para apresentar")

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
                    messagebox.showinfo("Success", "Relatório baixado com sucesso")
                except Exception as e:
                    messagebox.showerror("Error", f"Falha ao salvar relatório: {e}")
        else:
            messagebox.showwarning("Warning", "Nenhum dado de relatório para mostrar")

    def failed_report(self):
        # Check if the report is loaded
        if self.report is not None:
            final = self.report[self.report['Status'] != 'Sucesso']
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Report"
            )

            if file_path:
                try:
                    final.to_excel(file_path, index=False)
                    messagebox.showinfo("Success", "Relatório baixado com sucesso")
                except Exception as e:
                    messagebox.showerror("Error", f"Falha ao salvar relatório: {e}")
        else:
            messagebox.showwarning("Warning", "Nenhum dado de relatório para mostrar")


    def go_back(self):
        # Closes current window and returns to the SelectionWindow
        self.close_window()
        main_window = ctk.CTk()
        bot = Bot()
        SelectionWindow(main_window, bot)
        main_window.mainloop()

# Initialize the application
if __name__ == "__main__":
    welcome_root = ctk.CTk()  # Use customtkinter's CTk as the welcome window
    welcome_window = WelcomeWindow(welcome_root)
    welcome_root.mainloop()
