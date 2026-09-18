#!/usr/bin/env python3
"""Screenshots each panel at a chosen point on its animation timeline.

    python assets/verify.py            # every panel at t=6s, both themes
    python assets/verify.py 2.5        # mid-reveal instead

Screenshotting an animated SVG directly is a race: the browser paints whenever
it is ready, which is usually frame zero, where a panel that reveals itself is
by definition blank. So each file is inlined into a page that pauses the SMIL
clock and seeks it, which makes the result the same every run.

Output lands in the system temp directory; nothing here is committed.
"""

import glob
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(tempfile.gettempdir(), "panel-verify")

CHROME = next((c for c in (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/chromium", "/usr/bin/google-chrome",
) if os.path.exists(c)), None)

PAGE = """<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:transparent}</style>
%s
<script>
  const svg = document.querySelector('svg');
  svg.pauseAnimations();
  svg.setCurrentTime(%s);
</script>
"""


def main():
    if not CHROME:
        sys.exit("no Chrome or Edge found to render with")
    when = sys.argv[1] if len(sys.argv) > 1 else "6"
    os.makedirs(OUT, exist_ok=True)

    for path in sorted(glob.glob(os.path.join(HERE, "*.svg"))):
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as fh:
            markup = fh.read()
        width = markup.split('width="', 1)[1].split('"', 1)[0]
        height = markup.split('height="', 1)[1].split('"', 1)[0]

        page = os.path.join(OUT, name + ".html")
        with open(page, "w", encoding="utf-8") as fh:
            fh.write(PAGE % (markup, when))

        shot = os.path.join(OUT, name + ".png")
        subprocess.run([
            CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", "--virtual-time-budget=3000",
            "--screenshot=" + shot,
            "--window-size=%s,%s" % (width, height),
            "file:///" + page.replace("\\", "/"),
        ], capture_output=True)

        size = os.path.getsize(shot) if os.path.exists(shot) else 0
        flag = "  <-- suspiciously small" if size < 9000 else ""
        print("  %-18s %sx%-4s %7d bytes%s" % (name, width, height, size, flag))

    print("\nwrote %s at t=%ss" % (OUT, when))


if __name__ == "__main__":
    main()
