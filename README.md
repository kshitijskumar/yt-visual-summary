# yt-visual-summary

A [Claude Code](https://claude.com/claude-code) skill that turns a YouTube video into a single, self-contained HTML page you can skim in about three minutes: a TL;DR, topic sections, tight bullets, small diagrams and tables, and timestamp links that jump to the right moment in the video.

## What it does

1. **Fetch** – `scripts/fetch.sh` uses `yt-dlp` to download only the captions and metadata (no video), then cleans the transcript into `[mm:ss] text` paragraphs.
2. **Summarise** – Claude reads the transcript and writes an HTML body fragment, grounded only in what the speaker said, with visuals (flow, table, columns, stats, timeline) where the content has structure.
3. **Build** – `scripts/build_page.py` wraps the body with inline CSS and a header, converts `[[mm:ss]]` markers into links to that moment in the video, refuses any external resource, and writes `~/yt-summaries/<date>-<slug>.html`.

## Example

Generated from *"What Is Agentic AI? All You Need to Know in Under 5 Minutes"* (full page: [`examples/agentic-ai-explained.html`](examples/agentic-ai-explained.html)):

> ### TL;DR
> - Agentic AI = systems that autonomously set goals, plan, and run multi-step workflows without supervision (00:20).
> - An AI agent is a specialist for one job; agentic AI is the whole managed team working toward a bigger goal (01:39).
> - Automation is like a map (fixed, predictable steps); agentic AI is like a GPS that recalculates (02:03).
>
> ### Agentic AI vs agents vs automation
>
> | Concept | Analogy | Example / trait |
> |---|---|---|
> | AI agent | Talented specialist | Reads an email, drafts a calendar invite |
> | Agentic AI | The specialist's whole team | Plans a corporate event, books travel, sends invites, adjusts |
> | AI automation | A map | Repetitive, well-defined, predictable steps |

## Install

Requires `yt-dlp` and Python 3.

Copy this repo into a skills folder, e.g.:

```bash
git clone https://github.com/<your-user>/yt-visual-summary ~/.claude/skills/yt-visual-summary
```

Then in Claude Code, give it a YouTube link and ask for a summary (or invoke `/yt-visual-summary`).

## Layout

```
SKILL.md              skill instructions for Claude
scripts/fetch.sh      download captions + metadata
scripts/clean_vtt.py  VTT -> timestamped transcript
scripts/meta.py       extract metadata (title, channel, chapters, ...)
scripts/build_page.py build the final HTML page
assets/style.css      styles inlined into every page
examples/             sample generated summary
```
