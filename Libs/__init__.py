from pathlib import Path
import math

ROOT = Path(__file__).parent.parent

BIN_PATH = ROOT / "Bin"
TEMPLATE_PATH = ROOT / "Template" 
LOG_PATH = ROOT / "Logs"
HISTORY_PATH = ROOT / "Bin" / "projects.json"

POS_INF = math.inf
NEG_INF = math.inf*(-1)

project_structure_path = BIN_PATH / "project_structure.json"

ALLOWED_DECIMALS = 4
EPSILON = 1e-10 # CONSTANT TO AVOID DIVISION BY ZERO

ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']
CHARS = [chr(i) for i in range(65, 65+26)]

RAW_FORMAT_INDICATOR = "-position.csv"
RAW_FORMAT_SEPARATOR = "Well"
BATCH_FOLDER_FORMAT = "Batch {}"

DEFAULT_PARAMS = {
    "CONVERSION RATE": 82,
    "FRAME RATE": 30,
    "DURATION": 180
}
# [TODO] Add a Template generator so that the default params are consistent

WELL_CENTER_POINTS = {
    "1": {
        "X" :252, 
        "Y": 209
        },
    "2": {
        "X" :765, 
        "Y": 210
        },
    "3": {
        "X" :250, 
        "Y": 558
        },
    "4": {
        "X" :761, 
        "Y": 548
        }
    }

CENTER_RANGE = 1.5


SPEED_THRESHOLD = 6 * 100 / 3600 # cm/s
FAST_FORWARD_FACTOR = 10

FREEZING_THRESHOLD = 0.06
AV_SPEED_THRESHOLD = 90

DAY_FORMAT = "Day {}"
TREATMENT_REP_FORMAT = "Treatment {}"
