from __future__ import annotations

import html as html_lib
import random
from typing import Any
from urllib.parse import urlencode

import pandas as pd
import plotly.express as px
import streamlit as st

from tvmaze_api import BASE_URL, TVMazeError, get_json, image_url, strip_html, year_from_date


st.set_page_config(
    page_title="What to watch",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: #080808; color: #f5f5f5; }
      [data-testid="stSidebar"] { background: #111; border-right: 1px solid #282828; }
      [data-testid="stSidebar"] * { color: #f5f5f5; }
      .block-container { max-width: 1440px; padding-top: 4.5rem; padding-bottom: 4rem; }
      [data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
      h1, h2, h3 { letter-spacing: -.025em; }
      h1 { font-size: clamp(2.7rem, 5vw, 5rem) !important; line-height: .95 !important; }
      .brand { color:#e50914; font-size:1.55rem; font-weight:900; letter-spacing:-.06em; }
      .eyebrow { color: #e50914; font: 800 .72rem monospace; letter-spacing: .16em; }
      .hero-copy { max-width: 760px; color: #c5c5c5; font-size: 1.08rem; line-height: 1.6; }
      .api-chip { display:inline-block; background:#292929; color:#fff; border:1px solid #414141; border-radius:20px; padding:.35rem .7rem; font:700 .72rem sans-serif; margin:.15rem .25rem .15rem 0; }
      .muted { color:#999; font-size:.86rem; }
      div[data-testid="stMetric"] { background:#171717; border:1px solid #2d2d2d; border-radius:12px; padding:1rem; }
      div[data-testid="stVerticalBlockBorderWrapper"] { background:#131313; border-color:#292929; border-radius:14px; }
      .stButton > button { border-radius:7px; border:1px solid #444; background:#222; color:#fff; font-weight:700; }
      .stButton > button:hover { border-color:#fff; color:#fff; transform:translateY(-1px); }
      .stButton > button[kind="primary"] { background:#e50914; color:white; border-color:#e50914; }
      [data-testid="stTextInput"] input { background:#161616; color:#fff; border:1px solid #484848; border-radius:8px; }
      [data-testid="stDataFrame"] { border:1px solid #292929; }
      [data-testid="stImage"] img { border-radius:10px; }
      .hero { min-height:250px; padding:2rem 0 1rem; }
      .rating { color:#65d46e; font-weight:800; }
      .episode-copy { color:#bbb; line-height:1.55; }
      footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def api(path: str, params_tuple: tuple[tuple[str, Any], ...] = ()) -> Any:
    """Cached wrapper: Streamlit avoids repeating identical API requests for one hour."""
    return get_json(path, dict(params_tuple))


def request_url(path: str, params: dict[str, Any] | None = None) -> str:
    query = f"?{urlencode(params)}" if params else ""
    return f"{BASE_URL}/{path.lstrip('/')}{query}"


def endpoint_note(path: str, params: dict[str, Any] | None = None) -> None:
    with st.expander("🧪 See the API request used"):
        st.code(f"GET {request_url(path, params)}", language="http")
        st.caption("The response is JSON. Identical calls are cached for one hour in this app.")


def safe_api(path: str, params: dict[str, Any] | None = None) -> Any | None:
    try:
        return api(path, tuple(sorted((params or {}).items())))
    except TVMazeError as exc:
        st.error(str(exc))
        return None


def show_label(show: dict[str, Any]) -> str:
    network = (show.get("network") or show.get("webChannel") or {}).get("name", "Unknown network")
    return f"{show.get('name', 'Untitled')} · {year_from_date(show.get('premiered'))} · {network}"


def select_show(show: dict[str, Any]) -> None:
    """Open a show and remember it so the details view survives reruns."""
    st.session_state.selected_show = show
    st.session_state.show_id = show["id"]
    st.session_state.page = "Show details"
    st.session_state.navigation = "Show details"
    history = st.session_state.setdefault("history", [])
    st.session_state.history = [show] + [item for item in history if item["id"] != show["id"]][:7]


def toggle_watchlist(show: dict[str, Any]) -> None:
    watchlist = st.session_state.setdefault("watchlist", [])
    if any(item["id"] == show["id"] for item in watchlist):
        st.session_state.watchlist = [item for item in watchlist if item["id"] != show["id"]]
    else:
        st.session_state.watchlist = [show, *watchlist]


def go_home() -> None:
    st.session_state.page = "Home"
    st.session_state.navigation = "Home"


def recommendation_pool() -> list[dict[str, Any]]:
    """Build varied shelves with only four paginated API requests."""
    shows: dict[int, dict[str, Any]] = {}
    for page in (0, 80, 160, 240):
        for show in safe_api("shows", {"page": page}) or []:
            if image_url(show) and (show.get("rating") or {}).get("average"):
                shows[show["id"]] = show
    return list(shows.values())


def poster_shelf(title: str, shows: list[dict[str, Any]], key: str, limit: int = 6) -> None:
    if not shows:
        return
    st.subheader(title)
    columns = st.columns(min(limit, len(shows)), gap="small")
    for index, show in enumerate(shows[:limit]):
        with columns[index]:
            st.image(image_url(show), width="stretch")
            rating = (show.get("rating") or {}).get("average")
            st.caption(f"★ {rating or '—'}  ·  {year_from_date(show.get('premiered'))}")
            st.button(
                show.get("name", "Untitled"),
                key=f"{key}-{show['id']}",
                width="stretch",
                on_click=select_show,
                args=(show,),
            )


def render_search() -> None:
    st.markdown('<div class="brand">WHAT TO WATCH</div>', unsafe_allow_html=True)
    query = st.text_input(
        "Search shows",
        value=st.session_state.get("search_query", ""),
        placeholder="Search for a series — try Severance, Dark or The Bear",
        label_visibility="collapsed",
    )
    st.session_state.search_query = query
    if len(query.strip()) < 2:
        return
    path, params = "search/shows", {"q": query.strip()}
    results = safe_api(path, params)
    if not results:
        st.warning("No matching series found. Try a different title.")
        return
    st.subheader(f"Search results for “{query.strip()}”")
    poster_shelf("", [item["show"] for item in results], "search", limit=min(6, len(results)))
    endpoint_note(path, params)


def render_discovery() -> None:
    render_search()
    pool = recommendation_pool()
    if not pool:
        st.info("Recommendations are temporarily unavailable. Search still works above.")
        return

    rated = sorted(pool, key=lambda item: (item.get("rating") or {}).get("average") or 0, reverse=True)
    hero = rated[0]
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    left, right = st.columns([1.7, 1], gap="large")
    with left:
        st.markdown('<p class="eyebrow">FEATURED TONIGHT</p>', unsafe_allow_html=True)
        st.title(hero["name"])
        st.markdown(f'<p class="hero-copy">{html_lib.escape(strip_html(hero.get("summary")))}</p>', unsafe_allow_html=True)
        genres = hero.get("genres") or ["Series"]
        st.markdown(" ".join(f'<span class="api-chip">{html_lib.escape(genre)}</span>' for genre in genres), unsafe_allow_html=True)
        st.caption(f"{year_from_date(hero.get('premiered'))} · ★ {(hero.get('rating') or {}).get('average') or '—'} · {hero.get('status') or 'Unknown'}")
        st.button("▶ View episodes", type="primary", on_click=select_show, args=(hero,))
    with right:
        st.image(image_url(hero, "original"), width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

    st.button(
        "🎲 Surprise me",
        help="Pick a random show from today's recommendation pool",
        on_click=select_show,
        args=(random.choice(pool),),
    )

    watchlist = st.session_state.get("watchlist", [])
    history = st.session_state.get("history", [])
    poster_shelf("My watchlist", watchlist, "watchlist")
    poster_shelf("Continue exploring", history, "history")
    poster_shelf("Top rated", rated, "top")
    for genre, key in (("Drama", "drama"), ("Comedy", "comedy"), ("Science-Fiction", "scifi"), ("Crime", "crime")):
        matches = [show for show in rated if genre in (show.get("genres") or [])]
        poster_shelf(f"{genre} picks", matches, key)


def episodes_frame(episodes: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for episode in episodes:
        rows.append(
            {
                "Season": episode.get("season"),
                "Episode": episode.get("number"),
                "Title": episode.get("name"),
                "Air date": episode.get("airdate"),
                "Runtime": episode.get("runtime"),
                "Rating": (episode.get("rating") or {}).get("average"),
                "Summary": strip_html(episode.get("summary")),
            }
        )
    return pd.DataFrame(rows)


def render_show_studio() -> None:
    show = st.session_state.get("selected_show")
    if not show:
        st.title("Choose a show first")
        st.write("Search or select a recommendation from Home to open its episode guide.")
        st.button("← Go to Home", on_click=go_home)
        return
    show_id = show["id"]
    with st.spinner("Loading episodes and cast from TVMaze…"):
        episodes = safe_api(f"shows/{show_id}/episodes", {"specials": 1}) or []
        cast = safe_api(f"shows/{show_id}/cast") or []
        crew = safe_api(f"shows/{show_id}/crew") or []

    st.button("← Back to browsing", on_click=go_home)
    poster, info = st.columns([1, 2.6], gap="large")
    with poster:
        if image_url(show, "original"):
            st.image(image_url(show, "original"), width="stretch")
    with info:
        st.markdown('<p class="eyebrow">NOW EXPLORING</p>', unsafe_allow_html=True)
        st.title(show["name"])
        rating = (show.get("rating") or {}).get("average")
        st.markdown(f'<span class="rating">★ {rating or "Not rated"}</span> &nbsp; {year_from_date(show.get("premiered"))} &nbsp; {show.get("status") or "—"}', unsafe_allow_html=True)
        st.write(strip_html(show.get("summary")))
        genres = show.get("genres") or ["Series"]
        st.markdown(" ".join(f'<span class="api-chip">{html_lib.escape(genre)}</span>' for genre in genres), unsafe_allow_html=True)
        network = (show.get("network") or show.get("webChannel") or {}).get("name", "Unknown platform")
        st.caption(f"{network} · {show.get('language') or 'Unknown language'} · TVMaze ID {show_id}")
        in_list = any(item["id"] == show_id for item in st.session_state.get("watchlist", []))
        st.button("✓ Remove from My List" if in_list else "+ Add to My List", on_click=toggle_watchlist, args=(show,))

    st.divider()
    tabs = st.tabs(["Episodes", "Cast & crew", "Ratings", "API data"])
    with tabs[0]:
        frame = episodes_frame(episodes)
        seasons = sorted({episode.get("season") for episode in episodes if episode.get("season") is not None})
        season_choice = st.selectbox("Season", ["All seasons", *seasons])
        visible = episodes if season_choice == "All seasons" else [item for item in episodes if item.get("season") == season_choice]
        st.caption(f"Showing {len(visible)} of {len(episodes)} episodes")
        for episode in visible:
            season = episode.get("season") or 0
            number = episode.get("number")
            code = f"S{season:02d}E{number:02d}" if number is not None else f"S{season:02d} Special"
            title = f"{code} · {episode.get('name') or 'Untitled episode'}"
            with st.expander(title):
                image_col, copy_col = st.columns([1, 2.5], gap="medium")
                with image_col:
                    if image_url(episode, "original"):
                        st.image(image_url(episode, "original"), width="stretch")
                with copy_col:
                    st.markdown(f"**{episode.get('airdate') or 'Air date unknown'}** · {episode.get('runtime') or '—'} min · ★ {(episode.get('rating') or {}).get('average') or '—'}")
                    st.markdown(f'<p class="episode-copy">{html_lib.escape(strip_html(episode.get("summary")))}</p>', unsafe_allow_html=True)
        st.download_button("Download episodes as CSV", frame.to_csv(index=False).encode("utf-8"), f"{show['name'].lower().replace(' ', '-')}-episodes.csv", "text/csv")
        endpoint_note(f"shows/{show_id}/episodes", {"specials": 1})

    with tabs[1]:
        st.subheader("Main cast")
        cols = st.columns(min(6, max(1, len(cast))))
        for index, credit in enumerate(cast[:18]):
            person, character = credit["person"], credit["character"]
            with cols[index % len(cols)]:
                if image_url(person):
                    st.image(image_url(person), width="stretch")
                st.markdown(f"**{person['name']}**")
                st.caption(f"as {character['name']}")
        crew_frame = pd.DataFrame([{"Name": item["person"]["name"], "Role": item["type"]} for item in crew])
        if not crew_frame.empty:
            st.subheader("Crew")
            st.dataframe(crew_frame, width="stretch", hide_index=True)

    with tabs[2]:
        frame = episodes_frame(episodes)
        rated = frame.dropna(subset=["Rating"]) if not frame.empty else frame
        if rated.empty:
            st.info("No episode-level ratings are available for this show.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Episodes", len(frame))
            c2.metric("Seasons", int(frame["Season"].nunique()))
            c3.metric("Average rating", f"{rated['Rating'].mean():.2f}")
            rated = rated.copy()
            rated["Episode order"] = range(1, len(rated) + 1)
            chart = px.line(rated, x="Episode order", y="Rating", color="Season", hover_data=["Title", "Air date"], markers=True)
            chart.update_layout(paper_bgcolor="#080808", plot_bgcolor="#111", font_color="#eee")
            st.plotly_chart(chart, width="stretch")

    with tabs[3]:
        st.caption("Inspect the unmodified JSON returned by TVMaze.")
        resource = st.radio("Resource", ["Show", "Episodes", "Cast", "Crew"], horizontal=True)
        st.json({"Show": show, "Episodes": episodes, "Cast": cast, "Crew": crew}[resource], expanded=False)


def render_people() -> None:
    st.markdown('<p class="eyebrow">04 · PEOPLE + EMBEDDED CREDITS</p>', unsafe_allow_html=True)
    st.title("Career Mapper")
    query = st.text_input("Search for an actor or creator", "Pedro Pascal")
    if len(query.strip()) < 2:
        return
    path, params = "search/people", {"q": query.strip()}
    results = safe_api(path, params)
    endpoint_note(path, params)
    if not results:
        st.warning("No people matched that search.")
        return
    people = [item["person"] for item in results]
    person = st.selectbox("Choose a person", people, format_func=lambda item: item["name"])
    credits = safe_api(f"people/{person['id']}/castcredits", {"embed": "show"}) or []
    left, right = st.columns([1, 3], gap="large")
    with left:
        if image_url(person, "original"):
            st.image(image_url(person, "original"), width="stretch")
        st.caption(f"Born: {person.get('birthday') or '—'} · Country: {(person.get('country') or {}).get('name', '—')}")
    with right:
        st.header(person["name"])
        shows = [item.get("_embedded", {}).get("show") for item in credits]
        shows = [show for show in shows if show]
        frame = pd.DataFrame([{"Show": show["name"], "Premiered": show.get("premiered"), "Status": show.get("status"), "Rating": (show.get("rating") or {}).get("average"), "Genres": ", ".join(show.get("genres") or [])} for show in shows])
        st.metric("TV series credits", len(frame))
        if not frame.empty:
            st.dataframe(frame.sort_values("Premiered", ascending=False, na_position="last"), width="stretch", hide_index=True)
    endpoint_note(f"people/{person['id']}/castcredits", {"embed": "show"})


PAGES = {
    "Home": render_discovery,
    "Show details": render_show_studio,
    "People": render_people,
}

with st.sidebar:
    st.markdown('<div class="brand">WHAT TO WATCH</div>', unsafe_allow_html=True)
    st.caption("Explore television through live API data")
    st.divider()
    default_page = st.session_state.get("page", "Home")
    if "navigation" not in st.session_state or st.session_state.navigation not in PAGES:
        st.session_state.navigation = default_page if default_page in PAGES else "Home"
    page = st.radio(
        "Navigate",
        list(PAGES),
        label_visibility="collapsed",
        key="navigation",
    )
    st.session_state.page = page
    st.divider()
    watchlist_count = len(st.session_state.get("watchlist", []))
    st.markdown(f"**My List · {watchlist_count} shows**")
    st.caption("Search, save, inspect episodes, explore cast and analyze ratings.")
    st.divider()
    st.caption("Built with Streamlit + the public TVMaze REST API")
    st.markdown("[TVMaze API documentation](https://www.tvmaze.com/api)")

PAGES[page]()

st.divider()
st.caption("Data provided by TVMaze under CC BY-SA. Built as an educational project; no API key is required.")
