from src.data.storage import Storage
import random
import datetime
import re

# Configurable tag for bored mode. Set to empty string for any tag.
# Change this value to the tag you want bored mode to use by default.
BORED_TAG = ""  # e.g. 'array', 'graph', or '' for any


def print_statistics():
    storage = Storage()
    problems = storage.get_problems()
    print(f"Total problems: {len(problems)}")
    # Count by difficulty
    diff_count = {}
    for p in problems:
        diff = p.difficulty or "Unrated"
        diff_count[diff] = diff_count.get(diff, 0) + 1
    print("Problems by difficulty:")
    for diff, count in diff_count.items():
        print(f"  {diff}: {count}")
    # Count by tags
    tag_count = {}
    for p in problems:
        for tag in p.tags:
            tag_count[tag] = tag_count.get(tag, 0) + 1
    print("Problems by tag:")
    tag_count = dict(sorted(tag_count.items(), key=lambda item: item[1], reverse=True))
    for tag, count in tag_count.items():
        print(f"  {tag}: {count}")
    # skip_recall summary
    skipped = len([p for p in problems if getattr(p, 'skip_recall', False)])
    print(f"Skipped for recall: {skipped}")


def review_daily():
    """Review only problems scheduled for today (next_review == today)."""
    storage = Storage()
    problems = storage.get_problems()
    today = datetime.date.today().isoformat()
    due_today = [p for p in problems if p.next_review == today]
    if not due_today:
        print("No problems scheduled for review today!")
        return
    print(f"{len(due_today)} problem(s) scheduled for today.")
    for idx, problem in enumerate(due_today):
        print(f"\nProblem {idx+1}: {problem.title}")
        print(f"Tags: {', '.join(problem.tags)} | Difficulty: {problem.difficulty}")
        print(problem.statement)
        input("Try to recall the solution. Press Enter to reveal...")
        print("Solution:")
        print(problem.solution)
        correct = input("Did you recall it correctly? (y/n): ").strip().lower() == 'y'
        difficulty = input("Rate the difficulty (Easy/Medium/Hard): ").strip().capitalize() or problem.difficulty
        problem.mark_reviewed(success=correct, difficulty=difficulty)
        if problem.notes:
            print(f"Notes: {problem.notes}")
    storage.save_data()


def review_bored(tag_override=None):
    """Review a random problem using a tag.

    Tag precedence:
      1) tag_override argument (if provided)
      2) BORED_TAG environment variable (BORED_TAG)
      3) BORED_TAG constant in this module

    An empty tag means "any".
    """
    storage = Storage()
    problems = storage.get_problems()

    # Helper: normalize tags so 'two pointers', 'two-pointers', 'two_pointers' all match
    def normalize_tag(s: str) -> str:
        if not s:
            return ""
        return re.sub(r'[^a-z0-9]', '', s.lower())

    # Determine which tag to use (raw) and its normalized form
    if tag_override is not None:
        tag_raw = str(tag_override).strip()
    else:
        import os
        env_tag = os.environ.get('BORED_TAG')
        if env_tag is not None:
            tag_raw = env_tag.strip()
        else:
            tag_raw = BORED_TAG.strip()

    tag_norm = normalize_tag(tag_raw)

    # Exclude problems that are marked to skip recall
    filtered = [p for p in problems if not getattr(p, 'skip_recall', False)]
    if tag_norm:
        filtered = [p for p in filtered if any(normalize_tag(t) == tag_norm for t in p.tags)]
    if not filtered:
        if tag_norm:
            print(f"No problems found for the configured bored tag: '{tag_raw}'. Trying any tag instead.")
            # fallback to any problem that's not skipped
            filtered = [p for p in problems if not getattr(p, 'skip_recall', False)]
        if not filtered:
            print("No problems available to select for bored mode.")
            return
    problem = random.choice(filtered)
    print(f"\nRandom Problem: {problem.title}")
    print(f"Tags: {', '.join(problem.tags)} | Difficulty: {problem.difficulty}")
    print(problem.statement)
    input("Try to recall the solution. Press Enter to reveal...")
    print("Solution:")
    print(problem.solution)
    correct = input("Did you recall it correctly? (y/n): ").strip().lower() == 'y'
    difficulty = input("Rate the difficulty (Easy/Medium/Hard): ").strip().capitalize() or problem.difficulty
    problem.mark_reviewed(success=correct, difficulty=difficulty)
    if problem.notes:
        print(f"Notes: {problem.notes}")
    # Allow toggling whether this specific problem should be excluded from future recall/bored sessions
    current_skip = getattr(problem, 'skip_recall', False)
    print(f"Currently skipped for recall: {current_skip}")
    toggle = input("Toggle skip recall for this problem? (y/N): ").strip().lower()
    if toggle == 'y':
        problem.skip_recall = not current_skip
        print(f"skip_recall set to {problem.skip_recall}")
    storage.save_data()

def review_problems(mode):
    """Review problems in two modes: 1 (recall), 2 (blanks)."""
    storage = Storage()
    problems = storage.get_problems()

    # --- Filtering ---
    tag_filter_raw = input("Filter by tag (leave blank for all): ").strip()
    diff_filter = input("Filter by difficulty (Easy/Medium/Hard/leave blank for all): ").strip().capitalize()
    status_filter = input("Filter by status (unseen/failed/due/all): ").strip().lower() or "due"
    filtered = [p for p in problems if not getattr(p, 'skip_recall', False)]
    # use same normalization helper from above
    def normalize_tag(s: str) -> str:
        if not s:
            return ""
        return re.sub(r'[^a-z0-9]', '', s.lower())

    tag_filter = normalize_tag(tag_filter_raw)
    if tag_filter:
        filtered = [p for p in filtered if any(normalize_tag(t) == tag_filter for t in p.tags)]
    if diff_filter:
        filtered = [p for p in filtered if p.difficulty == diff_filter]
    if status_filter == "unseen":
        filtered = [p for p in filtered if p.review_count == 0]
    elif status_filter == "failed":
        filtered = [p for p in filtered if p.review_count > 0 and p.success_count < p.review_count]
    elif status_filter == "due":
        filtered = [p for p in filtered if p.is_due()]
    # else "all": no further filtering

    if not filtered:
        print("No problems match the selected filters.")
        return

    random.shuffle(filtered)
    for idx, problem in enumerate(filtered):
        print(f"\nProblem {idx+1}: {problem.title}")
        print(f"Tags: {', '.join(problem.tags)} | Difficulty: {problem.difficulty}")
        print(problem.statement)
        # Allow toggling whether a problem should be excluded from recall sessions
        toggle = input("Toggle skip recall for this problem? (y/N): ").strip().lower()
        if toggle == 'y':
            problem.skip_recall = not getattr(problem, 'skip_recall', False)
            print(f"skip_recall set to {problem.skip_recall}")
        if mode == '1':
            input("Try to recall the solution. Press Enter to reveal...")
            print("Solution:")
            print(problem.solution)
            correct = input("Did you recall it correctly? (y/n): ").strip().lower() == 'y'
        elif mode == '2':
            lines = problem.solution.splitlines()
            blank_indices = [i for i, line in enumerate(lines) if any(kw in line for kw in ['for ', 'while ', 'if ', 'else', 'elif', 'return'])]
            blanked = []
            for i, line in enumerate(lines):
                if i in blank_indices:
                    blanked.append("...")
                else:
                    blanked.append(line)
            print("\n".join(blanked))
            input("Try to fill in the blanks. Press Enter to reveal full solution...")
            print(problem.solution)
            correct = input("Did you recall the blanks correctly? (y/n): ").strip().lower() == 'y'
        else:
            print("Invalid review mode.")
            break
        # Ask for difficulty rating after review
        difficulty = input("Rate the difficulty (Easy/Medium/Hard): ").strip().capitalize() or problem.difficulty
        # Update review stats and schedule next review
        problem.mark_reviewed(success=correct, difficulty=difficulty)
        # Show notes after review
        if problem.notes:
            print(f"Notes: {problem.notes}")
    # Save updated problems
    storage.save_data()


if __name__ == "__main__":
    # Allow running this file directly to launch bored mode (used by run_bored_mode.bat)
    # Accept a CLI override: --tag TAG
    import argparse

    parser = argparse.ArgumentParser(description="Run bored mode (pick a random problem by tag)")
    parser.add_argument('--tag', '-t', help='Override tag for bored mode (empty for any)')
    args = parser.parse_args()

    if args.tag is not None:
        review_bored(tag_override=args.tag)
    else:
        review_bored()