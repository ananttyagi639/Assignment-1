import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection
DATABASE_URI = 'mysql+mysqlconnector://root:root@localhost/your_database'
engine = create_engine(DATABASE_URI)

# Streamlit app
st.title('Redbus Data Filtering Application')

# Sidebar filters
st.sidebar.header('Filters')

# Fetch dynamic options for routes, bus types, and star ratings range from the database
with engine.connect() as conn:
    # Fetch distinct routes
    route_query = "SELECT DISTINCT route_name FROM redbus_data"
    routes_df = pd.read_sql(route_query, conn)
    route_options = routes_df['route_name'].tolist()

    # Fetch distinct bus types
    bus_type_query = "SELECT DISTINCT bus_type FROM redbus_data"
    bus_type_df = pd.read_sql(bus_type_query, conn)
    bus_type_options = bus_type_df['bus_type'].tolist()

    # Fetch star rating range
    star_rating_range_query = "SELECT MIN(star_rating) as min_rating, MAX(star_rating) as max_rating FROM redbus_data"
    star_rating_range_df = pd.read_sql(star_rating_range_query, conn)
    min_star_rating = star_rating_range_df['min_rating'][0]
    max_star_rating = star_rating_range_df['max_rating'][0]

# Bus type filter (dynamically fetched from the database)
bus_types = st.sidebar.multiselect('Select Bus Types', options=bus_type_options)

# Route filter (dynamically fetched from the database)
routes = st.sidebar.multiselect('Select Routes', options=route_options)

# Star rating range filter (dynamically fetched from the data)
star_rating_range = st.sidebar.slider('Select Star Rating Range', min_value=min_star_rating, max_value=max_star_rating, value=(min_star_rating, max_star_rating))

# Price range filter
price_range = st.sidebar.slider('Price Range', min_value=0, max_value=10000, value=(0, 10000))

# Seat availability range filter
seat_availability_range = st.sidebar.slider('Select Seat Availability Range', min_value=0, max_value=100, value=(0, 100))

# Search button
search_button = st.sidebar.button('Search')

# Create SQL filters based on user input
if search_button:  # Only execute query when the Search button is clicked
    if routes:
        route_filter = f"AND LOWER(TRIM(route_name)) IN ({', '.join(f'LOWER(TRIM(\'{r}\'))' for r in routes)})"
    else:
        route_filter = ""

    if bus_types:
        bus_type_filter = f"AND LOWER(TRIM(bus_type)) IN ({', '.join(f'LOWER(TRIM(\'{b}\'))' for b in bus_types)})"
    else:
        bus_type_filter = ""

    star_rating_filter = f"AND star_rating BETWEEN {star_rating_range[0]} AND {star_rating_range[1]}"

    price_filter = f"AND price BETWEEN {price_range[0]} AND {price_range[1]}"
    
    seat_availability_filter = f"AND seat_availability BETWEEN {seat_availability_range[0]} AND {seat_availability_range[1]}"

    # Create SQL query based on filters
    query = f"""
    SELECT *
    FROM redbus_data
    WHERE 1=1
    {bus_type_filter}
    {route_filter}
    {price_filter}
    {star_rating_filter}
    {seat_availability_filter}
    """

    # Execute query and load data into a DataFrame
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)

    # Check if data is empty
    if data.empty:
        st.write("No buses found for the selected filters.")
    else:
        # Display the filtered data
        st.write('Filtered Data')
        st.dataframe(data)

        # Optional: Display statistics or visualizations
       # st.subheader('Data Statistics')
        #st.write(data.describe())