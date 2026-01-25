# SwithMe MVP1 実装計画

## 概要

SwithMeは、マイルストーンを達成できなかった場合に課金される自己管理支援サービスです。本計画では、MVP1を段階的に分割して実装します。

**実装範囲の決定事項**:
- バックエンドAPIのみ（フロントエンドは別フェーズ）
- 位置情報による検証のみ（画像・音声は将来実装）
- モック決済のみ（実際の決済は将来実装）
- PostgreSQLを使用

**技術スタック**: FastAPI + Pydantic + PostgreSQL
**開発手法**: TDD（Red-Green-Refactor）+ DDD + 関数型プログラミング

---

## フェーズ分割

MVP1は大きすぎるため、以下のように段階的に分割します：

```
MVP0.1 → MVP0.2 → MVP0.3 → MVP0.4 → MVP1
  ↓        ↓        ↓        ↓        ↓
基盤    マイル   位置情報   ペナル   統合と
構築    ストーン   検証     ティ    レポート
```

---

## ディレクトリ構造

```
/Users/taisei/Projects/private/SwitchMe/
├── apps/
│   └── api/                      # FastAPIアプリケーション
│       ├── main.py              # FastAPIエントリーポイント
│       ├── routers/             # APIルーター
│       ├── dependencies.py      # 依存性注入の設定
│       └── middleware/          # ミドルウェア
├── domain/                      # ドメイン層（DDD）
│   ├── user/                   # User集約（集約、エンティティ、値オブジェクト、リポジトリIF）
│   ├── milestone/              # Milestone集約
│   ├── verification/           # Verification集約
│   ├── achievement/            # AchievementRecord集約
│   ├── penalty/                # Penalty集約
│   ├── payment/                # PaymentMethod集約
│   ├── report/                 # Report集約
│   └── shared/                 # 共通ドメインクラス（Money, 例外）
├── application/                 # アプリケーション層（ユースケース）
│   ├── user/                   # User関連ユースケース
│   ├── milestone/              # Milestone関連ユースケース
│   ├── verification/           # Verification関連ユースケース
│   ├── achievement/            # AchievementRecord関連ユースケース
│   ├── penalty/                # Penalty関連ユースケース
│   ├── payment/                # PaymentMethod関連ユースケース
│   └── report/                 # Report関連ユースケース
├── infrastructure/              # インフラ層（DB実装、外部アダプター）
│   ├── user/                   # User永続化・アダプター
│   ├── milestone/              # Milestone永続化・アダプター
│   ├── verification/           # Verification永続化・アダプター
│   ├── achievement/            # AchievementRecord永続化・アダプター
│   ├── penalty/                # Penalty永続化・アダプター
│   ├── payment/                # PaymentMethod永続化・アダプター
│   ├── report/                 # Report永続化・アダプター
│   └── shared/                 # 共通インフラ（DB接続、ユーティリティ）
├── tests/                       # テスト
│   ├── unit/                   # 単体テスト（ドメインロジック）
│   │   ├── domain/
│   │   └── application/
│   ├── integration/            # 統合テスト（リポジトリ、DB）
│   └── e2e/                    # E2Eテスト（API）
├── migrations/                  # DBマイグレーション（Alembic）
├── pyproject.toml              # 依存関係管理
├── .env                        # 環境変数
└── README.md                   # プロジェクトドキュメント
```

---

## MVP0.1: 基盤構築

### 目標
- プロジェクト構造の確立
- FastAPI基本セットアップ
- PostgreSQL接続
- JWT認証基盤
- User集約の完全実装

### 実装順序（TDDサイクル）

#### ステップ1: プロジェクト初期化

**タスク1.1: 依存関係管理のセットアップ**
1. `uv init` でプロジェクトを初期化
2. `pyproject.toml` を作成（uv形式）
   - FastAPI, Pydantic, SQLAlchemy, asyncpg, pytest等
3. `uv sync` で依存関係をインストール

**コマンド**:
```bash
uv init
uv add fastapi uvicorn[standard] pydantic pydantic-settings
uv add sqlalchemy asyncpg alembic
uv add python-jose[cryptography] passlib[bcrypt] python-multipart
uv add python-dotenv structlog
uv add --dev pytest pytest-asyncio pytest-cov pytest-mock httpx
uv add --dev ruff mypy
```

**成果物**: `/Users/taisei/Projects/private/SwitchMe/pyproject.toml`

---

#### ステップ2: 共通基盤の実装

**タスク2.1: Result型の実装（TDD）**

**RED: テスト作成**
- ファイル: `tests/unit/infrastructure/shared/test_result.py`
- テスト内容:
  - `Ok()` で成功のResultが作成されること
  - `Err()` で失敗のResultが作成されること
  - `map()` で値を変換できること
  - `and_then()` で処理を連鎖できること

**GREEN: 実装**
- ファイル: `infrastructure/shared/result.py`
- 実装内容:
  - `Ok[T, E]`: 成功を表す型
  - `Err[T, E]`: 失敗を表す型
  - `Result = Union[Ok, Err]`
  - メソッド: `is_ok()`, `is_err()`, `unwrap()`, `map()`, `and_then()`

**REFACTOR:**
- `ruff check infrastructure/shared/result.py`
- `ruff format infrastructure/shared/result.py`

**コミット:**
```bash
git add tests/unit/infrastructure/shared/test_result.py
git commit -m "test: Result型のテストを追加"
git add infrastructure/shared/result.py
git commit -m "feat: Result型を実装"
```

---

**タスク2.2: 共通値オブジェクト（Money）の実装（TDD）**

**RED: テスト作成**
- ファイル: `tests/unit/domain/shared/test_value_objects.py`
- テスト内容:
  - 正の金額でMoneyが作成できること
  - 負の金額は拒否されること
  - 同じ通貨のMoneyを加算できること
  - 異なる通貨のMoneyは加算できないこと

**GREEN: 実装**
- ファイル: `domain/shared/value_objects.py`
  - `Money`: 金額を表す値オブジェクト（Pydantic BaseModel、frozen=True）
  - バリデーション: amount >= 0, currency in ["JPY", "USD", "EUR"]
  - メソッド: `add(other: Money) -> Money`

- ファイル: `domain/shared/exceptions.py`
  - `DomainException`: ドメイン層の基底例外
  - `DomainValidationError`: バリデーションエラー
  - `EntityNotFoundError`: エンティティが見つからない
  - `UnauthorizedError`: 認証エラー

**コミット:**
```bash
git add tests/unit/domain/shared/ domain/shared/
git commit -m "feat: 共通値オブジェクト（Money）とドメイン例外を実装"
```

---

**タスク2.3: Database接続管理の実装（TDD）**

**RED: テスト作成**
- ファイル: `tests/unit/infrastructure/shared/test_database.py`
- テスト内容:
  - DATABASE_URLが正しく構築されること
  - エンジンが作成されること

**GREEN: 実装**
- ファイル: `infrastructure/shared/database.py`
  - `get_database_url()`: PostgreSQL接続URLの構築
  - `get_engine()`: SQLAlchemyエンジンの作成
  - `get_session_maker()`: セッションメーカーの作成
  - `get_session()`: セッションの取得（依存性注入用）

**コミット:**
```bash
git add tests/unit/infrastructure/shared/ infrastructure/shared/database.py
git commit -m "feat: データベース接続管理を実装"
```

---

#### ステップ3: User集約の実装

**タスク3.1: Userドメインモデルの実装（TDD）**

**RED: テスト作成**
- ファイル: `tests/unit/domain/user/test_models.py`
- テスト内容:
  - Emailが正しい形式を検証すること
  - Userが作成できること
  - ログインすると最終ログイン日時が更新されること
  - アカウント削除するとステータスが変わること

**GREEN: 実装**
- ファイル: `domain/user/models.py`
  - 値オブジェクト:
    - `UserId(value: UUID)`: ユーザーID
    - `Email(value: str)`: メールアドレス（正規表現検証）
    - `HashedPassword(value: str)`: ハッシュ化されたパスワード
    - `UserStatus(status: Literal["active", "suspended", "deleted"], last_login_at: datetime | None)`: ステータス
  - 集約ルート:
    - `User`: ユーザー（frozen=True）
    - メソッド: `create()`, `login()`, `delete_account()`

**コミット:**
```bash
git add tests/unit/domain/user/test_models.py domain/user/models.py
git commit -m "feat: Userドメインモデルを実装"
```

---

**タスク3.2: Userリポジトリインターフェースの実装（TDD）**

**RED: テスト作成**
- ファイル: `tests/unit/domain/user/test_repositories.py`
- テスト内容（インメモリ実装を使用）:
  - ユーザーを保存して取得できること
  - メールアドレスでユーザーを検索できること
  - 存在しないユーザーの検索はErrを返すこと
  - ユーザーを削除できること

**GREEN: 実装**
- ファイル: `domain/user/repositories.py`
  - `UserRepository` (Protocol): リポジトリインターフェース
    - `save(user: User) -> Result[None, Exception]`
    - `find_by_id(user_id: UserId) -> Result[User, EntityNotFoundError]`
    - `find_by_email(email: Email) -> Result[User, EntityNotFoundError]`
    - `delete(user_id: UserId) -> Result[None, Exception]`
  - `InMemoryUserRepository`: テスト用インメモリ実装

**コミット:**
```bash
git add tests/unit/domain/user/test_repositories.py domain/user/repositories.py
git commit -m "feat: Userリポジトリインターフェースとインメモリ実装"
```

---

**タスク3.3: User登録ユースケースの実装（TDD）**

**RED: テスト作成**
- ファイル: `tests/unit/application/user/test_use_cases.py`
- テスト内容:
  - ユーザー登録が成功すること
  - 同じメールアドレスでの登録は失敗すること

**GREEN: 実装**
- ファイル: `application/user/use_cases.py`
  - `RegisterUserInput(email: str, password: str)`: 入力モデル
  - `RegisterUserUseCase`: ユーザー登録ユースケース
    - メールアドレスの重複チェック
    - パスワードのハッシュ化
    - ユーザー作成と保存

- ファイル: `infrastructure/user/adapters/password_hasher.py`
  - `PasswordHasher` (Protocol): パスワードハッシュ化インターフェース
  - `BcryptPasswordHasher`: Bcryptを使用した実装
  - `InMemoryPasswordHasher`: テスト用実装

**コミット:**
```bash
git add tests/unit/application/user/ application/user/ infrastructure/user/adapters/
git commit -m "feat: ユーザー登録ユースケースを実装"
```

---

**タスク3.4: FastAPIエンドポイントの実装（E2E）**

**RED: テスト作成**
- ファイル: `tests/e2e/test_user_api.py`
- テスト内容:
  - ユーザー登録APIが動作すること（201ステータス）
  - 重複メールアドレスでの登録は失敗すること（400ステータス）

**GREEN: 実装**
- ファイル: `apps/api/main.py`
  - FastAPIアプリケーションの初期化
  - ルーターの登録
  - ヘルスチェックエンドポイント

- ファイル: `apps/api/routers/user_router.py`
  - `POST /api/v1/users/register`: ユーザー登録
  - リクエスト/レスポンスモデル（Pydantic）
  - 依存性注入（Depends）
  - エラーハンドリング（HTTPException）

**コミット:**
```bash
git add tests/e2e/ apps/api/
git commit -m "feat: ユーザー登録APIエンドポイントを実装"
```

---

### MVP0.1の完了基準

1. すべてのテストがパスすること
   ```bash
   pytest tests/ --cov=. --cov-report=term-missing
   ```

2. 静的解析とフォーマットがクリーンであること
   ```bash
   ruff check .
   ruff format .
   ```

3. 以下のAPIが動作すること
   - `POST /api/v1/users/register`: ユーザー登録
   - `GET /health`: ヘルスチェック

4. カバレッジ目標: 80%以上

5. コミット履歴がTDDサイクルに従っていること

---

## MVP0.2: マイルストーン管理

### 目標
- Milestone集約の完全実装
- マイルストーンCRUD API
- 値オブジェクト（DeadlineInfo, VerificationCriteria, PenaltyInfo）の実装

### 実装順序

#### ステップ1: Milestoneドメインモデルの実装

**実装内容:**
1. 値オブジェクトの実装（TDD）
   - `DeadlineInfo`: 期限情報（date, time, timezone, reminderSettings）
   - `VerificationCriteria`: 検証基準（type, conditions, threshold）
   - `PenaltyInfo`: ペナルティ情報（amount: Money, description）

2. Milestone集約ルートの実装（TDD）
   - `MilestoneId`, `Title`等の値オブジェクト
   - `Milestone`: マイルストーン集約
   - メソッド: `create()`, `update()`, `delete()`, `setPenaltyAmount()`
   - ステータス管理: active, completed, failed, cancelled

3. リポジトリインターフェースの実装
   - `MilestoneRepository`: 保存、検索、削除
   - インメモリ実装（テスト用）

**主要ファイル:**
- `domain/milestone/models.py`
- `domain/milestone/repositories.py`
- `tests/unit/domain/milestone/test_models.py`

---

#### ステップ2: マイルストーンユースケースの実装

**実装内容:**
1. `CreateMilestoneUseCase`: マイルストーン作成
2. `UpdateMilestoneUseCase`: マイルストーン更新
3. `GetMilestonesUseCase`: 一覧取得（ユーザーIDでフィルタ）
4. `DeleteMilestoneUseCase`: 削除（論理削除）

**テスト戦略:**
- 認可チェック（所有者のみ更新/削除可能）
- ビジネスルールの検証
- エラーハンドリング

**主要ファイル:**
- `application/milestone/use_cases.py`
- `tests/unit/application/milestone/test_use_cases.py`

---

#### ステップ3: マイルストーンAPI + JWT認証の実装

**実装内容:**
1. JWT認証ミドルウェア
   - `POST /api/v1/auth/login`: ログイン（JWTトークン発行）
   - トークン検証ミドルウェア
   - ユーザーIDの抽出

2. マイルストーンAPIエンドポイント
   - `POST /api/v1/milestones`: マイルストーン作成
   - `GET /api/v1/milestones`: 一覧取得
   - `GET /api/v1/milestones/{milestone_id}`: 詳細取得
   - `PUT /api/v1/milestones/{milestone_id}`: 更新
   - `DELETE /api/v1/milestones/{milestone_id}`: 削除

**主要ファイル:**
- `apps/api/routers/milestone_router.py`
- `apps/api/routers/auth_router.py`
- `apps/api/middleware/auth.py`
- `tests/e2e/test_milestone_api.py`

---

### MVP0.2の完了基準

1. すべてのテストがパスすること
2. マイルストーンCRUD APIが完全に動作すること
3. JWT認証が正しく機能すること
4. カバレッジ: 80%以上

---

## MVP0.3: 位置情報検証

### 目標
- Verification集約の実装
- AchievementRecord集約の実装
- 位置情報による検証ロジック
- GPS検証アルゴリズム（Haversine公式）

### 実装順序

#### ステップ1: Verificationドメインモデルの実装

**実装内容:**
1. 値オブジェクト
   - `Location(latitude: float, longitude: float)`: 位置情報
   - `Distance(meters: float)`: 距離
   - `VerificationResult(success: bool, score: float, confidence: float)`: 検証結果

2. エンティティ
   - `SensorData`: センサーデータ（位置情報、タイムスタンプ）
   - `AnalysisResult`: 分析結果

3. Verification集約ルート
   - `Verification`: 検証プロセス
   - メソッド: `start()`, `collectSensorData()`, `analyze()`, `finalize()`

**主要ファイル:**
- `domain/verification/models.py`
- `domain/verification/services.py`
- `tests/unit/domain/verification/test_services.py`

---

#### ステップ2: GPS検証サービスの実装

**実装内容:**
1. `GPSVerificationService`: GPS検証ドメインサービス
   - Haversine公式による距離計算
   - 閾値との比較
   - スコア計算

2. 位置情報送信API
   - `POST /api/v1/verifications`: 検証開始
   - `POST /api/v1/verifications/{verification_id}/location`: 位置情報送信
   - `POST /api/v1/verifications/{verification_id}/complete`: 検証完了

**テスト戦略:**
- 実際の位置情報データでのテスト
- エッジケース（境界上、遠すぎる、近すぎる）

**主要ファイル:**
- `domain/verification/services.py`
- `apps/api/routers/verification_router.py`

---

#### ステップ3: AchievementRecordドメインモデルの実装

**実装内容:**
1. AchievementRecord集約ルート
   - 達成記録の作成
   - 失敗記録の作成
   - 通知情報の管理

2. 値オブジェクト
   - `Status(achieved: bool, reason: str, score: float)`: 達成状態
   - `Evidence(type: str, references: List)`: 証拠
   - `NotificationInfo`: 通知情報

3. ユースケース
   - `RecordAchievementUseCase`: 達成記録
   - `RecordFailureUseCase`: 失敗記録

**主要ファイル:**
- `domain/achievement/models.py`
- `application/achievement/use_cases.py`

---

### MVP0.3の完了基準

1. 位置情報による検証が正しく動作すること
2. 達成/失敗が正確に記録されること
3. GPS距離計算の精度テストがパスすること
4. カバレッジ: 80%以上

---

## MVP0.4: ペナルティシステム（モック決済）

### 目標
- Penalty集約の実装
- PaymentMethod集約（モック決済）
- モック決済処理
- 通知機能

### 実装順序

#### ステップ1: Penaltyドメインモデルの実装

**実装内容:**
1. Penalty集約ルート
   - ペナルティの発生
   - 決済処理
   - 通知送信

2. 値オブジェクト
   - `ChargeDetails(amount: Money, paymentMethodId: UUID)`: 課金詳細
   - `ChargeStatus(status: str, processedAt: datetime)`: 課金ステータス
   - `NotificationLog`: 通知ログ

3. ユースケース
   - `ChargePenaltyUseCase`: ペナルティ課金
   - `GetPenaltyHistoryUseCase`: ペナルティ履歴取得

**主要ファイル:**
- `domain/penalty/models.py`
- `application/penalty/use_cases.py`

---

#### ステップ2: PaymentMethodドメインモデル（モック）の実装

**実装内容:**
1. PaymentMethod集約ルート
   - 支払い方法の登録
   - 削除
   - 課金処理（モック）

2. モック決済アダプター
   - `MockPaymentGateway`: 常に成功する決済ゲートウェイ
   - 課金履歴の記録

3. API
   - `POST /api/v1/payment-methods`: 支払い方法登録
   - `GET /api/v1/payment-methods`: 一覧取得
   - `DELETE /api/v1/payment-methods/{id}`: 削除

**主要ファイル:**
- `domain/payment/models.py`
- `infrastructure/payment/adapters/payment_gateway.py`

---

#### ステップ3: 通知機能の実装

**実装内容:**
1. 通知アダプター
   - `NotificationService` (Protocol): 通知インターフェース
   - `MockNotificationService`: コンソール出力のみ

2. 通知ユースケース
   - マイルストーンのリマインダー
   - 達成/失敗の通知
   - ペナルティ課金の通知

**主要ファイル:**
- `infrastructure/notification/adapters/notification_service.py`

---

### MVP0.4の完了基準

1. ペナルティが正しく発生すること
2. モック決済が動作すること
3. 通知が送信されること
4. カバレッジ: 80%以上

---

## MVP1: 統合とレポート

### 目標
- Report集約の実装
- エンドツーエンドフローの統合
- PostgreSQL永続化実装
- APIドキュメント完成

### 実装順序

#### ステップ1: Reportドメインモデルの実装

**実装内容:**
1. Report集約ルート
   - 習慣形成レポートの生成
   - 課金履歴レポートの生成

2. レポートユースケース
   - `GenerateHabitFormationReportUseCase`: 達成率、連続日数など
   - `GenerateChargeHistoryUseCase`: 課金履歴サマリー

3. API
   - `GET /api/v1/reports/habit-formation`: 習慣形成レポート
   - `GET /api/v1/reports/charge-history`: 課金履歴レポート

**主要ファイル:**
- `domain/report/models.py`
- `application/report/use_cases.py`

---

#### ステップ2: エンドツーエンドフローの統合

**実装内容:**
1. 統合テスト
   - ユーザー登録 → マイルストーン作成 → 検証 → 達成/失敗 → ペナルティ → レポート
   - 複数のマイルストーンの並行実行

2. パフォーマンステスト
   - 負荷テスト
   - レスポンスタイムの測定（目標: 500ms以内）

**主要ファイル:**
- `tests/e2e/test_full_flow.py`
- `tests/performance/test_load.py`

---

#### ステップ3: PostgreSQL永続化実装

**実装内容:**
1. SQLAlchemyモデルの定義
   - 各集約ルートのテーブル定義
   - リレーションシップ

2. リポジトリの永続化実装
   - `PostgresUserRepository`
   - `PostgresMilestoneRepository`
   - 他のリポジトリ

3. マイグレーション
   - Alembicによるマイグレーション管理

**主要ファイル:**
- `infrastructure/*/persistence/models.py`
- `infrastructure/*/persistence/repositories.py`
- `migrations/`

---

#### ステップ4: OpenAPIドキュメント

**実装内容:**
1. FastAPIの自動ドキュメント生成
   - スキーマの整理
   - 説明の追加
   - サンプルリクエスト/レスポンス

2. Redocによるドキュメント公開
   - `/docs`: Swagger UI
   - `/redoc`: Redoc

**主要ファイル:**
- `apps/api/main.py`

---

### MVP1の完了基準

1. すべてのE2Eテストがパスすること
2. PostgreSQL永続化が動作すること
3. OpenAPIドキュメントが完全であること
4. パフォーマンス目標を達成すること（レスポンス500ms以内）
5. カバレッジ: 85%以上
6. デプロイ可能な状態であること

---

## クリティカルファイル

以下は、実装を開始する上で最も重要なファイルです：

1. **`pyproject.toml`** - プロジェクトの依存関係と設定
2. **`infrastructure/shared/result.py`** - Result型（エラーハンドリングの基盤）
3. **`domain/shared/value_objects.py`** - 共通値オブジェクト（Money等）
4. **`domain/shared/exceptions.py`** - ドメイン例外
5. **`infrastructure/shared/database.py`** - データベース接続管理
6. **`domain/user/models.py`** - User集約（認証の基盤）
7. **`apps/api/main.py`** - FastAPIエントリーポイント

---

## 検証方法

### テストの実行

```bash
# 単体テストのみ（高速）
pytest tests/unit -v

# 統合テストのみ（DB必要）
pytest tests/integration -v

# E2Eテストのみ（フルスタック）
pytest tests/e2e -v

# すべてのテスト + カバレッジ
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

# 特定のモジュールのみ
pytest tests/unit/modules/user -v
```

### 静的解析とフォーマット

```bash
# リンティング
ruff check .

# フォーマット
ruff format .

# 型チェック
mypy .
```

### APIの動作確認

```bash
# ローカルサーバー起動
uvicorn apps.api.main:app --reload

# ヘルスチェック
curl http://localhost:8000/health

# ユーザー登録
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# OpenAPIドキュメント
# http://localhost:8000/docs にアクセス
```

---

## Git戦略

### コミットメッセージのプレフィックス

```
test:      テストの追加・修正
feat:      新機能の実装
refactor:  リファクタリング
fix:       バグ修正
docs:      ドキュメント
chore:     雑務（依存関係の追加など）
```

### TDDサイクルのコミット例

```bash
# Red: テスト作成
git add tests/unit/modules/user/domain/test_models.py
git commit -m "test: Userドメインモデルのテストを追加"

# Green: 実装
git add modules/user/domain/models.py
git commit -m "feat: Userドメインモデルを実装"

# Refactor: リファクタリング
git add modules/user/domain/models.py
git commit -m "refactor: Userドメインモデルの型ヒントを改善"
```

### 各MVPフェーズのタグ付け

```bash
git tag -a v0.1.0 -m "MVP0.1: 基盤構築完了"
git tag -a v0.2.0 -m "MVP0.2: マイルストーン管理完了"
git tag -a v0.3.0 -m "MVP0.3: 位置情報検証完了"
git tag -a v0.4.0 -m "MVP0.4: ペナルティシステム完了"
git tag -a v1.0.0 -m "MVP1: 統合とレポート完了"
```

---

## 重要な原則

1. **TDD**: Red → Green → Refactor のサイクルを厳守
2. **関数型**: 純粋関数を優先、不変データ構造を使用
3. **DDD**: ドメインモデル中心、集約の独立性を保つ
4. **Result型**: エラーハンドリングを明示化
5. **小さく始める**: 過度な抽象化を避け、段階的に拡張

---

## 次のステップ

1. **環境構築**
   ```bash
   cd /Users/taisei/Projects/private/SwitchMe
   uv init
   uv add fastapi uvicorn[standard] pydantic pydantic-settings
   uv add sqlalchemy asyncpg alembic
   uv add python-jose[cryptography] passlib[bcrypt] python-multipart
   uv add python-dotenv structlog
   uv add --dev pytest pytest-asyncio pytest-cov pytest-mock httpx
   uv add --dev ruff mypy
   uv sync
   ```

2. **MVP0.1から順次実装**
   - 各ステップをTDDサイクルで進める
   - 小さく頻繁にコミット
   - 各フェーズ完了時にタグ付け

3. **継続的な改善**
   - テストカバレッジの維持
   - リファクタリング
   - ドキュメントの更新
