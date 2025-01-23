import os
import socket
import subprocess
import secrets
import shutil
from dotenv import load_dotenv, set_key, dotenv_values
from urllib.parse import urlparse, urlunparse

def update_configuration(verbose=False, regenerate_cert=False):
    # Helper function for printing messages if verbose is True
    def log(message):
        if verbose:
            print(message)

    # Get the base directory of the current script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct paths relative to the base directory
    cert_dir = os.path.join(base_dir, 'conf', 'cert')
    env_path = os.path.join(base_dir, 'conf', '.env')
    openssl_cnf_path = os.path.join(base_dir, 'conf', 'openssl.cnf')
    log_path = os.path.join(base_dir, 'skysync_app.log')
    client_cert_dir = os.path.join(base_dir, '../client/conf/cert')
    ml_model_dir = os.path.join(base_dir, '../machine_learning/best.pt')

    # Ensure necessary directories exist
    os.makedirs(cert_dir, exist_ok=True)

    # Ensure openssl.cnf exists with correct format
    if not os.path.exists(openssl_cnf_path):
        log("openssl.cnf not found. Creating a new one.")
        openssl_cnf_content = """[ req ]
                                default_bits        = 2048
                                default_md          = sha256
                                default_keyfile     = key.pem
                                prompt              = no
                                encrypt_key         = yes
                                distinguished_name  = req_distinguished_name
                                x509_extensions     = v3_req

                                [ req_distinguished_name ]
                                C                   = CA
                                ST                  = Ontario
                                L                   = Ottawa
                                O                   = SkySync
                                OU                  = Admin
                                CN                  = Ahmed

                                [ v3_req ]
                                subjectAltName      = @alt_names

                                [ alt_names ]
                                """

        with open(openssl_cnf_path, 'w') as file:
            file.write(openssl_cnf_content)
        log(f"Created openssl.cnf at {openssl_cnf_path}")

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

    # Update or set essential .env variables
    paths_to_update = {
        'SERVER_URL': updated_server_url,
        'CERT_PATH': os.path.join(cert_dir, 'cert.pem'),
        'KEY_PATH': os.path.join(cert_dir, 'key.pem'),
        'LOG_PATH': log_path,
        'SERVER_PATH': base_dir,
        'DATABASE_URL': existing_env_vars.get('DATABASE_URL', 'postgresql://skysync_user:password@localhost:5432/skysync_db'),
        'model_path' : ml_model_dir
    }

    # Handle SECRET_KEY separately
    if 'SECRET_KEY' not in existing_env_vars or not existing_env_vars['SECRET_KEY']:
        new_secret_key = secrets.token_urlsafe(32)
        set_key(env_path, 'SECRET_KEY', new_secret_key)
        log("Generated new SECRET_KEY because no key existed.")
    else:
        log("SECRET_KEY already exists in .env")

    # Update or set the other variables
    for key, value in paths_to_update.items():
        existing_value = existing_env_vars.get(key, '')
        if existing_value != value:
            set_key(env_path, key, value)
            log(f"Updated {key} to {value} in .env")
        else:
            log(f"{key} is already set to {value} in .env")

    # Update openssl.cnf to add the new IP address if not present
    with open(openssl_cnf_path, 'r') as file:
        lines = file.readlines()

    existing_ips = {line.split('=')[1].strip() for line in lines if line.strip().startswith('IP.')}
    if current_ip not in existing_ips:
        ip_changed = True
        last_ip_index = max(
            [int(line.split('=')[0].strip().split('.')[1]) for line in lines if line.strip().startswith('IP.')],
            default=0
        )
        new_ip_entry = f'IP.{last_ip_index + 1:<17}= {current_ip}\n'
        with open(openssl_cnf_path, 'a') as file:
            file.write(new_ip_entry)
        log(f"Added {current_ip} as IP.{last_ip_index + 1} in openssl.cnf")
    else:
        ip_changed = False
        log(f"{current_ip} already exists in openssl.cnf")

    # Check if cert and key already exist
    cert_path = paths_to_update['CERT_PATH']
    key_path = paths_to_update['KEY_PATH']
    cert_exists = os.path.exists(cert_path)
    key_exists = os.path.exists(key_path)
    client_cert_exists = os.path.exists(os.path.join(client_cert_dir, 'cert.pem'))

    # Check if certificates need to be regenerated or synced
    if not cert_exists or not key_exists or ip_changed or regenerate_cert:
        generate_certificate_and_key(openssl_cnf_path, cert_path, key_path, verbose)
        # Always sync the regenerated certificate to the client
        sync_cert_to_client(cert_path, client_cert_dir, verbose)
    elif not client_cert_exists:
        sync_cert_to_client(cert_path, client_cert_dir, verbose)
    else:
        log("Certificate, key, and client certificate are up-to-date; no action required.")

def generate_certificate_and_key(openssl_cnf_path, cert_path, key_path, verbose=False):
    """Generate a new self-signed certificate and key using OpenSSL."""
    def log(message):
        if verbose:
            print(message)

    openssl_cmd = [
        'openssl', 'req', '-x509', '-nodes', '-days', '365',
        '-newkey', 'rsa:2048',
        '-keyout', key_path,
        '-out', cert_path,
        '-config', openssl_cnf_path
    ]
    try:
        result = subprocess.run(openssl_cmd, check=True, capture_output=True, text=True)
        log("OpenSSL command executed to generate certificate and key.")
    except subprocess.CalledProcessError as e:
        log(f"Error generating certificates: {e.stderr}")

def sync_cert_to_client(cert_path, client_cert_dir, verbose=False):
    """Sync cert to Client."""
    def log(message):
        if verbose:
            print(message)
    dest_path = os.path.join(client_cert_dir, 'cert.pem')
    shutil.copy2(cert_path, dest_path)
    log(f"Synced cert to client: {dest_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update server configuration.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("-r", "--regenerate-cert", action="store_true", help="Force regeneration of certificates.")
    args = parser.parse_args()

    update_configuration(verbose=args.verbose, regenerate_cert=args.regenerate_cert)

# TODO:
# Use diffie-hellman for key-exchange to generate symmetric keys
# Use TLS 1.3 for secure communication; use nonce and other security concepts
# Communicate the cert from server to client securely
