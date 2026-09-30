# 이가은 | AI Engineer Portfolio

사용자의 업무에 맞게 데이터를 가공하고, AI의 출력을 서비스에 연결합니다.

## 대표 프로젝트: Blooming CRM

- 기간: 2025.12.02–2026.01.08
- 주제: 페르소나 기반 개인화 뷰티 CRM 메시지 생성
- 팀 저장소: [Blooming CRM](https://github.com/Joonsung-Byun/blooming-v1)
- 담당: 초기 LLM 상품 추천, 추천 API 연동, 데이터 변환 및 서비스 통합 보완
- 기술: Python, FastAPI, Pydantic, OpenAI API, Supabase, LangGraph 기반 서비스 연동
- [본인 구현과 문제 해결 기록](https://github.com/Joonsung-Byun/blooming-v1/blob/main/docs/gaeun-contributions.md)

### 문제와 해결

| 문제 | 본인의 행동 | 확인 가능한 근거 |
|---|---|---|
| 고객마다 보유한 정보가 다름 | 프로필·구매/행동 이력 유무를 네 가지 경우로 나눠 LLM 추천 입력 구성 | [초기 추천 구현](https://github.com/Joonsung-Byun/blooming-v1/commit/d49cb48a3bf7a6aed3b63f8d203a953dc2dcbc8e) |
| 실제 상품 스키마와 코드의 가정이 다름 | 상품 식별자와 카테고리 변환 수정, 누락 카테고리 확인 코드 작성 | [스키마·확인 코드](https://github.com/Joonsung-Byun/blooming-v1/commit/d5021f5cdf13d7696e6628f340fc5e3a0877cf48) |
| 추천 API와 백엔드의 필드·자료형 불일치 | 브랜드 목록 정규화, 발송 목적과 추천 의도 연결, 결과 없음 처리 | [API 통합 보완](https://github.com/Joonsung-Byun/blooming-v1/commit/d3f7192ceeb13f4b55e6de582c5ed238db395710) |
| 메시지 저장·조회 기준 불일치 | 페르소나 ID 기준 통일, 백엔드 이력을 프런트에서 조회하도록 수정 | [이력 흐름 수정](https://github.com/Joonsung-Byun/blooming-v1/commit/f63e5a47e0f44b0f7aa7106581f958365dbecf14) |

현재 팀 추천 API는 벡터 검색·Cross-Encoder 기반 경로를 사용합니다. 초기 LLM 추천과 현재 추천 방식을 구분하며, 팀 전체의 구현을 개인 단독 성과로 제시하지 않습니다.

## 추가 프로젝트: 모바일 환경 자전거 도로 이상 탐지

- 기간: 2025.04.22–2025.06.16
- 목표: 도로 위험 요소 탐지 모델의 연산 부담 감소
- 담당: YOLO11 기반 Ghost Convolution 적용, 백본·넥 구조 변경, 데이터 변환 및 추론 성능 측정
- [프로젝트와 코드](https://github.com/helenalee02/deepsys_final)

## 관련 개발 경험

### 메디룰 인턴 — FDA 문서 RAG
2025.08.12–2025.09.11. 문서 수집, 페이지 단위 청킹, 출처·문서 유형 메타데이터 관리, Gemma 기반 키워드 추출, 유사도 검색 및 로컬 LLM 답변·참고 문서 반환을 담당했습니다. 이 페이지에는 회사 코드나 내부 문서를 포함하지 않습니다.

### Agora — 멀티에이전트 토론 서비스
2026.03.03–2026.06.14. 오케스트레이터와 백엔드 API 통합·보완, FastAPI와 SSE 기반 진행 상태·응답 전달, 토론 기록과 평가 저장, 뉴스 수집 흐름 분리를 경험했습니다.

### Smart Note — 온라인 강의 문서화
2025.06.24–2025.08.27. PDF 페이지 변환, DocLayout-YOLO 기반 레이아웃 분석, OpenCV 마스킹, OCR용 데이터 가공을 담당했습니다.

## 학습 및 구현 기록

- [생성형 AI 학습 저장소](https://github.com/helenalee02/ktcloud_Genai)
- [소음 데이터를 활용한 산책 경로 탐색](https://github.com/helenalee02/traffic)

## 검증 범위

링크가 제공된 프로젝트는 공개 코드와 커밋에서 구현 내용을 확인할 수 있습니다. 관련 개발 경험은 개인 경험 요약입니다. 재현 조건이 확인되지 않은 정확도·처리 속도·매출 개선 수치는 제시하지 않습니다.
