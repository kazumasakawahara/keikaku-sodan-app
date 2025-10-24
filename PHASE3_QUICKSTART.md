# Phase 3 クイックスタートガイド

## 起動手順

### 1. サーバー起動

```bash
cd /Users/k-kawahara/Ai-Workspace/keikaku-sodan-app

# 仮想環境を有効化
source .venv/bin/activate

# サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. ブラウザでアクセス

サーバー起動後、以下のURLにアクセスしてください:

**ダッシュボード (メイン画面)**
```
http://localhost:8000/dashboard
```

---

## 機能別アクセス方法

### 📊 ダッシュボード

**URL**: `http://localhost:8000/dashboard`

**確認項目**:
- [ ] 統計カード (利用者数、計画数、モニタリング数、アラート数) が表示される
- [ ] 4つのグラフ (円グラフ、棒グラフ、折れ線グラフ、ドーナツグラフ) が表示される
- [ ] アラート一覧が表示される (データがある場合)
- [ ] 最近の相談記録が表示される
- [ ] クイックアクションボタンが機能する

**スクリーンショット**: ダッシュボード全体が見えるように

---

### 🔍 高度な検索機能

**URL**: `http://localhost:8000/users`

**確認項目**:
1. **簡易検索**:
   - [ ] 検索ボックスに氏名またはカナを入力して検索できる
   - [ ] 検索結果がテーブルに表示される

2. **詳細検索**:
   - [ ] 「詳細検索」ボタンをクリックすると詳細フォームが展開される
   - [ ] 複数条件 (氏名、カナ、性別、年齢、障害支援区分、後見人) で検索できる
   - [ ] 「検索実行」で結果が表示される
   - [ ] 「条件クリア」で検索条件がリセットされる

3. **ソート機能**:
   - [ ] テーブルヘッダー (ID、氏名、年齢) をクリックすると昇順/降順が切り替わる
   - [ ] ソートアイコンが上下矢印で表示される

4. **ページネーション**:
   - [ ] 「前へ」「次へ」ボタンでページ移動できる
   - [ ] 現在のページ番号が表示される

---

### 🕸️ ネットワーク図

**URL**: `http://localhost:8000/users/{user_id}/network`

**アクセス方法**:
1. 利用者一覧から任意の利用者の「詳細」ボタンをクリック
2. 利用者詳細画面の「ネットワーク図を表示」ボタンをクリック

**確認項目**:
- [ ] D3.jsグラフが表示される
- [ ] 利用者ノード (青色) が中央に配置される
- [ ] 関係機関ノードが周囲に配置される:
  - 通所先・サービス (水色)
  - 医療機関 (緑)
  - 後見人 (オレンジ)
  - 担当スタッフ (紫)
  - その他 (グレー)

**インタラクション**:
- [ ] ノードをドラッグして移動できる
- [ ] ノードにホバーすると詳細情報がツールチップで表示される
- [ ] マウスホイールでズームイン/ズームアウトできる
- [ ] ドラッグで画面全体を移動できる

**エクスポート**:
- [ ] 「PNG出力」ボタンでPNGファイルがダウンロードされる
- [ ] 「SVG出力」ボタンでSVGファイルがダウンロードされる

---

## API動作確認

### ダッシュボード統計API

```bash
curl http://localhost:8000/api/dashboard/stats | jq
```

**期待される出力**:
```json
{
  "total_users": 5,
  "active_plans": 4,
  "pending_approvals": 0,
  "upcoming_monitorings": 2,
  "consultation_by_type": {
    "来所": 10,
    "訪問": 5,
    "電話": 3
  },
  "plan_status": {
    "実施中": 4,
    "作成中": 1
  },
  "users_by_age_group": {
    "0-17": 0,
    "18-39": 2,
    "40-64": 2,
    "65+": 1,
    "不明": 0
  },
  "monthly_consultations": [...]
}
```

### ダッシュボードアラートAPI

```bash
curl http://localhost:8000/api/dashboard/alerts | jq
```

**期待される出力**:
```json
{
  "plan_expiring_soon": [...],
  "monitoring_overdue": [...],
  "notebook_expiring": [...],
  "total_alerts": 3
}
```

### ネットワークデータAPI

```bash
curl http://localhost:8000/api/network/users/1/network | jq
```

**期待される出力**:
```json
{
  "nodes": [
    {
      "id": "user_1",
      "label": "田中太郎",
      "type": "user",
      "data": {...}
    },
    {
      "id": "org_1",
      "label": "ワークセンター北九州",
      "type": "service",
      "data": {...}
    }
  ],
  "edges": [
    {
      "from": "user_1",
      "to": "org_1",
      "relationship": "通所先",
      "frequency": "週5日"
    }
  ],
  "user_id": 1,
  "user_name": "田中太郎"
}
```

### 高度な検索API

```bash
# 年齢範囲で検索
curl "http://localhost:8000/api/users?min_age=20&max_age=40" | jq

# 障害支援区分で検索
curl "http://localhost:8000/api/users?disability_support_level=3" | jq

# 後見人ありで検索
curl "http://localhost:8000/api/users?has_guardian=true" | jq

# 複数条件 + ソート
curl "http://localhost:8000/api/users?min_age=30&gender=男性&sort_by=name&order=asc" | jq
```

---

## トラブルシューティング

### グラフが表示されない

**原因**: Chart.jsまたはD3.jsのCDNが読み込まれていない

**解決策**:
1. ブラウザの開発者ツール (F12) を開く
2. Consoleタブでエラーを確認
3. ネットワークタブでCDNの読み込み状況を確認

### ネットワーク図が空

**原因**: 利用者に関係機関が登録されていない

**解決策**:
1. テストデータを投入する: `python scripts/seed_data.py`
2. または手動で関係機関を登録する

### 検索結果が表示されない

**原因**: データベースに利用者データがない

**解決策**:
1. テストデータを投入する: `python scripts/seed_data.py`
2. または新規利用者を登録する

### ページネーションが機能しない

**原因**: データが20件以下しかない

**解決策**:
- 1ページは20件表示なので、21件以上のデータが必要
- テストデータを追加する

---

## レスポンシブ確認

### PC (1920x1080)

すべての機能が横に展開されて表示されます。

### タブレット (iPad: 768x1024)

- ダッシュボード: 統計カードが2列表示
- ネットワーク図: グラフが縦長に調整
- 検索フォーム: フィールドが縦積み

### スマートフォン (375x667)

- すべての要素が縦積み表示
- テーブルは横スクロール

---

## 次のステップ

1. ✅ サーバーを起動
2. ✅ ダッシュボードにアクセス
3. ✅ 各機能を動作確認
4. ✅ API動作確認
5. ✅ レスポンシブ確認

すべて確認できたら、Phase 3の実装は完了です！

---

## 参考リンク

- **Swagger API ドキュメント**: http://localhost:8000/api/docs
- **ReDoc API ドキュメント**: http://localhost:8000/api/redoc

- **実装詳細**: `/Users/k-kawahara/Ai-Workspace/keikaku-sodan-app/PHASE3_IMPLEMENTATION_SUMMARY.md`
- **プロジェクトREADME**: `/Users/k-kawahara/Ai-Workspace/keikaku-sodan-app/README.md`
