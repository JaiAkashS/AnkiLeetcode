
import datetime

class Problem:
    def __init__(self, title, statement, solution, tags=None, notes=None, difficulty=None,
                 last_reviewed=None, next_review=None, review_count=0, success_count=0, ef=2.5, interval=1,
                 skip_recall=False):
        self.title = title
        self.statement = statement
        self.solution = solution
        self.tags = tags if tags is not None else []
        self.notes = notes or ""
        self.difficulty = difficulty or "Unrated"
        self.last_reviewed = last_reviewed
        self.next_review = next_review
        self.review_count = review_count
        self.success_count = success_count
        self.ef = ef  # Easiness factor for SM-2
        self.interval = interval  # Days until next review
        self.skip_recall = skip_recall

    def mark_reviewed(self, success, difficulty):
        self.last_reviewed = datetime.date.today().isoformat()
        self.review_count += 1
        if success:
            self.success_count += 1
        self.difficulty = difficulty
        # SM-2 scheduling
        self.ef = max(1.3, self.ef + 0.1 - (5 - (5 if success else 2)) * (0.08 + (5 - (5 if success else 2)) * 0.02))
        if self.review_count == 1:
            self.interval = 1
        elif self.review_count == 2:
            self.interval = 6
        else:
            self.interval = int(self.interval * self.ef)
        next_date = datetime.date.today() + datetime.timedelta(days=self.interval)
        self.next_review = next_date.isoformat()

    def is_due(self):
        if not self.next_review:
            return True
        return datetime.date.fromisoformat(self.next_review) <= datetime.date.today()

    def to_dict(self):
        return {
            "title": self.title,
            "statement": self.statement,
            "solution": self.solution,
            "tags": self.tags,
            "notes": self.notes,
            "difficulty": self.difficulty,
            "last_reviewed": self.last_reviewed,
            "next_review": self.next_review,
            "review_count": self.review_count,
            "success_count": self.success_count,
            "ef": self.ef,
            "interval": self.interval
            , "skip_recall": self.skip_recall
        }

    @staticmethod
    def from_dict(d):
        return Problem(
            title=d.get("title"),
            statement=d.get("statement"),
            solution=d.get("solution"),
            tags=d.get("tags", []),
            notes=d.get("notes", ""),
            difficulty=d.get("difficulty", "Unrated"),
            last_reviewed=d.get("last_reviewed"),
            next_review=d.get("next_review"),
            review_count=d.get("review_count", 0),
            success_count=d.get("success_count", 0),
            ef=d.get("ef", 2.5),
            interval=d.get("interval", 1),
            skip_recall=d.get("skip_recall", False)
        )

class Solution:
    def __init__(self, code, language='Python'):
        self.code = code
        self.language = language

    def __str__(self):
        return self.code

class Review:
    def __init__(self, problem: Problem):
        self.problem = problem

    def recall_solution(self):
        return self.problem.solution

    def partially_blank_solution(self, sections_to_blank):
        solution_lines = self.problem.solution.splitlines()
        for index in sections_to_blank:
            if 0 <= index < len(solution_lines):
                solution_lines[index] = '...'  # Indicate a blanked-out line
        return "\n".join(solution_lines)