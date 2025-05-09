import pandas as pd
import pickle
import os
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

class InternationalEducationPredictor:
    """
    A class for predicting international education costs using a trained machine learning model.
    
    This model predicts education costs based on various factors such as country, city, 
    university, program, level, duration, and other related metrics.
    """
    
    def __init__(self, model_path='trained_model.pkl'):
        """
        Initialize the predictor by loading the trained model.
        
        Parameters:
        -----------
        model_path : str
            Path to the trained model file (default is 'trained_model.pkl')
        """
        # Check if model file exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        # Load the trained model
        try:
            with open(model_path, 'rb') as file:
                self.model = pickle.load(file)
            print("Model loaded successfully!")
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def predict(self, data):
        """
        Make predictions using the trained model.
        
        Parameters:
        -----------
        data : pandas.DataFrame or dict
            Data for which to make predictions. If a dict is provided, it will be converted to a DataFrame.
            
        Returns:
        --------
        float or numpy.ndarray
            Predicted education cost(s) in USD
        """
        # Convert dict to DataFrame if necessary
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        elif not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame or a dictionary")
        
        # Ensure all required columns are present
        required_columns = [
            'Country', 'City', 'University', 'Program', 'Level', 
            'Duration_Years', 'Living_Cost_Index', 'Rent_USD', 
            'Visa_Fee_USD', 'Insurance_USD', 'Exchange_Rate'
        ]
        
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Make prediction
        try:
            prediction = self.model.predict(data)
            return prediction
        except Exception as e:
            raise Exception(f"Error making prediction: {str(e)}")
    
    def get_estimated_cost(self, country, city, university, program, level, 
                          duration_years, living_cost_index, rent_usd, 
                          visa_fee_usd, insurance_usd, exchange_rate):
        """
        Get an estimated education cost based on input parameters.
        
        Parameters:
        -----------
        country : str
            Country name
        city : str
            City name
        university : str
            University name
        program : str
            Program of study
        level : str
            Education level (e.g., 'Bachelor', 'Master', 'PhD')
        duration_years : float
            Duration of the program in years
        living_cost_index : float
            Living cost index for the location
        rent_usd : int
            Monthly rent in USD
        visa_fee_usd : int
            Visa fee in USD
        insurance_usd : int
            Annual insurance cost in USD
        exchange_rate : float
            Exchange rate to USD
            
        Returns:
        --------
        float
            Estimated education cost in USD
        """
        # Create a DataFrame with the input data
        data = {
            'Country': country,
            'City': city,
            'University': university,
            'Program': program,
            'Level': level,
            'Duration_Years': duration_years,
            'Living_Cost_Index': living_cost_index,
            'Rent_USD': rent_usd,
            'Visa_Fee_USD': visa_fee_usd,
            'Insurance_USD': insurance_usd,
            'Exchange_Rate': exchange_rate
        }
        
        # Make prediction
        prediction = self.predict(data)
        return prediction[0]
    
    def get_total_cost(self, country, city, university, program, level, 
                     duration_years, living_cost_index, rent_usd, 
                     visa_fee_usd, insurance_usd, exchange_rate):
        """
        Calculate the total cost including tuition, rent, visa, and insurance for the entire duration.
        
        Parameters:
        -----------
        [same as get_estimated_cost]
            
        Returns:
        --------
        dict
            Dictionary containing tuition cost, living expenses, and total cost
        """
        # Get estimated tuition cost
        tuition = self.get_estimated_cost(
            country, city, university, program, level, 
            duration_years, living_cost_index, rent_usd, 
            visa_fee_usd, insurance_usd, exchange_rate
        )
        
        # Calculate living expenses for the entire duration
        monthly_rent = rent_usd
        annual_insurance = insurance_usd
        
        # Calculate total living cost for the entire program duration
        living_expenses = (monthly_rent * 12 * duration_years) + (annual_insurance * duration_years) + visa_fee_usd
        
        # Calculate total cost
        total_cost = tuition + living_expenses
        
        return {
            'estimated_tuition_usd': round(tuition, 2),
            'living_expenses_usd': round(living_expenses, 2),
            'total_cost_usd': round(total_cost, 2)
        }


# Example usage
if __name__ == "__main__":
    # Initialize the predictor
    try:
        predictor = InternationalEducationPredictor()
        
        # Example: Predict cost for studying at MIT
        cost = predictor.get_total_cost(
            country="USA",
            city="Boston",
            university="MIT",
            program="Computer Science",
            level="Master",
            duration_years=2,
            living_cost_index=83.2,
            rent_usd=2200,
            visa_fee_usd=160,
            insurance_usd=1500,
            exchange_rate=1.0
        )
        
        print(f"Estimated Tuition: ${cost['estimated_tuition_usd']:,.2f}")
        print(f"Living Expenses: ${cost['living_expenses_usd']:,.2f}")
        print(f"Total Cost: ${cost['total_cost_usd']:,.2f}")
        
        # Example: Batch prediction
        sample_data = pd.DataFrame([
            {
                'Country': 'UK', 'City': 'London', 'University': 'Imperial College London',
                'Program': 'Data Science', 'Level': 'Master', 'Duration_Years': 1,
                'Living_Cost_Index': 75.8, 'Rent_USD': 1800, 'Visa_Fee_USD': 485,
                'Insurance_USD': 800, 'Exchange_Rate': 0.79
            },
            {
                'Country': 'Germany', 'City': 'Munich', 'University': 'Technical University of Munich',
                'Program': 'Computer Science', 'Level': 'Master', 'Duration_Years': 2,
                'Living_Cost_Index': 70.5, 'Rent_USD': 1100, 'Visa_Fee_USD': 75,
                'Insurance_USD': 550, 'Exchange_Rate': 0.92
            }
        ])
        
        batch_predictions = predictor.predict(sample_data)
        print("\nBatch Predictions:")
        for i, pred in enumerate(batch_predictions):
            print(f"  Program {i+1}: ${pred:,.2f}")
            
    except Exception as e:
        print(f"Error: {str(e)}") 