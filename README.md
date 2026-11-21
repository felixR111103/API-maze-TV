# What to watch

What to watch is a Netflix-inspired Streamlit application powered by the free public [TVMaze API](https://www.tvmaze.com/api). It helps users discover series, inspect full episode guides, explore cast credits, save a watchlist, and turn live API data into an interactive streaming-style experience.

## What the project demonstrates

- Sending HTTP `GET` requests with paths and query parameters
- Decoding JSON responses and navigating nested objects
- Using stable resource IDs to request related episodes, cast, and crew
- Embedding related data in one response
- Converting JSON into pandas DataFrames
- Visualizing API data with Plotly
- Exporting transformed API data as CSV
- Caching repeated requests in Streamlit
- Retrying temporary HTTP failures and handling `404`/`429` responses
- Identifying an application with a custom `User-Agent`

## App sections

| Section | API concepts |
| --- | --- |
| Home | Fuzzy search, clickable recommendation shelves, watchlist, viewing history |
| Show details | Complete episode guide and descriptions, cast, crew, filters, charts |
| People | People search and embedded show credits |

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens the app at `http://localhost:8501`.

To install test dependencies and run the tests:

```bash
python3 -m pip install -r requirements-dev.txt
pytest -q
```

## Project structure

```text
API-maze-TV/
├── app.py                    # Streamlit interface and data transformations
├── tvmaze_api.py             # Reusable API client, retries, error handling
├── requirements.txt
├── .streamlit/config.toml    # Visual theme and server settings
└── tests/test_tvmaze_api.py  # Small unit tests for helper functions
```

## Example request

```python
import requests

response = requests.get(
    "https://api.tvmaze.com/search/shows",
    params={"q": "Severance"},
    timeout=15,
)
response.raise_for_status()
shows = response.json()
```

The app uses a reusable session with retries, a descriptive `User-Agent`, explicit timeouts, and user-friendly error messages. TVMaze documents a rate limit of at least 20 calls per 10 seconds per IP; repeated calls in the app are cached for one hour.

## Data credit

Data and images are provided by [TVMaze](https://www.tvmaze.com) under CC BY-SA. No API key is required.
