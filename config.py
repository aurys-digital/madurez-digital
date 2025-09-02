from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from msal.telemetry import CLIENT_REQUEST_ID

load_dotenv(find_dotenv())
import os


PROJ_ROOT = Path(__file__).parent
DATA_DIR = PROJ_ROOT / "data"

LEVELS = ["AD", "DM", "JE", "OP", "ND"]

CLIENT_ID = os.environ.get("CLIENT_ID")
TENANT_ID = os.environ.get("TENANT_ID")
