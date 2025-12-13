import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

access_token = utils.load_config("access_token")
if not access_token:
    print("[ERROR] No access token found. Run A2 first.")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {access_token}"
}

utils.send_and_print(
    url=f"{BASE_URL}/auth/send-verification-email",
    method="POST",
    headers=headers,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)