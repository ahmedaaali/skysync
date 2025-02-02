import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
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
        self.SERVER_URL = os.environ.get('SERVER_URL','http://localhost:5000')
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
        self.subheader_font = ("Helvetica Neue", 20, "bold")
        self.body_font = ("Helvetica Neue", 16)

    def create_frame(self, parent, **kwargs):
        frame = ctk.CTkFrame(parent, fg_color=self.bg_color)
        frame.pack(fill=kwargs.get('fill', ctk.BOTH), expand=kwargs.get('expand', True))
        return frame

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
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

        # Buttons: Login and Sign Up
        button_frame = self.create_frame(center_frame)
        self.create_button(
            button_frame, "Login", self.verify_login, width=150, fg_color="#34A853"
        ).pack(side=tk.LEFT, padx=10, pady=20)
        self.create_button(
            button_frame, "Sign Up", self.show_signup_screen, width=150, fg_color="#4285F4"
        ).pack(side=tk.LEFT, padx=10, pady=20)

        # Footer
        self.create_label(
            center_frame,
            "SkySync © 2025",
            font=("Helvetica Neue", 12, "italic"),
            pady=20
        ).pack()

    def create_label(self, parent, text, font=None, **kwargs):
        return ctk.CTkLabel(parent, text=text, text_color=self.text_color, font=font or self.body_font, **kwargs)

    def create_entry(self, parent, placeholder="", **kwargs):
        return ctk.CTkEntry(parent, placeholder_text=placeholder, **kwargs)

    def create_button(self, parent, text, command, **kwargs):
        return ctk.CTkButton(parent, text=text, command=command, **kwargs)
    
    def show_signup_screen(self):
        """Display the sign-up screen."""
        self.clear_frame()

        # Center frame to hold sign-up elements
        center_frame = self.create_frame(self.main_frame)

        # Title
        self.create_label(
            center_frame,
            "Admin Sign-Up",
            font=self.header_font,
            pady=20
        ).pack()

        # Input fields
        input_frame = self.create_frame(center_frame)

        self.create_label(input_frame, "Username:").grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.signup_username_entry = self.create_entry(input_frame, placeholder="Enter new username")
        self.signup_username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.create_label(input_frame, "Password:").grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.signup_password_entry = self.create_entry(
            input_frame, placeholder="Enter new password", show="*"
        )
        self.signup_password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.create_label(input_frame, "Confirm Password:").grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.confirm_password_entry = self.create_entry(
            input_frame, placeholder="Confirm password", show="*"
        )
        self.confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Buttons: Register and Back
        button_frame = self.create_frame(center_frame)
        self.create_button(
            button_frame, "Register", self.register_admin, width=150, fg_color="#34A853"
        ).pack(side=tk.LEFT, padx=10, pady=20)
        self.create_button(
            button_frame, "Back", self.show_login_screen, width=150, fg_color="#FF5252"
        ).pack(side=tk.LEFT, padx=10, pady=20)

    def show_dashboard(self):
        self.clear_frame()

        self.create_label(self.main_frame, "Admin Dashboard", font=self.header_font, pady=20).pack()

        button_frame = self.create_frame(self.main_frame, fill=tk.X, expand=False)
        self.create_button(button_frame, "View Users", self.show_users_screen, width=150).pack(side=tk.LEFT, padx=10, pady=10)
        self.create_button(button_frame, "Manage Missions", self.show_missions_screen, width=150).pack(side=tk.LEFT, padx=10, pady=10)
        self.create_button(button_frame, "Manage Images", self.show_images_screen, width=150).pack(side=tk.LEFT, padx=10, pady=10)
        self.create_button(button_frame, "Logout", self.logout, width=150).pack(side=tk.LEFT, padx=10, pady=10)

        self.show_users_screen()

    def show_users_screen(self):
        self.clear_frame()

        self.create_label(self.main_frame, "User Management", font=self.subheader_font, pady=10).pack()

        user_list_frame = self.create_frame(self.main_frame, fill=tk.BOTH, expand=True)
        self.users_listbox = tk.Listbox(user_list_frame, bg="#333333", fg=self.text_color, font=self.body_font)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.users_listbox.bind("<<ListboxSelect>>", self.on_user_select)

        action_frame = self.create_frame(self.main_frame, fill=tk.X, expand=False)
        self.create_button(action_frame, "Delete User", self.delete_user, width=150).pack(side=tk.LEFT, padx=10, pady=10)
        self.create_button(action_frame, "View User Missions", self.view_user_missions, width=150).pack(side=tk.LEFT, padx=10, pady=10)
        self.fetch_users()

    def show_missions_screen(self):
        self.clear_frame()

        self.create_label(self.main_frame, "Mission Management", font=self.subheader_font, pady=10).pack()

        mission_list_frame = self.create_frame(self.main_frame, fill=tk.BOTH, expand=True)
        self.missions_listbox = tk.Listbox(mission_list_frame, bg="#333333", fg=self.text_color, font=self.body_font)
        self.missions_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.missions_listbox.bind("<<ListboxSelect>>", self.on_mission_select)

        action_frame = self.create_frame(self.main_frame, fill=tk.X, expand=False)
        self.create_button(action_frame, "Delete Mission", self.delete_mission, width=150).pack(side=tk.LEFT, padx=10, pady=10)

        self.view_user_missions()

    def show_images_screen(self):
        self.clear_frame()

        self.create_label(self.main_frame, "Image Management", font=self.subheader_font, pady=10).pack()

        image_list_frame = self.create_frame(self.main_frame, fill=tk.BOTH, expand=True)
        self.images_listbox = tk.Listbox(image_list_frame, bg="#333333", fg=self.text_color, font=self.body_font)
        self.images_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.images_listbox.bind("<<ListboxSelect>>", self.on_image_select)

        action_frame = self.create_frame(self.main_frame, fill=tk.X, expand=False)
        self.create_button(action_frame, "Delete Image", self.delete_image, width=150).pack(side=tk.LEFT, padx=10, pady=10)

        self.fetch_images()

    def fetch_users(self):
        try:
            response = requests.get(
                f"{self.SERVER_URL}/users",
                headers={"Authorization": f"Bearer {self.token}"},
                verify=self.CERT_PATH  # Use the certificate for verification
            )
            logging.info(f"Fetch client users response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    self.users_listbox.insert(tk.END, user["username"])
            else:
                raise Exception(response.json().get("error", "Failed to fetch client users."))
        except Exception as e:
            logging.error(f"Error fetching client users: {e}")
            messagebox.showerror("Error", f"Failed to fetch client users: {e}")

    def fetch_missions(self):
        try:
            response = requests.get(f"{self.SERVER_URL}/missions", headers={"Authorization": f"Bearer {self.token}"}, verify=self.CERT_PATH)
            if response.status_code == 200:
                missions = response.json()
                for mission in missions:
                    self.missions_listbox.insert(tk.END, mission["mission_name"])
            else:
                raise Exception(response.json().get("error", "Failed to fetch missions."))
        except Exception as e:
            logging.error(f"Error fetching missions: {e}")
            messagebox.showerror("Error", f"Failed to fetch missions: {e}")

    def fetch_images(self):
        try:
            response = requests.get(f"{self.SERVER_URL}/images", headers={"Authorization": f"Bearer {self.token}"}, verify=self.CERT_PATH)
            if response.status_code == 200:
                images = response.json()
                for image in images:
                    self.images_listbox.insert(tk.END, image["filename"])
            else:
                raise Exception(response.json().get("error", "Failed to fetch images."))
        except Exception as e:
            logging.error(f"Error fetching images: {e}")
            messagebox.showerror("Error", f"Failed to fetch images: {e}")

    def on_user_select(self, event):
        selection = self.users_listbox.curselection()
        if selection:
            self.selected_user = self.users_listbox.get(selection[0])
            self.show_user_details(self.selected_user)

    def on_mission_select(self, event):
        selection = self.missions_listbox.curselection()
        if selection:
            self.selected_mission = self.missions_listbox.get(selection[0])
            self.show_mission_details(self.selected_mission)

    def on_image_select(self, event):
        selection = self.images_listbox.curselection()
        if selection:
            self.selected_image = self.images_listbox.get(selection[0])
            self.show_image_details(self.selected_image)

    def show_user_details(self, username):
        # Implement logic to fetch and display user details here
        pass

    def show_mission_details(self, mission_name):
        # Implement logic to fetch and display mission details here
        pass

    def show_image_details(self, image_name):
        # Implement logic to fetch and display image details here
        pass

    def view_user_missions(self):
        if not self.selected_user:
            messagebox.showerror("Error", "No user selected.")
            return
        
        # try:
        #     response = requests.get(f"{self.SERVER_URL}/missions?username={self.selected_user}", headers={"Authorization": f"Bearer {self.token}"}, verify=self.CERT_PATH)
        #     if response.status_code == 200:
        #         messagebox.showinfo("Success", response.json())
                
        #     else:
        #         raise Exception(response.json().get("error", "Failed to fetch user missions."))
        # except Exception as e:
        #     logging.error(f"Failed to fetch user missions: {e}")
        #     messagebox.showerror("Error", f"Failed to fetch user missions: {e}")
        # Implement logic to fetch and display user missions here

        try:
            headers = {'x-access-token': app.token}
            response = requests.get(f"{app.SERVER_URL}/missions/get_missions", headers=headers, verify=app.CERT_PATH)

            if response.status_code == 200:
                missions = response.json()
                if not missions:
                    messagebox.showinfo("No Missions", "No missions found for the selected user.")
                    return
            else:
                logging.error(f"Failed to fetch missions: {response.text}")
                messagebox.showerror("Error", f"Failed to fetch user missions: {response.text}")
                return
            
        except Exception as e:
            logging.error(f"Error fetching missions: {e}")
            messagebox.showerror("Error", f"Failed to fetch user missions: {e}")
            return
        
        # Create a new window to display the missions
        missions_window = tk.Toplevel(self.root)
        missions_window.title(f"Missions for {self.selected_user}")
        missions_window.geometry("400x300")

        # Add a label to the top of the window
        tk.Label(missions_window, text=f"Missions for {self.selected_user}", font=("Arial", 14, "bold")).pack(pady=10)

        # Create a Listbox to display the missions
        missions_listbox = tk.Listbox(missions_window, width=50, height=15)
        missions_listbox.pack(pady=10, padx=10)

        # Populate the Listbox with mission data
        for mission in missions:
            mission_name = mission.get("mission_name", "Unnamed Mission")
            missions_listbox.insert(tk.END, mission_name)

        # Add a close button
        tk.Button(missions_window, text="Close", command=missions_window.destroy).pack(pady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(title="Select Image")
        if not file_path:
            return
        try:
            with open(file_path, "rb") as file:
                response = requests.post(
                    f"{self.SERVER_URL}/images/upload",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files={"image": file},
                )
            if response.status_code == 200:
                messagebox.showinfo("Success", "Image uploaded successfully!")
            else:
                raise Exception(response.json().get("error", "Image upload failed."))
        except Exception as e:
            logging.error(f"Image upload failed: {e}")
            messagebox.showerror("Error", f"Image upload failed: {e}")

    def delete_user(self):
        selected_user = self.users_listbox.get(tk.ACTIVE)
        if not selected_user:
            messagebox.showerror("Error", "No user selected.")
            return
        try:
            response = requests.delete(f"{self.SERVER_URL}/client_users/{selected_user}", headers={"Authorization": f"Bearer {self.token}"}, verify=self.CERT_PATH)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Client user deleted successfully.")
                self.fetch_users()
            else:
                raise Exception(response.json().get("error", "Failed to delete client user."))
        except Exception as e:
            logging.error(f"Error deleting client user: {e}")
            messagebox.showerror("Error", f"Failed to delete client user: {e}")

    def delete_mission(self):
        selected_mission = self.missions_listbox.get(tk.ACTIVE)
        if not selected_mission:
            messagebox.showerror("Error", "No mission selected.")
            return
        try:
            response = requests.delete(f"{self.SERVER_URL}/missions/{selected_mission}", headers={"Authorization": f"Bearer {self.token}"}, verify=self.CERT_PATH)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Mission deleted successfully.")
                self.fetch_missions()
            else:
                raise Exception(response.json().get("error", "Failed to delete mission."))
        except Exception as e:
            logging.error(f"Error deleting mission: {e}")
            messagebox.showerror("Error", f"Failed to delete mission: {e}")

    def delete_image(self):
        selected_image = self.images_listbox.get(tk.ACTIVE)
        if not selected_image:
            messagebox.showerror("Error", "No image selected.")
            return
        try:
            response = requests.delete(f"{self.SERVER_URL}/images/{selected_image}", headers={"Authorization": f"Bearer {self.token}"}, verify=self.CERT_PATH)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Image deleted successfully.")
                self.fetch_images()
            else:
                raise Exception(response.json().get("error", "Failed to delete image."))
        except Exception as e:
            logging.error(f"Error deleting image: {e}")
            messagebox.showerror("Error", f"Failed to delete image: {e}")

    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        threading.Thread(target=self.authenticate_user, args=(username, password), daemon=True).start()

    def authenticate_user(self, username, password):
        try:
            response = requests.post(
                f"{self.SERVER_URL}/loginadmin",
                json={"username": username, "password": password},
                verify=self.CERT_PATH,
            )
            logging.info(f"Server response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                self.token = response.json().get("token")
                messagebox.showinfo("Success", "Login successful!")
                logging.info("Admin logged in successfully.")
                self.show_dashboard()
            else:
                error_message = response.json().get("error", "Login failed.")
                logging.warning(f"Login failed for user {username}: {error_message}")
                raise Exception(error_message)
        except Exception as e:
            logging.error(f"Login failed for user {username}: {e}")
            messagebox.showerror("Error", f"Login failed: {e}")

    def register_admin(self):
        """Handle admin registration."""
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required.")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        try:
            response = requests.post(
                f"{self.SERVER_URL}/registeradmin",
                json={"username": username, "password": password},
                verify=self.CERT_PATH
            )
            logging.info(f"Server response: {response.status_code} - {response.text}")
            if response.status_code == 201:
                messagebox.showinfo("Success", "Registration successful! Please log in.")
                self.show_login_screen()
            else:
                raise Exception(response.json().get("error", "Registration failed."))
        except Exception as e:
            logging.error(f"Registration failed: {e}")
            messagebox.showerror("Error", f"Registration failed: {e}")

    def logout(self):
        self.token = None
        self.selected_user = None
        self.show_login_screen()


if __name__ == "__main__":
    root = ctk.CTk()
    app = AdminApp(root)
    root.mainloop()

# TODO:
# Create admin gui for server side management and easy database access
