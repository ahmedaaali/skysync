import customtkinter as ctk
from .. import utils

def show_team_page(app):
    """Displays the team information page."""
    utils.clear_frame(app, app.display_frame)  
    utils.create_title(app, "Meet the SkySync Team", font_size=30)  

    # Get the team information
    team_info = get_team_info()

    # Create dropdown for team member selection
    app.team_dropdown = ctk.CTkOptionMenu(
        app.display_frame,
        values=list(team_info.keys()),
        command=lambda member: display_team_member_info(app, member, team_info),
        fg_color=app.accent_color
    )
    app.team_dropdown.pack(pady=20)

    # Label to display selected team member's information
    app.team_info_label = ctk.CTkLabel(
        app.display_frame,
        text="",
        font=app.body_font,
        text_color=app.text_color,
        wraplength=800,
        justify="left"
    )
    app.team_info_label.pack(pady=20)

    # Automatically display the first team member's info
    first_member = list(team_info.keys())[0]
    display_team_member_info(app, first_member, team_info)

def display_team_member_info(app, member_name, team_info):
    """Displays information about the selected team member."""
    member_data = team_info.get(member_name, {})
    program = member_data.get("program", "N/A")
    info = member_data.get("info", "N/A")
    app.team_info_label.configure(text=f"Program: {program}\n\n\n{info}")

def get_team_info():
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

