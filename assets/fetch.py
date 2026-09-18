#!/usr/bin/env python3
"""Pulls the account's own numbers from the GitHub API into assets/data/github.json.

    python assets/fetch.py            # refresh the snapshot
    python assets/build.py            # redraw the panels from it

Kept separate from build.py on purpose. Drawing has to work offline and give the
same picture twice, so the network step writes a dated snapshot and the renderer
only ever reads that file. Every figure on the measured panel traces back to a
field in here.

Nothing identifying a single repository survives this script. Names, owners,
descriptions and per-repository rows are aggregated in memory and dropped; what
lands on disk is counts, because the file is committed to a public repository
and the panel only ever needed the totals.

Two decisions worth knowing about, because both change the answer:

  Commits, not repository counts. Counting repositories says Java 25 to C# 17,
  which measures how many things were started. Counting commits says C# 1,044
  to Java 288, which measures where the work actually went. The second is the
  honest answer to "what does this person write".

  Every repository committed to, not just the public ones. Authenticated as the
  account itself, private and organisation repositories are visible, and leaving
  them out would drop most of the recent work and almost all of the C#.

It also counts what GitHub will not. A commit is only attributed to an account
when its author address is verified on that account, so years spent committing
from an employer laptop under an employer address are quietly undercounted. The
scan over owned repositories below finds those commits by address and reports
them separately, which is slow but is the difference between a chart that is
low and a chart that is wrong.

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

CONTRIBUTIONS = """query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      totalCommitContributions
      commitContributionsByRepository(maxRepositories: 100) {
        repository { id isPrivate primaryLanguage { name } owner { login } }
        contributions { totalCount }
      }
    }
  }
}"""


def gh(*args, **kwargs):
    """Call the CLI. `tolerant` returns None instead of exiting, which an empty
    repository needs: listing its commits is a 409, not a problem."""
    out = subprocess.run(("gh",) + args, capture_output=True, text=True,
                         encoding="utf-8")
    if out.returncode:
        if kwargs.get("tolerant"):
            return None
        sys.exit("gh %s failed:\n%s" % (" ".join(args), out.stderr.strip()))
    return json.loads(out.stdout or "null")


def main():
    print("listing public repositories ...")
    raw, page = [], 1
    while True:
        batch = gh("api", "users/%s/repos?per_page=100&page=%d" % (LOGIN, page))
        if not batch:
            break
        raw.extend(batch)
        page += 1
    public = [r for r in raw if not r["fork"] and not r["archived"]]
    print("  %d public, %d after forks and archives" % (len(raw), len(public)))

    # Only kept to justify why nothing here is measured in bytes.
    bytes_by_language = Counter()
    for i, r in enumerate(public, 1):
        bytes_by_language.update(gh("api", "repos/%s/%s/languages"
                                    % (LOGIN, r["name"]), tolerant=True) or {})
        if i % 20 == 0 or i == len(public):
            print("  languages %d/%d" % (i, len(public)))

    print("walking commit contributions ...")
    now = datetime.now(timezone.utc)
    first = min(int(r["created_at"][:4]) for r in public)
    by_year, touched = {}, {}
    for year in range(first, now.year + 1):
        c = gh("api", "graphql", "-f", "query=" + CONTRIBUTIONS,
               "-f", "login=" + LOGIN,
               "-f", "from=%d-01-01T00:00:00Z" % year,
               "-f", "to=%d-12-31T23:59:59Z" % year)["data"]["user"]["contributionsCollection"]
        mine = org = org_repos = 0
        for row in c["commitContributionsByRepository"]:
            repo, n = row["repository"], row["contributions"]["totalCount"]
            if repo["owner"]["login"] == LOGIN:
                mine += n
            else:
                org += n
                org_repos += 1
            # Deduplicated across years by opaque id, which is then discarded.
            seen = touched.setdefault(repo["id"], {
                "language": (repo["primaryLanguage"] or {}).get("name"),
                "private": repo["isPrivate"],
                "commits": 0,
            })
            seen["commits"] += n
        by_year[str(year)] = {
            "commits": c["totalCommitContributions"],
            "own": mine,
            "organisation": org,
            "organisation_repositories": org_repos,
        }
        print("  %d  %5d total  %5d own  %5d organisation (%d repos)"
              % (year, c["totalCommitContributions"], mine, org, org_repos))

    languages, unclassified = {}, {"commits": 0, "repositories": 0}
    for entry in touched.values():
        if not entry["language"]:
            unclassified["commits"] += entry["commits"]
            unclassified["repositories"] += 1
            continue
        bucket = languages.setdefault(entry["language"],
                                      {"commits": 0, "repositories": 0,
                                       "private_repositories": 0})
        bucket["commits"] += entry["commits"]
        bucket["repositories"] += 1
        bucket["private_repositories"] += 1 if entry["private"] else 0

    # Addresses this person has committed under. Anything not verified on the
    # GitHub account produces a commit the contribution graph will not show.
    # An employer address cannot be verified here any more, so these commits are
    # recognised by the author name and address on the commit itself, inside
    # repositories this account owns. Narrow enough not to claim other people's
    # work, wide enough to find every laptop this person has ever committed from.
    print("scanning owned repositories for unattributed commits ...")
    owned, page = [], 1
    while True:
        batch = gh("api", "user/repos?affiliation=owner&per_page=100&page=%d" % page)
        if not batch:
            break
        owned.extend(r for r in batch if not r["fork"])
        page += 1

    unattributed, seen_addresses = Counter(), Counter()
    for i, r in enumerate(owned, 1):
        page = 1
        while True:
            batch = gh("api", "repos/%s/commits?per_page=100&page=%d"
                       % (r["full_name"], page), tolerant=True)
            if not isinstance(batch, list) or not batch:
                break
            for c in batch:
                author = (c.get("commit") or {}).get("author") or {}
                linked = (c.get("author") or {}).get("login")
                if linked == LOGIN:
                    continue
                email = (author.get("email") or "").lower()
                name = (author.get("name") or "").lower()
                if linked is None and ("mosfik" in email or "mosfik" in name):
                    unattributed[(author.get("date") or "????")[:4]] += 1
                    seen_addresses[email] += 1
            if len(batch) < 100:
                break
            page += 1
        if i % 20 == 0 or i == len(owned):
            print("  %d/%d repositories" % (i, len(owned)))
    print("  %d commits authored here but not attributed" % sum(unattributed.values()))
    for email, n in seen_addresses.most_common():
        print("    %-45s %4d" % (email, n))

    total_bytes = sum(bytes_by_language.values())
    top_byte_language, top_bytes = bytes_by_language.most_common(1)[0]
    snapshot = {
        "login": LOGIN,
        "generated": now.strftime("%Y-%m-%d"),
        "through_month": now.strftime("%B"),
        "public_repositories": len(public),
        "repositories_touched": len(touched),
        "commits_by_year": by_year,
        "commits_by_language": dict(sorted(languages.items(),
                                           key=lambda kv: -kv[1]["commits"])),
        "unclassified": unclassified,
        # Authored by this person, in repositories this account owns, but not
        # attributed by GitHub because the address was never verified here.
        "unattributed_by_year": dict(sorted(unattributed.items())),
        "byte_share_top_language": {
            "language": top_byte_language,
            "percent": round(100.0 * top_bytes / total_bytes),
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(snapshot, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote %s (aggregates only, no repository names)" % OUT)


if __name__ == "__main__":
    main()
