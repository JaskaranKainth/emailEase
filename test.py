import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from database import create_connection, create_tables, insert_data

# initialize database
connection = create_connection()

def login_and_upload():
    # Get input from UI
    email = email_entry.get()
    password = password_entry.get()

    # Validate
    if not email or not password:
        messagebox.showerror("Invalid Input", "Please enter both email and password.")
        return

    # Replace with your login logic
    user_data = {"username": email, "password": password, "email_address": email}
    insert_data(connection, "users", user_data)

    # After successful login, enable other UI elements
    folder_entry.config(state=tk.NORMAL)
    upload_button.config(state=tk.NORMAL)

def create_folder_and_upload():
    # Get input from UI
    folder_name = folder_entry.get()

    # Validate
    if not folder_name:
        messagebox.showerror("Invalid Input", "Please enter a folder name.")
        return

    # Insert folder data into the database
    folder_data = {"name": folder_name, "user_id": None}
    insert_data(connection, "folders", folder_data)

    # Allow email upload
    file_upload_button.config(state=tk.NORMAL)

def upload_email():
    # Get input from UI
    folder_name = folder_entry.get()

    # Validate
    if not folder_name:
        messagebox.showerror("Invalid Input", "Please enter a folder name.")
        return

    # Open file dialog to select a text file
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

    if file_path:
        try:
            # Read content from the file
            with open(file_path, "r") as file:
                content = file.read()

            # Insert email data into the database
            email_data = {"subject": "", "content": content, "sender": "", "timestamp": "", "folder_id": None}
            insert_data(connection, "emails", email_data)

            messagebox.showinfo("Email Uploaded", "Email successfully uploaded to the database!")

        except Exception as e:
            messagebox.showerror("Error", f"Error reading or uploading file: {str(e)}")

def show_data_tables():
    # Fetch data from the database
    data = fetch_all_data(connection)

    # Display data in scrolled text widget
    data_text.config(state=tk.NORMAL)
    data_text.delete(1.0, tk.END)
    data_text.insert(tk.END, data)
    data_text.config(state=tk.DISABLED)

def fetch_all_data(connection):
    """
    Function: fetch_all_data(connection)
    Description: Fetch all data from the 'users', 'folders', and 'emails' tables.
    Parameters:
        connection: MySQL database connection object.
    Returns: data (str): Formatted string containing all data from the tables.
    """
    if connection is not None:
        try:
            cursor = connection.cursor(dictionary=True)

            # Fetch users data
            cursor.execute("SELECT * FROM users")
            users_data = cursor.fetchall()

            # Fetch folders data
            cursor.execute("SELECT * FROM folders")
            folders_data = cursor.fetchall()

            # Fetch emails data
            cursor.execute("SELECT * FROM emails")
            emails_data = cursor.fetchall()

            cursor.close()

            return f"Users Data:\n{users_data}\n\nFolders Data:\n{folders_data}\n\nEmails Data:\n{emails_data}"

        except Error as e:
            print(f"Error fetching all data: {str(e)}")
            return "Error fetching data"

# the main application window
app = tk.Tk()
app.title("EmailEase")

# Styling
app.geometry("400x300")
app.configure(bg="#C0C5C1")

# Main content
main_frame = tk.Frame(app, bg="#C0C5C1")
main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Email and Password Entry
email_label = tk.Label(main_frame, text="Email:", bg="#C0C5C1", font=("Arial", 12))
password_label = tk.Label(main_frame, text="Password:", bg="#C0C5C1", font=("Arial", 12))
email_entry = tk.Entry(main_frame, width=30, bg="#7D8491", font=("Arial", 12))
password_entry = tk.Entry(main_frame, width=30, bg="#7D8491", show="*", font=("Arial", 12))

# Folder Entry
folder_label = tk.Label(main_frame, text="Folder Name:", bg="#C0C5C1", font=("Arial", 12))
folder_entry = tk.Entry(main_frame, width=30, bg="#7D8491", font=("Arial", 12))
folder_entry.config(state=tk.DISABLED)

# Buttons
login_button = tk.Button(main_frame, text="Login", command=login_and_upload, font=("Arial", 12, "bold"))
folder_upload_button = tk.Button(main_frame, text="Create Folder and Upload", command=create_folder_and_upload, font=("Arial", 12, "bold"))
file_upload_button = tk.Button(main_frame, text="Upload Email (TXT)", command=upload_email, font=("Arial", 12, "bold"))
file_upload_button.config(state=tk.DISABLED)

# Place widgets on grid
email_label.grid(row=0, column=0, pady=5, sticky="e")
email_entry.grid(row=0, column=1, pady=5, sticky="w")
password_label.grid(row=1, column=0, pady=5, sticky="e")
password_entry.grid(row=1, column=1, pady=5, sticky="w")
login_button.grid(row=2, column=0, columnspan=2, pady=10)
folder_label.grid(row=3, column=0, pady=5, sticky="e")
folder_entry.grid(row=3, column=1, pady=5, sticky="w")
folder_upload_button.grid(row=4, column=0, columnspan=2, pady=10)
file_upload_button.grid(row=5, column=0, columnspan=2, pady=10)

# Scrolled text widget to display data
data_text = scrolledtext.ScrolledText(main_frame, bg="#7D8491", width=50, height=10, state=tk.DISABLED, font=("Arial", 12))
data_text.grid(row=6, column=0, columnspan=2, pady=10)

# Button to show data tables
show_data_button = tk.Button(main_frame, text="Show Data Tables", command=show_data_tables, font=("Arial", 12, "bold"))
show_data_button.grid(row=7, column=0, columnspan=2, pady=10)

app.mainloop()
