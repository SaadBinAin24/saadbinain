import os
import pickle
import pandas as pd
from django.conf import settings

class EducationCostPredictor:
    """
    A class for predicting international education costs using the trained ML model.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EducationCostPredictor, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load the trained model from the file."""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'trained_model.pkl')
            with open(model_path, 'rb') as file:
                self.model = pickle.load(file)
            self.model_loaded = True
            print("Model loaded successfully!")
        except Exception as e:
            self.model_loaded = False
            print(f"Error loading model: {str(e)}")
    
    def predict(self, data):
        """
        Make a prediction based on input data.
        
        Args:
            data (dict): Dictionary containing the input data
            
        Returns:
            dict: Prediction results including tuition cost, living expenses, and total cost
        """
        if not self.model_loaded:
            return {"error": "Model not loaded. Please check the model file."}
            
        try:
            # Convert input data to DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = data.copy()
                
            # Get the program name (handle 'Other' case)
            if 'other_program' in data and data['program'] == 'Other':
                df['Program'] = data['other_program']
            else:
                df['Program'] = data['program']
            
            # Convert string values to appropriate numeric types if needed
            for field in ['living_cost_index', 'rent_usd', 'visa_fee_usd', 'insurance_usd', 'exchange_rate', 'duration_years']:
                if field in data and isinstance(data[field], str) and data[field].strip():
                    try:
                        df[field] = float(data[field])
                    except ValueError:
                        return {"error": f"Invalid value for {field}: {data[field]}"}
                        
            # Prepare DataFrame with required columns in correct format
            prediction_data = pd.DataFrame({
                'Country': df['country'],
                'City': df['city'],
                'University': df['university'],
                'Program': df['Program'],
                'Level': df['level'],
                'Duration_Years': df['duration_years'],
                'Living_Cost_Index': df['living_cost_index'],
                'Rent_USD': df['rent_usd'],
                'Visa_Fee_USD': df['visa_fee_usd'],
                'Insurance_USD': df['insurance_usd'],
                'Exchange_Rate': df['exchange_rate'],
            })
                
            # Make prediction (estimated tuition)
            tuition = self.model.predict(prediction_data)[0]
            
            # Convert all values to appropriate types for calculations
            monthly_rent = float(str(data['rent_usd']).strip())
            annual_insurance = float(str(data['insurance_usd']).strip())
            visa_fee = float(str(data['visa_fee_usd']).strip())
            duration_years = float(str(data['duration_years']).strip())
            
            # Calculate living expenses for the entire duration
            living_expenses = (monthly_rent * 12 * duration_years) + (annual_insurance * duration_years) + visa_fee
            
            # Calculate total cost
            total_cost = tuition + living_expenses
            
            return {
                'estimated_tuition_usd': round(tuition, 2),
                'living_expenses_usd': round(living_expenses, 2),
                'total_cost_usd': round(total_cost, 2)
            }
        except Exception as e:
            return {"error": f"Prediction error: {str(e)}"}
    
    def get_model_info(self):
        """
        Get information about the model.
        
        Returns:
            dict: Information about the model
        """
        if not self.model_loaded:
            return {"error": "Model not loaded"}
            
        try:
            # For a scikit-learn Pipeline with XGBoost, we can get info like this
            model_type = type(self.model).__name__
            
            # Get the estimator (XGBoost model) from the pipeline
            estimator = self.model.named_steps['model']
            estimator_type = type(estimator).__name__
            
            # Get feature information
            preprocessor = self.model.named_steps['preprocessor']
            feature_info = {}
            
            try:
                # Try to get information about the features
                feature_info['numerical_features'] = list(preprocessor.transformers_[0][2])
                feature_info['categorical_features'] = list(preprocessor.transformers_[1][2])
            except:
                # If that fails, just give basic info
                feature_info['features'] = "Information not available"
                
            # Get model parameters
            try:
                model_params = estimator.get_params()
                important_params = {
                    'n_estimators': model_params.get('n_estimators', 'N/A'),
                    'learning_rate': model_params.get('learning_rate', 'N/A'),
                    'max_depth': model_params.get('max_depth', 'N/A'),
                }
            except:
                important_params = {"params": "Information not available"}
            
            return {
                "model_type": model_type,
                "estimator_type": estimator_type,
                "feature_info": feature_info,
                "parameters": important_params,
                "model_accuracy": "95.68%"  # This was the accuracy from the Jupyter notebook
            }
        except Exception as e:
            return {"error": f"Error getting model info: {str(e)}"}
            
    def get_sample_data_stats(self):
        """
        Get statistics about the sample dataset
        
        Returns:
            dict: Statistics about the dataset
        """
        try:
            # Try to load the CSV file
            try:
                data_path = os.path.join(settings.BASE_DIR, 'International_Education_Costs.csv')
                df = pd.read_csv(data_path)
            except FileNotFoundError:
                # Try alternative path
                data_path = os.path.join(settings.BASE_DIR, 'model and data', 'International_Education_Costs.csv')
                df = pd.read_csv(data_path)
            
            # Calculate statistics
            stats = {
                "total_records": len(df),
                "countries": df['Country'].nunique(),
                "universities": df['University'].nunique(),
                "programs": df['Program'].nunique(),
                "levels": df['Level'].nunique(),
                "avg_tuition": round(df['Tuition_USD'].mean(), 2),
                "median_tuition": round(df['Tuition_USD'].median(), 2),
                "min_tuition": round(df['Tuition_USD'].min(), 2),
                "max_tuition": round(df['Tuition_USD'].max(), 2),
                "avg_duration": round(df['Duration_Years'].mean(), 2),
                "countries_distribution": df['Country'].value_counts().head(10).to_dict(),
                "levels_distribution": df['Level'].value_counts().to_dict(),
                "tuition_by_level": df.groupby('Level')['Tuition_USD'].mean().to_dict(),
            }
            return stats
        except Exception as e:
            return {"error": f"Error getting dataset stats: {str(e)}"} 