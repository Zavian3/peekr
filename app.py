import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import gspread
import json
import os
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Peekr Client Outreach Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }

    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }

    
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_from_gsheet():
    # Try to get credentials from Streamlit secrets first, then environment variables
    try:
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            # Use Streamlit secrets (for deployment)
            credentials_info = dict(st.secrets["gcp_service_account"])
        else:
            # Use environment variables (for local development)
            credentials_info = {
                "type": "service_account",
                "project_id": os.getenv("GCP_PROJECT_ID"),
                "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GCP_PRIVATE_KEY", "").replace('\\n', '\n'),
                "client_email": os.getenv("GCP_CLIENT_EMAIL"),
                "client_id": os.getenv("GCP_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GCP_CLIENT_EMAIL', '').replace('@', '%40')}",
                "universe_domain": "googleapis.com"
            }
        
        # Create credentials from the info
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
        client = gspread.authorize(creds)
        
    except Exception as e:
        st.error(f"Error loading credentials: {str(e)}")
        st.info("Please set up your Google Cloud Service Account credentials as environment variables or Streamlit secrets.")
        st.stop()

    spreadsheet_id = "1_SlKC3SkL90lYf2i_lELZrZQvh2tdMUaZSKe5_nG4WQ"
    worksheet = client.open_by_key(spreadsheet_id).worksheet("Incoming Leads")
    worksheet1 = client.open_by_key(spreadsheet_id).worksheet("Categories")
    data = worksheet.get_all_records()
    data1 = worksheet1.get_all_records()

    leads_df = pd.DataFrame(data)
    categories_df = pd.DataFrame(data1)

    def extract_country(location):
        location_str = str(location).lower()
        if any(city in location_str for city in ['dubai', 'abu dhabi', 'ras al khaimah', 'uae']):
            return 'UAE'
        elif 'poland' in location_str:
            return 'Poland'
        else:
            return 'Other'

    leads_df['Country'] = leads_df['Location'].apply(extract_country)
    categories_df['Country'] = categories_df['Location'].apply(extract_country)

    return leads_df, categories_df

def create_metrics_cards(leads_df, categories_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_leads = len(leads_df)
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Total Leads</h3>
            <h2>{total_leads}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        valid_emails = len(leads_df[(leads_df['Valid Email'] != '') | (leads_df['Valid Email'] != '')])
        st.markdown(f"""
        <div class="metric-card">
            <h3>📧 Valid Emails</h3>
            <h2>{valid_emails}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        unique_domains = leads_df['domain'].nunique() if 'domain' in leads_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>🌐 Unique Domains</h3>
            <h2>{unique_domains}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        categories_count = len(leads_df['Category'].unique()) if 'Category' in leads_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>📂 Categories</h3>
            <h2>{categories_count}</h2>
        </div>
        """, unsafe_allow_html=True)

def create_location_chart(categories_df):
    if 'Location' not in categories_df.columns:
        return go.Figure()

    location_counts = categories_df['Country'].value_counts()

    fig = px.pie(
        values=location_counts.values,
        names=location_counts.index,
        title="Leads Distribution by Country (from Categories Sheet)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_font_size=18, height=400)
    return fig

def create_categories_chart(leads_df):
    if 'Category' not in leads_df.columns:
        return go.Figure()

    category_counts = leads_df['Category'].value_counts()

    fig = px.bar(
        x=category_counts.values,
        y=category_counts.index,
        orientation='h',
        title="Business Categories Distribution (from Incoming Leads)",
        color=category_counts.values,
        color_continuous_scale='viridis'
    )

    fig.update_layout(height=500, title_font_size=18, showlegend=False)
    return fig



def create_email_status_chart(leads_df):
    email_status = [
        'Has Email' if row['Email'] or row['Valid Email'] else 'No Email'
        for _, row in leads_df.iterrows()
    ]
    email_counts = pd.Series(email_status).value_counts()

    fig = go.Figure(data=[
        go.Bar(
            x=email_counts.index,
            y=email_counts.values,
            marker_color=['#2ecc71', '#e74c3c'],
            text=email_counts.values,
            textposition='auto'
        )
    ])
    fig.update_layout(title="Email Availability Status", height=400)
    return fig

def create_email_flow_chart(leads_df):
    sent_col = 'Status'
    answer_col = 'Mail reply send'
    followup_col = 'Follow Up'

    total_sent = leads_df[sent_col].fillna('').astype(str).str.lower().eq('send').sum()
    total_answered = leads_df[answer_col].fillna('').astype(str).str.lower().eq('yes').sum()
    total_followups = leads_df[followup_col].fillna('').astype(str).str.lower().eq('send').sum()

    data = {
        'Status': ['Emails Sent', 'Emails Answered', 'Follow Ups'],
        'Count': [total_sent, total_answered, total_followups]
    }

    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        x='Status',
        y='Count',
        title='📬 Email Communication Summary',
        color='Status',
        text='Count',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=500)

    return fig

def main():
    st.markdown('<h1 class="main-header">🎯 Peekr Client Outreach Agent</h1>', unsafe_allow_html=True)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
    leads_df, categories_df = load_data_from_gsheet()

    # Sidebar using categories_df countries
    st.sidebar.markdown('<div class="sidebar-header">🔍 Filters</div>', unsafe_allow_html=True)
    countries = ['All'] + sorted(categories_df['Country'].unique())
    selected_country = st.sidebar.selectbox("Select Country (from Categories)", countries)

    domains = ['All']
    if 'Domain' in leads_df.columns:
        domains += list(leads_df['Domain'].unique())
    selected_domain = st.sidebar.selectbox("Select Domain", domains)

    # Apply filters
    filtered_df = leads_df.copy()
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
        categories_df = categories_df[categories_df['Country'] == selected_country]

    if selected_domain != 'All' and 'Domain' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Domain'] == selected_domain]

    # Render metrics and charts
    create_metrics_cards(filtered_df, categories_df)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(create_location_chart(categories_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(create_email_status_chart(filtered_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")    
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(create_categories_chart(filtered_df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(create_email_flow_chart(filtered_df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📋 Data Tables")
    with st.expander("📊 Leads Data", expanded=False):
        st.dataframe(filtered_df, use_container_width=True, height=400)

    with st.expander("📂 Categories Data", expanded=False):
        st.dataframe(categories_df, use_container_width=True, height=300)

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
            <p>🎯 Peekr Client Outreach Agent | by Peekr</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
