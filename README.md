
# Greek Football Analytics

A Football Data Analytics project focused on the Greek Super League 2024-2025 season.

## Project Overview

This project uses API-Football data to analyze team performance,
match results, attacking and defensive statistics.

## Features

- League Standings
- Match Explorer
- Team Analysis
- Team Comparison
- Home vs Away Analysis
- Goals per Match
- Clean Sheets Analysis
- Data Quality Validation
- Automated Testing
- Interactive Streamlit Dashboard

## Technologies

- Python
- Pandas
- Streamlit
- Altair
- Matplotlib
- API-Football
- Pytest

## Dataset

- 236 collected matches
- 14 teams
- 182 Regular Season matches
- 13 columns in the processed dataset

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## API Configuration

Create a `.env` file based on `.env.example`.

Add your API-Football key:

```text
API_FOOTBALL_KEY=your_api_key_here
```

## Run the Dashboard

```bash
python -m streamlit run app.py
```

## Run Automated Tests

```bash
python -m pytest -v
```

## Data Validation

```bash
python -m utils.data_validation
```

## Project Structure

```text
greek-football-analytics/
│
├── data/
│   └── processed/
│
├── logs/
│
├── pages/
│
├── tests/
│
├── utils/
│
├── app.py
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## Project Status

Development in progress.
