# International Football Knowledge Chatbot
A Streamlit app that uses Neo4j graph database and OpenAI's GPT-4o model to anser questions about the international football history from 1872 to present.

## Setup
1) Clone repository
2) Create environment and install dependencies
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
3) Set up your .streamlit/secrets.toml file with the following keys:
  - NEO4J_URI
  - NEO4J_USER
  - NEO4J_PASSWORD
4) Run the app
```powershell
streamlit run app.py
```

## Deployment
To deploy this app on Streamlit Cloud:
1) Push code to GitHub repo
2) Connect GitHub account to Streamlit Cloud
3) Create a new app in Streamlit Cloud and select your repository
4) Add secrets to Streamlit Cloud dashboard under the "Secrets" section
5) Deploy app
