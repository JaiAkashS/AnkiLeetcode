from typing import List, Dict
import json
import os
from src.types.models import Problem

class Storage:
    def __init__(self, storage_file: str = 'problems.json'):
        self.storage_file = storage_file
        self.load_data()

    def load_data(self) -> None:
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as file:
                raw = json.load(file)
                self.data = [Problem.from_dict(p) for p in raw]
        else:
            self.data = []

    def save_data(self) -> None:
        with open(self.storage_file, 'w') as file:
            json.dump([p.to_dict() for p in self.data], file, indent=4)

    def add_problem(self, problem: Problem) -> None:
        self.data.append(problem)
        self.save_data()

    def get_problems(self) -> List[Problem]:
        return self.data

    def clear_data(self) -> None:
        self.data = []
        self.save_data()