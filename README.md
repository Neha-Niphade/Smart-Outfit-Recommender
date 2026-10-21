# 👗 Smart Outfit Recommender: Rule-Based AI System

**TL;DR:** You give it temperature, weather, occasion, style and preferences. It runs a chain of readable IF–ELSE rules and returns a top, bottom, footwear, optional layer and accessories, plus the exact rules that fired. No ML, no APIs, no training data.

---

## 1. Problem Statement and Objectives

**Problem:** Choosing what to wear means juggling weather, temperature, occasion and personal taste. People often end up too hot, too cold, wet, or under- or over-dressed.

**Objectives**
1. Recommend a complete outfit (top, bottom, footwear, layer, accessories).
2. Use an **explainable** rule-based AI technique (`IF–ELSE`), so every output can be justified.
3. Support 5 temperature bands, 6 weather types, 4 occasions, 5 styles and 8 gender-neutral preferences.
4. Show a short explanation (the "rule trace") with every recommendation.
5. Build it with only Python and Streamlit, simple enough for undergraduates to explain.

## 2. Abstract

The Smart Outfit Recommender is a knowledge-based expert system. Domain knowledge about clothing is stored as dictionaries (facts) and `IF–ELSE` rules (inference). The user provides temperature, weather, occasion, style and optional preferences. The engine picks a base outfit from a lookup table, then applies style, preference and weather rules in a fixed order. Weather rules come last because safety and comfort must override fashion. The result is shown in a Streamlit interface together with a human-readable explanation of every rule that fired. The system needs no data, no training and no internet, and its behaviour is fully predictable and testable.

## 3. Introduction

*Analogy:* think of a very organised friend with a checklist: "If it is raining, wear waterproof shoes. If it is a formal event, no sneakers." That checklist is a **rule base**. An **expert system** is software that stores such expert knowledge and applies it to new situations.

Why rule-based instead of machine learning?
- **Explainable:** you can point to the exact rule behind every suggestion.
- **No data needed:** there is no dataset of "good outfits" to collect or label.
- **Deterministic:** the same input always gives the same output, so it is easy to test.
- **Beginner-friendly:** the whole logic fits in one readable file.

## 4. System Architecture and Workflow

```
 ┌────────────────────┐   ┌─────────────────────────────────────┐   ┌─────────────────────┐
 │  Streamlit UI      │   │          rules.py                   │   │  Streamlit UI       │
 │  (app.py)          │──▶│  INFERENCE ENGINE  recommend()      │──▶│  Outfit cards,      │
 │  temp, weather,    │   │   R1 base outfit  (BASE dictionary) │   │  accessories,       │
 │  occasion, style,  │   │   R2 style tweaks                   │   │  palette, rule      │
 │  preferences       │   │   R3 preference tweaks              │   │  trace, download    │
 └────────────────────┘   │   R4 weather overrides (final word) │   └─────────────────────┘
                          │  KNOWLEDGE BASE: BASE, PALETTES,    │
                          │  OCCASION_ACCESSORIES               │
                          └─────────────────────────────────────┘
```

**Workflow**
1. User fills the sidebar form and clicks **Recommend**.
2. `get_temp_band()` converts the number into a label (freezing/cold/mild/warm/hot).
3. **R1:** look up the base outfit in `BASE[occasion][band]`.
4. **R2:** apply style rules (e.g. Streetwear → oversized top, chunky sneakers).
5. **R3:** apply preference rules (e.g. Avoid jeans → swap bottom).
6. **R4:** apply weather rules last (e.g. Rainy → waterproof jacket and shoes).
7. Return the outfit plus a `trace` list explaining each step; the UI renders it.

**Why this order?** Later stages can overwrite earlier ones. Putting weather last guarantees you never get "suede shoes in a downpour" just because you asked for a stylish look.

## 5. Rule Base and Sample IF–ELSE Conditions

**Temperature bands**

| Band | Range (°C) |
|---|---|
| freezing | below 10 |
| cold | 10 to 17 |
| mild | 18 to 24 |
| warm | 25 to 31 |
| hot | 32 and above |

**Rule groups**

| ID | Inputs | What it does |
|---|---|---|
| R1 | temperature band + occasion | Picks the base outfit (20 combinations) and standard accessories |
| R2 | style (+ occasion) | Rewrites pieces and sets the colour palette |
| R3 | preferences | Personal tweaks (comfort, fit, jeans, sneakers, layering, colours, eco) |
| R4 | weather | Safety and comfort overrides (rain, snow, wind, sun, humidity) |

**Sample rules (as in the code)**

```python
# R1 - temperature band
if temp_c < 10:        band = "freezing"
elif temp_c < 18:      band = "cold"
elif temp_c < 25:      band = "mild"
elif temp_c < 32:      band = "warm"
else:                  band = "hot"

# R2 - style
if style == "Streetwear" and occasion != "Formal":
    top = "Oversized hoodie" if band in ("freezing", "cold") else "Oversized graphic tee"
    footwear = "Chunky sneakers"

# R3 - preference
if "Prefer sneakers" in preferences and occasion == "Formal":
    pass   # ignored: sneakers do not suit a formal dress code

# R4 - weather (wins over everything above)
if weather == "Rainy":
    outer = "Waterproof jacket"
    footwear = "Waterproof sneakers or boots"
    accessories.append("Compact umbrella")
```

**Conflict handling:** weather beats style and preferences. A preference that clashes with the occasion (sneakers + formal) is ignored and the trace says so. If both Bold and Neutral colours are chosen, Bold wins.

## 6. Folder Structure

```
smart-outfit-recommender/
├── app.py            # Streamlit UI (looks + user interaction)
├── rules.py          # Knowledge base + inference engine (the "AI")
├── test_rules.py     # Automated test cases
├── requirements.txt  # streamlit
└── README.md         # This report
```

**Why two code files?** `rules.py` contains no UI code, so you can test it without Streamlit. This is called *separation of concerns* and examiners like it.

## 7. Setup and Execution

```bash
# 1. Go into the folder
cd Smart-Outfit-Recommender

# 2. (Recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 3. Install the only dependency
pip install -r requirements.txt

# 4. Run the app (opens http://localhost:8501)
streamlit run app.py

# 5. Run the tests (no Streamlit needed)
python test_rules.py
```

## 8. Code Explanation

**`rules.py`**
- **Lists** (`OCCASIONS`, `WEATHERS`, `STYLES`, `PREFERENCES`) feed the UI dropdowns, so adding an option means editing only one place.
- **`BASE` dictionary:** a table `BASE[occasion][band] = (top, bottom, footwear, outer)`. Storing knowledge as data keeps the code short.
- **`get_temp_band()`:** an `if / elif / else` ladder. Order matters: the first true condition wins.
- **`recommend()`:** the inference engine. It reads the base outfit, then runs the R2, R3 and R4 blocks in order. Each block appends `(rule_id, sentence)` to `trace`, which gives explainability for free.
- **`_add()`:** adds an accessory only if it is not already present, to avoid duplicates.
- It returns a dictionary, so the UI never needs to know how the rules work.

**`app.py`**
- `st.set_page_config` sets the title and wide layout.
- A CSS block inside `st.markdown(..., unsafe_allow_html=True)` creates the gradient hero, hover cards, chips, colour swatches and the temperature meter. It uses translucent backgrounds so it works in both light and dark mode.
- `st.form` in the sidebar groups the inputs, so the app recomputes only when you click the button.
- `st.session_state` stores the last result so it does not disappear when you click Download.
- `html.escape()` makes text safe before it goes into HTML.

## 9. Sample Inputs and Outputs

| # | Input | Output |
|---|---|---|
| 1 | 24°C, Sunny, College, Sporty, [Prefer sneakers] | **Top:** Dry-fit performance tee · **Bottom:** Track pants · **Footwear:** Running shoes · **Layer:** none · **Accessories:** Backpack, Water bottle · **Palette:** Grey, black & neon accents |
| 2 | 14°C, Rainy, Formal, Classic, [Comfort first] | **Top:** Full-sleeve formal shirt · **Bottom:** Tailored trousers (stretch/soft fabric) · **Footwear:** Water-resistant leather shoes · **Layer:** Waterproof jacket · **Accessories:** Analog watch, Leather belt, Compact umbrella |
| 3 | 33°C, Humid, Party, Ethnic Fusion, [Neutral colours, Eco-friendly fabrics] | **Top:** Embroidered kurta in breathable cotton/linen · **Bottom:** Straight pants or dhoti pants · **Footwear:** Mojaris or juttis · **Layer:** none · **Accessories:** Statement watch or jewellery, Sling bag, Reusable tote bag, Handkerchief or small towel · **Palette:** Neutral shades |

**Sample explanation (Input 2):**
- R1: 14°C is 'cold', so the base formal outfit for cold weather was chosen.
- R2: Classic style: the base outfit is already classic, only the palette is applied.
- R3: Comfort first: bottoms in a stretch or soft fabric.
- R4: Rainy: waterproof outer layer and footwear, quick-dry bottoms, umbrella.

## 10. Test Cases and Expected Results

All 11 are automated in `test_rules.py`.

| TC | Input (°C, weather, occasion, style, prefs) | Expected result |
|---|---|---|
| 1 | Bands at 9, 10, 17, 18, 24, 25, 31, 32 | freezing, cold, cold, mild, mild, warm, warm, hot (boundary check) |
| 2 | 5, Snowy, College, Minimal | Insulated waterproof jacket and boots, gloves and beanie |
| 3 | 35, Sunny, College, Sporty | Dry-fit tee, athletic shorts, running shoes, sunglasses, sunscreen, cap |
| 4 | 22, Cloudy, Formal, Classic | Formal shirt, tailored trousers, leather formal shoes, light blazer |
| 5 | 28, Rainy, Casual, Streetwear | Oversized graphic tee, waterproof footwear, waterproof jacket/poncho, umbrella |
| 6 | 12, Windy, Party, Ethnic Fusion, [Love layering] | Embroidered kurta, keeps leather/denim jacket, adds scarf |
| 7 | 22, Sunny, Formal, Minimal, [Prefer sneakers] | Footwear stays "Leather formal shoes" (preference ignored) |
| 8 | 22, Cloudy, College, Minimal, [Avoid jeans] and 15, Cloudy, College, Classic, [Avoid jeans] | "Chinos or cargo pants" and "Thick cargo pants" |
| 9 | 36, Rainy, Casual, Minimal | Shorts replaced by "Quick-dry light pants" |
| 10 | 20, Snowy, Casual, Minimal | Warning shown: snow unlikely above 5°C |
| 11 | Every occasion × weather × style × 6 temperatures | Never crashes; top, bottom, footwear and trace are always filled |

## 11. Advantages, Limitations and Future Scope

**Advantages**
- Fully explainable: every output is traceable to a rule.
- No dataset, training, internet or paid service needed.
- Predictable and easy to test.
- Easy to extend: add a dictionary entry or an `elif`.
- Gender-neutral wording, with a locally relevant Ethnic Fusion style (kurta, Kolhapuri).

**Limitations**
- Rules are hand-written, so coverage is limited to what the author thought of.
- No learning: it cannot adapt to a user's taste over time.
- It does not know what clothes the user actually owns.
- Weather is typed in manually.
- A large rule base would get hard to maintain, since rule conflicts grow with size.

**Future scope**
- Fetch live weather from a free API such as Open-Meteo.
- Add a "my wardrobe" input so only owned items are suggested.
- Add feedback buttons (👍/👎) and learn weights; this is a natural step toward a hybrid rule + ML system.
- Add outfit images, seasonal and festival rules, and a budget filter.
- Use fuzzy logic for smoother temperature boundaries.

## 12. Conclusion

The Smart Outfit Recommender shows that useful AI does not always need machine learning. By turning everyday clothing knowledge into a clear rule base, the system gives complete, weather-safe, occasion-appropriate outfits and explains each decision. Its layered design (base outfit, then style, preferences and weather) keeps the logic simple, testable and easy to demonstrate, which makes it a good first expert-system project.

## 13. Viva Questions with Answers

**Q1. What type of AI is this?**
A knowledge-based (rule-based) expert system. Knowledge is stored as facts and IF–ELSE rules, and an inference engine applies them.

**Q2. Why not use machine learning?**
It needs a labelled dataset, which we do not have. It is also less explainable. Rules are transparent and need no training.

**Q3. What are the knowledge base and the inference engine here?**
Knowledge base: `BASE`, `PALETTES`, `OCCASION_ACCESSORIES`. Inference engine: the `recommend()` function.

**Q4. Why is weather applied last?**
Later rules overwrite earlier ones. Weather affects safety and comfort (staying dry, warm and protected), so it must override fashion choices.

**Q5. How do you handle conflicting rules?**
By a fixed priority order: weather > preferences > style > base. Occasion-inappropriate preferences are ignored (sneakers for formal), and the trace tells the user why.

**Q6. How is the system explainable?**
Each rule appends a sentence with its ID (R1 to R4) to a `trace` list, and the UI shows that list.

**Q7. What is the difference between `if` and `elif` in `get_temp_band()`?**
`elif` is only checked if the earlier conditions were false. Because the checks go from low to high temperature, the first match is the right band.

**Q8. How would you add a new occasion, e.g. "Wedding"?**
Add "Wedding" to `OCCASIONS`, add a `BASE["Wedding"]` entry with 5 bands, and add its accessories. The UI picks it up automatically.

**Q9. How did you test it?**
11 unit tests covering boundary values, each weather and style behaviour, conflicting preferences, a warning case, and a stress test of all combinations.

**Q10. What are the limitations?**
Hand-written rules, no learning, no wardrobe awareness, manual weather input.

**Q11. How can it become "smarter"?**
Collect user feedback and learn which suggestions are liked (a hybrid rule + ML system), or add live weather and wardrobe data.

**Q12. Why did you split the code into `app.py` and `rules.py`?**
Separation of concerns. The logic can be tested without the UI, and the UI can change without touching the rules.

**Q13. What is `st.session_state` used for?**
Streamlit reruns the whole script on every interaction. Session state remembers the last result, so it does not vanish when you click Download.

**Q14. Is the system gender-neutral?**
Yes. Items are named by garment type (tee, pants, kurta) and no input or rule depends on gender.
