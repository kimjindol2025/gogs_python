# 🔌 **API 참조 문서**

> Python University 분산 시스템 & 양자 보안 연구 — 모든 클래스와 함수의 상세 API 문서

---

## **v8.2: 데이터 레이크 & 분산 병렬 처리**

### Enum 정의

#### `PartitionStrategy`
```python
class PartitionStrategy(Enum):
    RANGE = "range"      # 범위 기반 분할
    HASH = "hash"        # 해시 기반 분산
```

#### `WorkerStatus`
```python
class WorkerStatus(Enum):
    IDLE = "idle"         # 유휴 상태
    RUNNING = "running"   # 실행 중
    FAILED = "failed"     # 실패
    RETRYING = "retrying" # 재시도 중
```

#### `SkewLevel`
```python
class SkewLevel(Enum):
    BALANCED = "balanced"     # 균형 (<10% std)
    MODERATE = "moderate"     # 중간 (10~30% std)
    SEVERE = "severe"         # 심각 (>30% std)
```

### Dataclass 정의

#### `Partition`
```python
@dataclass
class Partition:
    partition_id: str       # 파티션 ID
    data: List[Any]        # 데이터
    strategy: str          # 분할 전략
    node_id: str           # 노드 ID
    size: int              # 파티션 크기

# 예시
partition = Partition(
    partition_id="p1",
    data=[1, 2, 3, 4, 5],
    strategy="range",
    node_id="node_0",
    size=5
)
```

#### `WorkerResult`
```python
@dataclass
class WorkerResult:
    worker_id: str         # 워커 ID
    partition_id: str      # 파티션 ID
    result: Any           # 결과
    status: str           # 상태
    attempts: int         # 시도 횟수
    duration_ms: float    # 실행 시간 (ms)
```

#### `MapReduceResult`
```python
@dataclass
class MapReduceResult:
    total_items: int              # 총 항목 수
    unique_keys: int              # 고유 키 수
    final_output: Dict[Any, Any]  # 최종 출력
    map_time_ms: float            # Map 단계 시간
    shuffle_time_ms: float        # Shuffle 단계 시간
    reduce_time_ms: float         # Reduce 단계 시간
```

### RangePartitioner 클래스

```python
class RangePartitioner:
    def partition(self, data: List[Any]) -> List[Partition]:
        """
        범위 기반으로 데이터를 균등하게 분할합니다.

        Args:
            data: 분할할 데이터 리스트

        Returns:
            Partition 객체 리스트

        예시:
            partitioner = RangePartitioner()
            data = list(range(100))
            partitions = partitioner.partition(data)
            # 결과: 4개 파티션, 각 25개 항목
        """
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        파티션 통계를 반환합니다.

        Returns:
            {
                "partition_sizes": [25, 25, 25, 25],
                "mean_size": 25.0,
                "std_dev": 0.0
            }
        """
        pass
```

### HashPartitioner 클래스

```python
class HashPartitioner:
    def partition(self, data: List[Any]) -> List[Partition]:
        """
        해시 함수를 이용해 데이터를 분산시킵니다.

        Args:
            data: 분할할 데이터 리스트

        Returns:
            Partition 객체 리스트

        예시:
            partitioner = HashPartitioner()
            data = ["apple", "banana", "cherry", ...]
            partitions = partitioner.partition(data)
            # 결과: 4개 파티션, 데이터 분산 배치
        """
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        파티션 통계를 반환합니다.

        Returns:
            {
                "partition_sizes": [24, 26, 25, 25],
                "mean_size": 25.0,
                "std_dev": 0.816  # 약간의 분산
            }
        """
        pass
```

### MapReduceExecutor 클래스

```python
class MapReduceExecutor:
    def map_phase(self, data: List[Any], map_func: Callable) -> List[Tuple]:
        """
        데이터에 map 함수를 적용합니다.

        Args:
            data: 입력 데이터
            map_func: 변환 함수 (item → List[Tuple])

        Returns:
            변환된 (key, value) 튜플 리스트

        예시:
            def word_count_mapper(text):
                return [(word, 1) for word in text.split()]

            mapped = executor.map_phase(text, word_count_mapper)
        """
        pass

    def shuffle_phase(self, mapped_data: List[Tuple]) -> Dict[Any, List[Any]]:
        """
        키별로 값들을 그룹핑합니다.

        Args:
            mapped_data: (key, value) 튜플 리스트

        Returns:
            {key: [value1, value2, ...]}

        예시:
            mapped = [("apple", 1), ("apple", 1), ("banana", 1)]
            shuffled = executor.shuffle_phase(mapped)
            # 결과: {"apple": [1, 1], "banana": [1]}
        """
        pass

    def reduce_phase(self, shuffled: Dict[Any, List[Any]],
                    reduce_func: Callable) -> Dict[Any, Any]:
        """
        그룹핑된 값들을 집계합니다.

        Args:
            shuffled: {key: [values]} 형식
            reduce_func: 집계 함수 (key, values → result)

        Returns:
            최종 결과 {key: result}

        예시:
            def word_count_reducer(key, values):
                return sum(values)

            reduced = executor.reduce_phase(shuffled, word_count_reducer)
            # 결과: {"apple": 2, "banana": 1}
        """
        pass

    def execute(self, data: List[Any], map_func: Callable,
               reduce_func: Callable) -> MapReduceResult:
        """
        전체 MapReduce 파이프라인을 실행합니다.

        Args:
            data: 입력 데이터
            map_func: Map 함수
            reduce_func: Reduce 함수

        Returns:
            MapReduceResult 객체 (결과 + 타이밍 정보)
        """
        pass
```

### FaultToleranceManager 클래스

```python
class FaultToleranceManager:
    def execute_with_retry(self, func: Callable, chunk: Any,
                          partition_id: str, worker_id: str) -> WorkerResult:
        """
        함수를 실행하고, 실패시 최대 3회 재시도합니다.

        Args:
            func: 실행할 함수
            chunk: 처리할 청크
            partition_id: 파티션 ID
            worker_id: 워커 ID

        Returns:
            WorkerResult 객체

        예시:
            result = manager.execute_with_retry(
                func=process_chunk,
                chunk=data_chunk,
                partition_id="p1",
                worker_id="w1"
            )
        """
        pass

    def reassign_partition(self, partition: Partition,
                          available_workers: List[str]) -> str:
        """
        실패한 파티션을 다른 워커에 재할당합니다.

        Args:
            partition: 재할당할 파티션
            available_workers: 사용 가능한 워커 목록

        Returns:
            재할당된 워커 ID
        """
        pass

    def run_with_fault_tolerance(self, data: List[Any], func: Callable,
                                num_workers: int) -> List[WorkerResult]:
        """
        결함 허용 모드로 데이터를 처리합니다.

        Args:
            data: 처리할 데이터
            func: 처리 함수
            num_workers: 워커 수

        Returns:
            WorkerResult 객체 리스트
        """
        pass
```

### DataLocalityOptimizer 클래스

```python
class DataLocalityOptimizer:
    def register_node(self, node: 'DataNode') -> None:
        """
        처리 노드를 등록합니다.

        Args:
            node: DataNode 객체
        """
        pass

    def calculate_processing_cost(self, partition_id: str,
                                 target_node_id: str) -> float:
        """
        파티션을 특정 노드에서 처리하는 비용을 계산합니다.

        Args:
            partition_id: 파티션 ID
            target_node_id: 대상 노드 ID

        Returns:
            비용 (로컬: 1.0, 원격: 3.0 이상)
        """
        pass

    def find_optimal_node(self, partition_id: str) -> str:
        """
        파티션에 최적의 노드를 찾습니다.

        Args:
            partition_id: 파티션 ID

        Returns:
            최적 노드 ID
        """
        pass

    def optimize_assignments(self, partitions: List[Partition]) -> Dict[str, str]:
        """
        모든 파티션의 최적 배치를 계산합니다.

        Args:
            partitions: 파티션 리스트

        Returns:
            {partition_id: optimal_node_id}
        """
        pass
```

### SkewHandler 클래스

```python
class SkewHandler:
    def detect_skew(self, partitions: List[Partition]) -> 'SkewReport':
        """
        데이터 스큐를 탐지합니다.

        Args:
            partitions: 파티션 리스트

        Returns:
            SkewReport 객체

        예시:
            report = handler.detect_skew(partitions)
            # 결과: SEVERE 스큐 탐지 (std_dev > 30%)
        """
        pass

    def find_hot_keys(self, data: List[Any], top_n: int = 3) -> List[Tuple]:
        """
        가장 빈번한 키들을 찾습니다.

        Args:
            data: 데이터 리스트
            top_n: 상위 N개

        Returns:
            [(key, frequency), ...] 리스트
        """
        pass

    def rebalance(self, partitions: List[Partition]) -> List[Partition]:
        """
        불균형한 파티션들을 재분산합니다.

        Args:
            partitions: 파티션 리스트

        Returns:
            재분산된 파티션 리스트
        """
        pass

    def isolate_hot_key(self, partitions: List[Partition],
                       hot_key: Any) -> List[Partition]:
        """
        특정 핫키를 별도 파티션으로 격리합니다.

        Args:
            partitions: 파티션 리스트
            hot_key: 격리할 핫키

        Returns:
            격리된 파티션 리스트
        """
        pass
```

---

## **v8.3: 양자 저항 암호화**

### QuantumThreatAnalyzer 클래스

```python
class QuantumThreatAnalyzer:
    def analyze_shor_threat(self, key_size: int = 2048) -> Dict[str, Any]:
        """
        Shor 알고리즘의 RSA 파괴 가능성을 분석합니다.

        Args:
            key_size: RSA 키 크기 (기본값: 2048)

        Returns:
            {
                "threat_level": "CRITICAL",
                "speedup_factor": 500000,  # 양자 컴퓨터 가속 배수
                "classical_years": 10000,  # 고전 컴퓨터 예상 시간
                "quantum_hours": 1          # 양자 컴퓨터 예상 시간
            }
        """
        pass

    def estimate_key_lifespan(self, key_size: int) -> Dict[str, Any]:
        """
        현재 암호 키의 예상 수명을 추정합니다.

        Returns:
            {
                "years_until_broken": 15,
                "current_status": "SAFE",
                "recommendation": "REPLACE_IN_5_YEARS"
            }
        """
        pass

    def recommend_key_size(self, target_security_level: int) -> int:
        """
        목표 보안 수준에 필요한 키 크기를 추천합니다.

        Args:
            target_security_level: 보안 수준 (256, 512, etc)

        Returns:
            권장 키 크기 (비트)
        """
        pass
```

### LatticeKEM 클래스

```python
class LatticeKEM:
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        격자 기반 공개키와 비밀키를 생성합니다.

        Returns:
            (public_key, secret_key)
        """
        pass

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        공유 비밀(공유키)과 암호문을 생성합니다.

        Args:
            public_key: 수신자의 공개키

        Returns:
            (shared_secret, ciphertext)
        """
        pass

    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """
        암호문으로부터 공유 비밀을 복구합니다.

        Args:
            ciphertext: 암호문
            secret_key: 비밀키

        Returns:
            shared_secret
        """
        pass

    def get_security_level(self) -> int:
        """
        이 KEM의 보안 강도(비트)를 반환합니다.

        Returns:
            보안 강도 (256, 512 등)
        """
        pass
```

### HybridCryptoSystem 클래스

```python
class HybridCryptoSystem:
    def encrypt(self, plaintext: bytes) -> Tuple[bytes, Dict]:
        """
        RSA + Lattice 하이브리드 암호화를 수행합니다.

        Args:
            plaintext: 평문

        Returns:
            (ciphertext, metadata)
        """
        pass

    def decrypt(self, ciphertext: bytes, metadata: Dict) -> bytes:
        """
        하이브리드 암호문을 복호화합니다.

        Args:
            ciphertext: 암호문
            metadata: 암호화 메타데이터

        Returns:
            plaintext
        """
        pass

    def get_hybrid_strength(self) -> Dict[str, int]:
        """
        RSA와 Lattice의 각각 강도를 반환합니다.

        Returns:
            {"rsa_bits": 2048, "lattice_bits": 256}
        """
        pass
```

### CryptoAgilityEngine 클래스

```python
class CryptoAgilityEngine:
    def switch_algorithm(self, new_algorithm: str) -> bool:
        """
        암호 알고리즘을 무중단으로 전환합니다.

        Args:
            new_algorithm: 새 알고리즘 이름

        Returns:
            전환 성공 여부
        """
        pass

    def execute_with_agility(self, data: bytes,
                            operation: str) -> Tuple[bytes, Dict]:
        """
        민첩한 알고리즘으로 작업을 수행합니다.

        Args:
            data: 입력 데이터
            operation: "encrypt" 또는 "decrypt"

        Returns:
            (result, metadata)
        """
        pass

    def get_agility_status(self) -> Dict[str, Any]:
        """
        현재 알고리즘 전환 상태를 반환합니다.

        Returns:
            {
                "current_algorithm": "hybrid",
                "available_algorithms": ["rsa", "lattice", "hybrid"],
                "switchable_algorithms": ["lattice", "hybrid"]
            }
        """
        pass
```

---

## **v8.4: 그랜드 통합 아키텍처**

### QuantumSecurityLayer 클래스

```python
class QuantumSecurityLayer:
    def protect_data(self, data: bytes) -> Dict[str, Any]:
        """
        데이터를 양자 저항 보안으로 보호합니다.

        Args:
            data: 입력 데이터

        Returns:
            {
                "protection_status": "QUANTUM_RESISTANT",
                "security_level": 256,
                "encryption_time_ms": 5.2
            }
        """
        pass

    def detect_quantum_threat(self) -> bool:
        """
        양자 위협을 탐지합니다.

        Returns:
            위협 탐지 여부
        """
        pass
```

### SelfHealingKernel 클래스

```python
class SelfHealingKernel:
    def detect_anomaly(self, cpu_usage: int,
                      memory_usage: int) -> bool:
        """
        시스템 이상을 탐지합니다.

        Args:
            cpu_usage: CPU 사용률 (%)
            memory_usage: 메모리 사용률 (%)

        Returns:
            이상 탐지 여부
        """
        pass

    def heal_system(self, issue: str) -> Dict[str, Any]:
        """
        시스템 문제를 자동으로 치유합니다.

        Args:
            issue: 문제 종류

        Returns:
            {
                "status": "HEALED",
                "action_taken": "restarted_service",
                "recovery_time_ms": 250
            }
        """
        pass
```

### UniversalMonitor 클래스

```python
class UniversalMonitor:
    def collect_metrics(self, **kwargs) -> 'SystemMetrics':
        """
        시스템 메트릭을 수집합니다.

        Args:
            cpu, memory, security_level, distributed_nodes, etc.

        Returns:
            SystemMetrics 객체
        """
        pass

    def calculate_health_score(self, metrics: 'SystemMetrics') -> float:
        """
        메트릭을 기반으로 건강도 점수를 계산합니다.

        Args:
            metrics: 시스템 메트릭

        Returns:
            건강도 점수 (0-100)
        """
        pass
```

### GogsArchitectureEngine 클래스

```python
class GogsArchitectureEngine:
    def run_integrated_system(self, iterations: int) -> 'SystemReport':
        """
        통합 시스템을 실행합니다.

        Args:
            iterations: 실행 반복 횟수

        Returns:
            SystemReport 객체
        """
        pass

    def verify_dissertation_principles(self) -> List['DissertationEvidence']:
        """
        박사 논문의 3원칙을 검증합니다.

        Returns:
            DissertationEvidence 리스트
            - 불변성
            - 관측성
            - 자율성
        """
        pass
```

---

## **v9.3: 행성급 분산 합의**

### LogReplicator 클래스

```python
class LogReplicator:
    def append_log(self, node_id: str, entry: 'LogEntry') -> bool:
        """
        로그 엔트리를 추가합니다.

        Args:
            node_id: 노드 ID
            entry: LogEntry 객체

        Returns:
            성공 여부
        """
        pass

    def replicate_to_followers(self, leader_id: str,
                              followers: List[str],
                              entry: 'LogEntry') -> List[bool]:
        """
        팔로워들에게 로그를 복제합니다.

        Args:
            leader_id: 리더 ID
            followers: 팔로워 ID 리스트
            entry: 복제할 LogEntry

        Returns:
            각 팔로워의 복제 성공 여부
        """
        pass

    def check_quorum_replication(self, num_nodes: int,
                                results: Dict[str, bool]) -> bool:
        """
        Quorum 복제 여부를 확인합니다.

        Args:
            num_nodes: 전체 노드 수
            results: 각 노드의 복제 결과

        Returns:
            과반수 이상이 복제되었는가?
        """
        pass
```

### LeaderElection 클래스

```python
class LeaderElection:
    def start_election(self, candidate_id: str,
                      num_nodes: int) -> bool:
        """
        리더 선출을 시작합니다.

        Args:
            candidate_id: 후보 노드 ID
            num_nodes: 전체 노드 수

        Returns:
            선출 성공 여부
        """
        pass

    def receive_vote_request(self, candidate_id: str,
                            term: int,
                            voter_id: str) -> 'VoteResponse':
        """
        투표 요청을 처리합니다.

        Args:
            candidate_id: 후보 ID
            term: 현재 텀
            voter_id: 투표자 ID

        Returns:
            VoteResponse 객체
        """
        pass

    def handle_leader_failure(self, num_nodes: int) -> None:
        """
        리더 장애를 처리합니다.

        Args:
            num_nodes: 전체 노드 수
        """
        pass
```

### StateMachine 클래스

```python
class StateMachine:
    def apply_entry(self, entry: 'LogEntry') -> bool:
        """
        로그 엔트리를 상태 머신에 적용합니다.

        Args:
            entry: LogEntry 객체

        Returns:
            적용 성공 여부
        """
        pass

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        현재 상태의 스냅샷을 반환합니다.

        Returns:
            {
                "state": {...},
                "version": 10,
                "applied_entries": 10
            }
        """
        pass

    def verify_state_consistency(self, snapshot: Dict) -> bool:
        """
        상태 일관성을 검증합니다.

        Args:
            snapshot: 상태 스냅샷

        Returns:
            일관성 검증 결과
        """
        pass
```

### RaftConsensus 클래스

```python
class RaftConsensus:
    def reach_consensus(self, data: Any) -> bool:
        """
        데이터에 대한 합의를 도달합니다.

        Args:
            data: 합의할 데이터

        Returns:
            합의 성공 여부
        """
        pass

    def get_consensus_status(self) -> Dict[str, Any]:
        """
        현재 합의 상태를 반환합니다.

        Returns:
            {
                "node_id": "node_0",
                "state": "LEADER",
                "term": 5,
                "leader": "node_0"
            }
        """
        pass
```

### GlobalDatacenter 클래스

```python
class GlobalDatacenter:
    def broadcast_consensus_request(self, data: Any) -> List[Dict]:
        """
        모든 노드에 합의 요청을 전파합니다.

        Args:
            data: 합의할 데이터

        Returns:
            각 노드의 응답 리스트
        """
        pass

    def handle_regional_failure(self, region: str) -> Dict[str, Any]:
        """
        지역 장애를 처리합니다.

        Args:
            region: 장애 지역

        Returns:
            {
                "failed_region": "asia",
                "recovery_success": True,
                "affected_nodes": 1,
                "recovery_time_ms": 500
            }
        """
        pass
```

### DisasterRecovery 클래스

```python
class DisasterRecovery:
    def detect_failure(self, node_id: str,
                      failure_type: str) -> Dict[str, Any]:
        """
        노드 장애를 탐지합니다.

        Args:
            node_id: 노드 ID
            failure_type: 장애 유형

        Returns:
            장애 정보
        """
        pass

    def initiate_recovery(self, failure: Dict) -> bool:
        """
        복구를 시작합니다.

        Args:
            failure: 장애 정보

        Returns:
            복구 시작 성공 여부
        """
        pass

    def get_recovery_status(self) -> Dict[str, int]:
        """
        복구 상태를 반환합니다.

        Returns:
            {
                "failures_detected": 1,
                "successful_recoveries": 1,
                "failed_recoveries": 0
            }
        """
        pass
```

---

## 📚 **공통 타입 정의**

### LogEntry
```python
@dataclass
class LogEntry:
    term: int              # Raft term
    index: int             # 로그 인덱스
    entry_type: EntryType  # 엔트리 타입
    data: Any             # 데이터
```

### VoteResponse
```python
@dataclass
class VoteResponse:
    voter_id: str     # 투표자 ID
    granted: bool     # 투표 여부
    term: int        # 현재 term
```

### SystemMetrics
```python
@dataclass
class SystemMetrics:
    cpu_usage: int
    memory_usage: int
    security_level: int
    distributed_nodes: int
    quantum_threats: int
    healing_actions: int
```

---

**문서 버전**: 1.0
**마지막 업데이트**: 2026년 02월 25일
