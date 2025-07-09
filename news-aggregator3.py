import streamlit as st 
import requests
import openai
import time

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

# --- Categorize with GPT ---
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

# --- Summarize with GPT ---
def summarize_news(title, description):
    try:
        prompt = f"""
        Summarize this news in 2-3 lines for quick understanding:

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

# --- Streamlit UI ---
st.set_page_config(page_title="🗞️ STAT-TECH-AI News", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Filters & Options")
    country_name = st.selectbox("🌍 Select Country", list(COUNTRIES.keys()))
    country_code = COUNTRIES[country_name]

    category_name = st.selectbox("🗂️ Select News Type", list(CATEGORIES.keys()))
    category_code = CATEGORIES[category_name]

    search_query = st.text_input("🔍 Keyword Search (Optional)")

    st.markdown("---")
    show_raw_json = st.checkbox("🛠️ Show Raw JSON (Debug)", key="raw_json_checkbox")

# --- Violet Colored Stylish Title ---
custom_title = """
<div style='text-align: center; padding: 10px 0;'>
<span style='font-size:28px; color:#8F00FF; font-weight:bold;'>STAT-TECH-AI: Your Global News Channel</span>
</div>
"""
st.markdown(custom_title, unsafe_allow_html=True)

# --- Fetch News ---
news_data = fetch_news(query=search_query, country=country_code, category=category_code)

if show_raw_json:
    st.write(news_data)

# --- Display Stylish News ---
if not news_data:
    st.warning("⚠️ No news found. Try changing filters or keywords.")
else:
    st.success(f"✅ Showing {len(news_data)} latest articles from **{country_name}**, Category: **{category_name}**")

    for idx, article in enumerate(news_data):
        title = article.get("title", "No Title")
        description = article.get("description", "No description available.")
        url = article.get("url", "")
        image_url = article.get("urlToImage", "")

        styled_title = f"<span style='font-size:22px; color:#0047AB; font-weight:bold;'>📰 {title}</span>"
        st.markdown(styled_title, unsafe_allow_html=True)

        with st.expander("📝 Details"):
            if image_url:
                st.image(image_url, use_container_width=True)
            st.write(description)
            if url:
                st.markdown(f"[🌐 Read Full Article]({url})")

# --- AI Categorize & Summarize ---
if news_data and st.button("💡 AI Categorize & Summarize All"):
    with st.spinner("🧠 GPT-4 Processing... Please wait..."):
        categorized = {"Politics": [], "Economy": [], "Entertainment": [], "Technology": [], "Sports": [], "Other": []}

        for idx, article in enumerate(news_data):
            title = article.get("title", "No Title")
            description = article.get("description", "")
            url = article.get("url", "")
            category = categorize_news(title, description)
            summary = summarize_news(title, description)
            categorized.setdefault(category, []).append((title, summary, description, url))
            time.sleep(1)  # Respect API limits

    st.subheader("🔎 AI-Powered Categorized News")
    for cat, items in categorized.items():
        if items:
            st.subheader(f"📂 {cat} News")
            for idx, (title, summary, description, url) in enumerate(items):
                styled_title = f"<span style='font-size:20px; color:#D90429; font-weight:bold;'>📰 {title}</span>"
                st.markdown(styled_title, unsafe_allow_html=True)

                with st.expander("📝 Details"):
                    st.write(f"**Summary:** {summary}")
                    if url:
                        st.markdown(f"[🌐 Read Full Article]({url})")
                    st.write(description)
