#!/usr/bin/env python3
"""
Phase 7-10 API エンドポイントテストクラス
認証、ウォッチリスト、ポートフォリオ、アラート機能の統合テスト
"""

import requests
import json
import time
from typing import Optional, Dict, Any

class Phase710APITester:
    """Phase 7-10 API統合テストクラス"""

    def __init__(self, base_url: str = "https://miraikakaku-api-465603676610.us-central1.run.app"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.test_username = f"testuser_{int(time.time())}"
        self.test_email = f"test_{int(time.time())}@example.com"
        self.test_password = "SecurePassword123!"

        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }

    def log(self, message: str, level: str = "INFO"):
        """ログ出力"""
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ "
        }.get(level, "")
        print(f"{prefix} {message}")

    def assert_test(self, condition: bool, test_name: str, message: str = ""):
        """テスト結果を記録"""
        if condition:
            self.results["passed"] += 1
            self.log(f"PASS: {test_name}", "SUCCESS")
        else:
            self.results["failed"] += 1
            self.log(f"FAIL: {test_name} - {message}", "ERROR")

        self.results["tests"].append({
            "name": test_name,
            "passed": condition,
            "message": message
        })

    # ==================== Phase 7: 認証テスト ====================

    def test_user_registration(self) -> bool:
        """ユーザー登録テスト"""
        self.log("\n【Phase 7-1】ユーザー登録テスト", "INFO")

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={
                    "username": self.test_username,
                    "email": self.test_email,
                    "password": self.test_password
                },
                timeout=10
            )

            self.assert_test(
                response.status_code == 201,
                "ユーザー登録",
                f"Status: {response.status_code}"
            )

            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("user_id")
                self.log(f"登録成功: user_id={self.user_id}, username={self.test_username}")
                return True

            return False

        except Exception as e:
            self.assert_test(False, "ユーザー登録", str(e))
            return False

    def test_user_login(self) -> bool:
        """ログインテスト"""
        self.log("\n【Phase 7-2】ログインテスト", "INFO")

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                data={
                    "username": self.test_username,
                    "password": self.test_password
                },
                timeout=10
            )

            self.assert_test(
                response.status_code == 200,
                "ログイン",
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.log(f"ログイン成功: token取得完了")
                return True

            return False

        except Exception as e:
            self.assert_test(False, "ログイン", str(e))
            return False

    def test_get_current_user(self) -> bool:
        """現在のユーザー情報取得テスト"""
        self.log("\n【Phase 7-3】ユーザー情報取得テスト", "INFO")

        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )

            self.assert_test(
                response.status_code == 200,
                "ユーザー情報取得",
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"ユーザー情報: {data.get('username')}, {data.get('email')}")
                return True

            return False

        except Exception as e:
            self.assert_test(False, "ユーザー情報取得", str(e))
            return False

    # ==================== Phase 8: ウォッチリストテスト ====================

    def test_add_to_watchlist(self) -> bool:
        """ウォッチリスト追加テスト"""
        self.log("\n【Phase 8-1】ウォッチリスト追加テスト", "INFO")

        test_symbols = ["AAPL", "7203.T", "MSFT"]

        for symbol in test_symbols:
            try:
                response = requests.post(
                    f"{self.base_url}/api/watchlist",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json={
                        "symbol": symbol,
                        "notes": f"Test note for {symbol}"
                    },
                    timeout=10
                )

                self.assert_test(
                    response.status_code in [200, 201],
                    f"ウォッチリスト追加 ({symbol})",
                    f"Status: {response.status_code}"
                )

            except Exception as e:
                self.assert_test(False, f"ウォッチリスト追加 ({symbol})", str(e))

        return True

    def test_get_watchlist(self) -> bool:
        """ウォッチリスト取得テスト"""
        self.log("\n【Phase 8-2】ウォッチリスト取得テスト", "INFO")

        try:
            response = requests.get(
                f"{self.base_url}/api/watchlist",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )

            self.assert_test(
                response.status_code == 200,
                "ウォッチリスト取得",
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"ウォッチリスト件数: {len(data)}")
                return True

            return False

        except Exception as e:
            self.assert_test(False, "ウォッチリスト取得", str(e))
            return False

    # ==================== Phase 9: ポートフォリオテスト ====================

    def test_add_to_portfolio(self) -> bool:
        """ポートフォリオ追加テスト"""
        self.log("\n【Phase 9-1】ポートフォリオ追加テスト", "INFO")

        test_holdings = [
            {"symbol": "AAPL", "quantity": 10, "purchase_price": 150.50, "purchase_date": "2024-01-15"},
            {"symbol": "7203.T", "quantity": 100, "purchase_price": 2500, "purchase_date": "2024-02-20"}
        ]

        for holding in test_holdings:
            try:
                response = requests.post(
                    f"{self.base_url}/api/portfolio",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=holding,
                    timeout=10
                )

                self.assert_test(
                    response.status_code in [200, 201],
                    f"ポートフォリオ追加 ({holding['symbol']})",
                    f"Status: {response.status_code}"
                )

            except Exception as e:
                self.assert_test(False, f"ポートフォリオ追加 ({holding['symbol']})", str(e))

        return True

    def test_get_portfolio(self) -> bool:
        """ポートフォリオ取得テスト"""
        self.log("\n【Phase 9-2】ポートフォリオ取得テスト", "INFO")

        try:
            response = requests.get(
                f"{self.base_url}/api/portfolio",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )

            self.assert_test(
                response.status_code == 200,
                "ポートフォリオ取得",
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"ポートフォリオ件数: {len(data)}")
                return True

            return False

        except Exception as e:
            self.assert_test(False, "ポートフォリオ取得", str(e))
            return False

    def test_get_portfolio_summary(self) -> bool:
        """ポートフォリオサマリー取得テスト"""
        self.log("\n【Phase 9-3】ポートフォリオサマリー取得テスト", "INFO")

        try:
            response = requests.get(
                f"{self.base_url}/api/portfolio/summary",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )

            self.assert_test(
                response.status_code == 200,
                "ポートフォリオサマリー取得",
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"総資産価値: {data.get('total_value', 0)}, 損益: {data.get('unrealized_gain', 0)}")
                return True

            return False

        except Exception as e:
            self.assert_test(False, "ポートフォリオサマリー取得", str(e))
            return False

    # ==================== Phase 10: アラートテスト ====================

    def test_create_alert(self) -> bool:
        """アラート作成テスト"""
        self.log("\n【Phase 10-1】アラート作成テスト", "INFO")

        test_alerts = [
            {"symbol": "AAPL", "alert_type": "price_above", "target_price": 200},
            {"symbol": "7203.T", "alert_type": "price_below", "target_price": 2000}
        ]

        for alert in test_alerts:
            try:
                response = requests.post(
                    f"{self.base_url}/api/alerts",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=alert,
                    timeout=10
                )

                self.assert_test(
                    response.status_code in [200, 201],
                    f"アラート作成 ({alert['symbol']} - {alert['alert_type']})",
                    f"Status: {response.status_code}"
                )

            except Exception as e:
                self.assert_test(False, f"アラート作成 ({alert['symbol']})", str(e))

        return True

    def test_get_alerts(self) -> bool:
        """アラート一覧取得テスト"""
        self.log("\n【Phase 10-2】アラート一覧取得テスト", "INFO")

        try:
            response = requests.get(
                f"{self.base_url}/api/alerts",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )

            self.assert_test(
                response.status_code == 200,
                "アラート一覧取得",
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                self.log(f"アラート件数: {len(data)}")
                return True

            return False

        except Exception as e:
            self.assert_test(False, "アラート一覧取得", str(e))
            return False

    # ==================== テスト実行 ====================

    def run_all_tests(self):
        """全テストを実行"""
        self.log("\n" + "="*60, "INFO")
        self.log("Phase 7-10 API エンドポイント統合テスト開始", "INFO")
        self.log("="*60, "INFO")

        # Phase 7: 認証テスト
        if not self.test_user_registration():
            self.log("ユーザー登録に失敗したため、テストを中断します", "ERROR")
            return

        if not self.test_user_login():
            self.log("ログインに失敗したため、テストを中断します", "ERROR")
            return

        self.test_get_current_user()

        # Phase 8: ウォッチリストテスト
        self.test_add_to_watchlist()
        self.test_get_watchlist()

        # Phase 9: ポートフォリオテスト
        self.test_add_to_portfolio()
        self.test_get_portfolio()
        self.test_get_portfolio_summary()

        # Phase 10: アラートテスト
        self.test_create_alert()
        self.test_get_alerts()

        # 結果サマリー
        self.print_summary()

    def print_summary(self):
        """テスト結果サマリーを表示"""
        self.log("\n" + "="*60, "INFO")
        self.log("テスト結果サマリー", "INFO")
        self.log("="*60, "INFO")

        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0

        self.log(f"合計テスト数: {total}")
        self.log(f"成功: {self.results['passed']} ({pass_rate:.1f}%)", "SUCCESS")
        self.log(f"失敗: {self.results['failed']}", "ERROR" if self.results["failed"] > 0 else "INFO")

        if self.results["failed"] > 0:
            self.log("\n失敗したテスト:", "ERROR")
            for test in self.results["tests"]:
                if not test["passed"]:
                    self.log(f"  - {test['name']}: {test['message']}", "ERROR")

        self.log("\n" + "="*60, "INFO")

def main():
    """メイン関数"""
    tester = Phase710APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
