#!/bin/bash
# MiraiKakaku 統一依存関係管理スクリプト

set -e

echo "🔧 MiraiKakaku 依存関係管理システム"
echo "=================================="

# 色付きログ出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# プロジェクトルートの確認
if [ ! -f "package.json" ] || [ ! -f "requirements.txt" ]; then
    log_error "プロジェクトルートで実行してください"
    exit 1
fi

# 操作の選択
case "${1:-help}" in
    "audit")
        log_info "セキュリティ監査を実行中..."

        # Node.js セキュリティ監査
        log_info "フロントエンドのセキュリティ監査..."
        cd miraikakakufront
        npm audit
        cd ..

        # Python セキュリティ監査 (safety が利用可能な場合)
        if command -v safety &> /dev/null; then
            log_info "Python依存関係のセキュリティ監査..."
            safety check -r requirements.txt
        else
            log_warning "safety がインストールされていません。'pip install safety' でインストールしてください"
        fi

        log_success "セキュリティ監査完了"
        ;;

    "update")
        log_info "依存関係の更新中..."

        # Node.js 依存関係更新
        log_info "フロントエンド依存関係を更新中..."
        cd miraikakakufront
        npm update
        npm audit fix 2>/dev/null || log_warning "一部の脆弱性は手動修正が必要です"
        cd ..

        # Python 依存関係更新チェック
        if command -v pip-review &> /dev/null; then
            log_info "Python依存関係の更新可能パッケージをチェック中..."
            pip-review --local --interactive
        else
            log_warning "pip-review がインストールされていません。'pip install pip-review' でインストールしてください"
        fi

        log_success "依存関係の更新完了"
        ;;

    "check")
        log_info "依存関係の状態をチェック中..."

        # Node.js 依存関係チェック
        log_info "フロントエンドの古いパッケージをチェック..."
        cd miraikakakufront
        npm outdated || log_info "古いパッケージが見つかりました（上記参照）"
        cd ..

        # Python 依存関係チェック
        if command -v pip list &> /dev/null; then
            log_info "Python環境の依存関係..."
            pip list --outdated | head -10
        fi

        # ファイルサイズチェック
        log_info "Node modules サイズ..."
        if [ -d "miraikakakufront/node_modules" ]; then
            du -sh miraikakakufront/node_modules
        else
            log_warning "node_modules が見つかりません"
        fi

        log_success "依存関係チェック完了"
        ;;

    "install")
        log_info "すべての依存関係をインストール中..."

        # ルート依存関係
        log_info "ルートワークスペースの依存関係..."
        npm install

        # フロントエンド依存関係
        log_info "フロントエンド依存関係..."
        cd miraikakakufront
        npm install
        cd ..

        # Python依存関係（仮想環境の確認）
        if [ -n "$VIRTUAL_ENV" ]; then
            log_info "Python依存関係をインストール中 (仮想環境: $VIRTUAL_ENV)"
            pip install -r requirements.txt
        else
            log_warning "仮想環境が有効化されていません。Python依存関係は手動でインストールしてください"
            log_warning "推奨: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        fi

        log_success "依存関係のインストール完了"
        ;;

    "clean")
        log_info "依存関係をクリーンアップ中..."

        # Node.js キャッシュクリア
        log_info "npmキャッシュをクリア..."
        npm cache clean --force

        # node_modules削除
        if [ -d "miraikakakufront/node_modules" ]; then
            log_info "node_modulesを削除..."
            rm -rf miraikakakufront/node_modules
        fi

        if [ -d "node_modules" ]; then
            rm -rf node_modules
        fi

        # Pythonキャッシュクリア
        log_info "Pythonキャッシュをクリア..."
        find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true

        log_success "クリーンアップ完了"
        ;;

    "setup")
        log_info "開発環境をセットアップ中..."

        # 必要なディレクトリ作成
        mkdir -p scripts logs

        # 依存関係インストール
        $0 install

        # 開発環境の確認
        log_info "開発環境を確認中..."
        echo "Node.js: $(node --version)"
        echo "npm: $(npm --version)"
        if command -v python3 &> /dev/null; then
            echo "Python: $(python3 --version)"
        fi

        log_success "開発環境のセットアップ完了"
        ;;

    "help"|*)
        echo "使用方法: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  audit     - セキュリティ脆弱性の監査"
        echo "  update    - 依存関係の更新"
        echo "  check     - 依存関係の状態確認"
        echo "  install   - すべての依存関係をインストール"
        echo "  clean     - 依存関係とキャッシュをクリーンアップ"
        echo "  setup     - 開発環境の初期セットアップ"
        echo "  help      - このヘルプを表示"
        echo ""
        echo "例:"
        echo "  $0 audit          # セキュリティ監査"
        echo "  $0 update         # 依存関係の更新"
        echo "  $0 clean install  # クリーンインストール"
        ;;
esac

echo ""
log_info "操作完了: $(date)"
echo "=================================="