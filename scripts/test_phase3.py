#!/usr/bin/env python3
"""
Phase 3機能のテストスクリプト
"""
import requests
import json
import base64
from io import BytesIO

BASE_URL = "http://localhost:8000"

def test_login():
    """ログインテスト"""
    print("\n=== ログインテスト ===")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    print(f"ステータス: {response.status_code}")
    if response.status_code == 200:
        print("✅ ログイン成功")
        return response.cookies
    else:
        print(f"❌ ログイン失敗: {response.text}")
        return None

def test_dashboard_stats(cookies):
    """ダッシュボード統計APIテスト"""
    print("\n=== ダッシュボード統計APIテスト ===")
    response = requests.get(f"{BASE_URL}/api/dashboard/stats", cookies=cookies)
    print(f"ステータス: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ ダッシュボード統計取得成功")
        print(f"  - 総利用者数: {data.get('total_users', 0)}")
        print(f"  - 実施中の計画数: {data.get('active_plans', 0)}")
        print(f"  - 承認待ち計画数: {data.get('pending_approvals', 0)}")
        print(f"  - 今月のモニタリング予定: {data.get('upcoming_monitorings', 0)}")
        print(f"  - 年齢層別利用者数: {data.get('users_by_age_group', {})}")
        return True
    else:
        print(f"❌ 失敗: {response.text}")
        return False

def test_dashboard_alerts(cookies):
    """ダッシュボードアラートAPIテスト"""
    print("\n=== ダッシュボードアラートAPIテスト ===")
    response = requests.get(f"{BASE_URL}/api/dashboard/alerts", cookies=cookies)
    print(f"ステータス: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ アラート情報取得成功")
        print(f"  - 総アラート数: {data.get('total_alerts', 0)}")
        print(f"  - 計画更新期限が近い: {len(data.get('plan_expiring_soon', []))}件")
        print(f"  - モニタリング期限超過: {len(data.get('monitoring_overdue', []))}件")
        print(f"  - 手帳更新期限が近い: {len(data.get('notebook_expiring', []))}件")
        return True
    else:
        print(f"❌ 失敗: {response.text}")
        return False

def test_users_list(cookies):
    """利用者一覧API（高度な検索）テスト"""
    print("\n=== 利用者一覧API（高度な検索）テスト ===")

    # 通常の一覧取得
    response = requests.get(f"{BASE_URL}/api/users", cookies=cookies)
    print(f"ステータス: {response.status_code}")

    if response.status_code == 200:
        users = response.json()
        print(f"✅ 利用者一覧取得成功: {len(users)}件")

        # 検索テスト（名前での検索）
        if len(users) > 0:
            first_user_name = users[0].get('name', '')
            response = requests.get(
                f"{BASE_URL}/api/users",
                params={"search": first_user_name[:2]},
                cookies=cookies
            )
            if response.status_code == 200:
                search_results = response.json()
                print(f"✅ 名前検索成功: {len(search_results)}件")
            else:
                print(f"❌ 検索失敗: {response.text}")
        return True
    else:
        print(f"❌ 失敗: {response.text}")
        return False

def test_network_api(cookies):
    """ネットワーク図APIテスト"""
    print("\n=== ネットワーク図APIテスト ===")

    # まず利用者IDを取得
    response = requests.get(f"{BASE_URL}/api/users", cookies=cookies)
    if response.status_code != 200 or not response.json():
        print("❌ テスト用利用者が見つかりません")
        return False

    user_id = response.json()[0]['id']
    print(f"テスト対象利用者ID: {user_id}")

    # ネットワークデータ取得
    response = requests.get(
        f"{BASE_URL}/api/network/users/{user_id}/network",
        cookies=cookies
    )
    print(f"ステータス: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ ネットワークデータ取得成功")
        print(f"  - ノード数: {len(data.get('nodes', []))}")
        print(f"  - エッジ数: {len(data.get('edges', []))}")
        print(f"  - 利用者名: {data.get('user_name', '')}")
        return user_id
    else:
        print(f"❌ 失敗: {response.text}")
        return None

def test_network_pdf(cookies, user_id):
    """ネットワーク図PDF出力APIテスト"""
    print("\n=== ネットワーク図PDF出力APIテスト ===")

    if not user_id:
        print("❌ テスト用利用者IDが不正です")
        return False

    try:
        # ダミーのPNG画像データを作成（1x1ピクセルの白い画像）
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Base64エンコード
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        image_data = f"data:image/png;base64,{img_base64}"

        # PDF生成APIを呼び出し
        response = requests.post(
            f"{BASE_URL}/api/network/users/{user_id}/network/pdf",
            json={"image_data": image_data},
            cookies=cookies
        )
        print(f"ステータス: {response.status_code}")

        if response.status_code == 200:
            print("✅ ネットワーク図PDF生成成功")
            print(f"  - Content-Type: {response.headers.get('Content-Type')}")
            print(f"  - PDFサイズ: {len(response.content)} bytes")

            # PDFを保存してテスト
            with open('/tmp/test_network.pdf', 'wb') as f:
                f.write(response.content)
            print("  - PDFファイル保存: /tmp/test_network.pdf")
            return True
        else:
            print(f"❌ 失敗: {response.text}")
            return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=" * 60)
    print("Phase 3 機能テスト開始")
    print("=" * 60)

    # ログイン
    cookies = test_login()
    if not cookies:
        print("\n❌ ログインに失敗したため、テストを中止します")
        return

    # テスト実行
    results = {
        "ダッシュボード統計": test_dashboard_stats(cookies),
        "ダッシュボードアラート": test_dashboard_alerts(cookies),
        "利用者一覧・検索": test_users_list(cookies),
    }

    user_id = test_network_api(cookies)
    if user_id:
        results["ネットワーク図API"] = True
        results["ネットワーク図PDF出力"] = test_network_pdf(cookies, user_id)
    else:
        results["ネットワーク図API"] = False
        results["ネットワーク図PDF出力"] = False

    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    for test_name, result in results.items():
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{test_name}: {status}")

    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)
    print(f"\n合計: {success_count}/{total_count} テスト成功")
    print("=" * 60)

if __name__ == "__main__":
    main()
