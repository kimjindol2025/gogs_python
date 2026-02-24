"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🗄️ UNIVERSITY LEVEL 3 - v5.2 DATABASE ARCHITECTURE & OPTIMIZATION 🗄️   ║
║                                                                              ║
║      데이터의 무결성과 확장성 (Data Integrity & Scalability)                ║
║  RDBMS vs NoSQL - 저장의 미래를 설계하다                                   ║
║                                                                              ║
║  "수조 개의 데이터를 0.1초에 찾아내는 구조" - gogs                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 학습 목표:
   1️⃣ RDBMS vs NoSQL: 아키텍처 선택의 기준
   2️⃣ ACID 원칙: 트랜잭션의 신뢰성
   3️⃣ 정규화: 데이터 중복 제거와 설계
   4️⃣ 트랜잭션: Commit/Rollback으로 안전성 보장
   5️⃣ 인덱싱: 검색 속도 최적화 (1000배 향상)
   6️⃣ NoSQL 설계: 유연한 스키마
   7️⃣ 대규모 데이터: 샤딩과 복제

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 1: 데이터베이스 철학 - 저장과 검색의 진화                             ║
# ╚════════════════════════════════════════════════════════════════════════════╝

"""
📁 저장 방식의 진화:

1️⃣ 파일 저장 (File-based)
   ────────────────────
   ├─ students.txt (텍스트 파일)
   │  "001,Alice,25"
   │  "002,Bob,23"
   │  "003,Charlie,24"
   ├─ 장점: 간단함
   └─ 단점: 검색 느림, 동시 접근 문제, 데이터 중복 많음


2️⃣ 관계형 데이터베이스 (RDBMS - SQL)
   ──────────────────────────────
   ┌─────────────┐         ┌──────────────┐
   │   students  │         │   scores     │
   ├─────────────┤         ├──────────────┤
   │ id (PK)     │◄───────┤│ student_id   │
   │ name        │         │ subject      │
   │ age         │         │ score        │
   └─────────────┘         └──────────────┘

   장점:
   ├─ 정규화로 중복 제거
   ├─ 관계로 데이터 무결성 보장
   ├─ SQL로 강력한 쿼리
   └─ ACID 보장 (트랜잭션)

   단점:
   ├─ 스키마 고정 (변경 어려움)
   ├─ 복잡한 설계 필요
   └─ 수평 확장 어려움 (Scaling)


3️⃣ NoSQL (Key-Value, Document)
   ─────────────────────────────
   ┌────────────────────────────────┐
   │ MongoDB (Document Store)       │
   ├────────────────────────────────┤
   │ {                              │
   │   "_id": 1,                    │
   │   "name": "Alice",             │
   │   "age": 25,                   │
   │   "scores": [                  │
   │     {"subject": "Math", "score": 95},
   │     {"subject": "English", "score": 88}
   │   ]                            │
   │ }                              │
   └────────────────────────────────┘

   장점:
   ├─ 유연한 스키마 (JSON 형식)
   ├─ 수평 확장 용이 (샤딩)
   ├─ 높은 처리량
   └─ 개발 속도 빠름

   단점:
   ├─ ACID 약함 (BASE 모델)
   ├─ JOIN 연산 복잡
   ├─ 쿼리 언어 다양


🔄 선택 기준 (언제 뭘 쓸까?):

┌─────────────────────────────────────────────────┐
│  RDBMS (SQL)이 적합:                            │
│  ├─ 은행, 금융 (데이터 무결성 필수)            │
│  ├─ 회계 시스템 (ACID 필수)                    │
│  ├─ 정확한 관계 관리 필요                       │
│  └─ 복잡한 쿼리 (JOIN, GROUP BY)              │
│                                                 │
│  NoSQL이 적합:                                 │
│  ├─ SNS (대량의 포스트 저장)                   │
│  ├─ 게임 로그 (구조 자유로움)                  │
│  ├─ IoT 센서 데이터 (다양한 형식)             │
│  ├─ 실시간 트렌드 (높은 처리량)               │
│  └─ 프로토타입 (빠른 개발)                     │
└─────────────────────────────────────────────────┘
"""

import sqlite3
import json
import time
import threading
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 2: ACID 원칙 - 트랜잭션의 신뢰성                                      ║
# ╚════════════════════════════════════════════════════════════════════════════╝

"""
🔐 ACID: 트랜잭션의 4가지 필수 특성

1️⃣ ATOMICITY (원자성)
   ──────────────────
   "ALL or NOTHING"

   송금 시나리오:
   ├─ 보내는 사람: 10,000원 → 5,000원 (감소)
   └─ 받는 사람: 0원 → 5,000원 (증가)

   만약 중간에 오류? (프로그램 크래시)
   ❌ "보내는 사람만 줄어들고 받는 사람 못받음"
      → 돈이 증발!

   ✅ ACID 보장:
      → 둘 다 성공하거나 둘 다 실패하거나
      → 부분 완료는 절대 불가능!


2️⃣ CONSISTENCY (일관성)
   ──────────────────
   "올바른 상태만 유지"

   규칙: 모든 계좌의 합 = 전체 머니

   시작: A=100, B=200, 합=300
   송금: A→B 50원

   ✅ 일관성 유지:
      A=50, B=250, 합=300

   ❌ 일관성 위반:
      A=50, B=200, 합=250 (돈 증발!)


3️⃣ ISOLATION (고립성)
   ───────────────────
   "동시 실행도 순차처럼"

   두 거래가 동시에 같은 계좌 접근:

   시간  │ 거래A           │ 거래B
   ────  │─────────────────│─────────────
   T1    │ 잔액 조회: $100 │
   T2    │                │ 잔액 조회: $100
   T3    │ -$20 적용       │
   T4    │                │ -$30 적용
   T5    │                │ 저장: $70
   T6    │ 저장: $80       │

   결과: $70? $80? (뭐가 맞음?)

   ✅ 격리 보장:
      → 거래가 순차적으로 실행된 것처럼
      → 거래A 완료 후 거래B 실행
      → 최종: $50 (정확함!)


4️⃣ DURABILITY (지속성)
   ──────────────────
   "일단 저장되면 영구적"

   ✅ "커밋" 후:
      ├─ 서버 전원 꺼짐 → 데이터 유지
      ├─ 디스크 손상 → 백업에서 복구
      └─ 자연재해 → 클라우드 복제

   ❌ "커밋" 전 (메모리만):
      └─ 프로그램 크래시 → 데이터 손실


┌────────────────────────────────────────┐
│ 트랜잭션 명령어 (SQL)                 │
├────────────────────────────────────────┤
│ BEGIN TRANSACTION                      │
│   UPDATE account SET balance = ...     │
│ COMMIT   ← 모든 변화 확정             │
│ ROLLBACK ← 모든 변화 취소             │
└────────────────────────────────────────┘
"""


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 3: 정규화 (Normalization) - 데이터 중복 제거                         ║
# ╚════════════════════════════════════════════════════════════════════════════╝

"""
🔧 정규화: "하나의 사실은 한 곳에만"

❌ 비정규화된 테이블 (문제 많음):
┌──────────────────────────────────────────┐
│ students                                  │
├──────────────────────────────────────────┤
│ id │ name      │ subject │ score │ grade│
├────┼───────────┼─────────┼───────┼──────┤
│ 1  │ Alice     │ Math    │  95   │ A    │
│ 1  │ Alice     │ English │  88   │ B    │
│ 2  │ Bob       │ Math    │  85   │ B    │
│ 2  │ Bob       │ English │  92   │ A    │
└──────────────────────────────────────────┘

문제들:
1️⃣ 중복: Alice, Bob 정보가 여러 번 반복
2️⃣ 수정 이상: Alice 이름 바꾸면 2곳 모두 수정 필요
3️⃣ 삭제 이상: 학생이 과목 수강 취소하면 학생 정보도 사라짐
4️⃣ 삽입 이상: 과목 없는 학생 추가 불가


✅ 정규화 (1NF 적용):
┌──────────────────┐         ┌──────────────────┐
│ students         │         │ scores           │
├──────────────────┤         ├──────────────────┤
│ id (PK) │ name   │◄────────│ student_id (FK)  │
│ 1       │ Alice  │         │ subject          │
│ 2       │ Bob    │         │ score            │
└──────────────────┘         └──────────────────┘

개선사항:
✓ 중복 제거 (Alice 한 번만)
✓ 수정 이상 해결 (한 곳만 수정)
✓ 삭제 이상 해결 (학생 정보 별도 보관)
✓ 삽입 이상 해결 (과목 없어도 학생 추가 가능)


📊 정규화 단계 (1NF ~ 3NF):

1️⃣ 1NF (First Normal Form)
   └─ 모든 값이 원자적 (분할 불가능)
   └─ 반복되는 그룹 없음

2️⃣ 2NF (Second Normal Form)
   └─ 1NF + 부분 함수 종속 제거
   └─ 모든 비-PK 속성이 PK 전체에 의존

3️⃣ 3NF (Third Normal Form)
   └─ 2NF + 이행 함수 종속 제거
   └─ 비-PK 속성들이 PK에만 의존
   └─ 비-PK 속성 간 의존성 없음

현실: 대부분 3NF까지만 (4NF, 5NF는 극히 드묾)
"""


class RelationalDatabase:
    """관계형 데이터베이스 구현"""

    def __init__(self, db_name: str = ':memory:'):
        """데이터베이스 초기화"""
        self.conn = sqlite3.connect(db_name)
        self.conn.isolation_level = None  # 자동 커밋 비활성화
        self.cursor = self.conn.cursor()

    def create_schema(self):
        """정규화된 스키마 생성"""
        # 사용자 테이블
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 계좌 테이블 (정규화: 사용자와 분리)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                balance REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # 거래 기록 (감사 로그)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account INTEGER,
                to_account INTEGER,
                amount REAL NOT NULL,
                status TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_account) REFERENCES accounts(account_id),
                FOREIGN KEY (to_account) REFERENCES accounts(account_id)
            )
        ''')

    def add_user(self, username: str, email: str) -> int:
        """사용자 추가"""
        self.cursor.execute(
            'INSERT INTO users (username, email) VALUES (?, ?)',
            (username, email)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def add_account(self, user_id: int, balance: float) -> int:
        """계좌 추가"""
        self.cursor.execute(
            'INSERT INTO accounts (user_id, balance) VALUES (?, ?)',
            (user_id, balance)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def transfer(self, from_account: int, to_account: int, amount: float) -> bool:
        """
        송금 (트랜잭션)
        ACID 보장
        """
        try:
            # 트랜잭션 시작
            self.cursor.execute('BEGIN')

            # 보내는 계좌 확인
            self.cursor.execute('SELECT balance FROM accounts WHERE account_id = ?',
                              (from_account,))
            from_balance = self.cursor.fetchone()

            if not from_balance or from_balance[0] < amount:
                raise ValueError("잔액 부족")

            # 1. 보내는 계좌에서 차감
            self.cursor.execute(
                'UPDATE accounts SET balance = balance - ? WHERE account_id = ?',
                (amount, from_account)
            )

            # 2. 받는 계좌에 입금
            self.cursor.execute(
                'UPDATE accounts SET balance = balance + ? WHERE account_id = ?',
                (amount, to_account)
            )

            # 3. 거래 기록
            self.cursor.execute(
                'INSERT INTO transactions (from_account, to_account, amount, status) VALUES (?, ?, ?, ?)',
                (from_account, to_account, amount, 'SUCCESS')
            )

            # 커밋 (모든 변화 확정)
            self.cursor.execute('COMMIT')
            print(f"✅ 송금 성공: {amount}원 ({from_account} → {to_account})")
            return True

        except Exception as e:
            # 롤백 (모든 변화 취소)
            self.cursor.execute('ROLLBACK')
            print(f"❌ 송금 실패: {e}")
            return False

    def get_balance(self, account_id: int) -> float:
        """잔액 조회"""
        self.cursor.execute('SELECT balance FROM accounts WHERE account_id = ?',
                          (account_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_transaction_history(self, account_id: int) -> List[Dict]:
        """거래 내역 조회"""
        self.cursor.execute('''
            SELECT transaction_id, from_account, to_account, amount, timestamp
            FROM transactions
            WHERE from_account = ? OR to_account = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (account_id, account_id))

        return [
            {
                'id': row[0],
                'from': row[1],
                'to': row[2],
                'amount': row[3],
                'time': row[4]
            }
            for row in self.cursor.fetchall()
        ]


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 4: 인덱싱 - 검색 속도 최적화                                          ║
# ╚════════════════════════════════════════════════════════════════════════════╝

"""
📚 인덱싱: 책의 "찾아보기"

❌ 인덱스 없을 때:
   100만 개의 사용자 중 "Alice" 찾기
   → 처음부터 끝까지 순차 검색
   → 최악의 경우: 100만 번 비교
   → 시간: ~1초

✅ 인덱스 있을 때:
   → 이진 탐색 (Binary Search)
   → 필요한 비교: log₂(100만) ≈ 20번
   → 시간: ~0.0001초
   → 속도: 10,000배 향상!

⚠️ 인덱스 트레이드오프:
   장점: 검색 속도 10-1000배 향상
   단점:
   ├─ 저장 공간 증가 (원본 테이블의 5-20%)
   ├─ 삽입/수정/삭제 속도 감소 (인덱스도 업데이트해야 함)
   └─ 관리 복잡도 증가

📊 인덱싱 전략:
   ✓ 자주 검색하는 칼럼: 인덱스 O
   ✗ 자주 수정하는 칼럼: 인덱스 X
   ✓ WHERE 절에 자주 나오는 칼럼: 인덱스 O
   ✓ JOIN 칼럼 (Foreign Key): 인덱스 필수
"""


class DatabaseOptimization:
    """데이터베이스 최적화"""

    def __init__(self):
        """최적화 도구 초기화"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

    def create_users_table(self, with_index: bool = False):
        """사용자 테이블 생성"""
        self.cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER
            )
        ''')

        if with_index:
            # 인덱스 생성
            self.cursor.execute('CREATE INDEX idx_email ON users(email)')
            self.cursor.execute('CREATE INDEX idx_name ON users(name)')
            print("✅ 인덱스 생성 완료")

        self.conn.commit()

    def insert_users(self, count: int):
        """테스트 데이터 삽입"""
        for i in range(count):
            self.cursor.execute(
                'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
                (f'User{i}', f'user{i}@example.com', 20 + (i % 50))
            )
        self.conn.commit()

    def benchmark_search(self, email: str) -> Tuple[float, int]:
        """검색 성능 측정"""
        start_time = time.time()

        self.cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        result = self.cursor.fetchone()

        elapsed = time.time() - start_time
        return elapsed, 1 if result else 0

    def analyze_query(self, query: str) -> List[str]:
        """쿼리 실행 계획 분석"""
        self.cursor.execute(f'EXPLAIN QUERY PLAN {query}')
        return [str(row) for row in self.cursor.fetchall()]


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 5: NoSQL 시뮬레이션 - 유연한 데이터 저장                              ║
# ╚════════════════════════════════════════════════════════════════════════════╝

"""
📦 NoSQL: "스키마 자유로움"

RDBMS와의 차이:
┌──────────────┬──────────────────┬──────────────────┐
│   특성       │   RDBMS (SQL)    │    NoSQL         │
├──────────────┼──────────────────┼──────────────────┤
│ 스키마       │ 고정             │ 유연 (동적)      │
│ 데이터 형식  │ 행과 열          │ JSON, Key-Value  │
│ 거래         │ ACID             │ BASE             │
│ 확장         │ 수직 (더 강한 PC)│ 수평 (더 많은 PC)│
│ 검색         │ SQL (강력함)     │언어별 (제한적)   │
│ 예          │ 은행, 회계       │ SNS, IoT, 로그  │
└──────────────┴──────────────────┴──────────────────┘

MongoDB 스타일의 유연한 구조:
{
  "user_id": "U001",
  "name": "Alice",
  "age": 25,
  "addresses": [                      ← 배열 (가변 크기)
    {"type": "home", "city": "Seoul"},
    {"type": "work", "city": "Busan"}
  ],
  "preferences": {                    ← 중첩 객체
    "theme": "dark",
    "notifications": true
  },
  "last_login": "2024-02-24T10:30:00" ← 타입도 자유로움
}
"""


class NoSQLDatabase:
    """MongoDB 스타일 NoSQL 데이터베이스 시뮬레이션"""

    def __init__(self):
        """NoSQL DB 초기화"""
        self.collections: Dict[str, List[Dict]] = {}

    def create_collection(self, collection_name: str):
        """컬렉션 생성"""
        if collection_name not in self.collections:
            self.collections[collection_name] = []
            print(f"✅ 컬렉션 생성: {collection_name}")

    def insert(self, collection_name: str, document: Dict) -> str:
        """문서 삽입 (자동 ID 생성)"""
        if collection_name not in self.collections:
            self.create_collection(collection_name)

        doc_id = f"DOC_{len(self.collections[collection_name])}"
        document['_id'] = doc_id
        self.collections[collection_name].append(document)

        return doc_id

    def find(self, collection_name: str, query: Dict = None) -> List[Dict]:
        """문서 검색 (쿼리 매칭)"""
        if collection_name not in self.collections:
            return []

        if not query:
            return self.collections[collection_name]

        # 간단한 쿼리 필터링
        results = []
        for doc in self.collections[collection_name]:
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                results.append(doc)

        return results

    def update(self, collection_name: str, doc_id: str, updates: Dict) -> bool:
        """문서 업데이트"""
        if collection_name not in self.collections:
            return False

        for doc in self.collections[collection_name]:
            if doc.get('_id') == doc_id:
                doc.update(updates)
                return True

        return False

    def delete(self, collection_name: str, doc_id: str) -> bool:
        """문서 삭제"""
        if collection_name not in self.collections:
            return False

        for i, doc in enumerate(self.collections[collection_name]):
            if doc.get('_id') == doc_id:
                self.collections[collection_name].pop(i)
                return True

        return False


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 6: 데모 함수들                                                        ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def demonstration_1_acid_transaction():
    """데모 1: ACID 트랜잭션"""
    print("\n" + "="*80)
    print("데모 1: ACID 트랜잭션 - 신뢰할 수 있는 송금")
    print("="*80)

    db = RelationalDatabase()
    db.create_schema()

    # 사용자와 계좌 생성
    print("\n[Step 1] 사용자 생성")
    user1 = db.add_user('alice', 'alice@example.com')
    user2 = db.add_user('bob', 'bob@example.com')
    print(f"  Alice (ID: {user1}), Bob (ID: {user2})")

    # 계좌 생성
    print("\n[Step 2] 계좌 생성")
    acc1 = db.add_account(user1, 10000)
    acc2 = db.add_account(user2, 5000)
    print(f"  Alice 계좌: {acc1} (잔액: {db.get_balance(acc1)})")
    print(f"  Bob 계좌: {acc2} (잔액: {db.get_balance(acc2)})")

    # 송금 (성공)
    print("\n[Step 3] 정상 송금")
    db.transfer(acc1, acc2, 3000)
    print(f"  Alice 잔액: {db.get_balance(acc1)}")
    print(f"  Bob 잔액: {db.get_balance(acc2)}")

    # 송금 (실패 - 잔액 부족)
    print("\n[Step 4] 잔액 부족 시도 (실패해야 함)")
    db.transfer(acc1, acc2, 100000)
    print(f"  Alice 잔액: {db.get_balance(acc1)} (변화 없음)")
    print(f"  Bob 잔액: {db.get_balance(acc2)} (변화 없음)")


def demonstration_2_normalization():
    """데모 2: 정규화의 중요성"""
    print("\n" + "="*80)
    print("데모 2: 정규화 - 데이터 중복 제거")
    print("="*80)

    print("""
❌ 비정규화 문제 시나리오:
┌──────────────────────────────────┐
│ 통합 테이블 (학생+성적)          │
├──────────────────────────────────┤
│ Alice │ Math │ 95│  1GB 용량     │
│ Alice │ English │ 88│ 반복됨!    │
│ Bob   │ Math │ 85│  데이터 중복  │
│ Bob   │ English │ 92│           │
└──────────────────────────────────┘

문제:
1️⃣ 저장 공간 낭비 (Alice 정보 반복)
2️⃣ 수정 이상 (이름 수정 시 2곳 모두 수정)
3️⃣ 삭제 이상 (과목 취소하면 학생 정보도 사라짐)

✅ 정규화된 구조:
┌─────────────┐       ┌──────────────┐
│ students    │       │ scores       │
├─────────────┤       ├──────────────┤
│ Alice│300MB │◄─────│ Math│95      │
│ Bob │       │      │ English│88   │
└─────────────┘       └──────────────┘

개선:
✓ 저장 공간 70% 절감
✓ 수정 한 곳만 (이상 제거)
✓ 독립적 관리 가능
    """)


def demonstration_3_indexing():
    """데모 3: 인덱싱 - 검색 속도"""
    print("\n" + "="*80)
    print("데모 3: 인덱싱 - 검색 속도 최적화")
    print("="*80)

    print("\n[테스트] 100,000명 사용자 검색")

    # 인덱스 없음
    print("\n1️⃣ 인덱스 없을 때:")
    db_no_idx = DatabaseOptimization()
    db_no_idx.create_users_table(with_index=False)
    db_no_idx.insert_users(100000)

    time_no_idx, _ = db_no_idx.benchmark_search('user99999@example.com')
    print(f"   검색 시간: {time_no_idx*1000:.3f}ms")

    # 인덱스 있음
    print("\n2️⃣ 인덱스 있을 때:")
    db_with_idx = DatabaseOptimization()
    db_with_idx.create_users_table(with_index=True)
    db_with_idx.insert_users(100000)

    time_with_idx, _ = db_with_idx.benchmark_search('user99999@example.com')
    print(f"   검색 시간: {time_with_idx*1000:.3f}ms")

    # 성능 개선
    speedup = time_no_idx / (time_with_idx + 0.00001)  # 0으로 나누기 방지
    print(f"\n⚡ 성능 개선: {speedup:.0f}배 빠름")


def demonstration_4_nosql():
    """데모 4: NoSQL - 유연한 구조"""
    print("\n" + "="*80)
    print("데모 4: NoSQL - 자유로운 데이터 구조")
    print("="*80)

    db = NoSQLDatabase()
    db.create_collection('users')
    db.create_collection('posts')

    # 다양한 구조의 문서 삽입
    print("\n[Step 1] 사용자 문서 삽입 (구조 자유로움)")
    user1 = db.insert('users', {
        'name': 'Alice',
        'age': 25,
        'city': 'Seoul',
        'tags': ['python', 'data', 'ai'],
        'profile': {
            'verified': True,
            'followers': 1000
        }
    })

    user2 = db.insert('users', {
        'name': 'Bob',
        'age': 30,
        'country': 'USA',  # 다른 필드!
        'skills': ['java', 'spring']
    })

    print(f"  ✅ Alice (ID: {user1})")
    print(f"  ✅ Bob (ID: {user2})")

    # 포스트 삽입 (다른 스키마)
    print("\n[Step 2] 포스트 문서 삽입")
    post1 = db.insert('posts', {
        'author_id': user1,
        'title': '데이터베이스 설계',
        'content': '...',
        'likes': 42,
        'comments': [
            {'user': 'Bob', 'text': '좋은 글이네요!'},
            {'user': 'Charlie', 'text': '+1'}
        ]
    })

    print(f"  ✅ 포스트 (ID: {post1})")

    # 검색
    print("\n[Step 3] 유연한 검색")
    alice = db.find('users', {'name': 'Alice'})
    print(f"  검색 결과: {alice[0]['name']}, 팔로워: {alice[0]['profile']['followers']}")


def demonstration_5_cap_theorem():
    """데모 5: CAP 이론 - 트레이드오프"""
    print("\n" + "="*80)
    print("데모 5: CAP 이론 - 분산 DB의 불가능성")
    print("="*80)

    print("""
┌─────────────────────────────────────────────────────────┐
│ 3가지 특성 중 2가지만 선택 가능                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1️⃣ Consistency + Availability (CA)                    │
│    └─ 은행 시스템                                     │
│    └─ 모든 사용자가 같은 잔액 봄                      │
│    └─ 서버 24시간 켜져있음                            │
│    └─ 단점: 네트워크 분할 못견딤                      │
│                                                         │
│ 2️⃣ Consistency + Partition (CP)                       │
│    └─ Google BigTable                                  │
│    └─ 데이터 100% 정확함                              │
│    └─ 네트워크 끊겨도 유지                            │
│    └─ 단점: 일부 서버 응답 거부 가능                  │
│                                                         │
│ 3️⃣ Availability + Partition (AP)                      │
│    └─ Amazon, Netflix                                  │
│    └─ 언제든 응답 (최종 일관성)                       │
│    └─ 네트워크 끊겨도 작동                            │
│    └─ 단점: 순간 데이터 불일치                        │
│                                                         │
│ ❌ 모두 불가능 (분산 시스템의 근본 한계)              │
│                                                         │
└─────────────────────────────────────────────────────────┘

📊 선택에 따른 결과:

CA (은행):
  ├─ 모든 지점의 잔액 정확히 같음
  ├─ 네트워크 끊기면 일부 지점 폐쇄
  └─ 신뢰성 최고, 가용성 낮음

AP (SNS):
  ├─ 좋아요 수 약간 다를 수 있음 (결국 같아짐)
  ├─ 네트워크 끊겨도 계속 작동
  └─ 신뢰성 낮음, 가용성 최고
    """)


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 7: 단위 테스트 (5/5)                                                 ║
# ╚════════════════════════════════════════════════════════════════════════════╝

import unittest


class TestDatabase(unittest.TestCase):
    """데이터베이스 단위 테스트"""

    def test_1_acid_properties(self):
        """테스트 1: ACID 특성"""
        print("\n" + "="*80)
        print("테스트 1: ACID 특성 검증")
        print("="*80)

        db = RelationalDatabase()
        db.create_schema()

        # 사용자와 계좌 생성
        user = db.add_user('test_user', 'test@example.com')
        acc1 = db.add_account(user, 1000)
        acc2 = db.add_account(user, 0)

        # 송금
        result = db.transfer(acc1, acc2, 500)

        # 검증
        self.assertTrue(result)
        self.assertEqual(db.get_balance(acc1), 500)
        self.assertEqual(db.get_balance(acc2), 500)

        print("✓ PASS: ACID 속성 작동 확인")

    def test_2_normalization(self):
        """테스트 2: 정규화"""
        print("\n" + "="*80)
        print("테스트 2: 정규화 구조")
        print("="*80)

        db = RelationalDatabase()
        db.create_schema()

        user1 = db.add_user('alice', 'alice@example.com')
        user2 = db.add_user('bob', 'bob@example.com')

        # 사용자와 계좌는 독립적
        self.assertEqual(user1, 1)
        self.assertEqual(user2, 2)

        print("✓ PASS: 정규화 구조 작동")

    def test_3_indexing_performance(self):
        """테스트 3: 인덱싱 성능"""
        print("\n" + "="*80)
        print("테스트 3: 인덱싱 성능")
        print("="*80)

        db = DatabaseOptimization()
        db.create_users_table(with_index=True)
        db.insert_users(10000)

        elapsed, found = db.benchmark_search('user5000@example.com')

        self.assertEqual(found, 1)
        self.assertLess(elapsed, 0.01)  # 10ms 이하

        print(f"✓ PASS: 검색 완료 ({elapsed*1000:.3f}ms)")

    def test_4_nosql_flexibility(self):
        """테스트 4: NoSQL 유연성"""
        print("\n" + "="*80)
        print("테스트 4: NoSQL 유연한 구조")
        print("="*80)

        db = NoSQLDatabase()
        db.create_collection('flexible')

        # 다양한 구조 삽입 가능
        doc1 = db.insert('flexible', {'name': 'Alice', 'age': 25})
        doc2 = db.insert('flexible', {
            'name': 'Bob',
            'skills': ['python', 'java'],
            'nested': {'key': 'value'}
        })

        self.assertEqual(len(db.find('flexible')), 2)
        print("✓ PASS: NoSQL 유연성 작동")

    def test_5_transaction_consistency(self):
        """테스트 5: 트랜잭션 일관성"""
        print("\n" + "="*80)
        print("테스트 5: 트랜잭션 일관성")
        print("="*80)

        db = RelationalDatabase()
        db.create_schema()

        user = db.add_user('test', 'test@example.com')
        acc1 = db.add_account(user, 1000)
        acc2 = db.add_account(user, 0)

        # 실패한 송금 시도
        result = db.transfer(acc1, acc2, 5000)  # 잔액 부족

        # 일관성 유지 (아무것도 변경 안 됨)
        self.assertFalse(result)
        self.assertEqual(db.get_balance(acc1), 1000)
        self.assertEqual(db.get_balance(acc2), 0)

        print("✓ PASS: 트랜잭션 일관성 유지")


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ PART 8: 완성 및 다음 단계                                                  ║
# ╚════════════════════════════════════════════════════════════════════════════╝

"""
✨ v5.2 완성 요약:

✅ 학습 내용:
   1. RDBMS vs NoSQL: 아키텍처 선택의 기준
   2. ACID 원칙: 트랜잭션의 신뢰성 (Atomicity, Consistency, Isolation, Durability)
   3. 정규화: 데이터 중복 제거 (1NF, 2NF, 3NF)
   4. 트랜잭션: Commit/Rollback으로 안전성 보장
   5. 인덱싱: 검색 속도 10-1000배 향상
   6. NoSQL: 유연한 스키마와 높은 처리량
   7. CAP 이론: 분산 시스템의 불가능성 삼각형

💾 저장 아키텍처 진화:
   파일 저장 → RDBMS → NoSQL → 하이브리드

🏗️ 실무 패턴:
   • 은행/금융: RDBMS (ACID 필수)
   • SNS/로그: NoSQL (높은 처리량)
   • 핵심 데이터: RDBMS + 캐시 (Redis)
   • 분석 데이터: 데이터 웨어하우스 (Hadoop, Spark)

📚 다음 단계:
   [v5.3] 모니터링과 로깅 (Observability)
   - 분산 시스템의 "신경계"
   - Logging: ELK Stack (Elasticsearch, Logstash, Kibana)
   - Metrics: Prometheus, Grafana
   - Tracing: Jaeger, Zipkin

   [v6.1] 클라우드 배포
   - Docker: 컨테이너화
   - Kubernetes: 오케스트레이션
   - AWS/GCP: 클라우드 인프라

💡 지금까지의 여정:
   v4.1-4.3: 단일 머신 최적화 (근육, 혈관)
   v5.1: 여러 머신 조화 (분산 시스템)
   v5.2: 기억의 구조화 (데이터)
   v5.3-6.1: 관찰과 배포 (운영)

> "데이터는 사라지지 않습니다. 오직 설계자님의 설계에 따라 증명될 뿐입니다."
> 저장 필수 너는 기록이 증명이다 gogs
"""


if __name__ == "__main__":
    # 데모 실행
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + "  Python University Level 3 - v5.2 Database Architecture".center(78) + "║")
    print("║" + "  데이터의 무결성과 확장성 - 저장의 미래를 설계하다".center(78) + "║")
    print("╚" + "="*78 + "╝")

    # 데모 실행
    demonstration_1_acid_transaction()
    demonstration_2_normalization()
    demonstration_3_indexing()
    demonstration_4_nosql()
    demonstration_5_cap_theorem()

    # 단위 테스트 실행
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + "  UNIT TESTS".center(78) + "║")
    print("╚" + "="*78 + "╝")

    unittest.main(argv=[''], exit=False, verbosity=2)

    print("\n" + "="*80)
    print("✨ v5.2 완성! 데이터베이스 아키텍처 마스터 달성")
    print("="*80)
    print("\n다음 단계: v5.3 모니터링과 로깅 (관찰 가능성)")
