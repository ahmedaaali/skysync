import os
import ssl
import socket
import time
import hashlib
import requests
from urllib.parse import urlparse

def create_ssl_context():
    """
    Create an SSLContext that does minimal checks. We'll do pinned fingerprint ourselves.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers("ECDHE+AESGCM:!aNULL:!eNULL")
    return context

def get_server_certificate_fingerprint(host, port, timeout=5):
    ssl_context = create_ssl_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ssl_context.wrap_socket(sock, server_hostname=host) as ssock:
            der_cert = ssock.getpeercert(True)
            return hashlib.sha256(der_cert).hexdigest()

def load_pinned_fingerprint(pin_file):
    if os.path.exists(pin_file):
        with open(pin_file, 'r') as f:
            return f.read().strip()
    return None

def save_pinned_fingerprint(pin_file, fingerprint):
    with open(pin_file, 'w') as f:
        f.write(fingerprint)

def verify_or_set_fingerprint(server_url, pinned_fpr_file, max_retries=10, delay=2):
    """
    Trust On First Use logic for the RPi:
      - If pinned fingerprint not found, trust the server's current cert & store it
      - If pinned fingerprint changes, warn user
    """
    parsed = urlparse(server_url)
    host = parsed.hostname
    port = parsed.port if parsed.port else 443

    pinned_fpr = load_pinned_fingerprint(pinned_fpr_file)

    for attempt in range(1, max_retries + 1):
        print(f"[Attempt {attempt}/{max_retries}] Checking server certificate fingerprint...")
        try:
            actual_fpr = get_server_certificate_fingerprint(host, port)
        except (socket.error, ssl.SSLError) as e:
            print(f"Connection error: {e}, retrying in {delay} sec...")
            time.sleep(delay)
            continue

        if pinned_fpr is None:
            print("No pinned fingerprint found. Trusting current server cert (TOFU).")
            save_pinned_fingerprint(pinned_fpr_file, actual_fpr)
            break
        else:
            if pinned_fpr != actual_fpr:
                print("WARNING: Server certificate fingerprint has CHANGED!")
                print(f"Old pinned: {pinned_fpr}")
                print(f"New actual: {actual_fpr}")
                print("Possible MITM attack. Proceed with caution.")
            else:
                print("Pinned fingerprint matches the server certificate.")
            break
        time.sleep(delay)

    # Optional: confirm server is up by checking /ping
    try:
        # Using verify=False because we skip normal CA validation
        resp = requests.get(f"{server_url}/ping", verify=False, timeout=5)
        if resp.status_code == 200:
            print("Server responded OK to /ping.")
        else:
            print(f"/ping returned status {resp.status_code}, ignoring.")
    except requests.RequestException as e:
        print(f"Failed /ping check: {e}")
