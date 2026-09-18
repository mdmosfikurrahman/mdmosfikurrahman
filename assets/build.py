#!/usr/bin/env python3
"""Generates the animated SVG assets embedded in README.md.

    python assets/build.py

Pure SVG + SMIL. No JavaScript, no web fonts, no network calls at render time:
GitHub proxies these through camo, where scripts never execute but declarative
animation does. Both themes come out of one palette swap and are selected in the
README with <picture media="(prefers-color-scheme: ...)">.

Three charts, one visual grammar — an axis, labelled rows, a playhead that
sweeps left to right, and everything revealing in the order it really happened:

    career-*.svg     eight years across education, research and three companies
    trace-*.svg      one search request on the current platform, span by span
    topology-*.svg   that same platform with the clock taken out

The career chart is the wide shot and the other two are the close-up, which is
the order the README reads them in.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

MONO = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")
SANS = ("ui-sans-serif, -apple-system, 'Segoe UI', Inter, Roboto, "
        "'Helvetica Neue', Arial, sans-serif")

PALETTES = {
    "dark": dict(
        bg="#0d1117", card="#161b22", card_alt="#1c2128", border="#30363d",
        stripe="#161b22", fg="#e6edf3", muted="#8b949e", faint="#6e7681",
        blue="#58a6ff", cyan="#56d4dd", green="#3fb950", purple="#bc8cff",
        yellow="#d29922", orange="#f0883e", wire="#30363d", accent="#58a6ff",
    ),
    "light": dict(
        bg="#ffffff", card="#f6f8fa", card_alt="#eaeef2", border="#d0d7de",
        stripe="#f6f8fa", fg="#1f2328", muted="#59636e", faint="#818b98",
        blue="#0969da", cyan="#1b7c83", green="#1a7f37", purple="#8250df",
        yellow="#9a6700", orange="#bc4c00", wire="#d0d7de", accent="#0969da",
    ),
}

# Every chart runs on the same clock, so two of them on one page stay in step.
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


def steps(frames, x, y, size, colour, font=MONO, anchor="end", weight="700"):
    """One readout rendered as N overlapping texts, each visible for its slice.

    SMIL cannot animate text content, so a ticker is N elements taking turns.
    """
    out = []
    for i, (start, stop, label) in enumerate(frames):
        if stop <= start:
            continue
        out.append('<text x="%s" y="%s" text-anchor="%s" font-family="%s" '
                   'font-size="%s" font-weight="%s" fill="%s" opacity="0">%s'
                   '<animate attributeName="opacity" dur="%gs" '
                   'repeatCount="indefinite" calcMode="discrete" values="0;1;0" '
                   'keyTimes="0;%s;%s"/></text>'
                   % (f(x), f(y), anchor, font, size, weight, colour, esc(label),
                      LOOP, f(start / LOOP), f(min(stop, DIM) / LOOP)))
    return out


def playhead(x0, x1, top, bottom, colour):
    return ('<g opacity="0">\n'
            '  <animateTransform attributeName="transform" type="translate" '
            'dur="%gs" repeatCount="indefinite" calcMode="linear"\n'
            '                    values="0 0;0 0;%s 0;%s 0" keyTimes="0;%s;%s;1"/>\n'
            '  <animate attributeName="opacity" dur="%gs" repeatCount="indefinite" '
            'values="0;0;1;1;0;0" keyTimes="0;%s;%s;%s;%s;1"/>\n'
            '  <line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.5"/>\n'
            '  <circle cx="%s" cy="%s" r="3.2" fill="%s"/>\n'
            '</g>'
            % (LOOP, f(x1 - x0), f(x1 - x0),
               f(PLAY_FROM / LOOP), f(PLAY_TO / LOOP), LOOP,
               f(PLAY_FROM / LOOP), f((PLAY_FROM + 0.12) / LOOP),
               f((PLAY_TO - 0.2) / LOOP), f((PLAY_TO + 0.25) / LOOP),
               f(x0), f(top - 6), f(x0), f(bottom + 6), colour,
               f(x0), f(bottom + 10), colour))


def wipe(x0, width, height):
    """One clip does the work of N reveals — rows appear in their true order."""
    return ('<clipPath id="wipe"><rect x="%s" y="0" width="0" height="%d">\n'
            '  <animate attributeName="width" dur="%gs" repeatCount="indefinite" '
            'calcMode="linear"\n'
            '           values="0;0;%s;%s;0;0" keyTimes="0;%s;%s;%s;%s;1"/>\n'
            '</rect></clipPath>'
            % (f(x0 - 1), height, LOOP, f(width + 3), f(width + 3),
               f(PLAY_FROM / LOOP), f(PLAY_TO / LOOP),
               f(DIM / LOOP), f((DIM + 0.02) / LOOP)))


def document(w, h, aria, title, defs, layers, pal):
    return """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="%d" height="%d" viewBox="0 0 %d %d" role="img"
     aria-label="%s">
  <title>%s</title>
  <defs>
%s
  </defs>

  <rect x="0.5" y="0.5" width="%s" height="%s" rx="10" fill="%s" stroke="%s"/>

%s
</svg>
""" % (w, h, w, h, aria, title, indent(defs), w - 1, h - 1, pal["bg"],
       pal["border"], "\n\n".join(layers))


# ============================================================ career timeline ==
#
# The wide shot. Two threads — production engineering and applied research — have
# run side by side since 2018, and the colour key is the honest answer to "which
# stack is he": Java for two employers, .NET for the third, Python throughout the
# research, and his own builds in both.

C_W, C_H = 900, 424
C_X0, C_X1 = 258.0, 876.0
C_FROM, C_TO = 2018.0, 2027.0
C_PX = (C_X1 - C_X0) / (C_TO - C_FROM)
C_ROW_Y, C_ROW_H = 96.0, 34.0
NOW = 2026.72

#      headline                                detail                                        from      to      tone
CAREER = [
    ("B.Sc. Computer Science & Engineering", "Daffodil International University · CGPA 3.83", 2018.00, 2021.98, "purple"),
    ("Erasmus+ exchange semester",           "Adam Mickiewicz University, Poznań",        2021.10, 2021.60, "purple"),
    ("Applied ML research",                  "10 papers · 185 citations · h-index 4",          2020.00, NOW,     "yellow"),
    ("Peer review & invited talks",          "4 journals · 3 conferences · IEEE speaker",      2022.00, NOW,     "hatch"),
    ("BJIT Group — GraphQL BFF",             "Java · GraphQL · Rakuten, Denka",                2022.25, 2023.50, "orange"),
    ("REVE Systems — NBR Customs Bond",      "Spring Boot · Oracle · OAuth2",                  2023.50, 2024.83, "orange"),
    ("Akij iBOS — Travilo platform",         ".NET 9 · gRPC · Kubernetes · SQL Server",        2024.83, NOW,     "blue"),
    ("Open source & side builds",            "Flavian · Task-Flow-Manager · BloomERP",         2025.42, NOW,     "green"),
]

C_MARKERS = [(2020.95, "start", "IEEE Best Paper Award"),
             (2024.85, "end",   "Team lead · 10 engineers")]

# What was actually in his hands that year — the readout, ticking with the sweep.
C_YEARS = [(2018, "undergraduate · CSE"), (2019, "undergraduate · CSE"),
           (2020, "Python · applied ML"), (2021, "Python · applied ML"),
           (2022, "Java · GraphQL"), (2023, "Java · Spring Boot · Oracle"),
           (2024, "Spring Boot → .NET 9"), (2025, ".NET 9 · gRPC · Kubernetes"),
           (2026, ".NET 9 · Java 21 · Next.js")]

C_LEGEND = [("purple", "Education"), ("yellow", "Research"),
            ("orange", "Java · Spring"), ("blue", ".NET"),
            ("green", "Own builds")]


def c_at(year):
    return PLAY_FROM + ((year - C_FROM) / (C_TO - C_FROM)) * (PLAY_TO - PLAY_FROM)


def c_x(year):
    return C_X0 + (year - C_FROM) * C_PX


def career(theme):
    p = PALETTES[theme]
    grid_top, grid_bottom = 84.0, 372.0
    base, revealed, labels = [], [], []

    base.append('<text x="24" y="30" font-family="%s" font-size="13.5" '
                'font-weight="700" fill="%s">Two threads, one instinct</text>'
                % (SANS, p["fg"]))
    base.append('<text x="24" y="49" font-family="%s" font-size="10.5" fill="%s">'
                'Production engineering and applied research in parallel since 2018 '
                '— Java, .NET and Python, three companies, ten papers.</text>'
                % (SANS, p["faint"]))

    frames = [(c_at(y), c_at(y + 1), str(y)) for y, _ in C_YEARS]
    base += steps(frames, 876, 38, "21", p["accent"])
    base += steps([(a, b, C_YEARS[i][1]) for i, (a, b, _) in enumerate(frames)],
                  876, 53, "10", p["faint"], font=MONO, weight="400")

    for year in range(int(C_FROM), int(C_TO)):
        gx = c_x(year)
        base.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                    'stroke-width="1" stroke-dasharray="2 4"/>'
                    % (f(gx), grid_top, f(gx), grid_bottom, p["border"]))
        base.append('<text x="%s" y="72" text-anchor="middle" font-family="%s" '
                    'font-size="9.5" fill="%s">%d</text>'
                    % (f(gx), MONO, p["faint"], year))
    base.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
                % (f(C_X0), grid_top, f(C_X0), grid_bottom, p["border"]))

    for i, (head, detail, s0, s1, tone) in enumerate(CAREER):
        top = C_ROW_Y + i * C_ROW_H
        if i % 2 == 0:
            base.append('<rect x="24" y="%s" width="852" height="%s" fill="%s" '
                        'opacity="0.55"/>' % (f(top), f(C_ROW_H - 4), p["stripe"]))

        labels.append('<text x="24" y="%s" font-family="%s" font-size="11.5" '
                      'font-weight="600" fill="%s" opacity="0">%s%s</text>'
                      % (f(top + 14), SANS, p["fg"], esc(head), fade(c_at(s0), 0.12)))
        labels.append('<text x="24" y="%s" font-family="%s" font-size="9.5" '
                      'fill="%s" opacity="0">%s%s</text>'
                      % (f(top + 27), SANS, p["faint"], esc(detail),
                         fade(c_at(s0), 0.12)))

        fill = "url(#hatch)" if tone == "hatch" else p[tone]
        revealed.append('<rect x="%s" y="%s" width="%s" height="12" rx="3" fill="%s"/>'
                        % (f(c_x(s0)), f(top + 9), f(max((s1 - s0) * C_PX, 3)), fill))

    for year, anchor, text in C_MARKERS:
        mx = c_x(year)
        revealed.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                        'stroke-width="1.2" stroke-dasharray="3 3" opacity="0.85"/>'
                        % (f(mx), grid_top - 4, f(mx), grid_bottom + 4, p["accent"]))
        labels.append('<text x="%s" y="388" text-anchor="%s" font-family="%s" '
                      'font-size="10" font-weight="600" fill="%s" opacity="0">%s%s</text>'
                      % (f(mx + (7 if anchor == "start" else -7)), anchor, SANS,
                         p["accent"], esc(text), fade(c_at(year) + 0.08, 0.14)))

    widths = [22.0 + len(t) * 5.3 for _, t in C_LEGEND]
    cursor = 450.0 - (sum(widths) + 16.0 * (len(C_LEGEND) - 1)) / 2.0
    for (tone, text), width in zip(C_LEGEND, widths):
        base.append('<rect x="%s" y="404" width="9" height="9" rx="2" fill="%s"/>'
                    % (f(cursor), p[tone]))
        base.append('<text x="%s" y="412" font-family="%s" font-size="9.5" '
                    'fill="%s">%s</text>'
                    % (f(cursor + 14), SANS, p["faint"], esc(text)))
        cursor += width + 16.0

    hatch = ('<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
             'patternTransform="rotate(45)">\n'
             '  <rect width="6" height="6" fill="%s" opacity="0.26"/>\n'
             '  <rect width="2.5" height="6" fill="%s" opacity="0.7"/>\n'
             '</pattern>' % (p["yellow"], p["yellow"]))

    return document(
        C_W, C_H,
        "Career timeline, 2018 to 2026. A B.Sc. in Computer Science and Engineering "
        "at Daffodil International University with a CGPA of 3.83, including an "
        "Erasmus+ exchange semester at Adam Mickiewicz University in Poznan. Applied "
        "machine learning research runs from 2020 to now — ten papers, 185 citations, "
        "h-index 4 — alongside peer review for four journals and three conferences. "
        "Industry work moves from GraphQL backend-for-frontend services in Java at "
        "BJIT Group, to the National Board of Revenue customs bond system in Spring "
        "Boot and Oracle at REVE Systems, to .NET 9 platform architecture at Akij iBOS "
        "leading a team of ten, with open-source and personal builds alongside.",
        "Two threads, one instinct &#8212; eight years of engineering and research",
        [hatch, wipe(C_X0, C_X1 - C_X0, C_H)],
        [indent(base),
         '  <g clip-path="url(#wipe)">\n%s\n  </g>' % indent(revealed, "    "),
         indent(labels),
         indent([playhead(C_X0, C_X1, grid_top, grid_bottom, p["accent"])])],
        p)


# =========================================================== trace waterfall ==
#
# The close-up. A search is one request that becomes eleven; the waterfall is the
# honest way to show that, because the fan-out is visible as parallelism and the
# two claims worth making are markers on a real axis.

T_W, T_H = 900, 416
T_X0, T_X1 = 224.0, 832.0
T_DUR_X = 876.0
T_SPAN = 10.5
T_PX = (T_X1 - T_X0) / T_SPAN
T_ROW_Y, T_ROW_H = 96.0, 24.0

#          label                          depth  start   end   tone
SPANS = [
    ("api-gateway",                   0,  0.00, 9.80, "blue"),
    ("reservation.SearchFlights",     1,  0.06, 9.78, "blue"),
    ("fmg.ResolvePricingRules",       2,  0.10, 0.34, "purple"),
    ("orchestrator.FanOut",           2,  0.36, 9.60, "cyan"),
    ("sabre.BargainFinderMax",        3,  0.42, 3.41, "green"),
    ("amadeus.FlightOffersSearch",    3,  0.44, 4.12, "green"),
    ("travelport.LowFareSearch",      3,  0.45, 5.06, "green"),
    ("pkfare.Shopping",               3,  0.47, 2.88, "green"),
    ("airmaster.Search",              3,  0.48, 6.72, "green"),
    ("+6 connectors",                 3,  0.50, 9.41, "hatch"),
    ("merge · rank · dedupe", 2, 3.55, 9.55, "yellow"),
    ("sse.StreamToAgent",             1,  3.62, 9.72, "orange"),
]

T_MARKERS = [(3.62, "start", "first fare on screen · 3.6 s"),
             (9.80, "end", "search complete · 9.8 s")]

TICKER = [(0.00, "0"), (3.62, "112"), (4.20, "268"), (4.90, "431"),
          (5.60, "588"), (6.40, "702"), (7.20, "815"), (8.00, "921"),
          (8.90, "1,004"), (9.72, "1,047")]


def t_at(seconds):
    return PLAY_FROM + (seconds / T_SPAN) * (PLAY_TO - PLAY_FROM)


def t_x(seconds):
    return T_X0 + seconds * T_PX


def trace(theme):
    p = PALETTES[theme]
    grid_top, grid_bottom = 82.0, 386.0
    base, revealed, labels = [], [], []

    base.append('<text x="24" y="30" font-family="%s" font-size="13.5" fill="%s">'
                '<tspan fill="%s" font-weight="700">POST</tspan>'
                '  /api/v1/flights/search</text>' % (MONO, p["fg"], p["green"]))
    base.append('<text x="24" y="49" font-family="%s" font-size="10.5" fill="%s">'
                'trace 7f3a91c1 · 12 spans · one request fanned out to eleven '
                'suppliers, streamed back as it lands</text>' % (SANS, p["faint"]))

    frames = []
    for i, (start, label) in enumerate(TICKER):
        stop = TICKER[i + 1][0] if i + 1 < len(TICKER) else T_SPAN
        frames.append((t_at(start), t_at(stop), label))
    base += steps(frames, 876, 38, "21", p["green"])
    base.append('<text x="876" y="53" text-anchor="end" font-family="%s" '
                'font-size="10" fill="%s">fares streamed</text>'
                % (SANS, p["faint"]))

    for s in range(0, 11, 2):
        gx = t_x(s)
        base.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                    'stroke-width="1" stroke-dasharray="2 4"/>'
                    % (f(gx), grid_top, f(gx), grid_bottom, p["border"]))
        base.append('<text x="%s" y="72" text-anchor="middle" font-family="%s" '
                    'font-size="9.5" fill="%s">%d s</text>'
                    % (f(gx), MONO, p["faint"], s))
    base.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
                % (f(T_X0), grid_top, f(T_X0), grid_bottom, p["border"]))

    for i, (name, depth, s0, s1, tone) in enumerate(SPANS):
        top = T_ROW_Y + i * T_ROW_H
        if i % 2 == 0:
            base.append('<rect x="24" y="%s" width="852" height="%s" fill="%s" '
                        'opacity="0.55"/>' % (f(top), f(T_ROW_H - 4), p["stripe"]))

        labels.append('<text x="%s" y="%s" font-family="%s" font-size="10" '
                      'fill="%s" opacity="0">%s%s</text>'
                      % (24 + depth * 12, f(top + 13), MONO,
                         p["faint"] if tone == "hatch" else p["muted"],
                         esc(name), fade(t_at(s0), 0.10)))
        labels.append('<text x="%s" y="%s" text-anchor="end" font-family="%s" '
                      'font-size="9.5" fill="%s" opacity="0">%.2f s%s</text>'
                      % (f(T_DUR_X), f(top + 14), MONO, p["faint"],
                         s1 - s0, fade(t_at(s1) + 0.06, 0.10)))

        fill = "url(#hatch)" if tone == "hatch" else p[tone]
        revealed.append('<rect x="%s" y="%s" width="%s" height="11" rx="3" fill="%s"/>'
                        % (f(t_x(s0)), f(top + 5), f(max((s1 - s0) * T_PX, 2)), fill))

    for s, anchor, text in T_MARKERS:
        mx = t_x(s)
        revealed.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                        'stroke-width="1.2" stroke-dasharray="3 3" opacity="0.85"/>'
                        % (f(mx), grid_top - 4, f(mx), grid_bottom + 4, p["accent"]))
        labels.append('<text x="%s" y="402" text-anchor="%s" font-family="%s" '
                      'font-size="10" font-weight="600" fill="%s" opacity="0">%s%s</text>'
                      % (f(mx + (7 if anchor == "start" else -7)), anchor, SANS,
                         p["accent"], esc(text), fade(t_at(s) + 0.08, 0.14)))

    hatch = ('<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
             'patternTransform="rotate(45)">\n'
             '  <rect width="6" height="6" fill="%s" opacity="0.28"/>\n'
             '  <rect width="2.5" height="6" fill="%s" opacity="0.75"/>\n'
             '</pattern>' % (p["green"], p["green"]))

    return document(
        T_W, T_H,
        "Distributed trace of one flight search. An API gateway span runs 9.8 "
        "seconds; inside it the reservation service resolves pricing rules in 0.24 "
        "seconds, then an orchestrator fans out in parallel to Sabre, Amadeus, "
        "Travelport, PKfare, AirMaster and six further connectors. Merging and "
        "ranking begins at 3.55 seconds, the first fare reaches the agent over "
        "Server-Sent Events at 3.6 seconds, and 1,047 fares have streamed by 9.8 "
        "seconds.",
        "One search, traced &#8212; eleven suppliers in parallel, first fare in 3.6 s",
        [hatch, wipe(T_X0, T_X1 - T_X0, T_H)],
        [indent(base),
         '  <g clip-path="url(#wipe)">\n%s\n  </g>' % indent(revealed, "    "),
         indent(labels),
         indent([playhead(T_X0, T_X1, grid_top, grid_bottom, p["accent"])])],
        p)


# ================================================================= topology ==
#
# The same platform with the clock taken out: what talks to what, and where the
# eleven parallel calls in the trace above actually come from.

P_W, P_H = 900, 306
P_LOOP = 6.0
MID = 163.0

PANELS = [("Admin Panel", "operations", 100.0),
          ("B2B Agency", "742 accounts", 163.0),
          ("B2C Web", "consumer", 226.0)]

SERVICES = ["Reservation", "Finance", "Configuration", "Notification",
            "Report", "User", "Visa", "Hotel"]

SUPPLIERS = [("Sabre", 79.0), ("Amadeus", 121.0), ("Travelport", 163.0),
             ("PKfare", 205.0), ("+7 connectors", 247.0)]

COLUMNS = [(24.0, 150.0, "Panels · Next.js"),
           (232.0, 232.0, "Platform core · .NET 9"),
           (520.0, 150.0, "Search orchestrator"),
           (730.0, 146.0, "Suppliers / GDS")]


def box(x, y, w, h, fill, stroke, rx=7):
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" '
            'stroke="%s"/>' % (f(x), f(y), f(w), f(h), rx, fill, stroke))


def flow(path_id, colour, t0, t1, reverse=False, r=3.4):
    keys = [0.0, t0, t1, P_LOOP]
    points = "1;1;0;0" if reverse else "0;0;1;1"
    op = [0.0, t0, t0 + 0.14, t1 - 0.14, t1, P_LOOP]
    return ('<circle r="%s" fill="%s" opacity="0">\n'
            '  <animateMotion dur="%gs" repeatCount="indefinite" calcMode="linear"\n'
            '                 keyTimes="%s" keyPoints="%s">\n'
            '    <mpath xlink:href="#%s" href="#%s"/>\n'
            '  </animateMotion>\n'
            '  <animate attributeName="opacity" dur="%gs" repeatCount="indefinite"\n'
            '           values="0;0;1;1;0;0" keyTimes="%s"/>\n'
            '</circle>'
            % (r, colour, P_LOOP, ";".join(f(k / P_LOOP) for k in keys), points,
               path_id, path_id, P_LOOP,
               ";".join(f(k / P_LOOP) for k in op)))


def topology(theme):
    p = PALETTES[theme]
    wires, nodes, dots = [], [], []

    nodes.append('<text x="24" y="28" font-family="%s" font-size="13" '
                 'font-weight="700" fill="%s">Platform topology</text>'
                 % (SANS, p["fg"]))
    nodes.append('<text x="876" y="28" text-anchor="end" font-family="%s" '
                 'font-size="10.5" fill="%s">gRPC fan-out → SSE stream back</text>'
                 % (MONO, p["faint"]))

    for x, w, title in COLUMNS:
        nodes.append('<text x="%s" y="50" font-family="%s" font-size="10" '
                     'font-weight="700" letter-spacing="0.9" fill="%s">%s</text>'
                     % (f(x), SANS, p["faint"], esc(title.upper())))
        nodes.append(box(x, 60, w, 206, p["card"], p["border"], 8))

    for title, sub, cy in PANELS:
        nodes.append(box(38, cy - 24, 122, 48, p["card_alt"], p["border"]))
        nodes.append('<text x="50" y="%s" font-family="%s" font-size="11.5" '
                     'font-weight="600" fill="%s">%s</text>'
                     % (f(cy - 4), SANS, p["fg"], esc(title)))
        nodes.append('<text x="50" y="%s" font-family="%s" font-size="9.5" '
                     'fill="%s">%s</text>' % (f(cy + 11), SANS, p["faint"], esc(sub)))

    for i, name in enumerate(SERVICES):
        cx, cy = 244 + (i % 2) * 108, 80 + (i // 2) * 44
        nodes.append(box(cx, cy, 104, 34, p["card_alt"], p["border"], 6))
        nodes.append('<text x="%s" y="%s" text-anchor="middle" font-family="%s" '
                     'font-size="10.5" fill="%s">%s</text>'
                     % (cx + 52, cy + 21.5, SANS, p["fg"], esc(name)))

    nodes.append('<text x="595" y="146" text-anchor="middle" font-family="%s" '
                 'font-size="12.5" font-weight="700" fill="%s">Fan-out</text>'
                 % (SANS, p["accent"]))
    for k, line in enumerate(["11 parallel gRPC calls",
                              "merge · rank · dedupe",
                              "stream as each lands"]):
        nodes.append('<text x="595" y="%s" text-anchor="middle" font-family="%s" '
                     'font-size="10.5" fill="%s">%s</text>'
                     % (170 + k * 18, SANS, p["faint"], esc(line)))

    for name, cy in SUPPLIERS:
        nodes.append(box(742, cy - 16, 122, 32, p["card_alt"], p["border"], 6))
        nodes.append('<text x="803" y="%s" text-anchor="middle" font-family="%s" '
                     'font-size="10.5" fill="%s">%s</text>'
                     % (f(cy + 3.8), SANS,
                        p["faint"] if name.startswith("+") else p["fg"], esc(name)))

    for i, (_, _, cy) in enumerate(PANELS):
        wires.append('<path id="in%d" d="M174,%s C206,%s 206,%s 232,%s" fill="none" '
                     'stroke="%s" stroke-width="1.4"/>'
                     % (i, f(cy), f(cy), f(MID), f(MID), p["wire"]))
    wires.append('<path id="core" d="M464,%s H520" fill="none" stroke="%s" '
                 'stroke-width="1.4"/>' % (f(MID), p["wire"]))
    for i, (_, cy) in enumerate(SUPPLIERS):
        wires.append('<path id="sup%d" d="M670,%s C702,%s 702,%s 730,%s" fill="none" '
                     'stroke="%s" stroke-width="1.4"/>'
                     % (i, f(MID), f(MID), f(cy), f(cy), p["wire"]))

    for i in range(len(PANELS)):
        dots.append(flow("in%d" % i, p["blue"], 0.10 + i * 0.12, 1.05 + i * 0.12))
    dots.append(flow("core", p["blue"], 1.10, 1.70))
    for i in range(len(SUPPLIERS)):
        dots.append(flow("sup%d" % i, p["blue"], 1.75 + i * 0.10, 2.60 + i * 0.10))
    for i in range(len(SUPPLIERS)):
        dots.append(flow("sup%d" % i, p["green"], 2.85 + i * 0.12, 3.70 + i * 0.12,
                         reverse=True))
    for k in range(2):
        dots.append(flow("core", p["green"], 3.55 + k * 0.30, 4.10 + k * 0.30,
                         reverse=True, r=3.0))
    for i in range(len(PANELS)):
        dots.append(flow("in%d" % i, p["green"], 4.05 + i * 0.10, 5.00 + i * 0.10,
                         reverse=True, r=3.0))

    nodes.append('<text x="450" y="292" text-anchor="middle" font-family="%s" '
                 'font-size="10" fill="%s">eight services · eleven connectors '
                 '· three white-label tenants · 96 pricing rules held as '
                 'configuration, not code</text>' % (SANS, p["faint"]))

    glow = ('<filter id="glow" x="-150%" y="-150%" width="400%" height="400%">\n'
            '  <feGaussianBlur stdDeviation="2.2" result="b"/>\n'
            '  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>\n'
            '</filter>')

    return document(
        P_W, P_H,
        "Topology of the Travilo platform. Admin, B2B agency and B2C web panels on "
        "Next.js call eight .NET 9 services — reservation, finance, configuration, "
        "notification, report, user, visa and hotel. A search orchestrator issues "
        "eleven parallel gRPC calls to Sabre, Amadeus, Travelport, PKfare and seven "
        "further connectors, then merges, ranks and streams the results back. Three "
        "white-label tenants; 96 pricing rules held as configuration rather than code.",
        "Platform topology &#8212; eight services, eleven connectors, three tenants",
        [glow],
        [indent(wires), indent(nodes),
         '  <g filter="url(#glow)">\n%s\n  </g>' % indent(dots, "    ")],
        p)


def main():
    for theme in ("dark", "light"):
        for name, fn in (("career", career), ("trace", trace),
                         ("topology", topology)):
            path = os.path.join(HERE, "%s-%s.svg" % (name, theme))
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(fn(theme))
            print("wrote %-22s %6d bytes" % (os.path.basename(path),
                                             os.path.getsize(path)))


if __name__ == "__main__":
    main()
