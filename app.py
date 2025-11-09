import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Custom CSS and JS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def local_js(file_name):
    with open(file_name) as f:
        st.markdown(f'<script>{f.read()}</script>', unsafe_allow_html=True)

# Set page configuration
st.set_page_config(
    page_title="Netflix Data Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS and JS
local_css("assets/style.css")
local_js("assets/custom.js")

# App title and description
st.markdown("""
<div class="main-header">
    <h1>🎬 Netflix Content Analysis Dashboard</h1>
    <p class="subtitle">Exploring trends, genres, ratings, and global availability of Netflix content</p>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("netflix_titles.csv")
        # Data cleaning
        df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
        df['year_added'] = df['date_added'].dt.year
        df['month_added'] = df['date_added'].dt.month
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
        
        # Handle missing values
        df['country'] = df['country'].fillna('Unknown')
        df['rating'] = df['rating'].fillna('Not Rated')
        df['duration'] = df['duration'].fillna('Unknown')
        
        return df
    except FileNotFoundError:
        st.error("❌ netflix_titles.csv file not found. Please ensure the file is in the same directory.")
        return pd.DataFrame()

# Load the data
df = load_data()

if df.empty:
    st.stop()

# Sidebar
st.sidebar.markdown("""
<div class="sidebar-header">
    <h3>🔍 Filters</h3>
</div>
""", unsafe_allow_html=True)

# Filters
st.sidebar.markdown("### Content Type")
content_type = st.sidebar.multiselect(
    "Select content type:",
    options=df['type'].unique(),
    default=df['type'].unique()
)

st.sidebar.markdown("### Rating")
ratings = st.sidebar.multiselect(
    "Select ratings:",
    options=df['rating'].unique(),
    default=df['rating'].unique()
)

st.sidebar.markdown("### Release Year Range")
year_range = st.sidebar.slider(
    "Select release year range:",
    min_value=int(df['release_year'].min()),
    max_value=int(df['release_year'].max()),
    value=(2010, 2021)
)

# Apply filters
filtered_df = df[
    (df['type'].isin(content_type)) &
    (df['rating'].isin(ratings)) &
    (df['release_year'] >= year_range[0]) &
    (df['release_year'] <= year_range[1])
]

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Content", len(filtered_df))
with col2:
    st.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
with col3:
    st.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))
with col4:
    latest_year = filtered_df['release_year'].max()
    st.metric("Latest Release Year", int(latest_year) if not pd.isna(latest_year) else "N/A")

# Tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "🎭 Genres & Categories", 
    "🌍 Geographical Analysis", 
    "📈 Trends Over Time", 
    "🔍 Detailed Analysis"
])

with tab1:
    st.markdown("### Content Distribution Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Content type distribution
        type_counts = filtered_df['type'].value_counts()
        fig_type = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Content Type Distribution",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        # Rating distribution
        rating_counts = filtered_df['rating'].value_counts().head(10)
        fig_rating = px.bar(
            x=rating_counts.values,
            y=rating_counts.index,
            title="Top 10 Content Ratings",
            orientation='h',
            color=rating_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_rating.update_layout(xaxis_title="Count", yaxis_title="Rating")
        st.plotly_chart(fig_rating, use_container_width=True)
    
    # New: Donut chart for content over decades
    st.markdown("### Content Distribution by Decades")
    
    # Create decades
    filtered_df['decade'] = (filtered_df['release_year'] // 10) * 10
    decade_counts = filtered_df['decade'].value_counts().sort_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_decade = px.pie(
            values=decade_counts.values,
            names=decade_counts.index.astype(int),
            title="Content Distribution by Decades",
            hole=0.4
        )
        fig_decade.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_decade, use_container_width=True)
    
    with col2:
        # Stacked bar chart for type distribution by decade
        decade_type = pd.crosstab(filtered_df['decade'], filtered_df['type'])
        fig_decade_type = px.bar(
            decade_type,
            x=decade_type.index,
            y=decade_type.columns,
            title="Content Type Distribution by Decades",
            barmode='stack'
        )
        fig_decade_type.update_layout(xaxis_title="Decade", yaxis_title="Count")
        st.plotly_chart(fig_decade_type, use_container_width=True)
    
    # Duration analysis
    st.markdown("### Duration Analysis")
    
    # Separate movies and TV shows for duration analysis
    movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
    tv_shows_df = filtered_df[filtered_df['type'] == 'TV Show'].copy()
    
    # Extract duration for movies
    movies_df['duration_min'] = movies_df['duration'].str.extract('(\d+)').astype(float)
    
    # Extract seasons for TV shows
    tv_shows_df['seasons'] = tv_shows_df['duration'].str.extract('(\d+)').astype(float)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not movies_df.empty and 'duration_min' in movies_df.columns:
            fig_movie_duration = px.histogram(
                movies_df, 
                x='duration_min',
                title="Movie Duration Distribution (minutes)",
                nbins=30,
                color_discrete_sequence=['#E50914']
            )
            fig_movie_duration.update_layout(xaxis_title="Duration (minutes)", yaxis_title="Count")
            st.plotly_chart(fig_movie_duration, use_container_width=True)
    
    with col2:
        if not tv_shows_df.empty and 'seasons' in tv_shows_df.columns:
            season_counts = tv_shows_df['seasons'].value_counts().sort_index().head(15)
            fig_tv_seasons = px.bar(
                x=season_counts.index,
                y=season_counts.values,
                title="TV Shows by Number of Seasons",
                color=season_counts.values,
                color_continuous_scale='Plasma'
            )
            fig_tv_seasons.update_layout(xaxis_title="Number of Seasons", yaxis_title="Count")
            st.plotly_chart(fig_tv_seasons, use_container_width=True)

with tab2:
    st.markdown("### Genre Analysis")
    
    # Genre analysis
    all_genres = []
    for genres in filtered_df['listed_in'].dropna():
        all_genres.extend([genre.strip() for genre in genres.split(',')])
    
    genre_counts = pd.Series(all_genres).value_counts().head(15)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_genres = px.bar(
            x=genre_counts.values,
            y=genre_counts.index,
            title="Top 15 Genres/Categories",
            orientation='h',
            color=genre_counts.values,
            color_continuous_scale='Teal'
        )
        fig_genres.update_layout(xaxis_title="Count", yaxis_title="Genre")
        st.plotly_chart(fig_genres, use_container_width=True)
    
    with col2:
        # Genre treemap
        fig_genre_treemap = px.treemap(
            names=genre_counts.index,
            parents=[''] * len(genre_counts),
            values=genre_counts.values,
            title="Genre Distribution (Treemap)"
        )
        st.plotly_chart(fig_genre_treemap, use_container_width=True)
    
    # New: Genre over time
    st.markdown("### Genre Trends Over Time")
    
    # Extract genres and create genre-time analysis
    genre_time_data = []
    for idx, row in filtered_df.iterrows():
        if pd.notna(row['listed_in']):
            genres = [genre.strip() for genre in row['listed_in'].split(',')]
            for genre in genres:
                if genre in genre_counts.head(8).index:  # Top 8 genres
                    genre_time_data.append({
                        'genre': genre,
                        'release_year': row['release_year'],
                        'type': row['type']
                    })
    
    genre_time_df = pd.DataFrame(genre_time_data)
    
    if not genre_time_df.empty:
        genre_year_counts = genre_time_df.groupby(['release_year', 'genre']).size().reset_index(name='count')
        
        fig_genre_trend = px.line(
            genre_year_counts,
            x='release_year',
            y='count',
            color='genre',
            title="Top Genre Trends Over Time",
            markers=True
        )
        fig_genre_trend.update_layout(xaxis_title="Release Year", yaxis_title="Number of Titles")
        st.plotly_chart(fig_genre_trend, use_container_width=True)
    
    # Director and Cast analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Director analysis
        all_directors = []
        for directors in filtered_df['director'].dropna():
            all_directors.extend([director.strip() for director in directors.split(',')])
        
        director_counts = pd.Series(all_directors).value_counts().head(10)
        
        fig_directors = px.bar(
            x=director_counts.values,
            y=director_counts.index,
            title="Top 10 Directors",
            orientation='h',
            color=director_counts.values,
            color_continuous_scale='Rainbow'
        )
        fig_directors.update_layout(xaxis_title="Number of Titles", yaxis_title="Director")
        st.plotly_chart(fig_directors, use_container_width=True)
    
    with col2:
        # Cast analysis
        all_cast = []
        for cast in filtered_df['cast'].dropna():
            all_cast.extend([actor.strip() for actor in cast.split(',')])
        
        cast_counts = pd.Series(all_cast).value_counts().head(10)
        
        fig_cast = px.bar(
            x=cast_counts.values,
            y=cast_counts.index,
            title="Top 10 Actors/Actresses",
            orientation='h',
            color=cast_counts.values,
            color_continuous_scale='Rainbow'
        )
        fig_cast.update_layout(xaxis_title="Number of Appearances", yaxis_title="Actor/Actress")
        st.plotly_chart(fig_cast, use_container_width=True)

with tab3:
    st.markdown("### Geographical Distribution")
    
    # Country analysis
    all_countries = []
    for countries in filtered_df['country'].dropna():
        if countries != 'Unknown':
            all_countries.extend([country.strip() for country in countries.split(',')])
    
    country_counts = pd.Series(all_countries).value_counts().head(20)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_countries = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            title="Top 20 Countries by Content Production",
            orientation='h',
            color=country_counts.values,
            color_continuous_scale='Earth'
        )
        fig_countries.update_layout(xaxis_title="Count", yaxis_title="Country")
        st.plotly_chart(fig_countries, use_container_width=True)
    
    with col2:
        # World map visualization
        country_df = pd.DataFrame({
            'country': country_counts.index,
            'count': country_counts.values
        })
        
        # Simple choropleth
        try:
            fig_world = px.choropleth(
                country_df,
                locations='country',
                locationmode='country names',
                color='count',
                title="Content Production by Country",
                color_continuous_scale='Blues',
                hover_name='country',
                hover_data={'count': True}
            )
            fig_world.update_layout(geo=dict(showframe=False, showcoastlines=False))
            st.plotly_chart(fig_world, use_container_width=True)
        except Exception as e:
            st.info("Map visualization might not display correctly for some country names.")
    
    # New: Bubble chart for country vs rating
    st.markdown("### Country vs Rating Analysis")
    
    # Prepare data for bubble chart
    country_rating_data = []
    for country in country_counts.head(15).index:
        country_data = filtered_df[filtered_df['country'].str.contains(country, na=False)]
        rating_counts_country = country_data['rating'].value_counts().head(5)
        for rating, count in rating_counts_country.items():
            country_rating_data.append({
                'country': country,
                'rating': rating,
                'count': count
            })
    
    if country_rating_data:
        country_rating_df = pd.DataFrame(country_rating_data)
        
        fig_bubble = px.scatter(
            country_rating_df,
            x='country',
            y='rating',
            size='count',
            color='count',
            title="Rating Distribution by Country (Bubble Chart)",
            size_max=50,
            color_continuous_scale='Viridis'
        )
        fig_bubble.update_layout(xaxis_title="Country", yaxis_title="Rating")
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Content by country and type
    st.markdown("### Content Type Distribution by Top Countries")
    top_countries = country_counts.head(10).index
    country_type_data = []
    
    for country in top_countries:
        country_data = filtered_df[filtered_df['country'].str.contains(country, na=False)]
        movies_count = len(country_data[country_data['type'] == 'Movie'])
        tv_count = len(country_data[country_data['type'] == 'TV Show'])
        country_type_data.append({'country': country, 'Movies': movies_count, 'TV Shows': tv_count})
    
    country_type_df = pd.DataFrame(country_type_data)
    country_type_df = country_type_df.melt(id_vars=['country'], var_name='Type', value_name='Count')
    
    fig_country_type = px.bar(
        country_type_df,
        x='country',
        y='Count',
        color='Type',
        title="Movies vs TV Shows in Top 10 Countries",
        barmode='group',
        color_discrete_map={'Movies': '#E50914', 'TV Shows': '#221F1F'}
    )
    st.plotly_chart(fig_country_type, use_container_width=True)

with tab4:
    st.markdown("### Trends Over Time")
    
    # Release trends
    yearly_releases = filtered_df['release_year'].value_counts().sort_index()
    yearly_releases = yearly_releases[yearly_releases.index >= 1990]  # Focus on recent decades
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_yearly = px.line(
            x=yearly_releases.index,
            y=yearly_releases.values,
            title="Content Release Trend Over Years",
            markers=True
        )
        fig_yearly.update_layout(xaxis_title="Release Year", yaxis_title="Number of Titles")
        fig_yearly.update_traces(line=dict(color='#E50914', width=3))
        st.plotly_chart(fig_yearly, use_container_width=True)
    
    with col2:
        # Content added to Netflix over time
        if 'year_added' in filtered_df.columns:
            yearly_added = filtered_df['year_added'].value_counts().sort_index()
            fig_added = px.area(
                x=yearly_added.index,
                y=yearly_added.values,
                title="Content Added to Netflix Over Time"
            )
            fig_added.update_layout(xaxis_title="Year Added", yaxis_title="Number of Titles")
            fig_added.update_traces(fillcolor='rgba(229, 9, 20, 0.3)', line=dict(color='#E50914'))
            st.plotly_chart(fig_added, use_container_width=True)
    
    # New: Heatmap for monthly additions
    st.markdown("### Monthly Addition Patterns")
    
    if all(col in filtered_df.columns for col in ['year_added', 'month_added']):
        # Create heatmap data
        heatmap_data = filtered_df.groupby(['year_added', 'month_added']).size().reset_index(name='count')
        heatmap_pivot = heatmap_data.pivot(index='month_added', columns='year_added', values='count').fillna(0)
        
        fig_heatmap = px.imshow(
            heatmap_pivot,
            title="Monthly Content Additions Heatmap",
            color_continuous_scale='Reds',
            aspect='auto'
        )
        fig_heatmap.update_layout(xaxis_title="Year", yaxis_title="Month")
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Monthly analysis
    st.markdown("### Monthly Distribution")
    
    if 'month_added' in filtered_df.columns:
        monthly_added = filtered_df['month_added'].value_counts().sort_index()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        monthly_data = pd.DataFrame({
            'month': month_names,
            'count': [monthly_added.get(i, 0) for i in range(1, 13)]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_monthly = px.bar(
                monthly_data,
                x='month',
                y='count',
                title="Content Added by Month",
                color='count',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            # Polar chart for monthly distribution
            fig_polar = px.line_polar(
                monthly_data, 
                r='count', 
                theta='month', 
                line_close=True,
                title="Monthly Distribution (Polar Chart)"
            )
            fig_polar.update_traces(fill='toself')
            st.plotly_chart(fig_polar, use_container_width=True)

with tab5:
    st.markdown("### Detailed Data Exploration")
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🔍 Search titles:", placeholder="Enter title, director, or cast...")
    
    with col2:
        selected_genre = st.selectbox("Filter by genre:", ["All"] + list(df['listed_in'].str.split(',').explode().str.strip().unique())[:50])
    
    with col3:
        selected_country = st.selectbox("Filter by country:", ["All"] + list(df['country'].str.split(',').explode().str.strip().unique())[:50])
    
    # Apply search filter
    detailed_df = filtered_df.copy()
    if search_query:
        detailed_df = detailed_df[
            detailed_df['title'].str.contains(search_query, case=False, na=False) |
            detailed_df['director'].str.contains(search_query, case=False, na=False) |
            detailed_df['cast'].str.contains(search_query, case=False, na=False)
        ]
    
    if selected_genre != "All":
        detailed_df = detailed_df[detailed_df['listed_in'].str.contains(selected_genre, na=False)]
    
    if selected_country != "All":
        detailed_df = detailed_df[detailed_df['country'].str.contains(selected_country, na=False)]
    
    # Show statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Filtered Results", len(detailed_df))
    with col2:
        st.metric("Average Release Year", int(detailed_df['release_year'].mean()) if not detailed_df.empty else 0)
    with col3:
        st.metric("Movies", len(detailed_df[detailed_df['type'] == 'Movie']))
    with col4:
        st.metric("TV Shows", len(detailed_df[detailed_df['type'] == 'TV Show']))
    
    # Show detailed data
    st.markdown(f"**Displaying {len(detailed_df)} titles**")
    
    # Display as expandable cards
    for idx, row in detailed_df.head(100).iterrows():
        with st.expander(f"🎬 {row['title']} ({row['release_year']}) - {row['type']}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Type:** {row['type']}")
                if row['type'] == 'Movie':
                    st.markdown(f"**Duration:** {row['duration']}")
                else:
                    st.markdown(f"**Seasons:** {row['duration']}")
                st.markdown(f"**Rating:** {row['rating']}")
                st.markdown(f"**Release Year:** {row['release_year']}")
                if pd.notna(row['date_added']):
                    st.markdown(f"**Added on:** {row['date_added'].strftime('%Y-%m-%d')}")
            
            with col2:
                st.markdown(f"**Country:** {row['country']}")
                if pd.notna(row['director']) and row['director'] != 'Unknown':
                    st.markdown(f"**Director:** {row['director']}")
                if pd.notna(row['cast']) and row['cast'] != 'Unknown':
                    st.markdown(f"**Cast:** {row['cast'][:200]}...")
                st.markdown(f"**Genre:** {row['listed_in']}")
                if pd.notna(row['description']):
                    st.markdown(f"**Description:** {row['description']}")

# Footer
st.markdown("""
<div class="footer">
    <p>Netflix Data Analysis Dashboard | Created with Streamlit | Data Source: Kaggle Netflix Dataset</p>
</div>
""", unsafe_allow_html=True)