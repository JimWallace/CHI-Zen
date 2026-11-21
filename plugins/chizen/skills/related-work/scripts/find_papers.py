#!/usr/bin/env python3
"""find_papers.py: candidate related work from scholarly records, never from memory.

    python3 find_papers.py search "older adults smart speakers" [--rows 20] [--since 2015]
                                  [--venue "Human Factors in Computing Systems"]
                                  [--any-type]  # default: conference papers, journal articles
    python3 find_papers.py refs 10.1145/3173574.3173715      # what a paper cites (backward)
    python3 find_papers.py cites 10.1145/3173574.3173715     # what cites a paper (forward)
    python3 find_papers.py bibtex 10.1145/3173574.3173715 [...]   # BibTeX from doi.org
    python3 find_papers.py seeds PAPER_DIR                   # DOIs in the paper's .bib files

Options for search/refs/cites: --bib FILE (repeatable) marks candidates already in the
paper's bibliography (by DOI); --new-only drops them; --md prints a Markdown table instead
of JSON.

WHERE THE RECORDS COME FROM. Search and reference lists: Crossref (api.crossref.org),
which holds the reference lists ACM deposits for its papers. Citing papers: Semantic
Scholar (api.semanticscholar.org), then OpenAlex (api.openalex.org) if Semantic Scholar
refuses. Both rate-limit requests without a key; set SEMANTIC_SCHOLAR_API_KEY or
OPENALEX_API_KEY if you have one. BibTeX: content negotiation on doi.org, i.e. the record the
DOI's registration agency (Crossref, DataCite) holds. Set CROSSREF_MAILTO to an address of
your own to use Crossref's "polite" pool; nothing else identifies you.

WHAT THE OUTPUT MEANS. Every candidate is a record a service returned: title, authors,
year, venue, DOI, abstract (when the publisher deposited one) and citation count. It is a
reading list, not a set of citations: whether a paper supports a claim is for someone who
has read it to decide (guide: REF-13).

Standard library only. Exit status: 0 ok, 1 no service answered, 2 bad usage.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "CHI-Zen-find-papers/1.0 (+https://github.com/JimWallace/CHI-Zen)"
CROSSREF = "https://api.crossref.org/works"
S2 = "https://api.semanticscholar.org/graph/v1/paper"
OPENALEX = "https://api.openalex.org/works"
CR_FIELDS = "DOI,title,author,issued,container-title,type,abstract,is-referenced-by-count"


class Unavailable(Exception):
    pass


def get(url: str, accept: str = "application/json", headers: dict | None = None,
        tries: int = 4) -> bytes:
    hdrs = {"User-Agent": UA, "Accept": accept, **(headers or {})}
    delay = 2.0
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdrs), timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise Unavailable(f"not found: {url}") from e
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise Unavailable(f"HTTP {e.code} from {urllib.parse.urlsplit(url).netloc}") from e
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise Unavailable(f"{urllib.parse.urlsplit(url).netloc}: {e}") from e
    raise Unavailable(url)


def get_json(url: str, headers: dict | None = None) -> dict:
    return json.loads(get(url, headers=headers))


def norm_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi.strip(), flags=re.I)
    return doi.lower() or None


def strip_jats(s: str | None) -> str | None:
    if not s:
        return None
    s = html.unescape(s)
    s = re.sub(r"<jats:title>.*?</jats:title>", " ", s, flags=re.S)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).strip() or None


def authors_str(names: list[str]) -> str:
    names = [n for n in names if n]
    if len(names) > 3:
        return ", ".join(names[:3]) + " et al."
    return ", ".join(names)


# ------------------------------------------------------------------ records

def from_crossref(m: dict) -> dict:
    year = None
    for k in ("issued", "published-print", "published-online"):
        parts = (m.get(k) or {}).get("date-parts") or [[None]]
        if parts[0] and parts[0][0]:
            year = parts[0][0]
            break
    names = [" ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name", "")
             for a in m.get("author", [])]
    return {
        "doi": norm_doi(m.get("DOI")),
        "title": " ".join(m.get("title") or []) or None,
        "authors": authors_str(names),
        "year": year,
        "venue": " ".join(m.get("container-title") or []) or None,
        "type": m.get("type"),
        "abstract": strip_jats(m.get("abstract")),
        "cited_by": m.get("is-referenced-by-count"),
        "source": "crossref",
    }


def crossref_params(params: dict) -> str:
    mailto = os.environ.get("CROSSREF_MAILTO")
    if mailto:
        params = {**params, "mailto": mailto}
    return urllib.parse.urlencode(params)


# Papers and articles; --any-type also returns preprints, reports, datasets, book chapters...
PAPER_TYPES = ("proceedings-article", "journal-article")


def search(query: str, rows: int, since: int | None, any_type: bool = False,
           venue: str | None = None) -> list[dict]:
    params = {"query.bibliographic": query, "rows": rows, "select": CR_FIELDS}
    if venue:
        params["query.container-title"] = venue
    filters = [] if any_type else [f"type:{t}" for t in PAPER_TYPES]
    if since:
        filters.append(f"from-pub-date:{since}")
    if filters:
        params["filter"] = ",".join(filters)
    data = get_json(f"{CROSSREF}?{crossref_params(params)}")
    return [from_crossref(m) for m in data["message"]["items"]]


def crossref_many(dois: list[str]) -> list[dict]:
    """Metadata for many DOIs, 20 per request (Crossref ORs repeated doi: filters)."""
    out = []
    for i in range(0, len(dois), 20):
        chunk = dois[i:i + 20]
        params = {"filter": ",".join(f"doi:{d}" for d in chunk), "rows": len(chunk),
                  "select": CR_FIELDS}
        out += [from_crossref(m) for m in get_json(f"{CROSSREF}?{crossref_params(params)}")
                ["message"]["items"]]
    return out


def refs(doi: str) -> tuple[list[dict], list[str]]:
    """The works `doi` cites: records for references with a DOI; the rest as unstructured text."""
    m = get_json(f"{CROSSREF}/{urllib.parse.quote(doi)}?{crossref_params({})}")["message"]
    with_doi, without = [], []
    for r in m.get("reference", []):
        d = norm_doi(r.get("DOI"))
        if d:
            with_doi.append(d)
        else:
            without.append(r.get("unstructured") or " ".join(
                str(r[k]) for k in ("author", "year", "article-title", "volume-title",
                                    "journal-title") if r.get(k)))
    found = crossref_many(list(dict.fromkeys(with_doi)))
    return found, [w for w in without if w]


def cites(doi: str, rows: int) -> list[dict]:
    """The works that cite `doi`: Semantic Scholar, then OpenAlex."""
    errors = []
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    try:
        url = (f"{S2}/DOI:{urllib.parse.quote(doi)}/citations?limit={min(rows, 1000)}"
               "&fields=title,year,venue,authors,externalIds,abstract,citationCount")
        data = get_json(url, headers={"x-api-key": key} if key else None)
        out = []
        for c in data.get("data", []):
            p = c.get("citingPaper") or {}
            out.append({
                "doi": norm_doi((p.get("externalIds") or {}).get("DOI")),
                "title": p.get("title"),
                "authors": authors_str([a.get("name", "") for a in p.get("authors") or []]),
                "year": p.get("year"),
                "venue": p.get("venue") or None,
                "type": None,
                "abstract": p.get("abstract"),
                "cited_by": p.get("citationCount"),
                "source": "semanticscholar",
            })
        return out
    except Unavailable as e:
        errors.append(f"Semantic Scholar: {e}")
    try:
        params = {"filter": f"cites:doi:{doi}", "per-page": min(rows, 200),
                  "select": "doi,title,publication_year,authorships,primary_location,"
                            "cited_by_count,abstract_inverted_index,type"}
        if os.environ.get("OPENALEX_API_KEY"):
            params["api_key"] = os.environ["OPENALEX_API_KEY"]
        # OpenAlex resolves cites: with its own ID; look the work up first.
        w = get_json(f"{OPENALEX}/doi:{urllib.parse.quote(doi)}?"
                     + urllib.parse.urlencode({k: v for k, v in params.items() if k == "api_key"}))
        params["filter"] = f"cites:{w['id'].rsplit('/', 1)[-1]}"
        data = get_json(f"{OPENALEX}?{urllib.parse.urlencode(params)}")
        return [from_openalex(x) for x in data.get("results", [])]
    except (Unavailable, KeyError) as e:
        errors.append(f"OpenAlex: {e}")
    raise Unavailable("; ".join(errors))


def from_openalex(x: dict) -> dict:
    inv = x.get("abstract_inverted_index") or {}
    words = sorted((pos, w) for w, ps in inv.items() for pos in ps)
    src = ((x.get("primary_location") or {}).get("source") or {})
    return {
        "doi": norm_doi(x.get("doi")),
        "title": x.get("title"),
        "authors": authors_str([(a.get("author") or {}).get("display_name", "")
                                for a in x.get("authorships") or []]),
        "year": x.get("publication_year"),
        "venue": src.get("display_name"),
        "type": x.get("type"),
        "abstract": " ".join(w for _, w in words) or None,
        "cited_by": x.get("cited_by_count"),
        "source": "openalex",
    }


def bibtex(doi: str) -> str:
    return get(f"https://doi.org/{urllib.parse.quote(doi)}", accept="application/x-bibtex"
               ).decode("utf-8", "replace").strip()


# ------------------------------------------------------------------ the paper's .bib

def bib_dois(paths: list[Path]) -> set[str]:
    dois = set()
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in re.finditer(r"\bdoi\s*=\s*[{\"]\s*([^}\"]+)", text, re.I):
            d = norm_doi(m.group(1))
            if d:
                dois.add(d)
        for m in re.finditer(r"doi\.org/(10\.[^\s}\"]+)", text, re.I):
            dois.add(m.group(1).lower())
    return dois


def paper_bibs(paper: Path) -> list[Path]:
    return sorted(p for p in paper.rglob("*.bib")
                  if not any(part.startswith(".") for part in p.relative_to(paper).parts))


# ------------------------------------------------------------------ output

def mark(cands: list[dict], known: set[str], new_only: bool) -> list[dict]:
    seen, out = set(), []
    for c in cands:
        key = c.get("doi") or (c.get("title") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        c["in_bib"] = bool(c.get("doi") and c["doi"] in known)
        if not (new_only and c["in_bib"]):
            out.append(c)
    return out


def md_table(cands: list[dict]) -> str:
    rows = ["| # | Paper | Venue | DOI | Cited by | Abstract | In .bib |",
            "|---|-------|-------|-----|----------|----------|---------|"]
    for i, c in enumerate(cands, 1):
        cell = lambda s: (s or "").replace("|", "\\|")
        ab = c.get("abstract")
        rows.append(f"| {i} | {cell(c['authors'])} ({c['year']}). {cell(c['title'])} | "
                    f"{cell(c['venue'])} | {('https://doi.org/' + c['doi']) if c['doi'] else '-'} | "
                    f"{c['cited_by'] if c['cited_by'] is not None else '-'} | "
                    f"{cell(ab[:300] + ('…' if len(ab) > 300 else '')) if ab else 'not deposited'} | "
                    f"{'yes' if c.get('in_bib') else ''} |")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--since", type=int, help="earliest publication year")
    s.add_argument("--any-type", action="store_true",
                   help="not only conference papers and journal articles")
    s.add_argument("--venue", help='words from the venue\'s name, e.g. "Human Factors in '
                   'Computing Systems" (CHI); ranks matching venues first, doesn\'t filter')
    for name in ("refs", "cites"):
        sub.add_parser(name).add_argument("doi")
    b = sub.add_parser("bibtex")
    b.add_argument("doi", nargs="+")
    sd = sub.add_parser("seeds")
    sd.add_argument("paper", type=Path)
    for p in (s, sub.choices["refs"], sub.choices["cites"]):
        p.add_argument("--rows", type=int, default=25)
        p.add_argument("--bib", action="append", default=[], type=Path)
        p.add_argument("--new-only", action="store_true")
        p.add_argument("--md", action="store_true")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "seeds":
            if not args.paper.is_dir():
                print(f"{args.paper} is not a directory", file=sys.stderr)
                return 2
            print("\n".join(sorted(bib_dois(paper_bibs(args.paper)))))
            return 0
        if args.cmd == "bibtex":
            failed = 0
            for d in args.doi:
                try:
                    print(bibtex(norm_doi(d)) + "\n")
                except Unavailable as e:
                    print(f"% {d}: {e}", file=sys.stderr)
                    failed += 1
            return 1 if failed == len(args.doi) else 0
        unstructured: list[str] = []
        if args.cmd == "search":
            cands = search(args.query, args.rows, args.since, args.any_type, args.venue)
        elif args.cmd == "refs":
            cands, unstructured = refs(norm_doi(args.doi))
        else:
            cands = cites(norm_doi(args.doi), args.rows)
    except Unavailable as e:
        print(f"find_papers: no answer: {e}", file=sys.stderr)
        return 1

    cands = mark(cands, bib_dois(args.bib), args.new_only)
    if args.md:
        print(md_table(cands))
        if unstructured:
            print("\nReferences without a DOI (find them by title before citing):")
            print("\n".join(f"- {u}" for u in unstructured))
    else:
        print(json.dumps({"candidates": cands, "references_without_doi": unstructured},
                         indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
