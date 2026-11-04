# co2 — LLM wiki

This repo is a Markdown knowledge base that an LLM writes and keeps up to date.
People add sources; the LLM reads them and maintains the wiki.

## Layout

- `raw/` — source material (papers, notes, web clippings, data). Never edit these files once added.
- `wiki/` — pages the LLM writes. One topic per page, file names in kebab-case (`ocean-uptake.md`).
- `wiki/index.md` — a list of every page with a one-line summary. Keep it current.
- `wiki/log.md` — a dated record of every ingest, query and cleanup pass, newest at the bottom.

## Workflows

**Ingest** (a new file in `raw/`): read it, write a summary page for it, then update every
existing page it affects, add `[[links]]` between related pages, add the new pages to
`index.md`, and add a line to `log.md`.

**Query**: answer from the wiki, citing pages. If the answer is worth keeping, save it as a page.

**Cleanup**: look for contradictions, stale claims, orphan pages, missing links and
topics that are mentioned but have no page. Fix what you can and log the rest.

## Rules

- Every factual claim cites a source in `raw/` or another wiki page.
- Prefer editing an existing page over creating a near-duplicate.
- When sources disagree, record both views and say which source holds each.
