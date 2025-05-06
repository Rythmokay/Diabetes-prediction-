import os
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, url_for
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

app = Flask(__name__)

# Create model folder if it doesn't exist
if not os.path.exists('model'):
    os.makedirs('model')

# Train model on first run or load from pickle
def get_model():
    model_path = 'model/diabetes_model.pkl'
    scaler_path = 'model/scaler.pkl'
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        # Load existing model and scaler
        model = pickle.load(open(model_path, 'rb'))
        scaler = pickle.load(open(scaler_path, 'rb'))
        print("Loaded existing model and scaler")
    else:
        # Train new model
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
        print(classification_report(y_test, y_pred))
        
        # Save model and scaler
        pickle.dump(model, open(model_path, 'wb'))
        pickle.dump(scaler, open(scaler_path, 'wb'))
        print("Model and scaler saved")
    
    return model, scaler

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    # Get model and scaler
    model, scaler = get_model()
    
    # Get input values from form
    features = [float(request.form[field]) for field in [
        'pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
        'insulin', 'bmi', 'diabetes_pedigree', 'age'
    ]]
    
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

if __name__ == '__main__':
    # Make sure the model is trained or loaded before serving requests
    get_model()
    app.run(debug=True)