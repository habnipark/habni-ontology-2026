# 다음 세션 시작 가이드: 새 로컬 환경 셋업

## 1. 저장소 클론

```bash
git clone https://github.com/habnipark/habni-ontology-2026.git
cd habni-ontology-2026
```

## 2. 옵시디언 설치 및 Vault 열기

1. https://obsidian.md 에서 다운로드/설치
2. 옵시디언 실행 → **"열기"** (또는 Open folder as vault)
3. 클론한 저장소의 `vault/` 폴더 선택

## 3. 커뮤니티 플러그인 활성화

1. 설정(톱니바퀴) → **커뮤니티 플러그인** → **"커뮤니티 플러그인 사용"** 활성화

## 4. 플러그인 설치 (4개)

커뮤니티 플러그인 → **찾아보기**:

| 검색어 | 설치 후 설정 |
|---|---|
| `Dataview` | Enable. 설정에서 **Enable JavaScript Queries**, **Enable Inline Queries** ON |
| `Templater` | Enable. 아래 5단계 참고 |
| `Calendar` | Enable |
| `Importer` | Enable |

## 5. Templater 설정

설정 → Templater:

1. **Template folder location**: `Templates`
2. **Trigger Templater on new file creation**: ON
3. **Enable Folder Templates**: ON
4. **+** 버튼으로 매핑 추가:

| 폴더 | 템플릿 |
|---|---|
| `0-Inbox` | `inbox-template` |
| `1-Concept` | `concept-template` |
| `2-Project` | `project-template` |
| `3-Resource` | `resource-template` |
| `4-Log` | `log-template` |
| `5-Output` | `output-template` |

## 6. 검증

1. `MOC/Dashboard.md` 열기 → Dataview 테이블 표시 확인
2. `1-Concept` 폴더에서 새 노트 생성 → 템플릿 자동 적용 확인
3. Graph View 열기 → 노트 연결 확인

## 7. 다음 작업 (SP2 계속)

아직 마이그레이션하지 않은 Notion 자료:
- 여행 기록 (방콕, 파리, 하노이 등) → 4-Log
- 업무 프로젝트 (관광공사, KOTRA, 교보문고 등) → 2-Project
- 유튜브 대본, 광고 데이터, 포트폴리오
- 타임아웃 2권 재시도: 쓰고 상상하고 실행하라, 프리워커스

**주의:** Notion API 키는 재생성 필요 (이전 키 노출됨).
Notion Integration 설정 → 시크릿 재생성 후 환경변수로 설정:
```bash
export NOTION_API_KEY="새로운_키"
```
