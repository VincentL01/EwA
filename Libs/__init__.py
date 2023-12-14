from pathlib import Path
import math

ROOT = Path(__file__).parent.parent

BIN_PATH = ROOT / "Bin"
# TEMPLATE_PATH = ROOT / "Template" 
LOG_PATH = ROOT / "Logs"
HISTORY_PATH = ROOT / "Bin" / "projects.json"

POS_INF = math.inf
NEG_INF = math.inf*(-1)

project_structure_path = BIN_PATH / "project_structure.json"

ALLOWED_DECIMALS = 4
EPSILON = 1e-10 # CONSTANT TO AVOID DIVISION BY ZERO
ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']
CHARS = [chr(i) for i in range(65, 65+26)]

# STRUCTURAL CONSTANTS
PARAMS_FILE_NAME = "parameters.json"

RAW_FORMAT_INDICATOR = "-position*.csv"
RAW_FORMAT_SEPARATOR = "Well"
BATCH_FOLDER_FORMAT = "Batch {}"

OLD_DEFAULT_PARAMS = {
    "CONVERSION RATE": 82,
    "FRAME RATE": 30,
    "DURATION": 180
}

DEFAULT_PARAMS = {
    "CONVERSION RATE": 82,
    "FRAME RATE": 30,
    "DURATION": 180,
    "AV SPEED THREDHOLD": 90,
    "FREEZING THRESHOLD": 0.06,
    "SPEED THRESHOLD": 6 * 100 / 3600,
    "FAST FORWARD FACTOR": 10,
    "THIGMOTAXIS RANGE": 1.5,
    "CENTER" : {
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
}

PARAMS_UNITS = {
        "CONVERSION RATE": "pixel/cm",
        "FRAME RATE": "frames/s",
        "DURATION": "s",
        "AV SPEED THREDHOLD": "degree/s",
        "FREEZING THRESHOLD": "cm/s",
        "SPEED THRESHOLD": "cm/s",
        "FAST FORWARD FACTOR": "times",
        "THIGMOTAXIS RANGE": "cm"
    }

# PARAMS_UNITS = {
#     "CONVERSION RATE": "pixels/cm",
#     "FRAME RATE": "frames/second",
#     "DURATION": "seconds",
# }

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



#[TODO]
"""
A. Redesign the static structure, including the Batch
    1. Add widgets to input Batch-based parameters (well-center points)              in main.py
    2. Modify the Project directory structure generation                             in Libs.project
    3. Modify the Parameter class, to import parameters correctly,                   in Libs.classes
    n. Modify the Importer so it can import the old-format project directory to the new one
    
B. Add global parameters:
    PARAMS_VALUES = {
        "CONVERSION RATE": 82,
        "FRAME RATE": 30,
        "DURATION": 180,
        "AV_SPEED_THREDHOLD": 90,
        "FREEZING_THRESHOLD": 0.06,
        "SPEED_THRESHOLD": 6 * 100 / 3600,
        "FAST_FORWARD_FACTOR": 10
    }
    PARAMS_UNITS = {
        "CONVERSION RATE": "px/cm",
        "FRAME RATE": "fps",
        "DURATION": "s",
        "AV_SPEED_THREDHOLD": "degree/s",
        "FREEZING_THRESHOLD": "cm/s",
        "SPEED_THRESHOLD": "cm/s",
        "FAST_FORWARD_FACTOR": "times"
    }
Z. Ask user for trajectories format indicator and separator
"""

