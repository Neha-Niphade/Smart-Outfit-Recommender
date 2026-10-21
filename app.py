"""Streamlit user interface for the Smart Outfit Recommender."""
import html

import streamlit as st

from rules import (
    OCCASIONS,
    PALETTES,
    PREFERENCES,
    STYLES,
    WEATHERS,
    recommend,
)

st.set_page_config(page_title="Outfit Adventure Club", page_icon="🧢", layout="wide")

WEATHER_ICON = {
    "Sunny": "☀️",
    "Cloudy": "☁️",
    "Rainy": "🌧️",
    "Windy": "💨",
    "Snowy": "❄️",
    "Humid": "💦",
}
OCCASION_ICON = {"College": "🎒", "Formal": "💼", "Party": "🎉", "Casual": "🛋️"}
STYLE_ICON = {"Minimal": "⚪", "Classic": "🧥", "Streetwear": "🛹", "Sporty": "🏃", "Ethnic Fusion": "🪔"}
T_MIN, T_MAX = -5, 45
PAGES = ["🏠 Home", "✨ Outfit Maker", "📚 Style Book", "🧠 How It Works", "🌟 About"]

st.markdown(
    """<style>
#MainMenu, footer {visibility:hidden;}
.block-container {padding-top:1.6rem; max-width:1200px;}
[data-testid="stSidebar"] {border-right:3px solid rgba(124,58,237,.15);}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2 {color:#6d28d9;}
.hero{border-radius:30px;padding:38px 42px;color:#fff;background:linear-gradient(120deg,#6d28d9 0%,#db2777 55%,#f59e0b 100%);box-shadow:0 20px 50px -20px rgba(219,39,119,.55);margin-bottom:22px;position:relative;overflow:hidden}
.hero h1{margin:0;font-size:2.6rem;font-weight:800;letter-spacing:-.02em;color:#fff;padding:0}
.hero p{margin:8px 0 0;font-size:1.05rem;opacity:.93;color:#fff}
.hero .orb{position:absolute;right:-60px;top:-70px;width:250px;height:250px;border-radius:50%;background:rgba(255,255,255,.15)}
.hero .orb2{position:absolute;right:120px;bottom:-90px;width:160px;height:160px;border-radius:50%;background:rgba(255,255,255,.10)}
.eyebrow{color:#7c3aed;text-transform:uppercase;letter-spacing:.14em;font-weight:800;font-size:.8rem;margin-bottom:6px}
.kid-card{border-radius:24px;padding:24px 22px;height:100%;background:rgba(127,127,127,.08);border:2px solid rgba(124,58,237,.18);box-shadow:0 8px 0 rgba(124,58,237,.08)}
.kid-card h3{margin:4px 0 8px;color:#6d28d9}
.kid-card p{margin:0;line-height:1.55}
.big-emoji{font-size:2.8rem}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 6px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:999px;font-size:.88rem;font-weight:600;background:rgba(124,58,237,.12);border:1px solid rgba(124,58,237,.3)}
.chip.acc{background:rgba(245,158,11,.14);border-color:rgba(245,158,11,.45)}
.meter-wrap{margin:14px 0 26px;padding:0 6px}
.meter{position:relative;height:10px;border-radius:99px;background:linear-gradient(90deg,#60a5fa,#34d399 40%,#fbbf24 70%,#ef4444)}
.pin{position:absolute;top:-7px;width:24px;height:24px;border-radius:50%;background:#fff;border:4px solid #7c3aed;transform:translateX(-50%);box-shadow:0 4px 10px rgba(0,0,0,.3)}
.meter-labels{display:flex;justify-content:space-between;font-size:.75rem;opacity:.65;margin-top:12px}
.card{border-radius:22px;padding:22px 20px;height:100%;background:rgba(127,127,127,.08);border:1px solid rgba(127,127,127,.22);transition:transform .2s ease, box-shadow .2s ease}
.card:hover,.kid-card:hover{transform:translateY(-5px);box-shadow:0 18px 36px -18px rgba(124,58,237,.65)}
.card .ico{font-size:2.3rem}.card .lbl{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;opacity:.6;margin-top:8px;font-weight:700}.card .val{font-size:1.08rem;font-weight:700;margin-top:4px;line-height:1.35}
.panel{border-radius:22px;padding:20px 22px;background:rgba(127,127,127,.08);border:1px solid rgba(127,127,127,.22);height:100%}.panel h4{margin:0 0 12px;font-size:1rem;padding:0}
.swatches{display:flex;gap:10px;margin:12px 0 4px}.swatch{width:38px;height:38px;border-radius:50%;border:2px solid rgba(255,255,255,.75);box-shadow:0 3px 8px rgba(0,0,0,.25)}
.summary{border-left:5px solid #db2777;padding:14px 18px;border-radius:12px;background:rgba(219,39,119,.08);margin:22px 0 10px;font-size:1.02rem}
.rule{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px dashed rgba(127,127,127,.3);font-size:.94rem}
.badge{flex:none;min-width:38px;text-align:center;padding:3px 8px;border-radius:8px;font-weight:800;font-size:.78rem;color:#fff;background:#7c3aed}
.badge.R2{background:#db2777}.badge.R3{background:#0ea5e9}.badge.R4{background:#f59e0b}
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button{width:100%;border-radius:14px;font-weight:700;padding:.6rem 0;background:linear-gradient(120deg,#7c3aed,#db2777);color:#fff;border:0}
</style>""",
    unsafe_allow_html=True,
)


def go_to(page):
    st.session_state["page"] = page
    st.rerun()


def show_hero(title, subtitle):
    st.markdown(
        f"""<div class="hero"><div class="orb"></div><div class="orb2"></div>
<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>""",
        unsafe_allow_html=True,
    )


def show_outfit_result(res, inp):
    chips = [
        f'{WEATHER_ICON[inp["weather"]]} {inp["weather"]}',
        f'{OCCASION_ICON[inp["occasion"]]} {inp["occasion"]}',
        f'{STYLE_ICON[inp["style"]]} {inp["style"]}',
        f'🌡️ {inp["temp"]}°C · {res["band"].title()}',
    ]
    chip_html = "".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips)
    chip_html += "".join(f'<span class="chip acc">{html.escape(p)}</span>' for p in inp["prefs"])
    pct = (inp["temp"] - T_MIN) / (T_MAX - T_MIN) * 100
    st.markdown(
        f'<div class="chips">{chip_html}</div><div class="meter-wrap"><div class="meter">'
        f'<div class="pin" style="left:{pct:.1f}%"></div></div><div class="meter-labels">'
        f"<span>🥶 {T_MIN}°C</span><span>🧣 10°C</span><span>🌤️ 18°C</span>"
        f'<span>😎 25°C</span><span>🔥 {T_MAX}°C</span></div></div>',
        unsafe_allow_html=True,
    )
    for warning in res["warnings"]:
        st.warning(warning)

    cards = [
        ("👕", "Top", res["top"]),
        ("👖", "Bottom", res["bottom"]),
        ("👟", "Footwear", res["footwear"]),
        ("🧥", "Outer layer", res["outer"] or "No extra layer needed"),
    ]
    for col, (icon, label, value) in zip(st.columns(4, gap="medium"), cards):
        col.markdown(
            f'<div class="card"><div class="ico">{icon}</div><div class="lbl">{label}</div>'
            f'<div class="val">{html.escape(value)}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    left, right = st.columns(2, gap="medium")
    accessories = "".join(f'<span class="chip acc">{html.escape(a)}</span>' for a in res["accessories"])
    left.markdown(
        f'<div class="panel"><h4>🕶️ Optional accessories</h4><div class="chips">{accessories}</div></div>',
        unsafe_allow_html=True,
    )
    swatches = "".join(f'<div class="swatch" style="background:{c}"></div>' for c in res["palette_colors"])
    right.markdown(
        f'<div class="panel"><h4>🎨 Colour palette</h4><div class="swatches">{swatches}</div>'
        f'<div>{html.escape(res["palette_name"])}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="summary">💡 <b>Why this outfit?</b> {html.escape(res["summary"])}</div>',
        unsafe_allow_html=True,
    )
    with st.expander("🧠 See the exact rules that fired", expanded=True):
        rows = "".join(
            f'<div class="rule"><span class="badge {rid}">{rid}</span><span>{html.escape(text)}</span></div>'
            for rid, text in res["trace"]
        )
        st.markdown(rows, unsafe_allow_html=True)
        st.caption("R1 = temperature + occasion · R2 = style · R3 = preferences · R4 = weather")

    lines = [
        f"Outfit Adventure Club - {inp['temp']}°C, {inp['weather']}, {inp['occasion']}, {inp['style']}",
        "",
        f"Top: {res['top']}",
        f"Bottom: {res['bottom']}",
        f"Footwear: {res['footwear']}",
        f"Outer layer: {res['outer'] or 'None'}",
        f"Accessories: {', '.join(res['accessories'])}",
        f"Palette: {res['palette_name']}",
        "",
        "Why:",
    ] + [f"- [{rule_id}] {text}" for rule_id, text in res["trace"]]
    st.download_button("⬇️ Take this outfit plan home", "\n".join(lines), file_name="my_outfit.txt")


def render_home():
    show_hero("🧢 Welcome to Outfit Adventure Club!", "Pick a page, try some ideas, and discover your perfect outfit.")
    st.markdown('<div class="eyebrow">Your tiny fashion mission</div><h2>What do you want to explore?</h2>', unsafe_allow_html=True)
    columns = st.columns(3, gap="medium")
    cards = [
        ("✨", "Make an outfit", "Tell us the weather and your vibe. We will build a complete look.", "✨ Outfit Maker"),
        ("📚", "Learn your style", "Explore colours, occasions and fun tips for getting dressed.", "📚 Style Book"),
        ("🧠", "Become a rule detective", "See how simple IF–ELSE clues help choose each clothing item.", "🧠 How It Works"),
    ]
    for col, (icon, title, text, page) in zip(columns, cards):
        with col:
            st.markdown(
                f'<div class="kid-card"><div class="big-emoji">{icon}</div><h3>{title}</h3><p>{text}</p></div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Go to {title} →", key=f"home-{page}"):
                go_to(page)
    st.write("")
    st.info("🌈 Tip: There is no one “right” style. The best outfit is one that makes you feel comfortable and happy!")


def render_outfit_maker():
    show_hero("✨ Outfit Maker", "Answer five tiny questions and your outfit adventure is ready!")
    with st.sidebar:
        st.markdown("## 🎛️ Plan your day")
        with st.form("inputs"):
            temp = st.slider("🌡️ Temperature (°C)", T_MIN, T_MAX, 24)
            weather = st.selectbox("🌦️ Weather", WEATHERS, format_func=lambda w: f"{WEATHER_ICON[w]}  {w}")
            occasion = st.selectbox("📍 Occasion", OCCASIONS, format_func=lambda o: f"{OCCASION_ICON[o]}  {o}")
            style = st.selectbox("🎨 Preferred style", STYLES, format_func=lambda s: f"{STYLE_ICON[s]}  {s}")
            prefs = st.multiselect("💬 Clothing preferences (optional)", PREFERENCES)
            submitted = st.form_submit_button("✨ Recommend my outfit")
        st.caption("Rule-based AI: every answer comes from readable IF–ELSE rules, no black box.")

    if submitted or "last_result" not in st.session_state:
        st.session_state["last_result"] = recommend(temp, weather, occasion, style, prefs)
        st.session_state["last_inputs"] = dict(temp=temp, weather=weather, occasion=occasion, style=style, prefs=prefs)
    show_outfit_result(st.session_state["last_result"], st.session_state["last_inputs"])


def render_style_book():
    show_hero("📚 The Style Book", "A colourful little guide to outfits, colours and occasions.")
    st.markdown('<div class="eyebrow">Choose your character</div><h2>Five style worlds</h2>', unsafe_allow_html=True)
    descriptions = {
        "Minimal": ("🫧", "Keep it simple", "Solid colours, clean shapes and no loud logos."),
        "Classic": ("🎩", "Timeless explorer", "Polos, Oxford shirts and colours that always look neat."),
        "Streetwear": ("🛹", "City adventurer", "Oversized tops, baggy bottoms and chunky sneakers."),
        "Sporty": ("🏅", "Energy champion", "Breathable clothes, track pants and ready-to-run shoes."),
        "Ethnic Fusion": ("🪔", "Culture creator", "Kurta-inspired pieces mixed with comfy modern clothes."),
    }
    for row in range(0, len(STYLES), 2):
        for col, style in zip(st.columns(2, gap="medium"), STYLES[row:row + 2]):
            icon, title, text = descriptions[style]
            palette_name, _ = PALETTES[style]
            col.markdown(
                f'<div class="kid-card"><div class="big-emoji">{icon}</div><h3>{title}</h3>'
                f'<p>{text}</p><p><b>Colour quest:</b> {html.escape(palette_name)}</p></div>',
                unsafe_allow_html=True,
            )
        st.write("")
    st.markdown('<div class="eyebrow">Quick outfit tips</div><h2>Little rules, big difference</h2>', unsafe_allow_html=True)
    tips = ["☀️ Sunny day? Remember sunglasses and sunscreen.", "🌧️ Rainy day? Keep your feet and socks dry.", "🎒 College day? A backpack is your trusty sidekick.", "🎉 Party day? Add one fun statement item.", "🧣 Cold day? Layers are like a warm hug."]
    for tip in tips:
        st.markdown(f'<div class="rule"><span>{tip}</span></div>', unsafe_allow_html=True)


def render_how_it_works():
    show_hero("🧠 How It Works", "Meet the four friendly rules hiding behind every recommendation.")
    st.markdown("### Think of the app as a super-organised friend")
    st.write("It checks clues in order. Each clue adds a better idea, and weather gets the final say so your outfit stays safe and comfy.")
    steps = [
        ("1️⃣", "R1: Check the temperature", "Cold, mild or hot? This chooses a starting outfit for the occasion."),
        ("2️⃣", "R2: Add your style", "Sporty, classic, streetwear and more change the shape and vibe."),
        ("3️⃣", "R3: Listen to you", "Preferences such as relaxed fit or avoiding jeans personalise the look."),
        ("4️⃣", "R4: Watch the sky", "Rain, snow, sun and wind add the final comfort and safety touches."),
    ]
    for icon, title, text in steps:
        st.markdown(
            f'<div class="kid-card" style="margin:12px 0"><div class="big-emoji">{icon}</div>'
            f'<h3>{title}</h3><p>{text}</p></div>',
            unsafe_allow_html=True,
        )
    st.success("🎯 The secret: the same answers always create the same outfit. That makes this project predictable and easy to test!")


def render_about():
    show_hero("🌟 About This Project", "A small, explainable AI project made for curious learners.")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("### 🧩 What is inside?")
        st.write("This app is a rule-based expert system. It uses Python, Streamlit and friendly IF–ELSE rules instead of a mysterious black box.")
        st.markdown("### 🎒 Why is it useful?")
        st.write("It helps practise inputs, decisions, dictionaries, functions and testing while solving a fun everyday problem.")
    with right:
        st.markdown("### 🌈 Project powers")
        for label, value in [("Weather choices", len(WEATHERS)), ("Occasions", len(OCCASIONS)), ("Style worlds", len(STYLES)), ("Personal preferences", len(PREFERENCES))]:
            st.metric(label, value)
    st.write("")
    st.info("💡 Want to make it bigger? Add a favourite-colour question, a wardrobe page or a special festival occasion!")


with st.sidebar:
    st.markdown("# 🧢 Outfit Club")
    st.caption("A tiny style adventure")
    if "page" not in st.session_state:
        st.session_state["page"] = PAGES[0]
    selected_page = st.radio("Explore", PAGES, index=PAGES.index(st.session_state["page"]))
    if selected_page != st.session_state["page"]:
        st.session_state["page"] = selected_page
        st.rerun()
    st.divider()
    st.caption("Made with Python + Streamlit 💜")

page = st.session_state["page"]
if page == "🏠 Home":
    render_home()
elif page == "✨ Outfit Maker":
    render_outfit_maker()
elif page == "📚 Style Book":
    render_style_book()
elif page == "🧠 How It Works":
    render_how_it_works()
else:
    render_about()
