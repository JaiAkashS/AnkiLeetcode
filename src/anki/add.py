
from src.data.storage import Storage
from src.anki.utils import validate_problem_statement, format_solution
from src.types.models import Problem

def add_problem():
    """Wrapper for interactive problem addition, for compatibility with main.py import."""
    return add_problem_interactive()

def add_problem_interactive():
    # Prompt for problem title
    title = input("Enter problem title: ").strip()
    # Prompt for tags (comma separated)
    tags_input = input("Enter tags (comma separated): ").strip()
    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    # Prompt for multi-line problem statement
    print("Enter problem statement (end with a single line containing only 'END'):")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    problem_statement = '\n'.join(lines)
    validate_problem_statement(problem_statement)
    # Prompt for solution code (multi-line, end with END)
    print("Enter solution code (end with a single line containing only 'END'):")
    code_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        code_lines.append(line)
    solution_code = '\n'.join(code_lines)
    solution_code = format_solution(solution_code)
    # Prompt for notes
    notes = input("Enter any notes for this problem (optional): ").strip()
    # Prompt for difficulty
    difficulty = input("Enter difficulty (Easy/Medium/Hard): ").strip().capitalize() or "Unrated"
    storage = Storage()
    problem = Problem(
        title=title,
        statement=problem_statement,
        solution=solution_code,
        tags=tags,
        notes=notes,
        difficulty=difficulty
    )
    storage.add_problem(problem)

def list_problems():
    # This function retrieves and returns a list of all added problems.
    storage = Storage()
    return storage.get_problems()

def delete_problem(problem_id):
    # This function deletes a problem from the storage based on its ID.
    storage = Storage()
    problems = storage.get_problems()
    if 0 <= problem_id < len(problems):
        del problems[problem_id]
        storage.data = problems
        storage.save_data()

def update_problem(problem_id, new_problem_statement=None, new_solution_code=None):
    # This function updates an existing problem's statement or solution.
    storage = Storage()
    problems = storage.get_problems()
    if 0 <= problem_id < len(problems):
        if new_problem_statement:
            problems[problem_id]["statement"] = new_problem_statement
        if new_solution_code:
            problems[problem_id]["solution"] = format_solution(new_solution_code)
        storage.data = problems
        storage.save_data()