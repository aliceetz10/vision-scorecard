# Vision One Million Scorecard

Automated data pipeline and dashboard for the Vision One Million Scorecard (Winter 2026 Hackathon). This project assesses the Kitchener-Waterloo-Cambridge region's progress towards its strategic goals by analyzing key metrics using an AI-driven data pipeline.

## Features
- **Data Ingestion**: Automated fetching of regional metrics including Unemployment, Employment, Housing Starts, Transit Ridership, Hospital Wait Times, GO Train Services, GHG Emissions, and School Utilization.
- **AI Analysis**: Uses OpenAI (GPT-4o-mini) to analyze current trends, evaluate them against regional strategic goals (Kitchener, Waterloo, Cambridge), and provide actionable recommendations.
- **Dashboard**: A Flask-based web application providing a centralized view of all metrics, original sources, and AI assessments.

## Project Structure
- `backend/`: Contains data ingestion scripts (`fetch-scripts/`), SQLite databases (`database/`), and the core analytics engine (`main.py` and `ai-analysis/`).
- `frontend/`: Contains the Flask web application (`main.py`), templates (`templates/`), static assets (`static/`), and the generated timeline/overview database.

## Prerequisites
- Python 3.9+
- OpenAI API Key

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd vision-scorecard
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the project root and add your API credentials:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### 1. Update Data Pipeline (Backend)
To fetch the latest data and run the AI analysis to update the dashboard database, run:
```bash
python backend/main.py
```

### 2. Start the Dashboard (Frontend)
To start the Flask web server and view the UI:
```bash
python frontend/main.py
```
The application will be accessible at `http://localhost:5001/` by default.

## Data Sources
- **Economy**: Statistics Canada (Employment/Unemployment)
- **Housing**: CMHC (Housing Starts)
- **Transportation**: Grand River Transit (GRT), Metrolinx (GO Transit)
- **Healthcare**: Health Quality Ontario (Wait Times)
- **Environment**: ClimateActionWR (GHG Emissions)
- **Education**: WRDSB (School Utilization)
- **Documents**: Strategic Plans for the Cities of Cambridge, Kitchener, and Waterloo.
