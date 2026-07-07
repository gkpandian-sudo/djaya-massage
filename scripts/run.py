#!/usr/bin/env python3
"""
run.py — generate all Djaya Massage & Reflexology Instagram content locally.

Usage:
  python scripts/run.py                  # generate everything
  python scripts/run.py --type posts     # posts (1080x1080) only
  python scripts/run.py --type reels     # reels (1080x1920) only
  python scripts/run.py --slug balinese  # single treatment by slug
"""
import sys
import argparse
from pathlib import Path

# Add scripts/ to path so sibling imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

import content as C
import generate_post as P
import generate_reel as R


def run_posts():
    print("\n-- POSTS (1080x1080) -------------------------------------------")

    print("\n[Treatments]")
    for t in C.all_treatments():
        P.render_treatment(t)

    print("\n[Signature]")
    P.render_signature()

    print("\n[Testimonials]")
    for i, review in enumerate(C.REVIEWS):
        photo = C.GALLERY_PHOTOS[i % len(C.GALLERY_PHOTOS)]
        P.render_testimonial(review, photo, i)

    print("\n[Promo]")
    P.render_promo()

    print("\n[Location]")
    P.render_location()

    print("\n[Ambiance — all gallery photos]")
    for i, photo in enumerate(C.GALLERY_PHOTOS):
        P.render_ambiance(photo, i)

    print("\n[Booking Reminder]")
    P.render_booking_reminder()


def run_reels():
    print("\n-- REELS (1080x1920) -------------------------------------------")

    print("\n[Treatments]")
    for t in C.all_treatments():
        R.render_treatment(t)

    print("\n[Signature]")
    R.render_signature()

    print("\n[Testimonials]")
    for i, review in enumerate(C.REVIEWS):
        photo = C.GALLERY_PHOTOS[i % len(C.GALLERY_PHOTOS)]
        R.render_testimonial(review, photo, i)

    print("\n[Promo]")
    R.render_promo()

    print("\n[Location]")
    R.render_location()

    print("\n[Ambiance]")
    for i, photo in enumerate(C.GALLERY_PHOTOS):
        R.render_ambiance(photo, i)

    print("\n[Booking Reminder]")
    R.render_booking_reminder()


def run_single(slug: str):
    for t in C.all_treatments():
        if t["slug"] == slug:
            print(f"\n[Post + Reel] {slug}")
            P.render_treatment(t)
            R.render_treatment(t)
            return
    print(f"Slug '{slug}' not found. Available:")
    for t in C.all_treatments():
        print(f"  {t['slug']}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type",  choices=["posts", "reels", "all"], default="all")
    parser.add_argument("--slug",  default="")
    args = parser.parse_args()

    if args.slug:
        run_single(args.slug)
        return

    if args.type in ("posts", "all"):
        run_posts()
    if args.type in ("reels", "all"):
        run_reels()

    print("\nDone. Check output/posts/ and output/reels/")


if __name__ == "__main__":
    main()
