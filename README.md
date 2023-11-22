# EARTHWORM ANALYZER

![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/universities.png?raw=true)

## Author

Luong Cao Thang (Vincent Luong)
PhD candidate, I-Shou University, Kaohsiung, Taiwan.  
Email: [thang.luongcao@gmail.com](mailto:thang.luongcao@gmail.com)  

## Correspondence:

Prof. Chih-Hsin Hung  
Laboratory of Biotechnology, I-Shou University, Kaohsiung, Taiwan.  
Email: [chhung@isu.edu.tw](mailto:chhung@isu.edu.tw)  

Prof. Chung-Der Hsiao  
Laboratory of Biotechnology, ChungYuan Christian University, Taoyuan, Taiwan.  
Email: [cdhsiao@cycu.edu.tw](mailto:cdhsiao@cycu.edu.tw)  


# EARTHWORM ASSAY downstream analyzing application
Earthworm Analyzer is the new software we build to accelerate the Earthworm Assay analysis process. It was designed to streamline and automate the arduous data management and organize the processes associated with raw data.

## INSTALLATION GUIDE

1. Download ```.zip``` file of the whole repository by click on ```Code``` button and select ```Download ZIP``

    ![download_button](https://github.com/ThangLC304/EwA/blob/main/Bin/support/download_button.png)

2. Unzip the file, within the App Folder, run the ```new_setup.bat``` file to install independencies

3. Run the program using ```run.bat```

## APP NAVIGATION

1. Create new Project from scratch using ```Create Project``` button

    ![App_Screen](https://github.com/ThangLC304/EwA/blob/main/Bin/support/app_screen.png)

2. Select Project from available ones within the Project List -> ```Load Project```

3. Run analysis on the Data of the current Day (all treatments within it) using ```Analyze``` button

    The result will be saved as "EndPoints.xlsx" at the Day directory (e.g., [project_name]/Day 1/EndPoints.xlsx) <br>
    The following EndPoints will be included: <br>

    - Total Distance (cm)	Average Speed (cm/s) <br>
    - Total Absolute Turn Angle (degree) <br>
    - Average Angular Velocity (degree/s) <br>
    - Slow Angular Velocity Percentage (%) <br>
    - Fast Angular Velocity Percentage (%) <br>
    - Meandering (degree/m) <br>
    - Freezing Time (%) <br>
    - Moving Time (%) <br>
    - Average distance to Center of the Tank (cm) <br>
    - Time spent in Center (%) <br>
    - Total entries to the Center (times) <br>
    - Fractal Dimension <br>
    - Entropy <br>

4. Import existed legacy-formatted Projects using ```Import Trajectories``` button

    After clicking the Import Trajectories button, <br>
    First, you will be asked to Select the Folder of the Legacy Project you want to import. <br>
    Then, another window pop up asking you to Select the Folder where the Interpreted project will be stored (only the .csv files are transfered so you don't have to worry about having video files in the Legacy Project) <br>
    <br>
    e.g., If you Legacy Project is "Eu (Finish Calculated)" stored at "C:\EarthwormProject\Eu (Finished Calculated)" <br>
    In the first window, select that folder <br>
    In the second window, if you select a folder at "D:\ReAnalysis" <br>
    A new folder with the exact same name with the Legacy Project will be created inside "D:\ReAnalysis", the path will be "D:\ReAnalysis\Eu (Finish Calculated)" <br>

**<!!!>: Please refrain from changing the directory name at the new location**



## Regular questions:

1. What if I have changed the name of the directory name at the new location?

**A:** If there is no other folder with the name exactly like the old name of the project, when you use the ```Load Project``` button, the App will ask you to select the new location of the project so it can update within its memory. <br>
<br>
If you changed the name of the directory and then you created a new directory with the same exact name, the App will recognize the new empty folder as the valid path for the Project, hence not asking you for relocation -> Mismatching issue.

2. When I want to update the program, do I have to go to your GitHub Repository to download new version and replace the old one?

**A:** Fortunately no, you can use the ```updater.bat``` to check to update the app.




