# Paper Digest

매일 아침, 내 관심사에 맞는 최신 논문을 알기 쉽게 정리해서 받아보세요.

## 이게 뭔가요?

Paper Digest는 arXiv에서 새로 나온 논문들을 자동으로 찾아서,
Claude AI가 읽기 쉽게 설명해주는 도구예요.

**받는 것:**
- 매일 2편의 논문 요약 (내 관심사에 맞춰 자동 선택)
- 읽기 쉬운 구어체로 작성된 설명
- 웹 브라우저에서 보기 편한 HTML 파일

**장점:**
- Claude API 키 필요 없음 (Claude CLI 구독만 있으면 됨)
- 이미 읽은 논문은 자동으로 제외
- 매일 아침 자동 실행 가능 (원하는 시간 설정)
- 복잡한 설정 없음

## 설치 방법

### 1. 필요한 프로그램 설치

**Python 3.10 이상**
- 이미 있는지 확인: 터미널에서 `python3 --version` 실행
- 없으면 https://www.python.org/downloads/ 에서 다운로드

**uv (Python 패키지 관리자)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Claude CLI**
- https://docs.anthropic.com/en/docs/cli 에서 설치
- Claude Pro 또는 Max 구독 필요

### 2. Paper Digest 설치

```bash
# 이 저장소를 다운로드
git clone https://github.com/Inseop-dable/paper-digest.git
cd paper-digest

# 설치 실행 (키워드 입력 필요)
./install
```

설치 중에 묻는 것들:
- **관심 키워드**: 어떤 논문을 찾을지 (예: large language model, transformer)
- **자동 실행 설정**: 매일 아침 자동으로 실행할지

## 사용 방법

### 기본 실행

```bash
./run
```

실행하면:
1. arXiv에서 최신 논문 검색
2. Claude가 내 관심사에 맞는 논문 2개 선택
3. 읽기 쉽게 설명
4. `digests/` 폴더에 저장

### 검색만 테스트 (요약 안 함)

```bash
./run --dry-run
```

## 자동 실행 설정 (매일 논문 받기)

**이게 뭐죠?**
- 컴퓨터가 매일 지정한 시간에 자동으로 `./run`을 실행해줘요
- 매일 아침 출근해서 보면 새 논문 요약이 쌓여 있겠죠?
- "크론 잡(Cron Job)"이라는 기능을 써서 설정해요

### 설치할 때 같이 설정하기

```bash
./install
```

설치 중에 "자동 실행을 설정하시겠습니까?"라고 물어보면:
1. 선택지 `1`을 누르세요
2. 원하는 시간을 입력하세요 (예: `9` 또는 `9:30`)
3. 끝!

### 나중에 설정하기

```bash
# 매일 오전 9시에 실행
scripts/schedule daily 9:00

# 매일 오후 2시 30분에 실행
scripts/schedule daily 14:30
```

### 현재 설정 확인하기

```bash
scripts/schedule
```

현재 설정된 시간을 보여줍니다.

### 자동 실행 취소하기

```bash
scripts/schedule off
```

이 명령어 한 줄이면 자동 실행이 멈춰요.

**Q: 설정된 시간을 바꾸고 싶어요**
```bash
# 그냥 새로운 시간으로 다시 설정하면 됩니다
scripts/schedule daily 10:00  # 오전 10시로 변경
```

## 설정 변경

`config.yaml` 파일을 텍스트 에디터로 열어서 수정하세요.

### 키워드 변경

```yaml
interests:
  keywords:
    - "large language model"
    - "transformer"
    - "reinforcement learning"
```

### 관심 학회 추가

```yaml
venues:
  conferences:
    - NeurIPS
    - ICML
    - ICLR
```

### 관심 저자 추가

```yaml
authors:
  - "Yann LeCun"
  - "Geoffrey Hinton"
```

### arXiv 카테고리 변경

기본값은 AI/ML 분야예요. 다른 분야를 원하면:

```yaml
interests:
  categories:
    - cs.LG      # Machine Learning
    - cs.AI      # Artificial Intelligence
    - cs.CV      # Computer Vision
```

카테고리 전체 목록: https://arxiv.org/category_taxonomy

**주의:** AI/ML이 아닌 다른 분야(물리, 수학 등)를 원하면
카테고리를 해당 분야로 변경해야 해요.

## 결과 확인

요약된 논문은 `digests/` 폴더에 저장됩니다:
- `digests/2026-01-29.md` - 텍스트 파일
- `digests/2026-01-29.html` - 웹 브라우저로 보기

HTML 파일을 더블클릭하면 브라우저에서 예쁘게 볼 수 있어요.

## 자주 묻는 질문

**Q: Claude API 키가 필요한가요?**
A: 아니요! Claude CLI 구독(Pro/Max)만 있으면 됩니다.

**Q: 매일 몇 개의 논문을 받나요?**
A: 기본값은 2개예요. `config.yaml`에서 변경 가능합니다.

**Q: 논문을 하나도 못 찾았다고 나와요**
A: 검색된 논문이 없거나 Claude가 선택할 논문이 없는 경우예요.
`./run --dry-run`을 실행해서 어떤 논문이 검색되는지 확인해보세요.
키워드가 너무 구체적이면 관련 논문을 찾기 어려울 수 있으니
더 일반적인 키워드로 바꿔보세요.

**Q: 자동 실행이 잘 되고 있는지 어떻게 확인해요?**
A: `scripts/schedule` 명령어를 입력하면 현재 설정을 볼 수 있어요.
그리고 `digests/` 폴더에 날짜가 최신인 파일이 있는지 확인해보세요.

**Q: 자동 실행을 취소하고 싶어요**
A: `scripts/schedule off`를 실행하세요. 한 줄이면 끝납니다.

**Q: 크론 잡(Cron Job)이 뭔가요?**
A: macOS/Linux에서 "매일 특정 시간에 무언가 실행하기"를 설정하는 기능이에요.
Paper Digest는 이걸 써서 매일 아침 논문을 자동으로 찾아줍니다.

**Q: 자동 실행이 항상 되나요?**
A: 컴퓨터가 켜져 있을 때만 실행돼요. 컴퓨터가 꺼져 있거나
잠들어 있기(sleep) 모드이면 실행되지 않습니다.
화면만 꺼져있는 상태라면 정상 실행됩니다.

**Q: 오늘 이미 실행했는데 또 실행하면 어떻게 되나요?**
A: 이미 처리한 논문은 기록되어 있어서 건너뜁니다. 새로운 논문이 없으면
"모든 논문을 이미 봤다"고 나와요.

## 폴더 구조

```
paper-digest/
├── README.md          # 이 파일
├── config.yaml        # 내 설정
├── install            # 설치 스크립트
├── run                # 실행 스크립트
└── digests/           # 요약 결과 (여기 확인!)
    ├── 2026-01-29.md
    └── 2026-01-29.html
```

숨김 폴더들 (신경 안 써도 됨):
- `.tmp/` - 임시 파일
- `.venv/` - Python 가상환경
- `src/` - 소스 코드
- `scripts/` - 내부 스크립트

## 문제가 생겼어요

**"Claude CLI를 찾을 수 없음"**
- Claude CLI가 설치되어 있나요?
- https://docs.anthropic.com/en/docs/cli 에서 설치

**"config.yaml을 찾을 수 없음"**
- `./install` 을 먼저 실행하세요

**권한 오류가 나요**
```bash
chmod +x install run scripts/schedule
```

## 라이선스

MIT License - 자유롭게 사용하세요!

## 만든 사람

질문이나 문제가 있으면 GitHub Issues에 올려주세요.
