#!/usr/bin/env python3
"""Ethics Week 4 Quiz Prep PDF — Generative AI, Consent and Power"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, ListFlowable, ListItem
)

OUTPUT = '/home/ubuntu/clawd/output/ethics-week4-quiz-prep.pdf'

NAVY = colors.HexColor('#1e3a5f')
ACCENT = colors.HexColor('#e94560')
TEAL = colors.HexColor('#0f969c')
GOLD = colors.HexColor('#f5a623')
LIGHT = colors.HexColor('#f8f9fa')
DARK = colors.HexColor('#1a1a2e')

doc = SimpleDocTemplate(OUTPUT, pagesize=A4, topMargin=0.6*inch, bottomMargin=0.5*inch,
                        leftMargin=0.65*inch, rightMargin=0.65*inch)
styles = getSampleStyleSheet()

s_title = ParagraphStyle('T', parent=styles['Title'], fontSize=24, textColor=NAVY, spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
s_subtitle = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=11, textColor=colors.gray, spaceAfter=16, alignment=TA_CENTER)
s_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, textColor=NAVY, spaceBefore=18, spaceAfter=8, fontName='Helvetica-Bold')
s_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, textColor=ACCENT, spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
s_h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=11, textColor=TEAL, spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold')
s_body = ParagraphStyle('B', parent=styles['Normal'], fontSize=10.5, leading=15, spaceAfter=5, textColor=colors.HexColor('#333'))
s_bullet = ParagraphStyle('Bul', parent=styles['Normal'], fontSize=10.5, leading=15, spaceAfter=3, textColor=colors.HexColor('#333'), leftIndent=20, bulletIndent=8)
s_key = ParagraphStyle('Key', parent=styles['Normal'], fontSize=10.5, leading=15, spaceAfter=3, textColor=NAVY, fontName='Helvetica-Bold', leftIndent=20, bulletIndent=8)
s_quote = ParagraphStyle('Q', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555'), leftIndent=25, rightIndent=25, spaceBefore=6, spaceAfter=6, leading=14, fontName='Helvetica-Oblique')
s_box_title = ParagraphStyle('BT', parent=styles['Normal'], fontSize=11, textColor='white', fontName='Helvetica-Bold')
s_box_body = ParagraphStyle('BB', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#333'), spaceAfter=2)
s_stat = ParagraphStyle('Stat', parent=styles['Normal'], fontSize=18, textColor=ACCENT, fontName='Helvetica-Bold', alignment=TA_CENTER)
s_stat_label = ParagraphStyle('SL', parent=styles['Normal'], fontSize=8.5, textColor=colors.gray, alignment=TA_CENTER)
s_footer = ParagraphStyle('F', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)

def make_box(title, items, color=NAVY):
    """Create a coloured box with title and bullet items."""
    content = []
    # Title bar
    title_table = Table([[Paragraph(title, s_box_title)]], colWidths=[460])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]))
    content.append(title_table)
    
    # Body
    body_items = []
    for item in items:
        body_items.append(Paragraph(f'• {item}', s_box_body))
    
    body_table = Table([[body_items]], colWidths=[460])
    body_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ]))
    content.append(body_table)
    content.append(Spacer(1, 8))
    return content

story = []

# ── TITLE PAGE ──────────────────────────────────────
story.append(Spacer(1, 40))
story.append(Paragraph('Ethics Week 4 — Quiz Prep', s_title))
story.append(Paragraph('Generative AI, Consent and Power', s_subtitle))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=2))
story.append(Spacer(1, 10))
story.append(Paragraph('Dr Tina L. Peterson · ECS7025P · 20 February 2026', s_subtitle))
story.append(Spacer(1, 20))

# Key stats row
stats = [
    [Paragraph('51%', s_stat), Paragraph('59%', s_stat), Paragraph('85%', s_stat), Paragraph('1,000+', s_stat)],
    [Paragraph('of novelists think AI\nwill replace them', s_stat_label), 
     Paragraph('know work used to\ntrain LLMs without consent', s_stat_label),
     Paragraph('expect future income\ndriven down by AI', s_stat_label),
     Paragraph('musicians protesting\nUK copyright changes', s_stat_label)]
]
stats_table = Table(stats, colWidths=[115, 115, 115, 115])
stats_table.setStyle(TableStyle([
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,0), 10),
    ('BOTTOMPADDING', (0,1), (-1,1), 10),
    ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#eee')),
    ('LINEBELOW', (0,1), (-1,1), 1, colors.HexColor('#eee')),
]))
story.append(stats_table)
story.append(Spacer(1, 20))

story.append(Paragraph('This document covers everything from the lecture and all three assigned readings. Designed for quiz prep — key concepts, definitions, stats, and likely quiz questions.', s_body))

story.append(PageBreak())

# ── SECTION 1: CORE CONCEPTS ───────────────────────
story.append(Paragraph('1. Core Concepts from the Lecture', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 8))

story.append(Paragraph('Consent (in the context of Gen AI)', s_h2))
story.append(Paragraph('Consent means <b>voluntary, informed agreement</b> to a specific use of your work or likeness. In the context of generative AI, consent is often <b>conditional or forced</b> — creators must post work online to sell it, but they did not consent to having it scraped for AI training data.', s_body))

story.extend(make_box('🔑 Key Definition — Consent in AI Context', [
    '<b>True consent</b> = voluntary, informed, specific, revocable',
    '<b>Conditional consent</b> = "I consent to sharing my art online, NOT to AI scraping it"',
    '<b>Forced consent</b> = creators MUST be online to earn a living → no real choice about scraping',
    'Posting online ≠ consenting to AI training. Consent is conditional and context-specific.',
]))

story.append(Paragraph('Power & Abstracted Power', s_h2))
story.append(Paragraph('<b>Power</b> (related to Gen AI) = <b>control over the terms of another person\'s consent</b>.', s_body))
story.append(Paragraph('AI companies control the terms — they scrape first, ask later (if at all). Individual creators have almost no power to prevent it.', s_body))

story.extend(make_box('🔑 Key Definition — Abstracted Power', [
    '"A human actor\'s influence or control over a system, process, or dataset which, as a function of the technology that enables it, <b>obscures or distances the human actor from consequences</b> of that influence or control."',
    '— Peterson, Ferreira & Vardi (2023), IEEE Transactions on Technology and Society',
    'Technology creates <b>psychological distance</b> between action and consequence',
    'Makes people <b>feel less responsible</b> for harm they cause',
], color=ACCENT))

story.append(Paragraph('How Technology Changes Our Sense of Responsibility', s_h2))
story.append(Paragraph('The lecture compared different interaction modes to show how technology creates distance:', s_body))

tech_data = [
    ['Interaction', 'Distance', 'Sense of Responsibility'],
    ['Face-to-face conversation', 'None', 'Highest'],
    ['Texting someone', 'Low', 'High'],
    ['Playing a board game together', 'None', 'High'],
    ['Gaming space interaction', 'Medium', 'Medium'],
    ['Social media comment', 'High', 'Lower'],
    ['Scraping someone\'s data via API', 'Very High', 'Lowest'],
]
tech_table = Table(tech_data, colWidths=[200, 100, 140])
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(tech_table)
story.append(Spacer(1, 8))

story.append(Paragraph('The Trolley Problem "With a Twist"', s_h3))
story.append(Paragraph('The lecture used a modified trolley problem to illustrate abstracted power — when the mechanism between your action and its consequence becomes more complex/technological, people feel less responsible even though the outcome is identical.', s_body))

story.extend(make_box('🔑 Key Lecture Analogies — Physical vs Digital', [
    'Taking a painting from an artist\'s shop → <b>clearly theft</b>',
    'Scraping digital images from their website → <b>same thing, but feels different</b>',
    'Taking a musician\'s CD without paying → <b>clearly theft</b>',
    'Downloading tracks to remix and sell → <b>same thing, technology creates distance</b>',
    'Taking photos from someone\'s home → <b>clearly a violation</b>',
    'Scraping profile photos from social media → <b>same violation, normalised by technology</b>',
], color=TEAL))

story.append(Spacer(1, 6))
story.extend(make_box('💡 The Lecture\'s Core Rule', [
    '"<b>If you wouldn\'t do it in person, you shouldn\'t do it using technology.</b>"',
    'Technology can give us power over others while making us feel less responsible for how we impact them.',
]))

story.append(Paragraph('Non-Consensual Sexual Deepfakes', s_h2))
story.append(Paragraph('The lecture identified this as <b>"one of the most serious abuses of abstracted power and generative AI"</b>:', s_body))
story.append(Paragraph('• Creates realistic, believable images/videos of real people', s_bullet))
story.append(Paragraph('• Can <b>haunt and re-traumatise</b> victims forever', s_bullet))
story.append(Paragraph('• Law enforcement increasingly calling it <b>"virtual rape"</b>', s_bullet))
story.append(Paragraph('• A clear example of abstracted power: technology distances the perpetrator from the harm', s_bullet))

story.append(PageBreak())

# ── SECTION 2: ARTICLE 1 ──────────────────────────
story.append(Paragraph('2. Article 1: Silent Album Protest (BBC)', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 8))
story.append(Paragraph('<i>"Artists release silent album in protest against AI using their work"</i> — BBC News', s_quote))

story.extend(make_box('📰 Key Facts You Must Know', [
    '<b>1,000+ musicians</b> including Annie Lennox, Kate Bush, Damon Albarn, Hans Zimmer, Imogen Heap released a <b>silent album</b>',
    'Album title: <b>"Is This What We Want?"</b> — tracklisting spells out: "The British government must not legalise music theft to benefit AI companies"',
    'Features recordings of <b>empty studios and performance spaces</b> — what they fear the future looks like',
    'Profits donated to <b>Help Musicians</b> charity',
    'Part of the <b>"Make It Fair"</b> campaign with wrap-around newspaper adverts',
]))

story.append(Paragraph('What\'s the Policy Issue?', s_h2))
story.append(Paragraph('The UK government proposed changes to copyright law:', s_body))
story.append(Paragraph('• AI developers would be able to use <b>any content available online</b> for text/data mining', s_bullet))
story.append(Paragraph('• Artists would have a <b>"rights reservation"</b> — the ability to opt out', s_bullet))
story.append(Paragraph('• Critics say opt-out is <b>impractical</b>: impossible for one artist to notify thousands of AI companies', s_bullet))
story.append(Paragraph('• Cannot monitor what happened to their work across the entire internet', s_bullet))
story.append(Paragraph('• UK music contributed <b>£7.6 billion</b> to the economy in 2023', s_bullet))

story.extend(make_box('🔗 Connection to Lecture Concepts', [
    '<b>Consent:</b> Artists consent to sharing music online, NOT to AI scraping — conditional consent violated',
    '<b>Abstracted power:</b> AI companies scrape at scale, individual artists powerless to prevent it',
    '<b>Opt-out vs opt-in:</b> Government proposes opt-out (burden on artists) instead of opt-in (burden on AI companies) — who holds the power?',
    '<b>Paul McCartney quote:</b> Could make it "impossible for musicians and artists to make a living"',
], color=TEAL))

story.append(PageBreak())

# ── SECTION 3: ARTICLE 2 ──────────────────────────
story.append(Paragraph('3. Article 2: UK Novelists & AI (Cambridge)', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 8))
story.append(Paragraph('<i>"Half of UK novelists believe AI is likely to replace their work entirely"</i> — University of Cambridge', s_quote))

story.append(Paragraph('Key Statistics (likely quiz material)', s_h2))

stat_data = [
    ['Statistic', 'Value', 'What It Means'],
    ['Novelists who think AI will replace them', '51%', 'Majority believe full displacement is likely'],
    ['Know work used to train LLMs without consent', '59%', 'Most are aware of unauthorised scraping'],
    ['Income already hit by AI', '39%', 'Over a third already affected financially'],
    ['Expect future income driven down', '85%', 'Near-universal pessimism about earnings'],
    ['Use AI in their writing process', '33%', 'A third use it (mainly non-creative tasks)'],
    ['Agree AI offers benefits to society', '80%', 'NOT anti-AI — nuanced view'],
    ['Romance authors "extremely threatened"', '66%', 'Genre fiction most vulnerable'],
    ['Thriller authors "extremely threatened"', '61%', 'Formulaic genres easier to replicate'],
    ['Crime authors "extremely threatened"', '60%', 'Pattern-based genres at highest risk'],
]
stat_table = Table(stat_data, colWidths=[190, 55, 195])
stat_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(stat_table)
story.append(Spacer(1, 8))

story.extend(make_box('🔗 Connection to Lecture Concepts', [
    '<b>Consent:</b> 59% know their work was scraped without consent — "the brutal irony is GenAI tools affecting novelists are likely trained on millions of pirated novels"',
    '<b>Power asymmetry:</b> Individual authors vs billion-dollar tech companies — no meaningful ability to prevent scraping',
    '<b>Conditional consent:</b> Authors publish books to be READ, not to train AI. Context matters.',
    '<b>Key nuance:</b> 80% agree AI has societal benefits — they\'re not anti-technology, they\'re anti-exploitation',
    '<b>What they want:</b> Informed consent, fair remuneration, transparency from tech companies',
    '<b>UK publishing exports more books than any other country</b> — £11bn annual contribution',
], color=TEAL))

story.append(Paragraph('AI Tools Mentioned in the Article', s_h3))
story.append(Paragraph('• <b>Sudowrite, Novelcrafter</b> — brainstorm and edit novels', s_bullet))
story.append(Paragraph('• <b>Qyx AI Book Creator, Squibler</b> — draft full-length books', s_bullet))
story.append(Paragraph('• <b>Spines</b> — AI-assisted publishing (cover design to distribution)', s_bullet))

story.append(PageBreak())

# ── SECTION 4: ARTICLE 3 ──────────────────────────
story.append(Paragraph('4. Article 3: Non-Consensual Deepfakes (Digital Watch)', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 8))
story.append(Paragraph('<i>"Non-consensual deepfakes, consent, and power in synthetic media"</i> — Digital Watch Observatory', s_quote))

story.extend(make_box('📰 Key Concepts', [
    '<b>AI pornography</b> = using generative AI to create/manipulate sexual content of real people without consent',
    '<b>Nudify apps</b> = tools that digitally remove clothing from photos of real people',
    '<b>Deepfake pornography</b> = realistic fake sexual videos/images using someone\'s likeness',
    'What was once niche has become a <b>global policy concern</b>',
    'Consent reduced to a <b>"technical obstacle"</b> rather than treated as a social principle',
]))

story.append(Paragraph('Why This Is Different from Traditional Pornography', s_h2))
story.append(Paragraph('• Traditional pornography: involves <b>real performers, production, contracts</b> (even where exploitation exists)', s_bullet))
story.append(Paragraph('• AI-generated: <b>simulates</b> acts using algorithmic inference — the subject may <b>never have participated</b>', s_bullet))
story.append(Paragraph('• Faces, bodies, voices can be <b>reconstructed at scale</b> without knowledge or consent', s_bullet))
story.append(Paragraph('• Results can be <b>indistinguishable from real photos</b>', s_bullet))
story.append(Paragraph('• Once created, content can be <b>replicated endlessly</b> across jurisdictions', s_bullet))

story.append(Paragraph('Who Is Most Affected?', s_h2))
story.append(Paragraph('• <b>Women and girls</b> are disproportionately targeted', s_bullet))
story.append(Paragraph('• Public figures, journalists, politicians, and private individuals all targeted', s_bullet))
story.append(Paragraph('• Used to <b>humiliate, intimidate, or silence</b> victims', s_bullet))
story.append(Paragraph('• <b>Children</b> face extreme risk — AI can generate sexualised images of minors', s_bullet))
story.append(Paragraph('• Even without physical abuse, may constitute <b>child sexual abuse material</b> legally', s_bullet))

story.append(Paragraph('The Grok Controversy', s_h3))
story.append(Paragraph('Elon Musk\'s Grok AI was reported to generate/modify sexualised images of women and children. Despite claimed safeguards, repeated abusive outputs suggest <b>systemic design failures, not isolated misuse</b>.', s_body))

story.append(Paragraph('Legal Responses', s_h2))
story.append(Paragraph('• <b>US Take It Down Act</b> — recognises non-consensual synthetic sexual content as a distinct category of abuse', s_bullet))
story.append(Paragraph('• Law enforcement increasingly calls it <b>"virtual rape"</b> (also mentioned in lecture)', s_bullet))
story.append(Paragraph('• Legal systems struggle: built around <b>physical acts</b>, not synthetic representation', s_bullet))
story.append(Paragraph('• Harm arises through <b>exposure, distribution, psychological impact</b> — not just physical contact', s_bullet))

story.extend(make_box('🔗 Connection to Lecture Concepts', [
    '<b>Abstracted power at its worst:</b> Perpetrator is completely distanced from victim — clicks a button, ruins a life',
    '<b>Consent obliterated:</b> Subject never participated in ANY sexual act yet content looks authentic',
    '<b>Technology as force multiplier:</b> One person can victimise thousands using AI tools',
    '<b>The lecture\'s test:</b> "If you wouldn\'t do it in person, don\'t do it with technology" — nobody would do this face-to-face',
], color=ACCENT))

story.append(PageBreak())

# ── SECTION 5: LIKELY QUIZ QUESTIONS ───────────────
story.append(Paragraph('5. Likely Quiz Questions & How to Answer', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 8))

story.append(Paragraph('Based on lecture structure and reading themes, expect questions like:', s_body))

qa_data = [
    ['Likely Question', 'Key Points for Your Answer'],
    ['Define consent in the context of generative AI', 'Voluntary, informed agreement to specific use. Posting online ≠ consent to AI scraping. Consent is conditional and context-specific.'],
    ['What is abstracted power?', 'Peterson et al. (2023): influence/control over a system that obscures/distances the actor from consequences. Technology creates psychological distance.'],
    ['How does technology change our sense of responsibility?', 'More technological distance = less felt responsibility. Face-to-face (high) → API scraping (lowest). The trolley problem with a twist.'],
    ['What is the "opt-out" debate?', 'UK gov proposes creators opt-out of AI scraping. Critics: impractical for individuals vs thousands of AI companies. Shifts burden to creators, not AI firms.'],
    ['Why did musicians release a silent album?', '1,000+ artists protesting UK copyright changes. Album "Is This What We Want?" with empty studio recordings. Make It Fair campaign.'],
    ['What did the Cambridge study on novelists find?', '51% think AI will replace them. 59% know work scraped without consent. 85% expect income decline. But 80% agree AI has societal benefits.'],
    ['Which genres are most threatened by AI?', 'Romance (66%), thrillers (61%), crime (60%) — formulaic, pattern-based genres are easier for AI to replicate.'],
    ['What are non-consensual deepfakes?', 'AI-generated sexual content using real people\'s likeness without consent. Nudify apps, deepfake porn. Women/girls disproportionately targeted. Called "virtual rape."'],
    ['How is AI pornography different from traditional?', 'No real performers needed. Subject may never have participated. Content indistinguishable from real. Endlessly replicable. Consent is irrelevant to creation.'],
    ['What was the Grok controversy?', 'Musk\'s AI generated sexualised images of women/children. Systemic design failure, not isolated misuse. Triggered regulatory backlash.'],
    ['Give an example of the lecture\'s analogy about theft', 'Taking a painting from a shop = clearly theft. Scraping digital art from a website = same violation, but technology makes it feel different (abstracted power).'],
    ['What legal responses exist to deepfakes?', 'US Take It Down Act. "Virtual rape" classification. Challenge: legal systems built around physical acts struggle with synthetic harm.'],
]

qa_table = Table(qa_data, colWidths=[175, 275])
qa_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), ACCENT),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
story.append(qa_table)

story.append(PageBreak())

# ── SECTION 6: CHEAT SHEET ────────────────────────
story.append(Paragraph('6. One-Page Cheat Sheet', s_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
story.append(Spacer(1, 8))

story.extend(make_box('🧠 DEFINITIONS', [
    '<b>Consent</b> = voluntary, informed, specific agreement. Posting online ≠ AI consent.',
    '<b>Abstracted power</b> = tech-enabled control that distances actor from consequences (Peterson et al. 2023)',
    '<b>Conditional consent</b> = "I consent to X but NOT Y" — scraping violates the condition',
    '<b>Deepfake</b> = AI-generated realistic fake image/video of a real person',
    '<b>Nudify app</b> = AI tool that digitally removes clothing from photos',
], color=NAVY))

story.extend(make_box('📊 KEY STATS', [
    '<b>51%</b> of UK novelists think AI will fully replace them (Cambridge)',
    '<b>59%</b> know work used to train LLMs without consent',
    '<b>85%</b> expect income to decline due to AI',
    '<b>80%</b> agree AI has societal benefits (nuanced, NOT anti-tech)',
    '<b>33%</b> use AI for non-creative tasks in writing',
    '<b>66%</b> say romance authors are "extremely threatened"',
    '<b>1,000+</b> musicians released silent album protesting UK copyright changes',
    '<b>£7.6bn</b> UK music industry contribution (2023), <b>£11bn</b> publishing',
], color=ACCENT))

story.extend(make_box('🔗 CONNECTING THEMES', [
    '<b>All three articles</b> are about CONSENT being violated by AI companies',
    '<b>Power asymmetry</b>: individuals vs tech giants — creators have no real choice',
    '<b>Abstracted power</b> makes scraping/deepfakes feel "victimless" — but victims are real',
    '<b>Opt-out vs opt-in</b>: who bears the burden? Currently creators, not companies.',
    '<b>The test</b>: "If you wouldn\'t do it in person, don\'t do it with technology"',
    '<b>Genre fiction + formulaic content</b> most at risk (romance, thrillers, crime)',
    '<b>Women and girls</b> disproportionately targeted by deepfakes',
    '<b>Legal systems</b> struggling to catch up — built for physical harm, not synthetic',
], color=TEAL))

story.extend(make_box('👤 KEY PEOPLE & SOURCES', [
    '<b>Dr Tina L. Peterson</b> — lecturer, coined "abstracted power" (IEEE 2023)',
    '<b>Dr Clementine Collett</b> — Cambridge researcher, novelists study',
    '<b>Darren Lewis / Future Cut</b> — guest speaker, songwriter/producer (50M+ album sales)',
    '<b>Ed Newton-Rex</b> — organised the silent album protest',
    '<b>Paul McCartney</b> — called copyright changes "rip off" technology',
], color=NAVY))

story.append(Spacer(1, 20))
story.append(Paragraph('Good luck tomorrow. You\'ve got this. 🏛️', s_footer))
story.append(Paragraph('Compiled by Atlas · 19 February 2026', s_footer))

doc.build(story)
print(f'✅ Built: {OUTPUT}')
