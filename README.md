# Helicoidal

## Installation

After downloading the files from GitLab, use the package manager pip to install the application dependencies. Simply open the terminal with the program folder as your current working directory and type the following :
```bash
pip install -r requirements.txt
```
You will also need to install Google Chrome in order to launch the graphic user interface which allows you to modify the lambdas measurements. 

## How to get the lambdas measurements

1) Put your raw images (`.tiff` files only) in the `source` folder.
2) Launch `python3 tube_detection.py`. This will automatically calculate a first approximation of the lambas.
3) Launch `python3 app.py` and use the graphic user interface to modify the automatic detection of the tube and water. 
4) Once satisfied with your measures, launch `python3 json_to_dataframe.py` to create the `lambas.csv` file
