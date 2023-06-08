# Aims
The aim of this project is to develop a logic simulator program in Python. The program does the following:
1. Read a text file that describes a logic circuit and follows the rules of the specified logic description language,
2. Display syntax or semantic errors of the text file in the terminal or GUI if there is any,
3. Display the monitored signals,
4. Execute commands by the user (see user guide). 

# Codestyle
Some of the code files are not PEP 8 compliant because the maximum number of characters on the same line exceeds the required
limit. This is intentional for the purpose of readability. This is the only aspect of PEP8 which we have deviated from.


# Running the simulator
- Change directory into the final folder with ```cd final```
- To run the logic simulator type:
  - ``` python logsim.py -g ```- For loading the definition file graphically
  -  ```python logsim.py <file_path> ``` - For loading the file through the command line
  -  ```python logsim.py -c <file_path>  ```- For running the program through the command line
- The simulator also supports Simplified Chinese for the GUI. To run the simulator in Simplified Chinese, add LANG=zh_CN.utf8 before running the file, example:
  - ``` LANG=zh_CN.utf8 python logsim.py -g  ```or ``` LANG=zh_CN.utf8 ./logsim.py -g ```
 

# Testing
PyTests must be run from after changing current directory into final as the test definition file paths are relative. This can be done with this command: ```cd final```

