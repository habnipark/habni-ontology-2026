# Personal Knowledge Ontology — 설계 문서

> 개인 문서를 옵시디언 기반 온톨로지로 구축하고, Next.js+MDX 블로그와 연결하는 시스템 설계

**작성일**: 2026-03-22
**상태**: Draft
**범위**: Sub-project 1 — 옵시디언 온톨로지 스키마 설계

---

## 1. 프로젝트 개요

### 1.1 배경

- Notion에 파편적으로 흩어진 개인/업무 자료를 체계화
- 커리어(디지털 마케팅) 관련 기술 노트, 독서 기록, 여행 기록, 회사 자료 등을 포함
- 단순 폴더 정리가 아닌, 관계와 맥락이 있는 지식 온톨로지 구축

### 1.2 목표 (우선순위순)

1. **학습 갭 파악**: 내가 뭘 알고 뭘 모르는지 시각화
2. **자료 검색/탐색**: 흩어진 자료를 관계 기반으로 탐색
3. **지식 소화**: 회사 자료를 자기 것으로 학습하는 과정 지원
4. **콘텐츠 생산** (후순위): 온톨로지 기반 블로그 주제 추천 및 글쓰기

### 1.3 전체 시스템 구성 (4개 하위 프로젝트)

| # | 하위 프로젝트 | 설명 | 의존성 |
|---|---|---|---|
| 1 | 온톨로지 스키마 설계 | Vault 구조, 속성, 태그/링크 규칙 (본 문서) | 없음 |
| 2 | Notion → 옵시디언 마이그레이션 | 내보내기, 변환, 재구조화 | #1 완료 후 |
| 3 | 블로그 연결 파이프라인 | 옵시디언 → MDX → Next.js | #1, #2 완료 후 |
| 4 | 콘텐츠 제작 에이전트 | 주제 추천, 글쓰기 지원 | #1, #2, #3 완료 후 |

### 1.4 제약 조건

- **비용**: 무료 플랜 최대 활용 (옵시디언 무료, iCloud 동기화)
- **사용자**: 비개발자, 옵시디언 초보 — 학습 곡선 최소화 필요
- **기기**: Mac + iPhone/iPad (iCloud Drive 동기화)
- **보안**: 온톨로지에는 모든 정보 저장, 블로그 출력 시 회사명/수치 비노출, 동의 없는 외부 유출 금지

---

## 2. 설계: Vault 폴더 구조

### 2.1 접근법

**노트 타입 중심(Type-First)** 접근법을 채택한다. 폴더는 노트의 "종류"를 나타내고, 주제 분류는 속성과 태그가 담당한다.

선택 이유:
- 하나의 노트가 여러 맥락에 동시 연결 가능 (폴더 중심의 한계 극복)
- 학습 상태 추적이 자연스러움
- Notion DB 구조와의 속성 매핑 용이
- 블로그 파이프라인 연결 시 노트 타입별 처리 명확

### 2.2 폴더 구조

```
Vault/
├── 0-Inbox/          # 미분류 노트 임시 보관. Notion 자료 최초 진입점.
├── 1-Concept/        # 개념 노트. 1개념 = 1노트. (세션, GA4, SEO...)
├── 2-Project/        # 프로젝트/업무 기록. 클라이언트별, 프로젝트별.
├── 3-Resource/       # 독서, 강의, 아티클, 참고자료.
├── 4-Log/            # 일상 기록. 여행, 일지, 회고.
├── 5-Output/         # 블로그 초안, 발표자료, 결과물.
├── Templates/        # 노트 생성 시 자동 적용 템플릿.
└── MOC/              # Map of Content — 주제별 허브 문서.
```

**숫자 접두사(0~5)**: 파일 탐색기에서 일정한 순서 보장. 워크플로우 순서(수집→정리→활용→생산)와 대응.

### 2.3a Inbox 졸업 기준

0-Inbox의 노트가 아래 조건을 충족하면 해당 타입 폴더(1~5)로 이동한다:

- [ ] `type` 속성이 지정됨 (concept, project, resource, log, output 중 하나)
- [ ] `category` 속성이 지정됨 (career, life, side-project 중 하나)
- [ ] 태그가 1개 이상 부여됨
- [ ] 제목이 내용을 반영하도록 정리됨

### 2.3 대분류 (category 속성)

| category | 설명 |
|---|---|
| `career` | 업무, 직무, 기술 관련 |
| `life` | 개인 생활, 독서, 여행 |
| `side-project` | 개인 프로젝트, 블로그, 온톨로지 |

Learning은 별도 카테고리가 아닌 `learning-need` / `learning-status` 속성으로 관리한다. 어떤 카테고리의 노트든 학습 필요 표시가 가능.

---

## 3. 설계: 속성(Properties) 체계

### 3.1 공통 속성 (모든 노트)

| 속성 | 타입 | 값 | 설명 |
|---|---|---|---|
| `type` | text | concept, project, resource, log, output | 노트의 종류 (Templater가 폴더 기반 자동 설정) |
| `category` | text | career, life, side-project | 대분류 |
| `tags` | list | 자유 태그 | 세부 키워드 |
| `created` | date | YYYY-MM-DD | 생성일 |
| `updated` | date | YYYY-MM-DD | 수정일 |
| `learning-need` | boolean | true / false | 학습 필요 여부 |
| `learning-status` | text | not-started, in-progress, solid | 학습 진행 상태 |
| `visibility` | text | private, blog-safe | 블로그 공개 가능 여부 |

### 3.2 Concept 노트 전용 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `domain` | text | 도메인 (web-analytics, seo, ads, crm, content, dev, general) |
| `related-concepts` | list | 관련 개념 노트 링크 |
| `summary` | text | 한 줄 요약 (검색/MOC 표시용) |

### 3.3 Project 노트 전용 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `client` | text | 클라이언트명 |
| `project-status` | text | active, completed, archived |
| `period` | text | 프로젝트 기간 (YYYY-MM ~ YYYY-MM) |
| `key-concepts` | list | 핵심 개념 노트 링크 |
| `source` | text | personal, company (자료 출처) |

### 3.4 Resource 노트 전용 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `resource-type` | text | book, article, course, video, docs |
| `author` | text | 저자/출처 |
| `rating` | number | 평점 (1~5) |
| `read-date` | date | 읽은/수강 날짜 |
| `key-concepts` | list | 핵심 개념 노트 링크 |

### 3.5 Log 노트 전용 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `log-type` | text | travel, daily, weekly-review, memo |
| `location` | text | 장소 (선택) |
| `mood` | text | 기분 (선택) |

### 3.6 Output 노트 전용 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `output-type` | text | blog-draft, presentation, report |
| `output-status` | text | idea, drafting, review, published |
| `based-on` | list | 근거가 된 노트 링크 |
| `publish-url` | text | 게시 후 URL |

---

## 4. 설계: 태그 체계

### 4.1 계층형 태그 구조

옵시디언의 `#태그/하위태그` 형식을 사용. 상위 태그로 검색하면 하위 태그가 달린 노트까지 포함.

```
Career 도메인:
  #marketing
    #marketing/analytics
      #marketing/analytics/GA4
      #marketing/analytics/GTM
      #marketing/analytics/search-console
    #marketing/seo
    #marketing/ads
      #marketing/ads/google
      #marketing/ads/meta
    #marketing/crm
    #marketing/content
    #marketing/data-setup
      #marketing/data-setup/tracking
      #marketing/data-setup/tagging
  #dev
    #dev/web
    #dev/nextjs
    #dev/markdown

Life + Side Project:
  #reading
    #reading/nonfiction
    #reading/fiction
    #reading/tech
  #travel
    #travel/japan
    #travel/europe
    #travel/{지역명}
  #project
    #project/blog
    #project/ontology
```

태그는 시작점이며 사용하면서 자연스럽게 확장한다.

---

## 5. 설계: 링크 규칙

### 5.1 4가지 링크 규칙

| # | 규칙 | 설명 |
|---|---|---|
| 1 | 개념 노트 존재 시 반드시 링크 | `세션` 언급 + `1-Concept/세션.md` 존재 → `[[세션]]`으로 링크 |
| 2 | 미존재 개념도 링크 가능 | `[[전환율]]` → 빈 링크 = "아직 정리 안 된 개념" 신호 |
| 3 | 프로젝트 ↔ 개념 양방향 링크 | 프로젝트에서 `[[GA4]]` 언급 → GA4 백링크에 자동 표시 |
| 4 | Resource → Concept 출처 추적 | 독서 노트에서 `[[인지혁명]]` 링크 → 개념 노트에서 출처 역추적 |

### 5.2 태그 vs 링크 vs 속성 역할 분담

| 도구 | 역할 | 예시 |
|---|---|---|
| `#태그` | 주제 분류 (넓은 범위) | `#marketing/analytics` → 분석 관련 모든 노트 |
| `[[링크]]` | 구체적 관계 연결 | `[[GA4]]` → GA4와 직접 관련 |
| 속성 | 구조화된 메타데이터 (필터/쿼리) | `learning-status: in-progress` → 학습 중만 필터 |

---

## 6. 설계: 플러그인 구성

### 6.1 추천 플러그인 (4개)

| 플러그인 | 필요도 | 역할 |
|---|---|---|
| **Dataview** | 필수 | 속성 기반 쿼리/필터링 — 온톨로지의 핵심 엔진 |
| **Templater** | 필수 | 폴더별 자동 템플릿 적용 |
| **Calendar** | 권장 | 날짜 기반 노트 탐색 (Log 노트 활용) |
| **Obsidian Importer** | 권장 | Notion → 옵시디언 변환 (마이그레이션 단계) |

최소한의 플러그인으로 시작. 필요 시 추가.

### 6.2 핵심 Dataview 쿼리

**학습 갭 조회:**
```dataview
TABLE summary, domain, category
FROM "1-Concept"
WHERE learning-need = true AND learning-status = "not-started"
SORT created DESC
```

**회사 자료 소화 추적:**
```dataview
TABLE client, period, learning-status
FROM "2-Project"
WHERE source = "company" AND learning-status != "solid"
SORT learning-status ASC
```

**블로그 글감 후보:**
```dataview
TABLE summary, domain, tags
FROM "1-Concept" or "2-Project"
WHERE visibility = "blog-safe" AND learning-status = "solid"
SORT updated DESC
```

**올해 읽은 책:**
```dataview
TABLE author, rating, read-date
FROM "3-Resource"
WHERE resource-type = "book" AND read-date >= date(2026-01-01)
SORT rating DESC
```

**특정 개념 연결 노트 (예: 세션):**
```dataview
TABLE type, category, learning-status
FROM [[세션]]
SORT type ASC
```

---

## 7. 데이터 흐름

```
[Notion Export] → [0-Inbox] → 분류/속성 부여 → [1~4 폴더]
                                                    ↓
                              태그 + [[링크]]로 관계 형성 → Dataview로 조회/분석
                                                    ↓
                              MOC에서 주제별 탐색 → 학습 갭 발견 → 심화 학습
                                                    ↓
                              [5-Output] 블로그 초안 → MDX 변환 → Next.js
```

---

## 8. 동기화

- **방식**: iCloud Drive
- **기기**: Mac (주 작업) + iPhone/iPad (모바일 조회/간단 메모)
- **비용**: 무료 (iCloud 5GB — 텍스트 Vault는 수십 MB 수준)
- **Vault 위치**: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/habni-ontology/`
- **주의**: iCloud 동기화 시 간헐적 충돌 가능. 동일 노트를 여러 기기에서 동시 편집하지 않도록 주의. 충돌 발생 시 옵시디언이 `파일명 2.md` 형태로 복사본을 생성하므로, 주기적으로 확인하여 정리한다.

---

## 9. 보안 원칙

1. 온톨로지(옵시디언)에는 모든 정보를 제한 없이 저장
2. 로컬 + iCloud 저장 — 제3자 서버 미사용
3. 블로그 출력 시 회사명, 구체적 수치 비노출
4. `visibility` 속성으로 공개 가능 여부 관리
5. 동의 없는 외부 유출 절대 금지

---

## 10. 향후 확장 (Sub-project 2~4)

본 설계는 Sub-project 1(스키마 설계)에 해당. 이후:

- **SP2**: Notion 내보내기 → Obsidian Importer → 속성 매핑 → 재구조화
- **SP3**: 옵시디언 노트 → MDX 변환 스크립트 → Next.js 블로그 연동
- **SP4**: Claude 기반 에이전트 — 주제 추천, 글쓰기 지원, 학습 가이드

각 하위 프로젝트는 별도의 spec → plan → implementation 사이클을 거친다.
