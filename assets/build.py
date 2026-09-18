#!/usr/bin/env python3
"""Generates the animated SVG header used by README.md.

    python assets/build.py

Pure SVG + SMIL. No JavaScript, no web fonts, no network calls at render time:
GitHub proxies these through camo, where scripts never execute but declarative
animation does. Both themes come out of one palette swap and are selected in the
README with <picture media="(prefers-color-scheme: ...)">.

Emits `career-dark.svg` and `career-light.svg` — a composed panel rather than a
bare chart: a header lockup with a year readout that ticks through the stack
actually in hand at the time, a band of standing figures, then eight years of
education, research and three employers on one axis. Work still running does not
get a hard right edge; it fades into the future it has not finished yet.

There were charts of the platform at work as well, and they were good, but the
page they sat on is meant to be about a person rather than a portfolio, so they
came out again. `git log --diff-filter=D assets/` has them if they are wanted.
"""

import os

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

LOOP = 10.0
PLAY_FROM, PLAY_TO = 0.35, 5.60      # the playhead sweep
DIM, RESET = 9.20, 9.68              # hold, then dim, then start over


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    """Short, stable number formatting — keeps the emitted SVG diff-friendly."""
    return ("%.3f" % float(v)).rstrip("0").rstrip(".") or "0"


def indent(lines, pad="  "):
    return "\n".join(pad + l.replace("\n", "\n" + pad) for l in lines)


def fade(appear, rise=0.16):
    """Opacity track: hidden, fades in at `appear`, dims out with the cycle."""
    keys = [0.0, appear, appear + rise, DIM, RESET, LOOP]
    return ('<animate attributeName="opacity" dur="%gs" repeatCount="indefinite"'
            ' values="0;0;1;1;0;0" keyTimes="%s"/>'
            % (LOOP, ";".join(f(k / LOOP) for k in keys)))


def steps(frames, x, y, size, colour, font=MONO, anchor="end", weight="700",
          spacing=None):
    """A readout rendered as N overlapping texts, each visible for its slice.

    SMIL cannot animate text content, so a ticker is N elements taking turns.
    """
    out = []
    for start, stop, label in frames:
        if stop <= start:
            continue
        out.append('<text x="%s" y="%s" text-anchor="%s" font-family="%s" '
                   'font-size="%s" font-weight="%s"%s fill="%s" opacity="0">%s'
                   '<animate attributeName="opacity" dur="%gs" '
                   'repeatCount="indefinite" calcMode="discrete" values="0;1;0" '
                   'keyTimes="0;%s;%s"/></text>'
                   % (f(x), f(y), anchor, font, size, weight,
                      '' if spacing is None else ' letter-spacing="%s"' % spacing,
                      colour, esc(label), LOOP,
                      f(start / LOOP), f(min(stop, DIM) / LOOP)))
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
                'Production engineering and applied research in parallel since 2018 '
                '— Java, .NET and Python, three companies, ten papers.</text>'
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
            '  <animate attributeName="width" dur="%gs" repeatCount="indefinite" '
            'calcMode="linear"\n'
            '           values="0;0;%s;%s;0;0" keyTimes="0;%s;%s;%s;%s;1"/>\n'
            '</rect></clipPath>'
            % (f(X0 - 1), H, LOOP, f(X1 - X0 + 3), f(X1 - X0 + 3),
               f(PLAY_FROM / LOOP), f(PLAY_TO / LOOP),
               f(DIM / LOOP), f((DIM + 0.02) / LOOP)))

    play = ('<g opacity="0">\n'
            '  <animateTransform attributeName="transform" type="translate" '
            'dur="%gs" repeatCount="indefinite" calcMode="linear"\n'
            '                    values="0 0;0 0;%s 0;%s 0" keyTimes="0;%s;%s;1"/>\n'
            '  <animate attributeName="opacity" dur="%gs" repeatCount="indefinite" '
            'values="0;0;1;1;0;0" keyTimes="0;%s;%s;%s;%s;1"/>\n'
            '  <line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.5"/>\n'
            '  <circle cx="%s" cy="%s" r="3.2" fill="%s"/>\n'
            '</g>'
            % (LOOP, f(X1 - X0), f(X1 - X0),
               f(PLAY_FROM / LOOP), f(PLAY_TO / LOOP), LOOP,
               f(PLAY_FROM / LOOP), f((PLAY_FROM + 0.12) / LOOP),
               f((PLAY_TO - 0.2) / LOOP), f((PLAY_TO + 0.25) / LOOP),
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


def main():
    for theme in ("dark", "light"):
        path = os.path.join(HERE, "career-%s.svg" % theme)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(career(theme))
        print("wrote %-20s %6d bytes" % (os.path.basename(path),
                                         os.path.getsize(path)))


if __name__ == "__main__":
    main()
