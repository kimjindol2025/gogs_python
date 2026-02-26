#ifndef WCET_ANALYZER_H
#define WCET_ANALYZER_H

#include <string>
#include <unordered_map>
#include <vector>
#include <memory>
#include "../ast/ASTNode.h"

namespace zlang {

/**
 * 【 Step 4: WCET Analysis 】
 *
 * WCET (Worst-Case Execution Time): 최악의 경우 실행 시간
 * - 결정적 실행을 위해 임베디드 시스템에서 필수
 * - Exception path도 분석하여 안정성 보장
 */

struct WCETInfo {
    std::string node_name;
    unsigned long cycles;           // 추정 사이클 수
    unsigned long exception_cycles; // 예외 처리 사이클
    bool has_loop = false;
    int loop_depth = 0;
    bool is_critical_path = false;  // 임계 경로 여부
};

/**
 * WCET 분석기
 * - 함수별 최악의 경우 실행 시간 계산
 * - Exception path 추적
 * - Handler stack 최적화
 */
class WCETAnalyzer {
public:
    WCETAnalyzer();

    /**
     * 프로그램 분석
     * @param program 분석할 프로그램
     * @return 분석 성공 여부
     */
    bool analyze(const std::shared_ptr<ProgramNode>& program);

    /**
     * 함수의 WCET 조회
     * @param func_name 함수명
     * @return WCET 정보 (없으면 0)
     */
    unsigned long getWCET(const std::string& func_name) const;

    /**
     * Exception path WCET 조회
     */
    unsigned long getExceptionWCET(const std::string& func_name) const;

    /**
     * 임계 경로 함수들
     */
    std::vector<std::string> getCriticalPaths() const;

    /**
     * 분석 결과 보고
     */
    void printReport() const;

private:
    std::unordered_map<std::string, WCETInfo> wcet_map;
    std::vector<std::string> critical_paths;

    // 분석 헬퍼
    unsigned long analyzeNode(const std::shared_ptr<ASTNode>& node, int depth);
    unsigned long analyzeFunction(const std::shared_ptr<FunctionNode>& func);

    // 명령어별 사이클 수 추정
    unsigned long getInstructionCycles(const std::string& instr_type);
};

} // namespace zlang

#endif // WCET_ANALYZER_H
