import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os

def train_diabetes_model():
    """
    Train a diabetes prediction model using the Pima Indians Diabetes Dataset
    and save the trained model to a pickle file.
    """
    # Load the dataset
    # If the dataset doesn't exist locally, create sample data based on Pima Indians Diabetes Dataset
    try:
        # Try to load the dataset
        url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
        column_names = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                       'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']
        df = pd.read_csv(url, names=column_names)
        print("Dataset loaded from URL successfully.")
    except:
        # Create sample data if loading fails
        print("Creating sample dataset...")
        np.random.seed(42)
        n_samples = 768  # Same as Pima Indians dataset
        
        # Generate synthetic data with correlations similar to the real dataset
        pregnancies = np.random.randint(0, 18, n_samples)
        glucose = np.random.randint(50, 200, n_samples)
        blood_pressure = np.random.randint(30, 120, n_samples)
        skin_thickness = np.random.randint(0, 100, n_samples)
        insulin = np.random.randint(0, 850, n_samples)
        bmi = 20 + 30 * np.random.random(n_samples)  # BMI between 20 and 50
        diabetes_pedigree = 0.1 + 2 * np.random.random(n_samples)  # Between 0.1 and 2.1
        age = np.random.randint(21, 80, n_samples)
        
        # Create a synthetic target with some correlations to features
        probability = (
            0.1 +
            0.03 * pregnancies + 
            0.0025 * glucose +
            0.001 * blood_pressure +
            0.002 * bmi +
            0.02 * diabetes_pedigree +
            0.005 * age
        )
        probability = np.clip(probability, 0, 0.99)
        outcome = np.random.binomial(1, probability)
        
        # Create DataFrame
        data = {
            'Pregnancies': pregnancies,
            'Glucose': glucose,
            'BloodPressure': blood_pressure,
            'SkinThickness': skin_thickness,
            'Insulin': insulin,
            'BMI': bmi,
            'DiabetesPedigreeFunction': diabetes_pedigree,
            'Age': age,
            'Outcome': outcome
        }
        df = pd.DataFrame(data)
        print("Sample dataset created successfully.")

    # Display basic info about the dataset
    print(f"Dataset shape: {df.shape}")
    print(f"Diabetes cases: {df['Outcome'].sum()}")
    print(f"Diabetes prevalence: {df['Outcome'].mean():.2%}")

    # Split features and target
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train the model - using Random Forest for better accuracy
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")

    # Display classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Display confusion matrix
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save the model and scaler
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save the model
    with open(os.path.join(model_dir, 'model.pkl'), 'wb') as f:
        pickle.dump((model, scaler), f)
    
    print(f"Model saved to {os.path.join(model_dir, 'model.pkl')}")
    
    return model, scaler

def load_model():
    """Load the trained model and scaler from the pickle file."""
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model.pkl')
    
    # Check if model exists, if not train it
    if not os.path.exists(model_path):
        return train_diabetes_model()
    
    # Load the model and scaler
    with open(model_path, 'rb') as f:
        model, scaler = pickle.load(f)
    
    return model, scaler

def predict_diabetes(features):
    """
    Make a diabetes prediction using the trained model.
    
    Args:
        features (dict): Dictionary with feature names and values
        
    Returns:
        tuple: (prediction, probability)
    """
    # Load the model and scaler
    model, scaler = load_model()
    
    # Convert features to a DataFrame with the correct order
    feature_names = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    
    # Create a DataFrame with one row
    df = pd.DataFrame([features], columns=feature_names)
    
    # Scale the features
    scaled_features = scaler.transform(df)
    
    # Make prediction
    prediction = model.predict(scaled_features)[0]
    
    # Get probability
    probability = model.predict_proba(scaled_features)[0][1]
    
    return prediction, probability

if __name__ == "__main__":
    # Train and save the model if run directly
    train_diabetes_model()