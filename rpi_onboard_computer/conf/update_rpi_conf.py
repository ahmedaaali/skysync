import os
import argparse
from dotenv import load_dotenv, set_key, dotenv_values

def update_rpi_configuration(verbose=False, server_ip=None):
    def log(msg):
        if verbose:
            print(msg)

    # Adjust path to your .env as needed:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')

    # Load existing .env
    load_dotenv(env_path)
    existing_vars = dotenv_values(env_path)

    # If user supplies --server-ip, override SERVER_URL
    if server_ip:
        old_url = existing_vars.get('SERVER_URL', 'https://127.0.0.1:5000')
        # Basic parse:
        # e.g. old_url="https://127.0.0.1:5000"
        scheme = "https"
        port = "5000"
        # naive approach: parse out :port
        parts = old_url.split(':')
        if len(parts) >= 3:
            port = parts[-1]  # e.g. 5000
        new_url = f"{scheme}://{server_ip}:{port}"
        set_key(env_path, 'SERVER_URL', new_url)
        log(f"Updated SERVER_URL to {new_url}")

    log("RPi configuration updated successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update RPi .env config.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output")
    parser.add_argument('-p', '--server-ip', type=str, help="Specify new server IP address")
    args = parser.parse_args()

    update_rpi_configuration(verbose=args.verbose, server_ip=args.server_ip)
