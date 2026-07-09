# captions.py — Instagram caption generators for all 7 post types
# Data structures match content.py (name/desc/prices are dicts with "id"/"en" keys).

WA_LINK = "https://wa.me/6285278355590"
IG_HANDLE = "@djayamassage"
RATING_LINE = f"{IG_HANDLE} · Google 4.9★ · Tripadvisor 5.0★"


def _price_lines(prices: list) -> str:
    return "\n".join(f"{dur}  ·  {price}" for dur, price in prices)


def service_spotlight(t: dict, lang: str = "id") -> str:
    name  = t["name"][lang]
    desc  = t["desc"][lang]
    prices = _price_lines(t["prices"])
    if lang == "id":
        return (
            f"{name}\n\n"
            f"{desc}\n\n"
            f"{prices}\n\n"
            f"Booking langsung via WhatsApp, tim kami bantu pilih waktu terbaik.\n"
            f"{WA_LINK}\n\n"
            f"{RATING_LINE}"
        )
    return (
        f"{name}\n\n"
        f"{desc}\n\n"
        f"{prices}\n\n"
        f"Book directly on WhatsApp — our team will help you pick the best time.\n"
        f"{WA_LINK}\n\n"
        f"{RATING_LINE}"
    )


def signature(t: dict, lang: str = "id") -> str:
    name  = t["name"][lang]
    desc  = t["desc"][lang]
    prices = _price_lines(t["prices"])
    if lang == "id":
        return (
            f"{name}\n\n"
            f"{desc}\n\n"
            f"{prices}\n\n"
            f"Manjakan diri Anda dengan ritual lengkap yang menggabungkan tiga terapi "
            f"dalam satu sesi. Tersedia setiap hari, 10.00–22.00 WIB.\n\n"
            f"Reservasi:\n{WA_LINK}\n\n"
            f"{RATING_LINE}"
        )
    return (
        f"{name}\n\n"
        f"{desc}\n\n"
        f"{prices}\n\n"
        f"Treat yourself to a complete ritual combining three therapies in one session. "
        f"Available every day, 10:00–22:00 WIB.\n\n"
        f"Reserve:\n{WA_LINK}\n\n"
        f"{RATING_LINE}"
    )


def testimonial(review: dict, lang: str = "id") -> str:
    text  = review["text"][lang]
    stars = "★" * review["rating"]
    if lang == "id":
        return (
            f"{stars} {review['source']}\n\n"
            f'"{text}"\n\n'
            f"— {review['name']}\n\n"
            f"Bergabunglah dengan tamu kami yang puas. Booking:\n"
            f"{WA_LINK}\n\n"
            f"{RATING_LINE}"
        )
    return (
        f"{stars} {review['source']}\n\n"
        f'"{text}"\n\n'
        f"— {review['name']}\n\n"
        f"Join our happy guests. Book now:\n"
        f"{WA_LINK}\n\n"
        f"{RATING_LINE}"
    )


def promo(p: dict, lang: str = "id") -> str:
    if lang == "id":
        return (
            f"{p['label']['id']}\n\n"
            f"{p['terms']['id']}\n\n"
            f"Hubungi kami untuk informasi lebih lanjut dan reservasi:\n"
            f"{WA_LINK}\n\n"
            f"{IG_HANDLE} · Penuin Centre, Batam"
        )
    return (
        f"{p['label']['en']}\n\n"
        f"{p['terms']['en']}\n\n"
        f"Contact us for more info and reservations:\n"
        f"{WA_LINK}\n\n"
        f"{IG_HANDLE} · Penuin Centre, Batam"
    )


def ambiance(lang: str = "id") -> str:
    if lang == "id":
        return (
            f"Ketenangan yang berakar pada tradisi.\n\n"
            f"Temukan kedamaian sejati di Djaya Massage & Reflexology — "
            f"tempat setiap sentuhan membawa keseimbangan bagi tubuh dan pikiran.\n\n"
            f"Buka setiap hari, 10.00–22.00 WIB.\n"
            f"{WA_LINK}\n\n"
            f"{RATING_LINE}"
        )
    return (
        f"Calm, rooted in tradition.\n\n"
        f"Discover true peace at Djaya Massage & Reflexology — "
        f"where every touch brings balance to body and mind.\n\n"
        f"Open every day, 10:00–22:00 WIB.\n"
        f"{WA_LINK}\n\n"
        f"{RATING_LINE}"
    )


def location(business: dict, lang: str = "id") -> str:
    if lang == "id":
        return (
            f"Temukan kami di Batam\n\n"
            f"Djaya Massage & Reflexology\n"
            f"{business['address_short']}\n"
            f"{business['landmark']['id']}\n\n"
            f"{business['hours']['id']}\n\n"
            f"Booking:\n{WA_LINK}\n\n"
            f"{IG_HANDLE}"
        )
    return (
        f"Find us in Batam\n\n"
        f"Djaya Massage & Reflexology\n"
        f"{business['address_short']}\n"
        f"{business['landmark']['en']}\n\n"
        f"{business['hours']['en']}\n\n"
        f"Book:\n{WA_LINK}\n\n"
        f"{IG_HANDLE}"
    )


def booking_reminder(business: dict, lang: str = "id") -> str:
    if lang == "id":
        return (
            f"{business['hours']['id']}\n\n"
            f"Pesan sekarang, langsung via WhatsApp. "
            f"Tim kami siap membantu Anda memilih treatment yang tepat.\n\n"
            f"{WA_LINK}\n\n"
            f"{IG_HANDLE} · Penuin Centre, Lubuk Baja, Batam"
        )
    return (
        f"{business['hours']['en']}\n\n"
        f"Book now, directly on WhatsApp. "
        f"Our team is ready to help you choose the right treatment.\n\n"
        f"{WA_LINK}\n\n"
        f"{IG_HANDLE} · Penuin Centre, Lubuk Baja, Batam"
    )


# ── Hashtag sets ─────────────────────────────────────────────────────────────
HASHTAG_SETS = {
    "lokal": [
        "#pijatjakarta", "#pijatrefleksi", "#reflexology", "#pijattradisional",
        "#jasapijat", "#pijatenak", "#pijatmurah",
    ],
    "sg": [
        "#singaporemassage", "#massagesg", "#relaxsg", "#sgwellness",
        "#chinatownsg", "#tanjongpagar", "#singaporelife",
    ],
    "wellness": [
        "#massage", "#wellness", "#relaxation", "#selfcare",
        "#reflexologytherapy", "#bodycare", "#holistichealth",
    ],
}

_ALWAYS = ["#djayamassage", "#djayamassagesg"]


def _tags(lang: str, extra: list | None = None) -> str:
    """Build a hashtag string: always + lang-appropriate set + wellness + optional extras."""
    tags = list(_ALWAYS)
    if lang == "id":
        tags += HASHTAG_SETS["lokal"]
    else:
        tags += HASHTAG_SETS["sg"]
    tags += HASHTAG_SETS["wellness"]
    if extra:
        tags += extra
    return " ".join(tags)


# ── Hook-formula caption functions ────────────────────────────────────────────

def caption_r1(content: dict, lang: str) -> str:
    """Service spotlight — pain-point hook."""
    t = content.get("treatment", {})
    name = t.get("name", "")
    desc = t.get("desc", "")
    prices = t.get("prices", [])
    price_str = ""
    if prices:
        p = prices[0]
        price_str = f"Rp {p['price']:,.0f}".replace(",", ".") + f" / {p['duration']} min"

    if lang == "id":
        body = (
            f"Capek setelah seharian kerja? 😩\n\n"
            f"✨ {name} — {desc}\n\n"
            f"💆 Mulai dari {price_str}\n"
            f"📍 1 Keong Saik Rd, Singapore\n"
            f"📞 +65 6222 5885\n\n"
        )
    else:
        body = (
            f"Feeling drained after a long day? 😩\n\n"
            f"✨ {name} — {desc}\n\n"
            f"💆 From {price_str}\n"
            f"📍 1 Keong Saik Rd, Singapore\n"
            f"📞 +65 6222 5885\n\n"
        )
    return body + _tags(lang, extra=["#javanesemasage", "#traditionalmassage"])


def caption_r2(content: dict, lang: str) -> str:
    """Testimonial reel — social proof hook."""
    r = content.get("review", {})
    name = r.get("name", "")
    text = r.get("text", "")
    stars = "⭐" * min(int(r.get("rating", 5)), 5)

    if lang == "id":
        body = (
            f"Kata mereka tentang Djaya... 🤍\n\n"
            f"{stars}\n"
            f'"{text}"\n'
            f"— {name}\n\n"
            f"📍 1 Keong Saik Rd, Singapore\n"
            f"📞 +65 6222 5885\n\n"
        )
    else:
        body = (
            f"Here's what our guests say... 🤍\n\n"
            f"{stars}\n"
            f'"{text}"\n'
            f"— {name}\n\n"
            f"📍 1 Keong Saik Rd, Singapore\n"
            f"📞 +65 6222 5885\n\n"
        )
    return body + _tags(lang, extra=["#testimonial", "#massagereview"])


def caption_r3(content: dict, lang: str) -> str:
    """Ambiance/BTS reel — curiosity hook."""
    if lang == "id":
        body = (
            "Di balik layar Djaya Massage 🎬\n\n"
            "Suasana yang tenang, sentuhan yang tulus.\n"
            "Begini kami mempersiapkan pengalaman terbaik untuk kamu.\n\n"
            "📍 1 Keong Saik Rd, #01-01, Singapore 089109\n"
            "⏰ Buka setiap hari 10.00 – 22.00\n"
            "📞 +65 6222 5885\n\n"
        )
    else:
        body = (
            "A peek behind the scenes at Djaya Massage 🎬\n\n"
            "Calm space. Genuine care.\n"
            "This is how we prepare the perfect experience for you.\n\n"
            "📍 1 Keong Saik Rd, #01-01, Singapore 089109\n"
            "⏰ Open daily 10am – 10pm\n"
            "📞 +65 6222 5885\n\n"
        )
    return body + _tags(lang, extra=["#behindthescenes", "#spavibe"])


def caption_r4(content: dict, lang: str) -> str:
    """Promo reel — urgency hook."""
    p = content.get("promo", {})
    headline = p.get("headline", "Special Offer")
    sub = p.get("sub", "")
    cta = p.get("cta", "Book now")

    if lang == "id":
        body = (
            f"Jangan sampai ketinggalan! ⏳\n\n"
            f"🎁 {headline}\n"
            f"{sub}\n\n"
            f"👉 {cta} sekarang — DM atau telp +65 6222 5885\n"
            f"📍 1 Keong Saik Rd, Singapore\n\n"
        )
    else:
        body = (
            f"Don't miss out! ⏳\n\n"
            f"🎁 {headline}\n"
            f"{sub}\n\n"
            f"👉 {cta} — DM or call +65 6222 5885\n"
            f"📍 1 Keong Saik Rd, Singapore\n\n"
        )
    return body + _tags(lang, extra=["#massagepromo", "#spaoffer"])


def caption_r5(content: dict, lang: str) -> str:
    """Location/brand reel — curiosity + CTA hook."""
    b = content.get("business", {})
    name = b.get("name", "Djaya Massage")
    hours = b.get("hours", "10am – 10pm")
    address = b.get("address", "1 Keong Saik Rd")

    if lang == "id":
        body = (
            f"Tau nggak, ada spa mewah di jantung Singapore? 🇸🇬\n\n"
            f"✨ {name}\n"
            f"📍 {address}, Singapore\n"
            f"⏰ {hours} setiap hari\n"
            f"📞 +65 6222 5885\n\n"
            f"Booking via DM atau telepon langsung 👆\n\n"
        )
    else:
        body = (
            f"Did you know there's a hidden gem spa in the heart of Singapore? 🇸🇬\n\n"
            f"✨ {name}\n"
            f"📍 {address}, Singapore\n"
            f"⏰ Open daily {hours}\n"
            f"📞 +65 6222 5885\n\n"
            f"Book via DM or give us a call 👆\n\n"
        )
    return body + _tags(lang, extra=["#singaporespa", "#hiddengem"])
