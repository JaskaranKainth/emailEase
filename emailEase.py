from shutil import move, copyfile
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import imaplib
import bcrypt
from database import create_connection, create_tables, insert_data

# Initialize database
connection = create_connection()

def save_user(username, password, email_address):
    # Insert user info into database
    user_data = {"username": username, "password": password, "email_address": email_address}
    insert_data(connection, "users", user_data)

def hash(password):
    # Hash password before saving to database
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def extract_keywords(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read().lower()
            keywords = ["work", "school", "marketing", "SENG2020", "Project", "subscription", "billing", "Test", "Conestoga", ""]  # Add your desired keywords
            found_keywords = [keyword for keyword in keywords if keyword in content]
            return found_keywords
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "Please provide a keywords file.")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"Error reading file: {str(e)}")
        return []

def display_keywords():
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

    if file_path:
        keywords_found = extract_keywords(file_path)
        keywords_text.delete(1.0, tk.END)
        keywords_text.insert(tk.END, "\n".join(keywords_found))

def get_folder_names():
    folders = fetch_all_data(connection, "folders")
    return [folder["name"] for folder in folders]

def move_to_folder(folder_name, content):
    # Check if the folder exists in the local directory
    if not os.path.exists(folder_name):
        messagebox.showerror("Folder Not Found", f"The folder '{folder_name}' does not exist.")
        return

    # Create a folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    try:
        # Save the content to a file in the specified folder
        file_path = os.path.join(folder_name, "tempfile.txt")
        with open(file_path, "w") as file:
            file.write(content)

        # Optionally, you can copy the content instead of moving
        # copyfile(file_path, os.path.join(folder_name, "copied_file.txt"))

        messagebox.showinfo("Success", f"Content moved to the folder '{folder_name}'")
    except Exception as e:
        messagebox.showerror("Error", f"Error moving content: {str(e)}")


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

    # Import keywords from the text file
    try:
        with open("keywords.txt", "r") as file:
            keywords_from_file = file.read().splitlines()
    except FileNotFoundError:
        enable_ui()
        messagebox.showerror("File Not Found", "Please provide a keywords file.")
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

    for email_subject in keywords_from_file:
        # Insert into folder data
        folder_data = {"name": folder_name, "user_id": None}
        insert_data(connection, "folders", folder_data)

        # Insert email data
        email_data = {"subject": email_subject, "folder_id": None, "user_id": None}
        insert_data(connection, "emails", email_data)

        status, messages = mail.search(None, "SUBJECT", f'"{email_subject}"')
        message_ids = messages[0].split()

        for message_id in message_ids:
            # Move to folder only if any keyword matches the email subject
            if any(keyword.lower() in email_subject.lower() for keyword in keywords_from_file):
                move_to_folder(folder_name, message_id, mail)
                feedback_msg += f"Moved to '{folder_name}': {email_subject}\n"

    mail.close()
    mail.logout()

    enable_ui()

    # Print keywords from the text file
    keywords_from_file_str = ', '.join(keywords_from_file)
    feedback_msg += f"\nKeywords from File:\n{keywords_from_file_str}\n"

    # Print keywords from the emails_text box
    keywords_from_textbox = emails_text.get("1.0", tk.END).strip()
    feedback_msg += f"\nKeywords in Emails Textbox:\n{keywords_from_textbox}\n"
    messagebox.showinfo("Sorting Complete", "Emails sorted successfully!")

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

# The main application window
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
move_to_folder_button = tk.Button(main_frame, bg="#C0C5C1", fg="#574B60", text="Move to Folder", bd=0, highlightcolor="#C0C5C1", highlightbackground="#C0C5C1", command=lambda: move_to_folder(folder_entry.get(), emails_text.get("1.0", tk.END).strip()), font=("Arial", 12, "bold"), relief=tk.FLAT)
import_button = tk.Button(main_frame, text="Import Emails", fg="#574B60", bd=0, highlightcolor="#C0C5C1", highlightbackground="#C0C5C1", command=import_emails, font=("Arial", 12, "bold"), relief=tk.FLAT)
sort_button = tk.Button(main_frame, text="Parse Email", fg="#574B60", bd=0, highlightcolor="#C0C5C1", highlightbackground="#C0C5C1", command=display_keywords, font=("Arial", 12, "bold"), relief=tk.FLAT)
emails_label = tk.Label(main_frame, text="Emails Content", bg="#C0C5C1", fg="#574B60", font=("Arial", 15, "bold"))
keywords_label = tk.Label(main_frame, text="Keywords", bg="#C0C5C1", fg="#574B60", font=("Arial", 15, "bold"))
emails_text = scrolledtext.ScrolledText(main_frame, bg="#7D8491", width=50, height=5, font=("Arial", 15))
keywords_text = scrolledtext.ScrolledText(main_frame, bg="#7D8491", wrap=tk.WORD, width=40, height=5, font=("Arial", 15))

folder_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
folder_entry.grid(row=0, column=1, padx=10, pady=10)
move_to_folder_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")  # Align to the right
import_button.grid(row=1, column=1, pady=10, padx=5, sticky="w")  # Align to the left
sort_button.grid(row=1, column=1, pady=10, padx=5, sticky="e")  # Align to the right
emails_label.grid(row=2, column=0, columnspan=3, pady=10)
keywords_label.grid(row=4, column=0, columnspan=3, pady=10)
emails_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
keywords_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

app.grid_rowconfigure(1, weight=1)  # Allow main content to expand vertically

app.mainloop()