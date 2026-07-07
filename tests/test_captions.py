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
