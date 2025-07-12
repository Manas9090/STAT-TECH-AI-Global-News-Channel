import streamlit as st
import requests
import openai
import time
from gtts import gTTS
import tempfile

# --- CONFIG ---
openai.api_key = st.secrets["openai_api_key"]
news_api_key = st.secrets["news_api_key"]

# --- Country Codes ---
COUNTRIES = {
    "Global 🌍": None,
    "India 🇮🇳": "in",
    "United States 🇺🇸": "us",
    "United Kingdom 🇬🇧": "gb",
    "Australia 🇦🇺": "au",
    "Canada 🇨🇦": "ca",
    "Germany 🇩🇪": "de",
    "France 🇫🇷": "fr",
    "Japan 🇯🇵": "jp",
    "China 🇨🇳": "cn",
    "Brazil 🇧🇷": "br",
    "South Africa 🇿🇦": "za"
}

# --- News Categories ---
CATEGORIES = {
    "All 📰": None,
    "Business 💼": "business",
    "Entertainment 🎬": "entertainment",
    "General 🗞️": "general",
    "Health 🏥": "health",
    "Science 🔬": "science",
    "Sports ⚽": "sports",
    "Technology 💻": "technology"
}

# --- Language Map ---
language_map = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Gujarati": "gu",
    "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml",
    "Marathi": "mr", "Punjabi": "pa"
}

# --- Category YouTube Videos ---
category_videos = {
    "Politics": "https://www.youtube.com/embed/B56ixwzMuQs",
    "Economy": "https://www.youtube.com/embed/78F_w4sk1x8",
    "Entertainment": "https://www.youtube.com/embed/ZajzYJ9dOUM",
    "Technology": "https://www.youtube.com/embed/wCgD7LqBIDM",
    "Sports": "https://www.youtube.com/embed/JWqEKMnQG2g",
    "Other": "https://www.youtube.com/embed/HtTUsOKjWyQ"
}

# --- Streamlit Page Config ---
st.set_page_config(page_title="🗞️ Categorization & Summarization", layout="wide")

# --- Custom Title ---
st.markdown("""
<div style='text-align: center; padding: 10px 0;'>
<span style='font-size:28px; color:#8F00FF; font-weight:bold;'>Categorization & Summarization</span>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Filters & Options")
    country_name = st.selectbox("🌍 Select Country", list(COUNTRIES.keys()))
    country_code = COUNTRIES[country_name]

    category_name = st.selectbox("🗂️ Select News Type", list(CATEGORIES.keys()))
    category_code = CATEGORIES[category_name]

    search_query = st.text_input("🔍 Keyword Search (Optional)")

    summary_lang = st.selectbox("🗣️ Summary Language", list(language_map.keys()))
    enable_audio = st.checkbox("🔊 Enable Audio Summary")
    show_raw_json = st.checkbox("🛠️ Show Raw JSON (Debug)", key="raw_json_checkbox")

# --- Fetch News ---
def fetch_news(query=None, country=None, category=None):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": news_api_key,
        "language": "en",
        "pageSize": 20
    }
    if country:
        params["country"] = country
    if category:
        params["category"] = category
    if query:
        params["q"] = query

    response = requests.get(url, params=params)
    data = response.json()
    if "articles" not in data:
        st.error(f"❌ NewsAPI Error: {data.get('message', 'Unknown error')}")
        return []
    return data.get("articles", [])

# --- Categorize ---
def categorize_news(title, description):
    try:
        prompt = f"""
        Categorize this news into [Politics, Economy, Entertainment, Technology, Sports, Other]:

        Title: {title}
        Description: {description}

        Category:
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip()
    except:
        return "Other"

# --- Summarize ---
def summarize_news(title, description, lang="English"):
    try:
        prompt = f"""
        Summarize this news in 2-3 lines in {lang} for quick understanding:

        Title: {title}
        Description: {description}

        Summary:
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response["choices"][0]["message"]["content"].strip()
    except:
        return description[:150] + "..."

# --- Fetch News ---
news_data = fetch_news(query=search_query, country=country_code, category=category_code)

if show_raw_json:
    st.write(news_data)

# --- Show Articles ---
if not news_data:
    st.warning("⚠️ No news found. Try changing filters or keywords.")
else:
    st.success(f"✅ Showing {len(news_data)} latest articles from **{country_name}**, Category: **{category_name}**")

    for idx, article in enumerate(news_data):
        title = article.get("title", "No Title")
        description = article.get("description", "No description available.")
        url = article.get("url", "")
        image_url = article.get("urlToImage", "")
        published_at = article.get("publishedAt", "")

        styled_title = f"<span style='font-size:22px; color:#0047AB; font-weight:bold;'>📰 {title}</span>"
        st.markdown(styled_title, unsafe_allow_html=True)

        with st.expander("📝 Details"):
            if image_url:
                st.image(image_url, use_container_width=True)
            st.caption(f"🕒 Published: {published_at}")
            st.write(description)
            if url:
                st.markdown(f"[🌐 Read Full Article]({url})")

# --- AI Categorization & Summary ---
if news_data and st.button("💡 AI Categorize & Summarize All"):
    with st.spinner("🧠 GPT processing..."):
        categorized = {"Politics": [], "Economy": [], "Entertainment": [], "Technology": [], "Sports": [], "Other": []}

        for idx, article in enumerate(news_data):
            title = article.get("title", "No Title")
            description = article.get("description", "")
            url = article.get("url", "")
            category = categorize_news(title, description)
            summary = summarize_news(title, description, lang=summary_lang)
            categorized.setdefault(category, []).append((title, summary, description, url))
            time.sleep(1)

    st.subheader("🔎 AI-Powered Categorized News")
    for cat, items in categorized.items():
        if items:
            st.markdown(f"<h3 style='color:#D90429;'>📂 {cat} News</h3>", unsafe_allow_html=True)

            for title, summary, description, url in items:
                styled_title = f"<span style='font-size:20px; color:#1E1E1E; font-weight:bold;'>📰 {title}</span>"
                st.markdown(styled_title, unsafe_allow_html=True)

                with st.expander("📝 Details"):
                    st.write(f"**Summary:** {summary}")
                    if enable_audio:
                        tts_lang = language_map.get(summary_lang, "en")
                        tts = gTTS(summary, lang=tts_lang)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                            st.audio(fp.name)
                    if url:
                        st.markdown(f"[🌐 Read Full Article]({url})")
                    st.write(description)

            # --- YouTube Video per Category ---
            if cat in category_videos:
                st.markdown("🎥 **Watch more about this category:**")
                st.video(category_videos[cat])
