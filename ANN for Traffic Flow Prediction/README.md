# ANN for Traffic Flow Prediction

## Overview

In this project, I used Artificial Neural Networks (ANNs) to predict traffic conditions using historical traffic flow data. The project explores the complete machine learning pipeline, including data cleaning, exploratory data analysis, model development, evaluation, and then I used a Generative AI-assisted neural network design to compare it to my work.

---

## Features

- Cleans and preprocesses real-world traffic flow data.
- Performs exploratory data analysis (EDA) to identify trends and relationships.
- Develops and evaluates a Recurrent Neural Network (RNN) for traffic prediction.
- Compares a manually designed model with a Generative AI-assisted neural network implementation.
- Uses time-series data to predict traffic congestion levels.

---

## Repository Structure

### Main Files

| File | Description |
|------|-------------|
| **EDA(exploratory data analysis).ipynb** | Exploratory data analysis used to understand the dataset, identify patterns, and justify model selection. |
| **EDA(data cleaning).ipynb** | Data cleaning and preprocessing, including feature engineering and preparation of the dataset for model training. |
| **Model Design and Implementation.ipynb** | Development and training of the manually designed Recurrent Neural Network (RNN). |
| **Model Evaluation.ipynb** | Evaluation of the trained model using performance metrics and visualisations. |
| **GenAI-Assisted Neural Network.ipynb** | Implementation and evaluation of a Generative AI-assisted neural network for comparison with the manually developed model. |
| **TrafficTwoMonth.csv** | Dataset containing two months of traffic data used for training and evaluating the models. |

---

## Technologies Used

- Python
- Jupyter Notebook
- TensorFlow / Keras
- NumPy
- Pandas
- Matplotlib
- Scikit-learn

---

## Project Objective

This project aimed to develop an Artificial Neural Network capable of predicting traffic congestion levels from historical traffic flow data. The project also compares the performance of a manually developed Recurrent Neural Network with a Generative AI-assisted neural network to evaluate the benefits and limitations of AI-assisted model design.

---

## Results

The project demonstrated that recurrent neural networks can successfully learn temporal patterns within traffic data to predict congestion levels. Performance evaluation highlighted the strengths and limitations of the manually developed RNN while showing that the AI-assisted model achieved higher predictive accuracy through the use of a more advanced LSTM architecture.

---

## Future Improvements

Potential future work includes:

- Incorporating additional data sources such as weather and road incident information.
- Testing alternative deep learning architectures such as GRUs and Transformer models.
- Addressing class imbalance using more advanced sampling techniques.
- Evaluating performance using larger and more diverse traffic datasets.

---
