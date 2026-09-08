# StockSnow 웹 UI 사용 가이드

## 🎉 웹 UI에 통합 완료!

StockSnow가 이제 AI Hedge Fund 웹 애플리케이션에 완전히 통합되었습니다!

## 📍 접근 방법

### 1단계: 백엔드 API 서버 시작

터미널에서 StockSnow API 서버를 실행하세요:

```bash
poetry run python -m src.stocksnow.api
```

API 서버가 `http://localhost:8000`에서 실행됩니다.

### 2단계: 웹 애플리케이션 시작

별도의 터미널에서 웹 앱을 실행하세요:

```bash
cd app
./run.sh  # macOS/Linux
# 또는
run.bat   # Windows
```

### 3단계: StockSnow 열기

웹 애플리케이션에서:

1. **상단 바(Top Bar) 우측**에 있는 **Activity 아이콘 (📊)** 클릭
2. 새로운 "StockSnow" 탭이 열립니다
3. 실시간 주식 모니터링 시작!

## 🎨 UI 기능

### 탭 구조

StockSnow는 4개의 탭으로 구성되어 있습니다:

#### 1. 📊 Live Quotes (실시간 시세)
- 모니터링 중인 모든 주식의 실시간 가격
- 가격 변동 (금액 및 퍼센트)
- 거래량, 고가, 저가, 이전 종가
- 10초마다 자동 업데이트
- 색상 코딩: 상승(녹색), 하락(빨간색)

**특징:**
- 자동 새로고침 (10초 간격)
- 대시보드 우측 상단에 "Live" 상태 표시
- 깔끔한 테이블 형식으로 정리

#### 2. 🔧 Technical Analysis (기술적 분석)
- **RSI (Relative Strength Index)**
  - >70: Overbought (과매수) - 빨간색 배지
  - <30: Oversold (과매도) - 녹색 배지
  - 30-70: Neutral (중립) - 회색 배지
- **MACD** (Moving Average Convergence Divergence)
- **이동평균선**: SMA 20, SMA 50
- **지지선/저항선**: 자동 계산

**참고:**
- 기술적 지표는 최소 20개 데이터 포인트 필요
- 데이터가 충분하지 않으면 안내 메시지 표시

#### 3. 📋 Watchlists (관심종목)
관심종목 리스트를 생성하고 관리합니다.

**기능:**
- **New Watchlist 버튼**: 새로운 관심종목 리스트 생성
  - 예: "Tech Stocks", "Blue Chips", "Growth"
  
- **Add Stock 버튼**: 종목 추가
  - 티커 심볼 입력 (예: AAPL, MSFT)
  - 메모 추가 (선택사항)
  - 목표가 설정 (선택사항)

- **종목 카드**:
  - 티커 심볼 표시
  - 메모 및 목표가 확인
  - 추가 날짜 표시
  - 삭제 버튼 (휴지통 아이콘)

- **관심종목 선택**: 드롭다운으로 전환
- **Delete 버튼**: 전체 관심종목 삭제

#### 4. 🔔 Alerts (알림)
가격 알림을 설정하고 관리합니다.

**알림 유형:**

1. **Price Above (상한가)**
   - 주가가 설정한 가격 이상으로 올라갈 때
   - 예: AAPL이 $180 돌파 시

2. **Price Below (하한가)**
   - 주가가 설정한 가격 이하로 내려갈 때
   - 예: MSFT가 $350 하회 시

3. **Percentage Change (변동률)**
   - 가격이 설정한 퍼센트 이상 변동할 때
   - 예: 5% 이상 상승/하락

4. **Volume Spike (거래량 급증)**
   - 거래량이 임계값을 초과할 때

**알림 생성:**
1. "New Alert" 버튼 클릭
2. 티커 심볼 입력
3. 알림 유형 선택
4. 임계값 입력 ($ 또는 %)
5. 커스텀 메시지 입력 (선택사항)
6. "Create Alert" 클릭

**알림 상태:**
- **Active (활성)**: 녹색 배지 - 모니터링 중
- **Triggered (발동됨)**: 주황색 배지 - 조건 충족됨
- **Inactive (비활성)**: 회색 배지

**통계 카드:**
- Active Alerts: 현재 활성화된 알림 수
- Triggered Today: 오늘 발동된 알림 수

### 📈 하단 통계

대시보드 하단에 3개의 통계 카드 표시:
- **Monitored Stocks**: 모니터링 중인 종목 수
- **Watchlists**: 생성된 관심종목 리스트 수
- **Active Alerts**: 활성 알림 수

## 🔄 데이터 흐름

```
StockSnow Backend API (localhost:8000)
         ↓
  웹 UI (React Frontend)
         ↓
  자동 업데이트 (10초/30초)
         ↓
  실시간 대시보드 표시
```

- **Live Quotes**: 10초마다 업데이트
- **Alerts**: 30초마다 체크
- **Watchlists**: 변경 시 즉시 반영
- **Technical Indicators**: 데이터 업데이트 시 재계산

## 🎯 사용 시나리오

### 시나리오 1: 기술주 모니터링

1. **관심종목 생성**
   - Watchlists 탭 → "New Watchlist"
   - 이름: "Tech Giants"

2. **종목 추가**
   - "Add Stock" 클릭
   - AAPL, MSFT, GOOGL, NVDA 추가
   - 각각 메모와 목표가 설정

3. **알림 설정**
   - Alerts 탭 → "New Alert"
   - AAPL - Above $180
   - NVDA - Change 5%

4. **모니터링**
   - Live Quotes 탭에서 실시간 가격 확인
   - Technical Analysis 탭에서 RSI/MACD 확인

### 시나리오 2: 가치주 스윙 트레이딩

1. **관심종목 "Value Plays" 생성**
2. **저평가 종목 추가 (RSI < 30)**
3. **알림 설정:**
   - RSI 30 이하일 때 매수 검토
   - 목표가 도달 시 매도 알림
4. **기술적 분석으로 진입/청산 시점 판단**

### 시나리오 3: 포트폴리오 모니터링

1. **"My Portfolio" 관심종목 생성**
2. **보유 종목 모두 추가**
3. **각 종목에 손절가 알림 설정**
4. **Live Quotes에서 포트폴리오 전체 성과 확인**
5. **Technical Analysis에서 과매수/과매도 확인**

## 🎨 UI 요소

### 아이콘
- **📊 Activity**: StockSnow 열기 (Top Bar)
- **📈 TrendingUp**: Live Quotes
- **🔧 Activity**: Technical Analysis
- **📋 ListPlus**: Watchlists
- **🔔 Bell**: Alerts
- **➕ Plus**: 추가 버튼
- **🗑️ Trash2**: 삭제 버튼
- **⬆️ ArrowUp**: 상승
- **⬇️ ArrowDown**: 하락

### 색상 코딩
- **녹색**: 상승, 지지선, Oversold, Active
- **빨간색**: 하락, 저항선, Overbought
- **회색**: 중립, Inactive
- **주황색**: Triggered
- **파란색**: Change Percent 알림
- **보라색**: Volume Spike 알림

### 상태 표시
- **Live 배지**: 녹색 점 애니메이션 - 실시간 모니터링 중
- **Badge 컴포넌트**: 알림 타입, 상태, RSI 상태 표시
- **Table**: 정렬된 데이터 표시
- **Card**: 섹션 구분

## ⚠️ 주의사항

### API 연결 오류 시

API가 실행되지 않으면 다음과 같은 오류 화면이 표시됩니다:

```
StockSnow API Not Available
Cannot connect to StockSnow API. Please make sure it is running on http://localhost:8000

To start the StockSnow API server, run:
poetry run python -m src.stocksnow.api
```

**해결 방법:**
1. 터미널에서 API 서버 실행
2. "Retry Connection" 버튼 클릭

### 데이터 없음

- **Live Quotes 빈 화면**: 관심종목에 종목 추가 필요
- **Technical Indicators 없음**: 최소 20 데이터 포인트 대기
- **Alerts 없음**: 첫 알림 생성 필요

### 성능

- 많은 종목(50개 이상) 모니터링 시 업데이트 간격 증가 가능
- 브라우저 탭이 백그라운드일 때 업데이트 속도 감소 가능

## 🔧 트러블슈팅

### 문제: StockSnow 버튼이 안 보임
**해결**: 페이지 새로고침 (F5 또는 Cmd+R)

### 문제: 데이터가 업데이트되지 않음
**해결**: 
1. API 서버 실행 확인
2. 브라우저 개발자 도구(F12) → Console 확인
3. 네트워크 탭에서 요청 실패 확인

### 문제: 알림이 작동하지 않음
**해결**:
1. 알림이 Active 상태인지 확인
2. 임계값이 올바른지 확인
3. API 서버 로그 확인

### 문제: Technical Indicators 표시 안 됨
**해결**: 
- 최소 20개 데이터 포인트 필요
- 5초 × 20 = 100초 (약 2분) 대기
- Live Quotes 탭에서 종목이 표시되는지 확인

## 🎓 팁

1. **여러 관심종목 활용**
   - 섹터별, 전략별로 구분
   - 예: "Tech", "Finance", "Energy", "Growth", "Value"

2. **스마트 알림 설정**
   - 지지선/저항선 근처에 알림 설정
   - RSI 극값에 알림 설정
   - 중요 심리적 가격대에 알림

3. **탭 전환 활용**
   - Cmd+1/2/3/4 (macOS) 또는 Ctrl+1/2/3/4 (Windows)로 탭 전환 가능

4. **목표가 활용**
   - 관심종목에 목표가 설정
   - 알림으로 자동화

5. **데이터 축적**
   - 장시간 모니터링으로 더 정확한 기술적 지표
   - 백그라운드에서 계속 실행

## 📱 반응형 디자인

웹 UI는 다양한 화면 크기에 최적화:
- **Desktop**: 전체 기능 사용
- **Tablet**: 탭 레이아웃 조정
- **Mobile**: 세로 스크롤, 간소화된 테이블

## 🔐 보안

- 모든 통신은 localhost (로컬호스트)에서 이루어짐
- 외부 인터넷 연결 없음
- API 키는 백엔드에서만 사용

## 📊 통합 기능

StockSnow는 AI Hedge Fund의 다른 기능과 통합:
- **Portfolio Manager**: 포트폴리오 포지션 모니터링
- **Risk Manager**: 리스크 메트릭 확인
- **Backtester**: 과거 데이터 분석

## 🎉 요약

StockSnow 웹 UI는:
- ✅ 완전 통합된 실시간 대시보드
- ✅ 4개 탭: Quotes, Technicals, Watchlists, Alerts
- ✅ 자동 업데이트 (10초/30초)
- ✅ 직관적인 UI/UX
- ✅ 모바일 반응형
- ✅ 완전한 CRUD 기능
- ✅ 색상 코딩 및 시각적 피드백

**이제 상단 바의 Activity 아이콘을 클릭하여 StockSnow를 시작하세요!** 🚀
