# AX 마케팅 매니저 MVP

대화로 캠페인 정보를 채우고, Capa 확인 → 카피 생성 → 기획안 확정 → JSON 생성 → 어드민 이동까지 시험하는 Streamlit MVP입니다.

## 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 표시되는 로컬 주소(기본 `http://localhost:8501`)로 접속합니다.

## 샘플 입력

```text
군체 프로모션을 2026년 7월 28일부터 8월 12일까지 TARGET으로 진행해줘.
구매 시 3,000P를 지급하고 목표 Capa는 80만 명이야.
```

## 구조

```text
app.py                  Streamlit 화면과 사용자 흐름
marketing_mvp/
  models.py             캠페인 기본값과 검증
  extractor.py          사용자 문장의 필드 추출
  repository.py         SQLite 저장소
  capa_service.py       교체 가능한 Capa 조회 인터페이스와 mock
  copy_service.py       교체 가능한 카피 생성 서비스
  workflow.py           다음 질문과 JSON 변환
  integration_contract.py  B tv JSON·Mermaid 고정 계약 및 검증
data/
  mock_capa.json        Capa 샘플 데이터
tests/                  핵심 로직 테스트
```

## 실제 연동으로 교체할 곳

- Google Sheets: `marketing_mvp/capa_service.py`의 `CapaService` 규격을 유지한 채 `GoogleSheetsCapaService`를 추가합니다.
- AI/LLM: `extractor.py`와 `copy_service.py`의 공개 함수 규격을 유지한 채 회사 승인 API 호출로 바꿉니다.
- 어드민: 기본 연결 주소는 `https://btvcuration.github.io/campaign/`입니다. 전송 규격이 제공되지 않은 상태이므로 임의의 URL 파라미터를 만들지 않으며, 계약 검증을 통과한 JSON을 저장한 뒤 어드민으로 이동합니다. 주소 변경이 필요하면 환경변수 `ADMIN_BASE_URL`을 설정합니다.

## B tv 연동 계약

- 최상위 구조는 `action`, `mermaidCode`, `rawGasData`로 고정됩니다.
- `action`은 `CREATE_CAMPAIGN_ASSETS`로 고정됩니다.
- 배너별 `data` 필수 Key와 데이터 타입은 `integration_contract.py`에서 검증합니다.
- Mermaid UI 노드는 고정 이미지 URL과 `width='100'` 형식을 사용합니다.
- Userflow와 `assets`가 1:1로 일치하고 검수를 통과한 경우에만 최종 JSON을 생성합니다.
