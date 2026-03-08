#!/usr/bin/env python3
"""Ethics Week 4 — All Three Reading Articles compiled into one PDF."""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)

OUTPUT = '/home/ubuntu/clawd/output/ethics-week4-readings.pdf'

NAVY = colors.HexColor('#1e3a5f')
ACCENT = colors.HexColor('#e94560')
TEAL = colors.HexColor('#0f969c')
GOLD = colors.HexColor('#f5a623')
LIGHT = colors.HexColor('#f8f9fa')

doc = SimpleDocTemplate(OUTPUT, pagesize=A4, topMargin=0.6*inch, bottomMargin=0.5*inch,
                        leftMargin=0.7*inch, rightMargin=0.7*inch)
styles = getSampleStyleSheet()

s_title = ParagraphStyle('T', parent=styles['Title'], fontSize=22, textColor=NAVY, spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
s_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=11, textColor=colors.gray, spaceAfter=16, alignment=TA_CENTER)
s_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=17, textColor=NAVY, spaceBefore=16, spaceAfter=8, fontName='Helvetica-Bold')
s_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, textColor=ACCENT, spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
s_body = ParagraphStyle('B', parent=styles['Normal'], fontSize=10.5, leading=16, spaceAfter=8, textColor=colors.HexColor('#333'), alignment=TA_JUSTIFY)
s_source = ParagraphStyle('Src', parent=styles['Normal'], fontSize=9, textColor=colors.gray, spaceAfter=4, fontName='Helvetica-Oblique')
s_quote = ParagraphStyle('Q', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555'), leftIndent=25, rightIndent=25, spaceBefore=8, spaceAfter=8, leading=15, fontName='Helvetica-Oblique')
s_footer = ParagraphStyle('F', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
s_box_title = ParagraphStyle('BT', parent=styles['Normal'], fontSize=10, textColor='white', fontName='Helvetica-Bold')

def article_header(number, title, source, url):
    """Create a styled article header."""
    elements = []
    # Number badge + title
    badge = Table([[Paragraph(f'Article {number}', s_box_title)]], colWidths=[80])
    badge.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), ACCENT), ('TOPPADDING', (0,0), (-1,-1), 4),
                                ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('LEFTPADDING', (0,0), (-1,-1), 10),
                                ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(badge)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(title, s_h1))
    elements.append(Paragraph(f'Source: {source}', s_source))
    elements.append(Paragraph(f'URL: {url}', s_source))
    elements.append(HRFlowable(width='100%', color=ACCENT, thickness=1))
    elements.append(Spacer(1, 8))
    return elements

story = []

# ── COVER PAGE ──
story.append(Spacer(1, 60))
story.append(Paragraph('Ethics Week 4 — Assigned Readings', s_title))
story.append(Paragraph('Generative AI, Consent and Power', s_sub))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=2))
story.append(Spacer(1, 20))
story.append(Paragraph('ECS7025P · Dr Tina L. Peterson · 20 February 2026', s_sub))
story.append(Spacer(1, 30))

# Contents
toc_data = [
    ['#', 'Article', 'Source', 'Page'],
    ['1', 'Artists release silent album in protest against AI using their work', 'BBC News', '2'],
    ['2', 'Half of UK novelists believe AI is likely to replace their work entirely', 'University of Cambridge', '4'],
    ['3', 'Non-consensual deepfakes, consent, and power in synthetic media', 'Digital Watch Observatory', '5'],
]
toc_table = Table(toc_data, colWidths=[25, 250, 120, 40])
toc_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9),
    ('ALIGN', (0,0), (0,-1), 'CENTER'), ('ALIGN', (3,0), (3,-1), 'CENTER'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(toc_table)

story.append(Spacer(1, 40))
story.append(Paragraph('Compiled by Atlas for quiz preparation · 19 February 2026', s_footer))

story.append(PageBreak())

# ── ARTICLE 1: BBC Silent Album ──
story.extend(article_header(1,
    'Artists release silent album in protest against AI using their work',
    'BBC News · Paul Glynn, Culture reporter',
    'https://www.bbc.co.uk/news/articles/cwyd3r62kp5o'))

story.append(Paragraph('More than 1,000 musicians — including Annie Lennox, Damon Albarn and Kate Bush — released a silent album on Tuesday in protest at the UK government\'s planned changes to copyright law, which they say would make it easier for AI companies to train models using copyrighted work without a licence.', s_body))

story.append(Paragraph('Under the new proposals, AI developers will be able to use creators\' content on the internet to help develop their models, unless the rights holders elect to "opt out".', s_body))

story.append(Paragraph('The artists hope the album, entitled <i>Is This What We Want?</i>, will draw attention to the potential impact on livelihoods and the UK music industry. All profits will be donated to the charity Help Musicians.', s_body))

story.append(Paragraph('"In the music of the future, will our voices go unheard?" — Kate Bush', s_quote))

story.append(Paragraph('The album — also backed by the likes of Billy Ocean, Ed O\'Brien of Radiohead and Bastille\'s Dan Smith, as well as The Clash, Mystery Jets and Jamiroquai — features sound recordings of empty studios and performance spaces, demonstrating what the artists fear is the potential impact of the proposed law change.', s_body))

story.append(Paragraph('The tracklisting for the record simply spells out the message: "The British government must not legalise music theft to benefit AI companies."', s_body))

story.append(Paragraph('The government is currently consulting on proposals that would allow AI companies to use material that is available online without respecting copyright if they are using it for text or data mining. Generative AI programmes mine, or learn, from vast amounts of data like text, images, or music online to generate new content which feels like it has been made by a human.', s_body))

story.append(Paragraph('The proposals would give artists or creators a so-called "rights reservation" — the ability to opt out. But critics of the plan believe it is not possible for an individual writer or artist to notify thousands of different AI service providers that they do not want their content used in that way, or to monitor what has happened to their work across the whole internet.', s_body))

story.append(Paragraph('A spokesman for the Department for Science, Innovation and Technology (DSIT) said that the UK\'s "current regime for copyright and AI is holding back the creative industries, media and AI sector from realising their full potential — and that cannot continue." They added that "no decisions have been taken" and "no moves will be made until we are absolutely confident we have a practical plan that delivers each of our objectives."', s_body))

story.append(Paragraph('\'Disastrous for musicians\'', s_h2))

story.append(Paragraph('Imogen Heap, Yusuf aka Cat Stevens and Riz Ahmed have also backed the silent album release as well as Tori Amos and Hans Zimmer. Composer Max Richter noted how the plans not only have an impact on musicians but "impoverish creators" across the board, from writers to visual artists and beyond.', s_body))

story.append(Paragraph('In 2023, UK music contributed a record £7.6 billion to the economy.', s_body))

story.append(Paragraph('Organiser of the silent record, Ed Newton-Rex, said the proposals were not only "disastrous for musicians" in the UK but also "totally unnecessary", as the country can be "leaders in AI without throwing our world-leading creative industries under the bus."', s_body))

story.append(Paragraph('Singer-songwriter Naomi Kimpenu added: "We cannot be abandoned by the government and have our work stolen for the profit of big tech." She said the plans would "shatter the prospects of so many emerging artists in the UK."', s_body))

story.append(Paragraph('In January, Sir Paul McCartney told the BBC the proposed changes to copyright law could allow "rip off" technology that might make it impossible for musicians and artists to make a living. In a letter to The Times, signatories including Sir Paul, Lord Lloyd Webber and Sir Stephen Fry said that changes to the law will allow big tech to raid the creative sectors. They were joined by the likes of Bush, Ed Sheeran, Dua Lipa and Sting in opposing plans to change copyright laws.', s_body))

story.append(Paragraph('On Tuesday, the UK\'s creative industries launched the Make It Fair campaign, which includes wrap-around adverts in national newspapers, urging people to write to their MPs to object to the government\'s plans.', s_body))

story.append(PageBreak())

# ── ARTICLE 2: Cambridge Novelists ──
story.extend(article_header(2,
    'Half of UK novelists believe AI is likely to replace their work entirely',
    'University of Cambridge',
    'https://www.cam.ac.uk/stories/generative-ai-novelists'))

story.append(Paragraph('Just over half (51%) of published novelists in the UK say that artificial intelligence is likely to end up entirely replacing their work as fiction writers, a new report from the University of Cambridge has found.', s_body))

story.append(Paragraph('Close to two-thirds (59%) of novelists say they know their work has been used to train AI Large Language Models (LLMs) without permission or payment.', s_body))

story.append(Paragraph('Over a third (39%) of novelists say their income has already taken a hit from generative AI, for example due to loss of other work that facilitates novel writing. Most (85%) novelists expect their future income to be driven down by AI.', s_body))

story.append(Paragraph('In new research for Cambridge\'s Minderoo Centre for Technology and Democracy (MCTD), Dr Clementine Collett surveyed 258 published novelists earlier this year, as well as 74 industry insiders — from commissioning editors to literary agents — to gauge how AI is viewed and used in the world of British fiction.', s_body))

story.append(Paragraph('Genre authors are considered the most vulnerable to displacement by AI, according to the report, with two-thirds (66%) of all those surveyed listing romance authors as "extremely threatened", followed closely by writers of thrillers (61%) and crime (60%).', s_body))

story.append(Paragraph('Despite this, overall sentiment in UK fiction is not anti-AI, with 80% of respondents agreeing that AI offers benefits to parts of society. In fact, a third of novelists (33%) use AI in their writing process, mainly for "non-creative" tasks such as information search.', s_body))

story.append(Paragraph('However, the report outlines profound concerns from the cornerstone of a publishing industry that contributes an annual £11bn to the UK economy, and exports more books than any other country in the world.', s_body))

story.append(Paragraph('Literary creatives feel that copyright laws have not been respected or enforced since the emergence of generative AI. They call for informed consent and fair remuneration for the use of their work, along with transparency from big tech companies, and support in getting it from the UK government.', s_body))

story.append(Paragraph('Many warn of a potential loss of originality in fiction, as well as a fraying of trust between writers and readers if AI use is not disclosed. Some novelists worry that suspicions of AI use could damage their reputation.', s_body))

story.append(Paragraph('"There is widespread concern from novelists that generative AI trained on vast amounts of fiction will undermine the value of writing and compete with human novelists." — Dr Clementine Collett', s_quote))

story.append(Paragraph('"Many novelists felt uncertain there will be an appetite for complex, long-form writing in years to come."', s_quote))

story.append(Paragraph('Tech companies have the fiction market firmly in their sights. Generative AI tools such as Sudowrite and Novelcrafter can be used to brainstorm and edit novels, while Qyx AI Book Creator or Squibler can be used to draft full-length books. Platforms such as Spines use AI to assist with publishing processes from cover designs to distribution.', s_body))

story.append(Paragraph('"The brutal irony is that the generative AI tools affecting novelists are likely trained on millions of pirated novels scraped from shadow libraries without the consent or remuneration of authors." — Dr Collett', s_quote))

story.append(PageBreak())

# ── ARTICLE 3: Digital Watch Deepfakes ──
story.extend(article_header(3,
    'Non-consensual deepfakes, consent, and power in synthetic media',
    'Digital Watch Observatory',
    'https://dig.watch/updates/non-consensual-deepfakes-consent-and-power-in-synthetic-media'))

story.append(Paragraph('<i>The rise of AI pornography reveals bigger societal risks, where sexual representation becomes detached from lived experience and consent is reduced to a technical obstacle rather than a social principle.</i>', s_quote))

story.append(Paragraph('AI has reshaped almost every domain of digital life, from creativity and productivity to surveillance and governance. One of the most controversial and ethically fraught areas of AI deployment involves pornography, particularly where generative systems are used to create, manipulate, or simulate sexual content involving real individuals without consent.', s_body))

story.append(Paragraph('What was once a marginal issue confined to niche online forums has evolved into a global policy concern, driven by the rapid spread of AI-powered nudity applications, deepfake pornography, and image-editing tools integrated into mainstream platforms.', s_body))

story.append(Paragraph('Recent controversies surrounding AI-powered nudity apps and the image-generation capabilities of Elon Musk\'s Grok have accelerated public debate and regulatory scrutiny. Governments, regulators, and civil society organisations increasingly treat AI-generated sexual content not as a matter of taste or morality, but as an issue of digital harm, gender-based violence, child safety, and fundamental rights.', s_body))

story.append(Paragraph('Legislative initiatives such as the US Take It Down Act illustrate a broader shift toward recognising non-consensual synthetic sexual content as a distinct and urgent category of abuse.', s_body))

story.append(Paragraph('From online pornography to synthetic sexuality', s_h2))

story.append(Paragraph('Pornography has long been intertwined with technological change. From photography and film to VHS tapes, DVDs, and streaming platforms, sexual content has often been among the earliest adopters of new media technologies. The transition from traditional pornography to AI-generated sexual content, however, marks a deeper shift than earlier format changes.', s_body))

story.append(Paragraph('Conventional online pornography relies on human performers, production processes, and contractual relationships, even where exploitation or coercion exists. AI-generated pornography, instead of depicting real sexual acts, simulates them using algorithmic inference. Faces, bodies, voices, and identities can be reconstructed or fabricated at scale, often without the knowledge or consent of the individuals whose likenesses are used.', s_body))

story.append(Paragraph('AI nudity apps exemplify such a transformation. These tools allow users to upload images of real people and generate artificial nude versions, frequently marketed as entertainment or novelty applications. The underlying technology relies on diffusion models trained on vast datasets of human bodies and sexual imagery, enabling increasingly realistic outputs. Unlike traditional pornography, the subject of the image may never have participated in any sexual act, yet the resulting content can be indistinguishable from authentic photography.', s_body))

story.append(Paragraph('AI nudity apps and the normalisation of non-consensual sexual content', s_h2))

story.append(Paragraph('The recent proliferation of AI nudity applications has intensified concerns around consent and harm. These apps are frequently marketed through euphemistic language, emphasising humour, experimentation, or artistic exploration instead of sexual exploitation. Their core functionality, however, centres on digitally removing clothing from images of real people.', s_body))

story.append(Paragraph('Regulators and advocacy groups increasingly argue that such tools normalise a culture in which consent is irrelevant. The ability to undress someone digitally, without personal involvement, reflects a broader pattern of technological power asymmetry, where the subject of the image lacks meaningful control over how personal likeness is used.', s_body))

story.append(Paragraph('The ongoing Grok controversy illustrates how quickly the associated harms can scale when AI tools are embedded within major platforms. Reports that Grok can generate or modify images of women and children in sexualised ways have triggered backlash from governments, regulators, and victims\' rights organisations. Even where companies claim that safeguards are in place, the repeated emergence of abusive outputs suggests systemic design failures rather than isolated misuse.', s_body))

story.append(Paragraph('What distinguishes AI-generated sexual content from earlier forms of online abuse lies not only in realism but also in replicability. Once an image or model exists, reproduction can occur endlessly, with the content shared across jurisdictions and recontextualised in new forms. Victims often face a permanent loss of control over digital identity, with limited avenues for redress.', s_body))

story.append(Paragraph('Gendered harm and child protection', s_h2))

story.append(Paragraph('The impact of AI-generated pornography remains unevenly distributed. Research and reporting consistently show that women and girls are disproportionately targeted by non-consensual synthetic sexual content. Public figures, journalists, politicians, and private individuals alike have found themselves subjected to sexualised deepfakes designed to humiliate, intimidate, or silence them.', s_body))

story.append(Paragraph('Children face even greater risk. AI tools capable of generating nudified or sexualised images of minors raise alarm across legal and ethical frameworks. Even where no real child experiences physical abuse during content creation, the resulting imagery may still constitute child sexual abuse material under many legal definitions. The existence of such content contributes to harmful sexualisation and may fuel exploitative behaviour.', s_body))

story.append(Paragraph('AI complicates traditional child protection frameworks because the abuse occurs at the level of representation, not physical contact. Legal systems built around evidentiary standards tied to real-world acts struggle to categorise synthetic material. Regulators increasingly reject the argument that no real person suffered harm, recognising that harm arises through exposure, distribution, and psychological impact rather than physical contact alone.', s_body))

story.append(Paragraph('Platform responsibility and the limits of self-regulation', s_h2))

story.append(Paragraph('Technology companies have historically relied on self-regulation to address harmful content. In the context of AI-generated pornography, such an approach has demonstrated clear limitations. Platform policies banning non-consensual sexual content often lag behind technological capabilities, while enforcement remains inconsistent and opaque.', s_body))

story.append(Paragraph('The Grok case highlights these challenges. Even where companies announce restrictions or safeguards, questions remain regarding enforcement, detection accuracy, and accountability. AI systems struggle to reliably determine whether an image depicts a real person, whether consent exists, or whether local laws apply.', s_body))

story.append(Paragraph('Commercial incentives further complicate moderation efforts. AI image tools drive user engagement, subscriptions, and publicity. Restricting capabilities may conflict with business objectives, particularly in competitive markets. As a result, companies tend to act only after public backlash or regulatory intervention, instead of proactively addressing foreseeable harm.', s_body))

story.append(Paragraph('Legal responses and the emergence of targeted legislation', s_h2))

story.append(Paragraph('Governments worldwide are beginning to address AI-generated pornography through a combination of existing laws and new legislative initiatives. The Take It Down Act represents one of the most prominent attempts to directly confront non-consensual intimate imagery, including AI-generated content.', s_body))

story.append(Paragraph('The Act strengthens platforms\' obligations to remove intimate images shared without consent, regardless of whether the content is authentic or synthetic. Victims\' rights to request takedowns are expanded, while procedural barriers that previously left individuals navigating complex reporting systems are reduced. Crucially, the law recognises that harm does not depend on image authenticity, but on the impact experienced by the individual depicted.', s_body))

story.append(Paragraph('Within the EU, debates around AI nudity apps intersect with the AI Act and the Digital Services Act (DSA). While the AI Act categorises certain uses of AI as prohibited or high-risk, lawmakers continue to question whether nudity applications fall clearly within existing bans. Other jurisdictions, including Australia, the UK, and parts of Southeast Asia, are exploring regulatory approaches combining platform obligations, criminal penalties, and child protection frameworks.', s_body))

story.append(Paragraph('Enforcement challenges and jurisdictional fragmentation', s_h2))

story.append(Paragraph('Despite legislative progress, enforcement remains a significant challenge. AI-generated pornography operates inherently across borders. Applications may be developed in one country, hosted in another, and used globally. Content can be shared instantly across platforms, subject to different legal regimes. Jurisdictional fragmentation complicates takedown requests and criminal investigations.', s_body))

story.append(Paragraph('Technical enforcement presents additional difficulties. Automated detection systems struggle to distinguish consensual adult content from non-consensual synthetic imagery. Over-reliance on automation risks false positives and censorship, while under-enforcement leaves victims unprotected.', s_body))

story.append(Paragraph('Broader societal implications', s_h2))

story.append(Paragraph('Beyond legal and technical concerns, AI-generated pornography raises deeper questions about sexuality, power, and digital identity. The ability to fabricate sexual representations of others undermines traditional understandings of bodily autonomy and consent. Sexual imagery becomes detached from lived experience, transformed into manipulable data.', s_body))

story.append(Paragraph('Such shifts risk normalising the perception of individuals as visual assets rather than autonomous subjects. When sexual access can be simulated without consent, the social meaning of consent itself may weaken. Critics argue that such technologies reinforce misogynistic and exploitative norms, particularly where women\'s bodies are treated as endlessly modifiable digital material.', s_body))

story.append(Paragraph('Effective responses require legal clarity, platform accountability, technical safeguards, and cultural change, especially with the help of the educational system. As AI systems become more powerful and accessible, societies must confront difficult questions about consent, identity, and responsibility in the digital age.', s_body))

story.append(Paragraph('The challenge lies not merely in restricting technology, but in defining ethical boundaries that protect human dignity while preserving legitimate innovation.', s_body))

# Footer
story.append(Spacer(1, 20))
story.append(HRFlowable(width='100%', color=colors.HexColor('#ddd'), thickness=1))
story.append(Spacer(1, 8))
story.append(Paragraph('All three articles compiled for Ethics Week 4 quiz preparation.', s_footer))
story.append(Paragraph('Atlas · 19 February 2026', s_footer))

doc.build(story)
print(f'✅ Built: {OUTPUT}')
