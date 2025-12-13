import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

payload = {
    "email": "admin@example.com",
    "password": "password123"
}

response = utils.send_and_print(
    url=f"{BASE_URL}/auth/login",
    method="POST",
    body=payload,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)

if response.status_code == 200:
    data = response.json()
    # Update secrets with new tokens
    utils.save_config("access_token", data["tokens"]["access"]["token"])
    utils.save_config("refresh_token", data["tokens"]["refresh"]["token"])
    utils.save_config("user_id", data["user"]["id"])
    print("\n[INFO] New Tokens saved to secrets.json")