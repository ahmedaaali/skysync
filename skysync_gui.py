import customtkinter as ctk
import requests

# Set the theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SkySyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkySync - Autonomous Drone System")
        self.root.geometry("1200x700")

        # Defining different colors and fonts
        self.bg_color = "#1c1c1c"
        self.accent_color = "#007b83"
        self.light_accent = "#4ecdc4"
        self.text_color = "#f5f5f5"
        self.header_font = ("Helvetica Neue", 40, "bold")
        self.subheader_font = ("Helvetica Neue", 20, "italic")
        self.body_font = ("Helvetica Neue", 16)

        # User login flag
        self.is_logged_in = False

        # Setup layout
        self.create_layout()

    def create_layout(self):
        # Main Frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)

        # Show login screen initially
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_frame()

        # Application title above login
        app_title = ctk.CTkLabel(
            self.main_frame, text="SkySync - Autonomous Drone System", font=self.header_font, text_color=self.light_accent
        )
        app_title.pack(pady=(30, 10))

        # Add a decorative separator line to enhance layout
        separator = ctk.CTkLabel(self.main_frame, text="—" * 50, font=self.body_font, text_color=self.accent_color)
        separator.pack(pady=10)

        # Login Header
        login_header = ctk.CTkLabel(
            self.main_frame, text="Sign in", font=("Helvetica Neue", 30, "bold"), text_color=self.light_accent
        )
        login_header.pack(pady=(60, 5))  # Adjust padding before and after "Sign in"

        # Username and Password Frame
        input_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color)
        input_frame.pack(pady=20)

        # Username Label and Entry
        username_label = ctk.CTkLabel(input_frame, text="Username:", font=self.body_font, text_color=self.light_accent)
        username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter your username", width=200)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        # Password Label and Entry
        password_label = ctk.CTkLabel(input_frame, text="Password:", font=self.body_font, text_color=self.light_accent)
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter your password", show="*", width=200)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Login Button with updated color scheme
        login_button = ctk.CTkButton(
            self.main_frame, 
            text="Login", 
            command=self.verify_login, 
            fg_color="#3498db",
            hover_color="#2980b9",
            font=("Helvetica Neue", 22, "bold"),
            width=250,
            height=50,
            border_width=2,
            border_color="#2980b9",
            corner_radius=12,
        )
        login_button.pack(pady=30)


        # Error message placeholder (hidden by default)
        self.error_message = ctk.CTkLabel(self.main_frame, text="", text_color="red", font=("Helvetica Neue", 12, "italic"))
        self.error_message.pack(pady=(0, 10))

        # Bind Enter key to login
        self.root.bind("<Return>", self.verify_login_with_enter)

    def verify_login(self, event=None):
        # Replace later with backend server authentication
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "user" and password == "password":  # Sample credentials
            self.is_logged_in = True
            self.show_main_interface()
        else:
            self.show_error_message("Invalid username or password. Please try again!")

    def verify_login_with_enter(self, event=None):
        self.verify_login()

    # def verify_login(self):
    #     username = self.username_entry.get()
    #     password = self.password_entry.get()
    #
    #     try:
    #         response = requests.post('http://backend-server-url/login', json={'username': username, 'password': password})
    #         if response.status_code == 200:
    #             self.is_logged_in = True
    #             self.show_main_interface()
    #         else:
    #             self.show_error_message("Login failed. Please try again.")
    #     except requests.exceptions.RequestException:
    #         self.show_error_message("Server connection error. Check your connection.")
    #
    # def request_analysis(self):
    #     try:
    #         response = requests.post('http://backend-server-url/analyze')
    #         if response.status_code == 200:
    #             self.show_message("Analysis started successfully.")
    #         else:
    #             self.show_message("Error starting analysis.")
    #     except requests.exceptions.RequestException:
    #         self.show_message("Server connection error during analysis request.")

    def show_error_message(self, message):
        self.error_message.configure(text=message)
        self.error_message.after(5000, self.clear_error_message)

    def clear_error_message(self):
        self.error_message.configure(text="")

    def show_main_interface(self):
        self.clear_frame()

        # Header Frame with Title and Dropdown Menu for Profile, Settings, and Logout
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color=self.accent_color)
        self.header_frame.pack(fill=ctk.X)

        # Title
        title_label = ctk.CTkLabel(self.header_frame, text="SkySync", font=self.header_font, text_color=self.text_color)
        title_label.pack(pady=5)

        # Dropdown Menu for Profile, Settings, and Logout
        self.options_menu = ctk.CTkOptionMenu(
            self.header_frame, 
            values=["Profile", "Settings", "Logout"], 
            command=self.handle_menu_option,
            fg_color="#3498db" 
        )
        self.options_menu.pack(pady=5, anchor="e")

        # Navigation Sidebar
        self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=200, fg_color=self.light_accent)
        self.sidebar_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10)
        # Prevent sidebar from shrinking to fit its content
        self.sidebar_frame.pack_propagate(False)

        # Sidebar Buttons
        self.create_sidebar_buttons()

        # Main Display Frame
        self.display_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color)
        self.display_frame.pack(side=ctk.RIGHT, expand=True, fill=ctk.BOTH, padx=10, pady=10)

        # Load Home Page by default
        self.show_home_page()

    def handle_menu_option(self, selected_option):
        if selected_option == "Logout":
            self.is_logged_in = False
            self.show_login_screen()
        elif selected_option == "Profile":
            self.show_profile_page()
        elif selected_option == "Settings":
            self.show_settings_page()

    def show_profile_page(self):
        self.clear_display_frame()
        self.create_title("User Profile", font_size=30)

        profile_info = (
            "Username: user\n"
            "Role: Drone Operator\n"
            "Project: SkySync - Autonomous Drone System"
        )
        profile_label = ctk.CTkLabel(
            self.display_frame, text=profile_info, font=self.body_font, text_color=self.text_color, wraplength=600
        )
        profile_label.pack(pady=20)

    def show_settings_page(self):
        self.clear_display_frame()
        self.create_title("Settings", font_size=30)

        settings_label = ctk.CTkLabel(
            self.display_frame, text="Settings options placeholder...", font=self.body_font, text_color=self.text_color
        )
        settings_label.pack(pady=20)

    def create_sidebar_buttons(self):
        button_config = {"width": 180, "font": self.subheader_font, "fg_color": self.bg_color, "hover_color": self.accent_color}

        # Home Button
        home_button = ctk.CTkButton(self.sidebar_frame, text="Home", command=self.show_home_page, **button_config)
        home_button.pack(pady=(20, 10))

        # Drone Specs Button
        specs_button = ctk.CTkButton(self.sidebar_frame, text="Drone Specs", command=self.show_drone_specs, **button_config)
        specs_button.pack(pady=10)

        # Drone Inspection Button
        inspection_button = ctk.CTkButton(self.sidebar_frame, text="Drone Inspection", command=self.show_inspection_page, **button_config)
        inspection_button.pack(pady=10)

        # Meet the Team
        team_button = ctk.CTkButton(self.sidebar_frame, text="Meet the Team", command=self.show_team_page, **button_config)
        team_button.pack(pady=10)

    def show_home_page(self):
        self.clear_display_frame()
        self.create_title("Welcome to SkySync", font_size=30)

        # Description
        desc_text = (
            "SkySync project aims to enhance safety, accuracy and efficiency of bridge inspections. It will do this by integrating sensors, cameras and machine learning to find structural defects. The key objective of this project includes developing a drone, capable of autonomously navigating complex structures and using machine learning to detect cracks, corrosion and other defects. "
        )
        desc_label = ctk.CTkLabel(
            self.display_frame, text=desc_text, font=self.body_font, text_color=self.text_color, wraplength=800, justify="left"
        )
        desc_label.pack(pady=20)

    def show_drone_specs(self):
        self.clear_display_frame()
        self.create_title("Drone Specifications", font_size=30)

        specs_list = [
            "• Pixhawk 2.4 - Flight Controller",
            "• Raspberry Pi 5 - On-board Computer",
            "• RPI HQ Camera - Capture Camera",
            "• 5.1Ah 3S Battery - Power Source",
            "• SiK Telemetry Radio V3 - Data Communication",
            "• CubePilot Here4 RTK GNSS - High Accuracy Positioning",
        ]
        specs_text = "\n\n".join(specs_list)
        specs_label = ctk.CTkLabel(
            self.display_frame, text=specs_text, font=self.body_font, text_color=self.text_color, wraplength=600, justify="left"
        )
        specs_label.pack(pady=20)

    def show_inspection_page(self):
        self.clear_display_frame()
        self.create_title("Drone Inspection Overview", font_size=30)

        # Placeholder Gallery Area
        gallery_placeholder = ctk.CTkLabel(
            self.display_frame, text="Image Gallery Loading...", font=self.subheader_font, text_color=self.light_accent
        )
        gallery_placeholder.pack(pady=10)

        analyze_button = ctk.CTkButton(
            self.display_frame, text="Analyze Inspection Data", fg_color=self.accent_color,
            font=self.subheader_font, command=self.analyze_inspection
        )
        analyze_button.pack(pady=20)

    def analyze_inspection(self):
        print("Analyzing inspection data...")

    def show_team_page(self):
        self.clear_display_frame()
        self.create_title("Meet the SkySync Team", font_size=30)

        # Create dropdown for team member selection
        self.team_dropdown = ctk.CTkOptionMenu(
            self.display_frame, 
            values=list(self.get_team_info().keys()), 
            command=self.display_team_member_info,
            fg_color=self.accent_color
        )
        self.team_dropdown.pack(pady=20)

        self.team_info_label = ctk.CTkLabel(
            self.display_frame, text="", font=self.body_font, text_color=self.text_color, wraplength=800, justify="left"
        )
        self.team_info_label.pack(pady=20)

        # Automatically display the first team member's info
        first_member = list(self.get_team_info().keys())[0]  # Get the first member from the team list
        self.display_team_member_info(first_member)  # Display info for the first member

    def display_team_member_info(self, member_name):
        team_info = self.get_team_info().get(member_name, {})
        
        # Properly format the member's information
        program = team_info.get("program", "")
        info = team_info.get("info", "")
        
        self.team_info_label.configure(text=f"Program: {program}\n\n\n{info}")

    def get_team_info(self):
        return {
            "Ahmed": {
                "program": "Computer Systems Engineering",
                "info": (
                    "Ahmed brings hands-on experience in embedded systems, cloud automation, and application development from his previous co-ops and coursework. In this project, he is responsible for managing the communication interfaces. To achieve our goal of autonomous flight control, we need to integrate seamless data flow between the drone’s flight controller and on-board computer as a Raspberry Pi, as well as between the on-board computer and the base station.\n\nAhmed’s embedded systems experience includes a previous co-op at Ford, where he worked as a BSP Embedded Software Developer. His work involved configuring registers on M7 and A53 processors to control hardware interactions within the Linux Bootloader. This hands-on experience is essential for low-level embedded software development needed to configure the Raspberry Pi as an on-board computer. The Raspberry Pi will gather data from the camera and flight controller and send it to the base station through a second communication interface. Relevant course work includes SYSC3310 and SYSC4805.\n\nAhmed has cloud automation experience from his co-op at Nokia, where he used Python and Terraform to develop scripts that automate the deployment process for cloud resources. This experience, along with his CCNA certification, are key for integrating our drone’s remote communication system. In this project, the Raspberry Pi will communicate with a remote server, which will send data to a client on a GUI application. Relevant course work includes SYSC2004, ECOR1041 and ECOR1042."
                ),
            },
            "Alizée": {
                "program": "Computer Systems Engineering",
                "info": (
                    "Alizée brings prior experience in machine learning from her SYSC 3010 project, where she implemented a person detection algorithm using TensorFlow Lite for a home security system. She is now building on these foundational skills to tackle the unique challenges of structural defect detection for bridge inspection. Her project utilizes YOLO V11, a machine learning model capable of detecting issues like cracks, spalling, and corrosion in concrete structures. Alizée’s foundation in applying and optimizing machine learning models for embedded systems, as demonstrated in her work on the home security system, has equipped her with the technical skills needed to adapt these models for defect detection. Given that both person detection and defect detection fall under object detection, she brings cross-compatible skills in model configuration, allowing her to adapt her expertise to support reliable detection for this project.\n\nAdditionally, Alizée brings valuable hands-on experience in robotics and embedded systems from her previous projects, making her well-suited to tackle the challenge of implementing autonomous navigation for the drone. Her background includes work on an autonomous snowplow project in SYSC 4805, where she successfully configured the robot for autonomous operation using Inertial Measurement Unit (IMU) sensors for accurate orientation. This skill is directly applicable to her current project, as she will utilize Visual Inertial Odometry (VIO) for drone navigation. Since VIO also depends on IMU data for precise positioning, her expertise in sensor integration and real-time orientation will enhance her ability to configure the drone for reliable, GPS-free navigation in complex environments."
                ),
            },
            "Bisher": {
                "program": "Computer Systems Engineering",
                "info": (
                    "Bisher has software, wireless communication, and hardware design experience which will allow him to take responsibility for designing the architecture of the drone system along with ensuring the software and hardware integration of all components. Bisher also has experience in project management through previous coursework and internships, which allows him to manage the project’s timeline along with distributing tasks amongst team members. Moreover, he has knowledge and experience in machine learning due to courses such as SYSC3010, where he designed a facial recognition system from the ground up on a Raspberry Pi 4. He also has cloud experience, specifically in the integration of multiple features and components, allowing him to bring his expertise to the integration development of this drone. In addition, Bisher brings his extensive expertise in embedded and real-time systems learned through previous coursework such as SYSC3310 and SYSC3303, which enables him to provide crucial development to the embedded side of the drone."
                ),
            },
            "Hamdiata": {
                "program": "Computer Systems Engineering",
                "info": (
                    "With a strong foundation in computer systems from previous courses and co-op experience in telecommunications and cloud communication, Hamdiata is responsible for designing, implementing, and testing the drone’s backend and GPS coordination system. He is primarily responsible for configuring the cloud infrastructure to support the uploading of images to the cloud server. Having previous experience in configuring and communicating with Google’s Firebase using a custom-made API, he is well-suited to take on this challenge.\n\nMoreover, his co-op experience in testing and integrating an end-to-end product makes him well-suited for this project. This includes developing comprehensive test plans, setting up the lab environment, and executing test cases."
                ),
            },
            "Varun": {
                "program": "Electrical Engineering",
                "info": (
                    "Varun has completed two co-op terms as an ASIC hardware design engineer and a silicon and hardware validation engineer, bringing valuable experience to both hardware and software aspects of projects. As the only electrical engineer on his team, he is responsible for assembling and integrating the drone’s electrical components and testing their functionality.\n\nHis extensive experience in debugging hardware issues was gained during his hardware validation co-op, where he tested the performance of ASIC chips on various PCB boards under different conditions, configurations, and data rates. Varun is proficient with several instruments, including source measuring units (SMUs), multimeters, and power supplies, which will be essential for testing. Additionally, he has soldering experience from his work terms and a third-year project involving connections between Arduino and Raspberry Pi, which he will apply to solder battery connections, motor leads, ESCs, and any custom wiring as needed.\n\nFurthermore, he has experience in Python and C++ from his co-op positions, where he automated instrument control, generated plots, and programmed the GUI for PCB board operations. This experience will help him in integrating the components and during the testing process."
                ),
            },
        }

    def clear_display_frame(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_title(self, text, font_size=20):
        title_label = ctk.CTkLabel(self.display_frame, text=text, font=("Helvetica Neue", font_size, "bold"), text_color=self.text_color)
        title_label.pack(pady=10)

if __name__ == "__main__":
    root = ctk.CTk()
    app = SkySyncApp(root)
    root.mainloop()
