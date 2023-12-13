from shutil import move
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import imaplib
import bcrypt
import email
from venv import create
from database import create_connection, create_tables, insert_data

#initialize database
connection = create_connection()


def save_user(username, password, email_address):
    #insert user info into database
    user_data = {"username": username, "password": password, "email_address": email_address}
    insert_data(connection, "users", user_data)

def hash(password):
    #hash password before saving to database
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def sort_emails():
    disable_ui()

    # Get input from UI
    folder_name = folder_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    # Validate
    if not folder_name or not username or not password:
        messagebox.showerror("Invalid Input", "Please fill in all fields.")
        enable_ui()
        return

    # Prompt user for keywords
    keyword_input = simpledialog.askstring("Keyword Input", "Enter keywords (comma-separated):")
    
    if not keyword_input:
        enable_ui()
        return

    # Split keywords into a list
    keywords = [keyword.strip() for keyword in keyword_input.split(',')]

    # Import emails from the file
    try:
        with open("emails_to_sort.txt", "r") as file:
            emails_to_sort = file.read().splitlines()
    except FileNotFoundError:
        enable_ui()
        messagebox.showerror("File Not Found", "Please import emails first.")
        return
    
    # Save user info
    hashed_password = hash(password)
    save_user(username, hashed_password, username)
    
    # Init connection
    connection = create_connection()

    # Create tables if needed
    create_tables(connection)

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    feedback_msg = ""

    for email_subject in emails_to_sort:
        # Insert into folder data
        folder_data = {"name": folder_name, "user_id": None}
        insert_data(connection, "folders", folder_data)

        # Insert email data
        email_data = {"subject": email_subject, "folder_id": None, "user_id": None}
        insert_data(connection, "emails", email_data)

        status, messages = mail.search(None, "SUBJECT", f'"{email_subject}"')
        message_ids = messages[0].split()

        for message_id in message_ids:
            # Prompt user for keywords for each email
            keyword_input = simpledialog.askstring("Keyword Input", f"Enter keywords for '{email_subject}' (comma-separated):")
            if keyword_input:
                keywords = [keyword.strip() for keyword in keyword_input.split(',')]

            # Move to folder only if any keyword matches the email subject
            if any(keyword.lower() in email_subject.lower() for keyword in keywords):
                move_to_folder(folder_name, message_id, mail)
                feedback_msg += f"Moved to '{folder_name}': {email_subject}\n"

    mail.close()
    mail.logout()

    enable_ui()

    feedback_text.insert(tk.END, feedback_msg)
    feedback_text.config(state=tk.DISABLED)

    messagebox.showinfo("Sorting Complete", "Emails sorted successfully!")

def move_to_folder(folder_name, message_id, mail):
    mail.create(folder_name)
    mail.copy(message_id, folder_name)
    mail.store(message_id, '+FLAGS', '(\Deleted)')
    mail.expunge()

def disable_ui():
    sort_button.config(state=tk.DISABLED)
    folder_entry.config(state=tk.DISABLED)
    import_button.config(state=tk.DISABLED)

def enable_ui():
    sort_button.config(state=tk.NORMAL)
    folder_entry.config(state=tk.NORMAL)
    import_button.config(state=tk.NORMAL)

def import_emails():
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

    if file_path:
        try:
            with open(file_path, "r") as file:
                content = file.read()
                emails_text.delete(1.0, tk.END)
                emails_text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")

# connection.close()

# the main application window
app = tk.Tk()
app.title("EmailEase")

# Styling
app.geometry("580x500")
app.configure(bg="#C0C5C1")

# Title
title_label = tk.Label(app, text="EmailEase", bg="#C0C5C1", fg="#574B60", font=("Arial", 30, "bold", "italic"))
title_label.grid(row=0, column=0, pady=(20, 30), padx=20)

# Main content
main_frame = tk.Frame(app, bg="#C0C5C1")
main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
main_frame.columnconfigure(0, weight=1)  
main_frame.columnconfigure(1, weight=1)  
main_frame.rowconfigure(2, weight=1)  
main_frame.rowconfigure(3, weight=1) 

folder_label = tk.Label(main_frame, text="Enter A Folder Name:", bg="#C0C5C1", fg="#574B60", font=("Arial", 15, "bold"))
folder_entry = tk.Entry(main_frame, width=30, bg="#7D8491", font=("Arial", 12))
move_to_folder_button = tk.Button(main_frame, bg="#C0C5C1", fg="#574B60", text="Move to Folder", bd=0, highlightcolor="#C0C5C1", highlightbackground="#C0C5C1", command=move_to_folder, font=("Arial", 12, "bold"), relief=tk.FLAT)
import_button = tk.Button(main_frame, text="Import Emails", fg="#574B60", bd=0, highlightcolor="#C0C5C1", highlightbackground="#C0C5C1", command=import_emails, font=("Arial", 12, "bold"), relief=tk.FLAT)
sort_button = tk.Button(main_frame, text="Parse Email", fg="#574B60", bd=0, highlightcolor="#C0C5C1", highlightbackground="#C0C5C1", command=sort_emails, font=("Arial", 12, "bold"), relief=tk.FLAT)
feedback_text = scrolledtext.ScrolledText(main_frame, bg="#7D8491", width=50, height=5, state=tk.DISABLED, font=("Arial", 15))
emails_text = scrolledtext.ScrolledText(main_frame, bg="#7D8491", width=50, height=5, font=("Arial", 15))

folder_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
folder_entry.grid(row=0, column=1, padx=10, pady=10)
move_to_folder_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")  # Align to the right
import_button.grid(row=1, column=1, pady=10, padx=5, sticky="w")  # Align to the left
sort_button.grid(row=1, column=1, pady=10, padx=5, sticky="e")  # Align to the right
feedback_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
emails_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

app.grid_rowconfigure(1, weight=1)  # Allow main content to expand vertically

app.mainloop()