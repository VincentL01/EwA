from pathlib import Path
import math
import pandas as pd


from Libs.general import Loader, Time, Events, Area, Distance, Speed, Angle, Speed_A
from Libs.calculation import FD_Entropy_Calculator_2D, calculate_turning_angle
from Libs.misc import event_extractor
from . import SPEED_THRESHOLD, FAST_FORWARD_FACTOR, FREEZING_THRESHOLD

import logging

logger = logging.getLogger(__name__)


class GeneralAnalysis(Loader):
    def __init__(self, project_dir, day_num, treatment_char, group_num, worm_num, params):
        super().__init__(project_dir = project_dir, 
                         day_num=day_num, 
                         treatment_char=treatment_char, 
                         group_num=group_num,
                         worm_num=worm_num,
                         params = params
                         )
        
    
    def BasicCalculation(self, DEFAULT_INTERVAL = 1):

        if DEFAULT_INTERVAL > self.PARAMS["FRAME RATE"]:
            logger.error(f"User set {DEFAULT_INTERVAL=} but {self.PARAMS['FRAME RATE']=} is smaller than {DEFAULT_INTERVAL=}. Please check the code.")
            raise Exception(f"{self.PARAMS['FRAME RATE']=} is smaller than {DEFAULT_INTERVAL=}. Please check the code.")

        if self.PARAMS["FRAME RATE"] % DEFAULT_INTERVAL != 0:
            logger.error(f"User set {DEFAULT_INTERVAL=} but {self.PARAMS['FRAME RATE']=} is not divisible by {DEFAULT_INTERVAL=}. Please check the code.")
            raise Exception(f"{self.PARAMS['FRAME RATE']=} is not divisible by {DEFAULT_INTERVAL=}. Please check the code.")


        self.distance = self.distance_traveled()

        #####################################################################################

        NORMALIZED_SPEED_THRESHOLD = SPEED_THRESHOLD * FAST_FORWARD_FACTOR
        speed_list = []
        replace_count = 0
        for i in range(len(self.distance.list)):
            # Speed = Distance/Time
            speed = self.distance.list[i]/(1/self.PARAMS["FRAME RATE"])
            if speed >= NORMALIZED_SPEED_THRESHOLD:
                # logger.debug(f"Speed of {speed} cm/s detected at frame {i} (index {i+1})")
                # Find the nearest frame with speed < SPEED_THRESHOLD
                for j in range(i-1, 0, -1):
                    if speed_list[j] < NORMALIZED_SPEED_THRESHOLD:
                        # Replace the speed with the nearest frame
                        speed = speed_list[j]
                        # logger.debug(f"Speed replaced with {speed} cm/s at frame {j} (index {j+1})")
                        replace_count += 1
                        break
            
            speed_list.append(speed)
            # UNIT: cm/s

        logger.debug(f"Speed replaced {replace_count} times due to speed > {NORMALIZED_SPEED_THRESHOLD} cm/s, FAST_FORWARD_FACTOR = {FAST_FORWARD_FACTOR}")

        self.speed = Speed(speed_list = speed_list,
                           total_frames=self.TOTAL_FRAMES,
                           threshold = FREEZING_THRESHOLD)

        #####################################################################################

        # We only care about the turning angle of the fish on XY plane
        # We don't care about the turning angle of the fish on Z axis
        # Because the fish is not supposed to turn on Z axis

        turning_angle = TurningAngles(X_coords = self.WORM['X'].tolist(),
                                      Y_coords = self.WORM['Y'].tolist())
        
        
        self.turning_angle = Angle(angle_class = turning_angle, 
                                   frame_rate=self.PARAMS["FRAME RATE"], 
                                   interval = DEFAULT_INTERVAL)

        #####################################################################################
        
        self.meandering = self.turning_angle.total / self.distance.total * 100

        #####################################################################################

        self.distance_to_center = self.distance_to(TARGET="CENTER") # Object of Distance class

        self.time_in_center = self.within_range(distance_list = self.distance_to_center.list)
        self.time_in_center = Time(time_list = self.time_in_center)

        #####################################################################################

        self.travel_in_center = event_extractor(self.time_in_center.list, positive_token=1)
        self.travel_in_center = Events(event_dict = self.travel_in_center, duration=self.PARAMS["DURATION"])

        #####################################################################################

        self.fractal_dimension, self.entropy = FD_Entropy_Calculator_2D(self.WORM)

        #####################################################################################



class TurningAngles():

    def __init__(self, X_coords, Y_coords):

        self.X_coords = X_coords
        self.Y_coords = Y_coords

    def turning_angles(self, interval=1):
        """
        Calculate the turning angles of the fish
        :param interval: the interval between two points
        :return: a list of turning angles
        """
        turning_angles = []

        intervalized_X_coords = self.X_coords[::interval]
        intervalized_Y_coords = self.Y_coords[::interval]

        for i in range(len(intervalized_X_coords) - 2):
            turning_angle = calculate_turning_angle(intervalized_X_coords[i], intervalized_Y_coords[i], intervalized_X_coords[i + 1], intervalized_Y_coords[i + 1], intervalized_X_coords[i + 2], intervalized_Y_coords[i + 2])
            turning_angles.append(turning_angle)

        # for i in range(len(self.X_coords) - 2 * interval):
        #     turning_angle = compute_turning_angle(self.X_coords[i], self.Y_coords[i], self.X_coords[i + interval], self.Y_coords[i + interval], self.X_coords[i + 2 * interval], self.Y_coords[i + 2 * interval])
        #     turning_angles.append(turning_angle)

        return turning_angles
    