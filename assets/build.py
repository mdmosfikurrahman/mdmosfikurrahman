#!/usr/bin/env python3
"""Generates the animated SVG assets embedded in README.md.

    python assets/build.py

Pure SVG + SMIL. No JavaScript, no web fonts, no network calls at render time:
GitHub proxies these through camo, where scripts never execute but declarative
animation does. Both themes are emitted from one palette swap and selected in
the README with <picture media="(prefers-color-scheme: ...)">.

Emits, next to this file:

    trace-dark.svg      trace-light.svg      one search request, traced
    topology-dark.svg   topology-light.svg   the services behind that request

The two are deliberately complementary — the trace is the system in *time*,
the topology is the same system in *structure*.
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


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    """Short, stable number formatting — keeps the emitted SVG diff-friendly."""
    return ("%.3f" % float(v)).rstrip("0").rstrip(".") or "0"


def indent(lines, pad="  "):
    return "\n".join(pad + l.replace("\n", "\n" + pad) for l in lines)


# =========================================================== trace waterfall ==
#
# A search is one request that becomes eleven. The waterfall is the honest way
# to show that: the fan-out is visible as parallelism, and the two things worth
# claiming — first fare on screen, and completion — are markers on a real axis.

T_W, T_H = 900, 416
T_X0, T_X1 = 224.0, 832.0            # plot area
T_DUR_X = 876.0                      # right-aligned duration column
T_SPAN = 10.5                        # seconds of trace on the axis
PX = (T_X1 - T_X0) / T_SPAN
ROW_Y, ROW_H, BAR_H = 96.0, 24.0, 11.0

T_LOOP = 10.0                        # wall-clock seconds per cycle
T_PLAY_FROM, T_PLAY_TO = 0.35, 5.60  # when the playhead sweeps
T_DIM, T_RESET = 9.20, 9.68


def at(trace_seconds):
    """Wall-clock moment the playhead reaches a given point in the trace."""
    return T_PLAY_FROM + (trace_seconds / T_SPAN) * (T_PLAY_TO - T_PLAY_FROM)


def x_of(trace_seconds):
    return T_X0 + trace_seconds * PX


#            label                         depth  start   end   colour
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

MARKERS = [(3.62, "start", "first fare on screen · 3.6 s"),
           (9.80, "end", "search complete · 9.8 s")]

# The counter only means anything while the stream is actually running.
TICKER = [(0.00, "0"), (3.62, "112"), (4.20, "268"), (4.90, "431"),
          (5.60, "588"), (6.40, "702"), (7.20, "815"), (8.00, "921"),
          (8.90, "1,004"), (9.72, "1,047")]


def fade(appear, rise=0.16, loop=T_LOOP, dim=T_DIM, reset=T_RESET):
    keys = [0.0, appear, appear + rise, dim, reset, loop]
    return ('<animate attributeName="opacity" dur="%gs" repeatCount="indefinite"'
            ' values="0;0;1;1;0;0" keyTimes="%s"/>'
            % (loop, ";".join(f(k / loop) for k in keys)))


def trace(theme):
    p = PALETTES[theme]
    grid_top, grid_bottom = 82.0, 386.0
    out = []

    # -- header -------------------------------------------------------------
    out.append('<text x="24" y="30" font-family="%s" font-size="13.5" fill="%s">'
               '<tspan fill="%s" font-weight="700">POST</tspan>'
               '  /api/v1/flights/search</text>'
               % (MONO, p["fg"], p["green"]))
    out.append('<text x="24" y="49" font-family="%s" font-size="10.5" fill="%s">'
               'trace 7f3a91c1 · 12 spans · one request fanned out to eleven '
               'suppliers, streamed back as it lands</text>' % (SANS, p["faint"]))

    for start, label in TICKER:
        nxt = next((s for s, _ in TICKER if s > start), T_SPAN + 1)
        a, b = at(start), min(at(nxt), T_DIM)
        if b <= a:
            continue
        out.append('<text x="876" y="38" text-anchor="end" font-family="%s" '
                   'font-size="21" font-weight="700" fill="%s" opacity="0">%s'
                   '<animate attributeName="opacity" dur="%gs" '
                   'repeatCount="indefinite" calcMode="discrete" values="0;1;0" '
                   'keyTimes="0;%s;%s"/></text>'
                   % (MONO, p["green"], esc(label), T_LOOP,
                      f(a / T_LOOP), f(b / T_LOOP)))
    out.append('<text x="876" y="53" text-anchor="end" font-family="%s" '
               'font-size="10" fill="%s">fares streamed</text>'
               % (SANS, p["faint"]))

    # -- axis ---------------------------------------------------------------
    for s in range(0, 11, 2):
        gx = x_of(s)
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                   'stroke-width="1" stroke-dasharray="2 4"/>'
                   % (f(gx), grid_top, f(gx), grid_bottom, p["border"]))
        out.append('<text x="%s" y="72" text-anchor="middle" font-family="%s" '
                   'font-size="9.5" fill="%s">%d s</text>'
                   % (f(gx), MONO, p["faint"], s))
    # A solid origin, so the playhead parked at rest reads as t=0.
    out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
               % (f(T_X0), grid_top, f(T_X0), grid_bottom, p["border"]))

    # -- rows ---------------------------------------------------------------
    bars, labels = [], []
    for i, (name, depth, s0, s1, tone) in enumerate(SPANS):
        top = ROW_Y + i * ROW_H
        if i % 2 == 0:
            out.append('<rect x="24" y="%s" width="852" height="%s" fill="%s" '
                       'opacity="0.55"/>' % (f(top), f(ROW_H - 4), p["stripe"]))

        labels.append('<text x="%s" y="%s" font-family="%s" font-size="10" '
                      'fill="%s" opacity="0">%s%s</text>'
                      % (24 + depth * 12, f(top + 13), MONO,
                         p["faint"] if tone == "hatch" else p["muted"],
                         esc(name), fade(at(s0), 0.10)))

        fill = "url(#hatch)" if tone == "hatch" else p[tone]
        bars.append('<rect x="%s" y="%s" width="%s" height="%s" rx="3" fill="%s"/>'
                    % (f(x_of(s0)), f(top + 5), f(max((s1 - s0) * PX, 2)),
                       BAR_H, fill))
        labels.append('<text x="%s" y="%s" text-anchor="end" font-family="%s" '
                      'font-size="9.5" fill="%s" opacity="0">%.2f s%s</text>'
                      % (f(T_DUR_X), f(top + 14), MONO, p["faint"],
                         s1 - s0, fade(at(s1) + 0.06, 0.10)))

    # -- markers ------------------------------------------------------------
    for s, anchor, text in MARKERS:
        mx = x_of(s)
        bars.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                    'stroke-width="1.2" stroke-dasharray="3 3" opacity="0.85"/>'
                    % (f(mx), grid_top - 4, f(mx), grid_bottom + 4, p["accent"]))
        labels.append('<text x="%s" y="402" text-anchor="%s" font-family="%s" '
                      'font-size="10" font-weight="600" fill="%s" opacity="0">%s%s</text>'
                      % (f(mx + (7 if anchor == "start" else -7)),
                         "start" if anchor == "start" else "end",
                         SANS, p["accent"], esc(text), fade(at(s) + 0.08, 0.14)))

    # -- playhead -----------------------------------------------------------
    play = ('<g opacity="0">\n'
            '  <animateTransform attributeName="transform" type="translate" '
            'dur="%gs" repeatCount="indefinite" calcMode="linear"\n'
            '                    values="0 0;0 0;%s 0;%s 0" keyTimes="0;%s;%s;1"/>\n'
            '  <animate attributeName="opacity" dur="%gs" repeatCount="indefinite" '
            'values="0;0;1;1;0;0" keyTimes="0;%s;%s;%s;%s;1"/>\n'
            '  <line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.5"/>\n'
            '  <circle cx="%s" cy="%s" r="3.2" fill="%s"/>\n'
            '</g>'
            % (T_LOOP, f(T_X1 - T_X0), f(T_X1 - T_X0),
               f(T_PLAY_FROM / T_LOOP), f(T_PLAY_TO / T_LOOP),
               T_LOOP,
               f(T_PLAY_FROM / T_LOOP), f((T_PLAY_FROM + 0.12) / T_LOOP),
               f((T_PLAY_TO - 0.2) / T_LOOP), f((T_PLAY_TO + 0.25) / T_LOOP),
               f(T_X0), grid_top - 6, f(T_X0), grid_bottom + 6, p["accent"],
               f(T_X0), grid_bottom + 10, p["accent"]))

    # Everything time-bound lives behind one wipe, so twelve bars reveal in the
    # exact order the real request produced them — one animation, not twelve.
    wipe = ('<clipPath id="wipe"><rect x="%s" y="0" width="0" height="%d">\n'
            '  <animate attributeName="width" dur="%gs" repeatCount="indefinite" '
            'calcMode="linear"\n'
            '           values="0;0;%s;%s;0;0" keyTimes="0;%s;%s;%s;%s;1"/>\n'
            '</rect></clipPath>'
            % (f(T_X0 - 1), T_H, T_LOOP, f(T_X1 - T_X0 + 3), f(T_X1 - T_X0 + 3),
               f(T_PLAY_FROM / T_LOOP), f(T_PLAY_TO / T_LOOP),
               f(T_DIM / T_LOOP), f((T_DIM + 0.02) / T_LOOP)))

    return """<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img"
     aria-label="Distributed trace of one flight search on the Travilo platform. An API gateway span runs 9.8 seconds; inside it the reservation service resolves pricing rules in 0.24 seconds, then an orchestrator fans out in parallel to Sabre, Amadeus, Travelport, PKfare, AirMaster and six further connectors. Merging and ranking begins at 3.55 seconds and the first fare reaches the agent over Server-Sent Events at 3.6 seconds; 1,047 fares have streamed by 9.8 seconds.">
  <title>One search, traced &#8212; eleven suppliers in parallel, first fare in 3.6 s</title>
  <defs>
    <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="6" height="6" fill="%s" opacity="0.28"/>
      <rect width="2.5" height="6" fill="%s" opacity="0.75"/>
    </pattern>
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
""" % (T_W, T_H, T_W, T_H, p["green"], p["green"], indent([wipe]),
       T_W - 1, T_H - 1, p["bg"], p["border"],
       indent(out), indent(bars, "    "), indent(labels), indent([play]))


# ================================================================= topology ==
#
# The same platform with the clock taken out: what talks to what, and where the
# eleven parallel calls of the trace above actually come from.

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
        aggregate = name.startswith("+")
        nodes.append(box(742, cy - 16, 122, 32, p["card_alt"], p["border"], 6))
        nodes.append('<text x="803" y="%s" text-anchor="middle" font-family="%s" '
                     'font-size="10.5" fill="%s">%s</text>'
                     % (f(cy + 3.8), SANS,
                        p["faint"] if aggregate else p["fg"], esc(name)))

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

    return """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="%d" height="%d" viewBox="0 0 %d %d" role="img"
     aria-label="Topology of the Travilo platform. Admin, B2B agency and B2C web panels built on Next.js call eight .NET 9 services &#8212; reservation, finance, configuration, notification, report, user, visa and hotel. A search orchestrator issues eleven parallel gRPC calls to Sabre, Amadeus, Travelport, PKfare and seven further connectors, then merges, ranks and streams results back. Three white-label tenants; 96 pricing rules held as configuration rather than code.">
  <title>Platform topology &#8212; eight services, eleven connectors, three tenants</title>
  <defs>
    <filter id="glow" x="-150%%" y="-150%%" width="400%%" height="400%%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect x="0.5" y="0.5" width="%s" height="%s" rx="10" fill="%s" stroke="%s"/>

%s

%s

  <g filter="url(#glow)">
%s
  </g>
</svg>
""" % (P_W, P_H, P_W, P_H, P_W - 1, P_H - 1, p["bg"], p["border"],
       indent(wires), indent(nodes), indent(dots, "    "))


def main():
    for theme in ("dark", "light"):
        for name, fn in (("trace", trace), ("topology", topology)):
            path = os.path.join(HERE, "%s-%s.svg" % (name, theme))
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(fn(theme))
            print("wrote %-22s %6d bytes" % (os.path.basename(path),
                                             os.path.getsize(path)))


if __name__ == "__main__":
    main()
