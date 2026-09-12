#!/usr/bin/env python3
"""
Builds the BCS Fellowship evidence site.

Run it from this folder:      python3 build_site.py
It writes index.html, responsibility.html, mentoring.html, innovation.html,
standing.html and evidence-matrix.html.

Two things it does that matter:

1. The STAR statements come from ../_drafts/*.txt, which are the SAME files the
   Word form was built from. So the site can never drift from the application.
   Edit the .txt, rebuild the form, rerun this. They stay identical.

2. Every evidence item marked kind="file" points at evidence/<name>. If that
   file is not in the evidence/ folder at build time, the item renders as plain
   text with a "certificate on file" note instead of a link. That means the site
   can never ship a broken link to an assessor. Drop the PDFs in and rerun.
"""

import os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
DRAFTS = os.path.join(HERE, "..", "_drafts")
EVDIR = os.path.join(HERE, "evidence")

SITE_TITLE = "Somesh Rahul | BCS Fellowship Evidence"
CONTACT = "someshrahul@ieee.org"

PAGES = [
    ("index.html",          "Overview"),
    ("responsibility.html", "Responsibility"),
    ("mentoring.html",      "Mentoring &amp; Coaching"),
    ("innovation.html",     "Invention &amp; Innovation"),
    ("standing.html",       "Standing in the Community"),
    ("evidence-matrix.html","Evidence Matrix"),
]

# ---------------------------------------------------------------- STAR text

def star(fname):
    """Parse a SITUATION/TASK/ACTION/RESULT text file into ordered blocks."""
    path = os.path.join(DRAFTS, fname)
    text = open(path, encoding="utf-8").read()
    out, key, buf = [], None, []
    for line in text.split("\n"):
        s = line.strip()
        if s in ("SITUATION", "TASK", "ACTION", "RESULT"):
            if key:
                out.append((key, "\n".join(buf).strip()))
            key, buf = s, []
        else:
            buf.append(line)
    if key:
        out.append((key, "\n".join(buf).strip()))
    return out

def words(blocks):
    return sum(len(b.split()) for _, b in blocks)

def star_html(blocks, criterion, section):
    parts = [
        '<div class="star">',
        f'  <div class="star-head">{section} &mdash; {criterion}'
        f'<span>Statement as submitted &middot; {words(blocks)} words</span></div>',
        '  <div class="star-body">',
    ]
    for label, body in blocks:
        parts.append(f'    <h5>{label.title()}</h5>')
        for para in re.split(r"\n\s*\n", body):
            para = para.strip()
            if para:
                parts.append(f'    <p>{html.escape(para)}</p>')
    parts += ['  </div>', '</div>']
    return "\n".join(parts)

# ---------------------------------------------------------------- evidence

def ev(label, url=None, kind="live", note=""):
    """kind: live (external URL) | file (evidence/<url>) | hold (nothing yet)"""
    return {"label": label, "url": url, "kind": kind, "note": note}

def ev_html(items):
    rows = ['<ul class="ev">']
    for it in items:
        label, url, kind, note = it["label"], it["url"], it["kind"], it["note"]
        if kind == "file":
            exists = url and os.path.isfile(os.path.join(EVDIR, url))
            if exists:
                body = f'<a href="evidence/{url}">{label}</a><span class="pill file">PDF</span>'
            else:
                body = (f'{label}<span class="pill hold">on file</span>')
        elif kind == "live" and url:
            body = f'<a href="{url}" rel="noopener">{label}</a><span class="pill live">verify</span>'
        else:
            body = f'{label}<span class="pill hold">on file</span>' 
        cls = "" if (kind == "live" and url) else ' class="pending"'
        rows.append(f'  <li{cls}>{body}'
                    + (f'<br><span class="note" style="margin:2px 0 0;display:block">{note}</span>' if note else "")
                    + '</li>')
    rows.append('</ul>')
    return "\n".join(rows)

# ---------------------------------------------------------------- shell

def shell(current, title, hero, body):
    ACTIVE = ' class="active"'
    nav = "\n".join(
        '        <li><a href="%s"%s>%s</a></li>' % (f, ACTIVE if f == current else "", n)
        for f, n in PAGES
    )
    crumb = "" if current == "index.html" else (
        '  <div class="wrap"><div class="crumb">'
        f'<a href="index.html">Overview</a> &rsaquo; {title}</div></div>\n'
    )
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &mdash; {SITE_TITLE}</title>
<meta name="description" content="Supporting evidence for the BCS Fellowship (FBCS) application of Somesh Rahul, experiential route.">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header>
  <div class="nav">
    <a href="index.html" class="brand">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
      Somesh Rahul &middot; BCS Fellowship Evidence
    </a>
    <ul class="navlinks">
{nav}
    </ul>
  </div>
</header>
{crumb}{hero}
<main>
  <div class="wrap">
{body}
  </div>
</main>
<footer>
  <div class="wrap">
    <p><strong>Somesh Rahul</strong> &middot; Principal Product Manager, Emerging Technology, Walmart Global Tech &middot; IEEE Senior Member</p>
    <p>Supporting evidence for a BCS Fellowship (FBCS) application, experiential route. Contact: {CONTACT}</p>
    <p style="margin-top:9px">This site exists to let a BCS assessor verify the claims in the application form. Nothing here requires a login.</p>
  </div>
</footer>
</body>
</html>
"""

def hero(eyebrow, h1, lede, sub="", extra="", portrait=""):
    pic = (f'<img class="portrait" src="assets/{portrait}" width="560" height="560" '
           f'alt="Somesh Rahul" loading="eager">') if portrait else ""
    cls = " hero-split" if portrait else ""
    return f"""<section class="hero">
  <div class="wrap{cls}">
    {pic}
    <div class="hero-text">
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    {f'<p class="sub">{sub}</p>' if sub else ''}
    {extra}
    </div>
  </div>
</section>
"""

ASSESSOR = """<div class="assessor">
  <h4>For the BCS assessor</h4>
  <p>Each page on this site carries one of the four statements exactly as it appears in the
  application form, followed by the primary sources for the claims it makes. The statement text is
  generated from the same file the form was built from, so the two cannot drift apart.</p>
  <p>Items marked <span class="pill live">verify</span> are public links that open without a login.
  Items marked <span class="pill hold">on file</span> are original certificates and letters held by the
  applicant and supplied to BCS on request. If any link fails, please email {c} and I will send the
  document directly.</p>
</div>""".format(c=CONTACT)

# ---------------------------------------------------------------- patents

PATENTS = [
    ("US 11,438,225 B2", "US, granted 6 Sep 2022", "Commissioning and controlling load control devices",
     "https://patents.google.com/patent/US11438225B2/en", "Proximity commissioning family"),
    ("US 12,166,627 B2", "US, granted 10 Dec 2024", "Commissioning and controlling load control devices",
     "https://patents.google.com/patent/US12166627B2/en", "Proximity commissioning family"),
    ("EP 3,935,791 B1", "EPO, granted 2024", "Commissioning and controlling load control devices",
     "https://patents.google.com/patent/EP3935791B1/en", "Proximity commissioning family"),
    ("CA 3,115,114 C", "Canada, granted 18 Jul 2023", "Load control system configuration tool",
     "https://patents.google.com/patent/CA3115114C/en", "Configuration and estimation family"),
    ("CN 113,170,565 B", "China, granted", "Load control system, method and computing device for controlling electrical loads",
     "https://patents.google.com/patent/CN113170565B/en", "Configuration and estimation family"),
    ("CN 114,761,659 B", "China, granted 6 Sep 2024", "Control of covering materials and electric window treatments",
     "https://patents.google.com/patent/CN114761659B/en", "Motorised window treatment family"),
    ("USD 940,160 S1", "US design, 4 Jan 2022", "Display screen with animated graphical user interface",
     "https://patents.google.com/patent/USD940160S1/en", "Building and lighting control interface"),
    ("USD 993,972 S1", "US design, 1 Aug 2023", "Display screen with graphical user interface",
     "https://patents.google.com/patent/USD993972S1/en", "Building and lighting control interface"),
    ("USD 1,070,883 S1", "US design, 15 Apr 2025", "Display screen with graphical user interface",
     "https://patents.google.com/patent/USD1070883S1/en", "Building and lighting control interface"),
]

def patent_table():
    rows = "\n".join(
        f'      <tr><td class="ref"><a href="{u}" rel="noopener">{n}</a></td>'
        f'<td>{j}</td><td>{t}</td><td>{f}</td></tr>'
        for n, j, t, u, f in PATENTS
    )
    return f"""<div class="tablewrap">
  <table>
    <thead><tr><th>Patent number</th><th>Jurisdiction and status</th><th>Title</th><th>Invention family</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
</div>
<p class="note">Every number above links to its Google Patents record, where the inventor list,
assignee, claims and the "Cited by" panel can be read directly. All nine name Somesh Rahul as an
inventor and are assigned to Lutron.</p>"""

# ---------------------------------------------------------------- pages

def build():
    A = star("A_responsibility.txt")
    B = star("B_mentoring.txt")
    C = star("C_invention.txt")
    D = star("D_standing.txt")

    # ---------------- Overview
    stats = """<div class="stats">
  <div class="stat"><b>9</b><span>Granted and published patents across four jurisdictions</span></div>
  <div class="stat"><b>$100M+</b><span>Annual revenue from the platforms led</span></div>
  <div class="stat"><b>200,000+</b><span>Production 3D models on the generative pipeline</span></div>
  <div class="stat"><b>100+</b><span>Graduate students and engineers taught</span></div>
  <div class="stat"><b>25+</b><span>Papers and proposals peer reviewed</span></div>
</div>"""
    cards = """<div class="cards">
  <div class="card">
    <div><span class="tag">Section 3A &middot; Body of work</span>
    <h3>Responsibility</h3>
    <p>A portfolio of five production AI products and the platform underneath them, with the
    engineering standards and the production sign-off, across five partner organisations.</p></div>
    <a class="btn" href="responsibility.html">Open Section 3A</a>
  </div>
  <div class="card">
    <div><span class="tag">Section 3B &middot; Professional impact</span>
    <h3>Mentoring and coaching</h3>
    <p>Building architectural judgment in engineers and product managers at Walmart and Lutron,
    and teaching at Pennsylvania, Lehigh and IEEE outreach.</p></div>
    <a class="btn" href="mentoring.html">Open Section 3B</a>
  </div>
  <div class="card">
    <div><span class="tag">Section 3C &middot; Additional sub-criterion</span>
    <h3>Invention and innovation</h3>
    <p>RSSI proximity commissioning across nine patents, cited by Apple and licensed by Acclivis.
    A multimodal generative 3D engine at catalogue scale, and the Living Services Architecture.</p></div>
    <a class="btn" href="innovation.html">Open Section 3C</a>
  </div>
  <div class="card">
    <div><span class="tag">Section 3D &middot; Standing in the community</span>
    <h3>Awards</h3>
    <p>Distinguished Fellow of the Soft Computing Research Society, four international design
    awards, conference governance and peer review service.</p></div>
    <a class="btn" href="standing.html">Open Section 3D</a>
  </div>
</div>"""

    idx_body = ASSESSOR + "\n" + stats + """
<h2>The four statements</h2>
<p class="note">One page per sub-criterion, each carrying the statement as submitted and the sources behind it.</p>
""" + cards + """
<h2>Everything in one place</h2>
<p>The evidence matrix lists every artefact behind the application in a single table: patents,
independent press coverage, award records, academic adoption, appointments and review service,
each mapped to the section of the form it supports.</p>
<p><a class="btn" href="evidence-matrix.html">Open the evidence matrix</a></p>

<h2>Who I am, briefly</h2>
<p>I build AI systems that ship to customers and I stay accountable for them after they ship.
At Walmart Global Tech I own the architecture strategy, the engineering standards and the production
sign-off for the generative AI, computer vision and augmented reality platforms behind virtual
try-on, visual search and generative 3D. Before that I spent six years at Lutron Electronics
inventing device commissioning and configuration technology that is now cited by Apple, licensed by
Acclivis and running across the connected building industry.</p>
<p>I write and speak from the deployment side rather than the research side. Fifteen years in the
profession, nine granted and published patents across four jurisdictions, and IEEE Senior Member
grade conferred after independent peer assessment.</p>
<ul class="ev">
  <li><a href="https://www.linkedin.com/in/someshrahul" rel="noopener">LinkedIn profile</a><span class="pill live">verify</span></li>
  <li><a href="https://scholar.google.com/citations?hl=en&amp;user=lOHi43kAAAAJ" rel="noopener">Google Scholar profile</a><span class="pill live">verify</span></li>
  <li><a href="https://patents.google.com/?inventor=Somesh+Rahul" rel="noopener">All patents naming Somesh Rahul on Google Patents</a><span class="pill live">verify</span></li>
</ul>
"""
    badges = """<div class="badges">
      <span class="badge">Principal Product Manager, Walmart Global Tech</span>
      <span class="badge">IEEE Senior Member</span>
      <span class="badge">Distinguished Fellow, Soft Computing Research Society</span>
      <span class="badge">9 patents: US, EP, CA, CN</span>
      <span class="badge">Cited by Apple</span>
      <span class="badge">2 Gold MUSE Awards 2026</span>
      <span class="badge">2 iF Design Awards 2024</span>
      <span class="badge">MS HCI, University of Michigan</span>
    </div>"""
    write("index.html", shell("index.html", "Overview",
        hero("BCS Fellowship (FBCS) &middot; Experiential route",
             "Somesh Rahul",
             "Supporting evidence for a Fellowship application under the experiential route. "
             "Four statements, four sub-criteria, and the primary sources behind each one.",
             "Principal Product Manager, Emerging Technology (Generative AI and AR/XR), Walmart Global Tech. "
             "Previously Product and Design Leader, Lutron Electronics.",
             badges, portrait="somesh.jpg"),
        idx_body))

    # ---------------- Responsibility
    resp = ASSESSOR + "\n" + star_html(A, "Responsibility", "Section 3A &middot; Body of work") + """
<h2>Independent press coverage</h2>
<p class="note">The platforms named in the statement were covered by trade and national press at launch.
Only the first is company-issued. WWD sits behind a paywall and XR Today is occasionally unavailable,
so PDFs of both are held and can be sent to BCS directly.</p>
""" + ev_html([
        ev("Walmart corporate: scaling artificial intelligence, generative AI, augmented reality and immersive commerce",
           "https://corporate.walmart.com/news/2024/10/09/walmart-reveals-plan-for-scaling-artificial-intelligence-generative-ai-augmented-reality-and-immersive-commerce-experiences"),
        ev("WWD: Walmart adds virtual try-on tool for makeup",
           "https://wwd.com/beauty-industry-news/beauty-features/walmart-virtual-try-on-tool-1235860064/"),
        ev("AR Insider: Walmart invests big in AR shopping",
           "https://arinsider.co/2024/07/24/walmart-invests-big-in-ar-shopping/"),
        ev("Chain Store Age: Walmart adds a new dimension to virtual beauty try-on",
           "https://chainstoreage.com/walmart-adds-new-dimension-virtual-beauty-try"),
    ]) + """
<h2>The same practice, presented outside Walmart</h2>
<p class="note">Supporting material rather than part of the statement. The operating model behind these
platforms has been presented to three external audiences.</p>
""" + ev_html([
        ev("Keynote, 4th Congress on Smart Computing Technologies (CSCT 2025), NIT Sikkim, December 2025",
           "csct-2025-keynote.pdf", "file",
           "Proceedings published in the Scopus-indexed Springer Smart Innovation, Systems and Technologies series."),
        ev("Invited speaker, 2025 IEEE New Era AI World Leaders Summit. Real-time virtual try-on at retail scale.",
           "ieee-summit-2025.pdf", "file"),
        ev("Speaker, Emerging Technologies Tech Talk, ACM Fremont Chapter, November 2025. Shipping generative AI and AR safely at retail scale.",
           "acm-fremont-2025.pdf", "file"),
    ]) + """
<h2>Product ownership on the record</h2>
<p class="note">Each product named in the statement has an internal initiative plan or product
requirements page authored under my name. Those pages are Walmart-confidential and are not reproduced
here; they can be shown to BCS directly on request.</p>
""" + ev_html([
        ev("Product definition pages authored under my name: Shop the Background (July 2025), View in "
           "Home: Paint MVP (December 2024), AI Audio, and the FY26 initiative plan and OKRs for the "
           "generative 3D asset pipeline.", "", "hold"),
        ev("Launch announcements naming me as product lead for Shop the Background and AI Audio, and "
           "the A/B record showing the scale-up from 14,000 items to over 100,000 live item pages.",
           "", "hold"),
        ev("Acceptance criteria I set for an external 3D asset vendor before their output could be "
           "hosted on the platform.", "", "hold"),
    ]) + """
<h2>Internal recognition</h2>
""" + ev_html([
        ev("Make A Difference Award, Walmart Global Tech. The company's highest internal recognition.",
           "walmart-mada.pdf", "file"),
        ev("Promoted to Principal Product Manager, September 2026.", "", "hold"),
    ]) + """
<p class="note">The revenue and gross merchandise figures in the statement are internal Walmart
measures and are not publicly reportable. They are given as the platforms' contribution, and I am
happy to talk through how they are attributed on an assessor call.</p>
"""
    write("responsibility.html", shell("responsibility.html", "Responsibility",
        hero("Section 3A &middot; Body of work", "Responsibility",
             "A portfolio of five production AI products at Walmart, the platform underneath them, "
             "and the production sign-off on all of it."),
        resp))

    # ---------------- Mentoring
    ment = ASSESSOR + "\n" + star_html(B, "Mentoring and coaching", "Section 3B &middot; Professional impact") + """
<h2>Teaching and academic appointments</h2>
""" + ev_html([
        ev("University of Pennsylvania, Integrated Product Design. Graduate masterclasses, 2020 and 2026: "
           "the AI product orchestrator, and the evolution of product and design roles under AI.",
           "upenn-masterclass.pdf", "file"),
        ev("Lehigh University, 2019. Guest lectures on ambient computing and Zero UI architectures.",
           "lehigh-lecture.pdf", "file"),
        ev("IEEE Techs on Deck and IEEE STEM outreach workshops, 2025. Volunteer instructor.",
           "ieee-stem-outreach.pdf", "file"),
    ]) + """
<h2>Formal authority over other people's work</h2>
<p>The statement leads on formal review rather than informal coaching, because deciding who is hired
and who is promoted is the part an assessor can test. Sanjeev Kumar, then Vice President of Software at
Lutron and my manager, has documented all three of the items below in writing. That letter was written
for a different purpose and is not reproduced here, but it is available to BCS on request.</p>
""" + ev_html([
        ev("Lutron: wrote and signed the annual performance reviews for the design and research team.",
           "", "hold"),
        ev("Lutron: wrote the promotion cases and made the formal recommendations for salary and grade.",
           "mentee-promotions.pdf", "file"),
        ev("Lutron: member of the hiring and interview panel for the Design and Product organisation.",
           "", "hold"),
        ev("Walmart: hiring panellist for product management, user experience and AI roles.",
           "", "hold"),
    ]) + """
<h2>Line management and team leadership</h2>
""" + ev_html([
        ev("Shop the Background launch record: more than thirty-five people credited across eight "
           "functions, with me named as product lead and no reporting line into any of them.",
           "", "hold"),
        ev("Walmart Global Tech: two product managers report in, and the design and research partners "
           "across the immersive platforms are mentored directly.", "", "hold"),
        ev("Lutron Electronics: led the design and research team spanning industrial design, "
           "interaction design and user research.", "", "hold"),
        ev("Three people I coached at Walmart were promoted on my recommendation: Yash Garg, "
           "Abhimanyu Chadha and Daniel Lee. All three are credited on the launch record above and are "
           "available as references.", "walmart-mentoring-record.pdf", "file"),
        ev("More than a hundred graduate students and early-career engineers taught across the "
           "University of Pennsylvania, Lehigh and IEEE outreach.", "", "hold"),
    ])
    write("mentoring.html", shell("mentoring.html", "Mentoring and coaching",
        hero("Section 3B &middot; Professional impact", "Mentoring and coaching",
             "Building the architectural judgment that lets an engineer or product manager own a "
             "production AI system end to end."),
        ment))

    # ---------------- Innovation
    inno = ASSESSOR + "\n" + star_html(C, "Invention and innovation", "Section 3C &middot; Additional sub-criterion") + """
<h2>Patent portfolio</h2>
<p>Nine granted and published patents across the United States, Europe, Canada and China, in three
invention families. Each row opens the public record.</p>
""" + patent_table() + """
<h2>Adoption outside the originating company</h2>
<p>This is the part of the section that matters most for Fellowship, because it is the evidence that
the invention outlived the employer that paid for it.</p>
""" + ev_html([
        ev("Independent citation by Apple. Visible in the “Cited by” panel of the commissioning patents.",
           "https://patents.google.com/patent/US11438225B2/en"),
        ev("Built on across approximately 10 to 12 PassiveLogic patents.",
           "https://patents.google.com/?q=passivelogic&amp;oq=passivelogic"),
        ev("PassiveLogic company record, as captured", "passivelogic-adoption.pdf", "file"),
        ev("Licensed by Acclivis Technologies into an adjacent commercial vertical.",
           "acclivis-licence.pdf", "file"),
        ev("Adopted by Innovative Technology Solutions (ITS).", "its-adoption.pdf", "file"),
        ev("Platform integration with Samsung SmartThings.", "smartthings-integration.pdf", "file"),
        ev("Related: QuEstD, an AI-assisted configuration and estimation tool invented at Lutron and "
           "adopted by more than 35 firms outside it. Trade coverage in Electrical Contractor Magazine, "
           "ElectricSmarts Network and Interior Design.", "questd-coverage.pdf", "file"),
    ]) + """
<h2>Academic adoption of the Living Services Architecture</h2>
<p><i>The Anticipatory Home: A Blueprint for AI, Spatial Computing, and Ambient Commerce</i>
introduces the Living Services Architecture and the Anticipatory Readiness Index. An independent
academic read the frameworks and put them in front of graduate students, which is a different kind
of evidence than an employer liking the work.</p>
""" + ev_html([
        ev("Letter of evaluation and curriculum adoption, Prof. Vaibhav Unhelkar, Assistant Professor "
           "of Computer Science, Rice University. Adopted for graduate teaching in human-centred AI, "
           "interactive machine learning and autonomous agents.", "rice-unhelkar-letter.pdf", "file"),
        ev("Prof. Vaibhav Unhelkar, Rice University faculty page",
           "https://profiles.rice.edu/faculty/vaibhav-unhelkar"),
        ev("The Anticipatory Home, publisher listing", "anticipatory-home-book.pdf", "file"),
    ]) + """
<h2>The generative 3D pipeline</h2>
""" + ev_html([
        ev("Walmart corporate: scaling artificial intelligence, generative AI and augmented reality",
           "https://corporate.walmart.com/news/2024/10/09/walmart-reveals-plan-for-scaling-artificial-intelligence-generative-ai-augmented-reality-and-immersive-commerce-experiences"),
        ev("AR Insider: Walmart invests big in AR shopping",
           "https://arinsider.co/2024/07/24/walmart-invests-big-in-ar-shopping/"),
    ])
    write("innovation.html", shell("innovation.html", "Invention and innovation",
        hero("Section 3C &middot; Additional sub-criterion", "Invention and innovation",
             "Removing the expensive human step in three different industries, and the evidence that "
             "the inventions were taken up by people who do not work for me."),
        inno))

    # ---------------- Standing
    stand = ASSESSOR + "\n" + star_html(D, "Awards", "Section 3D &middot; Standing in the community") + """
<h2>Peer-assessed elevations</h2>
<p class="note">BCS guidance treats fellowship of another institution or a senior peer-assessed grade
as the strongest form of this sub-criterion, so these come first.</p>
""" + ev_html([
        ev("SCRS Fellow certificate, no. SCRS/Fellow/1395, issued 22 October 2025.",
           "scrs-fellow.pdf", "file"),
        ev("SCRS Distinguished Fellow, elevated from Fellow on the society's own review.",
           "scrs-distinguished-fellow.pdf", "file"),
        ev("Expert statement from Dr Jagdish Chand Bansal, Chair of the SCRS Fellow Membership Steering "
           "Committee, setting out the review and selection process.", "scrs-fellow.pdf", "file"),
        ev("Soft Computing Research Society", "https://www.scrs.in/"),
        ev("Member, Association for Computing Machinery.", "acm-membership.pdf", "file"),
    ]) + """
<h2>International awards</h2>
""" + ev_html([
        ev("MUSE Design Awards 2026, two Gold awards: Walmart Shop the Background and Walmart Dynamic "
           "Showroom, UX/UI and interaction design categories. Searchable in the MUSE winners gallery "
           "by year and category.",
           "https://design.museaward.com/winner.php"),
        ev("MUSE Design Awards 2026: both Gold certificates, issued in my name for Walmart Shop the "
           "Background and Walmart Dynamic Showroom", "muse-2026-certificates.pdf", "file"),
        ev("iF Design Award 2024: Walmart View in your home. Official iF winner page.",
           "https://ifdesign.com/en/winner-ranking/project/walmart-view-in-your-home/638773"),
        ev("iF Design Award 2024: Walmart Beauty Virtual Try-on. Official iF winner page.",
           "https://ifdesign.com/en/winner-ranking/project/walmart-beauty-virtual-try-on/640012"),
        ev("iF Design Award 2024, both winner records as captured", "if-2024-award.pdf", "file"),
        ev("IC BAM Under 40 Award 2026, Indian Brand Convention.", "icbam-under40.pdf", "file"),
        ev("Most Innovative AI Presentation, runner-up, 2025 IEEE New Era AI World Leaders Summit.",
           "ieee-summit-2025.pdf", "file"),
        ev("Make A Difference Award, Walmart Global Tech.", "walmart-mada.pdf", "file"),
        ev("GLF Innovation Award for myRoom VUE, Lutron Electronics.", "lutron-glf.pdf", "file"),
    ]) + """
<h2>Office, governance and keynotes</h2>
""" + ev_html([
        ev("Member, Industry Advisory Committee, IEEE World Conference on Computational Science and "
           "Technology (WCCST 2026). Appointed November 2025.", "wccst-appointment.pdf", "file"),
        ev("Member, Advisory Board, Customer Experience Programme, University of North Dakota. "
           "Invitation only.", "und-advisory.pdf", "file"),
        ev("Keynote, 4th Congress on Smart Computing Technologies (CSCT 2025), NIT Sikkim.",
           "csct-2025-keynote.pdf", "file"),
        ev("Treasurer, IEEE Computational Intelligence Society, Dallas Section Chapter (CH05266). "
           "Recorded in the IEEE vTools officer register.", "ieee-cis-treasurer.pdf", "file"),
        ev("World IA Day 2014, Ann Arbor. Named on the planning committee for the University of "
           "Michigan event.", "https://worldiaday.org/events/ann-arbor/2014"),
        ev("Reviewer, Elsevier Data in Brief. Certificate on record.", "elsevier-dib.pdf", "file"),
        ev("Reviewer, Elsevier MethodsX. Recognised Reviewer certificate on record.",
           "elsevier-methodsx.pdf", "file"),
        ev("Reviewer, IEEE WCCST 2026 and IEEE ICPC2T 2026 (NIT Raipur).", "ieee-reviews.pdf", "file"),
        ev("Book proposal reviewer, CRC Press (Taylor and Francis), for <i>Intelligent Commerce</i>.",
           "crc-press-review.pdf", "file"),
        ev("Session Chair and presentation evaluation panel, INCSTIC 2025.", "incstic-chair.pdf", "file"),
        ev("Google Scholar profile",
           "https://scholar.google.com/citations?hl=en&amp;user=lOHi43kAAAAJ"),
        ev("Google Scholar record, as captured", "google-scholar.pdf", "file"),
    ])
    write("standing.html", shell("standing.html", "Standing in the community",
        hero("Section 3D &middot; Standing in the community", "Awards",
             "Peer-assessed elevation, international awards, and what the standing has been used for "
             "on behalf of other people."),
        stand))

    # ---------------- Evidence matrix
    matrix_rows = [
        ("EV-01", "Patent", "US 11,438,225 B2, commissioning and controlling load control devices", "USPTO", "3C",
         "https://patents.google.com/patent/US11438225B2/en"),
        ("EV-02", "Patent", "US 12,166,627 B2, commissioning and controlling load control devices", "USPTO", "3C",
         "https://patents.google.com/patent/US12166627B2/en"),
        ("EV-03", "Patent", "EP 3,935,791 B1, commissioning and controlling load control devices", "EPO", "3C",
         "https://patents.google.com/patent/EP3935791B1/en"),
        ("EV-04", "Patent", "CA 3,115,114 C, load control system configuration tool", "CIPO", "3C",
         "https://patents.google.com/patent/CA3115114C/en"),
        ("EV-05", "Patent", "CN 113,170,565 B, load control system and computing device", "CNIPA", "3C",
         "https://patents.google.com/patent/CN113170565B/en"),
        ("EV-06", "Patent", "CN 114,761,659 B, control of covering materials and electric window treatments", "CNIPA", "3C",
         "https://patents.google.com/patent/CN114761659B/en"),
        ("EV-07", "Patent", "USD 940,160 S1, animated graphical user interface for building control", "USPTO", "3C",
         "https://patents.google.com/patent/USD940160S1/en"),
        ("EV-08", "Patent", "USD 993,972 S1, graphical user interface for building control", "USPTO", "3C",
         "https://patents.google.com/patent/USD993972S1/en"),
        ("EV-09", "Patent", "USD 1,070,883 S1, graphical user interface for building control", "USPTO", "3C",
         "https://patents.google.com/patent/USD1070883S1/en"),
        ("EV-10", "Citation", "Apple citation and PassiveLogic build-on, visible in the Cited by panel", "Google Patents", "3C",
         "https://patents.google.com/patent/US11438225B2/en"),
        ("EV-11", "Press", "Walmart corporate: scaling AI, generative AI and augmented reality", "Walmart Inc.", "3A, 3C",
         "https://corporate.walmart.com/news/2024/10/09/walmart-reveals-plan-for-scaling-artificial-intelligence-generative-ai-augmented-reality-and-immersive-commerce-experiences"),
        ("EV-12", "Press", "Walmart adds virtual try-on tool for makeup", "WWD", "3A",
         "https://wwd.com/beauty-industry-news/beauty-features/walmart-virtual-try-on-tool-1235860064/"),
        ("EV-13", "Press", "Walmart invests big in AR shopping", "AR Insider", "3A, 3C",
         "https://arinsider.co/2024/07/24/walmart-invests-big-in-ar-shopping/"),
        ("EV-14", "Press", "Walmart adds a new dimension to virtual beauty try-on", "Chain Store Age", "3A",
         "https://chainstoreage.com/walmart-adds-new-dimension-virtual-beauty-try"),
        ("EV-15", "Scholarly", "Google Scholar profile and citation record", "Google Scholar", "3C, 3D",
         "https://scholar.google.com/citations?hl=en&amp;user=lOHi43kAAAAJ"),
        ("EV-16", "Academic", "Rice University faculty record, Prof. Vaibhav Unhelkar", "Rice University", "3C",
         "https://profiles.rice.edu/faculty/vaibhav-unhelkar"),
        ("EV-17", "Award", "MUSE Design Awards winners gallery, searchable by year and category", "MUSE Design Awards", "3D",
         "https://design.museaward.com/winner.php"),
        ("EV-18", "Award", "iF Design Award 2024: Walmart View in your home", "iF International Forum Design", "3D",
         "https://ifdesign.com/en/winner-ranking/project/walmart-view-in-your-home/638773"),
        ("EV-18b", "Award", "iF Design Award 2024: Walmart Beauty Virtual Try-on", "iF International Forum Design", "3D",
         "https://ifdesign.com/en/winner-ranking/project/walmart-beauty-virtual-try-on/640012"),
        ("EV-19", "Profile", "Professional record and appointments", "LinkedIn", "All",
         "https://www.linkedin.com/in/someshrahul"),
        ("EV-19b", "Community service", "World IA Day 2014 Ann Arbor, named on the planning committee",
         "World IA Day / IA Institute", "3D",
         "https://worldiaday.org/events/ann-arbor/2014"),
    ]
    held = [
        ("EV-19c", "Society office", "IEEE vTools officer register showing Chapter Treasurer, Dallas Section Chapter CIS11", "IEEE", "3D", "ieee-cis-treasurer.pdf"),
        ("EV-20", "Academic adoption", "Letter of evaluation and curriculum adoption, Prof. Vaibhav Unhelkar", "Rice University", "3C", "rice-unhelkar-letter.pdf"),
        ("EV-21", "Fellowship", "SCRS Fellow certificate no. SCRS/Fellow/1395, 22 Oct 2025, plus the Steering Committee chair's statement of the selection process", "SCRS", "3D", "scrs-fellow.pdf"),
        ("EV-22", "Fellowship", "SCRS Distinguished Fellow, conferred August 2026", "SCRS", "3D", "scrs-distinguished-fellow.pdf"),
        ("EV-22b", "Elevation", "IEEE Senior Member grade certificate", "IEEE", "3B", "ieee-senior-member.pdf"),
        ("EV-23", "Award", "MUSE Design Awards 2026, both Gold certificates issued in the applicant's name", "MUSE Design Awards", "3D", "muse-2026-certificates.pdf"),
        ("EV-24", "Award", "iF Design Award 2024, entry and award proof", "iF Design", "3D", "if-2024-award.pdf"),
        ("EV-25", "Award", "IC BAM Under 40 Award 2026 certificate", "Indian Brand Convention", "3D", "icbam-under40.pdf"),
        ("EV-26", "Award", "Most Innovative AI Presentation, runner-up", "IEEE New Era AI Summit", "3A, 3D", "ieee-summit-2025.pdf"),
        ("EV-27", "Award", "Make A Difference Award and top 1% rating", "Walmart Global Tech", "3A, 3D", "walmart-mada.pdf"),
        ("EV-28", "Award", "GLF Innovation Award for myRoom VUE", "Lutron Electronics", "3D", "lutron-glf.pdf"),
        ("EV-29", "Appointment", "Industry Advisory Committee appointment", "IEEE WCCST 2026", "3D", "wccst-appointment.pdf"),
        ("EV-30", "Appointment", "Advisory Board, Customer Experience Programme", "University of North Dakota", "3D", "und-advisory.pdf"),
        ("EV-31", "Keynote", "Keynote invitation and programme", "CSCT 2025, NIT Sikkim", "3A, 3D", "csct-2025-keynote.pdf"),
        ("EV-32", "Review service", "Reviewer certificate", "Elsevier Data in Brief", "3D", "elsevier-dib.pdf"),
        ("EV-33", "Review service", "Recognised Reviewer certificate", "Elsevier MethodsX", "3D", "elsevier-methodsx.pdf"),
        ("EV-34", "Review service", "Completed review records", "IEEE WCCST 2026, IEEE ICPC2T 2026", "3D", "ieee-reviews.pdf"),
        ("EV-35", "Review service", "Book proposal review, Intelligent Commerce", "CRC Press", "3D", "crc-press-review.pdf"),
        ("EV-36", "Teaching", "Masterclass materials, Integrated Product Design", "University of Pennsylvania", "3B", "upenn-masterclass.pdf"),
        ("EV-37", "Teaching", "Guest lecture record, ambient computing and Zero UI", "Lehigh University", "3B", "lehigh-lecture.pdf"),
        ("EV-38", "Licensing", "Licence and integration record", "Acclivis Technologies", "3C", "acclivis-licence.pdf"),
        ("EV-39", "Trade press", "QuEstD coverage", "Electrical Contractor Magazine and others", "3C", "questd-coverage.pdf"),
        ("EV-40", "Adoption", "PassiveLogic company record, as captured", "PassiveLogic", "3C", "passivelogic-adoption.pdf"),
        ("EV-41", "Scholarly", "Google Scholar record, as captured", "Google Scholar", "3C, 3D", "google-scholar.pdf"),
        ("EV-42", "Publication", "The Anticipatory Home, publisher listing", "AGPH Books", "3C", "anticipatory-home-book.pdf"),
    ]

    rows = []
    for r, cat, desc, body, sec, url in matrix_rows:
        rows.append(f'      <tr><td class="ref">{r}</td><td>{cat}</td>'
                    f'<td><a href="{url}" rel="noopener">{desc}</a></td><td>{body}</td><td class="ref">{sec}</td></tr>')
    for r, cat, desc, body, sec, fn in held:
        exists = os.path.isfile(os.path.join(EVDIR, fn))
        cell = f'<a href="evidence/{fn}">{desc}</a>' if exists else f'{desc} <span class="pill hold">on file</span>'
        rows.append(f'      <tr><td class="ref">{r}</td><td>{cat}</td><td>{cell}</td><td>{body}</td><td class="ref">{sec}</td></tr>')

    matrix = ASSESSOR + """
<h2>Complete evidence inventory</h2>
<p>Everything behind the four statements, mapped to the section of the form it supports. Rows with a
link open a public record directly. Rows marked <span class="pill hold">on file</span> are original
certificates, letters and appointment records held by the applicant and supplied to BCS on request.</p>
<div class="tablewrap">
  <table>
    <thead><tr><th>Ref</th><th>Category</th><th>Artefact</th><th>Issuing body</th><th>Section</th></tr></thead>
    <tbody>
""" + "\n".join(rows) + """
    </tbody>
  </table>
</div>
<p class="note">Nothing on this site requires a login. If a link fails, please email """ + CONTACT + """
and I will send the document directly.</p>
"""
    write("evidence-matrix.html", shell("evidence-matrix.html", "Evidence matrix",
        hero("Verification index", "Master evidence matrix",
             "Every artefact behind the application, mapped to the section of the form it supports."),
        matrix))

def write(name, content):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name, f"({len(content):,} bytes)")

if __name__ == "__main__":
    os.makedirs(EVDIR, exist_ok=True)
    build()
    have = sorted(x for x in os.listdir(EVDIR) if not x.startswith("."))
    print(f"\nevidence/ contains {len(have)} file(s).")
    if have:
        print("  " + "\n  ".join(have))
    print("Any evidence item without its PDF renders as 'on file' text, never a broken link.")
