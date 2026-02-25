#!/usr/bin/env python3
"""
PYTHON_PROJECT_TEMPLATE.py - Python 모범 사례 템플릿

이 모듈은 gogs_python 프로젝트의 모든 모범 사례를 포함한 템플릿입니다.
새로운 모듈을 작성할 때 이 파일의 구조를 따르세요.

기록이 증명이다 - 표준화된 Python 코드는 협업을 쉽게 합니다.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

# ============================================================================
# 1️⃣ 로깅 설정 (Logging Configuration)
# ============================================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ============================================================================
# 2️⃣ 타입 정의 (Type Definitions)
# ============================================================================

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


# ============================================================================
# 3️⃣ Enum 정의 (Enum Definitions)
# ============================================================================

class Status(Enum):
    """작업 상태 열거형."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# 4️⃣ 데이터 클래스 (Data Classes)
# ============================================================================

@dataclass
class TaskResult:
    """작업 결과 데이터 클래스.

    Attributes:
        task_id: 작업 ID
        status: 작업 상태
        result: 작업 결과 (성공 시)
        error: 오류 메시지 (실패 시)
        duration_seconds: 실행 시간 (초)
    """

    task_id: str
    status: Status
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """TaskResult를 딕셔너리로 변환합니다.

        Returns:
            TaskResult의 딕셔너리 표현
        """
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'duration_seconds': self.duration_seconds,
        }


# ============================================================================
# 5️⃣ 데코레이터 (Decorators)
# ============================================================================

def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """재시도 데코레이터.

    주어진 함수를 여러 번 실행 시도합니다. 각 실패 후 지연이 증가합니다.

    Args:
        max_attempts: 최대 시도 횟수
        delay_seconds: 첫 번째 지연 (초)
        backoff_factor: 지연 증가 계수

    Returns:
        데코레이터 함수

    Example:
        @retry(max_attempts=3, delay_seconds=1.0)
        def fetch_data() -> str:
            return requests.get(url).text
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = delay_seconds
            last_exception: Optional[Exception] = None

            for attempt in range(max_attempts):
                try:
                    logger.debug(
                        f"실행 {func.__name__} (시도 {attempt + 1}/{max_attempts})"
                    )
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"시도 {attempt + 1} 실패: {str(e)}"
                    )
                    if attempt < max_attempts - 1:
                        logger.debug(f"{delay:.1f}초 대기 후 재시도...")
                        time.sleep(delay)
                        delay *= backoff_factor

            logger.error(f"모든 시도 실패: {str(last_exception)}")
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unknown error in {func.__name__}")

        return wrapper

    return decorator


def timed(func: Callable[..., T]) -> Callable[..., T]:
    """실행 시간 측정 데코레이터.

    함수 실행 시간을 측정하고 로깅합니다.

    Args:
        func: 측정할 함수

    Returns:
        래핑된 함수
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.time()
        logger.debug(f"시작: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(
                f"완료: {func.__name__} ({elapsed:.3f}초)"
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"실패: {func.__name__} ({elapsed:.3f}초): {str(e)}"
            )
            raise

    return wrapper


# ============================================================================
# 6️⃣ 추상 기본 클래스 (Abstract Base Classes)
# ============================================================================

class Worker(ABC):
    """작업자 추상 기본 클래스.

    구현자는 process 메서드를 구현해야 합니다.
    """

    def __init__(self, worker_id: str) -> None:
        """Worker 초기화.

        Args:
            worker_id: 작업자 고유 ID
        """
        self.worker_id = worker_id
        logger.debug(f"Worker {self.worker_id} 생성됨")

    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Any:
        """작업을 처리합니다.

        Args:
            task: 처리할 작업

        Returns:
            처리 결과

        Raises:
            NotImplementedError: 서브클래스에서 구현해야 함
        """
        pass


# ============================================================================
# 7️⃣ 구체적인 구현 (Concrete Implementations)
# ============================================================================

class DefaultWorker(Worker):
    """기본 작업자 구현."""

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업을 처리합니다.

        Args:
            task: 처리할 작업

        Returns:
            처리 결과
        """
        logger.info(f"Worker {self.worker_id} 처리 시작: {task}")
        result = {
            'worker_id': self.worker_id,
            'task_id': task.get('id'),
            'status': 'completed',
            'data': task,
        }
        logger.info(f"Worker {self.worker_id} 처리 완료")
        return result


# ============================================================================
# 8️⃣ 메인 클래스 (Main Classes)
# ============================================================================

class TaskManager:
    """작업 관리자.

    여러 작업을 큐에 저장하고 워커에 분배합니다.
    """

    def __init__(self, worker_count: int = 2) -> None:
        """TaskManager 초기화.

        Args:
            worker_count: 워커 수
        """
        self.workers: List[Worker] = [
            DefaultWorker(f"worker-{i}") for i in range(worker_count)
        ]
        self.task_queue: List[Dict[str, Any]] = []
        self.results: List[TaskResult] = []
        logger.info(f"TaskManager 초기화: {worker_count}명의 워커")

    def add_task(self, task_id: str, data: Dict[str, Any]) -> None:
        """작업을 큐에 추가합니다.

        Args:
            task_id: 작업 ID
            data: 작업 데이터
        """
        task = {
            'id': task_id,
            'data': data,
            'status': Status.PENDING.value,
        }
        self.task_queue.append(task)
        logger.debug(f"작업 추가됨: {task_id}")

    @timed
    def process_all_tasks(self) -> List[TaskResult]:
        """모든 작업을 처리합니다.

        Returns:
            처리 결과 목록
        """
        logger.info(f"작업 처리 시작: {len(self.task_queue)}개")
        results: List[TaskResult] = []

        for idx, task in enumerate(self.task_queue):
            worker = self.workers[idx % len(self.workers)]
            start_time = time.time()

            try:
                result = worker.process(task)
                duration = time.time() - start_time

                task_result = TaskResult(
                    task_id=task['id'],
                    status=Status.COMPLETED,
                    result=result,
                    duration_seconds=duration,
                )
                results.append(task_result)
                logger.info(
                    f"작업 완료: {task['id']} ({duration:.3f}초)"
                )
            except Exception as e:
                duration = time.time() - start_time
                task_result = TaskResult(
                    task_id=task['id'],
                    status=Status.FAILED,
                    error=str(e),
                    duration_seconds=duration,
                )
                results.append(task_result)
                logger.error(
                    f"작업 실패: {task['id']}: {str(e)}"
                )

        self.results = results
        logger.info(f"작업 처리 완료: {len(results)}개")
        return results

    def get_summary(self) -> Dict[str, Any]:
        """결과 요약을 반환합니다.

        Returns:
            {completed: int, failed: int, total_time: float}
        """
        completed = sum(
            1 for r in self.results if r.status == Status.COMPLETED
        )
        failed = sum(
            1 for r in self.results if r.status == Status.FAILED
        )
        total_time = sum(r.duration_seconds for r in self.results)

        return {
            'completed': completed,
            'failed': failed,
            'total_tasks': len(self.results),
            'total_time_seconds': total_time,
        }


# ============================================================================
# 9️⃣ 유틸리티 함수 (Utility Functions)
# ============================================================================

def load_json_file(file_path: str) -> Dict[str, Any]:
    """JSON 파일을 로드합니다.

    Args:
        file_path: 파일 경로

    Returns:
        파일 내용

    Raises:
        FileNotFoundError: 파일이 없음
        json.JSONDecodeError: JSON 파싱 실패
    """
    logger.debug(f"JSON 파일 로드: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """데이터를 JSON 파일로 저장합니다.

    Args:
        file_path: 파일 경로
        data: 저장할 데이터
    """
    logger.debug(f"JSON 파일 저장: {file_path}")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================================
# 🔟 메인 함수 (Main Function)
# ============================================================================

def main() -> None:
    """메인 함수.

    프로젝트 템플릿의 기본 실행 흐름을 보여줍니다.
    """
    logger.info("=" * 70)
    logger.info("Python 프로젝트 템플릿 실행")
    logger.info("=" * 70)

    # TaskManager 생성
    manager = TaskManager(worker_count=3)

    # 샘플 작업 추가
    sample_tasks = [
        {'name': 'task-1', 'value': 100},
        {'name': 'task-2', 'value': 200},
        {'name': 'task-3', 'value': 300},
        {'name': 'task-4', 'value': 400},
        {'name': 'task-5', 'value': 500},
    ]

    for idx, task_data in enumerate(sample_tasks):
        manager.add_task(f"task-{idx + 1}", task_data)

    # 모든 작업 처리
    results = manager.process_all_tasks()

    # 결과 출력
    logger.info("-" * 70)
    logger.info("처리 결과:")
    for result in results:
        logger.info(
            f"  {result.task_id}: {result.status.value} "
            f"({result.duration_seconds:.3f}초)"
        )

    # 요약 출력
    summary = manager.get_summary()
    logger.info("-" * 70)
    logger.info("요약:")
    logger.info(f"  완료: {summary['completed']}")
    logger.info(f"  실패: {summary['failed']}")
    logger.info(f"  총 시간: {summary['total_time_seconds']:.3f}초")

    logger.info("=" * 70)
    logger.info("실행 완료")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
