"""
rules.py - Rule base + inference engine for the Smart Outfit Recommender.

No machine learning, no APIs. Only dictionaries, IF-ELSE conditions and functions.

Inference order (each stage can overwrite the previous one):
    R1  temperature + occasion  -> base outfit      (lookup table)
    R2  personal style          -> style tweaks
    R3  clothing preferences    -> personal tweaks
    R4  weather condition       -> safety / comfort overrides (always wins)
"""

OCCASIONS = ["College", "Formal", "Party", "Casual"]
WEATHERS = ["Sunny", "Cloudy", "Rainy", "Windy", "Snowy", "Humid"]
STYLES = ["Minimal", "Classic", "Streetwear", "Sporty", "Ethnic Fusion"]
PREFERENCES = [
    "Comfort first", "Relaxed fit", "Avoid jeans", "Prefer sneakers",
    "Love layering", "Bold colours", "Neutral colours", "Eco-friendly fabrics",
]

# ---------------------------------------------------------------------------
# RULE BASE (facts stored as dictionaries)
# BASE[occasion][temperature_band] = (top, bottom, footwear, outer_layer)
# ---------------------------------------------------------------------------
BASE = {
    "College": {
        "freezing": ("Thermal tee + chunky knit sweater", "Thick jeans or cargo pants", "Ankle boots", "Padded puffer jacket"),
        "cold":     ("Full-sleeve tee + hoodie", "Jeans", "Sneakers", "Zip-up jacket"),
        "mild":     ("Plain cotton tee", "Jeans or chinos", "Sneakers", None),
        "warm":     ("Breathable cotton tee", "Light chinos", "Canvas sneakers", None),
        "hot":      ("Loose cotton tee", "Shorts or light cotton pants", "Sandals or slip-ons", None),
    },
    "Formal": {
        "freezing": ("Formal shirt + wool sweater", "Wool trousers", "Leather formal shoes", "Long overcoat"),
        "cold":     ("Full-sleeve formal shirt", "Tailored trousers", "Leather formal shoes", "Blazer"),
        "mild":     ("Formal shirt", "Tailored trousers", "Leather formal shoes", "Light blazer"),
        "warm":     ("Light formal shirt", "Tailored trousers", "Loafers", None),
        "hot":      ("Lightweight cotton shirt", "Light-colour trousers", "Loafers", None),
    },
    "Party": {
        "freezing": ("Knit or satin top", "Dark slim jeans or tailored pants", "Boots", "Long coat"),
        "cold":     ("Fitted knit top", "Dark jeans", "Boots or smart sneakers", "Leather/denim jacket"),
        "mild":     ("Printed shirt or sleek top", "Dark jeans", "Smart sneakers", None),
        "warm":     ("Lightweight statement top", "Tailored shorts or slim pants", "Loafers or fashion sneakers", None),
        "hot":      ("Short-sleeve statement top", "Light tailored shorts", "Open sandals or slip-ons", None),
    },
    "Casual": {
        "freezing": ("Thermal + fleece sweatshirt", "Joggers or thick jeans", "Warm sneakers or boots", "Puffer jacket"),
        "cold":     ("Sweatshirt", "Joggers or jeans", "Sneakers", "Light jacket"),
        "mild":     ("Casual tee", "Jeans or joggers", "Sneakers", None),
        "warm":     ("Relaxed cotton tee", "Shorts or light pants", "Slides or sneakers", None),
        "hot":      ("Loose short-sleeve tee", "Shorts", "Sandals", None),
    },
}

OCCASION_ACCESSORIES = {
    "College": ["Backpack", "Water bottle"],
    "Formal":  ["Analog watch", "Leather belt"],
    "Party":   ["Statement watch or jewellery", "Sling bag"],
    "Casual":  ["Tote bag or small sling"],
}

# style -> (palette description, swatch colours)
PALETTES = {
    "Minimal":       ("Solid neutrals", ["#111827", "#f9fafb", "#9ca3af", "#d6c8b4"]),
    "Classic":       ("Navy, white & camel", ["#1e3a5f", "#ffffff", "#c19a6b", "#6b7280"]),
    "Streetwear":    ("Black, olive & one loud accent", ["#0b0b0b", "#556b2f", "#f97316", "#e5e7eb"]),
    "Sporty":        ("Grey, black & neon accents", ["#4b5563", "#111827", "#a3e635", "#f1f5f9"]),
    "Ethnic Fusion": ("Indigo, mustard & maroon", ["#3730a3", "#d4a017", "#7f1d1d", "#f5e6c8"]),
}
BOLD = ("Bold colours (cobalt, rust, emerald)", ["#2563eb", "#c2410c", "#059669", "#f5f5f4"])
NEUTRAL = ("Neutral shades (black, white, grey, beige)", ["#111827", "#f9fafb", "#9ca3af", "#d6c8b4"])

COMFORT_PHRASE = {
    "freezing": "warm and protected", "cold": "cosy", "mild": "comfortable",
    "warm": "cool and breezy", "hot": "as cool as possible",
}


def get_temp_band(temp_c):
    """Convert a number (deg C) into a label the rules can work with."""
    if temp_c < 10:
        return "freezing"
    elif temp_c < 18:
        return "cold"
    elif temp_c < 25:
        return "mild"
    elif temp_c < 32:
        return "warm"
    else:
        return "hot"


def _add(items, item):
    """Append to a list only if it is not already there."""
    if item not in items:
        items.append(item)


def recommend(temp_c, weather, occasion, style, preferences=None):
    """Main inference function. Returns a dictionary with the outfit + explanation."""
    preferences = preferences or []
    band = get_temp_band(temp_c)
    cold_or_below = band in ("freezing", "cold")
    warm_or_hot = band in ("warm", "hot")

    top, bottom, footwear, outer = BASE[occasion][band]
    accessories = list(OCCASION_ACCESSORIES[occasion])
    palette_name, palette_colors = PALETTES[style]
    trace, warnings = [], []          # trace = list of (rule_id, explanation)

    # ---- R1: temperature + occasion -> base outfit --------------------------
    trace.append(("R1", f"{temp_c}°C is in the '{band}' band, so the base {occasion.lower()} "
                        f"outfit for {band} weather and its usual accessories were chosen."))

    # ---- R2: personal style -------------------------------------------------
    if style == "Sporty":
        if occasion in ("College", "Casual"):
            top = "Dry-fit performance tee" if band != "freezing" and band != "cold" else "Performance tee with a zip hoodie"
            bottom = "Athletic shorts" if warm_or_hot else "Track pants"
            footwear = "Running shoes"
            trace.append(("R2", "Sporty style + relaxed occasion: performance tee, athletic bottoms and running shoes."))
        elif occasion == "Party":
            footwear = "Clean fashion sneakers"
            _add(accessories, "Sleek sports watch")
            trace.append(("R2", "Sporty style at a party: kept the base outfit, swapped in fashion sneakers and a sports watch."))
        else:
            _add(accessories, "Sleek sports watch")
            trace.append(("R2", "Formal dress code beats sporty clothing, so the sporty touch is only a sleek watch."))
    elif style == "Streetwear":
        if occasion == "Formal":
            _add(accessories, "Statement watch")
            trace.append(("R2", "Streetwear toned down for a formal dress code: one statement watch only."))
        else:
            top = "Oversized hoodie" if cold_or_below else "Oversized graphic tee"
            bottom = "Baggy shorts" if band == "hot" else "Baggy cargo pants"
            footwear = "Chunky sneakers"
            trace.append(("R2", "Streetwear style: oversized top, baggy bottoms and chunky sneakers."))
    elif style == "Ethnic Fusion":
        if occasion == "Formal":
            top, bottom, footwear = "Nehru-collar kurta or bandhgala shirt", "Straight tailored trousers", "Leather juttis or formal shoes"
        elif occasion == "Party":
            top, bottom, footwear = "Embroidered kurta", "Straight pants or dhoti pants", "Mojaris or juttis"
        else:
            top = "Short cotton kurta"
            bottom = "Light cotton pants" if band == "hot" else "Straight-fit pants"
            footwear = "Kolhapuri chappals" if band in ("mild", "warm", "hot") else "Ankle boots or sneakers"
        trace.append(("R2", f"Ethnic Fusion style: kurta-based look adapted to a {occasion.lower()} occasion."))
    elif style == "Classic":
        if occasion in ("College", "Casual"):
            top = "Oxford shirt (layer a sweater on top)" if cold_or_below else "Polo shirt"
            if band in ("mild", "warm", "hot"):
                bottom = "Chinos"
                footwear = "Clean white sneakers or loafers"
            trace.append(("R2", "Classic style: polo/oxford shirt with clean, timeless pieces."))
        else:
            trace.append(("R2", "Classic style: the base outfit is already classic, only the colour palette is applied."))
    elif style == "Minimal":
        top = top + " (solid colour, no logos)"
        trace.append(("R2", "Minimal style: solid colours, no logos or loud prints."))

    # ---- R3: clothing preferences ------------------------------------------
    for pref in preferences:
        if pref == "Comfort first":
            bottom = bottom + " (stretch/soft fabric)"
            trace.append(("R3", "Comfort first: bottoms in a stretch or soft fabric."))
        elif pref == "Relaxed fit":
            top = top + " (relaxed fit)"
            trace.append(("R3", "Relaxed fit: top picked a size loose."))
        elif pref == "Avoid jeans":
            if "jeans" in bottom.lower():
                if occasion == "Party":
                    bottom = "Dark tailored pants"
                elif cold_or_below:
                    bottom = "Thick cargo pants"
                else:
                    bottom = "Chinos or cargo pants"
                trace.append(("R3", "Avoid jeans: jeans replaced with a non-denim alternative."))
            else:
                trace.append(("R3", "Avoid jeans: this outfit has no jeans, nothing to change."))
        elif pref == "Prefer sneakers":
            if occasion == "Formal":
                trace.append(("R3", "Prefer sneakers ignored: sneakers do not suit a formal dress code."))
            elif "sneaker" in footwear.lower() or "running" in footwear.lower():
                trace.append(("R3", "Prefer sneakers: footwear is already sneaker-style."))
            else:
                footwear = "Comfortable sneakers"
                trace.append(("R3", "Prefer sneakers: footwear switched to sneakers."))
        elif pref == "Love layering":
            if outer is None:
                outer = "Light overshirt or cardigan"
                trace.append(("R3", "Love layering: added a light overshirt/cardigan."))
            else:
                trace.append(("R3", "Love layering: the outfit already has an outer layer."))
        elif pref == "Eco-friendly fabrics":
            _add(accessories, "Reusable tote bag")
            trace.append(("R3", "Eco-friendly: choose organic cotton, linen or hemp; added a reusable tote."))
    if "Bold colours" in preferences:
        palette_name, palette_colors = BOLD
        trace.append(("R3", "Bold colours: palette switched to saturated shades (wins if Neutral is also chosen)."))
    elif "Neutral colours" in preferences:
        palette_name, palette_colors = NEUTRAL
        trace.append(("R3", "Neutral colours: palette switched to neutral shades."))

    # ---- R4: weather overrides (safety and comfort always win) -------------
    if weather == "Rainy":
        outer = "Lightweight waterproof jacket or poncho" if warm_or_hot else "Waterproof jacket"
        footwear = "Water-resistant leather shoes" if occasion == "Formal" else "Waterproof sneakers or boots"
        if "shorts" in bottom.lower():
            bottom = "Quick-dry light pants"
        _add(accessories, "Compact umbrella")
        trace.append(("R4", "Rainy: waterproof outer layer and footwear, quick-dry bottoms, umbrella."))
    elif weather == "Snowy":
        outer = "Insulated waterproof jacket"
        footwear = "Insulated waterproof boots"
        _add(accessories, "Woollen gloves")
        _add(accessories, "Beanie")
        trace.append(("R4", "Snowy: insulated jacket and boots, plus gloves and a beanie."))
        if temp_c > 5:
            warnings.append("Snow is unlikely above 5°C. Please double-check your inputs.")
    elif weather == "Windy":
        if outer is None:
            outer = "Light windcheater"
        if cold_or_below:
            _add(accessories, "Scarf")
        trace.append(("R4", "Windy: wind-blocking outer layer (and a scarf if it is cold)."))
    elif weather == "Sunny":
        if temp_c >= 25:
            _add(accessories, "Sunglasses")
            _add(accessories, "Sunscreen (SPF 30+)")
            if occasion in ("College", "Casual") and band == "hot":
                _add(accessories, "Cap")
            trace.append(("R4", "Sunny and 25°C or above: sun protection added."))
        else:
            trace.append(("R4", "Sunny but below 25°C: no extra sun protection needed."))
    elif weather == "Humid":
        if warm_or_hot:
            top = top + " in breathable cotton/linen"
            _add(accessories, "Handkerchief or small towel")
            trace.append(("R4", "Humid and warm: breathable fabric and a handkerchief."))
        else:
            trace.append(("R4", "Humid but not warm: no change needed."))
    elif weather == "Cloudy":
        if outer is None:
            _add(accessories, "Light layer in your bag (it may turn cooler)")
        trace.append(("R4", "Cloudy: no major change, just a spare layer if you have none."))

    summary = (f"Because it is {temp_c}°C ({band}) and {weather.lower()}, this {style.lower()} "
               f"{occasion.lower()} outfit keeps you {COMFORT_PHRASE[band]}.")

    return {
        "band": band, "top": top, "bottom": bottom, "footwear": footwear, "outer": outer,
        "accessories": accessories, "palette_name": palette_name, "palette_colors": palette_colors,
        "summary": summary, "trace": trace, "warnings": warnings,
    }
