import os
import socket
import subprocess
import shutil
from dotenv import load_dotenv, set_key, dotenv_values
from urllib.parse import urlparse, urlunparse

def update_configuration(verbose=False, regenerate_cert=False, server_ip=None):
    """Update the client configuration by modifying the .env file and managing certificates."""
    # Helper function for verbose output
    def log(message):
        if verbose:
            print(message)

    # Get the base directory of the current script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct paths relative to the base directory
    cert_dir = os.path.join(base_dir, 'conf', 'cert')
    env_path = os.path.join(base_dir, 'conf', '.env')
    log_path = os.path.join(base_dir, 'skysync_app.log')
    bg_img_path = os.path.join(base_dir, 'icons', 'bg_img.jpg')
    # server_cert_dir = os.path.abspath(os.path.join(base_dir, '../server/conf/cert'))

    # Ensure necessary directories exist
    os.makedirs(cert_dir, exist_ok=True)

    # Load existing environment variables from .env
    load_dotenv(env_path)
    existing_env_vars = dotenv_values(env_path)

    # Get the local IP address
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"  
        finally:
            s.close()
        return ip

    if server_ip:
        current_ip = server_ip
    else:
        current_ip = get_local_ip()

    # Parse existing SERVER_URL or create a new one
    existing_server_url = existing_env_vars.get('SERVER_URL', '')
    if existing_server_url:
        parsed_url = urlparse(existing_server_url)
        scheme = parsed_url.scheme or "https"
        hostname = current_ip
        port = parsed_url.port or 5000
    else:
        scheme = "https"
        hostname = current_ip
        port = 5000

    # Construct the updated SERVER_URL
    updated_server_url = urlunparse((scheme, f"{hostname}:{port}", '', '', '', ''))
    ip_changed = existing_server_url != updated_server_url

    # Update or set essential .env variables
    paths_to_update = {
        'SERVER_URL': updated_server_url,
        'CERT_PATH': os.path.join(cert_dir, 'cert.pem'),
        'LOG_PATH': log_path,
        'CLIENT_PATH': base_dir,
        'BG_IMG': bg_img_path,
    }

    for key, value in paths_to_update.items():
        existing_value = existing_env_vars.get(key, '')
        if existing_value != value:
            set_key(env_path, key, value)
            log(f"Updated {key} to {value} in .env")
        else:
            log(f"{key} is already set to {value} in .env")

    # # Check if cert and key already exist
    # cert_path = paths_to_update['CERT_PATH']
    # cert_exists = os.path.exists(cert_path)

    # # Re-copy cert if certs are missing or regenerate_cert is True
    # if ip_changed or not cert_exists or regenerate_cert:
    #     sync_cert_from_server(cert_path, server_cert_dir, verbose)
    # else:
    #     log("Certificate already exist; skipping cert copying.")
    log("Client configuration updated. No certificate sync needed (TOFU in use).")

# def sync_cert_from_server(cert_path, server_cert_dir, verbose=False):
#     """Sync cert to Client."""
#     def log(message):
#         if verbose:
#             print(message)
#     src_path = os.path.join(server_cert_dir, 'cert.pem')
#     shutil.copy2(src_path, cert_path)
#     log(f"Synced cert from server: {server_cert_dir}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update client configuration.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("-r", "--regenerate-cert", action="store_true", help="Force regeneration of certificates.")
    args = parser.parse_args()

    update_configuration(verbose=args.verbose, regenerate_cert=args.regenerate_cert)
