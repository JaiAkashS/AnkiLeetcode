from src.data.storage import Storage
import re
import argparse
import sys


def normalize_tag(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'[^a-z0-9]', '', s.lower())


def parse_index_list(spec: str):
    """Parse an index list like '1,2,5-7' into zero-based indices."""
    out = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            try:
                a_i = int(a) - 1
                b_i = int(b) - 1
            except ValueError:
                raise ValueError(f"Invalid range: {part}")
            if a_i <= b_i:
                out.update(range(a_i, b_i + 1))
            else:
                out.update(range(b_i, a_i + 1))
        else:
            try:
                idx = int(part) - 1
            except ValueError:
                raise ValueError(f"Invalid index: {part}")
            out.add(idx)
    return sorted(i for i in out if i >= 0)


def batch_update_by_indices(storage: Storage, indices, set_to: bool):
    problems = storage.get_problems()
    changed = 0
    for i in indices:
        if 0 <= i < len(problems):
            p = problems[i]
            if getattr(p, 'skip_recall', False) != set_to:
                p.skip_recall = set_to
                changed += 1
    if changed:
        storage.save_data()
    return changed


def batch_update_by_tag(storage: Storage, tag: str, set_to: bool):
    tag_norm = normalize_tag(tag)
    problems = storage.get_problems()
    changed = 0
    for p in problems:
        if any(normalize_tag(t) == tag_norm for t in p.tags) and getattr(p, 'skip_recall', False) != set_to:
            p.skip_recall = set_to
            changed += 1
    if changed:
        storage.save_data()
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(description="Batch mark/unmark problems to skip recall")
    parser.add_argument('--indices', '-i', help="Comma-separated 1-based indices or ranges, e.g. '1,3,5-7'")
    parser.add_argument('--tag', '-t', help="Tag to match (normalized, supports spaces)")
    parser.add_argument('--action', '-a', choices=['mark', 'unmark'], help="mark = skip recall, unmark = include in recall")
    parser.add_argument('--all', action='store_true', help="Apply to all problems")
    args = parser.parse_args(argv)

    storage = Storage()
    problems = storage.get_problems()

    # If no CLI selection provided, run interactive mode
    if not any([args.indices, args.tag, args.all, args.action]):
        print("Batch Skip Recall Manager - interactive")
        print("List of problems:")
        for idx, p in enumerate(problems, start=1):
            print(f"{idx}. [{ 'X' if getattr(p, 'skip_recall', False) else ' ' }] {p.title} (tags: {', '.join(p.tags)})")
        spec = input("Enter indices (comma/range), 'tag:<tag>', 'all' or leave blank to cancel: ").strip()
        if not spec:
            print("Cancelled.")
            return 0
        if spec.lower().startswith('tag:'):
            tag = spec.split(':', 1)[1].strip()
            op = input("Action (mark/unmark): ").strip().lower()
            if op not in ('mark', 'unmark'):
                print("Invalid action")
                return 2
            set_to = (op == 'mark')
            changed = batch_update_by_tag(storage, tag, set_to)
            print(f"Updated {changed} problems for tag '{tag}'")
            return 0
        if spec.lower() == 'all':
            op = input("Action for all (mark/unmark): ").strip().lower()
            if op not in ('mark', 'unmark'):
                print("Invalid action")
                return 2
            set_to = (op == 'mark')
            changed = 0
            for p in problems:
                if getattr(p, 'skip_recall', False) != set_to:
                    p.skip_recall = set_to
                    changed += 1
            if changed:
                storage.save_data()
            print(f"Updated {changed} problems (all)")
            return 0
        # otherwise treat as index spec
        try:
            indices = parse_index_list(spec)
        except ValueError as e:
            print(f"Error parsing indices: {e}")
            return 2
        op = input("Action (mark/unmark): ").strip().lower()
        if op not in ('mark', 'unmark'):
            print("Invalid action")
            return 2
        set_to = (op == 'mark')
        changed = batch_update_by_indices(storage, indices, set_to)
        print(f"Updated {changed} problems by indices")
        return 0

    # Non-interactive CLI mode
    if args.action is None:
        print("--action is required in CLI mode. Use --action mark|unmark")
        return 2
    set_to = (args.action == 'mark')

    total_changed = 0
    if args.indices:
        try:
            indices = parse_index_list(args.indices)
        except ValueError as e:
            print(f"Invalid index list: {e}")
            return 2
        changed = batch_update_by_indices(storage, indices, set_to)
        print(f"Updated {changed} problems by indices")
        total_changed += changed

    if args.tag:
        changed = batch_update_by_tag(storage, args.tag, set_to)
        print(f"Updated {changed} problems by tag '{args.tag}'")
        total_changed += changed

    if args.all:
        changed = 0
        for p in problems:
            if getattr(p, 'skip_recall', False) != set_to:
                p.skip_recall = set_to
                changed += 1
        if changed:
            storage.save_data()
        print(f"Updated {changed} problems (all)")
        total_changed += changed

    if total_changed == 0:
        print("No changes made.")
    else:
        print(f"Total updated: {total_changed}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
