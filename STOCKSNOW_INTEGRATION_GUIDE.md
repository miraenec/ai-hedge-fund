# StockSnow Integration Guide
# miraenec/stocksnow 저장소에 통합하기

이 가이드는 ai-hedge-fund에서 개발된 StockSnow 기능을 miraenec/stocksnow 저장소에 통합하는 방법입니다.

## 📁 파일 구조

```
miraenec/stocksnow/
├── src/stocksnow/                    # 백엔드 Python 모듈
│   ├── __init__.py
│   ├── models.py
│   ├── monitor.py
│   ├── watchlist.py
│   ├── alerts.py
│   ├── streaming.py
│   ├── technical.py
│   ├── cli.py
│   ├── api.py
│   └── README.md
│
├── app/frontend/src/
│   ├── components/
│   │   ├── stocksnow/              # 새로 추가
│   │   │   ├── stock-monitor.tsx
│   │   │   ├── live-quotes-table.tsx
│   │   │   ├── technical-indicators-table.tsx
│   │   │   ├── watchlist-manager.tsx
│   │   │   └── alerts-manager.tsx
│   │   ├── ui/
│   │   │   ├── label.tsx           # 새로 추가 (없으면)
│   │   │   └── select.tsx          # 새로 추가 (없으면)
│   │   ├── Layout.tsx              # 수정
│   │   └── layout/
│   │       └── top-bar.tsx         # 수정
│   │
│   └── services/
│       ├── stocksnow-api.ts        # 새로 추가
│       └── tab-service.ts          # 수정
│
├── tests/
│   └── test_stocksnow.py           # 새로 추가
│
├── examples/
│   └── stocksnow_demo.py           # 새로 추가
│
├── pyproject.toml                   # 수정 (stocksnow CLI 추가)
│
└── 문서/
    ├── STOCKSNOW_FEATURE.md
    ├── STOCKSNOW_SUMMARY.md
    └── STOCKSNOW_WEB_UI.md
```

## 🚀 통합 단계

### 1단계: 백엔드 파일 복사

```bash
# ai-hedge-fund 저장소에서
cd /path/to/ai-hedge-fund

# stocksnow 저장소로 복사
cp -r src/stocksnow /path/to/stocksnow/src/
cp tests/test_stocksnow.py /path/to/stocksnow/tests/
cp examples/stocksnow_demo.py /path/to/stocksnow/examples/
```

### 2단계: 프론트엔드 파일 복사

```bash
# 컴포넌트
cp -r app/frontend/src/components/stocksnow /path/to/stocksnow/app/frontend/src/components/

# UI 컴포넌트 (없으면 복사)
cp app/frontend/src/components/ui/label.tsx /path/to/stocksnow/app/frontend/src/components/ui/
cp app/frontend/src/components/ui/select.tsx /path/to/stocksnow/app/frontend/src/components/ui/

# API 서비스
cp app/frontend/src/services/stocksnow-api.ts /path/to/stocksnow/app/frontend/src/services/
```

### 3단계: 기존 파일 수정

#### 3-1. `pyproject.toml` 수정

```toml
[tool.poetry.scripts]
# 기존 스크립트들...
stocksnow = "src.stocksnow.cli:main"  # 이 라인 추가
```

#### 3-2. `app/frontend/src/services/tab-service.ts` 수정

```typescript
// 1. import 추가
import { StockMonitor } from '@/components/stocksnow/stock-monitor';

// 2. TabData type 수정
export interface TabData {
  type: 'flow' | 'settings' | 'stocksnow';  // 'stocksnow' 추가
  title: string;
  flow?: Flow;
  metadata?: Record<string, any>;
}

// 3. createTabContent에 case 추가
static createTabContent(tabData: TabData): ReactNode {
  switch (tabData.type) {
    // ... 기존 cases
    case 'stocksnow':
      return createElement(StockMonitor);
    default:
      throw new Error(`Unsupported tab type: ${tabData.type}`);
  }
}

// 4. 새 메소드 추가
static createStockSnowTab(): TabData & { content: ReactNode } {
  return {
    type: 'stocksnow',
    title: 'StockSnow',
    content: TabService.createTabContent({ type: 'stocksnow', title: 'StockSnow' }),
  };
}

// 5. restoreTab에 case 추가
static restoreTab(savedTab: TabData): TabData & { content: ReactNode } {
  switch (savedTab.type) {
    // ... 기존 cases
    case 'stocksnow':
      return TabService.createStockSnowTab();
    default:
      throw new Error(`Cannot restore unsupported tab type: ${savedTab.type}`);
  }
}
```

#### 3-3. `app/frontend/src/components/layout/top-bar.tsx` 수정

```typescript
// 1. import 추가
import { Activity, PanelBottom, PanelLeft, PanelRight, Settings } from 'lucide-react';

// 2. interface 수정
interface TopBarProps {
  // ... 기존 props
  onStockSnowClick?: () => void;  // 추가
}

// 3. function 파라미터 추가
export function TopBar({
  // ... 기존 props
  onStockSnowClick,
}: TopBarProps) {

// 4. Settings 버튼 전에 StockSnow 버튼 추가
{onStockSnowClick && (
  <Button
    variant="ghost"
    size="sm"
    onClick={onStockSnowClick}
    className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground hover:bg-ramp-grey-700 transition-colors"
    aria-label="Open StockSnow"
    title="Open StockSnow Monitor"
  >
    <Activity size={16} />
  </Button>
)}
```

#### 3-4. `app/frontend/src/components/Layout.tsx` 수정

```typescript
// 1. handleStockSnowClick 함수 추가 (handleSettingsClick 아래)
const handleStockSnowClick = () => {
  const tabData = TabService.createStockSnowTab();
  openTab(tabData);
};

// 2. TopBar에 prop 추가
<TopBar
  // ... 기존 props
  onStockSnowClick={handleStockSnowClick}  // 추가
/>
```

### 4단계: 문서 복사

```bash
cp STOCKSNOW_FEATURE.md /path/to/stocksnow/
cp STOCKSNOW_SUMMARY.md /path/to/stocksnow/
cp STOCKSNOW_WEB_UI.md /path/to/stocksnow/
```

### 5단계: 의존성 설치 및 빌드

```bash
cd /path/to/stocksnow

# Python 의존성 (이미 있을 수 있음)
poetry install

# 프론트엔드 의존성 (필요시)
cd app/frontend
npm install  # 또는 yarn install
```

### 6단계: Git 커밋 및 푸시

```bash
git add .
git commit -m "feat: Add StockSnow real-time monitoring system

- Real-time stock quotes and monitoring
- Watchlist management
- Price alerts (above/below/percentage/volume)
- Technical analysis (RSI, MACD, SMA, Bollinger Bands)
- Web UI integration with Activity icon
- CLI and REST API interfaces
"
git push origin main
```

### 7단계: Vercel 자동 배포

Vercel이 GitHub와 연결되어 있다면 자동으로 배포됩니다.

## ✅ 검증

### 백엔드 테스트
```bash
# CLI 실행
poetry run stocksnow

# API 서버 실행
poetry run python -m src.stocksnow.api

# 테스트 실행
poetry run pytest tests/test_stocksnow.py
```

### 프론트엔드 테스트
1. 웹 앱 실행
2. 상단 바에서 Activity 아이콘 (📊) 클릭
3. StockSnow 탭이 열리는지 확인

## 🔧 문제 해결

### API 연결 오류
- `FINANCIAL_DATASETS_API_KEY` 환경변수 설정 확인
- API 서버가 http://localhost:8000에서 실행 중인지 확인

### UI 컴포넌트 오류
- `label.tsx`, `select.tsx` 파일이 있는지 확인
- Radix UI 의존성 설치 확인: `@radix-ui/react-label`, `@radix-ui/react-select`

### 빌드 오류
- TypeScript 오류 확인
- import 경로 확인 (@/ alias 설정)

## 📊 완료 후 확인사항

- [ ] 백엔드 API 실행됨
- [ ] CLI 대시보드 실행됨
- [ ] 웹 UI에 Activity 아이콘 표시됨
- [ ] Activity 클릭 시 StockSnow 탭 열림
- [ ] Live Quotes 탭 작동
- [ ] Technical Analysis 탭 작동
- [ ] Watchlists 탭 작동
- [ ] Alerts 탭 작동
- [ ] Vercel 배포 성공
- [ ] https://stocksnowball.vercel.app에서 확인됨

## 📝 주요 변경사항

### 새로 추가된 파일 (총 17개)
- Python 백엔드: 9개 파일
- React 프론트엔드: 5개 컴포넌트
- API 서비스: 1개
- UI 컴포넌트: 2개
- 테스트: 1개
- 데모: 1개
- 문서: 3개

### 수정된 파일 (총 4개)
- pyproject.toml
- tab-service.ts
- top-bar.tsx
- Layout.tsx

## 🎯 기능 요약

1. **실시간 모니터링** - 5초마다 자동 업데이트
2. **관심종목** - 여러 리스트 생성 및 관리
3. **가격 알림** - 4가지 타입 (상한/하한/변동률/거래량)
4. **기술적 분석** - 11가지 지표
5. **웹 UI** - 4개 탭, 반응형 디자인
6. **CLI** - Rich 터미널 대시보드
7. **REST API** - FastAPI 기반

## 📞 지원

문제가 발생하면:
1. STOCKSNOW_WEB_UI.md 트러블슈팅 섹션 참조
2. GitHub Issues 생성
3. 로그 확인: API 서버 콘솔 출력

---

**통합 완료 후**: https://stocksnowball.vercel.app에서 Activity 아이콘을 확인하세요!
