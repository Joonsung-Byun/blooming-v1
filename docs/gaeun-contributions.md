# 이가은의 Blooming CRM 기여 기록

- GitHub: [helenalee02](https://github.com/helenalee02)
- 프로젝트 기간: 2025.12.02–2026.01.08
- 역할: 초기 LLM 추천 기능과 추천 API 연동, 데이터 변환 및 서비스 통합 보완
- 범위: 아래 개인 기여는 본인 작성 커밋으로 연결합니다. 팀의 전체 시스템과 개인 구현 범위를 구분합니다.

## 1. 고객 정보에 따른 초기 추천 기능

고객 프로필과 구매·행동 이력의 유무를 네 경우로 구분하여 LLM 입력을 구성했습니다. Supabase 상품 정보를 활용하고, JSON 응답의 상품 ID가 후보 목록에 포함되는지 확인하는 방식으로 구현했습니다.

- [초기 구현 커밋](https://github.com/Joonsung-Byun/blooming-v1/commit/d49cb48a3bf7a6aed3b63f8d203a953dc2dcbc8e)
- 초기 구현 파일은 당시 `RecSys/recommendation_model.py`이며, 현재 [LLM 추천 코드](../RecSys/recommendation_model_API_advanced.py)와 [운영 API 진입점](../RecSys/main.py)을 구분해서 확인할 수 있습니다.
- 현재 API 진입점은 `recommendation_model_API.py`를 사용합니다. 현재의 벡터 검색·Cross-Encoder 전체를 개인 단독 구현으로 주장하지 않습니다.

## 2. 실제 데이터 스키마에 맞춘 변환

상품 ID·상품 코드 및 카테고리 필드를 실제 데이터 구조에 맞췄습니다. 카테고리의 일부 값이 누락되더라도 존재하는 항목으로 문자열을 구성하도록 보완했습니다.

- [스키마 보완 및 확인 코드 추가](https://github.com/Joonsung-Byun/blooming-v1/commit/d5021f5cdf13d7696e6628f340fc5e3a0877cf48)
- [정상/누락 카테고리 파싱 확인 코드](../RecSys/test_schema_parsing.py)

이 확인 코드는 샘플 데이터를 출력하여 변환을 점검하는 스크립트입니다. 전체 추천 품질이나 서비스 통합을 보장하는 자동화 테스트와는 구분합니다.

## 3. 추천 API와 메시지 생성의 연결

브랜드 값의 문자열/목록 차이를 정규화하고, 백엔드의 `crm_reason`을 추천 API의 `intention`으로 매핑했습니다. 이전 상태 정의를 보완하고 추천 결과가 없는 경우도 처리했습니다.

- [상태 및 입력 연결](https://github.com/Joonsung-Byun/blooming-v1/commit/38e11f5e90d5bf6e17c96acd5d220610e9965245)
- [브랜드 자료형·발송 목적·결과 없음 처리](https://github.com/Joonsung-Byun/blooming-v1/commit/d3f7192ceeb13f4b55e6de582c5ed238db395710)
- [현재 정보 조회·추천 연동 코드](../backend/actions/info_retrieval.py)

## 4. 생성 이후 이력 조회까지 보완

메시지 저장·조회에서 페르소나 이름 대신 ID를 사용하도록 맞췄습니다. 프런트엔드의 별도 저장 흐름을 제거하고 백엔드가 저장한 `crm_message_history`를 조회해 화면에 맞게 변환하도록 수정했습니다.

- [이력 흐름 수정 커밋](https://github.com/Joonsung-Byun/blooming-v1/commit/f63e5a47e0f44b0f7aa7106581f958365dbecf14)
- [저장 노드](../backend/actions/save_crm.py) · [조회 노드](../backend/actions/retrieve_crm.py) · [프런트 조회](../frontend/src/services/logService.ts)

## 배운 점

추천 모델의 출력만으로 사용자가 결과를 얻는 것은 아닙니다. 데이터베이스, API, 에이전트 상태, 저장·조회 사이의 식별자와 자료형이 맞아야 전체 흐름이 연결됩니다. 오류가 발생한 경계를 좁히고 입력 변환부터 최종 조회까지 확인하는 관점을 익혔습니다.

## 재현 및 평가 범위

- [실행 안내](../README.md)를 참고하세요. 외부 API 및 Supabase 데이터·설정이 필요합니다.
- 코드와 커밋을 근거로 구현·수정 내용을 제시합니다.
- 독립적으로 재현한 정량 성능 결과가 없으므로 정확도나 응답 시간 개선율은 주장하지 않습니다.
