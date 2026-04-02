#!/usr/bin/env python3
"""Generate expanded test corpus (25 files)."""

from pathlib import Path

def generate_low_complexity(name):
    return f'''"""{name} - Low complexity module."""

def add(x, y):
    """Add two numbers."""
    return x + y

def subtract(x, y):
    """Subtract two numbers."""
    return x - y

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

def divide(x, y):
    """Divide two numbers."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y
'''

def generate_medium_complexity(name):
    return f'''"""{name} - Medium complexity module."""

def process_data(data, filter_func=None):
    """Process data with optional filtering."""
    results = []
    for item in data:
        if filter_func and not filter_func(item):
            continue
        if isinstance(item, (int, float)):
            results.append(item * 2)
        elif isinstance(item, str):
            results.append(item.upper())
        else:
            results.append(str(item))
    return results

def calculate_stats(numbers):
    """Calculate basic statistics."""
    if not numbers:
        return None
    
    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    
    sorted_nums = sorted(numbers)
    mid = count // 2
    if count % 2 == 0:
        median = (sorted_nums[mid-1] + sorted_nums[mid]) / 2
    else:
        median = sorted_nums[mid]
    
    return {{"mean": mean, "median": median, "count": count}}
'''

def generate_high_complexity(name):
    return f'''"""{name} - High complexity module."""

def complicated_processor(data, config, callbacks=None):
    """Complex data processor with many branches."""
    results = {{}}
    errors = []
    
    if not data:
        return None
    
    if config.get("validate"):
        for key, value in data.items():
            if key.startswith("_"):
                continue
            
            if isinstance(value, dict):
                if config.get("recursive"):
                    sub_result = complicated_processor(value, config, callbacks)
                    if sub_result:
                        results[key] = sub_result
            elif isinstance(value, list):
                processed = []
                for idx, item in enumerate(value):
                    if config.get("filter_nulls") and item is None:
                        continue
                    if config.get("transform"):
                        if isinstance(item, str):
                            processed.append(item.strip().lower())
                        elif isinstance(item, (int, float)):
                            processed.append(item * config.get("multiplier", 1))
                        else:
                            processed.append(item)
                    else:
                        processed.append(item)
                results[key] = processed
            else:
                results[key] = value
    
    if callbacks and "on_complete" in callbacks:
        try:
            callbacks["on_complete"](results)
        except Exception as e:
            errors.append(str(e))
    
    return results if not errors else None
'''

def generate_duplication(name):
    return f'''"""{name} - Code duplication patterns."""

def validate_user(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    if not data.get("email"):
        raise ValueError("Email required")
    return True

def validate_product(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    if not data.get("price"):
        raise ValueError("Price required")
    return True

def validate_order(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("user_id"):
        raise ValueError("User ID required")
    if not data.get("items"):
        raise ValueError("Items required")
    return True
'''

def generate_todo_issues(name):
    return '''"""Module with TODOs."""

def process(data):
    # TODO: Add error handling
    result = []
    for item in data:
        # TODO: Optimize this loop
        result.append(item * 2)
    # FIXME: Memory leak here
    return result
'''

def generate_dead_code_issues(name):
    return '''"""Module with dead code."""

def process(x):
    if x > 0:
        return x * 2
    return 0
    # Dead code below
    print("This never runs")
    y = x + 1
    return y
'''

def generate_long_function_issues(name):
    return '''"""Module with long function."""

def very_long_function(data, config, options, context):
    step1 = data.get("input")
    step2 = step1 * 2
    step3 = step2 + 10
    step4 = step3 / 2
    step5 = step4 - 5
    step6 = step5 * config.get("multiplier", 1)
    step7 = step6 + options.get("offset", 0)
    step8 = step7 / context.get("scale", 1)
    step9 = step8 * 2
    step10 = step9 + 100
    step11 = step10 - 50
    step12 = step11 / 2
    return step12
'''

def generate_complexity_spike_issues(name):
    return '''"""Module with complexity issues."""

def complex_function(a, b, c, d, e, f, g, h, i, j):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    return a + b + c + d
                return a + b + c
            return a + b
        return a
    return 0
'''

def generate_many_params_issues(name):
    return '''"""Module with many parameters."""

def too_many_params(a, b, c, d, e, f, g, h, i, j, k, l, m):
    return a + b + c + d + e + f
'''

def generate_mixed(name):
    return f'''"""{name} - Realistic mixed complexity module."""

import json
from pathlib import Path

class DataManager:
    def __init__(self, config):
        self.config = config
        self.cache = {{}}
    
    def load(self, filepath):
        path = Path(filepath)
        if not path.exists():
            return None
        
        if filepath in self.cache:
            return self.cache[filepath]
        
        with open(filepath) as f:
            data = json.load(f)
        
        processed = self._process(data)
        self.cache[filepath] = processed
        return processed
    
    def _process(self, data):
        if isinstance(data, list):
            return [self._process(item) for item in data]
        elif isinstance(data, dict):
            return {{k: self._process(v) for k, v in data.items()}}
        return data

def utility_function(items, predicate=None):
    if not items:
        return []
    results = []
    for item in items:
        if predicate is None or predicate(item):
            results.append(item)
    return results
'''

# Main
test_corpus = Path('test_corpus_expanded')
test_corpus.mkdir(exist_ok=True)

templates = [
    ("simple_math.py", "low"),
    ("simple_strings.py", "low"),
    ("simple_lists.py", "low"),
    ("simple_dicts.py", "low"),
    ("simple_io.py", "low"),
    ("medium_loops.py", "medium"),
    ("medium_conditionals.py", "medium"),
    ("medium_functions.py", "medium"),
    ("medium_classes.py", "medium"),
    ("medium_error_handling.py", "medium"),
    ("complex_nested.py", "high"),
    ("complex_recursion.py", "high"),
    ("complex_state_machine.py", "high"),
    ("complex_parser.py", "high"),
    ("complex_algorithm.py", "high"),
    ("duplicate_validation.py", "dup"),
    ("duplicate_logging.py", "dup"),
    ("duplicate_api_calls.py", "dup"),
    ("issues_todo.py", "todo"),
    ("issues_dead_code.py", "dead"),
    ("issues_complexity_spike.py", "complexity"),
    ("issues_long_function.py", "long"),
    ("issues_many_params.py", "params"),
    ("mixed_realistic_1.py", "mixed"),
    ("mixed_realistic_2.py", "mixed"),
]

generators = {
    "low": generate_low_complexity,
    "medium": generate_medium_complexity,
    "high": generate_high_complexity,
    "dup": generate_duplication,
    "todo": generate_todo_issues,
    "dead": generate_dead_code_issues,
    "long": generate_long_function_issues,
    "complexity": generate_complexity_spike_issues,
    "params": generate_many_params_issues,
    "mixed": generate_mixed,
}

for filename, level in templates:
    filepath = test_corpus / filename
    content = generators[level](filename)
    filepath.write_text(content)
    print(f"Created: {filename}")

print(f"\n✅ Created {len(templates)} test files in {test_corpus}/")
