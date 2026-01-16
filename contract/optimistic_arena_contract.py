from typing import Dict, List, Optional
import random


class OptimisticArenaContract:
    """
    Skeleton implementation of the Optimistic Arena game logic.

    Focus:
    - session and round management
    - prompt generation
    - submissions and voting
    - AI scoring with Optimistic Democracy (proposal + committee check)
    - appeals with XP bonds
    - XP distribution and leaderboards

    LLM calls are mocked for clarity. This is a contest-safe prototype (no tests).
    """

    def __init__(self):
        # In-memory state for prototype
        self.sessions: Dict[int, dict] = {}
        self.season_xp: Dict[str, int] = {}
        self.next_session_id: int = 1

    # -----------------------------
    # Session management
    # -----------------------------

    def create_session(self, host: str, max_players: int = 20) -> int:
        """
        Create a new game session.
        """
        session_id = self.next_session_id
        self.next_session_id += 1

        self.sessions[session_id] = {
            "host": host,
            "players": [],
            "max_players": max_players,
            "round": 0,
            "prompt": None,
            "submissions": {},             # player -> text
            "votes": {},                   # player -> votes count
            "ai_scores_proposed": {},      # player -> scores (leader proposal)
            "ai_scores": {},               # player -> scores (accepted after OD)
            "final_scores": {},            # player -> float
            "appeals": [],                 # list of appeals
            "od_accepted": False           # whether committee accepted proposal
        }
        return session_id

    def join_session(self, session_id: int, player: str) -> None:
        """
        Add player to session (simple limit check).
        """
        session = self.sessions[session_id]
        if player in session["players"]:
            return
        if len(session["players"]) >= session["max_players"]:
            raise Exception("Session is full")
        session["players"].append(player)

    # -----------------------------
    # Round flow
    # -----------------------------

    def start_round(self, session_id: int) -> str:
        """
        Initialize a new round and generate a prompt.
        """
        session = self.sessions[session_id]
        session["round"] += 1
        session["prompt"] = self._generate_prompt()
        session["submissions"] = {}
        session["votes"] = {}
        session["ai_scores_proposed"] = {}
        session["ai_scores"] = {}
        session["final_scores"] = {}
        session["appeals"] = []
        session["od_accepted"] = False
        return session["prompt"]

    def submit_answer(self, session_id: int, player: str, text: str) -> None:
        """
        Submit one short answer (<= 280 chars).
        """
        if len(text) > 280:
            raise Exception("Answer too long (max 280 chars)")
        session = self.sessions[session_id]
        if player not in session["players"]:
            raise Exception("Player must join the session first")
        session["submissions"][player] = text

    def vote(self, session_id: int, voter: str, target_player: str) -> None:
        """
        Simple upvote for a target player's answer.
        """
        session = self.sessions[session_id]
        if voter not in session["players"] or target_player not in session["players"]:
            raise Exception("Both voter and target must be in session")
        if target_player not in session["submissions"]:
            raise Exception("Target player has no submission")
        session["votes"][target_player] = session["votes"].get(target_player, 0) + 1

    # -----------------------------
    # AI scoring + Optimistic Democracy
    # -----------------------------

    def propose_ai_scores(self, session_id: int) -> None:
        """
        Leader validator proposes AI scores (mocked here).
        Saved to ai_scores_proposed; not yet accepted.
        """
        session = self.sessions[session_id]
        proposed = {}
        for player, answer in session["submissions"].items():
            proposed[player] = self._mock_ai_score_leader(answer)
        session["ai_scores_proposed"] = proposed
        session["od_accepted"] = False

    def committee_verify_scores(self, session_id: int, tolerance: int = 2) -> None:
        """
        Committee recomputes scores and checks equivalence vs leader proposal.
        If within tolerance per dimension, accept proposal; otherwise update
        flagged players to committee scores. Mixed acceptance is allowed.
        """
        session = self.sessions[session_id]
        if not session["ai_scores_proposed"]:
            raise Exception("No leader proposal to verify")

        accepted = {}
        proposal = session["ai_scores_proposed"]
        for player, proposed_scores in proposal.items():
            committee_scores = self._mock_ai_score_committee(session["submissions"][player])
            if self._equivalent_scores(proposed_scores, committee_scores, tolerance):
                accepted[player] = proposed_scores
            else:
                # Replace with committee's recomputation
                accepted[player] = committee_scores

        session["ai_scores"] = accepted
        session["od_accepted"] = True

    def challenge_score(self, session_id: int, challenger: str, target_player: str, bond_xp: int) -> None:
        """
        Player challenges an accepted AI score by posting an XP bond.
        """
        session = self.sessions[session_id]
        if target_player not in session["ai_scores"]:
            raise Exception("No accepted score to challenge")
        session["appeals"].append({
            "challenger": challenger,
            "target": target_player,
            "bond": bond_xp
        })

    def resolve_appeals(self, session_id: int) -> None:
        """
        Committee re-evaluates challenged scores.
        In this skeleton, outcomes are randomized to illustrate flow.
        """
        session = self.sessions[session_id]
        for appeal in session["appeals"]:
            target = appeal["target"]
            challenger = appeal["challenger"]
            bond = appeal["bond"]

            ai_was_wrong = random.choice([True, False])  # mock decision

            if ai_was_wrong:
                # Adjust score upward slightly to reflect correction; reward challenger
                session["ai_scores"][target]["total"] += 2
                self.season_xp[challenger] = self.season_xp.get(challenger, 0) + bond
            else:
                # Slash bond from challenger's season XP (not going below zero)
                self.season_xp[challenger] = max(0, self.season_xp.get(challenger, 0) - bond)

        # Clear appeals after resolution
        session["appeals"] = []

    # -----------------------------
    # Finalization
    # -----------------------------

    def finalize_round(self, session_id: int, human_weight: float = 0.6, ai_weight: float = 0.4) -> None:
        """
        Combine human votes and AI scores to produce final ranking.
        Distribute XP based on placement.
        """
        session = self.sessions[session_id]
        players_with_answers = list(session["submissions"].keys())

        for player in players_with_answers:
            human_score = session["votes"].get(player, 0)
            ai_score = session["ai_scores"].get(player, {}).get("total", 0)
            final = (human_weight * float(human_score)) + (ai_weight * float(ai_score))
            session["final_scores"][player] = final

        self._distribute_xp(session_id)

    def _distribute_xp(self, session_id: int) -> None:
        """
        Simple XP distribution:
        - base XP for participation
        - bonus XP decreasing by rank
        """
        session = self.sessions[session_id]
        ranked: List[tuple] = sorted(
            session["final_scores"].items(),
            key=lambda kv: kv[1],
            reverse=True
        )

        for rank, (player, _) in enumerate(ranked):
            base_xp = 5
            bonus = max(0, 10 - rank * 2)  # 10, 8, 6, ...
            self.season_xp[player] = self.season_xp.get(player, 0) + base_xp + bonus

    # -----------------------------
    # Helpers (mock LLM + scoring logic)
    # -----------------------------

    def _generate_prompt(self) -> str:
        prompts = [
            "Explain Optimistic Democracy as if you are a sports commentator.",
            "Describe GenLayer to a five-year-old.",
            "Pitch Intelligent Contracts as a startup idea.",
            "Summarize last week's GenLayer highlights in 2 sentences.",
            "Explain why subjective scoring needs consensus."
        ]
        return random.choice(prompts)

    def _mock_ai_score_leader(self, answer: str) -> dict:
        """
        Leader's proposed AI scores (mocked).
        """
        clarity = random.randint(4, 10)
        creativity = random.randint(4, 10)
        relevance = random.randint(4, 10)
        return {
            "clarity": clarity,
            "creativity": creativity,
            "relevance": relevance,
            "total": clarity + creativity + relevance
        }

    def _mock_ai_score_committee(self, answer: str) -> dict:
        """
        Committee recomputation (mocked), slightly different distribution.
        """
        clarity = random.randint(3, 10)
        creativity = random.randint(3, 10)
        relevance = random.randint(3, 10)
        return {
            "clarity": clarity,
            "creativity": creativity,
            "relevance": relevance,
            "total": clarity + creativity + relevance
        }

    @staticmethod
    def _equivalent_scores(a: dict, b: dict, tol: int) -> bool:
        """
        Equivalence check per dimension within tolerance.
        """
        dims = ["clarity", "creativity", "relevance"]
        for d in dims:
            if abs(int(a.get(d, 0)) - int(b.get(d, 0))) > tol:
                return False
        return True
