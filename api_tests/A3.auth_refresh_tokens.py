import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

refresh_token = utils.load_config("refresh_token")

if not refresh_token:
    print("[ERROR] No refresh token found in secrets.json. Run A1 or A2 first.")
    sys.exit(1)

payload = {
    "refresh_token": refresh_token
}

response = utils.send_and_print(
    url=f"{BASE_URL}/auth/refresh-tokens",
    method="POST",
    body=payload,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)

if response.status_code == 200:
    data = response.json()
    # Update secrets
    utils.save_config("access_token", data["access"]["token"])
    utils.save_config("refresh_token", data["refresh"]["token"])
    print("\n[INFO] Refreshed Tokens saved to secrets.json")