# Launch Playbook

How to share this publicly for maximum reach without spamming or looking salesy.

## Sequence

### T-7 days: Prep
- [ ] Write the companion blog post (see "Blog Post Outline" below)
- [ ] Verify all sanitization checks pass (`./scripts/check-sanitization.sh`)
- [ ] Get 2-3 trusted reviewers (no NDA needed — this is public content)
- [ ] Take screenshots and record a 2-minute demo video (keeps it accessible for non-technical readers)

### T-1 day: Stage
- [ ] Flip repo from private to public on GitHub
- [ ] Add repo topics: `claude-code`, `ai-agents`, `memory-architecture`, `rag`, `homelab`
- [ ] Enable GitHub Sponsors (non-salesy support)
- [ ] Pin 3-4 top repos to your GitHub profile
- [ ] Schedule the blog post to publish at 8 AM ET

### T-0: Launch day (Tuesday-Thursday, 8-10 AM ET)

**Hour 1 (8-9 AM ET):**
- [ ] Publish blog post
- [ ] Submit to Hacker News: "Show HN: I built a 6-layer memory architecture for Claude Code"
  - Use the "Show HN" prefix for better reception
  - Link the blog post, not the repo directly (better engagement signals)
- [ ] Tweet/post on X with 3-4 slides summarizing the architecture

**Hour 2 (9-10 AM ET):**
- [ ] Post detailed writeup to r/ClaudeAI — explain what you built and why, link to repo
- [ ] Respond to early HN commenters (engagement in first hour is critical for ranking)

**Hour 3+ (10 AM ET onward):**
- [ ] If HN is trending: keep engaging with comments, don't vanish
- [ ] If HN is flat: pivot to Reddit and LinkedIn

### T+1 day: Second wave

- [ ] r/homelab — focus on the "homelab as knowledge base" angle
- [ ] r/selfhosted — focus on the Qdrant + Cosma self-hosted stack
- [ ] r/devops — focus on the path-scoped rules + hooks pattern

### T+2 days: Third wave

- [ ] Dev.to cross-post of the blog
- [ ] Hashnode cross-post (you already have automation for this)
- [ ] LinkedIn long-form post linking back to blog

### T+7 days: Long tail

- [ ] Submit to `awesome-claude-code` via GitHub issue (not PR — their preference)
- [ ] Reach out to AI newsletters (Ben's Bites, TLDR AI, The Rundown) — pitch as "the memory architecture most people miss"
- [ ] If there's interest: offer to do a podcast appearance

## Blog Post Outline

Title options (A/B test these on social):
- "The 6-Layer Memory Architecture I Run for Claude Code"
- "I Built a Production Memory System for AI Agents. Here's What I Learned."
- "Most Claude Code Setups Stop at CLAUDE.md. I Went 5 Layers Deeper."

Structure (~2,000 words):
1. **Hook** (150 words) — "I spent 6 months building a memory system for my AI coding agent. Here's what actually works."
2. **The problem** (300 words) — why CLAUDE.md alone breaks at scale. Concrete example.
3. **The 6 layers** (800 words) — one paragraph each, with a diagram
4. **What I got wrong** (300 words) — personal honesty, e.g. "I originally had 5 Qdrant collections and realized 3 were redundant"
5. **Measurements** (200 words) — token savings, rebuild times, hit rates
6. **The repo** (100 words) — one-line link, don't oversell
7. **Who I am** (100 words) — quick bio, consulting mention without being pushy
8. **What's next** (50 words) — close loop, invite discussion

## What Works on HN

Sorted by historical pattern (highest-performing first):
1. **Specific number + genuine insight** — "I analyzed 200 CLAUDE.md files. Here's what the top 10% do differently."
2. **Honest failure + lesson** — "My AI agent memory system ate my context window. Here's how I fixed it."
3. **Show HN with live demo** — include a link people can poke at (your wiki graph would work)
4. **Architecture + data** — not just opinions, measurements

What DOESN'T work:
- "Introducing <product name>" (reads as marketing)
- Pure opinions without receipts
- Content that feels templated/AI-generated
- Hype language ("revolutionary", "game-changing")

## Non-Salesy Consulting CTA

Bad (reads as salesy):
> "Need help implementing this? Book a call with Guatu Labs! 30-minute free consultation!"

Good (reads as natural):
> "Built at [Guatu Labs](https://guatulabs.com) — we help companies implement AI agent infrastructure. If this architecture solves a problem you're wrestling with, [get in touch](https://guatulabs.com/contact)."

Place this at the bottom of the README (not the top).

## Measuring Success

**Proximate metrics** (tell you if the launch worked):
- Stars in first 48 hours (aim: 500+)
- HN front page for at least 4 hours
- Repo traffic: 1,000+ unique visitors in week 1
- Twitter/X impressions: 50K+

**Distal metrics** (what actually matters):
- Inbound consulting inquiries (aim: 2-15 in 6 months)
- Speaking invitations (aim: 1-3)
- Co-authoring opportunities
- Referrals

The distal metrics take 1-6 months to materialize. Don't optimize for spike, optimize for compounding.

## Handling Criticism

You WILL get:
- "This is over-engineered, just use CLAUDE.md"
  → Thank them, acknowledge it's opinionated, explain the scale where it pays off
- "You could have used <library X>"
  → If they're right, say so. If they're wrong, explain why. Never be defensive.
- "This is AI slop"
  → Show them your measurements. Data defuses hot takes.
- "Where's your benchmark?"
  → Point to the LongMemEval references in `research/benchmarks.md`
