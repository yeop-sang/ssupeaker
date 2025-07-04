# 🧪 우리 프로젝트의 테스트 전략

이 문서는 우리 추천 시스템의 안정성을 보장하기 위한 테스트 전략과 방법을 설명합니다.

## 1. 테스트 목표

- **단위 테스트(Unit Test):** 각각의 핵심 기능(추천 로직, DB 검색 등)이 독립적으로 잘 작동하는지 확인합니다.
- **통합 테스트(Integration Test):** 코드 변경 후에도 기존 기능이 고장 나지 않았는지(회귀 테스트) 자동으로 검증하고, 전체 시스템이 처음부터 끝까지 잘 연결되어 동작하는지 보장합니다.

## 2. 테스트 파일 설명

| 파일명 | 주요 역할 | 테스트 종류 |
| :--- | :--- | :--- |
| `test_recommender_logic.py` | 추천기의 핵심 계산 로직(`recommend_from_db`)이 주어진 텍스트와 가장 유사한 음악을 DB에서 정확히 찾아내는지 검증합니다. | **유닛 테스트** |
| `test_api_flow.py` | 실제 오디오 파일을 API 서버에 업로드하여, 전체 파이프라인(파일 처리 → 추천 → 결과 반환)을 거쳐 유효한 추천 결과(JSON)가 반환되는지 검증합니다. DB가 없을 때 서버가 올바르게 시작되지 않는지도 확인합니다. | **통합 테스트** |

## 3. 테스트 실행 방법

프로젝트 루트 디렉토리에서 아래 명령어를 실행하여 모든 테스트를 한 번에 실행할 수 있습니다.

```bash
bash run_pytest.sh
```

각 테스트의 상세한 결과를 보려면 `-v` 옵션을 추가하세요.

```bash
bash run_pytest.sh -v
```

## 4. 주요 테스트 시나리오

- **유닛 테스트:**
  - 가짜 데이터(fixture)와 모의 객체(mock)를 사용하여, AI 모델이나 외부 라이브러리에 의존하지 않고 순수 계산 로직의 정확성을 검증합니다. (`test_recommender_logic.py`)

- **통합 테스트:**
  - 가짜 오디오 파일과 임시 데이터베이스를 생성하여 실제와 유사한 환경을 구성합니다.
  - FastAPI의 `TestClient`를 사용해 메모리상에서 API 서버를 실행하고, `/recommend/` 엔드포인트에 파일을 업로드하여 전체 추천 흐름이 정상적으로 완료되는지 확인합니다. (`test_recommend_endpoint_success`)
  - 임베딩 데이터베이스 파일이 존재하지 않을 때, 서버가 의도대로 `RuntimeError`를 발생시키며 시작되지 않는지 검증합니다. (`test_server_startup_fails_if_db_not_found`) 