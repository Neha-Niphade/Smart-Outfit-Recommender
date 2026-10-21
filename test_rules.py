"""test_rules.py - run with:  python test_rules.py   (or: pytest)"""
from rules import recommend, get_temp_band, OCCASIONS, WEATHERS, STYLES


def test_temperature_bands():                                   # TC1
    expected = {9: "freezing", 10: "cold", 17: "cold", 18: "mild",
                24: "mild", 25: "warm", 31: "warm", 32: "hot"}
    for temp, band in expected.items():
        assert get_temp_band(temp) == band


def test_snowy_freezing_college():                              # TC2
    r = recommend(5, "Snowy", "College", "Minimal")
    assert r["outer"] == "Insulated waterproof jacket"
    assert r["footwear"] == "Insulated waterproof boots"
    assert "Beanie" in r["accessories"] and "Woollen gloves" in r["accessories"]


def test_hot_sunny_sporty_college():                            # TC3
    r = recommend(35, "Sunny", "College", "Sporty")
    assert r["top"] == "Dry-fit performance tee"
    assert r["bottom"] == "Athletic shorts"
    assert r["footwear"] == "Running shoes"
    for item in ("Sunglasses", "Sunscreen (SPF 30+)", "Cap"):
        assert item in r["accessories"]


def test_formal_cloudy_classic():                               # TC4
    r = recommend(22, "Cloudy", "Formal", "Classic")
    assert (r["top"], r["bottom"]) == ("Formal shirt", "Tailored trousers")
    assert r["footwear"] == "Leather formal shoes" and r["outer"] == "Light blazer"


def test_rainy_streetwear_casual():                             # TC5
    r = recommend(28, "Rainy", "Casual", "Streetwear")
    assert r["top"] == "Oversized graphic tee"
    assert r["footwear"] == "Waterproof sneakers or boots"
    assert r["outer"] == "Lightweight waterproof jacket or poncho"
    assert "Compact umbrella" in r["accessories"]


def test_windy_party_ethnic_fusion():                           # TC6
    r = recommend(12, "Windy", "Party", "Ethnic Fusion", ["Love layering"])
    assert r["top"] == "Embroidered kurta"
    assert r["outer"] == "Leather/denim jacket"
    assert "Scarf" in r["accessories"]


def test_sneakers_ignored_for_formal():                         # TC7
    r = recommend(22, "Sunny", "Formal", "Minimal", ["Prefer sneakers"])
    assert r["footwear"] == "Leather formal shoes"


def test_avoid_jeans():                                         # TC8
    assert recommend(22, "Cloudy", "College", "Minimal", ["Avoid jeans"])["bottom"] == "Chinos or cargo pants"
    assert recommend(15, "Cloudy", "College", "Classic", ["Avoid jeans"])["bottom"] == "Thick cargo pants"


def test_rain_replaces_shorts():                                # TC9
    assert recommend(36, "Rainy", "Casual", "Minimal")["bottom"] == "Quick-dry light pants"


def test_unrealistic_snow_warning():                            # TC10
    assert recommend(20, "Snowy", "Casual", "Minimal")["warnings"]


def test_every_combination_works():                             # TC11 (stress test)
    for occ in OCCASIONS:
        for wea in WEATHERS:
            for sty in STYLES:
                for t in (-5, 5, 12, 20, 28, 38):
                    r = recommend(t, wea, occ, sty)
                    assert r["top"] and r["bottom"] and r["footwear"] and r["trace"]


if __name__ == "__main__":
    tests = [f for name, f in list(globals().items()) if name.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print(f"\nAll {len(tests)} tests passed.")
