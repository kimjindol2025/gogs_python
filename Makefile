# gogs_python 프로젝트 Makefile
# "기록이 증명이다" - Python 모범 사례를 실행으로 검증

.PHONY: help setup install install-dev test lint format type-check clean

# 기본값
PYTHON := python3
PIP := $(PYTHON) -m pip
BLACK := $(PYTHON) -m black
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy
PYTEST := $(PYTHON) -m pytest

# 색상 정의
RESET := \033[0m
BOLD := \033[1m
GREEN := \033[32m
BLUE := \033[34m

help:
	@echo "$(BOLD)gogs_python 개발 가이드$(RESET)"
	@echo ""
	@echo "$(GREEN)설치$(RESET)"
	@echo "  make setup        - 개발 환경 설정"
	@echo "  make install      - 프로덕션 설치 (pip install .)"
	@echo "  make install-dev  - 개발 의존성 설치"
	@echo ""
	@echo "$(GREEN)개발$(RESET)"
	@echo "  make format       - 코드 자동 포매팅 (Black)"
	@echo "  make lint         - PEP8 검증 (Flake8)"
	@echo "  make type-check   - 타입 검사 (mypy)"
	@echo "  make test         - 테스트 실행 (pytest)"
	@echo ""
	@echo "$(GREEN)청소$(RESET)"
	@echo "  make clean        - 빌드 및 캐시 파일 제거"
	@echo "  make clean-test   - 테스트 캐시 제거"
	@echo ""

setup: install-dev
	@echo "$(GREEN)✓ 개발 환경 설정 완료$(RESET)"

install:
	$(PIP) install .

install-dev:
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✓ 개발 의존성 설치 완료$(RESET)"

# 코드 형식화
format:
	@echo "$(BLUE)→ Black으로 코드 포매팅 중...$(RESET)"
	$(BLACK) .
	@echo "$(GREEN)✓ 포매팅 완료$(RESET)"

# PEP8 검증
lint:
	@echo "$(BLUE)→ Flake8으로 PEP8 검증 중...$(RESET)"
	$(FLAKE8) .
	@echo "$(GREEN)✓ PEP8 검증 통과$(RESET)"

# 타입 검사
type-check:
	@echo "$(BLUE)→ mypy로 타입 검사 중...$(RESET)"
	$(MYPY) . --strict
	@echo "$(GREEN)✓ 타입 검사 통과$(RESET)"

# 테스트 실행
test:
	@echo "$(BLUE)→ pytest로 테스트 실행 중...$(RESET)"
	$(PYTEST) tests/ -v --tb=short
	@echo "$(GREEN)✓ 모든 테스트 통과$(RESET)"

# 모든 검사 실행
check: lint type-check test
	@echo "$(GREEN)✓ 모든 검사 통과$(RESET)"

# 정리
clean: clean-test clean-build

clean-build:
	@rm -rf build dist *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ 빌드 파일 제거 완료$(RESET)"

clean-test:
	@rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	@find . -type f -name "*.coverage" -delete
	@echo "$(GREEN)✓ 테스트 캐시 제거 완료$(RESET)"

