import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

# Data to register
payload = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "password123" # Must be at least 8 chars + 1 number
}

response = utils.send_and_print(
    url=f"{BASE_URL}/auth/register",
    method="POST",
    body=payload,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)

if response.status_code == 201:
    data = response.json()
    # Save tokens and user info for other scripts
    utils.save_config("access_token", data["tokens"]["access"]["token"])
    utils.save_config("refresh_token", data["tokens"]["refresh"]["token"])
    utils.save_config("user_id", data["user"]["id"])
    print("\n[INFO] Tokens and User ID saved to secrets.json")