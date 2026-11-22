# What to watch

**What to watch** is an educational Python and Streamlit project that uses the public [TVMaze REST API](https://www.tvmaze.com/api). The objective was to understand how an application connects to an external API, sends requests, receives JSON, follows relationships between resources, transforms the returned data, handles errors, and presents the result to a user.

The streaming-style interface makes those API concepts tangible. A user can search for a television series, open its complete episode guide, read episode descriptions, inspect cast and crew information, compare episode ratings, search for actors, and save temporary watchlist items.

## Purpose

The project was built to practise the complete API workflow:

1. A user performs an action in the Streamlit interface.
2. Python converts that action into an HTTP `GET` request.
3. The request is sent over HTTPS to `https://api.tvmaze.com`.
4. TVMaze finds the requested resource and returns a JSON response.
5. Python converts the JSON into dictionaries, lists, and pandas DataFrames.
6. Streamlit displays the result as posters, descriptions, episode lists, cast information, and charts.

```text
User in browser
      │
      │ search, click, or filter
      ▼
Streamlit interface (app.py)
      │
      │ calls get_json(path, parameters)
      ▼
API client (tvmaze_api.py)
      │
      │ HTTPS GET request
      ▼
TVMaze REST API
      │
      │ JSON response
      ▼
Python transformation → Streamlit presentation
```

The application has three main sections:

| Section | What the user can do | API concept demonstrated |
| --- | --- | --- |
| Home | Search for shows, browse recommendations, maintain a watchlist | Search endpoints, query parameters, pagination and filtering |
| Show details | View every episode and description, cast, crew and ratings | Resource IDs and related endpoints |
| People | Search for an actor and view their series credits | People resources and embedded related data |

## Data collection

### Data source

All television data and images come from the free public TVMaze API. The API root is:

```text
https://api.tvmaze.com
```

TVMaze returns structured JSON and does not require an API key for the endpoints used in this project. No web pages are scraped. The application only uses the documented API.

### How an API request is made

The reusable connection logic is located in `tvmaze_api.py`. The central function is `get_json()`:

```python
def get_json(path, params=None):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    with build_session() as session:
        response = session.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()
```

The function receives two pieces of information:

- `path`: identifies the resource, for example `search/shows`.
- `params`: optional query parameters, for example `{"q": "Severance"}`.

The `requests` library safely combines them into this URL:

```http
GET https://api.tvmaze.com/search/shows?q=Severance
```

`GET` means that the application is requesting data without changing anything on the TVMaze server. The server responds with an HTTP status code, headers, and a JSON body. `response.json()` converts the JSON body into normal Python dictionaries and lists.

### Example: searching for a show

When the user enters `Severance`, the app calls:

```http
GET /search/shows?q=Severance
```

A simplified part of the response looks like this:

```json
[
  {
    "score": 1.0,
    "show": {
      "id": 44933,
      "name": "Severance",
      "genres": ["Drama", "Science-Fiction", "Thriller"],
      "rating": {"average": 7.7},
      "summary": "...",
      "image": {
        "medium": "https://...",
        "original": "https://..."
      }
    }
  }
]
```

The app extracts the nested `show` object and uses its fields to display the title, poster, genres, rating, year, status, and description. Search results contain a numeric TVMaze `id`. This stable ID is important because two series can have similar names, while the ID uniquely identifies one resource.

### Example: following a show ID to related data

After a user selects a show, the application uses its ID to request related resources. For show ID `44933`, it sends:

```http
GET /shows/44933/episodes?specials=1
GET /shows/44933/cast
GET /shows/44933/crew
```

The episode response contains fields such as:

- season and episode number;
- episode title and summary;
- air date and runtime;
- episode rating;
- episode image.

The `specials=1` query parameter asks TVMaze to include special episodes as well as regular episodes. The application turns the episode list into a pandas DataFrame. This enables season filtering, average-rating calculations, Plotly charts, and CSV export.

Cast results combine a `person` resource with a `character` resource. Crew results combine a person with a role. The app reads these nested objects to show actor names, character names, portraits, and crew roles.

### Recommendations

TVMaze does not provide a personalised recommendation endpoint. The recommendation shelves are created by this project. The app requests four pages of the show catalogue:

```http
GET /shows?page=0
GET /shows?page=80
GET /shows?page=160
GET /shows?page=240
```

It then removes entries without an image or rating, sorts the remaining shows by rating, and groups them by genres such as Drama, Comedy, Science Fiction, and Crime. Therefore, the raw show information comes from TVMaze, but the recommendation logic is implemented locally in `app.py`.

### People and credit data

The people page first searches for a person:

```http
GET /search/people?q=Pedro+Pascal
```

After the user selects the correct result, the app uses that person's ID:

```http
GET /people/{person_id}/castcredits?embed=show
```

The `embed=show` parameter asks TVMaze to include the associated show objects inside the credit response. This avoids making a separate request for every show credit.

### Reliability and responsible API use

The API client includes several safeguards:

- A 15-second timeout prevents a request from waiting forever.
- Requests use a configured `requests.Session` so headers and retry rules are applied consistently.
- Temporary failures are retried up to three times with increasing delays.
- Retryable responses include `429`, `500`, `502`, `503`, and `504`.
- `404 Not Found` and `429 Too Many Requests` produce understandable messages.
- A descriptive `User-Agent` identifies this class project.
- Identical requests are cached by Streamlit for one hour to improve speed and reduce unnecessary traffic.

The interface calls `safe_api()`, which catches `TVMazeError` exceptions and shows a readable error instead of crashing the entire application.

## Data persistence

This version intentionally has no database and does not permanently store TVMaze data.

| Data | Storage location | Lifetime | Reason |
| --- | --- | --- | --- |
| API responses | Streamlit in-memory cache | Up to one hour | Speeds up repeated requests and reduces API traffic |
| Watchlist | `st.session_state` in server memory | Current browser session | Demonstrates interactive state without requiring accounts |
| Recently viewed shows | `st.session_state` in server memory | Current browser session | Allows quick navigation back to opened shows |
| Exported episodes | User-selected CSV download | Saved only if the user downloads it | Lets the user reuse transformed episode data |

Closing or restarting the Streamlit session removes the watchlist and viewing history. No user account, password, personal information, or API key is collected. TVMaze remains the authoritative source; the application does not maintain a permanent copy of its catalogue.

## User interaction

1. Open the application in a browser.
2. Use the search bar to find a television series by name.
3. Click a poster or title in the results or recommendation shelves.
4. On the show page, read the description and add or remove the show from the temporary watchlist.
5. Open the **Episodes** tab, choose a season or keep **All seasons**, and expand an episode to see its image, air date, runtime, rating, and description.
6. Use **Cast & crew** to inspect the people connected to the series.
7. Use **Ratings** to view the episode-rating trend generated from the API data.
8. Download the episode table as CSV if required.
9. Open **People** to search for an actor and retrieve their television credits.

The interface is designed like a streaming catalogue because posters and shelves make the API data easy to explore. It does not play or host video content.

## Setup

### Requirements

- Python 3.11 or newer is recommended.
- An internet connection is required to reach TVMaze and load its images.
- No TVMaze account or API key is required.

The main dependencies are:

| Package | Purpose |
| --- | --- |
| Streamlit | Web interface and session state |
| Requests | HTTP communication with TVMaze |
| pandas | JSON-to-table transformation and analysis |
| Plotly | Interactive episode-rating charts |
| pytest | Automated tests during development |

### Installation and execution

Clone the repository and enter its directory:

```bash
git clone https://github.com/felixR111103/API-maze-TV.git
cd API-maze-TV
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\activate
```

Install the application dependencies and start Streamlit:

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

The application normally opens at `http://localhost:8501`.

No secrets or environment variables need to be configured. Visual settings are stored in `.streamlit/config.toml`.

To install the development dependency and run the tests:

```bash
python3 -m pip install -r requirements-dev.txt
pytest -q
```

### Project structure

```text
API-maze-TV/
├── app.py                    # Streamlit interface and data transformations
├── tvmaze_api.py             # HTTP client, retries and error handling
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Runtime and test dependencies
├── .streamlit/config.toml    # Streamlit theme and server settings
└── tests/test_tvmaze_api.py  # Unit tests for the API client helpers
```

## Learning

Before this project, I had already used an API while creating my first Chrome extension. At that time, however, I did not fully understand what was happening in the background. I could use the API with help, but I did not understand how the different parts of the connection worked.

Through this project, I developed a much clearer understanding of APIs. I learned that an API acts as a connection between two applications. In this case, my application sends a request to TVMaze through a specific URL. The request describes what information is needed, such as a television series, its episodes, or its cast. TVMaze processes the request and returns the available information in a structured JSON format. My application can then select the relevant parts of this response and present them to the user.

Understanding this process also helped me work more effectively with ChatGPT. Because I had a better understanding of the available endpoints, parameters, responses, and limitations, I could describe my ideas more precisely. ChatGPT could then translate those ideas into code more accurately. Instead of simply asking it to “connect to an API,” I was able to explain what information should be requested, how the different data should be connected, and how it should appear in the application.

Based on this understanding, I decided to create a streaming-style overview where users could search for shows, receive recommendations, and explore episodes, descriptions, ratings, and cast information. The visual design was inspired by streaming platforms, but the main purpose remained to demonstrate how API data can be retrieved, connected, transformed, and presented.

A major challenge was understanding what information could actually be accessed through the TVMaze API. Not every feature I imagined was supported by the available endpoints. For example, TVMaze provides show information, episodes, ratings, images, and cast data, but it does not provide personalised recommendations or streaming functionality. I addressed this challenge by reviewing the available API content and brainstorming possible features with ChatGPT. This gave me a clearer overview of the information that could be retrieved and helped me design an application that was both realistic and possible with the available data.

Overall, the project gave me a much stronger conceptual understanding of APIs. I now feel more confident exploring API documentation, identifying what data is available, and communicating how that data should be used when developing an application.

## Limitations and assistance

### Current limitations

- The project covers television series, not a complete film catalogue, because it uses TVMaze.
- Recommendations are based on rating and genre from four sampled catalogue pages. They are not personalised by machine learning or viewing behaviour.
- The watchlist and recent history disappear when the Streamlit session ends.
- There is no database, login system, user account, or synchronization between devices.
- The application depends on TVMaze and an internet connection. If the service is unavailable, live content cannot load.
- Some TVMaze records have missing posters, summaries, dates, or ratings; the interface uses fallback text where possible.
- Very long-running series can produce a large episode page when **All seasons** is selected.
- The project does not stream, host, or link to video episodes.

### External resources and assistance

- The television data, including show descriptions, episode information, ratings, cast details, and images, is provided by TVMaze under its stated CC BY-SA licensing terms.

- I used the official TVMaze API documentation to understand the available endpoints, query parameters, response structures, rate limits, and licensing conditions.

- The application was developed in Python using several open-source packages. Streamlit was used to build the user interface, Requests to communicate with the TVMaze API, pandas to organise and transform the returned data, Plotly to create rating charts, and pytest to test parts of the application.

- I used Git and GitHub for version control and to store the project repository. A Python virtual environment and the terminal were used to install dependencies, run the application, and execute the tests.

- I used OpenAI Codex and ChatGPT as AI development assistants. They supported me with brainstorming, translating my ideas into Python code, debugging errors, testing the application, improving the interface, and structuring the documentation. I remained responsible for defining the project idea, deciding which features should be included, reviewing the results, and directing the different development iterations.

- During the classes, Ricardo helped me understand how API connections work. His explanations gave me a clearer understanding of how an application sends requests to an API, how the API returns data, and how this data can then be used inside a program.

- No API keys or proprietary datasets are included in the project. The source code was created specifically for this project with AI assistance and the open-source libraries listed in requirements.txt.

## Data credit

Television data and images are provided by [TVMaze](https://www.tvmaze.com). This project is for educational purposes.
