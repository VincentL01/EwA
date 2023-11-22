import pandas as pd
import time
from pathlib import Path

from Libs.analyzer import GeneralAnalysis
from Libs.general import Parameters
from Libs.misc import count_csv_file, append_df_to_excel, excel_polish, merge_cells, check_sheet_existence, remove_sheet_by_name
from Libs.dirFetch import get_working_dir, get_treatment_dir
from . import TEMPLATE_PATH, CHARS

import logging

logger = logging.getLogger(__name__)


# class Executor(GeneralAnalysis):

#     def __init__(self, project_dir=None, day_num=1, treatment_char="A", fish_num=1):

#         super().__init__(project_dir=project_dir, day_num=day_num, treatment_char=treatment_char, fish_num=fish_num)

def EndPoints_Adder(object):

    endpoints = {}

    def add_endpoint(name, value, unit):
        endpoints[name] = {"value": value, "unit": unit}

    name = "Total Distance"
    value = object.distance.total
    unit = object.distance.unit
    add_endpoint(name, value, unit)

    name = "Average Speed"
    value = object.speed.avg
    unit = object.speed.unit
    add_endpoint(name, value, unit)

    name = "Total Absolute Turn Angle"
    value = object.turning_angle.total
    unit = object.turning_angle.unit
    add_endpoint(name, value, unit)

    name = "Average Angular Velocity"
    value = object.turning_angle.velocity.avg
    unit = object.turning_angle.velocity.unit
    add_endpoint(name, value, unit)

    name = "Slow Angular Velocity Percentage"
    value = object.turning_angle.velocity.slow
    unit = "%"
    add_endpoint(name, value, unit)

    name = "Fast Angular Velocity Percentage"
    value = object.turning_angle.velocity.fast
    unit = "%"
    add_endpoint(name, value, unit)

    name = "Meandering"
    value = object.meandering
    unit = "degree/m"
    add_endpoint(name, value, unit)

    name = "Freezing Time"
    value = object.speed.slow
    unit = "%"
    add_endpoint(name, value, unit)

    name = "Moving Time"
    value = object.speed.fast
    unit = "%"
    add_endpoint(name, value, unit)

    name = "Average distance to Center of the Tank"
    value = object.distance_to_center.avg
    unit = object.distance_to_center.unit
    add_endpoint(name, value, unit)

    name = "Time spent in Center"
    value = object.time_in_center.percentage
    unit = "%"
    add_endpoint(name, value, unit)

    name = "Total entries to the Center"
    value = object.travel_in_center.count
    unit = "times"
    add_endpoint(name, value, unit)

    name = "Fractal Dimension"
    value = object.fractal_dimension
    unit = ""
    add_endpoint(name, value, unit)

    name = "Entropy"
    value = object.entropy
    unit = ""
    add_endpoint(name, value, unit)

    return endpoints


class Executor():
        
    def __init__(self, 
                 project_dir=None, 
                 day_num=1, 
                 treatment_char="A", 
                 EndPointsAnalyze=True, 
                 progress_window=None):

        self.ERROR = None

        self.timing = {}

        self.EPA = EndPointsAnalyze

        self.progress_window = progress_window



        # FIRST CHECK
        _starttime = time.time()

        if project_dir == None:
            self.project_dir = TEMPLATE_PATH
            logger.warning("No project directory specified. Using template directory instead.")
        else:
            self.project_dir = project_dir

        try:
            _ = int(day_num)
        except:
            day_num = 1
        self.day_num = day_num

        if treatment_char == None or treatment_char not in CHARS:
            self.treatment_char = "A"
            logger.warning("No treatment index specified. Using 'A' instead.")
        else:
            self.treatment_char = treatment_char

        self.timing["Project structure"] = time.time() - _starttime
        
        self.excel_path = self.get_excel_path()


    def PARAMS_LOADING(self):

        # SECOND CHECK
        _starttime = time.time()

        logger.info("Loading parameters...")

        self.PARAMS = Parameters(project_dir = self.project_dir, 
                                 day_num = self.day_num, 
                                 treatment_char = self.treatment_char)

        try:
            self.TOTAL_FRAMES = int(self.PARAMS["DURATION"] * self.PARAMS["FRAME RATE"])
        except:
            ERROR = "Failed to load 'DURATION' and 'FRAME RATE' from parameters.json"
            logger.error(ERROR)
            return ERROR
        
        self.timing["Parameters loading"] = time.time() - _starttime

        return None

    def GROUP_LOADING(self):
        self.treatment_dir = get_treatment_dir(self.project_dir, self.day_num, self.treatment_char)
        logger.debug(f"Accessing treatment directory... {self.treatment_dir}")
        group_dirs = [x for x in Path(self.treatment_dir).iterdir() if x.is_dir()]
        self.GROUP_INFO = {}
        for i, group_dir in enumerate(group_dirs):
            group_num = i + 1
            self.GROUP_INFO[group_num] = count_csv_file(group_dir)

        # remove group with csv count == 0
        self.GROUP_INFO = {k:v for k,v in self.GROUP_INFO.items() if v > 0}

        logger.debug(f"self.GROUP_INFO = {self.GROUP_INFO}")


    def ENDPOINTS_ANALYSIS(self, OVERWRITE=False, AV_interval=None):

        # ENDPOINTS ANALYSIS
        _starttime = time.time()

        logger.info("Loading Earthworm data...")

        if self.EPA:

            REPORT = self.analyzed_check()

            if REPORT == "Analyzed" and not OVERWRITE:
                return "Existed", None
            
            if REPORT == "Analyzed" and OVERWRITE:
                logger.info(f"Removing existing sheet of {self.treatment_char}...")

                try:
                    remove_sheet_by_name(self.excel_path, self.treatment_char)
                    logger.info(f"Existing sheet of {self.treatment_char} removed.")
                except:
                    logger.error(f"Failed to remove existing sheet of {self.treatment_char}.")
                    return "Skip", None
                

        DEFAULT_INTERVAL = self.PARAMS["FRAME RATE"]

        if AV_interval == None:
            AV_interval = DEFAULT_INTERVAL
        else:
            try:
                AV_interval = int(float(AV_interval))
            except:
                AV_interval = DEFAULT_INTERVAL
                logger.error(f"Invalid AV_interval. Using default value = {self.PARAMS['FRAME RATE']} instead.")

        self.WORMS = {}
        self.EndPoints = {}

        self.Worm_Adder(EPA = self.EPA, AV_interval = AV_interval)

        if self.EPA:
            self.Export_To_Excel(excel_path = self.excel_path)
            return_excel_path = self.excel_path
        else:
            return_excel_path = None

        self.timing["EndPoints analysis"] = time.time() - _starttime

        return "Completed", return_excel_path
    
    def update_progress_bar(self, value, text):
        if self.progress_window is not None:
            self.progress_window.task_update(value, text)
    
    def get_excel_path(self):
        working_dir = get_working_dir(self.project_dir, self.day_num)
        excel_path = working_dir / "EndPoints.xlsx"
        return excel_path



    def analyzed_check(self):
        if not self.excel_path.exists():
            return "Not analyzed"
        
        # open the workbook to see if there is sheetname == self.treatment_char
        if check_sheet_existence(self.excel_path, self.treatment_char):
            return "Analyzed"
        
        return "Not analyzed"
    

    def Export_To_Excel(self, excel_path):
        EndPoints_dict = {}
        for fish_num in self.EndPoints.keys():
            EndPoints_dict[fish_num] = {}
            for key, value in self.EndPoints[fish_num].items():
                if value['unit'] == "":
                    EndPoints_dict[fish_num][f"{key}"] = value["value"]
                else:
                    EndPoints_dict[fish_num][f"{key} ({value['unit']})"] = value["value"]

        df_endpoints = pd.DataFrame(EndPoints_dict).T
        print()
        print()
        logger.debug(f"df_endpoints = {df_endpoints}")
        print()
        print()


        append_df_to_excel(filename = excel_path,
                   df = df_endpoints,
                   sheet_name=self.treatment_char)
        logger.debug(f"EndPoints.xlsx is saved to {excel_path}")

        excel_polish(excel_path)
        logger.debug(f"EndPoints.xlsx is polished.")


    def Worm_Adder(self, EPA=True, AV_interval = 1):

        for group_num, worm_quantity in self.GROUP_INFO.items():
            _starttime = time.time()
            for worm_num in range(1, worm_quantity+1):
                self.WORMS[f"Group {group_num} - Well {worm_num}"] = GeneralAnalysis(project_dir = self.project_dir,
                                                                                    day_num = self.day_num,
                                                                                    treatment_char = self.treatment_char,
                                                                                    group_num = group_num,
                                                                                    worm_num = worm_num,
                                                                                    params = self.PARAMS)
                if EPA == True:
                    logger.info(f"EndPoints analysis for Group {group_num} - Well {worm_num} initiated...")
                    self.WORMS[f"Group {group_num} - Well {worm_num}"].BasicCalculation(DEFAULT_INTERVAL = AV_interval)
                    self.EndPoints[f"Group {group_num} - Well {worm_num}"] = EndPoints_Adder(self.WORMS[f"Group {group_num} - Well {worm_num}"])
                    logger.debug(f'After processing {worm_num}, self.EndPoints = {self.EndPoints[f"Group {group_num} - Well {worm_num}"]}')
                else:
                    logger.info(f"EndPoints analysis for Group {group_num} - Well {worm_num} skipped.")
                
                self.timing[f"Analyze Group {group_num} - Well {worm_num}"] = time.time() - _starttime

                progress = (group_num-1) / len(self.GROUP_INFO) * 100 + worm_num / worm_quantity / len(self.GROUP_INFO) * 100
                self.update_progress_bar(value=progress, text = f"Analyze Group {group_num} - Well {worm_num}")

            logger.debug(f'After processing {group_num}, self.EndPoints = {self.EndPoints[f"Group {group_num} - Well {worm_num}"]}')
            
    
    
            
                                                    
    
    

    


