import os
import io
import random
import urllib.request

import streamlit as st
from PIL import Image, ImageOps, ImageFilter

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
)
from reportlab.pdfbase.pdfmetrics import stringWidth


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BerryBini Kids Activity Hub",
    page_icon="🍓",
    layout="centered",
)


# ============================================================
# BRAND
# ============================================================

BRAND_NAME = "BerryBini"
APP_TITLE = "BerryBini Kids Activity Hub"
ASSET_DIR = "berrybini_assets"

os.makedirs(ASSET_DIR, exist_ok=True)


# ============================================================
# IMAGE ASSETS
# Twemoji assets are used as recognizable educational pictures.
# ============================================================

TWEMOJI_BASE = (
    "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/"
)

EMOJIS = {
    "apple": "1f34e",
    "banana": "1f34c",
    "strawberry": "1f353",
    "orange": "1f34a",
    "watermelon": "1f349",
    "grapes": "1f347",

    "dog": "1f436",
    "cat": "1f431",
    "lion": "1f981",
    "elephant": "1f418",
    "monkey": "1f435",
    "rabbit": "1f430",

    "sun": "2600-fe0f",
    "star": "2b50",
    "heart": "2764-fe0f",
    "flower": "1f33c",

    "car": "1f697",
    "balloon": "1f388",
    "ball": "26bd",
}


@st.cache_data(show_spinner=False)
def download_asset(name, code):
    """
    Downloads and caches a Twemoji PNG.
    """
    filename = os.path.join(ASSET_DIR, f"{name}.png")

    if not os.path.exists(filename):
        url = f"{TWEMOJI_BASE}{code}.png"
        try:
            urllib.request.urlretrieve(url, filename)
        except Exception:
            return None

    return filename


@st.cache_data(show_spinner=False)
def create_outline(source_path, name):
    """
    Creates a simple printable outline version.
    """
    if source_path is None:
        return None

    outline_path = os.path.join(ASSET_DIR, f"{name}_outline.png")

    if os.path.exists(outline_path):
        return outline_path

    try:
        img = Image.open(source_path).convert("RGBA")

        # White background
        background = Image.new("RGBA", img.size, "white")
        background.alpha_composite(img)

        gray = background.convert("L")

        # Detect edges
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.autocontrast(edges)

        # Convert edges into black lines
        edges = ImageOps.invert(edges)

        # Threshold
        edges = edges.point(lambda p: 0 if p < 210 else 255)

        edges.save(outline_path)

        return outline_path

    except Exception:
        return source_path


def get_asset(name):
    code = EMOJIS.get(name)

    if not code:
        return None

    return download_asset(name, code)


def get_outline(name):
    source = get_asset(name)
    return create_outline(source, name)


# ============================================================
# DATA
# ============================================================

FRUITS = [
    ("apple", "Apple"),
    ("banana", "Banana"),
    ("strawberry", "Strawberry"),
    ("orange", "Orange"),
    ("watermelon", "Watermelon"),
    ("grapes", "Grapes"),
]

ANIMALS = [
    ("dog", "Dog"),
    ("cat", "Cat"),
    ("lion", "Lion"),
    ("elephant", "Elephant"),
    ("monkey", "Monkey"),
    ("rabbit", "Rabbit"),
]

OBJECTS = [
    ("car", "Car"),
    ("balloon", "Balloon"),
    ("ball", "Ball"),
    ("flower", "Flower"),
    ("star", "Star"),
]

COLORS = [
    ("RED", "Apple"),
    ("YELLOW", "Banana"),
    ("ORANGE", "Orange"),
    ("GREEN", "Watermelon"),
    ("PURPLE", "Grapes"),
]


# ============================================================
# AGE-SPECIFIC ACTIVITY MENU
# ============================================================

AGE_ACTIVITIES = {
    "2–3 years": [
        "Color & Explore",
        "Colors Around Me",
        "Count 1–3",
        "Same or Different",
        "Big or Small",
        "Animal Friends",
        "Fruit Friends",
        "Pre-Writing Lines",
    ],

    "3–4 years": [
        "Color & Match",
        "Match the Same",
        "Count 1–5",
        "Beginning ABC",
        "Shapes & Patterns",
        "Fruit Matching",
        "Animal Matching",
        "Trace & Draw",
    ],

    "4–5 years": [
        "Count 1–10",
        "Missing Numbers",
        "Letter & Picture Match",
        "Sort & Classify",
        "Patterns",
        "Find the Odd One",
        "Animals & Homes",
        "Letter Tracing",
    ],

    "5–6 years": [
        "Count 1–20",
        "Picture Addition",
        "Picture Subtraction",
        "Beginning Sounds",
        "Word & Picture Match",
        "Number Sequencing",
        "Patterns",
        "Simple Maze",
    ],
}


AGE_TIPS = {
    "2–3 years":
        "At this age, children learn best through recognition, pointing, naming, movement and simple choices.",

    "3–4 years":
        "Encourage your child to say the answer aloud. Matching, counting and simple patterns build early thinking skills.",

    "4–5 years":
        "Ask your child to explain why an answer belongs. Sorting, sequencing and beginning sounds support early reasoning.",

    "5–6 years":
        "Encourage your child to solve independently first, then explain how they found the answer.",
}


# ============================================================
# PDF STYLES
# ============================================================

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "BerryTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=21,
    leading=25,
    alignment=TA_CENTER,
    spaceAfter=8,
)

subtitle_style = ParagraphStyle(
    "BerrySubtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=14,
    alignment=TA_CENTER,
    spaceAfter=12,
)

heading_style = ParagraphStyle(
    "BerryHeading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    spaceBefore=7,
    spaceAfter=7,
)

question_style = ParagraphStyle(
    "Question",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=15,
    spaceAfter=6,
)

small_style = ParagraphStyle(
    "Small",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=11,
)


# ============================================================
# PDF HELPERS
# ============================================================

def pdf_image(path, width=30 * mm, height=30 * mm):
    """
    Safely creates a ReportLab image.
    """
    if not path or not os.path.exists(path):
        return Spacer(width, height)

    return RLImage(path, width=width, height=height)


def answer_box(width=25 * mm, height=15 * mm):
    data = [[""]]

    table = Table(
        data,
        colWidths=[width],
        rowHeights=[height],
    )

    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return table


def footer(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(
        A4[0] / 2,
        8 * mm,
        "BerryBini Kids Activity Hub • Free printable activity"
    )

    canvas.restoreState()


def pdf_header(story, age, activity):
    story.append(Paragraph("🍓 BerryBini", title_style))
    story.append(
        Paragraph(
            f"{activity} • Age {age}",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            "Name: ______________________________    Date: ________________",
            small_style
        )
    )

    story.append(Spacer(1, 6 * mm))


def build_pdf(story, filename):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=filename,
        author="BerryBini",
    )

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer,
    )

    buffer.seek(0)
    return buffer.getvalue()


def instruction(story, text):
    story.append(Paragraph(text, question_style))
    story.append(Spacer(1, 2 * mm))


def picture_row(items, outline=False, size=27):
    row = []

    for name, label in items:
        path = get_outline(name) if outline else get_asset(name)

        cell = [
            pdf_image(
                path,
                width=size * mm,
                height=size * mm
            ),
            Paragraph(
                label,
                ParagraphStyle(
                    "PicLabel",
                    parent=small_style,
                    alignment=TA_CENTER,
                )
            ),
        ]

        row.append(cell)

    table = Table(
        [row],
        colWidths=[42 * mm] * len(row),
    )

    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return table


def numbered_choices(numbers):
    cells = []

    for n in numbers:
        cells.append(
            Table(
                [[str(n)]],
                colWidths=[22 * mm],
                rowHeights=[18 * mm],
                style=TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 1, colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 13),
                    ]
                ),
            )
        )

    table = Table(
        [cells],
        colWidths=[28 * mm] * len(cells),
    )

    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return table


# ============================================================
# 2–3 YEARS
# ============================================================

def activity_2_3_color(story):
    instruction(
        story,
        "Color the pictures. Ask your child to name each object."
    )

    items = [
        ("apple", "Apple"),
        ("banana", "Banana"),
        ("dog", "Dog"),
        ("flower", "Flower"),
    ]

    story.append(picture_row(items, outline=True, size=32))


def activity_2_3_colors(story):
    instruction(
        story,
        "Point to the RED picture."
    )

    story.append(
        picture_row(
            [
                ("apple", "RED"),
                ("banana", "YELLOW"),
                ("dog", "BROWN"),
            ],
            size=28
        )
    )

    story.append(Spacer(1, 5 * mm))

    instruction(
        story,
        "Point to the YELLOW picture."
    )

    story.append(
        picture_row(
            [
                ("banana", "YELLOW"),
                ("apple", "RED"),
                ("flower", "PINK"),
            ],
            size=28
        )
    )


def activity_2_3_count(story):
    instruction(
        story,
        "Look at the pictures. Count them. Circle the correct number."
    )

    questions = [
        (["apple"], [1, 2, 3]),
        (["banana", "banana"], [1, 2, 3]),
        (["strawberry", "strawberry", "strawberry"], [2, 3, 4]),
    ]

    for idx, (fruits, choices) in enumerate(questions, 1):
        story.append(
            Paragraph(f"{idx}. Count the pictures:", question_style)
        )

        items = [(x, "") for x in fruits]
        story.append(picture_row(items, size=24))
        story.append(numbered_choices(choices))
        story.append(Spacer(1, 6 * mm))


def activity_2_3_same(story):
    instruction(
        story,
        "Look at the first picture. Find the SAME picture."
    )

    questions = [
        ("apple", ["banana", "apple", "dog"]),
        ("dog", ["cat", "dog", "lion"]),
        ("banana", ["orange", "banana", "apple"]),
    ]

    for idx, (target, choices) in enumerate(questions, 1):
        story.append(
            Paragraph(
                f"{idx}. Find the same:",
                question_style
            )
        )

        story.append(
            picture_row([(target, "LOOK")], size=27)
        )

        story.append(
            picture_row(
                [(x, "") for x in choices],
                size=24
            )
        )

        story.append(Spacer(1, 5 * mm))


def activity_2_3_big_small(story):
    instruction(
        story,
        "Circle the BIG object in each pair."
    )

    pairs = [
        ("apple", "orange"),
        ("dog", "cat"),
        ("elephant", "rabbit"),
    ]

    for idx, pair in enumerate(pairs, 1):
        story.append(
            Paragraph(f"{idx}. Circle the BIG one.", question_style)
        )

        # Same images, different visual size
        row = []

        for j, name in enumerate(pair):
            size = 35 if j == 0 else 20
            row.append(
                [
                    pdf_image(
                        get_asset(name),
                        width=size * mm,
                        height=size * mm
                    )
                ]
            )

        table = Table(
            [row],
            colWidths=[65 * mm, 65 * mm],
            rowHeights=[40 * mm],
        )

        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 5 * mm))


def activity_2_3_animals(story):
    instruction(
        story,
        "Look at the animals. Point to the animal your parent names."
    )

    story.append(
        picture_row(
            [
                ("dog", "Dog"),
                ("cat", "Cat"),
                ("lion", "Lion"),
            ],
            size=30
        )
    )

    story.append(Spacer(1, 5 * mm))

    instruction(
        story,
        "Which animal says 'meow'? Point to it."
    )

    story.append(
        picture_row(
            [
                ("dog", "Dog"),
                ("cat", "Cat"),
                ("lion", "Lion"),
            ],
            size=30
        )
    )


def activity_2_3_fruits(story):
    instruction(
        story,
        "Point to the fruit your parent names."
    )

    story.append(
        picture_row(
            [
                ("apple", "Apple"),
                ("banana", "Banana"),
                ("strawberry", "Strawberry"),
            ],
            size=30
        )
    )

    story.append(Spacer(1, 5 * mm))

    instruction(
        story,
        "Which one is a BANANA?"
    )

    story.append(
        picture_row(
            [
                ("apple", "Apple"),
                ("banana", "Banana"),
                ("orange", "Orange"),
            ],
            size=30
        )
    )


def activity_2_3_lines(story):
    instruction(
        story,
        "Trace the lines slowly. Start at the dot."
    )

    lines = [
        "●  - - - - - - - - - - -  ★",
        "●  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  ★",
        "●  / / / / / / / / / /  ★",
        "●  ∩ ∩ ∩ ∩ ∩ ∩ ∩ ∩  ★",
    ]

    for line in lines:
        story.append(
            Paragraph(
                line,
                ParagraphStyle(
                    "Trace",
                    parent=styles["Normal"],
                    fontSize=20,
                    leading=35,
                    spaceAfter=5,
                )
            )
        )


# ============================================================
# 3–4 YEARS
# ============================================================

def activity_3_4_color_match(story):
    instruction(
        story,
        "Color each object. Then say its color aloud."
    )

    story.append(
        picture_row(
            [
                ("apple", "Apple"),
                ("banana", "Banana"),
                ("orange", "Orange"),
                ("strawberry", "Strawberry"),
            ],
            outline=True,
            size=28
        )
    )


def activity_3_4_match(story):
    instruction(
        story,
        "Match each picture to the SAME picture."
    )

    targets = [
        ("apple", "Apple"),
        ("dog", "Dog"),
        ("banana", "Banana"),
    ]

    choices = [
        ("banana", "Banana"),
        ("apple", "Apple"),
        ("dog", "Dog"),
    ]

    story.append(picture_row(targets, size=25))
    story.append(Spacer(1, 8 * mm))
    story.append(picture_row(choices, size=25))


def activity_3_4_count(story):
    instruction(
        story,
        "Count each group. Circle the correct number."
    )

    groups = [
        (["apple", "apple"], [1, 2, 3]),
        (["banana", "banana", "banana"], [2, 3, 4]),
        (
            ["strawberry", "strawberry", "strawberry", "strawberry"],
            [3, 4, 5]
        ),
    ]

    for idx, (items, choices) in enumerate(groups, 1):
        story.append(
            Paragraph(f"{idx}.", question_style)
        )

        story.append(
            picture_row([(x, "") for x in items], size=22)
        )

        story.append(numbered_choices(choices))
        story.append(Spacer(1, 5 * mm))


def activity_3_4_abc(story):
    instruction(
        story,
        "Match the letter to the picture that starts with that letter."
    )

    pairs = [
        ("A", "apple", "Apple"),
        ("B", "banana", "Banana"),
        ("D", "dog", "Dog"),
    ]

    for letter, image, label in pairs:
        table = Table(
            [
                [
                    Paragraph(
                        letter,
                        ParagraphStyle(
                            "BigLetter",
                            parent=styles["Normal"],
                            fontSize=28,
                            fontName="Helvetica-Bold",
                            alignment=TA_CENTER,
                        )
                    ),
                    pdf_image(
                        get_asset(image),
                        width=30 * mm,
                        height=30 * mm
                    ),
                    Paragraph(label, small_style),
                ]
            ],
            colWidths=[30 * mm, 45 * mm, 45 * mm],
        )

        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 4 * mm))


def activity_3_4_patterns(story):
    instruction(
        story,
        "Look at the pattern. What comes next?"
    )

    patterns = [
        ["apple", "banana", "apple", "banana"],
        ["dog", "cat", "dog", "cat"],
        ["star", "heart", "star", "heart"],
    ]

    answers = ["apple", "dog", "star"]

    for idx, (pattern, answer) in enumerate(zip(patterns, answers), 1):
        story.append(
            Paragraph(
                f"{idx}.",
                question_style
            )
        )

        story.append(
            picture_row(
                [(x, "") for x in pattern],
                size=20
            )
        )

        story.append(
            Paragraph(
                "What comes next?   ____________________",
                question_style
            )
        )

        story.append(Spacer(1, 5 * mm))


def activity_3_4_fruit_matching(story):
    instruction(
        story,
        "Draw a line to match each fruit with its same fruit."
    )

    left = [
        ("apple", "Apple"),
        ("banana", "Banana"),
        ("orange", "Orange"),
    ]

    right = [
        ("orange", "Orange"),
        ("apple", "Apple"),
        ("banana", "Banana"),
    ]

    table = Table(
        [
            [
                pdf_image(get_asset(left[i][0]), 25 * mm, 25 * mm),
                Paragraph("→", question_style),
                pdf_image(get_asset(right[i][0]), 25 * mm, 25 * mm),
            ]
            for i in range(3)
        ],
        colWidths=[50 * mm, 20 * mm, 50 * mm],
        rowHeights=[32 * mm] * 3,
    )

    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(table)


def activity_3_4_animal_matching(story):
    instruction(
        story,
        "Match the same animals."
    )

    story.append(
        picture_row(
            [
                ("dog", "Dog"),
                ("cat", "Cat"),
                ("lion", "Lion"),
            ],
            size=27
        )
    )

    story.append(Spacer(1, 8 * mm))

    story.append(
        picture_row(
            [
                ("lion", "Lion"),
                ("dog", "Dog"),
                ("cat", "Cat"),
            ],
            size=27
        )
    )


def activity_3_4_trace(story):
    instruction(
        story,
        "Trace the letters and draw the matching picture."
    )

    letters = [
        ("A", "apple"),
        ("B", "banana"),
        ("C", "cat"),
    ]

    for letter, image in letters:
        table = Table(
            [
                [
                    Paragraph(
                        f"{letter}  {letter}  {letter}",
                        ParagraphStyle(
                            "TraceLetter",
                            parent=styles["Normal"],
                            fontSize=24,
                            leading=30,
                        )
                    ),
                    pdf_image(
                        get_outline(image),
                        width=30 * mm,
                        height=30 * mm
                    ),
                ]
            ],
            colWidths=[80 * mm, 45 * mm],
            rowHeights=[35 * mm],
        )

        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 4 * mm))


# ============================================================
# 4–5 YEARS
# ============================================================

def activity_4_5_count(story):
    instruction(
        story,
        "Count each group and WRITE the number."
    )

    groups = [
        ["apple", "apple", "apple", "apple"],
        ["banana", "banana", "banana", "banana", "banana", "banana"],
        [
            "strawberry",
            "strawberry",
            "strawberry",
            "strawberry",
            "strawberry",
            "strawberry",
            "strawberry",
            "strawberry",
        ],
    ]

    for idx, group in enumerate(groups, 1):
        story.append(
            Paragraph(f"{idx}.", question_style)
        )

        story.append(
            picture_row(
                [(x, "") for x in group],
                size=17
            )
        )

        story.append(
            Paragraph(
                "My answer:  __________",
                question_style
            )
        )

        story.append(Spacer(1, 5 * mm))


def activity_4_5_missing_numbers(story):
    instruction(
        story,
        "Write the missing number."
    )

    sequences = [
        "1   2   ___   4   5",
        "3   ___   5   6   7",
        "6   7   8   ___   10",
    ]

    for idx, seq in enumerate(sequences, 1):
        story.append(
            Paragraph(
                f"{idx}.  {seq}",
                ParagraphStyle(
                    "Sequence",
                    parent=styles["Normal"],
                    fontSize=18,
                    leading=30,
                    spaceAfter=9,
                )
            )
        )


def activity_4_5_letter_picture(story):
    instruction(
        story,
        "Match each beginning letter to the correct picture."
    )

    items = [
        ("A", "apple", "Apple"),
        ("B", "banana", "Banana"),
        ("D", "dog", "Dog"),
        ("C", "cat", "Cat"),
    ]

    for letter, image, label in items:
        story.append(
            Table(
                [[
                    Paragraph(
                        letter,
                        ParagraphStyle(
                            "Letter",
                            parent=styles["Normal"],
                            fontSize=25,
                            fontName="Helvetica-Bold",
                            alignment=TA_CENTER,
                        )
                    ),
                    pdf_image(
                        get_asset(image),
                        width=25 * mm,
                        height=25 * mm
                    ),
                    Paragraph(label, small_style),
                    Paragraph(
                        "□ Match",
                        small_style
                    ),
                ]],
                colWidths=[22 * mm, 35 * mm, 40 * mm, 30 * mm],
                style=TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ]
                ),
            )
        )

        story.append(Spacer(1, 3 * mm))


def activity_4_5_sort(story):
    instruction(
        story,
        "Sort the pictures into the correct group: FRUIT or ANIMAL."
    )

    story.append(
        picture_row(
            [
                ("apple", "Apple"),
                ("dog", "Dog"),
                ("banana", "Banana"),
                ("cat", "Cat"),
            ],
            size=25
        )
    )

    story.append(Spacer(1, 8 * mm))

    table = Table(
        [
            [
                Paragraph(
                    "FRUIT",
                    heading_style
                ),
                Paragraph(
                    "ANIMAL",
                    heading_style
                ),
            ],
            [
                "__________________\n__________________",
                "__________________\n__________________",
            ],
        ],
        colWidths=[75 * mm, 75 * mm],
        rowHeights=[15 * mm, 30 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )

    story.append(table)


def activity_4_5_patterns(story):
    instruction(
        story,
        "Continue the pattern."
    )

    patterns = [
        "APPLE → BANANA → APPLE → BANANA → ______",
        "DOG → CAT → DOG → CAT → ______",
        "STAR → HEART → STAR → HEART → ______",
    ]

    for idx, pattern in enumerate(patterns, 1):
        story.append(
            Paragraph(
                f"{idx}. {pattern}",
                ParagraphStyle(
                    "PatternText",
                    parent=styles["Normal"],
                    fontSize=12,
                    leading=25,
                    spaceAfter=8,
                )
            )
        )


def activity_4_5_odd(story):
    instruction(
        story,
        "Three pictures belong together. Circle the one that does NOT belong."
    )

    groups = [
        ["apple", "banana", "dog"],
        ["cat", "lion", "orange"],
        ["banana", "strawberry", "elephant"],
    ]

    for idx, group in enumerate(groups, 1):
        story.append(
            Paragraph(f"{idx}.", question_style)
        )

        story.append(
            picture_row(
                [(x, "") for x in group],
                size=28
            )
        )

        story.append(Spacer(1, 4 * mm))


def activity_4_5_homes(story):
    instruction(
        story,
        "Think about where animals live. Circle the animal that belongs with each place."
    )

    questions = [
        ("Jungle", ["lion", "dog", "cat"]),
        ("Farm", ["elephant", "dog", "lion"]),
        ("Home", ["cat", "lion", "elephant"]),
    ]

    for idx, (place, choices) in enumerate(questions, 1):
        story.append(
            Paragraph(
                f"{idx}. {place}",
                question_style
            )
        )

        story.append(
            picture_row(
                [(x, "") for x in choices],
                size=27
            )
        )

        story.append(Spacer(1, 4 * mm))


def activity_4_5_letter_trace(story):
    instruction(
        story,
        "Trace each capital letter."
    )

    letters = ["A", "B", "C", "D", "E"]

    for letter in letters:
        story.append(
            Table(
                [[
                    Paragraph(
                        f"{letter}   {letter}   {letter}",
                        ParagraphStyle(
                            "TraceBig",
                            parent=styles["Normal"],
                            fontSize=27,
                            leading=34,
                        )
                    ),
                    Paragraph(
                        "________________________",
                        ParagraphStyle(
                            "WritingLine",
                            parent=styles["Normal"],
                            fontSize=18,
                        )
                    ),
                ]],
                colWidths=[65 * mm, 80 * mm],
                rowHeights=[22 * mm],
                style=TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                ),
            )
        )

        story.append(Spacer(1, 2 * mm))


# ============================================================
# 5–6 YEARS
# ============================================================

def activity_5_6_count(story):
    instruction(
        story,
        "Count the objects and write the number. Try counting up to 20."
    )

    groups = [
        FRUITS[:],
        ANIMALS[:],
    ]

    numbers = [
        12,
        15,
    ]

    for idx, (group, target) in enumerate(zip(groups, numbers), 1):
        story.append(
            Paragraph(
                f"{idx}. Count the pictures:",
                question_style
            )
        )

        repeated = []

        for i in range(target):
            repeated.append(group[i % len(group)][0])

        # Split into two rows
        row1 = repeated[:8]
        row2 = repeated[8:16]

        if row1:
            story.append(
                picture_row(
                    [(x, "") for x in row1],
                    size=15
                )
            )

        if row2:
            story.append(
                picture_row(
                    [(x, "") for x in row2],
                    size=15
                )
            )

        story.append(
            Paragraph(
                "My answer: __________________",
                question_style
            )
        )

        story.append(Spacer(1, 5 * mm))


def activity_5_6_addition(story):
    instruction(
        story,
        "Count the pictures. Add them together."
    )

    problems = [
        (2, 3, "apple"),
        (3, 2, "banana"),
        (4, 3, "strawberry"),
    ]

    for idx, (a, b, image) in enumerate(problems, 1):
        first = [(image, "") for _ in range(a)]
        second = [(image, "") for _ in range(b)]

        story.append(
            Paragraph(
                f"{idx}.",
                question_style
            )
        )

        story.append(
            picture_row(first, size=20)
        )

        story.append(
            Paragraph(
                "+",
                ParagraphStyle(
                    "Plus",
                    parent=styles["Normal"],
                    fontSize=20,
                    alignment=TA_CENTER,
                )
            )
        )

        story.append(
            picture_row(second, size=20)
        )

        story.append(
            Paragraph(
                "Answer: ________",
                question_style
            )
        )

        story.append(Spacer(1, 5 * mm))


def activity_5_6_subtraction(story):
    instruction(
        story,
        "Cross out the objects that are taken away. Then write the answer."
    )

    problems = [
        (5, 2, "apple"),
        (6, 3, "banana"),
        (7, 2, "strawberry"),
    ]

    for idx, (total, remove, image) in enumerate(problems, 1):
        story.append(
            Paragraph(
                f"{idx}. {total} − {remove} = ______",
                question_style
            )
        )

        items = []

        for i in range(total):
            label = "CROSS OUT" if i < remove else ""
            items.append((image, label))

        story.append(
            picture_row(items, size=18)
        )

        story.append(Spacer(1, 5 * mm))


def activity_5_6_sounds(story):
    instruction(
        story,
        "Say the beginning sound. Circle the correct letter."
    )

    questions = [
        ("apple", "Apple", ["A", "B", "C"]),
        ("banana", "Banana", ["B", "D", "E"]),
        ("cat", "Cat", ["A", "C", "D"]),
        ("dog", "Dog", ["B", "D", "G"]),
    ]

    for idx, (image, label, letters) in enumerate(questions, 1):
        story.append(
            Paragraph(
                f"{idx}. {label} begins with:",
                question_style
            )
        )

        story.append(
            picture_row([(image, label)], size=25)
        )

        story.append(
            numbered_choices(letters)
        )

        story.append(Spacer(1, 5 * mm))


def activity_5_6_word_match(story):
    instruction(
        story,
        "Read the word and match it to the correct picture."
    )

    pairs = [
        ("APPLE", "apple"),
        ("BANANA", "banana"),
        ("DOG", "dog"),
        ("CAT", "cat"),
    ]

    for word, image in pairs:
        table = Table(
            [[
                Paragraph(
                    word,
                    ParagraphStyle(
                        "Word",
                        parent=styles["Normal"],
                        fontSize=18,
                        fontName="Helvetica-Bold",
                        alignment=TA_CENTER,
                    )
                ),
                pdf_image(
                    get_asset(image),
                    width=28 * mm,
                    height=28 * mm
                ),
                "□ Match",
            ]],
            colWidths=[55 * mm, 45 * mm, 35 * mm],
            rowHeights=[35 * mm],
        )

        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 3 * mm))


def activity_5_6_sequence(story):
    instruction(
        story,
        "Put the numbers in the correct order."
    )

    sequences = [
        ["3", "1", "2", "5", "4"],
        ["8", "6", "7", "10", "9"],
        ["13", "11", "15", "12", "14"],
    ]

    for idx, seq in enumerate(sequences, 1):
        story.append(
            Paragraph(
                f"{idx}.",
                question_style
            )
        )

        cells = []

        for value in seq:
            cells.append(
                Table(
                    [[value]],
                    colWidths=[23 * mm],
                    rowHeights=[18 * mm],
                    style=TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 1, colors.black),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("FONTSIZE", (0, 0), (-1, -1), 13),
                        ]
                    ),
                )
            )

        table = Table(
            [cells],
            colWidths=[28 * mm] * len(cells),
        )

        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(table)

        story.append(
            Paragraph(
                "Write them in order: ______________________________",
                question_style
            )
        )

        story.append(Spacer(1, 5 * mm))


def activity_5_6_patterns(story):
    instruction(
        story,
        "Complete each pattern."
    )

    patterns = [
        "APPLE – BANANA – APPLE – BANANA – __________",
        "DOG – CAT – CAT – DOG – CAT – CAT – __________",
        "STAR – HEART – STAR – HEART – STAR – __________",
    ]

    for idx, pattern in enumerate(patterns, 1):
        story.append(
            Paragraph(
                f"{idx}. {pattern}",
                ParagraphStyle(
                    "AdvancedPattern",
                    parent=styles["Normal"],
                    fontSize=12,
                    leading=28,
                    spaceAfter=10,
                )
            )
        )


def activity_5_6_maze(story):
    instruction(
        story,
        "Help Bini get from START to the STAR. Draw a path without crossing the walls."
    )

    # Simple printable maze using a table.
    maze = [
        ["START", "", "█", "", "", "", "█"],
        ["", "█", "█", "", "█", "", "█"],
        ["", "", "", "", "█", "", ""],
        ["█", "█", "█", "", "█", "█", ""],
        ["", "", "", "", "", "", ""],
        ["", "█", "█", "█", "█", "█", ""],
        ["", "", "", "", "", "", "★"],
    ]

    table = Table(
        maze,
        colWidths=[20 * mm] * 7,
        rowHeights=[18 * mm] * 7,
    )

    style_commands = [
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]

    for r in range(7):
        for c in range(7):
            if maze[r][c] == "█":
                style_commands.append(
                    ("BACKGROUND", (c, r), (c, r), colors.black)
                )

    table.setStyle(TableStyle(style_commands))

    story.append(table)


# ============================================================
# DISPATCHER
# ============================================================

def generate_activity(age, activity):
    story = []

    pdf_header(story, age, activity)

    if age == "2–3 years":
        if activity == "Color & Explore":
            activity_2_3_color(story)
        elif activity == "Colors Around Me":
            activity_2_3_colors(story)
        elif activity == "Count 1–3":
            activity_2_3_count(story)
        elif activity == "Same or Different":
            activity_2_3_same(story)
        elif activity == "Big or Small":
            activity_2_3_big_small(story)
        elif activity == "Animal Friends":
            activity_2_3_animals(story)
        elif activity == "Fruit Friends":
            activity_2_3_fruits(story)
        elif activity == "Pre-Writing Lines":
            activity_2_3_lines(story)

    elif age == "3–4 years":
        if activity == "Color & Match":
            activity_3_4_color_match(story)
        elif activity == "Match the Same":
            activity_3_4_match(story)
        elif activity == "Count 1–5":
            activity_3_4_count(story)
        elif activity == "Beginning ABC":
            activity_3_4_abc(story)
        elif activity == "Shapes & Patterns":
            activity_3_4_patterns(story)
        elif activity == "Fruit Matching":
            activity_3_4_fruit_matching(story)
        elif activity == "Animal Matching":
            activity_3_4_animal_matching(story)
        elif activity == "Trace & Draw":
            activity_3_4_trace(story)

    elif age == "4–5 years":
        if activity == "Count 1–10":
            activity_4_5_count(story)
        elif activity == "Missing Numbers":
            activity_4_5_missing_numbers(story)
        elif activity == "Letter & Picture Match":
            activity_4_5_letter_picture(story)
        elif activity == "Sort & Classify":
            activity_4_5_sort(story)
        elif activity == "Patterns":
            activity_4_5_patterns(story)
        elif activity == "Find the Odd One":
            activity_4_5_odd(story)
        elif activity == "Animals & Homes":
            activity_4_5_homes(story)
        elif activity == "Letter Tracing":
            activity_4_5_letter_trace(story)

    elif age == "5–6 years":
        if activity == "Count 1–20":
            activity_5_6_count(story)
        elif activity == "Picture Addition":
            activity_5_6_addition(story)
        elif activity == "Picture Subtraction":
            activity_5_6_subtraction(story)
        elif activity == "Beginning Sounds":
            activity_5_6_sounds(story)
        elif activity == "Word & Picture Match":
            activity_5_6_word_match(story)
        elif activity == "Number Sequencing":
            activity_5_6_sequence(story)
        elif activity == "Patterns":
            activity_5_6_patterns(story)
        elif activity == "Simple Maze":
            activity_5_6_maze(story)

    # Parent tip
    story.append(Spacer(1, 8 * mm))
    story.append(
        Table(
            [[
                Paragraph(
                    f"<b>Parent Tip:</b> {AGE_TIPS[age]}",
                    small_style
                )
            ]],
            colWidths=[165 * mm],
            style=TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            ),
        )
    )

    story.append(Spacer(1, 6 * mm))

    story.append(
        Paragraph(
            "🍓 Keep learning playful. Praise effort, not just correct answers.",
            ParagraphStyle(
                "Closing",
                parent=small_style,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )
    )

    safe_activity = (
        activity
        .lower()
        .replace(" ", "_")
        .replace("&", "and")
        .replace("–", "-")
    )

    filename = f"BerryBini_{age.replace('–', '-')}_{safe_activity}.pdf"

    return build_pdf(story, filename), filename


# ============================================================
# STREAMLIT UI
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .tagline {
        text-align: center;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .berry-card {
        padding: 1rem;
        border: 1px solid #dddddd;
        border-radius: 14px;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">🍓 BerryBini Kids Activity Hub</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="tagline">Free playful learning activities for preschoolers</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# INTRO
# ------------------------------------------------------------

st.markdown(
    """
    <div class="berry-card">
    <b>Made for little learners.</b><br>
    Choose your child's age and create a printable activity designed
    for that developmental stage.
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# AGE
# ------------------------------------------------------------

st.subheader("👶 1. Choose Age")

age = st.radio(
    "Child's age",
    list(AGE_ACTIVITIES.keys()),
    horizontal=True,
)


# ------------------------------------------------------------
# ACTIVITY
# ------------------------------------------------------------

st.subheader("📚 2. Choose Activity")

activity = st.selectbox(
    "What would you like to practice?",
    AGE_ACTIVITIES[age],
)


# ------------------------------------------------------------
# LEARNING LEVEL
# ------------------------------------------------------------

learning_level = {
    "2–3 years": "Recognize & Explore",
    "3–4 years": "Match & Identify",
    "4–5 years": "Think & Classify",
    "5–6 years": "Solve & Apply",
}

st.info(
    f"**Learning level:** {learning_level[age]}  \n"
    f"{AGE_TIPS[age]}"
)


# ------------------------------------------------------------
# GENERATE
# ------------------------------------------------------------

st.subheader("🖨️ 3. Create Printable")

if st.button(
    "🍓 Create My BerryBini Activity",
    type="primary",
    use_container_width=True,
):

    with st.spinner("Creating your printable activity..."):
        pdf_bytes, filename = generate_activity(
            age,
            activity
        )

    st.success(
        "Your activity is ready! 🎉"
    )

    st.download_button(
        label="📄 Download Printable PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
    )


# ------------------------------------------------------------
# TODAY'S ACTIVITY
# ------------------------------------------------------------

st.divider()

st.subheader("🌟 BerryBini Learning Tip")

st.write(
    AGE_TIPS[age]
)

st.caption(
    "Parents can use these printables alongside BerryBini videos "
    "for a simple screen + hands-on learning routine."
)


# ------------------------------------------------------------
# BRAND FOOTER
# ------------------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;">
    <b>🍓 BerryBini</b><br>
    <small>Play • Learn • Grow</small>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Picture assets: Twemoji. See Twemoji licensing/attribution requirements before public deployment."
)