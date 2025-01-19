import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Mpox Dashboard", layout="wide")

# Custom CSS for styling with updated colors
st.markdown(
    """
    <style>
    /* General body styling */
    body {
        background-color: #A4B0F5;  /* Soft blue background for readability */
        font-family: 'Arial', sans-serif;
        color: #4464AD;  /* Dark blue text color */
    }
    /* Header styling */
    .header {
        background-color: #4464AD;  /* Strong blue for the header */
        color: white;
        padding: 10px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    /* Navigation bar styling */
    .navbar {
        background-color: #466995;  /* Muted steel blue for the navbar */
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .navbar a {
        color: white;
        padding: 8px 15px;
        text-decoration: none;
        font-size: 18px;
    }
    .navbar a:hover {
        background-color: #F58F29;  /* Orange hover effect */
        color: white;
        border-radius: 5px;
    }
    /* Keyword box styling */
    .keyword-box {
        background-color: white;
        border: 2px solid #4464AD;  /* Dark blue border */
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        color: #7D4600;  /* Warm brown text */
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    .keyword-box h4 {
        color: #F58F29;  /* Vibrant orange for headings */
    }
    /* Button styling */
    .stButton button {
        background-color: #466995;  /* Steel blue */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #F58F29;  /* Orange hover effect */
    }
    /* Metric box styling */
    .stMetric {
        background-color: #A4B0F5;  /* Soft blue background for metrics */
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 20px;
        text-align: center;
        color: #7D4600;  /* Warm brown text */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load datasets
file_path_book1 = "Copy of Book1.csv.xlsx"
file_path_final_merged = "1_19_merged.csv"

data_book1 = pd.read_excel(file_path_book1)
data_final_merged = pd.read_csv(file_path_final_merged)

# Normalize columns for both datasets
def normalize_dataset(dataset, source):
    if source == "Book1":
        dataset['Date'] = pd.to_datetime(dataset['CreateDate'], errors='coerce').dt.date
        dataset['Time'] = pd.to_datetime(dataset['CreateDate'], errors='coerce').dt.time
        dataset['Text'] = dataset['CleanedText']
        dataset['Name'] = dataset['author_name'] if 'author_name' in dataset.columns else None
        dataset['Location'] = dataset['Location'] if 'Location' in dataset.columns else None
        dataset['Follower Count'] = dataset['follower_count'] if 'follower_count' in dataset.columns else None
        dataset['Like Count'] = dataset['LikeCount'] if 'LikeCount' in dataset.columns else None
        dataset['Reply Count'] = dataset['ReplyCount'] if 'ReplyCount' in dataset.columns else None
    elif source == "FinalMerged":
        dataset['Date'] = pd.to_datetime(dataset['timestamp'], errors='coerce').dt.date
        dataset['Time'] = pd.to_datetime(dataset['timestamp'], errors='coerce').dt.time
        dataset['Text'] = dataset['body']
        dataset['Name'] = dataset['author']
        dataset['Location'] = dataset['place_name']
        dataset['Follower Count'] = dataset['follower_count'] if 'follower_count' in dataset.columns else None
        dataset['Like Count'] = dataset['like_count'] if 'like_count' in dataset.columns else None
        dataset['Reply Count'] = dataset['reply_count'] if 'reply_count' in dataset.columns else None

    return dataset[['Date', 'Time', 'Text', 'Name', 'Location', 'Follower Count', 'Like Count', 'Reply Count']]

# Normalize both datasets
data_normalized_book1 = normalize_dataset(data_book1, "Book1")
data_normalized_final_merged = normalize_dataset(data_final_merged, "FinalMerged")

# Combine the datasets
combined_data_normalized = pd.concat([data_normalized_book1, data_normalized_final_merged], ignore_index=True)

# Ensure Date column is properly converted and NaT values are handled
combined_data_normalized['Date'] = pd.to_datetime(combined_data_normalized['Date'], errors='coerce')

# Remove NaT values and set default values safely
valid_dates = combined_data_normalized['Date'].dropna()

if not valid_dates.empty:
    default_start_date = valid_dates.min().date()
    default_end_date = valid_dates.max().date()
else:
    default_start_date = pd.to_datetime("2020-01-01").date()
    default_end_date = pd.to_datetime("2024-12-31").date()

# Sidebar for Advanced Search
st.sidebar.markdown("## Advanced Search for Tweets")
with st.sidebar.form(key='advanced_search_form'):
    key_terms_1 = st.text_input("Key Term 1", "")
    key_terms_2 = st.text_input("Key Term 2 (Optional)", "")
    key_terms_3 = st.text_input("Key Term 3 (Optional)", "")
    start_date = st.date_input("Start Date", default_start_date)
    end_date = st.date_input("End Date", default_end_date)
    reply_count = st.slider("Minimum Reply Count", 0, 50, 0)
    like_count = st.slider("Minimum Like Count", 0, 50, 0)
    retweet_count = st.slider("Minimum Retweet Count", 0, 50, 0)
    submit_button = st.form_submit_button(label="Submit Advanced Search")

if submit_button:
    filtered_data = combined_data_normalized.copy()

    # Apply keyword filtering
    keyword_filter = pd.Series(True, index=filtered_data.index)
    if key_terms_1:
        keyword_filter &= filtered_data['Text'].str.contains(key_terms_1, case=False, na=False)
    if key_terms_2:
        keyword_filter &= filtered_data['Text'].str.contains(key_terms_2, case=False, na=False)
    if key_terms_3:
        keyword_filter &= filtered_data['Text'].str.contains(key_terms_3, case=False, na=False)
    
    filtered_data = filtered_data[keyword_filter]

    # Apply date range filtering
    filtered_data = filtered_data[
        (filtered_data['Date'].notna()) & 
        (filtered_data['Date'] >= pd.to_datetime(start_date)) & 
        (filtered_data['Date'] <= pd.to_datetime(end_date))
    ]

    # Apply count filters
    if reply_count > 0:
        filtered_data = filtered_data[filtered_data['Reply Count'].fillna(0) >= reply_count]
    if like_count > 0:
        filtered_data = filtered_data[filtered_data['Like Count'].fillna(0) >= like_count]
    if retweet_count > 0:
        filtered_data = filtered_data[filtered_data['Reply Count'].fillna(0) >= retweet_count]

    # Display results or a message if no results
    if filtered_data.empty:
        st.warning("No results found for the selected filters.")
    else:
        st.markdown("### Filtered Data")
        st.dataframe(filtered_data)



else:
    # Header for the homepage
    st.markdown("<div class='header'><h1>Mpox Dashboard</h1></div>", unsafe_allow_html=True)

    # Navigation bar
    st.markdown("""
        <div class="navbar">
            <a href="https://example.com/our-methodology" target="_blank">Our Methodology</a>
            <a href="https://example.com/our-mission" target="_blank">Our Mission</a>
        </div>
        """, unsafe_allow_html=True)

    # Metrics
    total_tweets = len(combined_data_normalized)
    total_cases_in_austin = combined_data_normalized['Location'].str.contains("Austin", case=False, na=False).sum()
    col1, col2 = st.columns(2)
    col1.metric("Total Number of Tweets", total_tweets)
    col2.metric("Total Cases in Austin", total_cases_in_austin)

    # Cluster Summary Table
    cluster_data = {
        "Cluster_Name": ["Cynicism", "Exasperation", "COVID-19", "Outbreak Reports", "Government Action", "Misinformation"],
        "RT": [436719, 12112, 418, 0, 33186, 160473],  # Total retweets
        "Rc": [75.951130, 26.915556, 0.981221, 0.000000, 43.494102, 108.574425],  # Average retweets
        "Tweets_n": [5751, 450, 426, 96, 763, 1478],  # Total tweets
        "Sample_Tweets": [
            "Is monkeypox in the US? What to know about mpox and its symptoms. Stay informed!",
            "@War_Rum MonkeyPox :joy: – sarcastic commentary on media overhyping mpox cases.",
            "મંકીપોક્સ વાયરસથી મળશે મુક્તિ! (Translation: Freedom from monkeypox virus!) #monkeypox #mpox",
            "Her bahis bir heyecan, her kazanç bir zafer! Bir başka deneyim burada... (Translation: Every bet is an excitement, every win is a victory! Another experience is here...)",
            ":zap:️:zap:️:zap:️:zap:️\n\n'L'Organizzazione Mondiale della Sanità ha annunciato... (Translation: The World Health Organization has announced...)",
            "Former health minister Khairy Jamaluddin has dismissed rumors circulating on social media about a new mpox wave, urging people to rely on verified sources."
        ]
    }
    cluster_summary_df = pd.DataFrame(cluster_data)
    st.markdown("### Cluster Summary Table")
    st.dataframe(cluster_summary_df, width=800, height=400)

    # Keyword analysis
    st.markdown("### List of Keywords")
    keywords = ["Monkey", "Pox", "Vaccine", "Quarantine"]
    keyword_counts = {kw: combined_data_normalized['Text'].str.contains(kw, case=False, na=False).sum() for kw in keywords}
    for keyword, count in keyword_counts.items():
        st.markdown(f"""
        <div class='keyword-box'>
            <h4>{keyword}</h4>
            <p>Occurrences: {count}</p>
        </div>
        """, unsafe_allow_html=True)

    # Bar chart for tweet counts by location
    st.markdown("### Tweet Counts per Location")
    location_counts = combined_data_normalized['Location'].value_counts()
    st.bar_chart(location_counts)
