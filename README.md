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

## Deployment

For deployment on Streamlit Cloud, add your credentials to the Streamlit secrets management instead of using environment variables.

## Security Note

Never commit your `leads-peeker-bot.json` file or `.env` file to version control. These files contain sensitive credentials. 