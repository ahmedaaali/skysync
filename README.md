# SkySync Project README

SkySync is an autonomous drone inspection system that automates the process of inspecting bridges and infrastructure. The system includes:

- A drone that captures images of structures.
- A backend server that processes and analyzes these images using machine learning.
- A client GUI application to interact with the system, view inspection results, and manage missions.

This README provides detailed instructions on how to set up and run the SkySync project on macOS, Linux, and Windows platforms.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone the Repository](#1-clone-the-repository)
  - [Set Up Python Virtual Environment](#2-set-up-python-virtual-environment)
  - [Install System Dependencies](#3-install-system-dependencies)
  - [Install Python Dependencies](#4-install-python-dependencies)
  - [Database Setup](#5-database-setup)
  - [SSL Certificate Setup](#6-ssl-certificate-setup)
- [Running the Server](#running-the-server)
- [Running the Client Application](#running-the-client-application)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Autonomous Drone Navigation**: Automate drone flight paths for bridge inspections.
- **Image Capture and Upload**: Capture images during flight and upload them to the backend server.
- **Machine Learning Analysis**: Analyze images using a YOLOv11-based model to detect defects.
- **Client GUI Application**: Interact with the system through a user-friendly GUI.
- **Mission Management**: Create and manage inspection missions.
- **User Authentication**: Secure login and user management.
- **Cross-Platform Compatibility**: Run on macOS, Linux, or Windows.

---

## Prerequisites

Ensure the following are installed on your system:

- Python 3.8 or higher
- Git
- OpenSSL
- PostgreSQL
- Redis
- pip (Python package installer)
- virtualenv (optional but recommended)

### Python 3.8 or Higher Installation

#### macOS
```bash
brew install python3
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

#### Windows
Download and install Python from the [official Python Downloads](https://www.python.org/).  
Ensure you check the box to "Add Python 3.x to PATH" during installation.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ahmedaaali/skysync.git
cd skysync
```

### 2. Set Up Python Virtual Environment
It is recommended to use a virtual environment for managing Python dependencies.

#### Create a Virtual Environment:
```bash
python3 -m venv venv
```

#### Activate the Virtual Environment:
- **macOS and Linux**:
  ```bash
  source venv/bin/activate
  ```
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

### 3. Install System Dependencies

#### OpenSSL
- **macOS**:
  ```bash
  brew install openssl
  ```
- **Linux**:
  ```bash
  sudo apt install openssl
  ```
- **Windows**:  
  Download and install OpenSSL from [slproweb.com](https://slproweb.com/).

#### PostgreSQL
- **macOS**:
  ```bash
  brew install postgresql
  brew services start postgresql
  ```
- **Linux**:
  ```bash
  sudo apt install postgresql postgresql-contrib
  sudo service postgresql start
  ```
- **Windows**:  
  Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/).

#### Redis
- **macOS**:
  ```bash
  brew install redis
  brew services start redis
  ```
- **Linux**:
  ```bash
  sudo apt install redis-server
  sudo service redis-server start
  ```
- **Windows**:  
  Download and install Redis from the [Microsoft archive](https://github.com/microsoftarchive/redis/releases).

### 4. Install Python Dependencies
With the virtual environment activated, install the required Python packages:
```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present, create it with the following content:
```
amqp==5.3.1
bcrypt==4.2.0
billiard==4.2.1
blinker==1.9.0
celery==5.4.0
certifi==2024.8.30
charset-normalizer==3.4.0
click==8.1.7
click-didyoumean==0.3.1
click-plugins==1.1.1
click-repl==0.3.0
customtkinter==5.2.2
darkdetect==0.8.0
Deprecated==1.2.15
Flask==2.3.3
Flask-Limiter==3.8.0
Flask-SQLAlchemy==3.1.1
gunicorn==23.0.0
idna==3.10
importlib_resources==6.4.5
itsdangerous==2.2.0
Jinja2==3.1.4
kombu==5.4.2
limits==3.13.0
markdown-it-py==3.0.0
MarkupSafe==3.0.2
mdurl==0.1.2
ordered-set==4.1.0
packaging==24.2
pillow==11.0.0
prompt_toolkit==3.0.48
psycopg2==2.9.10
Pygments==2.18.0
PyJWT==2.10.0
python-dateutil==2.9.0.post0
python-dotenv==1.0.1
redis==5.2.0
requests==2.32.3
rich==13.9.4
six==1.16.0
SQLAlchemy==2.0.36
tkinterdnd2==0.4.2
typing_extensions==4.12.2
tzdata==2024.2
urllib3==2.2.3
vine==5.1.0
wcwidth==0.2.13
Werkzeug==3.1.3
wrapt==1.17.0
```

### 5. Database Setup
#### Initialize the PostgreSQL Database:

./server/conf/setup_db.sh

or

1. Connect to the PostgreSQL shell:
   ```bash
   psql -U postgres
   ```
2. Run the following commands:
   ```sql
   CREATE DATABASE skysync_db;
   CREATE USER skysync_user WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE skysync_db TO skysync_user;
   ```
3. Exit the PostgreSQL shell:
   ```bash
   \q
   ```

#### Update Environment Variables:
Create a `.env` file in the `server/conf` directory with the following content:
```
DATABASE_URL=postgresql://skysync_user:yourpassword@localhost:5432/skysync_db
SECRET_KEY=your_secret_key
SERVER_URL=https://localhost:5000
SERVER_PATH=/path/to/skysync/server
CERT_PATH=/path/to/skysync/server/conf/cert/cert.pem
KEY_PATH=/path/to/skysync/server/conf/cert/key.pem
LOG_PATH=/path/to/skysync/server/skysync_app.log
```
Replace `/path/to/skysync` with the actual path to your `skysync` directory, and `your_secret_key` with a secure, random string.

### 6. SSL Certificate Setup
1. Navigate to the `conf` directory:
   ```bash
   cd server/conf
   ```
2. Run the certificate generation script:
   ```bash
   python update_server_conf.py -v -r
   ```

---

## Running the Server

```
usage: server.py [-h] [-v] [-r] [-g]

Run the SkySync server with various configuration and runtime options.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output for configuration updates.
  -r, --regenerate-cert Force regeneration of SSL certificates.
  -g, --run-gui         Start the Server GUI.
```

1. Navigate to the server directory:
   ```bash
   cd ../
   ```
2. Run the server using the provided script:
   ```bash
   python server.py -v -g
   ```

---

## Running the Client Application

```
usage: client.py [-h] [-v] [-r]

Run the SkySync client.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output for configuration updates.
  -r, --regenerate-cert Force regeneration of SSL certificates.
```

1. Open a new terminal window, activate the virtual environment, and navigate to the client directory:
   ```bash
   cd client
   source ../venv/bin/activate # For Windows: ..\venv\Scripts\activate
   ```
2. Run the client application:
   ```bash
   python client.py -v
   ```

---

## Usage

### Server Admin Functions:
- **Admin GUI**: Use the admin GUI to manage users and monitor the server. Access the admin interface when running the server with the `-g` flag.

### Client Application:
- **Login**: Use the client GUI to log in with your credentials.
- **Mission Management**: Create or select missions for inspections.
- **Upload Images**: Browse and upload images for analysis.
- **Analyze**: Trigger analysis of uploaded images using the machine learning model.
- **View Results**: View categorized defects in processed images within the GUI.

### Drone Integration:
Ensure the drone's onboard computer is configured to capture images and upload them to the server as per the project's specifications.

---

## Troubleshooting

| Issue                        | Solution                                                                                 |
|------------------------------|-----------------------------------------------------------------------------------------|
| Cannot Connect to Server     | Ensure the server is running and accessible at the specified `SERVER_URL`.              |
| Database Connection Errors   | Verify PostgreSQL is running and the credentials are correct in the `.env` file.        |
| SSL Certificate Issues       | Check the generated certificates and their paths in the `.env` file.                    |
| Redis Not Running            | Start Redis: `brew services start redis` (macOS) or `sudo service redis-server start`.  |
| Module Not Found Errors      | Ensure the virtual environment is activated and all dependencies are installed.         |
| Permission Denied Errors     | Check file permissions and run commands with appropriate privileges (e.g., `sudo`).     |

---

## Directory Structure
```
.
├── client/                 # Client GUI application
│   ├── conf/               # Client configuration files
│   ├── processed_images/   # Storage for processed images
│   ├── uploaded_images/    # Storage for uploaded images
│   └── ...                 # Client source code
├── server/                 # Backend server application
│   ├── conf/               # Server configuration files and scripts
│   ├── cached_images/      # Storage for cached images
│   └── ...                 # Server source code
├── skysync_env/            # Python virtual environment
├── requirements.txt        # List of Python dependencies
├── nav_mission_planner/    # Navigation MP application
├── rpi_onboard_computer/   # On-board computer application
└── ...                     # Other project files
```

---

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

---

## License

This project is licensed under the MIT License.
