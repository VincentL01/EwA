import tkinter
import tkinter.ttk as ttk
import customtkinter
import json
import os
import shutil
import re
from pathlib import Path

from . import HISTORY_PATH, PARAMS_FILE_NAME
from . import DEFAULT_PARAMS, PARAMS_UNITS
from Libs.dirFetch import get_static_dir
from Libs.misc import index_to_char, to_int_or_float

import logging
logger = logging.getLogger(__name__)

########################################### DISPLAY CLASSES ###########################################

class ProgressWindow(tkinter.Toplevel):
        
    def __init__(self, master, title="Analysis Progress", geometry="300x250"):
        tkinter.Toplevel.__init__(self, master)
        self.title(title)
        self.geometry(geometry)

        FONT = ('Helvetica', 14, 'bold')

        self.group_label = tkinter.Label(self, text="Group Progress", font=FONT)
        self.group_label.pack(pady=5)
        self.group = ttk.Progressbar(self, length=100, mode='determinate')
        self.group.pack(pady=5)

        self.step_label = tkinter.Label(self, text="Step Progress", font=FONT)
        self.step_label.pack(pady=5)
        self.step = ttk.Progressbar(self, length=100, mode='determinate')
        self.step.pack(pady=5)

        self.task_label = tkinter.Label(self, text="Task Progress", font=FONT)
        self.task_label.pack(pady=5)
        self.task = ttk.Progressbar(self, length=100, mode='determinate')
        self.task.pack(pady=5)

    def group_update(self, value, text="Group Progress"):
        self.group_label["text"] = text
        self.group["value"] = value
        self.update()

    def step_update(self, value, text="Step Progress"):
        self.step_label["text"] = text
        self.step["value"] = value
        self.update()

    def task_update(self, value, text="Task Progress"):
        self.task_label["text"] = text
        self.task["value"] = value
        self.update()

class CustomDialog(tkinter.Toplevel):
    def __init__(self, master, title=None, message=None, button_text=None, button_command=None):
        tkinter.Toplevel.__init__(self, master)
        self.title(title)

        FONT=('Helvetica', 14, 'bold')

        self.label = tkinter.Label(self, text=message, font=FONT)
        self.label.pack(padx=10, pady=10)

        self.button_command = button_command
        self.button = tkinter.Button(self, text=button_text, command=self.ok)
        self.button.pack(pady=10)

        self.geometry("+%d+%d" % (master.winfo_rootx(), master.winfo_rooty()))

    def ok(self):
        if self.button_command is not None:
            self.button_command()
        self.destroy()

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tkinter.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tkinter.Label(tw, text=self.text, justify=tkinter.LEFT,
                      background="#ffffe0", relief=tkinter.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)



########################################### CORE CLASSES ###########################################

class HISTORY():

    def __init__(self, history_path = HISTORY_PATH):
        self.history_path = history_path

        with open(HISTORY_PATH, "r") as file:
            self.projects_data = json.load(file)


    def reload(self):
        with open(HISTORY_PATH, "r") as file:
            self.projects_data = json.load(file)


    def find_dir(self, project_name):
        logger.debug("find_dir called")
        tkinter.messagebox.showerror("Error", "Project directory does not exist!")
        logger.info(f"Project directory of {project_name} does not exist. Asking for relocation")
        relocate = tkinter.messagebox.askyesno("Project not found", "Do you want to relocate it?")
        if relocate:
            # ask for new input of project_dir
            destination_parent_dir = tkinter.filedialog.askdirectory()
            
            self.projects_data[project_name]["DIRECTORY"] = destination_parent_dir
            self.saver()
            logger.info(f"Project directory of {project_name} has been relocated to {destination_parent_dir}")

            return destination_parent_dir
        else:
            return None

    def get_project_dir(self, project_name):
        self.reload()

        if project_name == "":
            logger.warning("Tried to get project directory of an empty project name")
            return None
        try:
            logger.debug("Trying to get project directory from history file")
            project_dir = self.projects_data[project_name]["DIRECTORY"]
        except KeyError:
            logger.warning(f"Project name {project_name} not found in history file")
            project_dir = self.find_dir(project_name)

        # check if the project directory exists
        if not os.path.exists(project_dir):
            logger.warning("Project directory does not exist, asking for relocation")
            project_dir = self.find_dir(project_name)

        return project_dir       
     

    def add_treatment(self, project_name, day_name, treatment_char, substance, dose, dose_unit, note=""):

        if project_name == "":
            logger.warning("Tried to add treatment to an empty project name")
            return

        if substance == "":
            logger.warning("Tried to add treatment with empty treatment name")
            return

        if day_name == "":
            logger.warning("Tried to add treatment with empty day name")
            return

        if project_name not in self.projects_data:
            logger.warning(f"Project name {project_name} not found in history file")
            return

        if day_name not in self.projects_data[project_name]:
            logger.warning(f"Day name {day_name} not found in history file")
            return

        if f"Treatment {treatment_char}" in self.projects_data[project_name][day_name]:
            logger.warning(f"Treatment {treatment_char} already exists in history file")
            choice = tkinter.messagebox.askyesno("Treatment already exists", "Do you want to overwrite it?")
            if choice:
                pass
            else:
                return
            
        self.projects_data[project_name][day_name][f"Treatment {treatment_char}"] = [substance, dose, dose_unit, note]

        self.saver()


    def saver(self):
        with open(self.history_path, "w") as file:
            json.dump(self.projects_data, file, indent=4)



class ScrollableProjectList(customtkinter.CTkScrollableFrame):

    def __init__(self, master, command=None, **kwargs):

        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.project_variable = customtkinter.StringVar()
        self.project_radiobuttons = []

    def add_project(self, project_name):
        project_radiobutton = customtkinter.CTkRadioButton(
            self, text=project_name, value=project_name, variable=self.project_variable
        )
        project_radiobutton.grid(row=len(self.project_radiobuttons), column=0, pady=(0, 10), sticky="w")
        self.project_radiobuttons.append(project_radiobutton)

    def clear_projects(self):
        for radiobutton in self.project_radiobuttons:
            radiobutton.destroy()
        self.project_radiobuttons = []

    def get_selected_project(self):
        return self.project_variable.get()

    def set_selected_project(self, project_name="last"):
        if project_name == "last":
            # set to the last project in list
            self.project_variable.set(self.project_radiobuttons[-1].cget("text"))
            logger.warning("Set project variable failed, set to the last project in list")
        else:
            self.project_variable.set(project_name)
            logger.debug("Set project variable to " + project_name)
    
    def select_project(self, project_name):
        for radiobutton in self.project_radiobuttons:
            if radiobutton.cget("text") == project_name:
                radiobutton.invoke()
                break

    def return_recent_project(self):
        return self.project_radiobuttons[-1].cget("text")
    

class InputWindow(tkinter.Toplevel):

    def __init__(self, master, project_name, project_created=False, **kwargs):
        super().__init__(master, **kwargs)

        logger.info("Project input window opened")


        # set window size
        self.geometry("460x500")

        self.title("Project Input")

        self.CURRENT_PROJECT = project_name
        self.PROJECT_CREATED = project_created
        self.day_name = "Day 1"
        self.BOLD_FONT = customtkinter.CTkFont(size = 15, weight="bold")

        self.TOTAL_INFO = {}

        self.treatment_widgets = []

        self.rowconfigure(0, weight=1)
        # Top Canvas
        self.top_canvas = customtkinter.CTkScrollableFrame(self, width = 440)
        # expand the canvas to fill the window
        self.top_canvas.grid(row=0, column=0, sticky="nsew")

        self.ROW=0
        # Project name
        project_name_label = customtkinter.CTkLabel(self.top_canvas, text="Project name:", font=self.BOLD_FONT)
        project_name_label.grid(row=self.ROW, column=0, pady=5)
        self.project_name_entry = customtkinter.CTkEntry(self.top_canvas)
        self.project_name_entry.grid(row=self.ROW, column=1, pady=5)

        self.DoseToggler = customtkinter.CTkCheckBox(self.top_canvas, text="Have Dose", command=self.toggle_dose)
        self.DoseToggler.grid(row=self.ROW, column=2, pady=5)
        self.DoseToggler.select()


        self.ROW+=1
        # Common substance
        common_substance_label = customtkinter.CTkLabel(self.top_canvas, text="Common substance:", font=self.BOLD_FONT)
        common_substance_label.grid(row=self.ROW, column=0, pady=5)
        self.common_substance_entry = customtkinter.CTkEntry(self.top_canvas)
        self.common_substance_entry.grid(row=self.ROW, column=1, pady=5)

        hover_button = tkinter.Button(self.top_canvas, text="?")
        hover_button.grid(row=self.ROW, column=2, pady=5)
        CreateToolTip(hover_button, text = 'Common condition in all group\n'
                    'Can be left blank\n'
                    'The info you put here would be saved as Note\n'
                    'Group A is default as Control, you can change at your own will'
        )


        self.ROW+=1
        # Treatment A (Control)
        treatment_a_label = customtkinter.CTkLabel(self.top_canvas, text="Group A:", font=self.BOLD_FONT)
        treatment_a_label.grid(row=self.ROW, column=0, pady=5)
        self.treatment_a_entry = customtkinter.CTkEntry(self.top_canvas)
        self.treatment_a_entry.grid(row=self.ROW, column=1, pady=5)
        self.treatment_a_entry.insert(0, "Control")

        self.ROW+=1
        # Dose
        dose_label = customtkinter.CTkLabel(self.top_canvas, text="Dose:")
        dose_label.grid(row=self.ROW, column=0, pady=5)
        self.dose_a_entry = customtkinter.CTkEntry(self.top_canvas)
        self.dose_a_entry.grid(row=self.ROW, column=1, pady=5)
        self.unit_a_optionmenu = customtkinter.CTkOptionMenu(self.top_canvas, values=["ppm", "ppb"])
        self.unit_a_optionmenu.grid(row=self.ROW, column=2, pady=5)


        # self.ROW+=1
        # Fish number
        # fish_number_a_label = customtkinter.CTkLabel(self.top_canvas, text="Fish Number:")
        # fish_number_a_label.grid(row=self.ROW, column=0, pady=5)
        # self.fish_number_a_entry = customtkinter.CTkEntry(self.top_canvas)
        # self.fish_number_a_entry.grid(row=self.ROW, column=1, pady=5)
        
        self.ROW+=1
        # Treatment B
        treatment_b_label = customtkinter.CTkLabel(self.top_canvas, text="Group B:", font=self.BOLD_FONT)
        treatment_b_label.grid(row=self.ROW, column=0, pady=(20, 5))
        self.treatment_b_entry = customtkinter.CTkEntry(self.top_canvas)
        self.treatment_b_entry.grid(row=self.ROW, column=1, pady=(20, 5))

        self.ROW+=1
        # Dose
        dose_label = customtkinter.CTkLabel(self.top_canvas, text="Dose:")
        dose_label.grid(row=self.ROW, column=0, pady=5)
        self.dose_b_entry = customtkinter.CTkEntry(self.top_canvas)
        self.dose_b_entry.grid(row=self.ROW, column=1, pady=5)
        self.unit_b_optionmenu = customtkinter.CTkOptionMenu(self.top_canvas, values=["ppm", "ppb"])
        self.unit_b_optionmenu.grid(row=self.ROW, column=2, pady=5)

        # self.ROW+=1
        # Fish number
        # fish_number_b_label = customtkinter.CTkLabel(self.top_canvas, text="Fish Number:")
        # fish_number_b_label.grid(row=self.ROW, column=0, pady=5)
        # self.fish_number_b_entry = customtkinter.CTkEntry(self.top_canvas)
        # self.fish_number_b_entry.grid(row=self.ROW, column=1, pady=5)

        # Bottom Canvas
        bottom_canvas = customtkinter.CTkFrame(self)
        bottom_canvas.grid(row=1, column=0, sticky="nsew")

        # Add button
        add_button = customtkinter.CTkButton(bottom_canvas, text="Add Group", 
                                                font = self.BOLD_FONT, 
                                                command=self.add_treatment)
        add_button.grid(row=0, column=0, padx=5, pady=20)

        # Confirm button
        confirm_button = customtkinter.CTkButton(bottom_canvas, text="CONFIRM", 
                                                    font = self.BOLD_FONT,
                                                    command=self.get_values)
        confirm_button.grid(row=1, column=0, padx=5, pady=20)

        # Cancel button
        cancel_button = customtkinter.CTkButton(bottom_canvas, text="CANCEL", 
                                                font = self.BOLD_FONT,
                                                command=self.cancel_button_command)
        cancel_button.grid(row=1, column=1, padx=5, pady=20)

        self.wait_window()


    def toggle_dose(self):

        if self.DoseToggler.get() == 1:
            self.dose_a_entry.configure(state="normal")
            self.unit_a_optionmenu.configure(state="normal")
            self.dose_b_entry.configure(state="normal")
            self.unit_b_optionmenu.configure(state="normal")
            for widget in self.treatment_widgets:
                widget[1].configure(state="normal")
                widget[2].configure(state="normal")
        else:
            self.dose_a_entry.configure(state="disabled")
            self.unit_a_optionmenu.configure(state="disabled")
            self.dose_b_entry.configure(state="disabled")
            self.unit_b_optionmenu.configure(state="disabled")
            for widget in self.treatment_widgets:
                widget[1].configure(state="disabled")
                widget[2].configure(state="disabled")

    
    def get_dose_value(self, dose_entry, unit_entry):
        try:
            dose = float(dose_entry.get())
            unit = unit_entry.get()
        except ValueError:
            dose = ""      
            unit = ""  
        return dose, unit


    def add_treatment(self):
        logger.debug("Add treatment button clicked")

        treatment_row = len(self.treatment_widgets)*3 + self.ROW + 1
        treatment_name = f"Group {chr(ord('C') + len(self.treatment_widgets))}:"

        treatment_label = customtkinter.CTkLabel(self.top_canvas, text=treatment_name, font=self.BOLD_FONT)
        treatment_label.grid(row=treatment_row, column=0, pady=(20, 5))
        treatment_entry = customtkinter.CTkEntry(self.top_canvas)
        treatment_entry.grid(row=treatment_row, column=1, pady=(20, 5))

        dose_label = customtkinter.CTkLabel(self.top_canvas, text="Dose:")
        dose_label.grid(row=treatment_row + 1, column=0, pady=5)
        dose_entry = customtkinter.CTkEntry(self.top_canvas)
        dose_entry.grid(row=treatment_row + 1, column=1, pady=5)
        unit_optionmenu = customtkinter.CTkOptionMenu(self.top_canvas, values=["ppm", "ppb"])
        unit_optionmenu.grid(row=treatment_row + 1, column=2, pady=5)

        # fish_number_label = customtkinter.CTkLabel(self.top_canvas, text="Fish Number:")
        # fish_number_label.grid(row=treatment_row + 2, column=0, pady=5)
        # fish_number_entry = customtkinter.CTkEntry(self.top_canvas)
        # fish_number_entry.grid(row=treatment_row + 2, column=1, pady=5)

        self.treatment_widgets.append((treatment_entry, 
                                       dose_entry, 
                                       unit_optionmenu, 
                                    #    fish_number_entry
                                       ))


    def get_values(self):
        project_name = self.project_name_entry.get()
        self.CURRENT_PROJECT = project_name
        try:
            note = self.common_substance_entry.get()
        except:
            note = ""
        a_dose, a_unit = self.get_dose_value(self.dose_a_entry, self.unit_a_optionmenu)
        b_dose, b_unit = self.get_dose_value(self.dose_b_entry, self.unit_b_optionmenu)
        try:
            treatment_list = {
                "Treatment A": [
                    self.treatment_a_entry.get(),
                    a_dose,
                    a_unit,
                    # int(self.fish_number_a_entry.get()),
                    note
                ],
                "Treatment B": [
                    self.treatment_b_entry.get(),
                    b_dose,
                    b_unit,
                    # int(self.fish_number_b_entry.get()),
                    note
                ]
            }
        except Exception as e:
            #show message box of error
            print(e)
            tkinter.messagebox.showerror("Error", "Please fill the required fields with right type of value")

        for i, (treatment_entry, 
                dose_entry, 
                unit_optionmenu, 
                # fish_number_entry
                ) in enumerate(self.treatment_widgets):
            treatment_name = f"Treatment {chr(ord('C') + i)}"
            dose, unit = self.get_dose_value(dose_entry, unit_optionmenu)
            treatment_list[treatment_name] = [
                treatment_entry.get(),
                dose,
                unit,
                # int(fish_number_entry.get()),
                note
            ]

        # Save values to projects.json
        project_data = {
            project_name: {
                self.day_name : treatment_list
                }
            }

        try:
            with open(HISTORY_PATH, "r") as file:
                existing_data = json.load(file)
            if project_name in existing_data:
                # Display message box of error
                tkinter.messagebox.showerror("Error", "Project already exists")
            else:
                existing_data.update(project_data)
                self.PROJECT_CREATED = True
                with open(HISTORY_PATH, "w") as file:
                    json.dump(existing_data, file, indent=2)
                self.destroy()  # Move this line inside the else block
        except:
            existing_data = project_data
            self.PROJECT_CREATED = True
            with open(HISTORY_PATH, "w") as file:
                json.dump(existing_data, file, indent=2)
            self.destroy()  # Move this line inside the except block


    def cancel_button_command(self):
        logger.debug("Cancel button clicked")

        self.PROJECT_CREATED = False
        self.destroy()

    def status(self):

        return self.CURRENT_PROJECT, self.PROJECT_CREATED
    
class ProjectDetailFrame(customtkinter.CTkScrollableFrame):

    def __init__(self, master, project_name, **kwargs):

        super().__init__(master, **kwargs)

        # # Create tree view
        # self.tree = ttkinter.Treeview(self, height = 5, show = "headings")
        # self.tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        

        # If project name is not empty, load the project details, 
        # otherwise, display "No project selected"
        self.project_name = project_name
        if self.project_name != "":
            self.load_project_details()
        else:
            label = customtkinter.CTkLabel(self, text="No project selected")
            label.grid(row=0, column=0, padx=5, pady=5)

    def update_grid_weight(self):
        rows, cols = self.grid_size()

        for row in range(rows):
            self.grid_rowconfigure(row, weight=1)

        for col in range(cols):
            self.grid_columnconfigure(col, weight=1)

    def load_project_details(self, project_name=None, day_name="Day 1"):

        logger.info(f"Loading.. project name = {project_name}")

        if project_name == "":
            label = customtkinter.CTkLabel(self, text="No project selected")
            label.grid(row=0, column=0, padx=5, pady=5)
            return

        if project_name is not None:
            self.project_name = project_name

        with open(HISTORY_PATH, "r") as file:
            projects_data = json.load(file)

        project_data = projects_data[self.project_name][day_name]

        logger.info(project_data)

        headers = ["Treatment", 
                   "Dose", 
                   "Dose Unit", 
                #    "Fish Number", 
                   "Note"
                   ]

        for i, header in enumerate(headers):
            label = customtkinter.CTkLabel(self, text=header, font=customtkinter.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=5, pady=5)

        for row, (treatment, details) in enumerate(project_data.items(), start=1):
            # treatment_name, dose, dose_unit, fish_number, note = details
            treatment_name, dose, dose_unit, note = details

            dose = dose if dose != 0 else ""
            dose_unit = dose_unit if dose_unit != "" else ""
            # fish_number = fish_number if fish_number != 0 else ""

            labels = [treatment_name, 
                      dose, 
                      dose_unit, 
                    #   fish_number, 
                      note]

            for col, label_text in enumerate(labels):
                label = customtkinter.CTkLabel(self, text=label_text)
                label.grid(row=row, column=col, padx=5, pady=5)

        self.update_grid_weight()

    def clear(self):
        for child in self.winfo_children():
            child.destroy()


class Parameters(customtkinter.CTkScrollableFrame):

    def __init__(self, master, project_dir=None, nested_mode=None, *args, **kwargs):
        
        super().__init__(master, *args, **kwargs)

        self.project_dir = project_dir
        if self.project_dir == None:
            self.project_dir = ""
            self.project_name = ""
        else:
            self.project_name = Path(self.project_dir).name

        # if project_dir == None or project_dir == "":
        #     self.project_dir = TEMPLATE_PATH
        # else:
        #     self.project_dir = project_dir
            
        # self.project_name = Path(self.project_dir).name

        self.null_label = None
        self.hyp_name = PARAMS_FILE_NAME
        self.UNITS = PARAMS_UNITS

        self.null_label_check()

        if self.project_name == "":
            self.null_label = customtkinter.CTkLabel(self, text="No project selected")
            self.null_label.grid(row=0, column=0, padx=5, pady=5)
        else:
            self.load_parameters(nested_mode = nested_mode)

        self.entries = {}


    def null_label_check(self):
        logger.debug(f"{self.null_label=}")
        if self.null_label == None:
            # Destroy null_label_notif if it exists
            logger.debug("Destroying null_label_notif")
            try:
                self.null_label_notif.destroy()
            except:
                pass
            return
        
        self.null_label_notif = customtkinter.CTkLabel(self, text="No parameters found, \nPress Load Project again to open Measurer window")
        self.null_label_notif.grid(row=0, column=0, padx=5, pady=5)

        
    def get_hyp_path(self, project_dir, day_num, treatment_char):

        static_dir = get_static_dir(project_dir=project_dir,
                                    day_num=day_num,
                                    treatment_char=treatment_char)
        
        hyp_path = static_dir / self.hyp_name

        logger.debug(f"Retrieved hyp from {hyp_path}")

        return hyp_path
        
    
    def get_current_entry_quantity(self):

        last_row = list(self.entries.keys())[-1]
        last_entry = self.entries[last_row]

        try:
            last_row_num = int(last_row.split('_')[-1])
            return last_row_num
        except:
            return 0
        

    def load_parameters(self, project_dir=None, day_num=1, treatment_char="A", nested_mode=0):

        if project_dir == None:
            project_dir = self.project_dir
            project_name = self.project_name
        else:
            project_name = Path(project_dir).name

        logger.debug(f"Loading parameters for project_name = {project_name}, day_num = {day_num}, treatment = {treatment_char}")

        self.null_label = None

        self.entries = {}

        self.clear()

        if project_dir == "" or project_dir == None:
            ori_dict = DEFAULT_PARAMS
        else:
            self.hyp_path = self.get_hyp_path(project_dir, day_num, treatment_char)

            try:
                logger.debug("Trying to load parameters from json file")
                with open(self.hyp_path, "r") as file:
                    ori_dict = json.load(file)

            except:
                logger.debug("Unable to load parameters from json file")
                logger.debug("Set parameters as default")
                ori_dict = DEFAULT_PARAMS

        # find the nested keys
        nested_keys = []
        for key, value in ori_dict.items():
            if isinstance(value, dict):
                nested_keys.append(key)


        nested_key = nested_mode
        if nested_mode == 0:
            display_dict = {k: v for k, v in ori_dict.items() if not isinstance(v, (dict, list))}
            headers = ["Parameter", "Value", "Unit"]
        else:
            try:
                nested_key = nested_keys[nested_mode-1]
            except IndexError:
                self.null_label = customtkinter.CTkLabel(self, text="No more nested keys")
                self.null_label.grid(row=0, column=0, padx=5, pady=5) 
                return "None"
            
            display_dict = ori_dict[nested_key]

            example_value = list(display_dict.values())[0]
            if not isinstance(example_value, dict):
                logger.error(f"Nested key {nested_key} is not a dict")
                raise ValueError(f"Nested key {nested_key} is not a dict")
            headers = ["Well"]
            for header in example_value.keys():
                headers.append(header)

        # if not nested key, meaning Global Params -> need unit labels
        example_key = list(display_dict.keys())[0]
        try:
            _ = int(example_key)
            pass
        except ValueError:
            units = [self.UNITS[k] for k in display_dict.keys()]
            for i, unit in enumerate(units):
                unit_label = customtkinter.CTkLabel(self, text=unit)
                unit_label.grid(row=i+1, column=2, padx=(5,10), pady=5)


        self.key_labels = {}
        for row, (key, value) in enumerate(display_dict.items()):
            self.key_labels[key] = customtkinter.CTkLabel(self, text=key)
            self.key_labels[key].grid(row=row+1, column=0, padx=5, pady=5)

            if isinstance(value, dict):
                entry_key = f"{nested_key}_{key}"
                self.entries[entry_key] = []

                param_value_column = 1
                nested_entry_width = 120//len(value)
                for header, param_value in value.items():
                    value_entry = customtkinter.CTkEntry(self, width=nested_entry_width)
                    value_entry.insert(0, param_value)
                    value_entry.grid(row=row+1, column=param_value_column, padx=5, pady=5)
                    param_value_column += 1

                    self.entries[f"{nested_key}_{key}"].append(value_entry)
                    logger.debug(f"Added {header} to self.entries[{nested_key}_{key}]")
            else:
                entry_key = key

                value_entry = customtkinter.CTkEntry(self)
                value_entry.insert(0, value)
                value_entry.grid(row=row+1, column=1, padx=5, pady=5)

                self.entries[entry_key] = value_entry
                logger.debug(f"Added {entry_key} to self.entries")
                
            # make a header
            for i, header in enumerate(headers):
                label = customtkinter.CTkLabel(self, text=header, font=customtkinter.CTkFont(weight="bold"))
                label.grid(row=0, column=i, padx=5, pady=5)

        return nested_key
        # display_dict = {k: v for k, v in ori_dict.items() if not isinstance(v, (dict, list))}
        # headers = ["Parameter", "Value", "Unit"]
        
        # example_key = list(display_dict.keys())[0]
        # units = [self.UNITS[k] for k in display_dict.keys()]
        # for i, unit in enumerate(units):
        #     unit_label = customtkinter.CTkLabel(self, text=unit)
        #     unit_label.grid(row=i+1, column=2, padx=(5,10), pady=5)

        # self.key_labels = {}

        # for row, (key, value) in enumerate(display_dict.items()):
        #     self.key_labels[key] = customtkinter.CTkLabel(self, text=key)
        #     self.key_labels[key].grid(row=row+1, column=0, padx=5, pady=5)

        #     value_entry = customtkinter.CTkEntry(self)
        #     value_entry.insert(0, value)
        #     value_entry.grid(row=row+1, column=1, padx=5, pady=5)

        #     entry_key = key

        #     self.entries[entry_key] = value_entry

        # # make a header
        #     for i, header in enumerate(headers):
        #         label = customtkinter.CTkLabel(self, text=header, font=customtkinter.CTkFont(weight="bold"))
        #         label.grid(row=0, column=i, padx=5, pady=5)


    def clear(self):
        for child in self.winfo_children():
            child.destroy()

    def save_parameters(self, project_dir, day_num, treatment_char, save_target="self", nested_mode=0):
        logger.debug(f"Saving parameters for {Path(project_dir).name}.Day {day_num}.Treatment {treatment_char}, save_target = {save_target}")

        def get_entry(entry_dict):
            out_dict = {}
            for key, value in entry_dict.items():
                logger.debug(f"Processing {key=}, {value=}")
                try:
                    if isinstance(value, list):
                        v = [float(entry.get()) for entry in value]
                        logger.debug(f"{value=} is list, we have {v=}")
                        value_type = "list"
                    else:
                        v = to_int_or_float(value.get())
                        value_type = "number"
                except AttributeError:
                    logger.warning(f"During saving parameters for {Path(project_dir).name}.Day {day_num}.Treatment {treatment_char}")
                    logger.warning(f"AttributeError: {key} is not a tkinter entry")
                    logger.warning(f"Value: ", v)
                    logger.warning(f"Value type: ", type(v))
                    continue
                out_dict[key] = (v, value_type)
            return out_dict
        
        if project_dir == "":
            tkinter.messagebox.showerror("Warning", "No project selected. No save was made.")
            return 
        else:
            self.hyp_path = self.get_hyp_path(project_dir, day_num, treatment_char)

        # Get the values from the entries
        updated_values = get_entry(self.entries)
        logger.debug(f"{updated_values=}")
        
        # load the original data
        try:
            with open(self.hyp_path, "r") as file:
                parameters_data = json.load(file)
        except:
            parameters_data = DEFAULT_PARAMS

        #separate the updated_values.items into 2 groups
        updated_values_simple = {key: updated_value[0] for key, updated_value in updated_values.items() if updated_value[1] == "number"}
        updated_values_nested = {key: updated_value[0] for key, updated_value in updated_values.items() if updated_value[1] == "list"}
        logger.debug(f"{updated_values_simple=}")
        logger.debug(f"{updated_values_nested=}")

        # Update the values in Global Parameters
        if nested_mode == 0:
            for key, value in updated_values_simple.items():
                try:
                    parameters_data[key] = value
                except ValueError:
                    _message = f"Invalid input for {key}: {value}, unable to save params of Day {day_num}. Treatment {treatment_char}"
                    logger.error(_message)
                    tkinter.messagebox.showerror("Warning", _message)
                    return
        else:
            # Update the values in Well-specific Parameters
            updated_values_nested_grouped = {}
            for key, value in updated_values_nested.items():
                # Convert values in value
                value = [to_int_or_float(v) for v in value]
                try:
                    nested_key, nested_key_well = key.split("_")
                except Exception as e:
                    logger.error(f"Invalid key {key} in {self.hyp_path}")
                    logger.critical(e)
                    raise e
                #e.g., with key = Center_1, nested_key = Center, nested_key_well = 1

                try:
                    nested_key_SubKeys = list(parameters_data[nested_key]["1"].keys()) 
                except:
                    nested_key_SubKeys = list(DEFAULT_PARAMS[nested_key]["1"].keys())
                logger.debug(f"{nested_key_SubKeys=}")
                #e.g,. with nested_key = Center, "1": {"X": 123, "Y": 45} ->  nested_key_SubKeys = ["X", "Y"]

                if nested_key not in updated_values_nested_grouped:
                    updated_values_nested_grouped[nested_key] = {}
                    # "Center": {}
                if nested_key_well not in updated_values_nested_grouped[nested_key]:
                    updated_values_nested_grouped[nested_key][nested_key_well] = {}
                    # "Center": {"1": {}}
                for i, SubKey in enumerate(nested_key_SubKeys):
                    #e.g., value = [321, 54], with SubKeys = ["X", "Y"], SubKey = "X", i = 0 -> updated value for "X" = value[0]
                    updated_values_nested_grouped[nested_key][nested_key_well][SubKey] = value[i]
                    # "Center": {"1": {"X": 321, "Y": 54}}
                logger.debug(f"{updated_values_nested_grouped=}")
        
            for nested_key, well_info in updated_values_nested_grouped.items():
                if nested_key not in parameters_data:
                    logger.error(f"Nested key {nested_key} not found in {self.hyp_path}")
                    raise ValueError(f"Nested key {nested_key} not found in {self.hyp_path}")
                parameters_data[nested_key] = well_info
                logger.debug(f"Assigned {well_info} to {nested_key} in parameters_data")

        # Save the updated data to the file
        logger.debug(f"Saving parameters_data to {self.hyp_path}")
        with open(self.hyp_path, "w") as file:
            json.dump(parameters_data, file, indent=4)
        logger.debug(f"Dumped {parameters_data} to {self.hyp_path}")


        # code for the CLONE function, when user want to duplicate the parameters to other treatments
        
        if save_target != "self":
            for target_char in save_target:
                target_hyp_path = self.get_hyp_path(project_dir, day_num, target_char)
                # Dump data to target_hyp_path
                with open(target_hyp_path, "w") as file:
                    json.dump(parameters_data, file, indent=4)
                    logger.debug(f"Parameters from {treatment_char} saved to {target_char}.")
                
                logger.debug(f"Essential coords from {treatment_char} saved to {target_char}.")


################################################# IMPORTER ##################################################

# def substance_dose_unit_finder(given_string):

#     parts = given_string.split()

#     if len(parts) == 1:
#         return given_string, "", ""
#     elif len(parts) >= 2:
#         substance = ""
#         dose = ""
#         unit = ""
#         for part in parts:
#             if re.search('[0-9]', part) and re.search('[a-zA-Z]', part):
#                 unit = re.findall("[a-zA-Z]+", part)[0]
#                 dose = part.replace(unit, "")
#             else:
#                 substance += part + " "
#         return substance.strip(), dose, unit

def substance_dose_unit_finder(given_string):
    # Define a regular expression pattern to match the desired format
    pattern = r'(\D+) (\d+(?:\.\d+)?)\s*(\w*)'

    # Use re.match to find the first match in the string
    match = re.match(pattern, given_string)

    if match:
        # Extract the matched groups
        substance = match.group(1)
        dose = match.group(2)
        unit = match.group(3)

        # Return the extracted values as a list
        return [substance, dose, unit]
    else:
        # If no match is found, return empty strings for dose and unit
        return [given_string, "", ""]
    
class Importer():

    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.project_name = self.source_dir.name
        logger.info(f"Found project {self.project_name} at {self.source_dir}")

        self.project_data = {}
        self.project_data[self.project_name] = {}

        self.hasStatic = {}

        self.CopyPair = {}

    def collect_info(self):
        # go into the source_dir, find all 1 level deep subdirectories with "Day"
        day_dirs = [x for x in self.source_dir.iterdir() if x.is_dir() and "Day" in x.name]
        # sort day_dirs based on day_dirs name
        day_dirs.sort(key=lambda x: int(re.findall(r'\d+', x.name)[0]))
        logger.info(f"Found {len(day_dirs)} days in {self.source_dir}")

        for day_dir in day_dirs:
            self.CopyPair[day_dir.name] = {}
            logger.debug(f"Working with {day_dir.name}")
            day_value = {}
            self.hasStatic[day_dir.name] = False
            # find all 1 level deep subdirectories
            treatment_dirs_all = [x for x in day_dir.iterdir() if x.is_dir()]
            # remove any treatment_dir with named include "static"
            treatment_dirs = [x for x in treatment_dirs_all if "static" not in x.name]
            if len(treatment_dirs) < len(treatment_dirs_all):
                self.hasStatic[day_dir.name] = True
            
            treatment_elems_sorted = []
            for i, treatment_dir in enumerate(treatment_dirs):
                substance, dose, unit = substance_dose_unit_finder(treatment_dir.name)
                note = ""
                batch_dirs = [x for x in treatment_dir.iterdir() if x.is_dir()]
                treatment_elems_sorted.append([substance, dose, unit, note, treatment_dir, batch_dirs])

            # Sort treatment_dirs_sorted based on 2 rules:
            # 1: substance == Control always at first
            # 2: Then sort based on the value of unit, ascending
            treatment_elems_sorted.sort(key=lambda x: (x[0] != "Control", x[2], x[1]))
            for i, treatment_elements in enumerate(treatment_elems_sorted):
                substance, dose, unit, note, treatment_dir, batch_dirs = treatment_elements
                treatment_char = index_to_char(i)
                day_value[f"Treatment {treatment_char}"] = [substance, dose, unit, note]
                logger.debug(f"Set 'Treatment {treatment_char}' to {substance=}, {dose=}, {unit=}, {note=}")

                _source_treatment_dir = treatment_dir
                _source_batches_dirs = batch_dirs
                _destination_treatment_name = f'{treatment_char} - {" ".join([x for x in [substance, dose, unit, note] if x != ""])}'

                self.CopyPair[day_dir.name][_destination_treatment_name] = [_source_treatment_dir, _source_batches_dirs]

            self.project_data[self.project_name][day_dir.name] = day_value

        
    def update_info(self, destination_parent_dir):
        self.destination_dir = Path(destination_parent_dir) / self.project_name
        self.destination_dir.mkdir(exist_ok=True)
        logger.debug(f"Created {self.destination_dir}")
        self.project_data[self.project_name]["DIRECTORY"] = str(self.destination_dir)
        logger.debug("Directory path set to " + str(self.destination_dir))
        try:
            with open(HISTORY_PATH, "r") as file:
                existing_data = json.load(file)
            if self.project_name in existing_data:
                # remove the project_name from existing_data for update
                existing_data.pop(self.project_name)
                logger.info(f"Project {self.project_name} already exists in history file. Updating...")

            existing_data.update(self.project_data)
            self.PROJECT_CREATED = True
            with open(HISTORY_PATH, "w") as file:
                json.dump(existing_data, file, indent=2)
            logger.info(f"Project {self.project_name} added to history file.")
        except:
            logger.info(f"Project {self.project_name} does not exist in history file. Creating new file...")
            existing_data = self.project_data
            self.PROJECT_CREATED = True
            with open(HISTORY_PATH, "w") as file:
                json.dump(existing_data, file, indent=2)


    def static_backward_compatible_copy(self, old_dir, new_dir):
        try:
            logger.debug(f"Trying to read from {old_dir / 'parameters.json'}")
            with open(old_dir / "parameters.json", "r") as file:
                old_params = json.load(file)
        except:
            old_params = {}

        # Check if old_params keys are the same as DEFAULT_PARAMS keys
        if old_params.keys() == DEFAULT_PARAMS.keys():
            logger.debug("Same format, copy directly")
            shutil.copytree(old_dir, new_dir)

        # Find the keys that are not in DEFAULT_PARAMS
        expired_keys = [key for key in old_params.keys() if key not in DEFAULT_PARAMS.keys()]
        logger.debug(f"Found {expired_keys=}, removing..")
        # Remove them from old_params
        for key in expired_keys:
            old_params.pop(key)

        # Find the keys that are not in old_params
        new_keys = [key for key in DEFAULT_PARAMS.keys() if key not in old_params.keys()]
        logger.debug(f"Found {new_keys=}, adding..")
        # Add them with default value in DEFAULT_PARAMS to old_params
        for key in new_keys:
            old_params[key] = DEFAULT_PARAMS[key]

        # Save old_params to new_dir/parameters.json
        new_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Generating parameters.json in {new_dir}")
        with open(new_dir / "parameters.json", "w") as file:
            json.dump(old_params, file, indent=4)
        logger.debug(f"Generated {new_dir / 'parameters.json'}")

    def copy_data(self):
        source_dir = self.source_dir
        destination_dir = self.destination_dir

        # Generate Day folder based on self.project_data[self.project_name]
        for day_name, day_value in self.project_data[self.project_name].items():
            if day_name == "DIRECTORY":
                continue
            day_dir = destination_dir / day_name
            day_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created {day_dir}")

            logger.debug(f"{self.hasStatic[day_name]=}")

            if self.hasStatic[day_name]:
                logger.debug(f"Found static folder in source, smart copy static folder to {day_dir}")
                old_static_dir = source_dir / day_name / "static"
                new_static_dir = day_dir / "static"
                # Get all treatment-specific static dir within old_static_dir (A, B, C, ..)
                for old_dir in old_static_dir.iterdir():
                    new_dir = new_static_dir / old_dir.name
                    self.static_backward_compatible_copy(old_dir, new_dir)
                # shutil.copytree(source_dir / day_name / "static", day_dir / "static")
                logger.debug(f"Copied static folder to {day_dir}")
            else:
                logger.info(f"No static folder found in source, generating static folder in {day_dir} using DEFAULT PARAMS")
                static_dir = day_dir / "static"
                static_dir.mkdir(parents=True, exist_ok=True)

                treatment_chars = [x.split(" ")[1] for x in self.project_data[self.project_name][day_name].keys()]

                #Generate static/treatment_char directories
                for treatment_char in treatment_chars:
                    static_treatment_dir = static_dir / treatment_char
                    static_treatment_dir.mkdir(parents=True, exist_ok=True)
                    # Use DEFAULT_PARAMS to generate json file in each static/treatment_char directory
                    with open(static_treatment_dir / "parameters.json", "w") as file:
                        json.dump(DEFAULT_PARAMS, file, indent=4)
                    logger.debug(f"Generated {static_treatment_dir / 'parameters.json'}")
        

            # Copy all child folders from source_dir / day_name to day_dir
            for _destination_treatment_name, [_source_treatment_dir, _source_batches_dirs] in self.CopyPair[day_name].items():
                # make destination folders as formatted
                treatment_destination = day_dir / _destination_treatment_name
                treatment_destination.mkdir(exist_ok=True)
                logger.debug(f"Created {treatment_destination}")

                for _source_batch in _source_batches_dirs:
                    source_batch_num = _source_batch.name.split(" ")[-1]
                    destination_batch = treatment_destination / f"Batch {source_batch_num}"
                    destination_batch.mkdir(exist_ok=True)
                    logger.debug(f"Created {destination_batch}")

                    # Copy all .csv file within _source_batch to destination_batch
                    for file in _source_batch.iterdir():
                        if file.suffix == ".csv":
                            shutil.copy(file, destination_batch)
                            logger.debug(f"Copied {file} to {destination_batch}")

class NK_button(customtkinter.CTkButton):
    def __init__(self, parent, text, command, row, column, columnspan=1, *args, **kwargs):
        super().__init__(parent, text=text, command=command, *args, **kwargs)
        self.parent = parent
        self.text = text
        self.command = command
        self.row = row
        self.column = column
        self.columnspan = columnspan

    def show(self):
        self.grid(row=self.row, 
                  column=self.column, 
                  columnspan=self.columnspan, 
                  padx=5, 
                  pady=5, 
                  sticky="nsew")

    def hide(self):
        self.grid_forget()                    
