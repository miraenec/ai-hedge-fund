#!/bin/bash
# StockSnow 파일을 miraenec/stocksnow 저장소로 복사하는 스크립트
# 사용법: ./copy-to-stocksnow.sh /path/to/stocksnow

set -e

if [ -z "$1" ]; then
    echo "사용법: $0 <stocksnow-repo-path>"
    echo "예: $0 /path/to/stocksnow"
    exit 1
fi

TARGET_DIR="$1"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 StockSnow 파일을 복사합니다..."
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo ""

# 디렉토리 존재 확인
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ 오류: 대상 디렉토리가 존재하지 않습니다: $TARGET_DIR"
    exit 1
fi

# 백엔드 파일 복사
echo "📦 백엔드 파일 복사 중..."
mkdir -p "$TARGET_DIR/src"
cp -r "$SOURCE_DIR/src/stocksnow" "$TARGET_DIR/src/"
echo "  ✓ src/stocksnow/"

# 테스트 파일 복사
echo "🧪 테스트 파일 복사 중..."
mkdir -p "$TARGET_DIR/tests"
cp "$SOURCE_DIR/tests/test_stocksnow.py" "$TARGET_DIR/tests/"
echo "  ✓ tests/test_stocksnow.py"

# 예제 파일 복사
echo "📝 예제 파일 복사 중..."
mkdir -p "$TARGET_DIR/examples"
cp "$SOURCE_DIR/examples/stocksnow_demo.py" "$TARGET_DIR/examples/"
echo "  ✓ examples/stocksnow_demo.py"

# 프론트엔드 파일 복사
if [ -d "$TARGET_DIR/app/frontend" ]; then
    echo "🎨 프론트엔드 파일 복사 중..."
    
    # 컴포넌트
    mkdir -p "$TARGET_DIR/app/frontend/src/components"
    cp -r "$SOURCE_DIR/app/frontend/src/components/stocksnow" "$TARGET_DIR/app/frontend/src/components/"
    echo "  ✓ app/frontend/src/components/stocksnow/"
    
    # UI 컴포넌트
    mkdir -p "$TARGET_DIR/app/frontend/src/components/ui"
    cp "$SOURCE_DIR/app/frontend/src/components/ui/label.tsx" "$TARGET_DIR/app/frontend/src/components/ui/" 2>/dev/null || echo "  ℹ  label.tsx already exists"
    cp "$SOURCE_DIR/app/frontend/src/components/ui/select.tsx" "$TARGET_DIR/app/frontend/src/components/ui/" 2>/dev/null || echo "  ℹ  select.tsx already exists"
    
    # API 서비스
    mkdir -p "$TARGET_DIR/app/frontend/src/services"
    cp "$SOURCE_DIR/app/frontend/src/services/stocksnow-api.ts" "$TARGET_DIR/app/frontend/src/services/"
    echo "  ✓ app/frontend/src/services/stocksnow-api.ts"
else
    echo "⚠️  프론트엔드 디렉토리가 없습니다. 백엔드만 복사되었습니다."
fi

# 문서 복사
echo "📚 문서 파일 복사 중..."
cp "$SOURCE_DIR/STOCKSNOW_FEATURE.md" "$TARGET_DIR/"
cp "$SOURCE_DIR/STOCKSNOW_SUMMARY.md" "$TARGET_DIR/"
cp "$SOURCE_DIR/STOCKSNOW_WEB_UI.md" "$TARGET_DIR/"
cp "$SOURCE_DIR/STOCKSNOW_INTEGRATION_GUIDE.md" "$TARGET_DIR/"
echo "  ✓ 문서 4개 파일"

echo ""
echo "✅ 파일 복사 완료!"
echo ""
echo "📝 다음 단계:"
echo "1. 수동으로 파일 수정이 필요합니다:"
echo "   - pyproject.toml"
echo "   - app/frontend/src/services/tab-service.ts"
echo "   - app/frontend/src/components/layout/top-bar.tsx"
echo "   - app/frontend/src/components/Layout.tsx"
echo ""
echo "2. STOCKSNOW_INTEGRATION_GUIDE.md를 참조하세요"
echo ""
echo "3. Git 커밋:"
echo "   cd $TARGET_DIR"
echo "   git add ."
echo "   git commit -m 'feat: Add StockSnow monitoring system'"
echo "   git push origin main"
echo ""
echo "🎉 완료!"
