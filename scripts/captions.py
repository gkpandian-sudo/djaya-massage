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
