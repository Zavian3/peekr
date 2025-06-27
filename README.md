# Peekr Client Outreach Agent 🎯

A Streamlit dashboard for analyzing client outreach data from Google Sheets.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Google Cloud Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Fill in the details and create
   - Create a key for the service account (JSON format)
5. Share your Google Sheet with the service account email

### 3. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Fill in your Google Cloud Service Account details in the `.env` file:

```env
GCP_PROJECT_ID=your-project-id
GCP_PRIVATE_KEY_ID=your-private-key-id  
GCP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----"
GCP_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GCP_CLIENT_ID=your-client-id
```

### 4. Run the Application

```bash
streamlit run app.py
```

## Features

- 📈 Total leads tracking
- 📧 Email validation status
- 🌐 Domain analysis
- 📂 Category distribution
- 🗺️ Geographic distribution
- 📬 Email communication tracking

## Deployment on Streamlit Cloud

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `Zavian3/peekr`
5. Set the main file path: `app.py`
6. Click "Deploy"

### 3. Configure Secrets
After deployment, go to your app settings and add your Google Cloud credentials:

1. In your Streamlit Cloud app, click the menu (⋮) → "Settings"
2. Go to the "Secrets" tab
3. Add your Google Cloud Service Account credentials in TOML format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

4. Click "Save"

### 4. Share Your Google Sheet
Make sure to share your Google Sheet with the service account email address (found in `client_email`).

## Security Note

Never commit your `leads-peeker-bot.json` file or `.env` file to version control. These files contain sensitive credentials. 