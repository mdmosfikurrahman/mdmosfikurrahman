#!/usr/bin/env python3
"""Generates the animated SVG header used by README.md.

    python assets/build.py

Pure SVG + SMIL. No JavaScript, no web fonts, no network calls at render time:
GitHub proxies these through camo, where scripts never execute but declarative
animation does. Both themes come out of one palette swap and are selected in the
README with <picture media="(prefers-color-scheme: ...)">.

Three panels, one visual language, all about a person rather than a product.

    career-*.svg    eight years on one axis. A header lockup with a year readout
                    that ticks through the stack actually in hand at the time, a
                    band of standing figures, then education, research and three
                    employers. Work still running gets no hard right edge; it
                    fades into the future it has not finished yet.

    rooms-*.svg     the three places the job was actually learned, as a
                    triptych: what each refused to let through, and what that
                    taught.

    measured-*.svg  the only one nobody wrote. Every figure comes out of
                    data/github.json, which fetch.py pulls from the API.

Each plays once and freezes, rather than looping beside someone trying to read.
A page reload starts it again.

There were charts of the platform at work as well, and they were good, but the
page they sat on is meant to be about a person rather than a portfolio, so they
came out again. `git log --diff-filter=D assets/` has them if they are wanted.
"""

import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

MONO = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")
SANS = ("ui-sans-serif, -apple-system, 'Segoe UI', Inter, Roboto, "
        "'Helvetica Neue', Arial, sans-serif")

PALETTES = {
    "dark": dict(
        bg="#0d1117", card="#161b22", border="#30363d", rule="#21262d",
        stripe="#161b22", fg="#e6edf3", muted="#8b949e", faint="#6e7681",
        blue="#58a6ff", green="#3fb950", purple="#bc8cff", yellow="#d29922",
        orange="#f0883e", accent="#58a6ff",
    ),
    "light": dict(
        bg="#ffffff", card="#f6f8fa", border="#d0d7de", rule="#e4e8ed",
        stripe="#f6f8fa", fg="#1f2328", muted="#59636e", faint="#818b98",
        blue="#0969da", green="#1a7f37", purple="#8250df", yellow="#9a6700",
        orange="#bc4c00", accent="#0969da",
    ),
}

# The panels play once and stay put. Nothing repeats, so a reader is not sitting
# next to something that keeps moving while they read it; a page reload replays
# it. Every animation runs on one RUN-second timeline and freezes on its last
# value, which is why keyTimes below are absolute seconds divided by RUN.
RUN = 6.5
PLAY_FROM, PLAY_TO = 0.35, 5.60      # the playhead sweep


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    """Short, stable number formatting — keeps the emitted SVG diff-friendly."""
    return ("%.3f" % float(v)).rstrip("0").rstrip(".") or "0"


def indent(lines, pad="  "):
    return "\n".join(pad + l.replace("\n", "\n" + pad) for l in lines)


def fade(appear, rise=0.16):
    """Opacity track: hidden, fades in at `appear`, then stays."""
    keys = [0.0, appear, appear + rise, RUN]
    return ('<animate attributeName="opacity" dur="%gs" fill="freeze"'
            ' values="0;0;1;1" keyTimes="%s"/>'
            % (RUN, ";".join(f(k / RUN) for k in keys)))


def steps(frames, x, y, size, colour, font=MONO, anchor="end", weight="700",
          spacing=None):
    """A readout rendered as N overlapping texts, each visible for its slice.

    SMIL cannot animate text content, so a ticker is N elements taking turns.
    """
    out = []
    usable = [fr for fr in frames if fr[1] > fr[0]]
    for i, (start, stop, label) in enumerate(usable):
        # The last frame has nothing to hand over to, so it stays on screen.
        if i == len(usable) - 1:
            values, keys = "0;1", "0;%s" % f(start / RUN)
        else:
            values = "0;1;0"
            keys = "0;%s;%s" % (f(start / RUN), f(min(stop, RUN) / RUN))
        out.append('<text x="%s" y="%s" text-anchor="%s" font-family="%s" '
                   'font-size="%s" font-weight="%s"%s fill="%s" opacity="0">%s'
                   '<animate attributeName="opacity" dur="%gs" fill="freeze" '
                   'calcMode="discrete" values="%s" keyTimes="%s"/></text>'
                   % (f(x), f(y), anchor, font, size, weight,
                      '' if spacing is None else ' letter-spacing="%s"' % spacing,
                      colour, esc(label), RUN, values, keys))
    return out


# ================================================================== the panel ==

W, H = 900, 484

X0, X1 = 258.0, 876.0                # plot area
FROM, TO = 2018.0, 2027.0
PX = (X1 - X0) / (TO - FROM)
NOW = 2026.72                        # where "still running" reaches

HEAD_RULE = 72.0
STAT_VALUE, STAT_LABEL, STAT_RULE = 112.0, 126.0, 148.0
TICK_Y, GRID_TOP = 168.0, 178.0
ROW_Y, ROW_H = 190.0, 30.0
GRID_BOTTOM = 434.0
MARKER_Y, LEGEND_Y = 452.0, 470.0

STATS = [("4.5 yrs", "in production"), ("3", "companies"),
         ("10", "peer-reviewed papers"), ("185", "citations"), ("4", "h-index")]

#      headline                                detail                                       from      to     tone
ROWS = [
    ("B.Sc. Computer Science & Engineering", "Daffodil International University · CGPA 3.83", 2018.00, 2021.98, "purple"),
    ("Erasmus+ exchange semester",           "Adam Mickiewicz University, Poznań",       2021.10, 2021.60, "purple"),
    ("Applied ML research",                  "10 papers · 185 citations · h-index 4",         2020.00, NOW,     "yellow"),
    ("Peer review & invited talks",          "4 journals · 3 conferences · IEEE speaker",     2022.00, NOW,     "soft"),
    ("BJIT Group",                           "Java · GraphQL · Japanese review standards",    2022.25, 2023.50, "orange"),
    ("REVE Systems",                         "Spring Boot · Oracle · customs compliance",     2023.50, 2024.83, "orange"),
    ("Akij iBOS Ltd.",                       ".NET 9 · gRPC · Kubernetes · team of ten",      2024.83, NOW,     "blue"),
    ("Building in public",                   "Java and .NET, on my own time",                 2025.42, NOW,     "green"),
]

MARKERS = [(2020.95, "start", "IEEE Best Paper Award"),
           (2024.85, "end", "Team lead · 10 engineers")]

# What was actually in hand that year — the readout, ticking with the sweep.
YEARS = [(2018, "undergraduate · CSE"), (2019, "undergraduate · CSE"),
         (2020, "Python · applied ML"), (2021, "Python · applied ML"),
         (2022, "Java · GraphQL"), (2023, "Java · Spring Boot · Oracle"),
         (2024, "Spring Boot → .NET 9"), (2025, ".NET 9 · gRPC · Kubernetes"),
         (2026, ".NET 9 · Java 21 · Next.js")]

LEGEND = [("purple", "Education"), ("yellow", "Research"),
          ("orange", "Java · Spring"), ("blue", ".NET"),
          ("green", "On my own time")]

TONE = {"purple": "purple", "yellow": "yellow", "soft": "yellow",
        "orange": "orange", "blue": "blue", "green": "green"}


def at(year):
    return PLAY_FROM + ((year - FROM) / (TO - FROM)) * (PLAY_TO - PLAY_FROM)


def x_of(year):
    return X0 + (year - FROM) * PX


def career(theme):
    p = PALETTES[theme]
    base, revealed, labels = [], [], []

    # -- header lockup ------------------------------------------------------
    base.append('<text x="24" y="34" font-family="%s" font-size="15" '
                'font-weight="700" fill="%s">Two threads, one instinct</text>'
                % (SANS, p["fg"]))
    base.append('<text x="24" y="54" font-family="%s" font-size="10.5" fill="%s">'
                'Production engineering and applied research in parallel since 2018. '
                'Java, .NET and Python, three companies, ten papers.</text>'
                % (SANS, p["faint"]))

    frames = [(at(y), at(y + 1), str(y)) for y, _ in YEARS]
    base += steps(frames, 876, 40, "24", p["accent"], spacing="0.5")
    base += steps([(a, b, YEARS[i][1]) for i, (a, b, _) in enumerate(frames)],
                  876, 56, "10", p["faint"], weight="400")
    base.append('<line x1="24" y1="%s" x2="876" y2="%s" stroke="%s" '
                'stroke-width="1"/>' % (HEAD_RULE, HEAD_RULE, p["border"]))

    # -- standing figures ---------------------------------------------------
    cell = 852.0 / len(STATS)
    for i, (value, label) in enumerate(STATS):
        cx = 24.0 + cell * (i + 0.5)
        if i:
            base.append('<line x1="%s" y1="88" x2="%s" y2="132" stroke="%s" '
                        'stroke-width="1"/>'
                        % (f(24.0 + cell * i), f(24.0 + cell * i), p["rule"]))
        labels.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                      'font-size="18" font-weight="700" fill="%s" opacity="0">%s%s</text>'
                      % (f(cx), STAT_VALUE, MONO, p["fg"], esc(value),
                         fade(0.30 + i * 0.09, 0.14)))
        labels.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                      'font-size="9" letter-spacing="0.4" fill="%s" opacity="0">%s%s</text>'
                      % (f(cx), STAT_LABEL, SANS, p["faint"], esc(label.upper()),
                         fade(0.30 + i * 0.09, 0.14)))
    base.append('<line x1="24" y1="%s" x2="876" y2="%s" stroke="%s" '
                'stroke-width="1"/>' % (STAT_RULE, STAT_RULE, p["border"]))

    # -- axis ---------------------------------------------------------------
    for year in range(int(FROM), int(TO)):
        gx = x_of(year)
        base.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                    'stroke-width="1" stroke-dasharray="2 4"/>'
                    % (f(gx), GRID_TOP, f(gx), GRID_BOTTOM, p["rule"]))
        base.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                    'font-size="9.5" fill="%s">%d</text>'
                    % (f(gx), TICK_Y, MONO, p["faint"], year))
    base.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
                % (f(X0), GRID_TOP, f(X0), GRID_BOTTOM, p["border"]))

    # Today, so the faded bar ends read as "still running" rather than "unknown".
    base.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                'stroke-width="1" stroke-dasharray="2 3" opacity="0.6"/>'
                % (f(x_of(NOW)), GRID_TOP, f(x_of(NOW)), GRID_BOTTOM, p["accent"]))
    base.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                'font-size="9" font-weight="600" fill="%s">now</text>'
                % (f(x_of(NOW)), TICK_Y, SANS, p["accent"]))

    # -- rows ---------------------------------------------------------------
    for i, (head, detail, s0, s1, tone) in enumerate(ROWS):
        top = ROW_Y + i * ROW_H
        if i % 2 == 0:
            base.append('<rect x="24" y="%s" width="852" height="%s" fill="%s" '
                        'opacity="0.5"/>' % (f(top), f(ROW_H - 3), p["stripe"]))

        labels.append('<text x="24" y="%s" font-family="%s" font-size="11.5" '
                      'font-weight="600" fill="%s" opacity="0">%s%s</text>'
                      % (f(top + 13), SANS, p["fg"], esc(head), fade(at(s0), 0.12)))
        labels.append('<text x="24" y="%s" font-family="%s" font-size="9.5" '
                      'fill="%s" opacity="0">%s%s</text>'
                      % (f(top + 25), SANS, p["faint"], esc(detail),
                         fade(at(s0), 0.12)))

        running = abs(s1 - NOW) < 1e-6
        fill = ("url(#run-%s)" % tone) if running else p[TONE[tone]]
        opacity = ' opacity="0.55"' if (tone == "soft" and not running) else ""
        revealed.append('<rect x="%s" y="%s" width="%s" height="13" rx="3.5" '
                        'fill="%s"%s/>'
                        % (f(x_of(s0)), f(top + 8), f(max((s1 - s0) * PX, 3)),
                           fill, opacity))

    # -- markers ------------------------------------------------------------
    for year, anchor, text in MARKERS:
        mx = x_of(year)
        revealed.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                        'stroke-width="1.2" stroke-dasharray="3 3" opacity="0.8"/>'
                        % (f(mx), GRID_TOP - 4, f(mx), GRID_BOTTOM + 4, p["accent"]))
        labels.append('<text x="%s" y="%s" text-anchor="%s" font-family="%s" '
                      'font-size="10" font-weight="600" fill="%s" opacity="0">%s%s</text>'
                      % (f(mx + (7 if anchor == "start" else -7)), MARKER_Y, anchor,
                         SANS, p["accent"], esc(text), fade(at(year) + 0.08, 0.14)))

    # -- key ----------------------------------------------------------------
    widths = [22.0 + len(t) * 5.3 for _, t in LEGEND]
    cursor = 450.0 - (sum(widths) + 16.0 * (len(LEGEND) - 1)) / 2.0
    for (tone, text), width in zip(LEGEND, widths):
        base.append('<rect x="%s" y="%s" width="9" height="9" rx="2" fill="%s"/>'
                    % (f(cursor), LEGEND_Y - 8, p[tone]))
        base.append('<text x="%s" y="%s" font-family="%s" font-size="9.5" '
                    'fill="%s">%s</text>'
                    % (f(cursor + 14), LEGEND_Y, SANS, p["faint"], esc(text)))
        cursor += width + 16.0

    # Work still running has no right edge to draw, so it fades into the future.
    # One gradient per lane, pinned in user space at today, padding left of it.
    gradients = []
    for tone in ("yellow", "soft", "blue", "green"):
        gradients.append(
            '<linearGradient id="run-%s" gradientUnits="userSpaceOnUse" '
            'x1="%s" y1="0" x2="%s" y2="0">\n'
            '  <stop offset="0" stop-color="%s" stop-opacity="%s"/>\n'
            '  <stop offset="1" stop-color="%s" stop-opacity="0"/>\n'
            '</linearGradient>'
            % (tone, f(x_of(NOW) - 24), f(x_of(NOW)), p[TONE[tone]],
               "0.5" if tone == "soft" else "1", p[TONE[tone]]))

    wipe = ('<clipPath id="wipe"><rect x="%s" y="0" width="0" height="%d">\n'
            '  <animate attributeName="width" dur="%gs" fill="freeze" '
            'calcMode="linear"\n'
            '           values="0;0;%s;%s" keyTimes="0;%s;%s;1"/>\n'
            '</rect></clipPath>'
            % (f(X0 - 1), H, RUN, f(X1 - X0 + 3), f(X1 - X0 + 3),
               f(PLAY_FROM / RUN), f(PLAY_TO / RUN)))

    # The playhead is the one thing that should not survive the reveal: parked
    # at the right-hand edge it would read as a border. It leaves when it lands.
    play = ('<g opacity="0">\n'
            '  <animateTransform attributeName="transform" type="translate" '
            'dur="%gs" fill="freeze" calcMode="linear"\n'
            '                    values="0 0;0 0;%s 0;%s 0" keyTimes="0;%s;%s;1"/>\n'
            '  <animate attributeName="opacity" dur="%gs" fill="freeze" '
            'values="0;0;1;1;0;0" keyTimes="0;%s;%s;%s;%s;1"/>\n'
            '  <line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.5"/>\n'
            '  <circle cx="%s" cy="%s" r="3.2" fill="%s"/>\n'
            '</g>'
            % (RUN, f(X1 - X0), f(X1 - X0),
               f(PLAY_FROM / RUN), f(PLAY_TO / RUN), RUN,
               f(PLAY_FROM / RUN), f((PLAY_FROM + 0.12) / RUN),
               f((PLAY_TO - 0.15) / RUN), f((PLAY_TO + 0.35) / RUN),
               f(X0), GRID_TOP - 6, f(X0), GRID_BOTTOM + 6, p["accent"],
               f(X0), GRID_BOTTOM + 10, p["accent"]))

    return """<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img"
     aria-label="Two threads, one instinct. A panel covering 2018 to 2026: four and a half years in production, three companies, ten peer-reviewed papers, 185 citations, h-index 4. On one timeline, a four-year B.Sc. in Computer Science and Engineering at Daffodil International University with a CGPA of 3.83 and an Erasmus+ exchange semester at Adam Mickiewicz University in Poznan; applied machine learning research running from 2020 to the present alongside peer review for four journals and three conferences; and industry work moving from Java and GraphQL at BJIT Group under Japanese review standards, to Spring Boot and Oracle on customs compliance at REVE Systems, to .NET 9, gRPC and Kubernetes at Akij iBOS leading a team of ten, with open work carried on in his own time. Marked along the way: an IEEE Best Paper Award in 2020 and taking technical lead of ten engineers in 2024.">
  <title>Two threads, one instinct &#8212; eight years of engineering and research</title>
  <defs>
%s
%s
  </defs>

  <rect x="0.5" y="0.5" width="%s" height="%s" rx="10" fill="%s" stroke="%s"/>

%s

  <g clip-path="url(#wipe)">
%s
  </g>

%s

%s
</svg>
""" % (W, H, W, H, indent(gradients), indent([wipe]), W - 1, H - 1, p["bg"],
       p["border"], indent(base), indent(revealed, "    "), indent(labels),
       indent([play]))


# =============================================================== three rooms ==
#
# The timeline says when. This says where it was actually learned, which is the
# part a list of employers never carries. Each room refused to let something
# through, and the refusal is the lesson.

R_W, R_H = 900, 300
R_COLS = [24.0, 316.0, 608.0]
R_COL_W = 268.0

ROOMS = [
    ("A Japanese review process", "BJIT Group, 2022–2023",
     ["Every change read by people who would not let it",
      "through for reasons I had never thought to check."],
     ["The reviewer is a user of your code, and the",
      "most expensive one to disappoint."]),
    ("A government office", "REVE Systems, 2023–2024",
     ["Customs compliance for exporters who would be",
      "audited on whatever the system printed."],
     ["Correctness is not a quality you add later.",
      "On some systems it is the entire product."]),
    ("An empty repository", "Akij iBOS, 2024 to now",
     ["No prior art, ten engineers waiting, and three",
      "clients arriving before the second release."],
     ["Architecture is only the decisions that are",
      "expensive to undo. Make those ones slowly."]),
]


def rooms(theme):
    p = PALETTES[theme]
    out = []

    out.append('<text x="24" y="34" font-family="%s" font-size="15" '
               'font-weight="700" fill="%s">Three rooms</text>' % (SANS, p["fg"]))
    out.append('<text x="24" y="54" font-family="%s" font-size="10.5" fill="%s">'
               'Nobody handed me this. What I know about building software I learned '
               'in three places that disagreed with each other.</text>'
               % (SANS, p["faint"]))
    out.append('<text x="876" y="34" text-anchor="end" font-family="%s" '
               'font-size="10.5" fill="%s">2022 to now</text>' % (MONO, p["faint"]))
    out.append('<line x1="24" y1="72" x2="876" y2="72" stroke="%s" stroke-width="1"/>'
               % p["border"])

    for i, (name, where, constraint, lesson) in enumerate(ROOMS):
        x = R_COLS[i]
        t0 = 0.55 + i * 1.20
        if i:
            out.append('<line x1="%s" y1="92" x2="%s" y2="286" stroke="%s" '
                       'stroke-width="1"/>' % (f(x - 16), f(x - 16), p["rule"]))

        out.append('<g opacity="0">%s\n'
                   '  <text x="%s" y="104" font-family="%s" font-size="11" '
                   'font-weight="700" letter-spacing="1.4" fill="%s">%02d</text>\n'
                   '  <text x="%s" y="128" font-family="%s" font-size="13.5" '
                   'font-weight="700" fill="%s">%s</text>\n'
                   '  <text x="%s" y="144" font-family="%s" font-size="9.5" '
                   'fill="%s">%s</text>\n'
                   '  <rect x="%s" y="156" width="36" height="2" rx="1" fill="%s"/>\n'
                   '</g>'
                   % (fade(t0, 0.14), f(x), MONO, p["accent"], i + 1,
                      f(x), SANS, p["fg"], esc(name),
                      f(x), SANS, p["faint"], esc(where),
                      f(x), p["accent"]))

        for k, (label, lines, colour, base_y) in enumerate((
                ("What it would not allow", constraint, p["muted"], 184.0),
                ("What that taught", lesson, p["fg"], 246.0))):
            block = ['<text x="%s" y="%s" font-family="%s" font-size="8.5" '
                     'font-weight="700" letter-spacing="1.1" fill="%s">%s</text>'
                     % (f(x), f(base_y), SANS, p["faint"], esc(label.upper()))]
            for n, line in enumerate(lines):
                block.append('<text x="%s" y="%s" font-family="%s" font-size="10.5" '
                             'fill="%s">%s</text>'
                             % (f(x), f(base_y + 18 + n * 15), SANS, colour,
                                esc(line)))
            out.append('<g opacity="0">%s\n%s\n</g>'
                       % (fade(t0 + 0.30 + k * 0.30, 0.14), indent(block)))

    return """<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img"
     aria-label="Three rooms where the work was learned. One, a Japanese review process at BJIT Group between 2022 and 2023: every change was read by people who would not let it through for reasons the author had never thought to check, which taught that the reviewer is a user of your code and the most expensive one to disappoint. Two, a government office at REVE Systems between 2023 and 2024: customs compliance for exporters who would be audited on whatever the system printed, which taught that correctness is not a quality you add later and on some systems it is the entire product. Three, an empty repository at Akij iBOS from 2024 to now: no prior art, ten engineers waiting and three clients arriving before the second release, which taught that architecture is only the decisions that are expensive to undo, so those ones should be made slowly.">
  <title>Three rooms &#8212; where the job was actually learned</title>

  <rect x="0.5" y="0.5" width="%s" height="%s" rx="10" fill="%s" stroke="%s"/>

%s
</svg>
""" % (R_W, R_H, R_W, R_H, R_W - 1, R_H - 1, p["bg"], p["border"], indent(out))


# ============================================================ measured panel ==
#
# The only panel here that nobody wrote by hand. Every figure is read out of
# assets/data/github.json, which assets/fetch.py pulls from the GitHub API.
#
# Two methodology calls worth defending, because both change the answer:
#
#   Repositories, not bytes. Jupyter notebooks store their rendered output in
#   the file, so 83% of the account's bytes are one notebook's plots. Counting
#   repositories by primary language gives Java 24 to C# 7, which is the true
#   shape; counting bytes gives Jupyter 84%, which is an artefact.
#
#   Public only, and said out loud. Company work sits in private repositories
#   and is absent from all of this. The 2022 figure is four commits for exactly
#   that reason, and a panel claiming to measure should say so rather than crop.

M_W, M_H = 900, 464
M_SPLIT = 486.0
M_LEFT, M_RIGHT = 24.0, 506.0
M_PLOT_X0, M_PLOT_X1 = 62.0, 466.0   # column chart, right of the value gutter
M_BAR_W, M_BAR_GAP = 24.0, 4.0       # one column per series, side by side
M_BASE, M_TOP = 342.0, 196.0         # column chart floor and ceiling
M_BAR_Y, M_BAR_H = 200.0, 24.0       # language rows


def axis_ceiling(value, divisions=4):
    """Round a maximum up to something a gridline can be labelled with."""
    for step in (10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000):
        if step * divisions >= value:
            return step * divisions, step
    return value, value / float(divisions)

LANG_TONE = {"C#": "blue", "TypeScript": "purple", "Java": "orange",
             "JavaScript": "yellow", "Python": "green", "TeX": "faint",
             "Jupyter Notebook": "yellow", "HTML": "faint", "Other": "faint"}
LANG_ROWS = 6


def snapshot():
    path = os.path.join(HERE, "data", "github.json")
    if not os.path.exists(path):
        raise SystemExit("missing %s — run `python assets/fetch.py` first" % path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def thousands(n):
    return "{:,}".format(int(n))


def grow_up(x, w, height, colour, t0, rx=3, floor=None):
    """A column that rises out of its floor instead of appearing whole."""
    floor = M_BASE if floor is None else floor
    kt = ";".join(f(k / RUN) for k in (0.0, t0, t0 + 0.55, RUN))
    return ('<rect x="%s" y="%s" width="%s" height="0" rx="%s" fill="%s">\n'
            '  <animate attributeName="height" dur="%gs" fill="freeze"'
            ' values="0;0;%s;%s" keyTimes="%s"/>\n'
            '  <animate attributeName="y" dur="%gs" fill="freeze"'
            ' values="%s;%s;%s;%s" keyTimes="%s"/>\n'
            '</rect>'
            % (f(x), f(floor), f(w), rx, colour,
               RUN, f(height), f(height), kt,
               RUN, f(floor), f(floor), f(floor - height), f(floor - height), kt))


def grow_right(x, y, width, height, colour, t0, rx=3):
    kt = ";".join(f(k / RUN) for k in (0.0, t0, t0 + 0.55, RUN))
    return ('<rect x="%s" y="%s" width="0" height="%s" rx="%s" fill="%s">\n'
            '  <animate attributeName="width" dur="%gs" fill="freeze"'
            ' values="0;0;%s;%s" keyTimes="%s"/>\n'
            '</rect>'
            % (f(x), f(y), f(height), rx, colour, RUN, f(width), f(width), kt))


def measured(theme):
    p = PALETTES[theme]
    d = snapshot()
    out = []

    years = sorted(d["commits_by_year"])
    commits = [d["commits_by_year"][y]["commits"] for y in years]
    total_commits = sum(commits)
    total_repos = d["repositories_touched"]

    # Ranked by commits, not by how many repositories were started. Started
    # things are cheap; this is the measure that puts the day job in the chart.
    ranked = sorted(d["commits_by_language"].items(),
                    key=lambda kv: -kv[1]["commits"])
    rows, tail = ranked[:LANG_ROWS], ranked[LANG_ROWS:]
    if tail:
        rows = rows + [("Other", {
            "commits": sum(v["commits"] for _, v in tail),
            "repositories": sum(v["repositories"] for _, v in tail),
        })]
    noisy = d["byte_share_top_language"]
    # What the other ranking would have said, quoted from the same data so the
    # note stays true the next time fetch.py runs.
    by_repo = sorted(d["commits_by_language"].items(),
                     key=lambda kv: -kv[1]["repositories"])[:2]
    by_repo_count = " to ".join("%s %d" % (k, v["repositories"])
                                for k, v in by_repo)
    org_from = next(y for y in years if d["commits_by_year"][y]["organisation"])
    missing = d["unattributed_by_year"]
    missing_total = sum(missing.values())
    org_total = sum(d["commits_by_year"][y]["organisation"] for y in years)

    nice = datetime.strptime(d["generated"], "%Y-%m-%d").strftime("%d %B %Y")

    # -- header -------------------------------------------------------------
    out.append('<text x="24" y="34" font-family="%s" font-size="15" '
               'font-weight="700" fill="%s">Public work, measured</text>'
               % (SANS, p["fg"]))
    out.append('<text x="24" y="54" font-family="%s" font-size="10.5" fill="%s">'
               'Nothing on this panel was typed by hand. Every figure is read '
               'straight from the GitHub API on %s.</text>'
               % (SANS, p["faint"], esc(nice)))
    out.append('<text x="876" y="34" text-anchor="end" font-family="%s" '
               'font-size="10.5" fill="%s">gh api · %s</text>'
               % (MONO, p["faint"], esc(d["login"])))
    out.append('<line x1="24" y1="72" x2="876" y2="72" stroke="%s" '
               'stroke-width="1"/>' % p["border"])

    # -- standing figures ---------------------------------------------------
    stats = [(thousands(total_commits), "commits since %s" % years[0]),
             (thousands(org_total), "in organisation repos"),
             (thousands(missing_total), "authored, not counted"),
             (str(total_repos), "repositories touched"),
             (str(len(d["commits_by_language"])), "languages")]
    cell = 852.0 / len(stats)
    for i, (value, label) in enumerate(stats):
        cx = 24.0 + cell * (i + 0.5)
        if i:
            out.append('<line x1="%s" y1="88" x2="%s" y2="132" stroke="%s" '
                       'stroke-width="1"/>'
                       % (f(24.0 + cell * i), f(24.0 + cell * i), p["rule"]))
        out.append('<g opacity="0">%s\n'
                   '  <text x="%s" y="112" text-anchor="middle" font-family="%s" '
                   'font-size="18" font-weight="700" fill="%s">%s</text>\n'
                   '  <text x="%s" y="126" text-anchor="middle" font-family="%s" '
                   'font-size="9" letter-spacing="0.4" fill="%s">%s</text>\n'
                   '</g>'
                   % (fade(0.30 + i * 0.09, 0.14), f(cx), MONO, p["fg"], esc(value),
                      f(cx), SANS, p["faint"], esc(label.upper())))
    out.append('<line x1="24" y1="148" x2="876" y2="148" stroke="%s" '
               'stroke-width="1"/>' % p["border"])
    out.append('<line x1="%s" y1="164" x2="%s" y2="380" stroke="%s" '
               'stroke-width="1"/>' % (f(M_SPLIT), f(M_SPLIT), p["rule"]))

    # -- commits per year ---------------------------------------------------
    out.append('<text x="%s" y="176" font-family="%s" font-size="9" '
               'font-weight="700" letter-spacing="1.1" fill="%s">COMMITS PER YEAR'
               '</text>' % (f(M_LEFT), SANS, p["faint"]))

    # Two series, because "where are the organisation commits" is the first
    # question this chart should answer rather than quietly fold into a total.
    cursor = M_PLOT_X1
    for tone, text in (("blue", "organisation"), ("green", "own")):
        width = 11.0 + len(text) * 4.7
        cursor -= width
        out.append('<rect x="%s" y="170" width="8" height="8" rx="2" fill="%s"/>'
                   % (f(cursor), p[tone]))
        out.append('<text x="%s" y="177" font-family="%s" font-size="9" fill="%s">'
                   '%s</text>' % (f(cursor + 11), SANS, p["faint"], esc(text)))
        cursor -= 10.0

    # A column chart with no quantitative reference is a sketch. The range here
    # runs 4 to 1,785, so the short years are read off the label and the tall
    # ones off the gridlines; both need to be there.
    ceiling, step = axis_ceiling(max(commits))
    scale = (M_BASE - M_TOP) / float(ceiling)
    value = 0
    while value <= ceiling:
        gy = M_BASE - value * scale
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                   'stroke-width="1"%s/>'
                   % (f(M_PLOT_X0), f(gy), f(M_PLOT_X1), f(gy),
                      p["border"] if not value else p["rule"],
                      '' if not value else ' stroke-dasharray="2 4"'))
        out.append('<text x="%s" y="%s" text-anchor="end" font-family="%s" '
                   'font-size="8.5" fill="%s">%s</text>'
                   % (f(M_PLOT_X0 - 8), f(gy + 3), MONO, p["faint"],
                      esc(thousands(value))))
        value += step

    # Grouped rather than stacked: the two series answer different questions and
    # a reader should be able to compare them directly instead of subtracting.
    # Positions stay fixed even when a series is zero, so the arrival of
    # organisation work shows up without a word of explanation.
    span = (M_PLOT_X1 - M_PLOT_X0) / len(years)
    group = M_BAR_W * 2 + M_BAR_GAP
    for i, year in enumerate(years):
        row = d["commits_by_year"][year]
        cx = M_PLOT_X0 + span * (i + 0.5)
        t0 = 0.90 + i * 0.16
        for k, (key, tone) in enumerate((("own", "green"),
                                         ("organisation", "blue"))):
            n = row[key]
            if not n:
                continue
            bx = cx - group / 2.0 + k * (M_BAR_W + M_BAR_GAP)
            height = max(n * scale, 1.5)
            out.append(grow_up(bx, M_BAR_W, height, p[tone], t0 + k * 0.10))
            out.append('<text x="%s" y="%s" text-anchor="middle" '
                       'font-family="%s" font-size="8.5" font-weight="700" '
                       'fill="%s" opacity="0">%s%s</text>'
                       % (f(bx + M_BAR_W / 2.0), f(M_BASE - height - 6), MONO,
                          p["fg"], esc(thousands(n)),
                          fade(t0 + k * 0.10 + 0.6, 0.12)))
        out.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                   'font-size="9.5" fill="%s">%s</text>'
                   % (f(cx), f(M_BASE + 18), MONO, p["faint"], esc(year)))
    out.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
               'font-size="8.5" fill="%s">to %s</text>'
               % (f(M_PLOT_X0 + span * (len(years) - 0.5)), f(M_BASE + 32), SANS,
                  p["faint"], esc(d["through_month"])))

    # -- repositories by primary language -----------------------------------
    out.append('<text x="%s" y="176" font-family="%s" font-size="9" '
               'font-weight="700" letter-spacing="1.1" fill="%s">'
               'COMMITS BY LANGUAGE OF THE REPOSITORY</text>'
               % (f(M_RIGHT), SANS, p["faint"]))

    bar_x, bar_w = M_RIGHT + 128.0, 200.0
    repo_x = M_RIGHT + 120.0
    for label, x, anchor in (("REPOS", repo_x, "end"), ("COMMITS", 876, "end")):
        out.append('<text x="%s" y="192" text-anchor="%s" font-family="%s" '
                   'font-size="8" letter-spacing="0.8" fill="%s">%s</text>'
                   % (f(x), anchor, SANS, p["faint"], label))

    widest = max(v["commits"] for _, v in rows)
    for i, (lang, v) in enumerate(rows):
        y = M_BAR_Y + i * M_BAR_H
        t0 = 2.25 + i * 0.14
        out.append('<text x="%s" y="%s" font-family="%s" font-size="10" '
                   'fill="%s" opacity="0">%s%s</text>'
                   % (f(M_RIGHT), f(y + 11), SANS, p["muted"], esc(lang),
                      fade(t0, 0.12)))
        out.append('<text x="%s" y="%s" text-anchor="end" font-family="%s" '
                   'font-size="9.5" fill="%s" opacity="0">%d%s</text>'
                   % (f(repo_x), f(y + 11), MONO, p["faint"], v["repositories"],
                      fade(t0, 0.12)))
        out.append(grow_right(bar_x, y + 3,
                              (v["commits"] / float(widest)) * bar_w, 12,
                              p[LANG_TONE.get(lang, "faint")], t0))
        out.append('<text x="876" y="%s" text-anchor="end" font-family="%s" '
                   'font-size="10" font-weight="700" fill="%s" opacity="0">%s%s</text>'
                   % (f(y + 11), MONO, p["fg"], esc(thousands(v["commits"])),
                      fade(t0 + 0.5, 0.12)))

    # -- what the numbers do not cover --------------------------------------
    lines = [
        "Commits include private organisation repositories from %s, when the "
        "current employer's work moved onto GitHub. Counts only: no repository "
        "name, description or content is read." % org_from,
        "GitHub attributes a commit only when its author address is verified on "
        "the account. %s here are not, having been written from employer laptops "
        "under employer addresses: %s."
        % (thousands(missing_total),
           ", ".join("%s in %s" % (thousands(n), y)
                     for y, n in sorted(missing.items()) if n)),
        "Those are counted in the figure above but not in the chart, which shows "
        "what GitHub itself reports. 2022 is genuinely four: that year's work "
        "never reached GitHub at all.",
        # One %-format runs on this string, so a literal percent sign is %%.
        "Ranked by commits rather than by repositories started, which would read "
        "%s, or by bytes, where %s alone takes %d%% because notebooks store "
        "their own rendered output." % (by_repo_count, esc(noisy["language"]),
                                        noisy["percent"]),
    ]
    out.append('<g opacity="0">%s\n%s\n</g>'
               % (fade(3.90),
                  indent(['<text x="24" y="%s" font-family="%s" font-size="9.5" '
                          'fill="%s">%s</text>' % (400 + n * 15, SANS, p["faint"], t)
                          for n, t in enumerate(lines)])))

    return """<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img"
     aria-label="%s">
  <title>Public work, measured &#8212; read from the GitHub API</title>

  <rect x="0.5" y="0.5" width="%s" height="%s" rx="10" fill="%s" stroke="%s"/>

%s
</svg>
""" % (M_W, M_H, M_W, M_H,
       esc("A panel of figures read from the GitHub API on %s for the account %s. "
           "%s commits since %s, of which %s are in private organisation "
           "repositories, across %d repositories committed to, %d of them public, "
           "in %d languages. Commits per year, split into own and organisation "
           "repositories, run %s. Commits by the primary language of the "
           "repository, with the number of repositories in brackets, run %s. "
           "Commits include private organisation repositories from %s, when the "
           "current employer's work moved onto GitHub; only counts are read, never "
           "a repository name, description or content. Code written for earlier "
           "employers never lived on this account, which is why 2022, a full year "
           "of Java in production, reads as four commits. Languages are ranked by "
           "commits rather than by how many repositories were started, which would "
           "read %s, and not by bytes, where notebooks alone take "
           "most of the account because they store their own rendered output."
           % (nice, d["login"], thousands(total_commits), years[0],
              thousands(org_total), total_repos, d["public_repositories"],
              len(d["commits_by_language"]),
              ", ".join("%s %s own and %s organisation"
                        % (y, thousands(d["commits_by_year"][y]["own"]),
                           thousands(d["commits_by_year"][y]["organisation"]))
                        for y in years),
              ", ".join("%s %s (%d)" % (k, thousands(v["commits"]),
                                        v["repositories"]) for k, v in rows),
              org_from, by_repo_count)),
       M_W - 1, M_H - 1, p["bg"], p["border"], indent(out))


def main():
    for theme in ("dark", "light"):
        for name, fn in (("career", career), ("rooms", rooms),
                         ("measured", measured)):
            path = os.path.join(HERE, "%s-%s.svg" % (name, theme))
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(fn(theme))
            print("wrote %-20s %6d bytes" % (os.path.basename(path),
                                             os.path.getsize(path)))


if __name__ == "__main__":
    main()
