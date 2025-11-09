import pandas as pd
import numpy as np
from datetime import datetime

def clean_netflix_data(df):
    """
    Clean and preprocess Netflix dataset
    """
    # Make a copy to avoid modifying original
    df_clean = df.copy()
    
    # Handle date columns
    df_clean['date_added'] = pd.to_datetime(df_clean['date_added'], errors='coerce')
    df_clean['year_added'] = df_clean['date_added'].dt.year
    df_clean['month_added'] = df_clean['date_added'].dt.month
    
    # Handle numeric columns
    df_clean['release_year'] = pd.to_numeric(df_clean['release_year'], errors='coerce')
    
    # Fill missing values
    df_clean['country'] = df_clean['country'].fillna('Unknown')
    df_clean['rating'] = df_clean['rating'].fillna('Not Rated')
    df_clean['duration'] = df_clean['duration'].fillna('Unknown')
    df_clean['director'] = df_clean['director'].fillna('Unknown')
    df_clean['cast'] = df_clean['cast'].fillna('Unknown')
    
    return df_clean

def extract_top_items(series, top_n=10, sep=','):
    """
    Extract top items from a series containing comma-separated values
    """
    all_items = []
    for items in series.dropna():
        if sep in str(items):
            all_items.extend([item.strip() for item in str(items).split(sep)])
        else:
            all_items.append(str(items).strip())
    
    return pd.Series(all_items).value_counts().head(top_n)

def calculate_content_trends(df, year_col='release_year'):
    """
    Calculate content release trends over years
    """
    yearly_trends = df[year_col].value_counts().sort_index()
    return yearly_trends

def get_country_stats(df, country_col='country'):
    """
    Get statistics by country
    """
    country_stats = {}
    all_countries = []
    
    for countries in df[country_col].dropna():
        if ',' in str(countries):
            all_countries.extend([country.strip() for country in str(countries).split(',')])
        else:
            all_countries.append(str(countries).strip())
    
    country_series = pd.Series(all_countries)
    country_stats['counts'] = country_series.value_counts()
    country_stats['total_unique'] = country_series.nunique()
    
    return country_stats

def create_summary_stats(df):
    """
    Create summary statistics for the dataset
    """
    stats = {
        'total_titles': len(df),
        'movies_count': len(df[df['type'] == 'Movie']),
        'tv_shows_count': len(df[df['type'] == 'TV Show']),
        'earliest_release': df['release_year'].min(),
        'latest_release': df['release_year'].max(),
        'unique_countries': df['country'].nunique(),
        'unique_directors': df['director'].nunique(),
        'most_common_rating': df['rating'].mode().iloc[0] if not df['rating'].mode().empty else 'N/A'
    }
    
    return stats