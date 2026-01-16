# Optimistic Democracy Flow (game scoring)

This document describes how non-deterministic LLM scoring is handled via Optimistic Democracy.

Roles
- Leader validator: proposes initial AI scores for all answers.
- Committee: recomputes scores and checks equivalence.
- Players: can appeal specific scores by posting an XP bond.

Round Scoring Steps
1) Leader proposes AI scores (clarity, creativity, relevance; 0–10 each).
2) Committee verifies proposal:
   - recompute scores with their own prompt/model;
   - if per-dimension difference <= tolerance, accept proposal;
   - otherwise, replace flagged players’ scores with committee version.
3) Players can challenge accepted scores by posting an XP bond.
4) Committee re-evaluates challenged answers:
   - if AI was off, correct the scores and reward the challenger;
   - if not, slash the bond.

ASCII Sequence

Leader → propose scores
      → committee verify → accept (equivalent) → finalize → distribute XP
                      ↘ not equivalent → replace flagged → finalize → distribute XP
Players → challenge (bond) → committee re-eval → correct+reward OR slash bond
