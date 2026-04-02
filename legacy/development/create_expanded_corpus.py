#!/usr/bin/env python3
"""Expand test corpus from 25 to 55+ files across 8 categories."""

import os

def create_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    test_dir = 'test_corpus'
    os.makedirs(f'{test_dir}/simple', exist_ok=True)
    os.makedirs(f'{test_dir}/medium', exist_ok=True)
    os.makedirs(f'{test_dir}/complex', exist_ok=True)
    os.makedirs(f'{test_dir}/duplicate', exist_ok=True)
    os.makedirs(f'{test_dir}/issues', exist_ok=True)
    os.makedirs(f'{test_dir}/mixed', exist_ok=True)
    os.makedirs(f'{test_dir}/edge', exist_ok=True)
    os.makedirs(f'{test_dir}/realistic', exist_ok=True)
    
    # SIMPLE (8 files) - existing 3 + 5 new
    simple_files = [
        ('simple/empty.py', ''),
        ('simple/single_func.py', 'def hello(): print("hello")'),
        ('simple/two_funcs.py', 'def a(): pass\ndef b(): pass'),
        ('simple/calc.py', '''
def add(x, y):
    return x + y

def sub(x, y):
    return x - y
'''),
        ('simple/greet.py', '''
def greet(name):
    return f"Hello, {name}!"

def farewell(name):
    return f"Goodbye, {name}!"
'''),
        ('simple/math_ops.py', '''
def square(x):
    return x * x

def cube(x):
    return x * x * x
'''),
        ('simple/string_utils.py', '''
def reverse(s):
    return s[::-1]

def capitalize(s):
    return s.capitalize()
'''),
        ('simple/list_ops.py', '''
def first(lst):
    return lst[0] if lst else None

def last(lst):
    return lst[-1] if lst else None
'''),
    ]
    
    # MEDIUM (10 files) - existing 5 + 5 new
    medium_files = [
        ('medium/class_basic.py', '''
class User:
    def __init__(self, name):
        self.name = name
    def greet(self):
        return f"Hi {self.name}"
'''),
        ('medium/conditional.py', '''
def grade(score):
    if score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    else: return "F"
'''),
        ('medium/loops.py', '''
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
'''),
        ('medium/recursion.py', '''
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
'''),
        ('medium/exceptions.py', '''
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
'''),
        ('medium/file_handler.py', '''
class FileHandler:
    def __init__(self, path):
        self.path = path
        self.file = None
    
    def open(self):
        self.file = open(self.path, 'r')
        return self.file
    
    def close(self):
        if self.file:
            self.file.close()
'''),
        ('medium/validator.py', '''
def validate_email(email):
    if '@' not in email:
        return False
    if '.' not in email.split('@')[1]:
        return False
    return True

def validate_phone(phone):
    digits = ''.join(c for c in phone if c.isdigit())
    return len(digits) >= 10
'''),
        ('medium/counter.py', '''
from collections import Counter

def word_freq(text):
    words = text.lower().split()
    return Counter(words)

def top_words(text, n=5):
    freq = word_freq(text)
    return freq.most_common(n)
'''),
        ('medium/cache.py', '''
class SimpleCache:
    def __init__(self):
        self._data = {}
    
    def get(self, key):
        return self._data.get(key)
    
    def set(self, key, value):
        self._data[key] = value
    
    def clear(self):
        self._data.clear()
'''),
        ('medium/api_client.py', '''
import json

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        return {"status": 200, "url": url}
    
    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        return {"status": 201, "data": data}
'''),
    ]
    
    # COMPLEX (8 files) - existing 5 + 3 new
    complex_files = [
        ('complex/nested.py', '''
def process(data):
    for item in data:
        if item.active:
            for sub in item.children:
                if sub.valid:
                    process(sub)
'''),
        ('complex/metaclass.py', '''
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass
'''),
        ('complex/decorators.py', '''
from functools import wraps

def retry(max_attempts):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    continue
            raise Exception("Max retries")
        return wrapper
    return decorator

@retry(3)
def fetch():
    pass
'''),
        ('complex/context_manager.py', '''
class Database:
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def connect(self): pass
    def close(self): pass
    def query(self, sql): pass
'''),
        ('complex/generators.py', '''
def fib_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def chunk_iterator(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]
'''),
        ('complex/async_example.py', '''
import asyncio

async def fetch_data(url):
    await asyncio.sleep(1)
    return {"url": url, "data": "content"}

async def main():
    tasks = [fetch_data(f"url_{i}") for i in range(5)]
    results = await asyncio.gather(*tasks)
    return results
'''),
        ('complex/state_machine.py', '''
class StateMachine:
    def __init__(self):
        self.state = 'idle'
        self.transitions = {
            'idle': {'start': 'running'},
            'running': {'pause': 'paused', 'stop': 'idle'},
            'paused': {'resume': 'running', 'stop': 'idle'}
        }
    
    def trigger(self, event):
        if event in self.transitions.get(self.state, {}):
            self.state = self.transitions[self.state][event]
            return True
        return False
'''),
        ('complex/pipeline.py', '''
class Pipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, func):
        self.steps.append(func)
        return self
    
    def execute(self, data):
        result = data
        for step in self.steps:
            result = step(result)
        return result
    
    def compose(self, other):
        new_pipe = Pipeline()
        new_pipe.steps = self.steps + other.steps
        return new_pipe
'''),
    ]
    
    # DUPLICATE (6 files) - existing 3 + 3 new
    duplicate_files = [
        ('duplicate/exact_dup.py', '''
def func_a(x):
    if x > 0:
        return x * 2
    return 0

def func_b(x):
    if x > 0:
        return x * 2
    return 0
'''),
        ('duplicate/validation_dup.py', '''
def validate_user(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    return True

def validate_product(data):
    if data is None:
        raise ValueError("Data is None")
    if not data.get("name"):
        raise ValueError("Name required")
    return True
'''),
        ('duplicate/crud_dup.py', '''
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()

def get_product(product_id):
    return db.query(Product).filter(Product.id == product_id).first()

def get_order(order_id):
    return db.query(Order).filter(Order.id == order_id).first()
'''),
        ('duplicate/process_dup.py', '''
def process_items_a(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result

def process_items_b(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result
'''),
        ('duplicate/handler_dup.py', '''
class UserHandler:
    def get(self, id):
        return db.get_user(id)
    def create(self, data):
        return db.create_user(data)

class ProductHandler:
    def get(self, id):
        return db.get_product(id)
    def create(self, data):
        return db.create_product(data)
'''),
        ('duplicate/transform_dup.py', '''
def transform_a(data):
    result = []
    for item in data:
        cleaned = item.strip().lower()
        if cleaned:
            result.append(cleaned)
    return result

def transform_b(data):
    result = []
    for item in data:
        cleaned = item.strip().lower()
        if cleaned:
            result.append(cleaned)
    return result
'''),
    ]
    
    # ISSUES (8 files) - existing 5 + 3 new
    issues_files = [
        ('issues/long_lines.py', 'x = "' + 'a' * 200 + '"'),
        ('issues/deep_nesting.py', '''
def deep():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        if True:
                            pass
'''),
        ('issues/many_params.py', 'def many(a, b, c, d, e, f, g, h, i, j, k): pass'),
        ('issues/many_locals.py', '''
def locals_test():
    a, b, c, d, e = 1, 2, 3, 4, 5
    f, g, h, i, j = 6, 7, 8, 9, 10
    k, l, m, n, o = 11, 12, 13, 14, 15
    return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o
'''),
        ('issues/long_func.py', '''
def long_func():
    x1 = 1
    x2 = 2
    x3 = 3
    x4 = 4
    x5 = 5
    x6 = 6
    x7 = 7
    x8 = 8
    x9 = 9
    x10 = 10
    x11 = 11
    x12 = 12
    x13 = 13
    x14 = 14
    x15 = 15
    return x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15
'''),
        ('issues/high_complexity.py', '''
def complex_decision(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return "A"
            elif z < 0:
                return "B"
            else:
                return "C"
        elif y < 0:
            return "D"
        else:
            if z > 0:
                return "E"
            return "F"
    elif x < 0:
        return "G"
    else:
        return "H"
'''),
        ('issues/dead_code.py', '''
def with_dead_code():
    x = 1  # unused
    y = 2
    result = y * 2
    return result
    x = 3  # unreachable
    return x
'''),
        ('issues/long_lambda.py', '''
process = lambda data: [item for item in data if item.active and item.score > 50 and item.category in ['A', 'B']]
'''),
    ]
    
    # MIXED (6 files) - existing 4 + 2 new
    mixed_files = [
        ('mixed/todo_dead.py', '''
def process():
    # TODO: implement this
    pass

def old_func():
    x = 1  # never used
    return 2
'''),
        ('mixed/complex_todo.py', '''
def complex_logic():
    for i in range(10):
        if i % 2 == 0:
            for j in range(5):
                # FIXME: optimize this
                pass
'''),
        ('mixed/duplicate_todo.py', '''
def validate_a(x):
    if x > 0:
        return x
    return 0

def validate_b(x):
    if x > 0:
        return x
    return 0

# TODO: refactor duplicates
'''),
        ('mixed/all_issues.py', '''
def problematic():
    # TODO: fix this
    x1, x2, x3, x4, x5 = 1, 2, 3, 4, 5
    unused = 999
    if x1:
        if x2:
            if x3:
                return x1 + x2 + x3 + x4 + x5
'''),
        ('mixed/mixed_quality.py', '''
class GoodCode:
    def clean(self):
        return "nice"

def bad_func():  # TODO: refactor
    x = 1
    y = 2
    z = 3  # unused
    if x:
        if y:
            return x + y
'''),
        ('mixed/partial_issues.py', '''
def okay_func():
    return "this is fine"

def bad_func():
    # FIXME: performance
    result = []
    for i in range(1000):
        if i % 2 == 0:
            if i % 3 == 0:
                result.append(i)
    return result
'''),
    ]
    
    # EDGE CASES (5 files) - existing 0 + 5 new
    edge_files = [
        ('edge/one_liner.py', 'f = lambda x: x * 2'),
        ('edge/only_comments.py', '# This is a comment\n# Another comment'),
        ('edge/only_strings.py', '"hello"\n"world"'),
        ('edge/unicode.py', '''
def 日本語関数(引数):
    return f"こんにちは {引数}"

def emoji_test():
    return "🐍 🚀 💻"
'''),
        ('edge/special_chars.py', '''
def test__special__name__():
    """Docstring with special chars: <>&\"'"""
    x__ = 1
    _private = 2
    return x__ + _private
'''),
    ]
    
    # REALISTIC (10 files) - existing 3 + 7 new
    realistic_files = [
        ('realistic/api_routes.py', '''
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify([])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return jsonify(data), 201
'''),
        ('realistic/data_processor.py', '''
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.cache = {}
    
    def process(self, data):
        if data['id'] in self.cache:
            return self.cache[data['id']]
        result = self.transform(data)
        self.cache[data['id']] = result
        return result
    
    def transform(self, data):
        return {k: v.upper() if isinstance(v, str) else v 
                for k, v in data.items()}
'''),
        ('realistic/config_loader.py', '''
import json
import os

def load_config(path=None):
    if path is None:
        path = os.getenv('CONFIG_PATH', 'config.json')
    
    with open(path) as f:
        return json.load(f)

def merge_configs(base, override):
    result = base.copy()
    result.update(override)
    return result
'''),
        ('realistic/logger.py', '''
import logging
import sys

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
'''),
        ('realistic/auth.py', '''
from functools import wraps

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = kwargs.get('auth_token')
        if not auth:
            raise PermissionError("No auth token")
        return func(*args, **kwargs)
    return wrapper

def check_role(user, required_role):
    return user.get('role') == required_role
'''),
        ('realistic/validation.py', '''
import re

def validate_username(username):
    if not username:
        return False, "Username required"
    if len(username) < 3:
        return False, "Too short"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Invalid characters"
    return True, None

def validate_password(password):
    if len(password) < 8:
        return False, "Too short"
    if not any(c.isupper() for c in password):
        return False, "Need uppercase"
    if not any(c.isdigit() for c in password):
        return False, "Need digit"
    return True, None
'''),
        ('realistic/db_models.py', '''
from datetime import datetime

class BaseModel:
    def __init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def save(self):
        self.updated_at = datetime.now()
        # TODO: implement actual save
        pass

class User(BaseModel):
    def __init__(self, name, email):
        super().__init__()
        self.name = name
        self.email = email
'''),
        ('realistic/http_client.py', '''
import urllib.request
import json

class HTTPClient:
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url
        self.timeout = timeout
    
    def get(self, path):
        url = f"{self.base_url}{path}"
        with urllib.request.urlopen(url, timeout=self.timeout) as resp:
            return json.loads(resp.read())
    
    def post(self, path, data):
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())
'''),
        ('realistic/csv_parser.py', '''
import csv
from io import StringIO

def parse_csv(content, delimiter=','):
    reader = csv.DictReader(StringIO(content), delimiter=delimiter)
    return list(reader)

def write_csv(rows, fields, delimiter=','):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
'''),
        ('realistic/task_queue.py', '''
from queue import Queue
from threading import Thread, Lock

class TaskQueue:
    def __init__(self, num_workers=4):
        self.queue = Queue()
        self.workers = []
        self.lock = Lock()
        self.results = {}
        
        for i in range(num_workers):
            t = Thread(target=self._worker)
            t.daemon = True
            t.start()
            self.workers.append(t)
    
    def submit(self, task_id, func, *args):
        self.queue.put((task_id, func, args))
    
    def _worker(self):
        while True:
            task_id, func, args = self.queue.get()
            try:
                result = func(*args)
                with self.lock:
                    self.results[task_id] = ('success', result)
            except Exception as e:
                with self.lock:
                    self.results[task_id] = ('error', str(e))
            finally:
                self.queue.task_done()
'''),
    ]
    
    # Write all files
    all_files = (simple_files + medium_files + complex_files + 
                 duplicate_files + issues_files + mixed_files + 
                 edge_files + realistic_files)
    
    for filepath, content in all_files:
        full_path = os.path.join(test_dir, filepath)
        create_file(full_path, content)
    
    # Count files
    count = sum(1 for _, _ in all_files)
    print(f"✅ Created {count} test files")
    
    # Print summary
    categories = {
        'simple': len(simple_files),
        'medium': len(medium_files),
        'complex': len(complex_files),
        'duplicate': len(duplicate_files),
        'issues': len(issues_files),
        'mixed': len(mixed_files),
        'edge': len(edge_files),
        'realistic': len(realistic_files),
    }
    
    print("\n📊 Corpus Summary:")
    for cat, num in categories.items():
        print(f"   {cat:12s}: {num} files")
    print(f"   {'─'*25}")
    print(f"   {'TOTAL':12s}: {count} files")


if __name__ == '__main__':
    main()
