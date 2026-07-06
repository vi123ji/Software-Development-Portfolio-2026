# Predicting House Pricing Using Machine Learning Algorithms

## Overview

This project investigates the use of machine learning regression algorithms to predict house prices based on property characteristics. It follows the complete machine learning workflow, including data preprocessing, exploratory data analysis, model development, hyperparameter tuning, and performance evaluation to determine which algorithm provides the most accurate predictions.

---

## Features

- Cleans and preprocesses a real-world housing dataset.
- Performs exploratory data analysis (EDA) to identify trends, correlations, and outliers.
- Implements and compares multiple regression algorithms for house price prediction.
- Optimises model performance using hyperparameter tuning with GridSearchCV.
- Evaluates model performance using standard regression metrics.

---

## Repository Structure

### Main Files

| File | Description |
|------|-------------|
| **Source code.ipynb** | Complete Jupyter Notebook containing data preprocessing, exploratory data analysis, model implementation, hyperparameter tuning, and evaluation. |
| **housesdata.csv** | Housing dataset used to train and evaluate the machine learning models. |

---

## Technologies Used

- Python
- Jupyter Notebook
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn

---

## Project Objective

This project aimed to develop and compare multiple machine learning regression models capable of predicting house prices from property features. The project evaluates the strengths and limitations of Linear Regression, Elastic Net Regression, and Decision Tree Regression to determine which model performs best for this dataset.

---

## Results

Three regression algorithms were evaluated and compared using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R² score. Hyperparameter tuning improved the performance of both the Elastic Net and Decision Tree models. Overall, Linear Regression and the tuned Elastic Net model achieved the strongest predictive performance on this dataset, while the tuned Decision Tree demonstrated improved performance but lower generalisation accuracy.

---

## Future Improvements

Potential future work includes:

- Evaluating additional regression algorithms such as Random Forest and Gradient Boosting.
- Incorporating additional property features to improve prediction accuracy.
- Performing more advanced feature engineering and feature selection.
- Using larger and more diverse housing datasets.
- Deploying the trained model as an interactive house price prediction application.

---
