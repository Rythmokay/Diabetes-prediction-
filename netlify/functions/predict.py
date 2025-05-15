import json
import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

# Add the project root to the path so we can import from app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Model and scaler variables
model = None
scaler = None
model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'model', 'diabetes_model.joblib')
scaler_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'model', 'scaler.joblib')

def train_model():
    global model, scaler
    print("Training new model...")
    
    # Load dataset
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'diabetes.csv')
    data = pd.read_csv(data_path)
    
    # Split features and target
    X = data.drop('Outcome', axis=1)
    y = data['Outcome']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Save model and scaler
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    
    return model, scaler

def load_model():
    global model, scaler
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("Model loaded successfully")
    except:
        print("Could not load model, training new one")
        model, scaler = train_model()
    return model, scaler

def handler(event, context):
    global model, scaler
    
    # Parse the request body
    try:
        request_body = json.loads(event['body'])
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body'})
        }
    
    # Ensure model is loaded
    if model is None or scaler is None:
        model, scaler = load_model()
    
    try:
        # Extract features
        features = []
        for field in ['pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
                    'insulin', 'bmi', 'diabetes_pedigree', 'age']:
            features.append(float(request_body.get(field, 0)))
        
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
