# Programming Data Cleaning and Analysis 

# Description
This is my final-year Master’s project (PFE) in Machine Learning at the University of Lille.
The project focuses on cleaning programming data from first-year Bachelor students collected using Thonny IDE, and analyzing the cleaned data to gain insights into the students’ progress. 

# Installation
1. Clone the repository
```
git clone https://github.com/sana-mirahsani/ApprentissagePython-Tests.git 
```

2. Create a virtual environment
```
python -m venv venv
```

3. Install dependencies
```
pip install -r requirements.txt
```

# Usage
1. Go to folder : **notebooks**

2. Run **7.run_all_cleaning.py** and give the name of the raw data.json which must be in data/raw directory.

3. This file creates a pipeline to execute all notebooks (from number 0 to 4) for cleaning phase. This pipeline gets the raw data in json and gives 
a cleaned df for actors and filenames in CSV in data/interim/filename.

4. In Every execution of a notebook the output is saved as csv file and it is passed to the next notebook as the input.

5. Add meta data tag:parameters the second cell in notebook

# Dataset
The dataset used in this project comes from Thonny IDE and contains JSON files for all students over one semester at the University of Lille. For privacy and security reasons, the dataset is not included in this repository.

# Methodology
The project uses a custom data cleaning pipeline built with Pandas and other Python methods to preprocess the JSON data collected from Thonny IDE. The pipeline was designed to handle the dataset in multiple steps, ensuring the data is clean and structured for further analysis.

## Data Cleaning Steps
The cleaning process is divided into multiple notebooks, each performing a specific task:

1. **0.Cleaning_JSON.ipynb** – Loads the JSON data, performs basic cleaning, and outputs a CSV file (filename_clean.csv).

2. **1.Cleaning_actors.ipynb** – Cleans student names and generates filename_actor_clean.csv.

3. **2.Cleaning_filename_phase1.ipynb** – Cleans filenames based on verbs, producing filename_filename_phase1_clean.csv.

4. **3.Cleaning_filename_phase2.ipynb** – Cleans filenames based on session/seance information, producing filename_filename_phase2_clean.csv.

5. **4.Cleaning_filename_phase3.ipynb** – Corrects filenames that are valid but do not match the content of P_codestate, generating filename_filename_phase3_clean.csv.

## Pipeline Flow
The pipeline processes the files sequentially:

1. filename + _clean.csv              → output of 0.Cleaning_JSON.ipynb
2. filename + _actor_clean.csv        → output of 1.Cleaning_actors.ipynb
3. filename + _filename_phase1_clean.csv → output of 2.Cleaning_filename_phase1.ipynb
4. filename + _filename_phase2_clean.csv → output of 3.Cleaning_filename_phase2.ipynb
5. filename + _filename_phase3_clean.csv → output of 4.Cleaning_filename_phase3.ipynb

This modular approach allows for incremental cleaning, making it easier to track changes and debug the preprocessing steps.


# Project Structure?
```
project-root/
├── data/ # Datasets (Ignored)
│
├── notebooks/             
│   ├── 1.Cleaning_actors.py           # Cleaning actor column
│   ├── 2.Cleaning_filename_phase1.py  # Cleaning filename_infere column by verb
│   ├── 3.Cleaning_filename_phase2.py  # Cleaning filename_infere column by sessions 
│   ├── 4.Cleaning_filename_phase3.py  # Finding and removing bizzar indices 
│   ├── 5.Anonymizing.py               # Anonymizing data   
│   ├── 6.Analyze.py                   # Analyzing data  
│   ├── 7.run_all_cleaning.py          # Run all notebooks by pipeline  
│
├── src/                     
│   ├── data/  # constant data (Ignored)
│   │    
│   ├── features/ 
│       ├── data_cleaning.py       # Functions to cleaning actors or filename_infere
│       ├── data_testing.py        # Functions to test the results after cleaning each time
│       ├── io_utils.py            # Functions to read and write csv files 
│       ├── pipeline_utils         # Functions to verify the values
│ 
├── requirement.txt
|       
└── README.md          
```

# License
This project is licensed under the MIT License. See LICENSE file for details.

# Contact
E-mail : s.mirahsani1998@gmail.com
Linkdin : https://www.linkedin.com/in/sana-mirahsani