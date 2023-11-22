import os
import json
from pathlib import Path

from Libs.misc import string_diff

import logging
logger = logging.getLogger(__name__)


def get_working_dir(project_dir, day_num):
    return Path(project_dir) / f"Day {day_num}"

def get_treatment_dir(project_dir, day_num, treatment_char):
    working_dir = get_working_dir(project_dir, day_num)

    treatment_pattern = f"{treatment_char} - "

    FOUND = False

    for child_dir in os.listdir(working_dir):
        if treatment_pattern in child_dir:
            FOUND = True
            return working_dir / child_dir

    # if FOUND == False:
    #     logger.info("Detect an imported project. Searching for treatment directory in history.json")
    #     folder_info = get_folder_info(project_dir, day_num, treatment_char)
    #     for child_dir in os.listdir(working_dir):
    #         child_dir_name = Path(child_dir).name
    #         if string_diff(child_dir_name, "".join(folder_info)) == 0:
    #             FOUND = True
    #             return working_dir / child_dir
            
    if FOUND == False:
        logger.error(f"Couldn't find treatment directory with pattern [{treatment_char} -]")
        raise FileNotFoundError(f"Couldn't find treatment directory with pattern [{treatment_char} -]")

def get_static_dir(project_dir, day_num, treatment_char):
    working_dir = get_working_dir(project_dir, day_num)
    return working_dir / "static" / treatment_char



