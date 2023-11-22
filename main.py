import tkinter
import tkinter.messagebox
import tkinter.ttk as ttk
import customtkinter

import os
from pathlib import Path

import pandas as pd
import json

import shutil
import time

import logging
from colorlog import ColoredFormatter

import threading

from Libs import CHARS, ORDINALS, HISTORY_PATH
from Libs.misc import initiator, open_explorer
from Libs.classes import *
from Libs.project import CreateProject
from Libs.executor import Executor


customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("Libs/dark_red.json")


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

Path('Log').mkdir(parents=True, exist_ok=True)
log_file = 'Log/log.txt'


class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    def filter(self, record):
        record.pathname = os.path.basename(record.pathname)  # Modify this line if you want to alter the path
        return True

# Define the log format with colors
log_format = "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s [%(pathname)s] %(message)s"

# Create a formatter with colored output
formatter = ColoredFormatter(log_format)

# Get the root logger

# Create a filter
f = ContextFilter()

# Create a file handler to save logs to the file
file_handler = logging.FileHandler(log_file, mode='a')  # Set the mode to 'a' for append
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s [%(pathname)s] %(message)s"))
file_handler.addFilter(f)  # Add the filter to the file handler
file_handler.setLevel(logging.DEBUG)

# Create a stream handler to display logs on the console with colored output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.addFilter(f)  # Add the filter to the stream handler
stream_handler.setLevel(logging.DEBUG)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

########################################################################################################################
initiator()

THE_HISTORY = HISTORY()

########################################################################################################################

class MainApp(customtkinter.CTk):

    def __init__(self):

        super().__init__()


        # PREDEFINED VARIABLES
        self.PROJECT_CREATED = False
        self.CURRENT_PROJECT = ""
        self.PREVIOUS_DAY = ""
        self.PREVIOUS_TREATMENT = ""
        self.TREATMENTLIST = ["Treatment A", "Treatment B", "Treatment C"]
        self.EPA = True

        # configure window
        APP_TITLE = "Earthworm Analyzer"
        self.title(APP_TITLE)
        self.geometry(f"{1500}x{900}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0) 
        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        ### COLUMN 0 ###

        TEXT_COLOR = "#000000"
        BOX_TEXT_COLOR = "Yellow"
        TINY_SIZE = 14
        SMALL_SIZE = TINY_SIZE + 2
        MEDIUM_SIZE = SMALL_SIZE + 2
        LARGE_SIZE = MEDIUM_SIZE + 4
        UNIVERSAL_FONT = 'Microsoft Sans Serif'
        HOVER_COLOR = "Orange"

        LOGO_CONFIG = {
                        "font": (UNIVERSAL_FONT, LARGE_SIZE, "bold"),
                        "text_color": TEXT_COLOR
        }

        LABEL_CONFIG = {
                        "font": (UNIVERSAL_FONT, SMALL_SIZE),
                        "text_color": TEXT_COLOR
        }

        BOLD_LABEL_CONFIG = {
                        "font": (UNIVERSAL_FONT, MEDIUM_SIZE, "bold"),
                        "text_color": TEXT_COLOR
        }

        BUTTON_CONFIG = {"font": (UNIVERSAL_FONT, SMALL_SIZE), 
                         "text_color": BOX_TEXT_COLOR,
                         "hover_color": HOVER_COLOR
        }

        PANEL_BUTTON_CONFIG = {"font": (UNIVERSAL_FONT, SMALL_SIZE), 
                         "width": 150, 
                         "height": 40,
                         "text_color": BOX_TEXT_COLOR,
                         "hover_color": HOVER_COLOR
        }

        OPTION_MENU_CONFIG = {"font": (UNIVERSAL_FONT, TINY_SIZE),
                            "text_color": BOX_TEXT_COLOR,
        }

        ############################### Start of sidebar frame ###################################

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        SIDEBAR_ROW = 0
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text=APP_TITLE)
        self.logo_label.configure(**LOGO_CONFIG)
        self.logo_label.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        SIDEBAR_ROW += 1
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, 
                                                        text="Create Project", 
                                                        command=self.create_project
                                                        )
        self.sidebar_button_1.configure(**PANEL_BUTTON_CONFIG)
        self.sidebar_button_1.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=20)

        SIDEBAR_ROW += 1
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, 
                                                        text="Load Project", 
                                                        command=self.load_project
                                                        )
        self.sidebar_button_2.configure(**PANEL_BUTTON_CONFIG)
        self.sidebar_button_2.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=20)
        
        SIDEBAR_ROW += 1
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, 
                                                        text="Delete Project", 
                                                        command=self.delete_project
                                                        )
        self.sidebar_button_3.configure(**PANEL_BUTTON_CONFIG)
        self.sidebar_button_3.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=20)

        SIDEBAR_ROW += 1
        self.ImportButton = customtkinter.CTkButton(self.sidebar_frame, 
                                                         text="Import Trajectories",
                                                         command=self.import_trajectories
                                                         )
        self.ImportButton.configure(**PANEL_BUTTON_CONFIG)
        self.ImportButton.grid(row=SIDEBAR_ROW, column=0, columnspan = 2, padx=20, pady=20)

        SIDEBAR_ROW += 1
        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, 
                                                        text="Analyze", 
                                                        command=self.analyze_project_THREADED
                                                        )
        self.sidebar_button_5.configure(**PANEL_BUTTON_CONFIG)
        self.sidebar_button_5.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=20)

        SIDEBAR_ROW += 1
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.configure(**LABEL_CONFIG)
        self.appearance_mode_label.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=(10, 0))
        
        ############################### Appearance Mode Option Menu ###############################

        SIDEBAR_ROW += 1
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, 
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.configure(**OPTION_MENU_CONFIG)
        self.appearance_mode_optionmenu.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=(10, 10))
        
        SIDEBAR_ROW += 1
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.configure(**LABEL_CONFIG)
        self.scaling_label.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=(10, 0))

        SIDEBAR_ROW += 1
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, 
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.configure(**OPTION_MENU_CONFIG)
        self.scaling_optionemenu.grid(row=SIDEBAR_ROW, column=0, columnspan=2, padx=20, pady=(10, 20))

        ############################### End of sidebar frame ####################################


        ############################### Start of main frame #####################################

        ## COLUMN 1 ###

        container_1 = customtkinter.CTkFrame(self)
        container_1.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        container_1.grid_rowconfigure(0, weight=0)
        container_1.grid_rowconfigure(1, weight=1)
        container_1.grid_columnconfigure(0, weight=0)

        # Top part
        container_2_top = customtkinter.CTkFrame(container_1)
        container_2_top.grid(row=0, column=0, sticky="nsew")

        project_previews_label = customtkinter.CTkLabel(container_2_top, text="Project List", font=customtkinter.CTkFont(size=20, weight="bold"))
        project_previews_label.configure(**BOLD_LABEL_CONFIG)
        project_previews_label.grid(row=0, column=0)

        # Bottom part
        bottom_part = customtkinter.CTkFrame(container_1)
        bottom_part.grid(row=1, column=0, sticky="nsew")

        bottom_part.grid_rowconfigure(0, weight=1)
        bottom_part.grid_rowconfigure(1, weight=0)

        self.scrollable_frame = ScrollableProjectList(bottom_part)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")

        refresh_button = customtkinter.CTkButton(bottom_part, text="Refresh", command=self.refresh_projects)
        refresh_button.configure(**BUTTON_CONFIG)
        refresh_button.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Initial refresh to populate the list
        self.refresh_projects()

        self.project_detail_container = ProjectDetailFrame(self, self.CURRENT_PROJECT, width = 400)
        self.project_detail_container.grid(row=1, column = 1, columnspan=3, padx=20, pady=20, sticky="nsew")

        ### COLUMN 2 ###

        column2_padx = 20
        column2_pady = (10,5)

        # Create a canvas to hold the project parameters
        container_2 = customtkinter.CTkFrame(self, width = 400)
        container_2.grid(row=0, column=2, columnspan = 2, padx=(column2_padx, 0), pady=column2_pady, sticky="nsew")

        # ROW 0
        CONTAINER_2_ROW = 0
        # Top part is a dropdown menu to select type of test
        container_2_top = customtkinter.CTkFrame(container_2)
        container_2_top.grid(row=CONTAINER_2_ROW, column=0, columnspan=3, sticky="nsew")

        CONTAINER_2_TOP_ROW =0
        Header = customtkinter.CTkLabel(container_2_top, text="Loaded Project:", anchor="w")
        Header.configure(**BOLD_LABEL_CONFIG)
        Header.grid(row=CONTAINER_2_TOP_ROW, column=0, padx=column2_padx, pady=column2_pady, sticky="nsew")

        self.LoadedProject = customtkinter.CTkLabel(container_2_top, text="None", anchor="w")
        self.LoadedProject.configure(**BOLD_LABEL_CONFIG)
        self.LoadedProject.grid(row=CONTAINER_2_TOP_ROW, column=1, columnspan=2, padx=column2_padx, pady=column2_pady, sticky="nsew")

        # ROW 1
        CONTAINER_2_ROW += 1
        self.DAYLIST = ["Day 1"]
        self.container_2_mid = customtkinter.CTkFrame(container_2)
        self.container_2_mid.grid(row=CONTAINER_2_ROW, column=0, columnspan=3, sticky="nsew")

        CONTAINER_2_MID_ROW = 0
        self.DayOptions = customtkinter.CTkOptionMenu(self.container_2_mid, dynamic_resizing=False,
                                                        width = 105, values=self.DAYLIST)
        self.DayOptions.configure(**OPTION_MENU_CONFIG)
        self.DayOptions.grid(row=CONTAINER_2_MID_ROW, column=0, padx=column2_padx, pady=column2_pady, sticky="nsew")

        self.DayAddButton = customtkinter.CTkButton(self.container_2_mid, text="Add Day", width = 40,
                                                        command=self.add_day)
        self.DayAddButton.configure(**BUTTON_CONFIG)
        self.DayAddButton.grid(row=CONTAINER_2_MID_ROW, column=1, padx=column2_padx, pady=column2_pady, sticky="nsew")

        self.DayRemoveButton = customtkinter.CTkButton(self.container_2_mid, text="Remove Day", width = 40,
                                                        command=self.remove_day)
        self.DayRemoveButton.configure(**BUTTON_CONFIG)
        self.DayRemoveButton.grid(row=CONTAINER_2_MID_ROW, column=2, padx=column2_padx, pady=column2_pady, sticky="nsew")
        
        CONTAINER_2_MID_ROW += 1
        self.TreatmentOptions = customtkinter.CTkOptionMenu(self.container_2_mid, dynamic_resizing=False,
                                                                width=210, values=self.TREATMENTLIST)
        self.TreatmentOptions.configure(**OPTION_MENU_CONFIG)
        self.TreatmentOptions.grid(row=CONTAINER_2_MID_ROW, column=0, columnspan=2, padx=column2_padx, pady=column2_pady, sticky="nsew")

        # Row 2
        CONTAINER_2_ROW += 1
        self.container_2_bot = customtkinter.CTkFrame(container_2)
        self.container_2_bot.grid(row=CONTAINER_2_ROW, column=0, columnspan=3, sticky="nsew")

        project_dir = THE_HISTORY.get_project_dir(self.CURRENT_PROJECT)

        CONTAINER_2_BOT_ROW = 0
        self.parameters_frame = Parameters(self.container_2_bot, project_dir, height = 500, width = 400)
        self.parameters_frame.grid(row=CONTAINER_2_BOT_ROW, columnspan=3, padx=20, pady=20, sticky="nsew")

        # Config
        self.DayOptions.configure(command=self.update_param_display)
        # self.TestOptions.configure(command=self.update_param_display)
        self.TreatmentOptions.configure(command=self.update_param_display)

        self.protocol("WM_DELETE_WINDOW", self.close_app)

    ################################################# HISTORY ACCESS #######################################################    

    def access_history(self, command_type, project_name = None, day_name=None, edit_command=None):
        logger.debug("Accessing history file")

        # load the history file
        try:
            with open(HISTORY_PATH, "r") as file:
                projects_data = json.load(file)
        except:
            ErrorType = f"Empty history file at path {HISTORY_PATH}"
            logger.warning(ErrorType)
            return None, ErrorType

        # current project name
        if project_name == None:
            logger.debug(f"No given project name, using {self.CURRENT_PROJECT=}")
            cp = self.CURRENT_PROJECT
        else:
            logger.debug(f"Use given project name: {project_name=}")
            cp = project_name

        # Check if the project exists
        if cp not in projects_data.keys():
            ErrorType = f"Project {cp} doesn't exist"
            logger.warning(ErrorType)
            return None, ErrorType
        
        # Check if the project directory exists
        project_dir = projects_data[cp]["DIRECTORY"]
        if not os.path.isdir(project_dir):
            project_dir = THE_HISTORY.find_dir(project_name = cp)
    
        # How many Day files are there?
        day_quantity = 0
        day_list = []
        for key in projects_data[cp].keys():
            if "Day" in key:
                day_quantity += 1
                day_list.append(key)

        if day_quantity == 0:
            ErrorType = "No Dayes"
            logger.warning(ErrorType)
            return None, ErrorType

        # Modify the history file
        if command_type == "add":
            logger.debug("Command = add")
            if day_name in projects_data[cp].keys():
                ErrorType = f"Day {day_name=} already exists, can't add"
                logger.warning(ErrorType)
                return None, ErrorType
            else:
                example_key = list(projects_data[cp].keys())[0]
                projects_data[cp][day_name] = projects_data[cp][example_key]
                with open(HISTORY_PATH, "w") as file:
                    json.dump(projects_data, file, indent=4)
                return None, None
            
        elif command_type == "remove":
            logger.debug("Command = remove")
            if day_quantity == 1:
                ErrorType = "Last Day, can't remove"
                logger.warning(ErrorType)
                return None, ErrorType
            elif day_name not in projects_data[cp].keys():
                ErrorType = f"{day_name} doesn't exist"
                logger.warning(ErrorType)
                return None, ErrorType
            else:
                # Remove the Day
                projects_data[cp].pop(day_name)
                with open(HISTORY_PATH, "w") as file:
                    json.dump(projects_data, file, indent=4)
                return None, None
            
        elif command_type == "edit":
            logger.debug("Command = edit")
            if edit_command == None:
                ErrorType = "No edit command given"
                logger.warning(ErrorType)
                return None, ErrorType
            else:
                treatment = edit_command[0]
                value_pos = edit_command[1]
                new_value = edit_command[2]
                try:
                    projects_data[cp][day_name][treatment][value_pos] = new_value
                    with open(HISTORY_PATH, "w") as file:
                        json.dump(projects_data, file, indent=4)
                    return None, None
                except:
                    logger.error("Invalid edit command")
                    raise Exception("Invalid edit command")

        elif command_type == "load day list":
            logger.debug("Command = load day list")
            return day_list, None
        
        elif command_type == "load treatment list":
            logger.debug("Command = load treatment list")
            logger.debug(f"CP: {cp} ,Day name: {day_name}")
            treatments = []
            key_list = list(projects_data[cp][day_name].keys())
            if key_list == 0:
                logger.warning(f"cp = {cp}, day_name = {day_name}, no treatments found")
            for treatment_key in projects_data[cp][day_name].keys():
                _name = projects_data[cp][day_name][treatment_key][0]
                _dose = projects_data[cp][day_name][treatment_key][1]
                _unit = projects_data[cp][day_name][treatment_key][2]
                if _unit == "":
                    treatments.append(_name)
                else:
                    treatments.append(f"{_name} {_dose} {_unit}")
            logger.debug(f"Treatments: {treatments}")
            return treatments, None
        
        else:
            logger.error("Invalid command type")
            raise Exception("Invalid command type")


    ##################################################### UPDATER ############################################################    

    def refresh(self):
        self.update_param_display(load_type = "refresh")
        self.refresh_projects_detail()

    def save_parameters(self, mode = "current", save_target="self"):
        assert mode in ["current", "previous"]

        if mode == "current":
            logger.debug("Save button pressed, save the current parameters")
            # Get the selected test type
            day_num = self.get_day_num()
            treatment_char = self.get_treatment_char()
            logger.debug(f"day num: {day_num}")
            logger.debug(f"treatment: {treatment_char}")
        else:
            logger.debug("Other option selected, save the previous parameters")
            day_num = self.PREVIOUS_DAY
            treatment_char = self.PREVIOUS_TREATMENT
            logger.debug(f"day num: {day_num}")
            logger.debug(f"treatment: {treatment_char}")

        # Save the parameters
        # save_parameters(self, project_name, selected_task, treatment, day_num, mode = 'single'):
        project_dir = THE_HISTORY.get_project_dir(self.CURRENT_PROJECT)
        self.parameters_frame.save_parameters(project_dir = project_dir, 
                                              day_num = day_num,
                                              treatment_char = treatment_char,
                                              save_target=save_target)

    def param_display(self, day_num = 1, treatment_char = "A"):

        project_dir = THE_HISTORY.get_project_dir(self.CURRENT_PROJECT)
        logger.debug(f"Current project dir: {project_dir}")
        self.parameters_frame.load_parameters(project_dir=project_dir, 
                                              day_num=day_num, 
                                              treatment_char=treatment_char)

        self.LoadedProject.configure(text=self.CURRENT_PROJECT)

        self.PREVIOUS_DAY = day_num
        logger.debug(f"Set PREVIOUS_DAY to {day_num}")
        self.PREVIOUS_TREATMENT = treatment_char
        logger.debug(f"Set PREVIOUS_TREATMENT to {treatment_char}")

    def update_param_display(self, event=None, load_type="not_first_load"):
        assert load_type in ["not_first_load", "first_load", "refresh"]

        if load_type == "first_load":
            logger.info("Loading the abitrary numbers used for initial display")

            #set TreatmentOptions to the first treatment
            self.TreatmentOptions.set(self.TREATMENTLIST[0])
            #set DayOptions to the first Day
            self.DayOptions.set(self.DAYLIST[0])

            self.param_display()
            return
        
        if load_type == "refresh":
            logger.info("Refreshing the parameters display")
            day_num = self.DayOptions.get().split()[1]
            current_treatment_char = self.get_treatment_char()

            self.param_display(day_num=day_num,
                               treatment_char=current_treatment_char)
            return
        
        self.save_parameters(mode = "previous")
        logger.debug("Saved the previous parameters")

        day_num = self.DayOptions.get().split()[1]
        logger.debug(f"Day DropDown: {self.PREVIOUS_DAY} -> {day_num}")
        
        treatment = self.TreatmentOptions.get() #OK - just for log
        logger.debug(f"treatment DropDown: {self.PREVIOUS_TREATMENT} -> {treatment}")
        # convert treatment_index to letter 1 -> A
        current_treatment_char = self.get_treatment_char()

        self.param_display(day_num = day_num, 
                           treatment_char = current_treatment_char)

    def refresh_projects_detail(self):
        
        logger.debug("Refresh projects detail")

        # Clear existing project details labels
        self.project_detail_container.clear()

        # Reload the project details
        self.project_detail_container.load_project_details(self.CURRENT_PROJECT)


    ################################################### OBJECT #########################################################    

    def add_day(self):
        logger.debug("Adding Day")
        new_Day_num = len(self.DAYLIST) + 1
        self.DAYLIST.append("Day " + str(new_Day_num))

        # Update the Day options
        self.DayOptions.configure(values=self.DAYLIST)

        # Set the Day to the last Day
        self.DayOptions.set(self.DAYLIST[-1])

        # Modify history file
        _, ErrorType = self.access_history("add", day_name=f"Day {new_Day_num}")

        if ErrorType != None:
            logger.error(ErrorType)
            tkinter.messagebox.showerror("Error", ErrorType)
            return

        # Create new Day directories and hyp files
        self.save_project(day_num = new_Day_num, subsequent_save = True)

        self.refresh()

    def remove_day(self):
        logger.debug("Removing Day")
        selected_Day = self.DayOptions.get()

        # Pop-up window to confirm deletion
        if not tkinter.messagebox.askokcancel("Delete Day", f"Are you sure you want to delete {selected_Day}?"):
            return

        # Modify history file
        _, ErrorType = self.access_history("remove", day_name=selected_Day)

        if ErrorType != None:
            logger.error(ErrorType)
            tkinter.messagebox.showerror("Error", ErrorType)
            return

        self.DAYLIST, _ = self.access_history("load Day list")

        # Update the Day options
        self.DayOptions.configure(values=self.DAYLIST)

        # Set the Day to the last Day
        self.DayOptions.set(self.DAYLIST[-1])

        # Remove the Day directories and hyp files
        self.delete_Day_dir(selected_Day)
    
    def delete_Day_dir(self, day_name):
        logger.debug("Deleting Day")

        day_num = day_name.split(" ")[1]

        project_dir = Path(THE_HISTORY.get_project_dir(self.CURRENT_PROJECT))

        # Find all directory in project_dir, at any level, that contain Day_ord, use shutil.rmtree to delete them
        Day_dir = project_dir / f"Day {day_num}"
        shutil.rmtree(Day_dir)

    ##################################################### PROJECT ############################################################    

    def create_project(self):

        logger.debug("Create project button pressed")

        self.PROJECT_CREATED = False
        ProjectsInputWindow = InputWindow(self, project_name = "", project_created=False)

        self.CURRENT_PROJECT = ProjectsInputWindow.CURRENT_PROJECT
        self.PROJECT_CREATED = ProjectsInputWindow.PROJECT_CREATED

        if self.PROJECT_CREATED:

            self.refresh_projects()
            # select the newly created project in the list
            self.scrollable_frame.select_project(self.CURRENT_PROJECT)

            self.save_project()

            self.load_project(custom_project=self.CURRENT_PROJECT)

        else:
            print("Project not created")

    def load_project(self, custom_project=None):

        logger.debug("Load project button pressed")

        if custom_project == None:
            selected_project = self.scrollable_frame.get_selected_project()
        else:
            selected_project = custom_project
            # set the current project to the custom project
            self.scrollable_frame.set_selected_project(custom_project)

        self.CURRENT_PROJECT = selected_project

        logger.info(f"Current project: {self.CURRENT_PROJECT}")

        # Update the day options
        self.DAYLIST, ErrorType = self.access_history("load day list")
        if ErrorType != None:
            tkinter.messagebox.showerror("Error", ErrorType)
            return
        
        
        self.DayOptions.configure(values=self.DAYLIST)

        retry = 0 
        while retry<3:
            try:
                self.TREATMENTLIST, ErrorType = self.access_history("load treatment list", day_name = self.DayOptions.get())
                logger.debug("Loaded treatment list")
                logger.debug(f"Possible warning: {ErrorType}")
                break
            except:
                logger.warning(f"Day {self.DayOptions.get()} does not exist in this project, try another day")
                self.DayOptions.set(self.DAYLIST[0])
                retry += 1
                logger.debug(f"Retried {retry} times")
        else:
            logger.error("Failed to load treatment list, please check the project directory")
            tkinter.messagebox.showerror("Error", "Failed to load treatment list, please check the project directory")
            return

        if ErrorType != None:
            tkinter.messagebox.showerror("Error", ErrorType)
            return
        
        #set values of TreatmentOptions
        self.TreatmentOptions.configure(values=self.TREATMENTLIST)
        #set current value to first choice
        self.TreatmentOptions.set(self.TREATMENTLIST[0])

        self.refresh_projects_detail()

        self.update_param_display(load_type = "first_load")

    def save_project(self, day_num = 1, subsequent_save = False):
        logger.info(f"Save project {self.CURRENT_PROJECT}")

        if not subsequent_save:
            save_dir = tkinter.filedialog.askdirectory()
            save_dir = Path(save_dir)
            project_dir = save_dir / self.CURRENT_PROJECT
        else:
            project_dir = Path(THE_HISTORY.get_project_dir(self.CURRENT_PROJECT))

        treatment_info, _ = self.access_history(command_type = "load treatment list", 
                                             day_name = f"Day {day_num}")

        CreateProject(project_dir, treatment_info = treatment_info, day_num = day_num)

        with open(HISTORY_PATH, "r") as file:
            projects_data = json.load(file)
        
        # save the directory of the project to the projects_data
        projects_data[self.CURRENT_PROJECT]["DIRECTORY"] = str(project_dir)

        with open(HISTORY_PATH, "w") as file:
            json.dump(projects_data, file, indent=4)

    def delete_project(self):

        # create confirmation box
        choice = tkinter.messagebox.askquestion("Delete Project", "Are you sure you want to delete this project?")
        if choice == "no":
            return

        # Get the selected project
        selected_project = self.scrollable_frame.get_selected_project()

        if selected_project == "":
            tkinter.messagebox.showerror("Error", "Please select a project")
            return

        # Delete the project from the history file
        with open(HISTORY_PATH, "r") as file:
            projects_data = json.load(file)

        # Delete the project directory
        try:
            project_dir = projects_data[selected_project]["DIRECTORY"]
            shutil.rmtree(project_dir)
            logger.info(f"Deleted project directory: {project_dir}")
        except:
            logger.debug("Project directory does not exist: , just remove from History")

        del projects_data[selected_project]

        with open(HISTORY_PATH, "w") as file:
            json.dump(projects_data, file, indent=4)

        self.CURRENT_PROJECT = ""

        logger.info("Set current project to blank")

        # Refresh the project list
        logger.debug("Refresh projects")
        self.refresh_projects()

        # Refresh the project details
        self.refresh_projects_detail()

    def refresh_projects(self):
        logger.debug("Refresh projects")

        # Clear existing project labels
        self.scrollable_frame.clear_projects()

        # Read the projects.json file and add project names to the list
        try:
            with open(HISTORY_PATH, "r") as file:
                projects_data = json.load(file)
        except:
            print("No projects found or no record of projects")
            return

        for project_name in projects_data.keys():
            self.scrollable_frame.add_project(project_name)


    def import_trajectories(self):
        logger.debug("Start importing trajectories")

        import_project_dir = tkinter.filedialog.askdirectory()
        if not import_project_dir:
            logger.debug("No directory selected")
            return
        
        importer = Importer(import_project_dir)
        importer.collect_info()

        destination_project_dir = tkinter.filedialog.askdirectory()
        if not destination_project_dir:
            logger.debug("No directory selected")
            return

        importer.update_info(destination_parent_dir = destination_project_dir)
        importer.copy_data()
        # importer.generate_static_json()

        # refresh the project list
        self.refresh_projects()

    ##################################################### CONVERTER ############################################################    

    def treatment_to_treatment_char(self, treatment):
        treatment_index = self.TREATMENTLIST.index(treatment)
        treatment_char = CHARS[treatment_index]
        return treatment_char
    
    def get_treatment_char(self, current_treatment = None):
        if current_treatment == None:
            current_treatment = self.TreatmentOptions.get()
        return self.treatment_to_treatment_char(current_treatment)
    
    def get_day_num(self):
        day_num = self.DayOptions.get().split()[1]
        return day_num
    

    ##################################################### ANALYZE ############################################################    

    def pre_analyze_check(self):
        logger.debug("Start pre-analyze check")

        if self.CURRENT_PROJECT == "":
            tkinter.messagebox.showerror("Error", "Please select a project")
            return False

        if self.DayOptions.get() == "":
            tkinter.messagebox.showerror("Error", "Please select a day")
            return False
        
        if self.TreatmentOptions.get() == "":
            tkinter.messagebox.showerror("Error", "Please select a treatment")
            return False
        
        return True

    def analyze_treatment(self, PROGRESS_WINDOW, treatment_char = None, treatment_name = None):

        if self.CURRENT_PROJECT == "":
            tkinter.messagebox.showerror("Error", "Please select a project")
            return
        
        project_dir = Path(THE_HISTORY.get_project_dir(self.CURRENT_PROJECT))

        try:
            day_num = int(self.get_day_num())
        except ValueError:
            day_num = 1

        if treatment_char == None:
            treatment_char = self.get_treatment_char()
        else:
            treatment_char = treatment_char

        logger.info(f"Start analyzing treatment: {treatment_char}")

        static_path = get_static_dir(project_dir, day_num, treatment_char)

        #######################################################################

        EXECUTOR = Executor(project_dir=project_dir, 
                            day_num = day_num, 
                            treatment_char=treatment_char, 
                            treatment_name=treatment_name,
                            EndPointsAnalyze=self.EPA,
                            progress_window=PROGRESS_WINDOW)
        
        #######################################################################
        PROGRESS_WINDOW.lift()
        PROGRESS_WINDOW.step_update(0, text = "Loading parameters...")
        
        while True:
            ERROR = EXECUTOR.PARAMS_LOADING()
            if ERROR == None:
                logger.debug("Parameters loaded successfully")
                break
            else:
                tkinter.messagebox.showerror("ERROR", ERROR)
                logger.error(ERROR)
                PROGRESS_WINDOW.destroy()
                return
            
        time.sleep(1)
        #######################################################################

        PROGRESS_WINDOW.lift()
        PROGRESS_WINDOW.step_update(20, text = "Loading parameters...")
        
        while True:
            ERROR = EXECUTOR.GROUP_LOADING()
            if ERROR == None:
                logger.debug("Group loaded successfully")
                break
            else:
                tkinter.messagebox.showerror("ERROR", ERROR)
                logger.error(ERROR)
                PROGRESS_WINDOW.destroy()
                return
            
        time.sleep(1)
        #######################################################################

        PROGRESS_WINDOW.step_update(40, text = "Analyzing...")
        # Lift the window to the front

        OVERWRITE = False
        while True:
            PROGRESS_WINDOW.lift()
            REPORT, EPA_path = EXECUTOR.ENDPOINTS_ANALYSIS(OVERWRITE=OVERWRITE, AV_interval=30)
            if REPORT == "Completed":
                logger.debug("Analysis completed successfully")
                break
            elif REPORT == "Existed":
                choice = tkinter.messagebox.askyesno("Error",  f"Sheet name {treatment_char} existed.\nDo you want to overwrite? Y/N?")
                if choice:
                    logger.debug("User chose to overwrite")
                    OVERWRITE = True
                else:
                    logger.debug("User chose not to overwrite")
                    return EPA_path, static_path
            elif REPORT == "Skip":
                _message = f"Skip analysis of {treatment_char}"
                tkinter.messagebox.showinfo(REPORT, _message)
                logger.debug(_message)
                return EPA_path, static_path
            elif REPORT == "Error":
                tkinter.messagebox.showerror(REPORT, f"Error during analysis of {treatment_char}")
                logger.error(f"Error during analysis of {treatment_char}")
                return None, None
            
        PROGRESS_WINDOW.step_update(100, text = "Completed")

        #######################################################################

        return EPA_path, static_path

    def analyze_project(self):

        PROGRESS_WINDOW = ProgressWindow(self)

        time00 = time.time()
        time0 = time.time()

        time_for_treatment = {}

        CHAR_TREATMENT_DICT = {self.treatment_to_treatment_char(treatment): treatment for treatment in self.TREATMENTLIST}
        # TREATMENT_LIST_CHAR = [self.treatment_to_treatment_char(treatment) for treatment in self.TREATMENTLIST]

        # for i, treatment_char in enumerate(TREATMENT_LIST_CHAR):
        i = 0
        for treatment_char, treatment_name in CHAR_TREATMENT_DICT.items():

            # _message = f"Analyzing treatment {treatment_char}"
            # _progress = (i+1) / len(TREATMENT_LIST_CHAR) * 100
            _message = f"Analyzing {treatment_name}"
            _progress = (i+1) / len(CHAR_TREATMENT_DICT) * 100
            PROGRESS_WINDOW.group_update(_progress, text = _message)
            logger.info(_message)
            EPA_path, static_path = self.analyze_treatment(PROGRESS_WINDOW, 
                                                           treatment_char=treatment_char, 
                                                           treatment_name=treatment_name)

            i+= 1
            
            if EPA_path == None and static_path == None:
                PROGRESS_WINDOW.destroy()
                return

            time_for_treatment[treatment_char] = time.time() - time0
            time0 = time.time()

        # Destroy the progress window
        logger.debug("Destroying the progress window")
        PROGRESS_WINDOW.destroy()

        _message = f"Time taken: {round(time.time() - time00, 2)} seconds"
        _message += f"\nTime taken for each treatment:"
        # for treatment_char in TREATMENT_LIST_CHAR:
        for treatment_char, treatment_name in CHAR_TREATMENT_DICT.items():
            _message += f"\n  {treatment_name}: {round(time_for_treatment[treatment_char], 2)} seconds"
        tkinter.messagebox.showinfo("Completion time", _message)


        logger.debug("EPA_path is not None")
        if EPA_path.exists():
            logger.debug("EPA_path exists")
            open_path = EPA_path.parent
            _ = CustomDialog(self, title = "Analysis Complete",
                                message =  "Click GO button to go to the saved directory of EndPoints.xlsx", 
                                button_text = "GO",
                                button_command = lambda : open_explorer(path=open_path))
            logger.info("Analysis complete")
        else:
            logger.debug("EPA_path does not exist")
            message = "Something went wrong during the analysis, no exported EndPoints.xlsx found"
            tkinter.messagebox.showerror("Error", message)
            logger.info(message)


    def analyze_project_THREADED(self):
        logger.debug("Open a new thread to analyze project")

        # save the current parameters
        self.save_parameters(mode='current')

        self.EPA = True        

        analyze_thread = threading.Thread(target=self.analyze_project)
        analyze_thread.start()


    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        logger.debug(f"New UI appearance mode: {new_appearance_mode}")

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        logger.debug(f"New UI scaling: {new_scaling_float}")
        customtkinter.set_widget_scaling(new_scaling_float)
    
    def close_app(self):
        self.quit()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
