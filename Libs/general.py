import pandas as pd
import numpy as np
import os
import math
from pathlib import Path
import json
import re
from statistics import mean
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment
from scipy.stats import pearsonr

from Libs.misc import *
from . import ALLOWED_DECIMALS, RAW_FORMAT_SEPARATOR, RAW_FORMAT_INDICATOR
from . import BATCH_FOLDER_FORMAT, CHARS, NEG_INF, POS_INF, DEFAULT_PARAMS
from . import WELL_CENTER_POINTS, CENTER_RANGE
from Libs.dirFetch import get_static_dir, get_treatment_dir

import logging

logger = logging.getLogger(__name__)



    
    

################################################### LOADER ######################################################## 

class Parameters():

    def __init__(self, project_dir=None, day_num=1, treatment_char="A"):

        if project_dir == None:
            self.project_dir = ""
            logger.warning("No project directory specified. Using template directory instead.")
        else:
            self.project_dir = project_dir

        if treatment_char not in CHARS:
            treatment_char = "A"
            logger.warning("Treatment character not specified. Using A as default.")

        static_dir = get_static_dir(self.project_dir, day_num, treatment_char)
            
        self.param_path = static_dir / "parameters.json"

        self.PARAMS = self.FirstLoad()

    def __getitem__(self, key, refresh=False):
        if refresh:
            self.Refresh()
        return self.PARAMS.get(key, None)
    

    def Refresh(self):
        self.PARAMS = self.Load(self)


    def Update(self, modify_dict):

        PARAMS = self.Load(self)
        
        for key, value in modify_dict.items():
            PARAMS[key] = value

        with open(self.param_path, 'w') as file:
            json.dump(PARAMS, file, indent=4)
        
        logger.info("Parameters updated.")
        self.PARAMS = PARAMS


    def Load(self):

        try:
            with open(self.param_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error(f"parameters.json not found at {self.param_path}, please check your input.")
            return None
        
        # Convert all values to float
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    data[key] = to_int_or_float(value)
                except:
                    raise ValueError(f"INVALID FORMAT: Value of {key} is a non-convertible string ({value=}), please check your input.")
            elif isinstance(value, (int, float)):
                data[key] = to_int_or_float(value)
            elif isinstance(value, dict):
                for well_num, coord_dict in value.items():
                    for axis, coord in coord_dict.items():
                        try:
                            data[key][well_num][axis] = to_int_or_float(coord)
                        except:
                            raise ValueError(f"INVALID FORMAT: Value of {key} is not convertible ({data[key][well_num][axis]}), please check your input.")
            else:
                # get value type of value
                value_type = type(value)
                raise ValueError(f"INVALID FORMAT: At {key}, {value=} is a {value_type}, please check your input.")

        return data
    

    def FirstLoad(self):

        logger.info("Initializing parameters...")
        data = self.Load()
        if data == None:
            logger.info("Creating new parameters.json...")
            data = DEFAULT_PARAMS
            with open(self.param_path, 'w') as file:
                json.dump(data, file, indent=4)

        return data




class Loader():
    
    def __init__(self, project_dir, day_num, treatment_char, group_num, worm_num, params):

        self.project_dir = project_dir
        self.day_num = day_num
        self.treatment_char = treatment_char
        self.worm_num = worm_num
        self.PARAMS = params

        self.group_name = BATCH_FOLDER_FORMAT.format(group_num)

        try:
            self.TOTAL_FRAMES = int(self.PARAMS["DURATION"] * self.PARAMS["FRAME RATE"])
        except:
            logger.error("Failed to load 'DURATION' and 'FRAME RATE' from parameters.json")
            raise ValueError("Failed to load 'DURATION' and 'FRAME RATE' from parameters.json")
        
        self.treatment_dir = get_treatment_dir(project_dir = self.project_dir, 
                                               day_num = self.day_num, 
                                               treatment_char = self.treatment_char)
        
        self.GROUP = self.GroupLoader()
        self.Loaded = self.assign_worm()


    ################################# FISH LOADER #################################

    def assign_worm(self):
        # try:
        #     self.WORM = self.GROUP[str(worm_num)]
        #     self.EXTRA_PARAMS = {}
        #     self.EXTRA_PARAMS["CENTER X"] = WELL_CENTER_POINTS[str(worm_num)]["X"]
        #     self.EXTRA_PARAMS["CENTER Y"] = WELL_CENTER_POINTS[str(worm_num)]["Y"]
        #     return True
        # except KeyError:
        #     logger.error(f"Failed to load worm {worm_num} from {self.group_name}")
        #     return False
        try:
            self.WORM = self.GROUP[str(self.worm_num)]
        except KeyError:
            logger.error(f"Failed to load worm {self.worm_num} from {self.group_name}")
            return False
        return True
        
    def GroupLoader(self):

        group_path = self.treatment_dir / self.group_name
        # find all file with RAW_FORMAT_INDICATOR
        raw_files = list(group_path.glob(f"*{RAW_FORMAT_INDICATOR}"))

        if len(list(raw_files)) == 0:
            logger.error(f"No raw files found at {group_path}")
            raise FileNotFoundError(f"No raw files found at {group_path}")

        group_dict = find_uncommon_substrings_in_paths(raw_files)
        # group_dict = {f.name.split(RAW_FORMAT_SEPARATOR)[-1].split(RAW_FORMAT_INDICATOR)[0].strip():f for f in raw_files}
        for worm_num, csv_path in group_dict.items():
            group_dict[worm_num] = self.WormLoader(csv_path) # Return as dataframe of 2 columns X and Y
        
        return group_dict

    def WormLoader(self, csv_path):
        df = pd.read_csv(csv_path, header=0, index_col=0)
        if len(df.columns) == 2:
            df.columns = ["X", "Y"]
        elif len(df.columns) == 3:
            df.columns = ["X", "Y", "Z"]
        return df
    
    def distance_traveled(self):
        distance_list = []

        for i in range(len(self.WORM)-1):
            distance = 0
            for axis in self.WORM.columns:
                distance += (self.WORM[axis].iloc[i+1] - self.WORM[axis].iloc[i])**2
            distance = math.sqrt(distance)
            distance = distance / self.PARAMS["CONVERSION RATE"]
            distance = round(distance, ALLOWED_DECIMALS)
            distance_list.append(distance)
            # UNIT: cm

        return Distance(distance_list = distance_list)
    
    def distance_to(self, TARGET = "CENTER"):
        distance_list = []
        try:
            all_worm_target_params = self.PARAMS[TARGET]
        except KeyError:
            logger.error(f"Failed to load {TARGET} from parameters.json")
            raise KeyError(f"Failed to load {TARGET} from parameters.json")
        
        try:
            target_params = all_worm_target_params[str(self.worm_num)]
        except KeyError:
            logger.error(f"Failed to load {TARGET} for worm {self.worm_num}")
            raise KeyError(f"Failed to load {TARGET} for worm {self.worm_num}")
        
        for _, row in self.WORM.iterrows():
            distance = 0
            for axis, param_coord in target_params.items():
                try:
                    row_value = row[axis]
                except KeyError:
                    _message = f"No {axis} coordinate found in Treatment {self.treatment_char}, {self.group_name}, Worm {self.worm_num}"
                    logger.error(_message)
                    raise KeyError(_message)
                distance += (row_value - param_coord) ** 2

            distance = np.sqrt(distance)
            distance = distance/self.PARAMS["CONVERSION RATE"]
            distance = round(distance, ALLOWED_DECIMALS)
            distance_list.append(distance)

        return Distance(distance_list)
    
    def within_range(self, distance_list):
        return [1 if distance <= self.PARAMS["THIGMOTAXIS RANGE"] else 0 for distance in distance_list]


class CustomDisplay():

    def __init__(self):

        pass

    def get_variables(self, magic = False):

        self_dir = [x for x in dir(self) if x not in dir(CustomDisplay)]
        if magic:
            return self_dir
        else:
            return [x for x in self_dir if not x.startswith('__')]

    def __str__(self):

        message = "Variables:\n"
        for variable in self.get_variables():
            message += f'{str(variable)}: {str(getattr(self, variable))}\n'

        return message


class Time(CustomDisplay):

    def __init__(self, time_list):

        self.list = time_list  # [1, 1, 1, 0, 0, 0, 1, 0]

        self.duration = sum(self.list)  # in frames
        # print(f'Duration: {self.duration} / {len(self.list)}')
        self.percentage = self.duration / len(self.list) * 100
        self.not_duration = len(self.list) - self.duration  # in frames
        self.not_percentage = 100 - self.percentage
        self.unit = 'frames'

    

class Events(CustomDisplay):

    def __init__(self, event_dict, duration):

        self.dict = event_dict

        if '-1' in event_dict.keys():
            self.count = 0
            self.longest = 0
            self.percentage = 0
            # take out this key
            self.dict.pop('-1')
        else:
            self.count = len(self.dict)
            try:
                self.longest = max(self.dict.values())
            except ValueError:
                self.longest = 0
            self.percentage = self.longest / duration * 100

        self.unit = 'frames'



class Area(CustomDisplay):

    def __init__(self, area_list):

        self.list = area_list
        self.avg = round(mean(self.list), ALLOWED_DECIMALS)
        self.unit = 'cm^2'
    

    def __add__(self, other):

        temp_list = self.list + other.list
        return Area(temp_list, self.hyp)
    


class Distance(CustomDisplay):

    def __init__(self, distance_list):

        self.list = distance_list

        self.total = round(sum(self.list), ALLOWED_DECIMALS)
        self.avg = round(mean(self.list), ALLOWED_DECIMALS)
        self.unit = 'cm'


    def __add__(self, other):

        temp_list = self.list + other.list
        return Distance(temp_list, self.hyp)
    


class Speed(CustomDisplay):

    def __init__(self, speed_list, total_frames, threshold):

        self.list = speed_list
        self.total_frames = total_frames
        self.threshold = threshold

        self.max = round(max(self.list), ALLOWED_DECIMALS)
        self.min = round(min(self.list), ALLOWED_DECIMALS)
        self.avg = round(mean(self.list), ALLOWED_DECIMALS)
        self.unit = 'cm/s'

        self.Classifier()

    
    def __add__(self, other):

        # Check if other has list and total_frames
        if not hasattr(other, 'list') or not hasattr(other, 'total_frames'):
            raise AttributeError("Other object doesn't have 'list' or 'total_frames' attribute")

        temp_list = self.list + other.list

        if self.total_frames != other.total_frames:
            raise ValueError(f"Total frames of self and other are not the same, {self.total_frames=} != {other.total_frames=}")
        else:
            return Speed(temp_list, self.total_frames)

    def Classifier(self):

        slow_count = 0
        fast_count = 0

        for speed in self.list:
            if speed < self.threshold:
                slow_count += 1
            else:
                fast_count += 1

        self.slow = round(slow_count / self.total_frames * 100, ALLOWED_DECIMALS)
        self.fast = round(fast_count / self.total_frames * 100, ALLOWED_DECIMALS)

        

class Angle(CustomDisplay):

    def __init__(self, angle_class, frame_rate, interval=1):

        self.angle_class = angle_class
        self.frame_rate = frame_rate

        self.interval = -1
        self.set_interval(interval=interval)


    def calculate_velocity(self):

        def chunk_calc(input_list : list[float], chunk_size : int) -> list[float]:
            logger.debug(f"Calculated angular velocity using chunk_calc(), {chunk_size=}")
            return [abs(sum(input_list[i:i+chunk_size]))%180 for i in range(0, len(input_list), chunk_size)]
        
        # angular_velocity_list = []
        # for i in range(len(self.list)):
        #     # Angular velocity = Turning angle/Time
        #     angular_velocity = self.list[i]
        #     angular_velocity_list.append(angular_velocity)
        #     # UNIT: degree/s
        chunk_size = int(self.frame_rate/self.interval)
        print(f"{chunk_size=}, {self.frame_rate=} {self.interval=}")
        angular_velocity_list = chunk_calc(input_list=self.list, chunk_size=chunk_size)

        # [NOTE] Used same name for the class and the variablwe to save memory, but they are different
            
        angular_velocity = Speed_A(speed_a_list = angular_velocity_list)

        return angular_velocity
    

    def set_interval(self, interval):
        
        if self.interval == interval:
            logger.warning(f"Interval is already {self.interval}, no need to set again.")
        else:
            logger.info(f"Setting interval to {interval}")
            self.interval = interval
            
            self.list = self.angle_class.turning_angles(interval=self.interval)
            self.absolute = [abs(x) for x in self.list]
            self.total = round(sum(self.absolute), ALLOWED_DECIMALS)
            self.avg = round(mean(self.absolute), ALLOWED_DECIMALS)
            self.unit = 'degree'

            self.velocity = self.calculate_velocity()



class Speed_A(CustomDisplay):

    def __init__(self, speed_a_list, THRESHOLD = 90):

        self.list = speed_a_list
        self.total_instances = len(self.list)

        self.max = round(max(self.list), ALLOWED_DECIMALS)
        self.min = round(min(self.list), ALLOWED_DECIMALS)
        self.avg = round(mean(self.list), ALLOWED_DECIMALS)
        self.unit = 'degree/s'

        self.Classifier(THRESHOLD)


    def Classifier(self, THRESHOLD):

        slow_count = 0
        fast_count = 0

        for i, speed in enumerate(self.list):
            if speed < 0:
                raise Exception(f"Negative speed, {speed=} found, please check your input.")
            if speed > 181:
                raise Exception(f"Speed > 180, {speed=} found at position {i}/{len(self.list)} please check your input.")
            
            if speed <= THRESHOLD:
                slow_count += 1
            else:
                fast_count += 1

        self.slow = round(slow_count / self.total_instances * 100, ALLOWED_DECIMALS)
        self.fast = round(fast_count / self.total_instances * 100, ALLOWED_DECIMALS)

    
    def plot_histogram(self, bins=100, DISPLAY=True, save_path=None, excel_path=None, fish_num=None):

        #reset figure
        plt.clf()

        percentile = plt.hist(self.list, bins=bins)
        plt.title('Angular Velocity')
        plt.xlabel('Angular Velocity (degree/s)')
        plt.ylabel('Frequency')
        if save_path:
            # if save_path file existed, overwrite
            if os.path.exists(save_path):
                os.unlink(save_path)
            plt.savefig(save_path)

        if excel_path and fish_num:
            if fish_num == 1:
                os.unlink(excel_path)
            if os.path.exists(excel_path):
                index=False
            else:
                index=True
            df = pd.DataFrame({f'Fish {fish_num}': self.list})
            append_df_to_excel(filename=excel_path,
                                df=df,
                                sheet_name='Angular Velocity',
                                startrow=0,
                                index=index)

        if DISPLAY:
            plt.show()

        thresholds = percentile[1]
        percentile = percentile[0]
        percentile = percentile.tolist()
        percentile = [i/sum(percentile) for i in percentile]

        print(f"Percentile: {percentile}")
        print(f"Thresholds: {thresholds}")
        