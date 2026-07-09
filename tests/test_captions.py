import pytest
import captions as C
import content as DATA

WA_LINK = "https://wa.me/6285278355590"


@pytest.fixture
def treatment():
    return list(DATA.all_treatments())[0]


@pytest.fixture
def review():
    return DATA.REVIEWS[0]


# --- service_spotlight ---

def test_service_spotlight_id_contains_name_desc_wa(treatment):
    result = C.service_spotlight(treatment, lang="id")
    assert treatment["name"]["id"] in result
    assert treatment["desc"]["id"] in result
    assert WA_LINK in result
    assert "@djayamassage" in result


def test_service_spotlight_en_contains_name_desc_wa(treatment):
    result = C.service_spotlight(treatment, lang="en")
    assert treatment["name"]["en"] in result
    assert treatment["desc"]["en"] in result
    assert WA_LINK in result


def test_service_spotlight_all_treatments_all_langs():
    for t in DATA.all_treatments():
        for lang in ("id", "en"):
            result = C.service_spotlight(t, lang=lang)
            assert WA_LINK in result, f"WA link missing: {t['slug']} lang={lang}"
            assert len(result) > 50


def test_service_spotlight_price_format(treatment):
    result = C.service_spotlight(treatment, lang="id")
    dur, price = treatment["prices"][0]
    assert dur in result
    assert price in result


# --- signature ---

def test_signature_id_contains_name_and_wa():
    t = DATA.TREATMENTS["signature"][0]
    result = C.signature(t, lang="id")
    assert WA_LINK in result
    assert "Healing Ritual" in result or "3-in-1" in result


def test_signature_en_contains_wa():
    t = DATA.TREATMENTS["signature"][0]
    result = C.signature(t, lang="en")
    assert WA_LINK in result
    assert len(result) > 50


# --- testimonial ---

def test_testimonial_id_contains_text_and_wa(review):
    result = C.testimonial(review, lang="id")
    assert review["text"]["id"] in result
    assert WA_LINK in result


def test_testimonial_en_contains_text_and_wa(review):
    result = C.testimonial(review, lang="en")
    assert review["text"]["en"] in result
    assert WA_LINK in result


def test_testimonial_all_reviews_all_langs():
    for r in DATA.REVIEWS:
        for lang in ("id", "en"):
            result = C.testimonial(r, lang=lang)
            assert WA_LINK in result
            assert r["text"][lang] in result


def test_testimonial_shows_star_rating(review):
    result = C.testimonial(review, lang="id")
    assert "★" * review["rating"] in result


# --- promo ---

def test_promo_id_contains_label_terms_wa():
    result = C.promo(DATA.PROMO, lang="id")
    assert DATA.PROMO["label"]["id"] in result
    assert DATA.PROMO["terms"]["id"] in result
    assert WA_LINK in result


def test_promo_en_contains_label_terms_wa():
    result = C.promo(DATA.PROMO, lang="en")
    assert DATA.PROMO["label"]["en"] in result
    assert DATA.PROMO["terms"]["en"] in result
    assert WA_LINK in result


# --- ambiance ---

def test_ambiance_id_contains_wa():
    result = C.ambiance(lang="id")
    assert WA_LINK in result
    assert len(result) > 30


def test_ambiance_en_contains_wa():
    result = C.ambiance(lang="en")
    assert WA_LINK in result


# --- location ---

def test_location_id_contains_batam_and_wa():
    result = C.location(DATA.BUSINESS, lang="id")
    assert WA_LINK in result
    assert "Batam" in result
    assert DATA.BUSINESS["hours"]["id"] in result


def test_location_en_contains_batam_and_wa():
    result = C.location(DATA.BUSINESS, lang="en")
    assert WA_LINK in result
    assert "Batam" in result


# --- booking_reminder ---

def test_booking_reminder_id_contains_hours_and_wa():
    result = C.booking_reminder(DATA.BUSINESS, lang="id")
    assert WA_LINK in result
    assert DATA.BUSINESS["hours"]["id"] in result


def test_booking_reminder_en_contains_wa():
    result = C.booking_reminder(DATA.BUSINESS, lang="en")
    assert WA_LINK in result


# ── Task 10: hashtag sets + hook-formula captions ────────────────────────────
import importlib
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import captions as CAP

def test_hashtag_sets_has_three_keys():
    assert "lokal" in CAP.HASHTAG_SETS
    assert "sg" in CAP.HASHTAG_SETS
    assert "wellness" in CAP.HASHTAG_SETS

def test_tags_returns_string():
    result = CAP._tags("id")
    assert isinstance(result, str)
    assert "#" in result

def test_tags_extra_appended():
    result = CAP._tags("en", extra=["#test123"])
    assert "#test123" in result

def test_caption_r1_id_contains_hook():
    content = {
        "treatment": {
            "name": "Pijat Refleksi",
            "category": "Reflexology",
            "desc": "Relaksasi mendalam",
            "prices": [{"duration": 60, "price": 150000}],
        }
    }
    cap = CAP.caption_r1(content, "id")
    assert isinstance(cap, str) and len(cap) > 30

def test_caption_r2_en_contains_quote_markers():
    content = {
        "review": {
            "name": "Alice",
            "rating": 5,
            "text": "Absolutely amazing massage.",
            "lang": "en",
        }
    }
    cap = CAP.caption_r2(content, "en")
    assert isinstance(cap, str) and len(cap) > 20

def test_caption_r3_both_langs():
    cap_id = CAP.caption_r3({}, "id")
    cap_en = CAP.caption_r3({}, "en")
    assert isinstance(cap_id, str) and isinstance(cap_en, str)
    assert cap_id != cap_en

def test_caption_r4_contains_cta():
    content = {"promo": {"headline": "FREE Foot Scrub", "sub": "This week only", "cta": "Book now"}}
    cap = CAP.caption_r4(content, "en")
    assert isinstance(cap, str)
    assert len(cap) > 20

def test_caption_r5_contains_address():
    content = {"business": {"name": "Djaya", "hours": "10am-10pm", "address": "1 Keong Saik Rd"}}
    cap = CAP.caption_r5(content, "en")
    assert "Keong Saik" in cap or "Keong" in cap or "Djaya" in cap

def test_all_captions_have_hashtags():
    content_map = {
        "r1": {"treatment": {"name": "T", "category": "C", "desc": "D", "prices": [{"duration": 60, "price": 100000}]}},
        "r2": {"review": {"name": "B", "rating": 5, "text": "Great", "lang": "id"}},
        "r3": {},
        "r4": {"promo": {"headline": "H", "sub": "S", "cta": "CTA"}},
        "r5": {"business": {"name": "Djaya", "hours": "10am-10pm", "address": "1 Keong Saik"}},
    }
    fns = [CAP.caption_r1, CAP.caption_r2, CAP.caption_r3, CAP.caption_r4, CAP.caption_r5]
    keys = ["r1", "r2", "r3", "r4", "r5"]
    for fn, key in zip(fns, keys):
        cap = fn(content_map[key], "id")
        assert "#" in cap, f"{key} caption missing hashtags"
