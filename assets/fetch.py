#!/usr/bin/env python3
"""Pulls the account's own numbers from the GitHub API into assets/data/github.json.

    python assets/fetch.py            # refresh the snapshot
    python assets/build.py            # redraw the panels from it

Kept separate from build.py on purpose. Drawing has to work offline and give the
same picture twice, so the network step writes a dated snapshot and the renderer
only ever reads that file. Every figure on the measured panel traces back to a
field in here.

Nothing identifying a single repository survives this script. Names, sizes,
descriptions and per-repository breakdowns are aggregated in memory and dropped;
what lands on disk is counts and nothing else, because the file is committed to
a public repository and the panel only ever needed the totals.

Uses the `gh` CLI so no token is handled here.
"""

import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

LOGIN = "mdmosfikurrahman"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "github.json")


def gh(*args):
    out = subprocess.run(("gh",) + args, capture_output=True, text=True,
                         encoding="utf-8")
    if out.returncode:
        sys.exit("gh %s failed:\n%s" % (" ".join(args), out.stderr.strip()))
    return json.loads(out.stdout or "null")


def main():
    print("listing repositories ...")
    raw, page = [], 1
    while True:
        batch = gh("api", "users/%s/repos?per_page=100&page=%d" % (LOGIN, page))
        if not batch:
            break
        raw.extend(batch)
        page += 1

    own = [r for r in raw if not r["fork"] and not r["archived"]]
    print("  %d public, %d after forks and archives" % (len(raw), len(own)))

    by_language = Counter()
    created_by_year = Counter()
    bytes_by_language = Counter()
    for i, r in enumerate(own, 1):
        # Fetched per repository, then immediately folded into totals.
        sizes = gh("api", "repos/%s/%s/languages" % (LOGIN, r["name"])) or {}
        bytes_by_language.update(sizes)
        created_by_year[r["created_at"][:4]] += 1
        if r["language"]:
            by_language[r["language"]] += 1
        if i % 10 == 0 or i == len(own):
            print("  %d/%d" % (i, len(own)))

    # Authenticated as the account itself, so private organisation repositories
    # are visible and their commits are counted. Only the counts are taken: the
    # per-repository rows are split into own versus organisation and discarded.
    print("counting commit contributions by year ...")
    query = """query($login:String!, $from:DateTime!, $to:DateTime!) {
      user(login:$login) {
        contributionsCollection(from:$from, to:$to) {
          totalCommitContributions
          commitContributionsByRepository(maxRepositories: 100) {
            repository { isPrivate owner { login } }
            contributions { totalCount }
          }
        }
      }
    }"""
    commits = {}
    now = datetime.now(timezone.utc)
    for year in range(min(int(y) for y in created_by_year), now.year + 1):
        c = gh("api", "graphql", "-f", "query=" + query, "-f", "login=" + LOGIN,
               "-f", "from=%d-01-01T00:00:00Z" % year,
               "-f", "to=%d-12-31T23:59:59Z" % year)["data"]["user"]["contributionsCollection"]
        mine = org = org_repos = 0
        for row in c["commitContributionsByRepository"]:
            n = row["contributions"]["totalCount"]
            if row["repository"]["owner"]["login"] == LOGIN:
                mine += n
            else:
                org += n
                org_repos += 1
        commits[str(year)] = {
            "commits": c["totalCommitContributions"],
            "own": mine,
            "organisation": org,
            "organisation_repositories": org_repos,
        }
        print("  %d  %5d total  %5d own  %5d organisation (%d repos)"
              % (year, c["totalCommitContributions"], mine, org, org_repos))

    total_bytes = sum(bytes_by_language.values())
    snapshot = {
        "login": LOGIN,
        "generated": now.strftime("%Y-%m-%d"),
        "through_month": now.strftime("%B"),
        "repositories": {
            "total": len(own),
            "by_primary_language": dict(by_language.most_common()),
            "created_by_year": dict(sorted(created_by_year.items())),
        },
        "commits_by_year": commits,
        # Kept only to justify why the panel counts repositories instead: one
        # language carries most of the bytes purely because of how it is stored.
        "byte_share_top_language": {
            "language": bytes_by_language.most_common(1)[0][0],
            "percent": round(100.0 * bytes_by_language.most_common(1)[0][1]
                             / total_bytes),
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(snapshot, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote %s (aggregates only, no repository names)" % OUT)


if __name__ == "__main__":
    main()
