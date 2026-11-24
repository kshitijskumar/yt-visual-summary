---
name: yt-visual-summary
description: Turn a YouTube video into a single-file visual HTML summary (TL;DR, topic sections, bullets, diagrams, timestamp links). Use when given a YouTube link to summarise or digest. Can also publish the page as a claude.ai Artifact (when the user asks for an artifact, a shareable link, or access on other devices).
---

# YouTube visual summary

Goal: one self-contained HTML page that lets someone grasp what a long video covered in ~3 minutes and decide whether to watch it. Not a transcript, not a blog post: short prose, dense bullets, and diagrams wherever the content has structure.

Scripts live in `scripts/` next to this file. Refer to that directory as `$SKILL` below.

## 1. Fetch
Run `bash $SKILL/scripts/fetch.sh "<URL>"`.
- It prints `WORK=<dir>` containing `transcript.txt` (`[mm:ss] text` paragraphs) and `meta.json` (id, title, channel, duration, upload date, chapters, description).
- Exit 2 (`NO_CAPTIONS`): tell the user the video has no captions and stop.
- Exit 1: show the error it printed and stop. If it says yt-dlp is missing, give the install command it printed.

## 2. Read
Read `meta.json` and the whole `transcript.txt`. Don't re-run anything to get metadata.

## 3. Plan before writing
1. Classify the video: tutorial/walkthrough, talk/explainer, interview/podcast, news/roundup, opinion/debate. This decides what sections emphasise (steps, arguments, Q&A themes, items, positions).
2. Split into 4-8 topic sections. Use chapters as starting boundaries if present, but merge or split by actual topic. Skip intros, sponsor reads, and outros.
3. For each section note its start timestamp, the one idea it conveys, and the concrete specifics (numbers, names, tools, models, steps, examples, caveats).
4. Pick visuals: at most one per section, 2-5 in total, only where the content has real structure:
   - process / pipeline / architecture -> `.flow`
   - A vs B, pros/cons, options -> `<table>` or `.cols`
   - spoken numbers -> `.stats` tiles, or an inline SVG bar chart
   - sequence of events -> `.timeline`
   - loop, hierarchy, or anything spatial -> inline SVG
   No decorative visuals. If the speaker refers to on-screen data whose numbers aren't spoken, don't invent them; write "chart shown at [[mm:ss]]".
5. Grounding:
   - Every claim must come from the transcript. No outside knowledge; if a clarification is truly needed, put it in a `<p class="note">Note: …</p>`.
   - Attribute opinion and speculation to the speaker ("argues", "predicts").
   - Auto-captions mangle names ("cloud code" for Claude Code, etc.). Fix obvious mis-hearings using the title and description; if unsure, keep the caption's spelling.

## 4. Write the body
Write ONLY the body fragment to `$WORK/body.html`. The build script adds `<html>`, `<head>`, CSS, the title header, and the footer.

Structure:
```html
<section class="card tldr">
  <h3>TL;DR</h3>
  <ul><li>…3-5 core takeaways…</li></ul>
  <p class="watch-if">Watch the full video if … — densest part at [[12:40]].</p>
</section>

<h2>Section topic [[04:15]]</h2>
<p>1-3 sentences of prose.</p>
<ul><li>2-5 specific bullets</li></ul>
<figure>…visual…<figcaption>What the visual shows</figcaption></figure>

<!-- repeat sections -->

<h2>Mentioned</h2>  <!-- only if the video names tools, models, papers, people, products -->
<ul><li><b>Name</b>: what it is, in a few words [[18:02]]</li></ul>
```
- Timestamps: write `[[mm:ss]]` or `[[h:mm:ss]]`; the build script turns them into links to that moment in the video.
- Available classes: `card`, `tldr`, `watch-if`, `flow` > `node` / `arrow` (use `→` in `<span class="arrow">`), `cols` > `div`, `timeline` (on `<ul>`), `stats` > `stat` (with `<b>` value), `label`, `note`, plus plain `table`, `figure`, `figcaption`.
- Prefer these HTML/CSS patterns; they never overflow. Use inline `<svg viewBox=…>` only for charts, cycles, and trees: font-size >= 13px, at most ~8 nodes, size boxes to fit text (~7.5px per character at 13px), colour with `currentColor` or `var(--accent)` / `var(--line)` so dark mode works.
- No external resources: no `<img>`, `<script src>`, fonts, or CDNs. The build fails if any are present.
- Write the body in one pass. To fix something, edit the specific part rather than rewriting the file.

## 5. Build and report
Run `python3 $SKILL/scripts/build_page.py "$WORK/meta.json" "$WORK/body.html"`.
- It writes `~/yt-summaries/<date>-<slug>.html`, prints the path, and opens it.
- If it reports external resources, remove them from `body.html` and rerun.

### Artifact mode (only when asked)
If the user asks for an artifact, a link, or to view the summary on another device (phone, another computer), publish the built page after building it. Change nothing else: same body, same CSS, same build.
- Publish the exact file `build_page.py` printed with the `Artifact` tool: `file_path` = that path, `icon: "video"`, `description` = the one-line gist. The page is already self-contained (inline CSS, no scripts, external links only to YouTube), so don't edit or re-style it. The artifact-design skill's contract is already met by `assets/style.css`.
- For a later fix to the same summary, edit `body.html`, rebuild, and publish the same path again so the URL stays the same.
- If the `Artifact` tool isn't available in this session, say so and give the local file path instead.

Before replying, spot-check three specific claims (a number, a name, a step) against `transcript.txt`. Reply with the file path (and the artifact URL in artifact mode) and a one-line gist. Don't repeat the summary in chat.
