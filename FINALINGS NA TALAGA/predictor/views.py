import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import base64
from io import BytesIO
import numpy as np

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse

from .forms import UserRegistrationForm, EducationCostPredictionForm, get_filtered_choices
from .ml_model import EducationCostPredictor

# Constants
CSV_PATH = os.path.join(settings.BASE_DIR, 'model and data', 'International_Education_Costs.csv')

def home(request):
    """Home page view."""
    return render(request, 'predictor/home.html')

def signup(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'predictor/signup.html', {'form': form})

@login_required
def predict(request):
    """Prediction view."""
    prediction_result = None
    
    if request.method == 'POST':
        # Get the form data
        post_data = request.POST.copy()
        
        # If the form is going to be invalid because of city/university not being in choices,
        # update the form choices before validation
        if 'country' in post_data and post_data.get('country'):
            country = post_data.get('country')
            city = post_data.get('city')
            
            # Pre-populate the form with the city choices based on the country
            form = EducationCostPredictionForm(post_data)
            form.fields['city'].choices = get_filtered_choices('City', {'Country': country}) 
            
            # If city is provided, update university choices based on country and city
            if city:
                form.fields['university'].choices = get_filtered_choices('University', 
                                                    {'Country': country, 'City': city})
                
                # If university is provided, update program choices
                university = post_data.get('university')
                if university:
                    form.fields['program'].choices = get_filtered_choices('Program', 
                                                     {'Country': country, 'City': city, 'University': university})
        else:
            form = EducationCostPredictionForm(post_data)
        
        if form.is_valid():
            # Get form data
            data = form.cleaned_data
            
            # Check if using manual values
            if data.get('use_manual_values'):
                # Replace values with manual entries
                data['living_cost_index'] = data.get('living_cost_index_manual')
                data['rent_usd'] = data.get('rent_usd_manual')
                data['visa_fee_usd'] = data.get('visa_fee_usd_manual')
                data['insurance_usd'] = data.get('insurance_usd_manual')
                data['exchange_rate'] = data.get('exchange_rate_manual')
            
            # Initialize predictor and make prediction
            predictor = EducationCostPredictor()
            prediction_result = predictor.predict(data)
            
            if 'error' in prediction_result:
                messages.error(request, f"Prediction Error: {prediction_result['error']}")
                prediction_result = None
        else:
            # If form validation failed, log the errors for debugging
            print(f"Form errors: {form.errors}")
    else:
        form = EducationCostPredictionForm()
    
    return render(request, 'predictor/predict.html', {
        'form': form,
        'prediction_result': prediction_result
    })

@login_required
def dashboard(request):
    """Dashboard view showing model information and statistics."""
    predictor = EducationCostPredictor()
    model_info = predictor.get_model_info()
    dataset_stats = predictor.get_sample_data_stats()
    
    # Generate visualizations
    visualizations = generate_visualizations(dataset_stats)
    
    # Add additional statistics for popular programs
    try:
        df = pd.read_csv(CSV_PATH)
        
        # Get top programs by popularity
        popular_programs = df['Program'].value_counts().head(5).to_dict()
        
        # Get average living costs by country
        avg_living_costs = df.groupby('Country')[['Living_Cost_Index', 'Rent_USD']].mean().sort_values(by='Living_Cost_Index', ascending=False).head(5).to_dict()
        
        # Add new statistics to context
        additional_stats = {
            'popular_programs': popular_programs,
            'avg_living_costs': avg_living_costs
        }
    except Exception as e:
        print(f"Error generating additional stats: {str(e)}")
        additional_stats = {}
    
    context = {
        'model_info': model_info,
        'dataset_stats': dataset_stats,
        'visualizations': visualizations,
        'additional_stats': additional_stats
    }
    
    return render(request, 'predictor/dashboard.html', context)

def generate_visualizations(stats):
    """Generate visualization charts for the dashboard."""
    visualizations = {}
    
    try:
        # 1. Top Countries Bar Chart
        countries_data = stats.get('countries_distribution', {})
        if countries_data:
            fig = Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            countries = list(countries_data.keys())[:8]  # Top 8 countries
            counts = [countries_data[country] for country in countries]
            ax.bar(countries, counts, color='skyblue')
            ax.set_title('Most Common Countries in Dataset')
            ax.set_ylabel('Number of Programs')
            ax.tick_params(axis='x', rotation=45)
            fig.tight_layout()
            
            # Convert plot to base64 string
            buf = BytesIO()
            FigureCanvas(fig).print_png(buf)
            visualizations['countries_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # 2. Education Levels Pie Chart
        levels_data = stats.get('levels_distribution', {})
        if levels_data:
            fig = Figure(figsize=(8, 8))
            ax = fig.add_subplot(111)
            labels = list(levels_data.keys())
            sizes = list(levels_data.values())
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                   shadow=True, explode=[0.1 if l == max(labels, key=levels_data.get) else 0 for l in labels])
            ax.axis('equal')
            ax.set_title('Distribution of Education Levels')
            fig.tight_layout()
            
            # Convert plot to base64 string
            buf = BytesIO()
            FigureCanvas(fig).print_png(buf)
            visualizations['levels_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # 3. Tuition by Level Bar Chart
        tuition_data = stats.get('tuition_by_level', {})
        if tuition_data:
            fig = Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            levels = list(tuition_data.keys())
            tuitions = [tuition_data[level] for level in levels]
            ax.bar(levels, tuitions, color='lightgreen')
            ax.set_title('Average Tuition by Education Level')
            ax.set_ylabel('Average Tuition (USD)')
            ax.tick_params(axis='x', rotation=45)
            
            # Add data labels on bars
            for i, v in enumerate(tuitions):
                ax.text(i, v + 500, f"${v:,.0f}", ha='center')
                
            fig.tight_layout()
            
            # Convert plot to base64 string
            buf = BytesIO()
            FigureCanvas(fig).print_png(buf)
            visualizations['tuition_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # 4. Cost Factors Breakdown (NEW)
        try:
            # Load the CSV to calculate cost factors
            df = pd.read_csv(CSV_PATH)
            
            # Calculate average costs by component
            avg_tuition = df['Tuition_USD'].mean()
            avg_rent = df['Rent_USD'].mean() * 12 * df['Duration_Years'].mean()  # Annual rent for average duration
            avg_insurance = df['Insurance_USD'].mean() * df['Duration_Years'].mean()  # Insurance for average duration
            avg_visa = df['Visa_Fee_USD'].mean()
            
            # Create pie chart of cost components
            fig = Figure(figsize=(8, 8))
            ax = fig.add_subplot(111)
            components = ['Tuition', 'Rent', 'Insurance', 'Visa Fee']
            values = [avg_tuition, avg_rent, avg_insurance, avg_visa]
            colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e']
            
            # Filter out components with very small values
            total = sum(values)
            labels = []
            filtered_values = []
            filtered_colors = []
            
            for i, (comp, val, color) in enumerate(zip(components, values, colors)):
                percentage = (val / total) * 100
                if percentage >= 1.0:  # Only include components that are at least 1% of total
                    labels.append(f"{comp} (${val:,.0f})")
                    filtered_values.append(val)
                    filtered_colors.append(color)
            
            wedges, texts, autotexts = ax.pie(
                filtered_values, 
                labels=None,  # We'll add custom legend instead
                autopct='%1.1f%%', 
                startangle=90, 
                colors=filtered_colors,
                shadow=False,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
                textprops={'fontsize': 12, 'fontweight': 'bold', 'color': 'white'}
            )
            
            # Add a legend
            ax.legend(
                wedges, 
                labels,
                title="Cost Components",
                loc="center left",
                bbox_to_anchor=(0.85, 0, 0.5, 1)
            )
            
            ax.axis('equal')
            ax.set_title('Average Education Cost Breakdown', fontsize=16, pad=20)
            fig.tight_layout()
            
            # Convert plot to base64 string
            buf = BytesIO()
            FigureCanvas(fig).print_png(buf)
            visualizations['cost_factors_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            # 5. Living Cost Index vs. Tuition Scatter Plot (NEW)
            fig = Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            
            # Filter out outliers for better visualization
            q_low = df['Tuition_USD'].quantile(0.01)
            q_high = df['Tuition_USD'].quantile(0.99)
            filtered_df = df[(df['Tuition_USD'] >= q_low) & (df['Tuition_USD'] <= q_high)]
            
            scatter = ax.scatter(
                filtered_df['Living_Cost_Index'], 
                filtered_df['Tuition_USD'], 
                alpha=0.6,
                c=filtered_df['Living_Cost_Index'],
                cmap='viridis',
                s=50
            )
            
            # Add a color bar using the figure's colorbar method
            cbar = fig.colorbar(scatter, ax=ax)
            cbar.set_label('Living Cost Index')
            
            # Add a trend line
            z = np.polyfit(filtered_df['Living_Cost_Index'], filtered_df['Tuition_USD'], 1)
            p = np.poly1d(z)
            x_range = np.linspace(filtered_df['Living_Cost_Index'].min(), filtered_df['Living_Cost_Index'].max(), 100)
            ax.plot(x_range, p(x_range), "r--", linewidth=2)
            
            ax.set_title('Relationship Between Living Cost Index and Tuition', fontsize=16)
            ax.set_xlabel('Living Cost Index', fontsize=12)
            ax.set_ylabel('Tuition (USD)', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Format y-axis with dollar signs
            from matplotlib.ticker import FuncFormatter
            def currency_formatter(x, pos):
                return '${:,.0f}'.format(x)
            ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
            
            fig.tight_layout()
            
            # Convert plot to base64 string
            buf = BytesIO()
            FigureCanvas(fig).print_png(buf)
            visualizations['cost_index_tuition_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"Error generating additional visualizations: {str(e)}")
            
    except Exception as e:
        print(f"Error generating visualizations: {str(e)}")
        
    return visualizations

# API endpoints for dynamic dropdown data
def education_data_api(request):
    """API endpoint to get all education data."""
    try:
        df = pd.read_csv(CSV_PATH)
        data = df.to_dict(orient='records')
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def cities_api(request):
    """API endpoint to get cities for a specific country."""
    try:
        country = request.GET.get('country', '')
        df = pd.read_csv(CSV_PATH)
        
        if country:
            cities = df[df['Country'] == country]['City'].unique().tolist()
        else:
            cities = df['City'].unique().tolist()
            
        return JsonResponse(sorted(cities), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def universities_api(request):
    """API endpoint to get universities for a specific country and city."""
    try:
        country = request.GET.get('country', '')
        city = request.GET.get('city', '')
        df = pd.read_csv(CSV_PATH)
        
        if country and city:
            universities = df[(df['Country'] == country) & (df['City'] == city)]['University'].unique().tolist()
        elif country:
            universities = df[df['Country'] == country]['University'].unique().tolist()
        else:
            universities = df['University'].unique().tolist()
            
        return JsonResponse(sorted(universities), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def university_data_api(request):
    """API endpoint to get data for a specific university."""
    try:
        country = request.GET.get('country', '')
        city = request.GET.get('city', '')
        university = request.GET.get('university', '')
        df = pd.read_csv(CSV_PATH)
        
        if country and city and university:
            university_data = df[(df['Country'] == country) & 
                                 (df['City'] == city) & 
                                 (df['University'] == university)].to_dict(orient='records')
        else:
            university_data = []
            
        return JsonResponse(university_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def programs_api(request):
    """API endpoint to get available programs for a specific university."""
    try:
        country = request.GET.get('country', '')
        city = request.GET.get('city', '')
        university = request.GET.get('university', '')
        df = pd.read_csv(CSV_PATH)
        
        if country and city and university:
            programs = df[(df['Country'] == country) & 
                          (df['City'] == city) & 
                          (df['University'] == university)]['Program'].unique().tolist()
        else:
            programs = df['Program'].unique().tolist()
            
        return JsonResponse(sorted(programs), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def program_details_api(request):
    """API endpoint to get details for a specific program at a university."""
    try:
        country = request.GET.get('country', '')
        city = request.GET.get('city', '')
        university = request.GET.get('university', '')
        program = request.GET.get('program', '')
        df = pd.read_csv(CSV_PATH)
        
        if country and city and university and program:
            program_data = df[(df['Country'] == country) & 
                             (df['City'] == city) & 
                             (df['University'] == university) &
                             (df['Program'] == program)].to_dict(orient='records')
        else:
            program_data = []
            
        return JsonResponse(program_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 