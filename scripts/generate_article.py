#!/usr/bin/env python3
"""
Daily NEET Dropper article generator for neetdropper.com
Generates a complete HTML article using Claude API and saves it to the repo.
Run via GitHub Actions on a daily schedule.
"""

import anthropic
import os
import sys
from datetime import datetime

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


def update_sitemap(slug, today_str):
    path = "sitemap.xml"
    if not os.path.exists(path):
        print("sitemap.xml not found, skipping update.")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "/" + slug + ".html" in content:
        print("sitemap.xml already contains " + slug + ", skipping.")
        return

    entry = (
        "  <url>\n"
        "    <loc>https://neetdropper.com/" + slug + ".html</loc>\n"
        "    <lastmod>" + today_str + "</lastmod>\n"
        "    <changefreq>monthly</changefreq>\n"
        "    <priority>0.75</priority>\n"
        "  </url>"
    )

    content = content.replace("</urlset>", entry + "\n</urlset>")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("sitemap.xml updated with " + slug)


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

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved " + filename + " (" + str(len(html)) + " bytes)")

    update_sitemap(topic["slug"], today_str)
    print("Done!")


if __name__ == "__main__":
    main()
