#!/usr/bin/env python
import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def train_model():
    """Train a model on the diabetes dataset"""
    # Load dataset
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'diabetes.csv')
    data = pd.read_csv(data_path)
    
    # Split features and target
    X = data.drop('Outcome', axis=1)
    y = data['Outcome']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    return model, scaler

def predict(form_data):
    """Make a prediction using the trained model"""
    # Train the model
    model, scaler = train_model()
    
    # Get input values from form
    features = [
        float(form_data.get('pregnancies', 0)),
        float(form_data.get('glucose', 0)),
        float(form_data.get('blood_pressure', 0)),
        float(form_data.get('skin_thickness', 0)),
        float(form_data.get('insulin', 0)),
        float(form_data.get('bmi', 0)),
        float(form_data.get('diabetes_pedigree', 0)),
        float(form_data.get('age', 0))
    ]
    
    # Make features into array and scale
    input_features = np.array(features).reshape(1, -1)
    input_features_scaled = scaler.transform(input_features)
    
    # Make prediction
    prediction = model.predict(input_features_scaled)[0]
    
    # Get prediction probability
    proba = model.predict_proba(input_features_scaled)[0][1]
    probability = round(proba * 100, 2)
    
    # Return result
    result = {
        'prediction': 'Positive' if prediction == 1 else 'Negative',
        'probability': probability,
        'features': {
            'Pregnancies': features[0],
            'Glucose': features[1],
            'Blood Pressure': features[2],
            'Skin Thickness': features[3],
            'Insulin': features[4],
            'BMI': features[5],
            'Diabetes Pedigree Function': features[6],
            'Age': features[7]
        }
    }
    
    return result

if __name__ == '__main__':
    try:
        # Get form data from JSON file
        if len(sys.argv) > 1:
            json_file_path = sys.argv[1]
            with open(json_file_path, 'r') as f:
                form_data = json.load(f)
            
            # Make prediction
            result = predict(form_data)
            
            # Print result as JSON
            print(json.dumps(result))
        else:
            print(json.dumps({"error": "No form data provided"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
