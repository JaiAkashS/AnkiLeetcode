def validate_problem_statement(statement):
    if not statement or len(statement) < 10:
        raise ValueError("Problem statement must be at least 10 characters long.")
    return True

def format_solution(solution):
    return solution.strip()

def load_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        return []

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        file.writelines(data)