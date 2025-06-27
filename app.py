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
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
        color: #f8fafc;
        min-height: 100vh;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #f1f5f9;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    .metric-card {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 20px rgba(96, 165, 250, 0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(96, 165, 250, 0.35);
    }
    
    .metric-card h3 {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        opacity: 1;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .metric-card h2 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 10px rgba(96, 165, 250, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(96, 165, 250, 0.4);
    }
    
    /* Ensure all text is visible */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f8fafc !important;
    }
    
    /* Remove default streamlit styling that causes dark backgrounds */
    .stDataFrame, .stDataFrame > div {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
        color: #f8fafc !important;
        border-radius: 8px;
    }
    
    /* Ensure tables have proper styling */
    [data-testid="stDataFrame"] {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        border-radius: 8px;
        border: 1px solid #6b7280;
        color: #f8fafc;
    }
    
    /* Footer styling */
    .footer-style {
        color: #cbd5e1;
        text-align: center;
        font-weight: 500;
        padding: 2rem;
        margin-top: 2rem;
    }
    
    /* Sidebar text visibility */
    .css-1d391kg {
        color: #f8fafc;
    }
    
    /* Section headers */
    h2 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Dropdown styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        border: 2px solid #6b7280;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
        color: #f8fafc;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #60a5fa;
        box-shadow: 0 6px 20px rgba(96, 165, 250, 0.25);
    }
    
    /* Dropdown menu styling */
    .stSelectbox [data-baseweb="select"] > div {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        border-radius: 12px;
        color: #f8fafc;
    }
    
    /* Dropdown options styling */
    .stSelectbox [role="listbox"] {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        border-radius: 12px;
        border: 2px solid #6b7280;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        max-height: 200px;
        overflow-y: auto;
    }
    
    .stSelectbox [role="option"] {
        color: #f8fafc !important;
        background-color: transparent;
        padding: 8px 12px;
    }
    
    .stSelectbox [role="option"]:hover {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%) !important;
        color: white !important;
    }
    
    /* Scrollbar styling for dropdowns */
    .stSelectbox [role="listbox"]::-webkit-scrollbar {
        width: 8px;
    }
    
    .stSelectbox [role="listbox"]::-webkit-scrollbar-track {
        background: #4b5563;
        border-radius: 4px;
    }
    
    .stSelectbox [role="listbox"]::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        border-radius: 4px;
    }
    
    .stSelectbox [role="listbox"]::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    }
    
    /* Fix spinner background */
    .stSpinner > div {
        background-color: transparent !important;
    }
    
    .stAlert {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
        border: 1px solid #6b7280 !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data_from_gsheet():
    # Try to get credentials from environment variables first, then Streamlit secrets
    try:
        # Check if we have environment variables (for local development)
        if os.getenv("GCP_PROJECT_ID") and os.getenv("GCP_PRIVATE_KEY"):
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
        elif hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            # Use Streamlit secrets (for deployment)
            credentials_info = dict(st.secrets["gcp_service_account"])
        else:
            raise ValueError("No credentials found in environment variables or Streamlit secrets")
        
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

    location_counts = categories_df['Location'].value_counts()

    fig = px.pie(
        values=location_counts.values,
        names=location_counts.index,
        title="Leads Distribution by Location (from Categories Sheet)",
        color_discrete_sequence=['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#fb7185']
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
        color_continuous_scale=[[0, '#60a5fa'], [1, '#34d399']]
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
            marker_color=['#60a5fa', '#34d399'],
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
        color_discrete_sequence=['#60a5fa', '#34d399', '#fbbf24']
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=500)

    return fig

def main():
    st.markdown('<h1 class="main-header">🎯 Peekr Client Outreach Agent</h1>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data"):
        # Clear cache
        st.cache_data.clear()
        
        # Show modern popup notification
        popup_placeholder = st.empty()
        with popup_placeholder.container():
            st.markdown("""
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                color: #f8fafc;
                padding: 2rem 3rem;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
                border: 2px solid #60a5fa;
                z-index: 9999;
                text-align: center;
                backdrop-filter: blur(10px);
                animation: fadeIn 0.3s ease-in-out;
            ">
                <div style="
                    font-size: 3rem;
                    margin-bottom: 1rem;
                    animation: spin 1s linear infinite;
                ">🔄</div>
                <h2 style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin-bottom: 0.5rem;
                    color: #60a5fa;
                ">Refreshing Data</h2>
                <p style="
                    font-size: 1rem;
                    color: #cbd5e1;
                    margin: 0;
                ">Please wait while we fetch the latest data...</p>
            </div>
            
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
                    to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                }
                
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
            """, unsafe_allow_html=True)
        
        # Small delay to show the popup
        import time
        time.sleep(1)
        
        # Clear the popup
        popup_placeholder.empty()
        
        # Show success message
        st.success("✅ Data refreshed successfully!")
        
        # Rerun to reload data
        st.rerun()
    
    # Show loading popup for initial data load
    if 'data_loaded' not in st.session_state:
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown("""
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                color: #f8fafc;
                padding: 2rem 3rem;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
                border: 2px solid #34d399;
                z-index: 9999;
                text-align: center;
                backdrop-filter: blur(10px);
                animation: fadeIn 0.3s ease-in-out;
            ">
                <div style="
                    font-size: 3rem;
                    margin-bottom: 1rem;
                    animation: pulse 1.5s ease-in-out infinite;
                ">📊</div>
                <h2 style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin-bottom: 0.5rem;
                    color: #34d399;
                ">Loading Data</h2>
                <p style="
                    font-size: 1rem;
                    color: #cbd5e1;
                    margin: 0;
                ">Fetching latest data from Google Sheets...</p>
            </div>
            
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
                    to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                }
                
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                }
            </style>
            """, unsafe_allow_html=True)
        
        # Load the data
        leads_df, categories_df = load_data_from_gsheet()
        
        # Clear the loading popup
        loading_placeholder.empty()
        
        # Mark data as loaded
        st.session_state.data_loaded = True
    else:
        # Data already loaded, just get it from cache
        leads_df, categories_df = load_data_from_gsheet()

    # Use all data without filters
    filtered_df = leads_df.copy()

    # Render metrics and charts
    create_metrics_cards(filtered_df, categories_df)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(create_location_chart(categories_df), use_container_width=True)

    with col2:
        st.plotly_chart(create_email_status_chart(filtered_df), use_container_width=True)
    
    st.plotly_chart(create_categories_chart(filtered_df), use_container_width=True)
    st.plotly_chart(create_email_flow_chart(filtered_df), use_container_width=True)

    st.markdown("## 📋 Data Tables")
    with st.expander("📊 Leads Data", expanded=False):
        st.dataframe(filtered_df, use_container_width=True, height=400)

    with st.expander("📂 Categories Data", expanded=False):
        st.dataframe(categories_df, use_container_width=True, height=300)

    st.markdown(
        """
        <div class='footer-style'>
            <p>🎯 Peekr Client Outreach Agent | by Peekr</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
