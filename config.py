from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


PROJ_ROOT = Path(__file__).parent
DATA_DIR = PROJ_ROOT / "data"

LEVELS = ["AD", "DM", "JE", "OP", "ND"]
