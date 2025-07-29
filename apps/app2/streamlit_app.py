import streamlit as st
import json
import base64
from pathlib import Path
import html
import math

# Load apps.json
APPS_JSON_PATH = "apps.json"

try:
    with open(APPS_JSON_PATH, "r") as f:
        apps = json.load(f)
except FileNotFoundError:
    st.error(f"Could not find '{APPS_JSON_PATH}'. Please make sure the file exists.")
    apps = []
except json.JSONDecodeError as e:
    st.error(f"Failed to parse '{APPS_JSON_PATH}': {e}")
    apps = []

# Convert image to base64
def get_image_base64(img_path: str) -> str:
   img_file = Path(__file__).parent / img_path
   if not img_file.exists():
       return "https://via.placeholder.com/300x180?text=No+Preview"
   with open(img_file, "rb") as f:
       encoded = base64.b64encode(f.read()).decode()
       suffix = img_file.suffix.lower()
       mime = "image/png" if suffix == ".png" else "image/jpeg"
       return f"data:{mime};base64,{encoded}"

# Set page config
st.set_page_config(page_title="App Gallery", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <div class="centered-header">
        <h1 style="margin-bottom:0;">🚀 Streamlit App Gallery</h1>
        <div class="welcome-message">
            Welcome to the Streamlit App Gallery!<br>
            Discover, preview, and explore a curated collection of Streamlit apps.<br>
            Use the filters on the left to find apps by name, author, or tags.<br>
            Click on any app card to view details or source code.<br>
            We're here to help you find inspiration and useful tools for your data projects!
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Theme toggle and styling
st.markdown("""
<style>
.centered-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 32px;
}
.centered-header h1 {
    text-align: center;
    font-size: 2.6rem;
    margin-bottom: 0;
}
.welcome-message {
    text-align: center;
    font-size: 18px;
    margin-top: 10px;
    margin-bottom: 24px;
    color: #444;
    max-width: 700px;
}
.page-controls-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}
.page-info-badge {
    background: #f7f8fa;
    border-radius: 12px;
    padding: 12px 24px;
    margin-bottom: 18px;
    font-size: 17px;
    font-weight: 600;
    color: #333;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    text-align: center;
}
.page-buttons-row {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-bottom: 32px;
}
.stButton > button {
    min-width: 120px;
    min-height: 40px;
    font-size: 16px;
    white-space: nowrap;
}
@media (max-width: 600px) {
    .stButton > button {
        min-width: 100px;
        font-size: 15px;
    }
    .welcome-message {
        font-size: 16px;
        max-width: 95vw;
    }
}
body.light .app-card { background-color: #ffffff; color: #000000; }
body.dark .app-card { background-color: #1e1e1e; color: #ffffff; }
.theme-toggle {
    position: fixed;
    top: 15px;
    right: 30px;
    background: #ddd;
    color: #000;
    padding: 6px 14px;
    border-radius: 12px;
    border: 1px solid #ccc;
    font-weight: bold;
    cursor: pointer;
    z-index: 9999;
}
.app-wrapper {
    width: 100%;
    padding: 0 32px 32px 32px;
    box-sizing: border-box;
}
.app-grid {
    display: grid;
    width: 100%;
    grid-template-columns: 1fr;
    gap: 40px;
}
@media (min-width: 600px) {
    .app-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
@media (min-width: 900px) {
    .app-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
.app-card {
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    overflow: hidden;
    border: 3px solid transparent;
    transition: all 0.3s ease;
    position: relative;
    padding: 16px;
    box-sizing: border-box;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}
.app-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    border-color: var(--hover-border-color);
}
.app-card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    display: block;
}
.app-content { padding: 16px 20px 24px 20px; flex: 1 1 auto; }
.app-name { font-weight: 700; font-size: 18px; margin-bottom: 6px; }
.app-author { font-size: 14px; color: #888; margin-bottom: 6px; text-transform: capitalize; }
.app-description { font-size: 13px; color: #666; margin-bottom: 10px; }
.app-tags { margin-bottom: 12px; }
.tag {
    background-color: #efefef;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 12px;
    color: #444;
    display: inline-block;
    margin-right: 6px;
    margin-bottom: 6px;
}
.app-link {
    font-size: 14px;
    color: #0072ff;
    text-decoration: none;
    font-weight: 600;
}
.app-link:hover { text-decoration: underline; }
.new-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    background-color: #e91e63;
    color: white;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
</style>
<script>
   window.addEventListener("DOMContentLoaded", function() {
       const toggle = document.createElement("div");
       toggle.innerText = "Toggle Theme";
       toggle.className = "theme-toggle";
       toggle.onclick = function () {
           document.body.classList.toggle("dark");
           document.body.classList.toggle("light");
       };
       document.body.classList.add("light");
       document.body.appendChild(toggle);
   });
</script>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar.expander("🔎 Filters", expanded=True):
    search = st.text_input("Search apps by name, author, or tag")
    all_tags = sorted({tag for app in apps for tag in app.get("tags", [])})
    selected_tags = st.multiselect("Filter by tags", all_tags)

# Filter logic
filtered_apps = []
for app in apps:
   tags = app.get("tags", [])
   match_search = (
       not search or
       search.lower() in app.get("name", "").lower() or
       search.lower() in app.get("author", "").lower() or
       any(search.lower() in tag.lower() for tag in tags)
   )
   match_tags = not selected_tags or any(tag in tags for tag in selected_tags)
   if match_search and match_tags:
       filtered_apps.append(app)

# --- Pagination Logic ---
APPS_PER_PAGE = 6
total_pages = math.ceil(len(filtered_apps) / APPS_PER_PAGE)
if "page" not in st.session_state:
   st.session_state.page = 1

# Navigation functions
def go_prev():
   if st.session_state.page > 1:
       st.session_state.page -= 1

def go_next():
   if st.session_state.page < total_pages:
       st.session_state.page += 1

# Helper function to validate page bounds
def validate_page_bounds(total_pages):
    st.session_state.page = max(1, min(st.session_state.page, total_pages))

# Validate page bounds again just in case
validate_page_bounds(total_pages)
start = (st.session_state.page - 1) * APPS_PER_PAGE
end = start + APPS_PER_PAGE
paginated_apps = filtered_apps[start:end]
validate_page_bounds(total_pages)

# Ensure valid page
validate_page_bounds(total_pages)
start = (st.session_state.page - 1) * APPS_PER_PAGE
end = start + APPS_PER_PAGE
paginated_apps = filtered_apps[start:end]

# Show message if no results
if not filtered_apps:
    st.warning("No apps found. Try a different search or tag.")
else:
    st.markdown(
        f'''
        <div class="page-controls-container">
            <div class="page-info-badge">
                Page {st.session_state.page} of {total_pages} &bull; {len(filtered_apps)} app(s) found
            </div>
            <div class="page-buttons-row">
        ''',
        unsafe_allow_html=True
    )
    # Center both buttons in the middle column
    btn_cols = st.columns([2, 1, 2])
    with btn_cols[1]:
        col_prev, col_next = st.columns([1, 1], gap="small")
        with col_prev:
            st.button(
                "← Previous",
                on_click=go_prev,
                disabled=st.session_state.page <= 1
            )
        with col_next:
            st.button(
                "Next →",
                on_click=go_next,
                disabled=st.session_state.page >= total_pages
            )

# App grid layout
cards_html = '<div class="app-wrapper"><div class="app-grid">'
for app in paginated_apps:
    image_uri = get_image_base64(app.get("image", ""))
    app_name = html.escape(app.get("name", ""))
    app_author = html.escape(app.get("author", ""))
    app_url = html.escape(app.get("url", "#"))
    source_url = html.escape(app.get("source_url", "#"))
    app_desc = html.escape(app.get("description", ""))
    tags_html = " ".join([f"<span class='tag'>{html.escape(tag)}</span>" for tag in app.get("tags", [])])
    new_badge_html = '<div class="new-badge">NEW</div>' if app.get("new", False) else "<div></div>"

    cards_html += (
        f'<div class="app-card" style="--hover-border-color: {app.get("theme", "#4A90E2")}">'
        f'<a href="{app_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit;">'
        f'<div style="position: relative;">'
        f'<img src="{image_uri}" alt="{app_name} preview" />'
        f'{new_badge_html}'
        f'</div>'
        f'<div class="app-content">'
        f'<div class="app-name">{app_name}</div>'
        f'<div class="app-author">{app_author}</div>'
        f'<div class="app-description">{app_desc}</div>'
        f'<div class="app-tags">{tags_html}</div>'
        f'<a href="{source_url}" class="app-link" target="_blank" rel="noopener noreferrer">View source →</a>'
        f'</div>'
        f'</a>'
        f'</div>'
    )

cards_html += '</div></div>'
st.markdown(cards_html, unsafe_allow_html=True)
st.markdown("---")
st.markdown("Thanks for exploring! Contact us to suggest new apps or updates.")