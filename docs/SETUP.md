# Djaya Instagram Pipeline — Setup Guide

## Prerequisites

- **The GitHub repo must be PUBLIC.** Meta's servers fetch the image URL unauthenticated from
  `raw.githubusercontent.com`. A private repo returns 404 and every publish fails at container creation.
  > Alternative: use a public image host (Cloudinary, S3, etc.) and push images there instead.
- @djayamassage converted to an Instagram **Business** account
- A Facebook **Page** linked to the Business account
- A Meta for Developers app with `instagram_basic` + `instagram_content_publish` permissions

---

## Step 1 — Convert @djayamassage to Business Account

1. Instagram app → Settings > Account > Switch to Professional Account
2. Choose **Business**, select category (Spa / Health & Beauty)
3. Link to a Facebook Page (create one for Djaya if needed)

---

## Step 2 — Create Meta App

1. Go to https://developers.facebook.com/apps/
2. Click **Create App** → **Business** type
3. Add product: **Instagram Graph API**
4. Note the **App ID** and **App Secret** from App Settings > Basic

---

## Step 3 — Generate Long-Lived Access Token

```bash
# 1. Get a short-lived user token from Graph API Explorer:
#    https://developers.facebook.com/tools/explorer
#    Permissions: instagram_basic, instagram_content_publish, pages_show_list

# 2. Exchange for long-lived token (~60 days):
curl "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"

# 3. Get the Instagram Business Account ID:
curl "https://graph.facebook.com/v19.0/me/accounts?access_token=LONG_LIVED_TOKEN"
# Then:
curl "https://graph.facebook.com/v19.0/PAGE_ID?fields=instagram_business_account&access_token=LONG_LIVED_TOKEN"
```

---

## Step 4 — Add GitHub Secrets

Repo → Settings → Secrets and variables → Actions → New repository secret

| Secret             | Value                                        |
|--------------------|----------------------------------------------|
| `IG_USER_ID`       | Instagram Business Account numeric ID        |
| `META_ACCESS_TOKEN`| Long-lived Page access token                 |

`GITHUB_TOKEN` is auto-provided — never set it manually.

---

## Step 5 — Make the Repo Public

Go to Settings → Danger Zone → Change visibility → **Public**

This is required for `raw.githubusercontent.com` CDN URLs to be reachable by Meta's servers.

---

## Step 6 — Token Renewal (every ~55 days)

Long-lived tokens expire in ~60 days. Renew before expiry:

1. Go to https://developers.facebook.com/tools/explorer
2. Generate a new short-lived token with the same permissions
3. Run the exchange curl above to get a new long-lived token
4. Update the `META_ACCESS_TOKEN` secret in GitHub Settings

**Set a calendar reminder 55 days after each renewal.**

---

## Step 7 — Dry Run Test

1. Actions → Instagram Post → Run workflow
2. Set `dry_run = true`, any `post_type`
3. Confirm the workflow passes and a JPG appears in `output/posts/`
4. Run with `dry_run = false` to publish for real

---

## Weekly Schedule (auto)

| Day       | Post Type          |
|-----------|--------------------|
| Monday    | service_spotlight  |
| Tuesday   | signature          |
| Wednesday | testimonial        |
| Thursday  | promo              |
| Friday    | ambiance           |
| Saturday  | location           |
| Sunday    | booking_reminder   |

Posts go out at **09:00 WIB** (02:00 UTC) every day.

---

## Updating Content

Edit `scripts/content.py` to:
- Add or update treatments (slug, name, desc, prices, photo)
- Add new customer reviews
- Update promo terms or business hours

Run `python scripts/run.py` locally to regenerate all static preview images.

---

## Local Dry Run

```powershell
# From djaya-massage/ root:
$env:DRY_RUN = "true"
$env:POST_TYPE = "service_spotlight"   # or any other type
python scripts/run_ig.py
```
