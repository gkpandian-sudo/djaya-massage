# content.py — mirrors lib/content.ts from github.com/adithyodw/djaya-apps
# Update this file when the website's treatment menu or reviews change.

PHONE = "6285278355590"
WA_BASE = f"https://wa.me/{PHONE}"
IG_HANDLE = "@djayamassage"
IG_URL = "instagram.com/djayamassage"

BUSINESS = {
    "name": "Djaya Massage & Reflexology",
    "address": "Jl. Komp. Penuin Centre No. 14, Blok A\nBatu Selicin, Kec. Lubuk Baja\nKota Batam, Kepulauan Riau 29411",
    "address_short": "Penuin Centre, Lubuk Baja, Batam",
    "landmark": {"id": "Dekat Grand Batam Mall & A2 Foodcourt", "en": "Near Grand Batam Mall & A2 Foodcourt"},
    "hours": {"id": "Buka setiap hari  ·  10.00 – 22.00", "en": "Open daily  ·  10 AM – 10 PM"},
    "rating_google": 4.9,
    "rating_tripadvisor": 5.0,
}

PROMO = {
    "active": True,
    "label": {"id": "Diskon 30% untuk Warga Lokal", "en": "30% Off for Local Residents"},
    "terms": {"id": "Tunjukkan KTP Kepri saat reservasi.", "en": "Show your Kepri ID card at reservation."},
    "cta":   {"id": "Chat kami di WhatsApp →",           "en": "Chat us on WhatsApp →"},
}

REVIEWS = [
    {
        "initial": "L",
        "name": "Lim C.",
        "source": "Google",
        "rating": 5,
        "text": {
            "id": "Minta terapis Dede untuk pijat kaki 2 jam — sangat menenangkan dan direkomendasikan!",
            "en": "Ask for Dede for a 2-hour leg massage — really relaxing and highly recommended!",
        },
    },
    {
        "initial": "S",
        "name": "Guest from Singapore",
        "source": "Tripadvisor",
        "rating": 5,
        "text": {
            "id": "Harga terjangkau, pijatannya kuat seperti sports massage. Sangat worth it — direkomendasikan!",
            "en": "Affordable prices, massage is really strong — almost like a sports massage. Totally worth it!",
        },
    },
    {
        "initial": "D",
        "name": "Dewa D.",
        "source": "Google",
        "rating": 5,
        "text": {
            "id": "Pijatan nyaman, harga terbaik yang pernah saya temukan. Semua staf sangat ramah.",
            "en": "Comfortable massages, the best price I've ever seen. All the staff are very kind.",
        },
    },
]

# photo key → filename in assets/photos/
TREATMENTS = {
    "reflexology": [
        {
            "slug": "foot-only",
            "category": {"id": "Refleksi", "en": "Reflexology"},
            "name":     {"id": "Refleksi Kaki",         "en": "Foot Reflexology"},
            "desc":     {
                "id": "Tekanan pada titik refleksi telapak kaki untuk melancarkan peredaran darah, meredakan pegal, dan menyeimbangkan energi tubuh.",
                "en": "Pressure on the reflex points of the soles to improve circulation, relieve fatigue, and rebalance the body's energy.",
            },
            "photo": "gallery-3.jpg",
            "prices": [("60 min", "Rp 150.000"), ("90 min", "Rp 200.000"), ("120 min", "Rp 250.000")],
        },
        {
            "slug": "complete-foot",
            "category": {"id": "Refleksi", "en": "Reflexology"},
            "name":     {"id": "Refleksi Kaki +\nPunggung, Bahu & Kepala", "en": "Complete Foot,\nBack, Shoulder & Head"},
            "desc":     {
                "id": "Kombinasi refleksi kaki dengan pijatan punggung, bahu, dan kepala — melepas tegang menyeluruh dari ujung kaki hingga kepala.",
                "en": "Foot reflexology combined with back, shoulder and head massage — full-body tension release from head to toe.",
            },
            "photo": "gallery-1.jpg",
            "prices": [("60 min", "Rp 170.000"), ("90 min", "Rp 220.000"), ("120 min", "Rp 270.000")],
        },
        {
            "slug": "organic-scrub",
            "category": {"id": "Refleksi", "en": "Reflexology"},
            "name":     {"id": "Scrub Kaki Organik & Pijat", "en": "Organic Foot Scrub Massage"},
            "desc":     {
                "id": "Eksfoliasi lembut dengan scrub organik untuk kulit kaki halus, dilanjutkan pijatan menenangkan.",
                "en": "Gentle exfoliation with an organic scrub for soft, renewed feet, followed by a soothing massage.",
            },
            "photo": "gallery-2.jpg",
            "prices": [("90 min", "Rp 270.000"), ("120 min", "Rp 320.000")],
        },
    ],
    "body": [
        {
            "slug": "traditional",
            "category": {"id": "Pijat Badan", "en": "Body Massage"},
            "name":     {"id": "Pijat Tradisional", "en": "Traditional Massage"},
            "desc":     {
                "id": "Teknik pijat khas Indonesia dengan tekanan menengah untuk meredakan otot kaku dan mengembalikan stamina.",
                "en": "Classic Indonesian technique with medium pressure to ease stiff muscles and restore stamina.",
            },
            "photo": "gallery-4.jpg",
            "prices": [("60 min", "Rp 170.000"), ("90 min", "Rp 220.000"), ("120 min", "Rp 270.000")],
        },
        {
            "slug": "balinese",
            "category": {"id": "Pijat Badan", "en": "Body Massage"},
            "name":     {"id": "Pijat Minyak Hangat Bali", "en": "Balinese Warm-Oil Massage"},
            "desc":     {
                "id": "Pijat aliran panjang dengan minyak aromaterapi hangat yang melemaskan otot dan menenangkan pikiran.",
                "en": "Long, flowing strokes with warm aromatherapy oil that loosens muscles and calms the mind.",
            },
            "photo": "gallery-5.jpg",
            "prices": [("60 min", "Rp 220.000"), ("90 min", "Rp 270.000"), ("120 min", "Rp 320.000")],
        },
        {
            "slug": "lulur",
            "category": {"id": "Pijat Badan", "en": "Body Massage"},
            "name":     {"id": "Lulur Badan & Pijat", "en": "Body Lulur & Massage"},
            "desc":     {
                "id": "Ritual lulur warisan keraton Jawa — mencerahkan dan menghaluskan kulit, dipadu pijatan relaksasi.",
                "en": "A Javanese royal lulur ritual — brightens and smooths the skin, paired with a relaxing massage.",
            },
            "photo": "gallery-6.jpg",
            "prices": [("90 min", "Rp 270.000"), ("120 min", "Rp 320.000")],
        },
        {
            "slug": "hot-stones",
            "category": {"id": "Pijat Badan", "en": "Body Massage"},
            "name":     {"id": "Batu Panas Mineral", "en": "Mineral Hot Stones"},
            "desc":     {
                "id": "Batu vulkanik hangat diletakkan pada titik tegang untuk melancarkan aliran darah dan melepas stres mendalam.",
                "en": "Warm volcanic stones placed on tension points to boost circulation and release deep-seated stress.",
            },
            "photo": "gallery-1.jpg",
            "prices": [("90 min", "Rp 340.000"), ("120 min", "Rp 390.000")],
        },
        {
            "slug": "foot-body",
            "category": {"id": "Pijat Badan", "en": "Body Massage"},
            "name":     {"id": "Kombinasi Kaki & Badan", "en": "Foot & Body Combination"},
            "desc":     {
                "id": "Paket lengkap refleksi kaki dan pijat badan dalam satu sesi — relaksasi total tanpa kompromi.",
                "en": "A complete package of foot reflexology and body massage in one session — total, uncompromised relaxation.",
            },
            "photo": "gallery-2.jpg",
            "prices": [("120 min", "Rp 320.000")],
        },
    ],
    "signature": [
        {
            "slug": "three-in-one",
            "category": {"id": "Signature", "en": "Signature"},
            "name":     {"id": "3-in-1 Healing Ritual", "en": "3-in-1 Healing Ritual"},
            "desc":     {
                "id": "Ritual istimewa Djaya: lulur tubuh, pijat aromaterapi, dan ear candling dalam satu pengalaman penyembuhan 150 menit.",
                "en": "Djaya's signature ritual: body scrub, aromatherapy massage, and ear candling in one 150-minute healing experience.",
            },
            "photo": "signature.jpg",
            "prices": [("150 min", "Rp 420.000")],
            "is_signature": True,
        },
    ],
    "additional": [
        {
            "slug": "neck-back",
            "category": {"id": "Tambahan", "en": "Additional"},
            "name":     {"id": "Leher, Punggung & Bahu", "en": "Neck, Back & Shoulder"},
            "desc":     {
                "id": "Fokus melepas ketegangan di area leher, punggung, dan bahu — ideal untuk pekerja kantoran.",
                "en": "Targeted relief for the neck, back and shoulders — ideal for desk-bound workers.",
            },
            "photo": "gallery-4.jpg",
            "prices": [("30 min", "Rp 95.000")],
        },
        {
            "slug": "ear-candling",
            "category": {"id": "Tambahan", "en": "Additional"},
            "name":     {"id": "Ear Candling", "en": "Ear Candling"},
            "desc":     {
                "id": "Terapi lilin telinga tradisional yang menenangkan dan membantu membersihkan kotoran telinga.",
                "en": "A traditional ear-candle therapy that soothes and helps clear the ear canal.",
            },
            "photo": "gallery-3.jpg",
            "prices": [("30 min", "Rp 100.000")],
        },
        {
            "slug": "guasa",
            "category": {"id": "Tambahan", "en": "Additional"},
            "name":     {"id": "Guasa (Kerok)", "en": "Gua Sha (Kerok)"},
            "desc":     {
                "id": "Teknik kerok tradisional untuk melancarkan peredaran darah dan meredakan masuk angin.",
                "en": "A traditional scraping technique to improve circulation and relieve aches and chills.",
            },
            "photo": "gallery-5.jpg",
            "prices": [("30 min", "Rp 120.000")],
        },
        {
            "slug": "cupping",
            "category": {"id": "Tambahan", "en": "Additional"},
            "name":     {"id": "Cupping (Bekam)", "en": "Cupping (Bekam)"},
            "desc":     {
                "id": "Terapi bekam dengan gelas vakum untuk detoksifikasi dan meredakan nyeri otot.",
                "en": "Cupping therapy with vacuum cups for detoxification and muscle-pain relief.",
            },
            "photo": "gallery-6.jpg",
            "prices": [("30 min", "Rp 120.000")],
        },
        {
            "slug": "v-ratus",
            "category": {"id": "Tambahan", "en": "Additional"},
            "name":     {"id": "V-Ratus", "en": "V-Ratus (V-Steam)"},
            "desc":     {
                "id": "Perawatan uap herbal tradisional khusus wanita untuk kebersihan dan kesegaran area kewanitaan.",
                "en": "A traditional herbal steam treatment for women, for feminine hygiene and freshness.",
            },
            "photo": "gallery-1.jpg",
            "prices": [("30 min", "Rp 175.000")],
        },
    ],
}

GALLERY_PHOTOS = [f"gallery-{i}.jpg" for i in range(1, 7)]
HERO_PHOTO = "hero.jpg"

def all_treatments():
    """Flat list of all treatments across all categories."""
    for items in TREATMENTS.values():
        yield from items
