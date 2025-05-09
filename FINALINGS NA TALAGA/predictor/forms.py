from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import pandas as pd
import os
from django.conf import settings

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

def get_csv_choices(field_name):
    """Get unique values from the CSV file for dropdown choices"""
    csv_path = os.path.join(settings.BASE_DIR, 'model and data', 'International_Education_Costs.csv')
    try:
        df = pd.read_csv(csv_path)
        # Get unique values and sort them
        unique_values = sorted(df[field_name].unique())
        # Convert to choice tuples (value, label)
        choices = [(str(val), str(val)) for val in unique_values]
        return choices
    except Exception as e:
        print(f"Error loading choices from CSV: {e}")
        return []

def get_filtered_choices(field_name, filters=None):
    """Get choices filtered by other field values"""
    csv_path = os.path.join(settings.BASE_DIR, 'model and data', 'International_Education_Costs.csv')
    try:
        df = pd.read_csv(csv_path)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if value:
                    df = df[df[key] == value]
        
        # Get unique values and sort them
        unique_values = sorted(df[field_name].unique())
        # Convert to choice tuples (value, label)
        choices = [(str(val), str(val)) for val in unique_values]
        return choices
    except Exception as e:
        print(f"Error loading filtered choices from CSV: {e}")
        return []

class EducationCostPredictionForm(forms.Form):
    # Load choices from CSV
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set choices for all dropdown fields from CSV
        self.fields['country'].choices = get_csv_choices('Country')
        self.fields['city'].choices = [('', '-- Select Country First --')]
        self.fields['university'].choices = [('', '-- Select City First --')]
        self.fields['program'].choices = get_csv_choices('Program')
        self.fields['level'].choices = get_csv_choices('Level')
        self.fields['duration_years'].choices = get_csv_choices('Duration_Years')
        
        # Load choices for numeric fields
        self.fields['living_cost_index'].choices = [('', '-- Auto-filled --')] + get_csv_choices('Living_Cost_Index')
        self.fields['rent_usd'].choices = [('', '-- Auto-filled --')] + get_csv_choices('Rent_USD')
        self.fields['visa_fee_usd'].choices = [('', '-- Auto-filled --')] + get_csv_choices('Visa_Fee_USD')
        self.fields['insurance_usd'].choices = [('', '-- Auto-filled --')] + get_csv_choices('Insurance_USD')
        self.fields['exchange_rate'].choices = [('', '-- Auto-filled --')] + get_csv_choices('Exchange_Rate')
        
        # Option to use manual values 
        self.fields['use_manual_values'].initial = False
    
    # Country selection field
    country = forms.ChoiceField(required=True)
    
    # City field as dropdown
    city = forms.ChoiceField(required=True)
    
    # University field as dropdown
    university = forms.ChoiceField(required=True)
    
    # Program field
    program = forms.ChoiceField(required=True)
    other_program = forms.CharField(max_length=100, required=False, help_text="If you selected 'Other', please specify")
    
    # Level field
    level = forms.ChoiceField(required=True)
    
    # Duration in years as dropdown
    duration_years = forms.ChoiceField(required=True)
    
    # Toggle for manual entry vs dropdown selection
    use_manual_values = forms.BooleanField(
        required=False,
        label="Use manual values for costs and rates",
        help_text="Enable to manually enter values instead of using dropdown selections"
    )
    
    # Living Cost Index - converted to ChoiceField with fallback to FloatField
    living_cost_index = forms.ChoiceField(
        required=True,
        help_text="Living cost index (0-100 scale)"
    )
    living_cost_index_manual = forms.FloatField(
        min_value=0, 
        max_value=100, 
        required=False,
        help_text="Manual entry: Living cost index (0-100 scale)",
        widget=forms.NumberInput(attrs={'class': 'manual-entry'})
    )
    
    # Monthly rent in USD
    rent_usd = forms.ChoiceField(
        required=True, 
        help_text="Monthly rent in USD"
    )
    rent_usd_manual = forms.IntegerField(
        min_value=0, 
        required=False, 
        help_text="Manual entry: Monthly rent in USD",
        widget=forms.NumberInput(attrs={'class': 'manual-entry'})
    )
    
    # Visa fee in USD
    visa_fee_usd = forms.ChoiceField(
        required=True, 
        help_text="Visa fee in USD"
    )
    visa_fee_usd_manual = forms.IntegerField(
        min_value=0, 
        required=False, 
        help_text="Manual entry: Visa fee in USD",
        widget=forms.NumberInput(attrs={'class': 'manual-entry'})
    )
    
    # Annual insurance in USD
    insurance_usd = forms.ChoiceField(
        required=True, 
        help_text="Annual insurance cost in USD"
    )
    insurance_usd_manual = forms.IntegerField(
        min_value=0, 
        required=False, 
        help_text="Manual entry: Annual insurance cost in USD",
        widget=forms.NumberInput(attrs={'class': 'manual-entry'})
    )
    
    # Exchange rate to USD
    exchange_rate = forms.ChoiceField(
        required=True,
        help_text="Exchange rate to USD (e.g., 0.85 for EUR, 1.35 for CAD)"
    )
    exchange_rate_manual = forms.FloatField(
        min_value=0.001, 
        required=False,
        help_text="Manual entry: Exchange rate to USD",
        widget=forms.NumberInput(attrs={'class': 'manual-entry'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get('country')
        city = cleaned_data.get('city')
        university = cleaned_data.get('university')
        program = cleaned_data.get('program')
        other_program = cleaned_data.get('other_program')
        use_manual = cleaned_data.get('use_manual_values')
        
        # Update the city choices based on the selected country
        if country:
            self.fields['city'].choices = get_filtered_choices('City', {'Country': country})
            
            # Update the university choices based on the selected country and city
            if city:
                self.fields['university'].choices = get_filtered_choices('University', 
                                                  {'Country': country, 'City': city})
        
        # Now validate the city and university fields with the updated choices
        if city and city not in [choice[0] for choice in self.fields['city'].choices]:
            self.add_error('city', f"Select a valid choice. {city} is not one of the available choices.")
            
        if university and university not in [choice[0] for choice in self.fields['university'].choices]:
            self.add_error('university', f"Select a valid choice. {university} is not one of the available choices.")
        
        if program == 'Other' and not other_program:
            self.add_error('other_program', 'Please specify the program when selecting "Other"')
            
        # If using manual values, validate those fields
        if use_manual:
            living_cost_manual = cleaned_data.get('living_cost_index_manual')
            rent_manual = cleaned_data.get('rent_usd_manual')
            visa_manual = cleaned_data.get('visa_fee_usd_manual')
            insurance_manual = cleaned_data.get('insurance_usd_manual')
            exchange_manual = cleaned_data.get('exchange_rate_manual')
            
            if living_cost_manual is None:
                self.add_error('living_cost_index_manual', 'This field is required when using manual values')
            if rent_manual is None:
                self.add_error('rent_usd_manual', 'This field is required when using manual values')
            if visa_manual is None:
                self.add_error('visa_fee_usd_manual', 'This field is required when using manual values')
            if insurance_manual is None:
                self.add_error('insurance_usd_manual', 'This field is required when using manual values')
            if exchange_manual is None:
                self.add_error('exchange_rate_manual', 'This field is required when using manual values')
                
            # Update the main fields with manual values for prediction
            if living_cost_manual is not None:
                cleaned_data['living_cost_index'] = living_cost_manual
            if rent_manual is not None:
                cleaned_data['rent_usd'] = rent_manual
            if visa_manual is not None:
                cleaned_data['visa_fee_usd'] = visa_manual
            if insurance_manual is not None:
                cleaned_data['insurance_usd'] = insurance_manual
            if exchange_manual is not None:
                cleaned_data['exchange_rate'] = exchange_manual
        
        return cleaned_data 