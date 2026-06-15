import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="PageLens", page_icon="🔍")
st.title("🔍 PageLens")
st.caption("Analyse any webpage and pull out the content you need.")

url = st.text_input("Enter a website URL:", placeholder="https://example.com")

data_type = st.selectbox("What would you like to analyse?", [
    "Headings (h1, h2, h3)",
    "All Paragraphs",
    "All Links",
    "Page Title & Meta Description"
])

if st.button("Analyse"):
    if not url.strip():
        st.error("Please enter a URL.")
    else:
        try:
            with st.spinner("Fetching page content..."):
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

            if data_type == "Headings (h1, h2, h3)":
                rows = []
                for tag in soup.find_all(["h1", "h2", "h3"]):
                    rows.append({"Tag": tag.name.upper(), "Text": tag.get_text(strip=True)})
                df = pd.DataFrame(rows)

            elif data_type == "All Paragraphs":
                texts = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
                df = pd.DataFrame({"Paragraph": texts})

            elif data_type == "All Links":
                links = []
                for a in soup.find_all("a", href=True):
                    links.append({"Text": a.get_text(strip=True), "URL": a["href"]})
                df = pd.DataFrame(links)

            else:
                title = soup.title.string if soup.title else "N/A"
                meta = soup.find("meta", attrs={"name": "description"})
                desc = meta["content"] if meta else "N/A"
                df = pd.DataFrame({"Field": ["Title", "Meta Description"], "Value": [title, desc]})

            if df.empty:
                st.warning("No content found for that selection.")
            else:
                st.success(f"✅ Found {len(df)} result(s)")
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False)
                st.download_button("⬇️ Download as CSV", csv, "results.csv", "text/csv")

        except Exception as e:
            st.error(f"Something went wrong: {e}")