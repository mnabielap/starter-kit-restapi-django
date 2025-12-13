import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

refresh_token = utils.load_config("refresh_token")
if not refresh_token:
    print("[ERROR] No refresh token found.")
    sys.exit(1)

payload = {
    "refresh_token": refresh_token
}

utils.send_and_print(
    url=f"{BASE_URL}/auth/logout",
    method="POST",
    body=payload,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)