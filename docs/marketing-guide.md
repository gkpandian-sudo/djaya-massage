# Djaya Massage & Reflexology — Instagram Marketing Operations Guide

> **Spa:** Djaya Massage & Reflexology · Penuin Centre, Lubuk Baja, Batam  
> **IG:** @djayamassage · **WA:** wa.me/6285278355590  
> **Pipeline version:** 2.0 (animated reels) · **Last updated:** 2026-07-09

---

## 1. Content Pillars

Five content pillars drive every post. Each has a dedicated reel template:

| Pillar | Template | Post type | Frequency |
|--------|----------|-----------|-----------|
| Service spotlight | R1 | Treatment deep-dive | 2× / week |
| Social proof | R2 | Guest testimonial | 1× / week |
| Ambiance / BTS | R3 | Behind-the-scenes | 1× / week |
| Promo / Urgency | R4 | Limited-time offer | 1× / week |
| Location / Brand | R5 | Find us / brand story | 1× / week |

Each reel runs with a hook-formula caption (`scripts/captions.py`) and a language variant (id/en) set by the 4-week rotation calendar.

---

## 2. 12-Month Seasonal Themes

Align promos and copy to Indonesian holidays and local calendar events:

| Month | Theme | Hook angle |
|-------|-------|------------|
| January | New Year reset | Fresh start, detox your body |
| February | Valentine's | Couples massage packages |
| March | Pre-Nyepi wind-down | Calm before the silence |
| April | Ramadan & Lebaran | Pamper before mudik |
| May | Post-Lebaran recovery | Recover your body after the journey |
| June | School holiday | Bring the family, kids welcome |
| July | Mid-year check-in | Half-year self-care audit |
| August | HUT RI (Independence Day) | Local pride, local healer |
| September | Back to work | Reset for Q4 |
| October | Pre year-end rush | Beat burnout before December |
| November | Year-end gratitude | Gift vouchers for colleagues |
| December | Year-end closure | Last chance before we close for CNY prep |

---

## 3. KPI Targets

Track these monthly via Instagram Insights:

| Metric | Baseline | 3-month target | 6-month target |
|--------|----------|---------------|----------------|
| Reel plays (avg) | — | 500 | 1,500 |
| Reach per post | — | 300 | 1,000 |
| Profile visits from reels | — | 50 / week | 200 / week |
| WA link taps | — | 10 / week | 40 / week |
| Followers gained | — | +50 / month | +150 / month |
| Save rate | — | ≥3% of reach | ≥5% of reach |

Review KPIs on the first Monday of each month. Adjust weak-performing templates before the next 4-week cycle.

---

## 4. Hashtag Strategy

The pipeline auto-generates hashtags via `scripts/captions.py::_tags()`.

**Always-on (every post):**
`#djayamassage` `#djayamassagesg`

**Lokal set (lang=id — Batam audience):**
`#pijatbatam` `#pijatrefleksi` `#reflexology` `#pijattradisional` `#jasapijatbatam` `#batamkota`

**SG set (lang=en — Singapore visitor audience):**
`#singaporemassage` `#massagesg` `#relaxsg` `#sgwellness` `#chinatownsg` `#tanjongpagar` `#singaporelife`

**Wellness (universal):**
`#massage` `#wellness` `#relaxation` `#selfcare` `#reflexologytherapy` `#bodycare` `#holistichealth`

**Rotation rule:** Use `lang=id` for Mon/Wed/Fri posts targeting local Batam/Indonesian audience. Use `lang=en` for Thu/Sat posts targeting Singapore ferry visitors and expats. Sunday always `lang=id` (family audience).

---

## 5. Caption Formulas

Five hook formulas, one per template:

| Template | Hook type | Opening line formula |
|----------|-----------|----------------------|
| R1 | Pain-point | "Capek setelah seharian kerja? 😩" / "Feeling drained after a long day?" |
| R2 | Social proof | "Kata mereka tentang Djaya... 🤍" / "Here's what our guests say..." |
| R3 | Curiosity / BTS | "Di balik layar Djaya Massage 🎬" / "A peek behind the scenes..." |
| R4 | Urgency | "Jangan sampai ketinggalan! ⏳" / "Don't miss out!" |
| R5 | Discovery | "Tau nggak, ada spa di Batam yang..." / "Did you know there's a hidden gem..." |

Every caption ends with a WhatsApp CTA and the hashtag block. Keep captions under 2,200 characters (Instagram limit).

---

## 6. Engagement Tactics

**First 30 minutes after posting:**
1. Reply to every comment within 30 minutes to boost algorithmic ranking.
2. Share the reel to Stories immediately after posting.
3. Send a WA broadcast to the guest list announcing the new post.

**Weekly:**
- Pin the best-performing reel of the week to the profile grid.
- Archive reels that fall below 200 plays after 14 days.
- Check DMs every evening; unanswered DMs after 24h cost bookings.

**Monthly:**
- Reshare top testimonial as a new R2 reel with updated copy.
- Run a 48-hour giveaway on the best-performing post month (e.g., free foot scrub for 1 winner who shares the reel to Stories).

---

## 7. Singapore Visitor Differentiation

Batam is a popular day-trip and weekend destination for Singapore residents (45-minute ferry). Target this audience with:

- **lang=en reels** on Thursday and Saturday (pre-weekend and weekend posting).
- **R5 location reel** every 2 weeks showing the Penuin Centre address and ferry route.
- **Caption copy**: mention "10 min from Harbour Bay ferry terminal" and "Batam day-trip package".
- **Hashtags**: include `#batamferry`, `#harbourbayferry`, `#batam` in R5 extras.
- **Promo idea**: "Singapore residents get 15% off — show your Singapore ID."

---

## 8. Crisis Plan

| Situation | Response |
|-----------|----------|
| Negative review on IG | Reply publicly within 2 hours: "Terima kasih masukkannya — kami minta maaf atas pengalaman ini dan akan menghubungi Anda langsung via WA." Never delete the comment. |
| Reel render fails | Use a static image post for that day; reschedule the reel for the next available slot using `--template rX --date YYYY-MM-DD`. |
| Pipeline GitHub Action fails | Check Actions logs; most failures are audio file path issues or `ffmpeg` version. Manual trigger: `gh workflow run post-reel.yml -f template=r5`. |
| Account flagged / restricted | Pause all auto-posting. Switch to manual posts. Review recent hashtags for policy violations. Do not post for 48 hours. |
| Power/internet outage on post day | GitHub Actions will retry on the next cron trigger. If missed, manually run: `python scripts/run_ig_reel.py` on any machine with env vars set. |

---

## 9. Monthly Checklist

Run this checklist on the first Monday of every month:

- [ ] Pull latest from `main`: `git pull origin main`
- [ ] Review last month's KPIs in Instagram Insights; note top and bottom performers
- [ ] Update `scripts/content.py` if treatment menu changed (new prices, new treatments)
- [ ] Rotate testimonials: add new Google/Tripadvisor reviews to `REVIEWS` list
- [ ] Update `PROMO` dict in `content.py` for the month's promotion
- [ ] Check 4-week calendar in `content_rotation.py` — adjust if a local holiday shifts posting days
- [ ] Verify `data/rotation.json` `week_index` matches current week (0–3)
- [ ] Run preview: `python scripts/preview_week.py` — check all 7 days render correctly
- [ ] Run render test: `python scripts/generate_reel_animated.py --template r1 --duration-scale 0.15 --fps 6` — confirm no crashes
- [ ] Archive output folder: move last month's MP4s to `output/archive/YYYY-MM/`
- [ ] Review and rotate the `photo_log` in `rotation.json` if manually overriding photos
