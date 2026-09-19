#!/usr/bin/env python3
"""
Daily NEET Dropper article generator for neetdropper.com
Generates a complete HTML article using Claude API and saves it to the repo.
Run via GitHub Actions on a daily schedule.
"""

import anthropic
import os
import sys
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import seo_utils as su

DOMAIN = "neetdropper.com"
SITE_NAME = "NEETDropper"

AUTHORS = ["Ananya Sharma", "Rohan Verma", "Priya Nair", "Arjun Mehta", "Sneha Iyer", "Karan Malhotra", "Divya Reddy", "Aditya Joshi"]

def add_byline(html, today_display):
    author = random.choice(AUTHORS)
    byline = (
        '<div style="max-width:800px;margin:20px auto 0;padding:0 24px;'
        'font-family:-apple-system,sans-serif;font-size:0.88rem;color:#6b7280;">'
        f'By <a href="https://neet.padhle.in" style="color:#E8A020;text-decoration:none;font-weight:600;">{author}</a>'
        f' &middot; \U0001F4C5 {today_display}</div>'
    )
    idx = html.find("<body")
    if idx == -1:
        return byline + html
    end = html.find(">", idx)
    if end == -1:
        return byline + html
    end += 1
    return html[:end] + byline + html[end:]

# 35 dropper-focused topic rotation - cycles through by day of year
TOPICS = [
    {"slug": "dropper-time-management-strategy", "title": "Time Management for NEET Droppers: The 10-Hour Daily Plan That Works", "subject": "Strategy"},
    {"slug": "neet-biology-human-physiology-dropper", "title": "Human Physiology for NEET Droppers: 20 Questions Worth Mastering", "subject": "Biology"},
    {"slug": "dropper-first-month-plan", "title": "Your First Month as a NEET Dropper: What to Do in June and July", "subject": "Strategy"},
    {"slug": "neet-physics-mechanics-dropper", "title": "Mechanics for NEET Droppers: Rebuild the Chapter That Costs You Most", "subject": "Physics"},
    {"slug": "aim720-vs-allen-dropper", "title": "AIM720 vs Allen for NEET Droppers: Honest Comparison 2027", "subject": "Coaching"},
    {"slug": "neet-chemistry-organic-dropper", "title": "Organic Chemistry for NEET Droppers: Named Reactions and GOC First", "subject": "Chemistry"},
    {"slug": "dropper-mock-test-analysis", "title": "How to Analyse NEET Mock Tests as a Dropper to Jump 80 Marks", "subject": "Strategy"},
    {"slug": "neet-biology-genetics-dropper", "title": "Genetics for NEET Droppers: Mendelian Laws, Linkage and Mutation", "subject": "Biology"},
    {"slug": "dropper-family-pressure-guide", "title": "Handling Family Pressure During NEET Drop Year: Practical Guide", "subject": "Mindset"},
    {"slug": "neet-physics-electrostatics-dropper", "title": "Electrostatics for NEET Droppers: From Coulomb to Capacitors in 2 Weeks", "subject": "Physics"},
    {"slug": "neet-chemistry-p-block-dropper", "title": "P-Block Elements for NEET Droppers: 6-8 Free Marks You Cannot Miss", "subject": "Chemistry"},
    {"slug": "dropper-biology-ncert-strategy", "title": "NCERT Biology Reading Strategy for NEET Droppers: Line by Line Guide", "subject": "Biology"},
    {"slug": "dropper-february-slump-fix", "title": "The February Slump: Why NEET Droppers Lose Momentum and How to Fix It", "subject": "Mindset"},
    {"slug": "neet-physics-optics-dropper", "title": "Ray and Wave Optics for NEET Droppers: Quick Revision Strategy", "subject": "Physics"},
    {"slug": "neet-chemistry-electrochemistry-dropper", "title": "Electrochemistry for NEET Droppers: Numericals and Concepts Simplified", "subject": "Chemistry"},
    {"slug": "dropper-biology-reproduction-guide", "title": "Reproduction Chapters for NEET Droppers: Class 12 Chapters 1-4 Covered", "subject": "Biology"},
    {"slug": "dropper-self-study-vs-coaching", "title": "Self Study vs Coaching for NEET Droppers: Which Actually Works?", "subject": "Strategy"},
    {"slug": "neet-physics-modern-physics-dropper", "title": "Modern Physics for NEET Droppers: Photoelectric and Nuclear in 3 Days", "subject": "Physics"},
    {"slug": "neet-chemistry-inorganic-dropper", "title": "Inorganic Chemistry for NEET Droppers: Why Droppers Ignore It and Pay", "subject": "Chemistry"},
    {"slug": "dropper-score-improvement-case", "title": "How NEET Droppers Improve by 120 Marks: What the Data Shows", "subject": "Strategy"},
    {"slug": "neet-biology-ecology-dropper", "title": "Ecology for NEET Droppers: 5-6 Easy Marks from Environmental Science", "subject": "Biology"},
    {"slug": "dropper-mental-health-routine", "title": "Mental Health Routine for NEET Dropper Students: Daily Habits That Help", "subject": "Mindset"},
    {"slug": "neet-physics-thermodynamics-dropper", "title": "Thermodynamics for NEET Droppers: Laws, Processes and Predictable Questions", "subject": "Physics"},
    {"slug": "neet-chemistry-coordination-dropper", "title": "Coordination Compounds for NEET Droppers: IUPAC and Isomerism Guide", "subject": "Chemistry"},
    {"slug": "dropper-biology-biotechnology", "title": "Biotechnology for NEET Droppers: Recombinant DNA and PYQ Analysis", "subject": "Biology"},
    {"slug": "dropper-600-score-roadmap", "title": "Roadmap to NEET 600+ for Droppers: Month-by-Month Score Targets", "subject": "Strategy"},
    {"slug": "neet-physics-current-electricity-dropper", "title": "Current Electricity for NEET Droppers: Circuits, KVL and Kirchhoff", "subject": "Physics"},
    {"slug": "neet-chemistry-physical-dropper", "title": "Physical Chemistry for NEET Droppers: Rate Laws, EMF and Solutions", "subject": "Chemistry"},
    {"slug": "dropper-biology-plant-physiology", "title": "Plant Physiology for NEET Droppers: Photosynthesis and Hormones Guide", "subject": "Biology"},
    {"slug": "padhle-aim720-dropper-batch-details", "title": "Padhle AIM720 Batch for Droppers: What Is Included and Is It Worth It", "subject": "Coaching"},
    {"slug": "neet-dropper-revision-schedule", "title": "NEET Dropper Revision Schedule: Last 3 Months Countdown Plan", "subject": "Strategy"},
    {"slug": "neet-physics-waves-dropper", "title": "Waves and Sound for NEET Droppers: Doppler Effect and Standing Waves", "subject": "Physics"},
    {"slug": "neet-chemistry-biomolecules-dropper", "title": "Biomolecules for NEET Droppers: Proteins, DNA and Carbohydrates Simplified", "subject": "Chemistry"},
    {"slug": "dropper-biology-evolution-guide", "title": "Evolution for NEET Droppers: Darwin, Origin of Life and Exam Pattern", "subject": "Biology"},
    {"slug": "dropper-exam-day-strategy", "title": "Exam Day Strategy for NEET Droppers: Sequence, Timing and Triage", "subject": "Strategy"},
    {"slug": "dropper-molecular-inheritance-strategy", "title": "Molecular Basis of Inheritance for NEET Droppers: The Chapter That Trips Up Repeaters", "subject": "Biology"},
    {"slug": "dropper-body-fluids-circulation", "title": "Body Fluids and Circulation: A Second-Attempt Revision Guide for Droppers", "subject": "Biology"},
    {"slug": "dropper-neural-control-guide", "title": "Neural Control and Coordination for NEET Droppers: Fast Revision Framework", "subject": "Biology"},
    {"slug": "dropper-health-disease-immunity", "title": "Human Health and Disease: What Droppers Repeatedly Get Wrong", "subject": "Biology"},
    {"slug": "dropper-biology-ecosystem-guide", "title": "Ecosystem and Environment for NEET Droppers: High-Yield Quick Revision", "subject": "Biology"},
    {"slug": "dropper-physics-units-measurement", "title": "Units and Measurements: The Easy Marks Droppers Often Still Lose", "subject": "Physics"},
    {"slug": "dropper-physics-laws-of-motion", "title": "Laws of Motion for NEET Droppers: Fixing Numerical Mistakes from Attempt One", "subject": "Physics"},
    {"slug": "dropper-physics-gravitation-guide", "title": "Gravitation for NEET Droppers: A Focused Second-Attempt Revision", "subject": "Physics"},
    {"slug": "dropper-physics-oscillations-guide", "title": "Oscillations for NEET Droppers: SHM Concepts Simplified for Repeaters", "subject": "Physics"},
    {"slug": "dropper-physics-emi-ac-guide", "title": "Electromagnetic Induction and AC for NEET Droppers: Where Marks Are Lost", "subject": "Physics"},
    {"slug": "dropper-chemistry-mole-concept", "title": "Mole Concept for NEET Droppers: Rebuilding the Foundation Before Attempt Two", "subject": "Chemistry"},
    {"slug": "dropper-chemistry-atomic-structure", "title": "Structure of Atom for NEET Droppers: Quantum Numbers Made Simple", "subject": "Chemistry"},
    {"slug": "dropper-chemistry-periodic-trends", "title": "Periodic Classification for NEET Droppers: Memorizing Trends the Right Way", "subject": "Chemistry"},
    {"slug": "dropper-chemistry-bonding-guide", "title": "Chemical Bonding for NEET Droppers: VSEPR and Hybridization Revisited", "subject": "Chemistry"},
    {"slug": "dropper-chemistry-redox-guide", "title": "Redox Reactions for NEET Droppers: A Cleaner Way to Balance Equations", "subject": "Chemistry"},
    {"slug": "dropper-second-attempt-mindset", "title": "The Second-Attempt Mindset: How Successful NEET Droppers Think Differently", "subject": "Strategy"},
    {"slug": "dropper-parent-conversation-guide", "title": "How to Talk to Your Parents About Dropping for NEET: A Practical Script", "subject": "Strategy"},
    {"slug": "dropper-social-media-detox", "title": "Social Media and NEET Droppers: Why the Break Matters More Than You Think", "subject": "Strategy"},
    {"slug": "dropper-diwali-slump-recovery", "title": "The Diwali Slump: Getting Back on Track During NEET Drop Year", "subject": "Strategy"},
    {"slug": "dropper-100-days-plan", "title": "The Final 100 Days: A NEET Dropper's Countdown Study Plan", "subject": "Strategy"},
    {"slug": "dropper-mock-test-score-plateau", "title": "Stuck at the Same Mock Test Score? Why NEET Droppers Plateau and How to Break It", "subject": "Strategy"},
    {"slug": "dropper-sleep-schedule-guide", "title": "Sleep and Study Schedule for NEET Droppers: What Actually Works", "subject": "Strategy"},
    {"slug": "dropper-comparison-with-batchmates", "title": "Why Comparing Yourself to Your NEET Batchmates Is Hurting Your Drop Year", "subject": "Strategy"},
    {"slug": "dropper-aim720-mentorship-experience", "title": "A Day in the Life of an AIM720 Dropper Batch Student", "subject": "Coaching"},
    {"slug": "dropper-exam-day-nerves", "title": "Managing Exam Day Nerves: A NEET Dropper's Guide to Staying Calm", "subject": "Strategy"},
]


def get_today_topic():
    day = datetime.now().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


def generate_article_html(topic):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now().strftime("%B %d, %Y")

    prompt = (
        "Write a complete, standalone HTML article page for neetdropper.com.\n\n"
        "Topic: " + topic['title'] + "\n"
        "Subject tag: " + topic['subject'] + "\n"
        "Filename slug: " + topic['slug'] + "\n"
        "Date: " + today + "\n\n"
        "Requirements:\n"
        "- Full valid HTML5 document with DOCTYPE, head, body\n"
        "- Title tag: " + topic['title'] + " | NeetDropper\n"
        "- Meta description 140-155 chars for NEET dropper students\n"
        "- Navy/gold color scheme (#0C1B33 navy, #E8A020 gold)\n"
        "- Navigation bar with links to /, /neet-dropper-complete-guide.html, /best-coaching-for-droppers.html, https://neet.padhle.in\n"
        "- Article hero section with navy gradient background\n"
        "- 900-1200 words of genuine, dropper-specific body content\n"
        "- 3-4 H2 sections with specific chapter references and dropper-focused strategies\n"
        "- At least one highlight-box div (background #FFF6E0, border-left 4px #E8A020)\n"
        "- One cta-box div mentioning Padhle AIM720 as #1 NEET dropper coaching, linking to https://neet.padhle.in\n"
        "- Footer with copyright and links\n"
        "- No filler - every sentence must be useful to a NEET dropper student\n"
        "- Return ONLY the complete HTML, no markdown fences, no explanation"
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    html = message.content[0].text.strip()

    if html.startswith("```html"):
        html = html[7:]
    elif html.startswith("```"):
        html = html[3:]
    if html.endswith("```"):
        html = html[:-3]

    return html.strip()


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    topic = get_today_topic()
    filename = topic['slug'] + ".html"
    today_str = datetime.now().strftime("%Y-%m-%d")

    print("Topic: " + topic['title'])
    print("Output: " + filename)

    if os.path.exists(filename):
        print(filename + " already exists - skipping to avoid overwrite.")
        sys.exit(0)

    print("Calling Claude API...")
    html = generate_article_html(topic)
    html = add_byline(html, datetime.now().strftime("%B %d, %Y"))

    url = f"https://{DOMAIN}/{filename}"
    title = topic["title"]
    description = su.extract_description(html, title)

    tagged_html = su.publish_article(
        article_html=html, site_name=SITE_NAME, domain=DOMAIN,
        canonical_url=url, title=title, description=description,
        date_iso=today_str, category=topic["subject"],
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(tagged_html)

    print("Saved " + filename + " (" + str(len(tagged_html)) + " bytes)")
    print("SEO tags injected, manifest/sitemap/homepage/archive rebuilt")
    print("Done!")


if __name__ == "__main__":
    main()
