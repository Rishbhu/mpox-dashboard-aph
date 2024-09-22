import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Mpox Dashboard", layout="wide")

# Custom CSS for a colorful and vibrant theme
st.markdown(
    """
    <style>
    /* General body styling */
    body {
        background-color: #F0F8FF;  /* AliceBlue background for a soft, bright feel */
        font-family: 'Arial', sans-serif;  /* Clean, modern font */
        color: #333333;  /* Set all text color to dark gray */
    }
    /* Header styling */
    .header {
        background-color: #FF6347;  /* Tomato color for a vibrant header */
        color: #FFFFFF;  /* Set header text color to white */
        padding: 10px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    /* Navigation bar styling */
    .navbar {
        background-color: #4682B4;  /* SteelBlue for the navbar */
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .navbar a {
        color: #FFFFFF;  /* Set navigation link color to white */
        padding: 8px 15px;
        text-decoration: none;
        font-size: 18px;
    }
    .navbar a:hover {
        background-color: #FFA07A;  /* LightSalmon hover effect */
        color: #FFFFFF;  /* Keep hover text color white */
        border-radius: 5px;
    }
    /* Box and Panel styling */
    .stMarkdown {
        background-color: #FFFFFF;
        border: 2px solid #4682B4;  /* SteelBlue border */
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        color: #333333;  /* Ensure content box text is dark gray */
    }
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #F0F8FF;
        color: #333333;  /* Ensure sidebar text is dark gray */
    }
    /* Button styling */
    .stButton button {
        background-color: #4682B4;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #FFA07A;  /* LightSalmon hover effect */
    }
    /* Metric box styling */
    .stMetric {
        background-color: #FFFAF0;  /* FloralWhite background for metrics */
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 20px;
        text-align: center;
        color: #333333;  /* Ensure metric text is dark gray */
    }
    /* Enhanced keyword list styling */
    .keyword-box {
        background-color: #FFFFFF;
        border: 1px solid #4682B4;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        color: #333333;
        font-size: 16px;
    }
    .keyword-box h4 {
        color: #FF6347;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load and process the data
file_path = "Copy of Book1.csv.xlsx"
data = pd.read_excel(file_path)

# Load the new file
file_path_1 = "merged mpox data scraped.csv"  # Replace with the correct path or file name

# Use pandas to read the new data file
data_new_1 = pd.read_csv(file_path_1)

# Combine both datasets
combined_data = pd.concat([data, data_new_1])

# Helper function to get top 10 most frequent words for each year
def get_top_10_words_by_year(df):
    df['CreateDate'] = pd.to_datetime(df['CreateDate'], errors='coerce')
    df['Year'] = df['CreateDate'].dt.year

    # Explode words from 'CleanedText' column
    df['CleanedText'] = df['CleanedText'].fillna("").str.split()
    df = df.explode('CleanedText')

    # Group by year and get the top 10 words for each year
    top_words_per_year = (
        df.groupby(['Year', 'CleanedText'])
        .size()
        .reset_index(name='Count')
        .sort_values(by=['Year', 'Count'], ascending=[True, False])
        .groupby('Year')
        .head(10)
    )

    # Pivot table to get top words as columns
    top_words_table = top_words_per_year.pivot_table(
        index='Year', columns='CleanedText', values='Count', fill_value=0
    )

    return top_words_table

# Initialize session state
if 'show_filtered_data' not in st.session_state:
    st.session_state['show_filtered_data'] = False
if 'filtered_data' not in st.session_state:
    st.session_state['filtered_data'] = pd.DataFrame()

# Sidebar for Advanced Search
st.sidebar.markdown("## Advanced Search for Tweets")
with st.sidebar.form(key='advanced_search_form'):
    # Allow for multiple keywords by using more input fields
    key_terms_1 = st.text_input("Key Term 1", "")
    key_terms_2 = st.text_input("Key Term 2 (Optional)", "")
    key_terms_3 = st.text_input("Key Term 3 (Optional)", "")
    time_period = st.selectbox("Time period", options=["2020", "2021", "2022"], index=0)
    reply_count = st.slider("Minimum Reply Count", 0, 50, 0)
    like_count = st.slider("Minimum Like Count", 0, 50, 0)
    retweet_count = st.slider("Minimum Retweet Count", 0, 50, 0)
    submit_button = st.form_submit_button(label="Submit Advanced Search")

if submit_button:
    # Filter the dataset based on the search criteria
    filtered_data = combined_data.copy()
    
    if key_terms_1:
        filtered_data = filtered_data[filtered_data['CleanedText'].str.contains(key_terms_1, case=False, na=False)]
    if key_terms_2:
        filtered_data = filtered_data[filtered_data['CleanedText'].str.contains(key_terms_2, case=False, na=False)]
    if key_terms_3:
        filtered_data = filtered_data[filtered_data['CleanedText'].str.contains(key_terms_3, case=False, na=False)]
    if time_period:
        filtered_data = filtered_data[filtered_data['CreateDate'].str.contains(time_period, na=False)]
    if reply_count:
        filtered_data = filtered_data[filtered_data['ReplyCount'] >= reply_count]
    if like_count:
        filtered_data = filtered_data[filtered_data['LikeCount'] >= like_count]
    if retweet_count:
        filtered_data = filtered_data[filtered_data['RetweetCount'] >= retweet_count]
    
    # Save the filtered data in session state
    st.session_state['filtered_data'] = filtered_data
    st.session_state['show_filtered_data'] = True

# Show filtered data page if the search has been submitted
if st.session_state['show_filtered_data']:
    st.markdown("<div class='header'><h1>Filtered Tweets</h1></div>", unsafe_allow_html=True)
    st.dataframe(st.session_state['filtered_data'])
else:
    # Header
    st.markdown("<div class='header'><h1>Mpox Dashboard</h1></div>", unsafe_allow_html=True)
    
    # Navigation Bar with links to external pages
    st.markdown("""
        <div class="navbar">
            <a href="https://example.com/our-methodology" target="_blank">Our Methodology</a>
            <a href="https://example.com/our-mission" target="_blank">Our Mission</a>
            <a href="#data-used" target="_self">Data Used</a>  <!-- Added Data Used link -->
        </div>
        """, unsafe_allow_html=True)

    # Combined total number of tweets across both files
    total_tweets = len(combined_data)
    total_cases_in_austin = combined_data['Location'].str.contains("Austin", case=False, na=False).sum()
    col1, col2 = st.columns(2)
    col1.metric("Total Number of Tweets", total_tweets)
    col2.metric("Total Cases in Austin", total_cases_in_austin)

    # Analyze keywords
    keywords = ["Monkey", "Pox", "Quarantine", "Crazy"]
    keyword_counts = {kw: combined_data['CleanedText'].str.contains(kw, case=False, na=False).sum() for kw in keywords}

    # Enhanced Keyword Section
    st.markdown("### List of Keywords")
    for keyword, count in keyword_counts.items():
        st.markdown(f"""
        <div class="keyword-box">
            <h4>{keyword}</h4>
            <p>Occurrences: {count}</p>
        </div>
        """, unsafe_allow_html=True)

    # Display tweet counts per location
    st.markdown("### Tweet Counts per Location")
    location_counts = combined_data['Location'].value_counts()
    st.bar_chart(location_counts)

    # Most Used Words Each Year Table
    st.markdown("### Top 10 Most Used Words Each Year")
    top_words = get_top_10_words_by_year(combined_data)
    st.table(top_words)

    # Footer Links
    st.markdown("### Learn more:")
    st.markdown("[Link to our paper](#)", unsafe_allow_html=True)

    # Initialize session state for toggling data display
    if 'show_data' not in st.session_state:
        st.session_state['show_data'] = False

    # Button to toggle data visibility
    if st.button("Show/Hide Data Used"):
        st.session_state['show_data'] = not st.session_state['show_data']

    # Data Used Section (conditionally rendered based on toggle state)
    if st.session_state['show_data']:
        st.markdown("### Data Used")
        st.dataframe(combined_data)
