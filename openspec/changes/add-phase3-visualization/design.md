# Design Document: Phase 3 - Visualization & Advanced Features

## Context

### Background
Phase 1 & 2で基本機能（利用者管理、相談記録、計画・モニタリング、PDF出力）が完成し、実際のデータが蓄積されている。現在、以下のニーズが顕在化している：
- 支援ネットワークの全体像を一目で把握したい（ケース会議、家族説明）
- 期限管理（計画更新、モニタリング実施）を自動化したい
- 蓄積したデータから統計情報を抽出したい
- 複数条件での高速検索を実現したい

### Constraints
- **技術制約**: SQLite（同時書き込み制限あり）
- **リソース制約**: 3-4名のスタッフ、事業所内サーバー
- **パフォーマンス制約**: タブレット対応必須、3秒以内の描画
- **学習コスト**: プログラミング初心者でも保守可能な実装

### Stakeholders
- **エンドユーザー**: 計画相談支援専門員（3-4名）
- **管理者**: 事業所管理者（1名）
- **開発者**: 将来のメンテナンス担当者（プログラミング初心者の可能性）

## Goals / Non-Goals

### Goals
1. **ネットワーク図の可視化**
   - 利用者を中心とした支援ネットワークをインタラクティブに表示
   - 支援会議・家族説明で活用できる印刷可能なエクスポート機能
   - 既存データ（user_organizations）を活用し、新規テーブル不要
2. **ダッシュボード強化**
   - 事業所全体の統計情報を視覚化
   - 期限が近い項目のアラート自動表示
   - クイックアクションによる業務効率化
3. **高度な検索機能**
   - 複数条件を組み合わせた検索
   - ページネーション対応
   - 2秒以内のレスポンス

### Non-Goals（Phase 4以降に延期）
- 保存された検索条件（ユーザー設定管理が必要）
- CSV/Excelエクスポート（外部ライブラリ依存）
- レポート機能（月次/年次）（複雑な集計ロジック）
- カスタムレポート（ユーザー定義の集計条件）
- ネットワーク図のリアルタイム編集（ドラッグで関係性を変更）
- AI分析機能（機械学習ライブラリ依存）

## Decisions

### 1. ネットワーク図ライブラリの選択: D3.js

**Decision**: D3.js (Force-Directed Graph) を採用

**Rationale**:
- **柔軟性**: ノード・エッジの視覚表現をカスタマイズ可能
- **軽量性**: CDN経由で利用可能、パッケージ管理不要
- **学習コスト**: サンプルコードが豊富、日本語情報も多い
- **レスポンシブ対応**: SVGベースでタッチ操作にも対応

**Alternatives Considered**:
1. **Cytoscape.js**
   - Pro: グラフ可視化に特化、高機能
   - Con: D3.jsより学習コスト高い、オーバースペック
   - 却下理由: シンプルなネットワーク図にはD3.jsで十分
2. **Vis.js**
   - Pro: すぐに使える高レベルAPI
   - Con: カスタマイズ性が低い、デザインの自由度が低い
   - 却下理由: Bootstrap 5との統一感を保ちたい
3. **自前実装（Canvas/SVG）**
   - Pro: 完全なコントロール
   - Con: Force Simulationの実装が複雑
   - 却下理由: 車輪の再発明、保守コストが高い

### 2. 統計グラフライブラリの選択: Chart.js

**Decision**: Chart.js v4 を採用

**Rationale**:
- **シンプル**: 宣言的な設定でグラフを描画可能
- **レスポンシブ**: 自動的に画面幅に合わせてリサイズ
- **Bootstrap 5との相性**: デザインが統一しやすい
- **軽量性**: CDN経由で利用可能

**Alternatives Considered**:
1. **Plotly.js**
   - Pro: インタラクティブ性が高い、科学的グラフに強い
   - Con: ファイルサイズが大きい（3MB+）、オーバースペック
   - 却下理由: ダッシュボードには Chart.js で十分
2. **ApexCharts**
   - Pro: モダンなデザイン、高機能
   - Con: Chart.js より学習コスト高い
   - 却下理由: Chart.js で要件を満たせる
3. **Google Charts**
   - Pro: Googleのサポート、豊富なグラフタイプ
   - Con: 外部サービス依存、オフライン動作不可
   - 却下理由: 事業所内サーバーで完結させたい

### 3. データベーススキーマ変更の回避

**Decision**: 既存テーブル（user_organizations）を活用し、新規テーブルを作成しない

**Rationale**:
- **シンプル性**: データベースマイグレーションが不要
- **データ整合性**: 既存データがそのまま活用可能
- **保守性**: テーブル数を増やさないことで理解しやすさを維持

**Trade-offs**:
- ネットワーク図のカスタム設定（ノード位置の保存等）は実装困難
  - 対策: Phase 4以降で必要に応じて検討
- 関係性の重みづけは`frequency`フィールドに依存
  - 対策: 現状のデータで十分、将来的に拡張可能

### 4. キャッシュ戦略

**Decision**: ダッシュボード統計データは15分間サーバーサイドキャッシュ

**Rationale**:
- **パフォーマンス**: 集計クエリの実行頻度を削減
- **鮮度**: 15分以内の変更であれば許容範囲
- **実装コスト**: Python標準ライブラリ（functools.lru_cache）で実装可能

**Invalidation Strategy**:
- 利用者・計画・モニタリングの作成/更新/削除時にキャッシュをクリア
- 実装: デコレーターで自動的にキャッシュクリア

### 5. ページネーション戦略

**Decision**: サーバーサイドページネーション（limit/offset方式）

**Rationale**:
- **パフォーマンス**: 大量データでもメモリ消費を抑制
- **ユーザー体験**: 初期表示が高速（20件のみロード）
- **実装コスト**: SQLAlchemyで簡単に実装可能

**Alternatives Considered**:
1. **クライアントサイドページネーション**
   - Pro: ページ切り替えが高速
   - Con: 初期ロードが遅い、メモリ消費大
   - 却下理由: 利用者数が増えた場合に問題

### 6. エクスポート形式: PNG/SVG

**Decision**: ネットワーク図はPNGとSVGの両方でエクスポート可能

**Rationale**:
- **PNG**: すぐに印刷・資料に貼り付け可能（ラスタ形式）
- **SVG**: 編集可能、拡大しても劣化しない（ベクタ形式）
- **実装コスト**: D3.jsのSVGをそのまま保存、またはCanvas変換

**Implementation**:
- SVG保存: 既存のSVG要素をBlobとしてダウンロード
- PNG保存: SVGをCanvasに変換してtoDataURLで保存

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│ │  D3.js      │ │  Chart.js   │ │ Advanced Search UI  ││
│ │  (Network)  │ │ (Dashboard) │ │ (Forms)             ││
│ └──────┬──────┘ └──────┬──────┘ └──────┬──────────────┘│
│        │                │                │               │
│        └────────────────┴────────────────┘               │
│                         │                                │
└─────────────────────────┼────────────────────────────────┘
                          │ HTTPS (JSON)
┌─────────────────────────┼────────────────────────────────┐
│                    Backend (FastAPI)                      │
├─────────────────────────┼────────────────────────────────┤
│ ┌──────────────┬────────┴────────┬──────────────────┐   │
│ │ /api/network │ /api/dashboard  │ /api/users (ext) │   │
│ │              │                 │ /api/plans (ext) │   │
│ └──────┬───────┴─────────┬───────┴─────────┬────────┘   │
│        │                 │                 │             │
│ ┌──────▼─────────────────▼─────────────────▼────────┐   │
│ │          Service Layer                             │   │
│ │  - NetworkService                                  │   │
│ │  - DashboardService (with cache)                   │   │
│ │  - SearchService                                   │   │
│ └──────────────────────┬─────────────────────────────┘   │
│                        │                                  │
│ ┌──────────────────────▼─────────────────────────────┐   │
│ │          SQLAlchemy Models                         │   │
│ │  - User, Organization, UserOrganization            │   │
│ │  - Plan, Monitoring, Consultation                  │   │
│ └──────────────────────┬─────────────────────────────┘   │
└────────────────────────┼──────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ SQLite  │
                    │   DB    │
                    └─────────┘
```

### Data Flow

#### ネットワーク図の描画
```
1. User clicks "ネットワーク図" tab
2. Frontend: GET /api/users/{user_id}/network
3. Backend:
   a. NetworkService.get_network_data(user_id)
   b. Query user_organizations table
   c. Generate nodes and edges JSON
4. Backend: Return JSON response
5. Frontend: D3.js renders Force-Directed Graph
6. User: Drag, zoom, click nodes
7. User clicks "PNG保存"
8. Frontend: Convert SVG to PNG, download
```

#### ダッシュボード統計の表示
```
1. User navigates to dashboard
2. Frontend: GET /api/dashboard/statistics
3. Backend:
   a. Check cache (15-minute TTL)
   b. If cache miss:
      - DashboardService.get_statistics()
      - Aggregate queries (user count, consultations, plans, monitorings)
      - Cache result
   c. Return JSON response
4. Frontend: Chart.js renders graphs
5. User sees statistics and alerts
```

#### 高度な検索
```
1. User fills search form (name, staff, disability level)
2. Frontend: GET /api/users?name=山田&staff_id=1&level_gte=4&limit=20&offset=0
3. Backend:
   a. SearchService.search_users(filters, pagination)
   b. Build dynamic SQLAlchemy query with filters
   c. Apply pagination (limit/offset)
   d. Execute query
4. Backend: Return {results: [...], total_count: 50}
5. Frontend: Render table with pagination controls
```

## Risks / Trade-offs

### Risk 1: ネットワーク図のパフォーマンス低下（関係機関が多い場合）
**Description**: 利用者に30件以上の関係機関が登録されている場合、Force Simulationの収束に時間がかかる

**Likelihood**: Low（現状、最大で10件程度）

**Impact**: Medium（描画に5秒以上かかる可能性）

**Mitigation**:
- 関係機関が20件以上の場合、警告メッセージを表示
- Force Simulationのiterations（反復回数）を制限
- 必要に応じて、静的レイアウト（円形配置等）にフォールバック

### Risk 2: SQLiteの同時書き込み制限
**Description**: ダッシュボード統計の集計中に他のユーザーがデータを更新すると、ロックエラーが発生する可能性

**Likelihood**: Low（3-4名のユーザー、読み取りが多い）

**Impact**: Low（エラーメッセージが表示されるが、再試行で成功）

**Mitigation**:
- 読み取り専用の統計クエリは優先度を下げる
- キャッシュにより集計クエリの実行頻度を削減
- 将来的にPostgreSQLへ移行する場合の準備（SQLAlchemy使用）

### Risk 3: ブラウザの互換性問題
**Description**: 古いブラウザ（IE11等）ではD3.jsとChart.jsが動作しない

**Likelihood**: Low（モダンブラウザを推奨）

**Impact**: High（機能が全く使えない）

**Mitigation**:
- ログイン画面でブラウザチェックを実施
- IE11等の古いブラウザの場合、警告メッセージを表示
- モダンブラウザ（Chrome, Firefox, Safari）の使用を推奨

### Risk 4: タブレットでのタッチ操作の不具合
**Description**: iPadでのピンチジェスチャーやドラッグ操作がうまく動作しない

**Likelihood**: Medium（D3.jsのタッチイベント処理が複雑）

**Impact**: Medium（モバイル体験が悪化）

**Mitigation**:
- 実装時にiPad実機でテスト
- タッチイベントのポリフィル（d3-drag, d3-zoom）を適切に設定
- 必要に応じて、タッチ操作用のカスタムハンドラーを実装

### Trade-off 1: キャッシュの鮮度 vs パフォーマンス
**Trade-off**: ダッシュボード統計を15分キャッシュすると、リアルタイムではない

**Decision**: 15分のキャッシュを採用

**Rationale**:
- 統計情報はリアルタイムである必要性が低い
- 集計クエリのパフォーマンスを優先
- 手動で「更新」ボタンを押せば強制的にキャッシュをクリア可能（将来実装）

### Trade-off 2: ページネーション vs 全件表示
**Trade-off**: ページネーションにすると、一覧性が低下する

**Decision**: 20件/ページでページネーション

**Rationale**:
- 初期ロード時間を短縮
- 現状（利用者5名）では問題ないが、将来的に増加した場合に備える
- 検索機能で絞り込み可能

## Migration Plan

### Phase 3リリース手順

#### 1. 準備（リリース前日）
- [ ] データベースバックアップ実施
- [ ] 開発環境で最終動作確認
- [ ] リリースノート作成

#### 2. リリース（リリース当日）
- [ ] Gitでタグ付け（v3.0.0）
- [ ] 本番サーバーにコードデプロイ
- [ ] 依存関係のインストール（不要、CDN使用）
- [ ] サービス再起動（uvicorn）
- [ ] スモークテスト実施
  - ログイン動作確認
  - ダッシュボード表示確認
  - ネットワーク図描画確認
  - 検索動作確認

#### 3. 動作確認（リリース直後）
- [ ] ユーザーに新機能の説明
- [ ] 実際のデータでネットワーク図を確認
- [ ] ダッシュボードのアラートが正しく動作するか確認

#### 4. フォローアップ（リリース1週間後）
- [ ] ユーザーからのフィードバック収集
- [ ] パフォーマンスメトリクスの確認
- [ ] バグ報告への対応

### Rollback Plan

もし重大な問題が発生した場合:

1. **即座に旧バージョンへロールバック**
   ```bash
   git checkout v2.0.0
   systemctl restart keikaku-sodan-app
   ```
2. **データベース復元**（もし必要な場合）
   ```bash
   cp backups/keikaku_sodan_backup_YYYYMMDD.db keikaku_sodan.db
   ```
3. **ユーザーへの通知**
   - 問題が発生したこと
   - 旧バージョンに戻したこと
   - 修正版のリリース予定

## Open Questions

### Q1: ネットワーク図のレイアウトアルゴリズム
**Question**: Force-Directed Graphが最適か？他のレイアウト（円形配置、階層配置）も検討すべきか？

**Answer**: まずはForce-Directed Graphで実装。ユーザーフィードバックを受けて、Phase 4で他のレイアウトも検討。

### Q2: ダッシュボードのカスタマイズ
**Question**: ユーザーごとにダッシュボードのグラフ表示/非表示を設定できるようにすべきか？

**Answer**: Phase 3ではすべてのユーザーに同じダッシュボードを表示。Phase 4以降でユーザー設定機能を検討。

### Q3: 検索条件の保存
**Question**: よく使う検索条件を保存できるようにすべきか？

**Answer**: Phase 4以降に延期。ユーザー設定テーブルの追加が必要なため、Phase 3では実装しない。

### Q4: モバイルアプリ対応
**Question**: スマートフォン専用のネイティブアプリを開発すべきか？

**Answer**: 現時点では不要。Webアプリのレスポンシブ対応で十分。将来的にニーズがあれば検討。

### Q5: リアルタイム更新（WebSocket）
**Question**: ダッシュボードをリアルタイムで更新すべきか（WebSocket使用）？

**Answer**: Phase 3では不要。キャッシュ戦略で十分。将来的にリアルタイム性が求められる場合に検討。

## Success Metrics

### パフォーマンス指標
- ダッシュボード初期ロード時間: **< 3秒** （目標: 2秒）
- ネットワーク図描画時間: **< 3秒** （目標: 2秒）
- 検索レスポンス時間: **< 2秒** （目標: 1秒）

### 機能利用率
- ネットワーク図の月次利用回数: **> 10回/月**
- ダッシュボードの日次アクセス: **> 3回/日**
- 高度な検索の月次利用回数: **> 20回/月**

### ユーザー満足度
- ネットワーク図の有用性: **4/5点以上**
- ダッシュボードアラートの有用性: **4/5点以上**
- 検索機能の使いやすさ: **4/5点以上**

### ビジネスインパクト
- 期限管理ミス: **月0件** （現状: 月1-2件）
- 情報検索時間: **平均30秒** （現状: 平均3分）
- 支援会議準備時間: **平均10分** （現状: 平均30分）

## Appendix

### 参考資料
- D3.js公式ドキュメント: https://d3js.org/
- Chart.js公式ドキュメント: https://www.chartjs.org/
- Force-Directed Graphサンプル: https://observablehq.com/@d3/force-directed-graph
- FastAPI キャッシング: https://fastapi.tiangolo.com/tutorial/dependencies/

### 技術的詳細

#### D3.jsのForce Simulationパラメータ
```javascript
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(edges).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide().radius(30));
```

#### Chart.jsのレスポンシブ設定
```javascript
const config = {
  type: 'line',
  data: data,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    }
  }
};
```

#### SQLAlchemyの動的クエリビルダー例
```python
def search_users(filters: dict):
    query = db.query(User)
    if filters.get('name'):
        query = query.filter(User.name.like(f"%{filters['name']}%"))
    if filters.get('assigned_staff_id'):
        query = query.filter(User.assigned_staff_id == filters['assigned_staff_id'])
    if filters.get('disability_support_level_gte'):
        query = query.filter(User.disability_support_level >= filters['disability_support_level_gte'])
    return query.offset(filters.get('offset', 0)).limit(filters.get('limit', 20)).all()
```
