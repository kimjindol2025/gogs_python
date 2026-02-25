# 🐍 Python 모범 사례 가이드 (gogs_python)

> **기록이 증명이다** - 분산 시스템의 Python 구현 표준

---

## 🎯 목차
1. PEP8 & 코드 스타일
2. 타입 힌팅 정책
3. 성능 최적화
4. 분산 시스템 패턴
5. 테스트 전략

---

## 1️⃣ **PEP8 & 코드 스타일**

### 표준 설정
```ini
# .flake8
[flake8]
max-line-length = 100
max-complexity = 10
ignore = E203, W503, E501
exclude = .git,__pycache__,.venv

# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py310']
```

### 명명 규칙
```python
# ✅ 좋은 예
class DataLakeProcessor:
    def __init__(self, buffer_size: int = 1024):
        self.buffer_size = buffer_size
        self._internal_state = {}  # private
    
    def process_map_task(self, data: List[Dict]) -> Dict:
        """Process map phase of MapReduce."""
        return self._execute_map(data)

# ❌ 나쁜 예
class DLP:  # 약자 사용
    def __init__(self, bs=1024):  # 타입 힌팅 없음
        self.BS = bs  # 상수처럼 보임
        self.state = {}
    
    def pmt(self, d):  # 함수명 약자
        return self.em(d)
```

### 최대 라인 길이: 100자
```python
# ✅ 좋음
very_long_variable_name = (
    some_function(param1, param2) + 
    another_function(param3, param4)
)

# ❌ 나쁨 (> 100자)
very_long_variable_name = some_function(param1, param2) + another_function(param3, param4)
```

---

## 2️⃣ **타입 힌팅 정책**

### 필수 타입 힌팅
```python
from typing import List, Dict, Optional, Callable, Any
from typing import Union, Tuple
import asyncio

# ✅ 완벽한 타입 힌팅
class DistributedProcessor:
    def __init__(
        self,
        worker_count: int,
        timeout_seconds: float = 30.0
    ) -> None:
        self.workers: List[Worker] = []
        self.results: Dict[str, Any] = {}
        self.config: Optional[Config] = None
    
    def process(
        self,
        data: List[Dict[str, Any]],
        callback: Optional[Callable[[Dict], None]] = None
    ) -> Dict[str, List[Any]]:
        """Process data with optional callback.
        
        Args:
            data: List of dictionaries to process
            callback: Optional callback function
            
        Returns:
            Dictionary mapping keys to processed values
            
        Raises:
            ValueError: If data is empty
        """
        if not data:
            raise ValueError("Data cannot be empty")
        return self._execute(data, callback)
    
    async def process_async(
        self,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Async version of process."""
        tasks = [self._process_one(item) for item in data]
        return await asyncio.gather(*tasks)
    
    def _execute(
        self,
        data: List[Dict[str, Any]],
        callback: Optional[Callable[[Dict], None]]
    ) -> Dict[str, List[Any]]:
        """Internal implementation."""
        pass
```

### mypy 검증
```bash
# 설정: mypy.ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

# 실행
mypy src/ --strict
```

---

## 3️⃣ **성능 최적화**

### 벤치마킹 패턴
```python
import timeit
from memory_profiler import profile

class PerformanceTest:
    @staticmethod
    def benchmark_map_reduce():
        """벤치마크: MapReduce 성능"""
        processor = MapReduceExecutor(workers=4)
        
        # 준비
        large_data = [
            {f"key_{i}": f"value_{i}"}
            for i in range(100000)
        ]
        
        # 측정: 3회 반복
        elapsed = timeit.timeit(
            lambda: processor.execute(large_data),
            number=3
        )
        
        avg_time = elapsed / 3
        throughput = len(large_data) / avg_time
        
        print(f"Average time: {avg_time:.3f}s")
        print(f"Throughput: {throughput:.0f} items/sec")
        
        return avg_time

    @profile  # memory_profiler 데코레이터
    def memory_intensive_operation(self, data: List[Dict]) -> Dict:
        """메모리 사용량 추적"""
        result = {}
        for item in data:
            # 처리 로직
            result[item["key"]] = self._process(item)
        return result

# 실행
if __name__ == "__main__":
    test = PerformanceTest()
    test.benchmark_map_reduce()
    # python -m memory_profiler memory_test.py
```

### 최적화 팁
```python
# ✅ 효율적
# 1. 리스트 컴프리헨션
result = [process(x) for x in data if x is not None]

# 2. 제너레이터 (메모리 절감)
def data_generator(large_file: str):
    with open(large_file) as f:
        for line in f:
            yield json.loads(line)

# 3. 내장 함수 사용
keys = map(lambda x: x["key"], data)

# 4. 다중 처리
from multiprocessing import Pool
with Pool(4) as pool:
    results = pool.map(heavy_computation, data)

# ❌ 비효율적
# 1. 반복 리스트 빌드
result = []
for x in data:
    if x is not None:
        result.append(process(x))

# 2. 전체 파일 로드
with open("large_file.txt") as f:
    all_lines = f.readlines()  # 메모리 낭비
```

---

## 4️⃣ **분산 시스템 패턴**

### 데이터 분할
```python
from typing import List, Dict, Any

class DataPartitioner:
    @staticmethod
    def partition_by_range(
        data: List[Dict[str, Any]],
        num_partitions: int,
        key: str
    ) -> List[List[Dict[str, Any]]]:
        """범위 기반 파티셔닝"""
        sorted_data = sorted(data, key=lambda x: x[key])
        partition_size = len(sorted_data) // num_partitions
        
        return [
            sorted_data[i:i+partition_size]
            for i in range(0, len(sorted_data), partition_size)
        ]
    
    @staticmethod
    def partition_by_hash(
        data: List[Dict[str, Any]],
        num_partitions: int,
        key: str
    ) -> List[List[Dict[str, Any]]]:
        """해시 기반 파티셔닝"""
        partitions: List[List[Dict]] = [[] for _ in range(num_partitions)]
        
        for item in data:
            partition_id = hash(item[key]) % num_partitions
            partitions[partition_id].append(item)
        
        return partitions
```

### 재시도 로직
```python
import time
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """재시도 데코레이터"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = delay_seconds
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        delay *= backoff_factor
            
            raise last_exception
        
        return wrapper
    return decorator

# 사용
@retry(max_attempts=3, delay_seconds=1.0)
def fetch_data_from_remote(url: str) -> Dict[str, Any]:
    """원격 서버에서 데이터 가져오기 (재시도 포함)"""
    # 네트워크 요청
    pass
```

---

## 5️⃣ **테스트 전략**

### 단위 테스트 (unittest)
```python
import unittest
from typing import List, Dict

class TestMapReduceExecutor(unittest.TestCase):
    def setUp(self) -> None:
        """각 테스트 전에 실행"""
        self.executor = MapReduceExecutor(workers=2)
        self.test_data: List[Dict] = [
            {"key": "a", "value": 1},
            {"key": "b", "value": 2},
        ]
    
    def test_map_phase(self) -> None:
        """Map 단계 테스트"""
        result = self.executor.map_phase(self.test_data)
        self.assertEqual(len(result), 2)
        self.assertIn("a", result)
    
    def test_reduce_phase(self) -> None:
        """Reduce 단계 테스트"""
        mapped = self.executor.map_phase(self.test_data)
        result = self.executor.reduce_phase(mapped)
        self.assertIsInstance(result, dict)
    
    def test_empty_data(self) -> None:
        """빈 데이터 처리"""
        with self.assertRaises(ValueError):
            self.executor.execute([])

if __name__ == "__main__":
    unittest.main()
```

### 통합 테스트
```python
class TestDistributedSystem(unittest.TestCase):
    def test_end_to_end_raft_consensus(self) -> None:
        """End-to-end Raft 합의 테스트"""
        # 1. 클러스터 생성
        cluster = RaftCluster(num_nodes=5)
        
        # 2. 리더 선출
        cluster.start_election()
        leader = cluster.get_leader()
        self.assertIsNotNone(leader)
        
        # 3. 로그 복제
        cluster.replicate_log("test_entry")
        
        # 4. 일관성 확인
        for node in cluster.nodes:
            self.assertEqual(
                node.get_last_log_index(),
                leader.get_last_log_index()
            )

# 실행
pytest test_distributed_system.py -v --cov=src/
```

---

## 📋 **체크리스트**

모든 Python 모듈이 다음을 만족해야 함:

- [ ] **타입 힌팅**: 모든 함수 파라미터 & 반환값
- [ ] **Docstring**: Google/NumPy 스타일
- [ ] **PEP8**: 라인 길이 ≤ 100자
- [ ] **테스트**: 커버리지 ≥ 80%
- [ ] **성능**: 벤치마크 결과 문서화
- [ ] **에러 처리**: 명시적 예외 정의
- [ ] **로깅**: debug/info/warning/error 적절히 사용

---

**기록이 증명이다. (Your record is your proof.)**

마지막 업데이트: 2026-02-26
