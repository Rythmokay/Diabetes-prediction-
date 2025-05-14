import os
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

app = Flask(__name__)

# Create model folder if it doesn't exist
if not os.path.exists('model'):
    os.makedirs('model')

# Create a global model and scaler
model = None
scaler = None

# Function to train the model
def train_model():
    global model, scaler
    print("Training new model...")
    
    # Load dataset
    data = pd.read_csv('data/diabetes.csv')
    
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
    
    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    global model, scaler
    
    # Ensure model is trained
    if model is None or scaler is None:
        train_model()
    
    try:
        # Get input values from form
        features = []
        for field in ['pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
                    'insulin', 'bmi', 'diabetes_pedigree', 'age']:
            features.append(float(request.form[field]))
        
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
        
        return render_template('result.html', result=result)
    except Exception as e:
        return render_template('index.html', error=f"Error making prediction: {e}")

# Train the model at startup
train_model()

# For Vercel deployment
if __name__ == '__main__':
    # Run locally when executed directly
    app.run(debug=False, host='127.0.0.1', port=5000)