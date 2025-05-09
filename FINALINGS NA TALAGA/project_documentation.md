International Education Cost Predictor - Project Documentation


Project Overview
This web application uses machine learning to predict international education costs based on various factors. The application allows users to create accounts, input details about their educational interests, receive cost predictions, and view statistics through a personalized dashboard.
Table of Contents
Project Structure
Dataset Description
ML Model Training
Authentication Implementation
Integration Steps
Application Features
API Reference
Challenges Encountered
Future Improvements
Deployment Guide


Project Structure
The project is organized as follows:

education_cost_predictor/
├── education_cost_predictor/    # Main Django project settings
├── predictor/                   # Main application with views, models, forms
│   ├── migrations/              # Database migrations
│   ├── templates/               # HTML templates
│   │   ├── predictor/           # App-specific templates
│   │   ├── registration/        # Authentication templates
│   ├── static/                  # Static files (CSS, JS, images)
│   ├── admin.py                 # Admin site configuration
│   ├── apps.py                  # App configuration
│   ├── forms.py                 # Form definitions
│   ├── models.py                # Database models
│   ├── tests.py                 # Tests
│   ├── urls.py                  # URL routing
│   └── views.py                 # View controllers
├── manage.py                    # Django command-line utility
└── db.sqlite3                   # SQLite database
├── trained_model.pkl            # Serialized ML model
├── requirements.txt             # Project dependencies



Dataset Description

The dataset used for training the education cost prediction model contains structured data with the following features:
Country: Country where the university is located
City: City where the university is located
University: Name of the university
Program Type: Type of program (Undergraduate, Master's, PhD)
Field of Study: Area of study (Engineering, Business, Medicine, etc.)
Duration: Length of the program in years
Living Arrangement: Type of accommodation (On-campus, Off-campus, Homestay)
Scholarship Status: Whether a scholarship is available
Exchange Rate: Current exchange rate relative to local currency
Cost of Living Index: Index representing the relative cost of living
The target variable is the Education Cost, which represents the total estimated cost of education including tuition and living expenses.

ML Model Training

The education cost prediction model was built using a Random Forest Regressor from scikit-learn. The training process followed these steps:
Data Preprocessing:
Loading the dataset from CSV
Cleaning and standardizing data
Encoding categorical variables
Handling missing values
Feature Scaling:
Using StandardScaler to normalize numeric features
Model Selection and Training:
Random Forest Regressor with optimized hyperparameters:
n_estimators = 100
max_depth = 10
min_samples_split = 5
min_samples_leaf = 2
random_state = 42
Model Evaluation:
Cross-validation to ensure model robustness
Performance metrics:
R² Score: Coefficient of determination
RMSE: Root Mean Squared Error
MAE: Mean Absolute Error
Feature Importance Analysis:
Identification of most influential features for cost prediction
Model Serialization:
The trained model and preprocessing components serialized using pickle
Saved as trained_model.pkl for use in the web application

Authentication Implementation

The application implements Django's built-in authentication system:
Registration:
Custom registration form with email validation
Account activation process
Success message upon registration
Login:
Username/email and password authentication
Session management
Remember-me functionality
Logout:
Secure session termination
Redirect to home page
Access Control:
LoginRequiredMixin for protected views
Permission-based access control
URL protection for authenticated-only sections

Integration Steps

The integration of the ML model with the Django application involved:
Model Integration:
Loading the serialized model using pickle
Creating prediction functions in views.py
Form Integration:
CostPredictionForm for collecting user input
Form validation and error handling
Database Integration:
PredictionResult model to store predictions
User relationship for personalized history
View Integration:
Form rendering and processing
Prediction calculation
Result storage and display
Dashboard Integration:
Data aggregation for statistics
Visualization implementation
Template System:
Bootstrap-based responsive design
Consistent UI across all pages

Application Features

The web application provides:
User Management:
Account creation and login
Profile management
Password reset functionality
Cost Prediction:
Interactive form for educational details
Real-time predictions
Detailed breakdown of costs
Dashboard:
Historical prediction tracking
Statistical analysis
Visualization of predictions over time
Cost comparisons across countries/programs
Educational Resources:
Information about universities
Scholarship opportunities
Cost-saving tips

API Reference
The internal API structure includes:
Model Loading AP:

   def load_model():
       """Load the pre-trained cost prediction model"""
       with open('trained_model.pkl', 'rb') as f:
           model = pickle.load(f)
       return model

Prediction API:

   def predict_cost(input_data):
       """Generate cost prediction based on input data"""
       model = load_model()
       # Process input data
       prediction = model.predict(processed_data)
       return prediction

View APIs:
Authentication views
Prediction form and results views
Dashboard data aggregation views

Challenges Encountered

During development, several challenges were addressed:
Package Dependencies:
Missing crispy_forms package caused rendering issues
Resolved by adding to requirements.txt and INSTALLED_APPS
Configuration Files:
Missing WSGI/ASGI files prevented deployment
Created and configured necessary files
Template Structure:
Authentication template organization issues
Restructured template directories for proper inheritance
URL Routing:
404 error for /predictor/ URL
Fixed by correctly configuring URL patterns
Server Errors:
500 error in dashboard view due to data processing
Implemented error handling and fixed calculation logic

Deployment Guide

To deploy this application:
Environment Setup:
Install Python 3.8+
Create virtual environment
Install dependencies: pip install -r requirements.txt
Configuration:
Configure settings.py for production
Set secure SECRET_KEY
Configure database settings
Database Setup:
Run migrations: python manage.py migrate
Create superuser: python manage.py createsuperuser
Static Files:
Collect static files: python manage.py collectstatic
WSGI Server:
Configure Gunicorn or uWSGI
Web Server:
Set up Nginx or Apache as reverse proxy
Security:
Implement HTTPS with SSL certificate
Configure security middlewares
Monitoring:
Set up logging and monitoring tools