import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import requests
import os
import logging

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkySync - Admin Panel")
        self.root.geometry("1440x900")

        # Access environment variables
        self.SERVER_URL = os.environ.get('SERVER_URL')
        self.CERT_PATH = os.environ.get('CERT_PATH')
        self.LOG_PATH = os.environ.get('LOG_PATH', 'server_gui.log')

        # Set up logging
        logging.basicConfig(
            filename=self.LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

        self.token = None  # Admin authentication token

        self.setup_styles()
        self.main_frame = self.create_frame(self.root)
        self.show_login_screen()

    def setup_styles(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.bg_color = "#1c1c1c"
        self.text_color = "#f5f5f5"
        self.header_font = ("Helvetica Neue", 30, "bold")
        self.body_font = ("Helvetica Neue", 16)

    def create_frame(self, parent, **kwargs):
        frame = ctk.CTkFrame(parent, fg_color=self.bg_color)
        frame.pack(fill=kwargs.get('fill', ctk.BOTH), expand=kwargs.get('expand', True))
        return frame

    def show_login_screen(self):
        self.clear_frame()

        center_frame = self.create_frame(self.main_frame)

        self.create_label(center_frame, "Admin Login", font=self.header_font, pady=20).pack()

        input_frame = self.create_frame(center_frame)

        self.create_label(input_frame, "Username:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = self.create_entry(input_frame, placeholder="Enter admin username")
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.create_label(input_frame, "Password:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = self.create_entry(input_frame, placeholder="Enter admin password", show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.create_button(center_frame, "Login", self.verify_login, width=150)

    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        threading.Thread(target=self.process_login, args=(username, password), daemon=True).start()

    def process_login(self, username, password):
        try:
            response = requests.post(
                f'{self.SERVER_URL}/auth/admin/login',
                json={'username': username, 'password': password},
                verify=self.CERT_PATH,
                timeout=5
            )
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.root.after(0, self.show_admin_panel)
            else:
                logging.warning("Invalid credentials provided for admin login.")
                self.root.after(0, lambda: messagebox.showerror("Error", "Invalid credentials."))
        except requests.exceptions.RequestException as e:
            logging.error(f"Server connection issue: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", "Server connection issue."))

    def show_admin_panel(self):
        self.clear_frame()
        self.create_label(self.main_frame, "Admin Panel", font=self.header_font).pack(pady=10)

        self.create_button(self.main_frame, "View Users", self.view_users)
        self.create_button(self.main_frame, "Add User", self.add_user)
        self.create_button(self.main_frame, "Remove User", self.remove_user)

        # Display area for user info
        self.users_text = tk.Text(self.main_frame, height=20, width=100)
        self.users_text.pack(pady=20)

    def view_users(self):
        threading.Thread(target=self.process_view_users, daemon=True).start()

    def process_view_users(self):
        headers = {'x-access-token': self.token}
        try:
            response = requests.get(
                f'{self.SERVER_URL}/auth/admin/users',
                headers=headers,
                verify=self.CERT_PATH,
                timeout=5
            )
            if response.status_code == 200:
                users = response.json().get('users', [])
                self.root.after(0, self.display_users, users)
            else:
                logging.error("Failed to retrieve users.")
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to retrieve users."))
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching users: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", "Server connection issue."))

    def display_users(self, users):
        self.users_text.delete(1.0, tk.END)
        if users:
            for user in users:
                self.users_text.insert(tk.END, f"Username: {user['username']}, Profile: {user['profile']}\n")
        else:
            self.users_text.insert(tk.END, "No users found.")

    def add_user(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add User")

        tk.Label(add_window, text="Username:").grid(row=0, column=0)
        username_entry = tk.Entry(add_window)
        username_entry.grid(row=0, column=1)

        tk.Label(add_window, text="Password:").grid(row=1, column=0)
        password_entry = tk.Entry(add_window, show="*")
        password_entry.grid(row=1, column=1)

        tk.Label(add_window, text="Profile:").grid(row=2, column=0)
        profile_entry = tk.Entry(add_window)
        profile_entry.grid(row=2, column=1)

        def submit_user():
            username = username_entry.get()
            password = password_entry.get()
            profile = profile_entry.get() or "Client User"

            if not username or not password:
                messagebox.showerror("Error", "Username and password are required.")
                return

            threading.Thread(
                target=self.process_add_user,
                args=(username, password, profile, add_window),
                daemon=True
            ).start()

        tk.Button(add_window, text="Add User", command=submit_user).grid(row=3, columnspan=2)

    def process_add_user(self, username, password, profile, window):
        headers = {'x-access-token': self.token}
        data = {'username': username, 'password': password, 'profile': profile}
        try:
            response = requests.post(
                f'{self.SERVER_URL}/auth/admin/add_user',
                json=data,
                headers=headers,
                verify=self.CERT_PATH,
                timeout=5
            )
            if response.status_code == 201:
                self.root.after(0, lambda: messagebox.showinfo("Success", "User added successfully."))
                self.root.after(0, window.destroy)
            else:
                error_message = response.json().get('error', 'Failed to add user.')
                logging.error(f"Add user failed: {error_message}")
                self.root.after(0, lambda: messagebox.showerror("Error", error_message))
        except requests.exceptions.RequestException as e:
            logging.error(f"Error adding user: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", "Server connection issue."))

    def remove_user(self):
        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remove User")

        tk.Label(remove_window, text="Username:").grid(row=0, column=0)
        username_entry = tk.Entry(remove_window)
        username_entry.grid(row=0, column=1)

        def delete_user():
            username = username_entry.get()
            if not username:
                messagebox.showerror("Error", "Username is required.")
                return

            threading.Thread(
                target=self.process_remove_user,
                args=(username, remove_window),
                daemon=True
            ).start()

        tk.Button(remove_window, text="Remove User", command=delete_user).grid(row=1, columnspan=2)

    def process_remove_user(self, username, window):
        headers = {'x-access-token': self.token}
        data = {'username': username}
        try:
            response = requests.post(
                f'{self.SERVER_URL}/auth/admin/remove_user',
                json=data,
                headers=headers,
                verify=self.CERT_PATH,
                timeout=5
            )
            if response.status_code == 200:
                self.root.after(0, lambda: messagebox.showinfo("Success", "User removed successfully."))
                self.root.after(0, window.destroy)
            else:
                error_message = response.json().get('error', 'Failed to remove user.')
                logging.error(f"Remove user failed: {error_message}")
                self.root.after(0, lambda: messagebox.showerror("Error", error_message))
        except requests.exceptions.RequestException as e:
            logging.error(f"Error removing user: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", "Server connection issue."))

    def create_label(self, parent, text, font=None, text_color=None, pady=10, **kwargs):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=font or self.body_font,
            text_color=text_color or self.text_color,
            **kwargs
        )
        return label

    def create_entry(self, parent, placeholder="", show="", width=200, **kwargs):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, show=show, width=width, **kwargs)
        return entry

    def create_button(self, parent, text, command, **kwargs):
        button = ctk.CTkButton(parent, text=text, command=command, **kwargs)
        button.pack(pady=10)
        return button

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = AdminApp(root)
    root.mainloop()
