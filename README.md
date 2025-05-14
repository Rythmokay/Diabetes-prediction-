# 🩺 Diabetes Prediction System

<p align="center">
  <img src="screenshots/banner.svg" alt="Diabetes Prediction Banner" width="800">
</p>

A modern web application that predicts diabetes risk based on health metrics using machine learning. The application uses a Random Forest classifier trained on the Pima Indians Diabetes Dataset to provide accurate risk assessments with probability scores.

## ✨ Features

- 📊 Interactive web interface for entering health metrics
- 🔮 Real-time prediction of diabetes risk with probability percentage
- 📱 Responsive design that works on mobile, tablet, and desktop devices
- 📋 Detailed results page with input feature summary
- 🚀 Ready for deployment on Vercel's serverless platform

## 📷 Screenshots

### Input Form
<p align="center">
  <img src="screenshots/input_screen.svg" alt="Input Form" width="600">
  <br>
  <em>Users enter their health metrics through an intuitive form interface</em>
</p>

### Results Page
<p align="center">
  <img src="screenshots/output_screen.svg" alt="Results Page" width="600">
  <br>
  <em>Prediction results with probability score and input feature summary</em>
</p>

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.9+)
- **Machine Learning**: scikit-learn (Random Forest Classifier)
- **Frontend**: HTML5, CSS3 with responsive design
- **Data Processing**: NumPy, Pandas
- **Deployment**: Vercel serverless platform

## 📊 Dataset

The application uses the Pima Indians Diabetes Dataset, which includes the following features:

- Pregnancies: Number of times pregnant
- Glucose: Plasma glucose concentration (mg/dL)
- BloodPressure: Diastolic blood pressure (mm Hg)
- SkinThickness: Triceps skinfold thickness (mm)
- Insulin: 2-Hour serum insulin (mu U/ml)
- BMI: Body mass index (weight in kg/(height in m)²)
- DiabetesPedigreeFunction: Diabetes pedigree function (genetic influence)
- Age: Age in years
- Outcome: Class variable (0: No diabetes, 1: Diabetes)

## 🚀 Local Development

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Diabetes-prediction-.git
   cd Diabetes-prediction-
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://127.0.0.1:5000`

## 🌐 Deploying to Vercel

This application is configured for deployment on Vercel. Follow these steps to deploy:

### Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy the application:
   ```bash
   vercel
   ```

4. For production deployment:
   ```bash
   vercel --prod
   ```

### Using Vercel Dashboard

1. Push your code to GitHub
2. Go to [Vercel](https://vercel.com) and sign in
3. Click "New Project" and import your repository
4. Select the Python framework preset
5. Click "Deploy"

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── data/                  # Dataset directory
│   └── diabetes.csv       # Diabetes dataset
├── model/                 # Directory for saved models
├── screenshots/           # Application screenshots
│   ├── input_screen.svg   # Input form screenshot
│   └── output_screen.svg  # Results page screenshot
├── static/                # Static assets
│   └── styles.css         # CSS styles
├── templates/             # HTML templates
│   ├── index.html         # Input form page
│   └── result.html        # Prediction results page
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
├── runtime.txt           # Python runtime specification
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

## ⚙️ How It Works

1. **Data Loading**: The application loads the Pima Indians Diabetes Dataset
2. **Preprocessing**: Data is split into training and testing sets, and features are standardized
3. **Model Training**: A Random Forest classifier is trained on the preprocessed data
4. **User Input**: Users enter their health metrics through the web interface
5. **Prediction**: The model predicts diabetes risk based on the input features
6. **Results**: Prediction results are displayed with probability score and feature summary

## 🔍 Model Performance

The Random Forest classifier achieves approximately 72% accuracy on the test dataset. The model is trained with the following parameters:

- n_estimators: 100 (number of trees in the forest)
- random_state: 42 (for reproducibility)

## 📝 Future Improvements

- Add user authentication for saving prediction history
- Implement additional machine learning models for comparison
- Add data visualization for better understanding of risk factors
- Develop a REST API for integration with other applications
- Add multi-language support for international users

## 🔒 Privacy

This application does not store any user data. All predictions are made in real-time and are not saved or transmitted to any external servers.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

If you have any questions or suggestions, please open an issue or contact the repository owner.

---

<p align="center">
Made with ❤️ for better healthcare through technology
</p>