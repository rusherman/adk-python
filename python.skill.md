# Python Skill

Python编程技能知识库，涵盖基础语法、高级特性和最佳实践。

## 基础语法

### 变量和数据类型

```python
# 基本类型
name = "Alice"          # str
age = 25                # int
height = 1.75           # float
is_active = True        # bool

# 容器类型
numbers = [1, 2, 3]           # list
unique = {1, 2, 3}            # set
person = {"name": "Alice"}    # dict
coords = (10, 20)             # tuple
```

### 函数定义

```python
# 基本函数
def greet(name: str) -> str:
    """打招呼函数"""
    return f"Hello, {name}!"

# 带默认参数
def greet(name: str = "World") -> str:
    return f"Hello, {name}!"

# *args 和 **kwargs
def flexible(*args, **kwargs):
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

# Lambda表达式
square = lambda x: x ** 2
```

### 类和面向对象

```python
from dataclasses import dataclass
from typing import Optional

# 传统类定义
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"

# 使用dataclass（推荐）
@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None
```

## 高级特性

### 装饰器

```python
import functools
from typing import Callable, TypeVar

T = TypeVar('T')

# 简单装饰器
def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

# 带参数的装饰器
def retry(times: int = 3):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == times - 1:
                        raise
        return wrapper
    return decorator
```

### 上下文管理器

```python
from contextlib import contextmanager

# 使用类
class FileHandler:
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        self.file = open(self.filename, 'r')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

# 使用contextmanager装饰器
@contextmanager
def timer_context():
    import time
    start = time.time()
    yield
    print(f"Elapsed: {time.time() - start:.2f}s")
```

### 异步编程

```python
import asyncio
from typing import List

async def fetch_data(url: str) -> dict:
    """模拟异步获取数据"""
    await asyncio.sleep(1)
    return {"url": url, "data": "..."}

async def fetch_all(urls: List[str]) -> List[dict]:
    """并发获取多个URL"""
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)

# 运行
asyncio.run(fetch_all(["url1", "url2", "url3"]))
```

## 最佳实践

### 类型提示

```python
from typing import List, Dict, Optional, Union, Callable

def process_items(
    items: List[str],
    callback: Optional[Callable[[str], str]] = None,
) -> Dict[str, int]:
    """处理项目列表"""
    result = {}
    for item in items:
        if callback:
            item = callback(item)
        result[item] = len(item)
    return result
```

### 错误处理

```python
class CustomError(Exception):
    """自定义异常"""
    pass

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("除数不能为0")
    return a / b

try:
    result = divide(10, 0)
except ValueError as e:
    print(f"错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
finally:
    print("清理资源")
```

### 代码组织

```
my_project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── pyproject.toml
└── README.md
```
