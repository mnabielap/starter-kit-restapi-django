import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

access_token = utils.load_config("access_token")
user_id = utils.load_config("user_id")

if not user_id:
    print("[ERROR] No user_id found.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

utils.send_and_print(
    url=f"{BASE_URL}/users/{user_id}",
    method="DELETE",
    headers=headers,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)