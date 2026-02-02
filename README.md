# AC

## Grade 17.6/20

## How to compile and run

First, you need to install the required libraries. They can be installed using the command line below:

```shell
pip install -r requirements.txt
```

If it doesn't work install one by one:

```shell
pip install pandas
pip install matplotlib
pip install seaborn
pip install scikit-learn
pip install numpy
pip install plotly
pip install imblearn
pip install lightgbm
pip install xgboost
pip install catboost
pip install ipython
pip install jinja2
```

## **Order to Read and Run the Report**

### **1. Data analysis:**

The **Data Analysis** section is located in the `data_analysis` folder and should be read first, as it provides the foundational understanding of the datasets and variables used throughout the project.

The recommended starting point is the file `_datasets_specifications`, which explains:

- The structure of the datasets
- The meaning of variables
- Key assumptions and constraints

After reviewing `_datasets_specifications`, the remaining analysis files in the `data_analysis` folder can be read or run in any order, as they explore the data from different datasets.

### **2. Data Preparation:**

The **Data Preparation** section is located in the `data_preparation` folder and should be reviewed after the data analysis, since it uses transformed data obtained during analysis.

Some of the datasets may correspond to older versions of the data if not all analysis steps were executed beforehand.
In such cases, the script `_data_cleaning_shortcut` should be run to ensure that:

- The datasets are correctly cleaned
- All required variables and formats are present

Aside from this requirement, the remaining data preparation reports and scripts can be run in any order.

All datasets generated during this stage are stored in the `predict_datasets` folder, which is required for the prediction phase.

### **3. Prediction Scripts (with the available years):**

The **prediction scripts** using the available historical data are located in the `prediction_scripts` folder, excluding the `test_data_prediction` file.

These scripts:

- Train and evaluate models using known data
- Generate predictions based on the available years

**⚠️ Important:**
These scripts can only be executed if the required datasets already exist in the `predict_datasets` folder.
If the datasets are missing or outdated, the data preparation step must be rerun first.

### **4. Prediction Scripts (with the test data):**

The **prediction script** that uses test data is located in: `prediction_scripts/test_data_prediction`.

This script:

- Applies trained models to the season eleven
- Produces final prediction outputs

**⚠️ Important:**
Just like the previous section, this script can only be run if the necessary datasets are present in the `predict_datasets` folder.
