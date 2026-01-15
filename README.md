# Optimistic Arena – AI Jury Party Game

## Overview

Optimistic Arena is a 5–15 minute multiplayer mini‑game for GenLayer community calls where players compete on fun, subjective prompts (humor, clarity, creativity), and an Intelligent Contract plus Optimistic Democracy validators act as an AI‑powered jury to rank submissions and distribute XP on‑chain.

Each session has 2–3 quick rounds with 4–20 players in a room. At the end, the contract produces a leaderboard and updates each player’s weekly/seasonal XP. The idea is lightweight enough to actually run during real community calls, not just exist as a slide.

---

## How One Round Works

1. **Prompt from the contract**  
   The GenLayer Intelligent Contract pulls recent web / GenLayer context and uses an LLM to generate a short prompt for this round.  
   Example: *“Explain Optimistic Democracy as if you’re a sports commentator.”*

2. **90 seconds to answer**  
   Each player submits one very short text answer (e.g. up to 280 characters). Submissions are sent to the contract.

3. **AI moderation**  
   The contract calls an LLM to quickly filter spam/toxic content and only keeps valid answers. Flagged content is excluded from scoring.

4. **Player voting**  
   All valid answers are shown anonymously. Each player votes for the most creative / most clear responses (for example, giving 2–3 votes per round).

5. **AI jury scoring + Optimistic Democracy**  
   In parallel, the contract asks an LLM to score each answer on:
   - clarity (0–10),
   - creativity (0–10),
   - relevance (0–10).

   A leader validator proposes these scores, and a small validator committee re‑computes them with their own models and checks equivalence via Optimistic Democracy before the scores are accepted.

6. **Quick appeals with XP bonds**  
   If someone strongly disagrees with an AI score, they can file an appeal by posting a small XP bond. A broader validator committee re‑evaluates that specific answer with a stricter scoring prompt.  
   - If the AI clearly mis‑judged it and the new scores align better with human votes, the scores are corrected and the appellant is rewarded.  
   - If not, the bond is slashed. This creates a nice “no way the AI is right here” moment during the call.

7. **Final ranking & XP**  
   The contract combines human votes (e.g. 60%) and AI scores (40%) into a final score per answer, ranks all players, and distributes XP:
   - base XP for participation,
   - bonus XP for top placements.

   The session leaderboard is shown to everyone, and Season XP per player is stored in contract state.

---

## Why This Is GenLayer‑Native

- The **Intelligent Contract** owns the full game loop: session/round management, prompt generation from live data, LLM‑based moderation and scoring, and on‑chain storage of XP and leaderboards.
- **Optimistic Democracy** is used where GenLayer is strongest: to reach consensus on non‑deterministic AI outputs (LLM scores) and to handle appeals with bonds and re‑validation by a wider committee of validators.
- The core mechanic is **subjective judgment** (creativity, humor, clarity), which matches GenLayer’s focus on AI‑backed, human‑aligned decision‑making instead of just deterministic numeric checks.

---

## Weekly Replayability

- Once per week, the contract refreshes a pool of prompts and themes based on recent web/GenLayer content.
- Each weekly session feels different (new topics, memes, use cases).
- Players accumulate XP over time, creating “regulars vs newcomers” dynamics on the leaderboard without changing the simple rules.

---

## Implementation Plan (High‑Level)

**Phase 1 – Contract logic & storage**

- Implement a GenLayer Intelligent Contract that:
  - manages sessions, rounds, prompts, submissions, votes and appeals,
  - integrates LLM calls for prompt generation, moderation and scoring,
  - stores XP and leaderboards in contract state,
  - exposes a minimal read/write API for the client.

**Phase 2 – Lightweight client (web or Discord)**

- Build a simple frontend or Discord bot for:
  - creating a room and starting a session,
  - joining a session with a GenLayer address,
  - submitting answers,
  - voting,
  - viewing round results and leaderboards.
- Keep all core rules and scoring in the contract; the client is just a thin UI.

**Phase 3 – Community playtests**

- Run a few test games during GenLayer community calls.
- Collect feedback on:
  - prompt style and difficulty,
  - balance between human votes and AI scores,
  - appeal/bond parameters.
- Iterate on prompt templates and scoring weights based on real player behavior.
