# OAuth2 + Google認証実装プラン

## 概要

MVP0.2 Step 3として、OAuth2によるGoogle認証を実装します。認証はGoogle認証のみとし、メールアドレス+パスワードによる登録機能は削除します。

## 目的

- ユーザーがGoogleアカウントで簡単にログインできるようにする
- JWT トークン（アクセストークン + リフレッシュトークン）でセッション管理
- HTTPOnly cookieを使用してセキュアにトークンを管理
- 既存のDDD + FP + TDDのアーキテクチャを維持

## 技術スタック

- **OAuth2ライブラリ**: Authlib >= 1.4.0（プロダクショングレードの実装）
- **HTTPクライアント**: httpx >= 0.28.1（Authlibの依存関係）
- **JWTライブラリ**: PyJWT（既存）
- **トークン管理**: HTTPOnly cookies
- **認証フロー**: Authorization Code Flow with PKCE

## アーキテクチャ設計

### 認証フロー

```
1. ユーザー → GET /api/v1/auth/google/login
2. サーバー → Google OAuth2認証URLへリダイレクト
3. ユーザー → Googleでログイン・承認
4. Google → GET /api/v1/auth/google/callback?code=...
5. サーバー → Googleからユーザー情報取得
6. サーバー → ユーザー情報をDBに保存/更新
7. サーバー → JWTトークン（access + refresh）を生成
8. サーバー → HTTPOnly cookieにトークンをセット
9. サーバー → フロントエンドへリダイレクト
```

### ドメインモデル拡張

**User集約の変更**:
- `hashed_password`フィールドを削除（パスワード認証を廃止）
- `oauth_provider: OAuthProvider`（"google"固定）
- `oauth_user_id: str`（Google User ID）

### レイヤー構造

1. **Domain Layer**: OAuthProvider, User拡張
2. **Infrastructure Layer**: GoogleOAuthClient, JWTTokenManager
3. **Application Layer**: GoogleLoginUseCase, GoogleCallbackUseCase, GetCurrentUserUseCase, LogoutUseCase
4. **API Layer**: auth_router, 認証middleware

## 実装フェーズ（TDDサイクル）

### Phase 1: 依存関係の追加

**タスク**:
- `pyproject.toml`にAuthlib、httpxを追加
- `uv sync`で依存関係をインストール

**ファイル**:
- `pyproject.toml`

### Phase 2: ドメインモデルの拡張

**タスク**:
1. **Red**: OAuthProvider値オブジェクトのテスト作成
2. **Green**: OAuthProvider実装（固定値: "google"）
3. **Red**: User集約の変更テスト（hashed_password削除、oauth情報を必須に）
4. **Green**: User.create()ファクトリメソッドを修正（OAuth情報を受け取る）
5. **Refactor**: 既存テストの修正、HashedPassword関連コードの削除

**ファイル**:
- `domain/user/models.py`
- `tests/unit/domain/user/test_models.py`
- `domain/user/password.py`（削除または非推奨化）

**期待される変更**:
```python
class OAuthProvider(BaseModel):
    model_config = {"frozen": True}
    value: Literal["google"] = "google"

class User(BaseModel):
    id: UserId
    email: Email
    oauth_provider: OAuthProvider
    oauth_user_id: str
    status: UserStatus

    @classmethod
    def create(
        cls,
        email: Email,
        oauth_provider: OAuthProvider,
        oauth_user_id: str
    ) -> "User":
        return cls(
            id=UserId(value=uuid4()),
            email=email,
            oauth_provider=oauth_provider,
            oauth_user_id=oauth_user_id,
            status=UserStatus(value="active")
        )
```

### Phase 3: リポジトリの拡張

**タスク**:
1. **Red**: find_by_oauth()メソッドのテスト作成
2. **Green**: UserRepository Protocolに追加
3. **Green**: InMemoryUserRepository実装
4. **Refactor**: テストの整理

**ファイル**:
- `domain/user/repositories.py`
- `tests/unit/domain/user/test_repositories.py`

**期待される変更**:
```python
class UserRepository(Protocol):
    def find_by_oauth(
        self,
        oauth_provider: OAuthProvider,
        oauth_user_id: str
    ) -> Optional[User]:
        ...
```

### Phase 4: GoogleOAuthClientアダプター実装

**タスク**:
1. **Red**: GoogleOAuthClient Protocolのテスト作成
2. **Green**: Protocol定義（get_authorization_url, get_user_info）
3. **Red**: AuthlibGoogleOAuthClient実装のテスト
4. **Green**: Authlib使用した実装
5. **Green**: MockGoogleOAuthClient（テスト用）実装
6. **Refactor**: エラーハンドリング、Result型での返却

**ファイル**:
- `infrastructure/auth/adapters/oauth_client.py`（新規）
- `tests/unit/infrastructure/auth/test_oauth_client.py`（新規）

**期待される実装**:
```python
from typing import Protocol
from infrastructure.shared.result import Result

class GoogleUserInfo(BaseModel):
    email: str
    google_user_id: str
    name: str

class GoogleOAuthClient(Protocol):
    def get_authorization_url(self, state: str) -> str:
        ...

    def get_user_info(self, code: str) -> Result[GoogleUserInfo, str]:
        ...

class AuthlibGoogleOAuthClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client = OAuth2Client(...)

    def get_authorization_url(self, state: str) -> str:
        return self.client.create_authorization_url(...)

    def get_user_info(self, code: str) -> Result[GoogleUserInfo, str]:
        try:
            token = self.client.fetch_token(...)
            resp = self.client.get("https://www.googleapis.com/oauth2/v2/userinfo")
            user_data = resp.json()
            return Ok(GoogleUserInfo(
                email=user_data["email"],
                google_user_id=user_data["id"],
                name=user_data["name"]
            ))
        except Exception as e:
            return Err(str(e))
```

### Phase 5: JWTTokenManager実装

**タスク**:
1. **Red**: TokenManager Protocolのテスト作成
2. **Green**: Protocol定義（create_access_token, create_refresh_token, verify_token）
3. **Red**: JWTTokenManager実装のテスト
4. **Green**: PyJWTを使用した実装
5. **Refactor**: トークン有効期限の設定、エラーハンドリング

**ファイル**:
- `infrastructure/auth/adapters/token_manager.py`（新規）
- `tests/unit/infrastructure/auth/test_token_manager.py`（新規）

**期待される実装**:
```python
class TokenPayload(BaseModel):
    user_id: str
    email: str
    exp: int

class TokenManager(Protocol):
    def create_access_token(self, user_id: str, email: str) -> str:
        ...

    def create_refresh_token(self, user_id: str) -> str:
        ...

    def verify_token(self, token: str) -> Result[TokenPayload, str]:
        ...

class JWTTokenManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def create_access_token(self, user_id: str, email: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {"user_id": user_id, "email": email, "exp": expire}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Result[TokenPayload, str]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return Ok(TokenPayload(**payload))
        except jwt.ExpiredSignatureError:
            return Err("Token expired")
        except jwt.InvalidTokenError:
            return Err("Invalid token")
```

### Phase 6: 認証ユースケース実装

**タスク**:
1. **Red**: GoogleLoginUseCaseのテスト（authorization URL生成）
2. **Green**: GoogleLoginUseCase実装
3. **Red**: GoogleCallbackUseCaseのテスト（ユーザー作成/更新、トークン生成）
4. **Green**: GoogleCallbackUseCase実装
5. **Red**: GetCurrentUserUseCaseのテスト（トークン検証、ユーザー取得）
6. **Green**: GetCurrentUserUseCase実装
7. **Red**: LogoutUseCaseのテスト（トークン無効化は今回未実装）
8. **Green**: LogoutUseCase実装（現時点ではcookie削除のみ）
9. **Refactor**: エラーハンドリング、Result型の統一

**ファイル**:
- `application/auth/use_cases.py`（新規）
- `tests/unit/application/auth/test_use_cases.py`（新規）

**期待される実装**:
```python
class GoogleLoginUseCase:
    def __init__(self, oauth_client: GoogleOAuthClient):
        self.oauth_client = oauth_client

    def execute(self, state: str) -> str:
        return self.oauth_client.get_authorization_url(state)

class GoogleCallbackUseCase:
    def __init__(
        self,
        oauth_client: GoogleOAuthClient,
        user_repository: UserRepository,
        token_manager: TokenManager
    ):
        self.oauth_client = oauth_client
        self.user_repository = user_repository
        self.token_manager = token_manager

    def execute(self, code: str) -> Result[dict[str, str], str]:
        # 1. Googleからユーザー情報取得
        user_info_result = self.oauth_client.get_user_info(code)
        if user_info_result.is_err():
            return Err(user_info_result.unwrap_err())

        user_info = user_info_result.unwrap()

        # 2. ユーザーをDBから検索または作成
        existing_user = self.user_repository.find_by_oauth(
            OAuthProvider(value="google"),
            user_info.google_user_id
        )

        if existing_user:
            user = existing_user
        else:
            user = User.create(
                email=Email(value=user_info.email),
                oauth_provider=OAuthProvider(value="google"),
                oauth_user_id=user_info.google_user_id
            )
            self.user_repository.save(user)

        # 3. トークン生成
        access_token = self.token_manager.create_access_token(
            str(user.id.value),
            user.email.value
        )
        refresh_token = self.token_manager.create_refresh_token(str(user.id.value))

        return Ok({
            "access_token": access_token,
            "refresh_token": refresh_token
        })

class GetCurrentUserUseCase:
    def __init__(
        self,
        token_manager: TokenManager,
        user_repository: UserRepository
    ):
        self.token_manager = token_manager
        self.user_repository = user_repository

    def execute(self, access_token: str) -> Result[User, str]:
        # 1. トークン検証
        payload_result = self.token_manager.verify_token(access_token)
        if payload_result.is_err():
            return Err(payload_result.unwrap_err())

        payload = payload_result.unwrap()

        # 2. ユーザー取得
        user = self.user_repository.find_by_id(UserId(value=UUID(payload.user_id)))
        if not user:
            return Err("User not found")

        return Ok(user)
```

### Phase 7: 認証APIエンドポイント実装

**タスク**:
1. **Red**: GET /api/v1/auth/google/login エンドポイントのテスト
2. **Green**: auth_routerに実装
3. **Red**: GET /api/v1/auth/google/callback エンドポイントのテスト
4. **Green**: callback実装（cookie設定を含む）
5. **Red**: GET /api/v1/auth/me エンドポイントのテスト
6. **Green**: 現在のユーザー情報取得実装
7. **Red**: POST /api/v1/auth/logout エンドポイントのテスト
8. **Green**: logout実装（cookie削除）
9. **Refactor**: レスポンスモデルの整理

**ファイル**:
- `apps/api/routers/auth_router.py`（新規）
- `apps/api/dependencies.py`（OAuth client、token manager追加）
- `apps/api/main.py`（auth_router登録）
- `tests/integration/test_auth_api.py`（新規）

**期待される実装**:
```python
# apps/api/routers/auth_router.py
from fastapi import APIRouter, Response, Cookie, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.get("/google/login")
def google_login(
    google_login_use_case: GoogleLoginUseCase = Depends(get_google_login_use_case)
):
    state = secrets.token_urlsafe(32)
    authorization_url = google_login_use_case.execute(state)
    return RedirectResponse(url=authorization_url)

@router.get("/google/callback")
def google_callback(
    code: str,
    response: Response,
    google_callback_use_case: GoogleCallbackUseCase = Depends(get_google_callback_use_case)
):
    result = google_callback_use_case.execute(code)

    if result.is_err():
        raise HTTPException(status_code=400, detail=result.unwrap_err())

    tokens = result.unwrap()

    # HTTPOnly cookieにトークンを設定
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,  # HTTPS必須
        samesite="lax",
        max_age=30 * 60  # 30分
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7日
    )

    return RedirectResponse(url="/dashboard")

@router.get("/me")
def get_current_user(
    access_token: str = Cookie(None),
    get_current_user_use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = get_current_user_use_case.execute(access_token)

    if result.is_err():
        raise HTTPException(status_code=401, detail=result.unwrap_err())

    user = result.unwrap()
    return {
        "id": str(user.id.value),
        "email": user.email.value,
        "status": user.status.value
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
```

### Phase 8: 認証middleware実装

**タスク**:
1. **Red**: 認証が必要なエンドポイントでのテスト（未認証時403）
2. **Green**: get_current_user依存関数の実装
3. **Refactor**: エラーメッセージの統一

**ファイル**:
- `apps/api/dependencies.py`

**期待される実装**:
```python
# apps/api/dependencies.py
from fastapi import Cookie, HTTPException, Depends
from domain.user.models import User

def get_current_user(
    access_token: str = Cookie(None),
    get_current_user_use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case)
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = get_current_user_use_case.execute(access_token)

    if result.is_err():
        raise HTTPException(status_code=401, detail=result.unwrap_err())

    return result.unwrap()
```

### Phase 9: MilestoneAPIに認証を追加

**タスク**:
1. **Red**: Milestone作成APIに認証が必要なテスト
2. **Green**: エンドポイントにcurrent_user依存を追加
3. **Refactor**: 既存テストの修正（認証トークン付き）

**ファイル**:
- `apps/api/routers/milestone_router.py`（未実装の場合は新規作成）
- `tests/integration/test_milestone_api.py`

**期待される変更**:
```python
@router.post("/api/v1/milestones")
def create_milestone(
    request: CreateMilestoneRequest,
    current_user: User = Depends(get_current_user),
    create_milestone_use_case: CreateMilestoneUseCase = Depends(...)
):
    result = create_milestone_use_case.execute(
        user_id=current_user.id,
        title=request.title,
        ...
    )
    ...
```

### Phase 10: 統合テストとリファクタリング

**タスク**:
1. 全テストの実行（pytest）
2. カバレッジ確認（95%以上を目標）
3. Ruffでのlint + format
4. 開発日記の更新
5. コミット作成

**ファイル**:
- 全ファイル

## 重要ファイル一覧

### 新規作成ファイル

1. `infrastructure/auth/adapters/oauth_client.py` - Google OAuth2クライアント
2. `infrastructure/auth/adapters/token_manager.py` - JWTトークンマネージャー
3. `application/auth/use_cases.py` - 認証ユースケース
4. `apps/api/routers/auth_router.py` - 認証APIルーター
5. `tests/unit/infrastructure/auth/test_oauth_client.py`
6. `tests/unit/infrastructure/auth/test_token_manager.py`
7. `tests/unit/application/auth/test_use_cases.py`
8. `tests/integration/test_auth_api.py`

### 変更ファイル

1. `pyproject.toml` - 依存関係追加
2. `domain/user/models.py` - User集約の変更（hashed_password削除、oauth情報必須化）
3. `domain/user/repositories.py` - find_by_oauth追加
4. `apps/api/dependencies.py` - OAuth client、token manager、get_current_user追加
5. `apps/api/main.py` - auth_router登録、user_router削除
6. `tests/unit/domain/user/test_models.py` - User変更のテスト
7. `tests/unit/domain/user/test_repositories.py` - find_by_oauthのテスト

### 削除ファイル

1. `application/user/use_cases.py` - RegisterUserUseCase削除
2. `infrastructure/user/adapters/password_hasher.py` - パスワードハッシャー削除
3. `apps/api/routers/user_router.py` - ユーザー登録エンドポイント削除
4. `tests/unit/application/user/test_use_cases.py` - RegisterUserUseCaseのテスト削除
5. `tests/unit/infrastructure/user/test_password_hasher.py` - パスワードハッシャーのテスト削除

## テスト戦略

### 単体テスト

- **Domain Layer**: 値オブジェクト、集約の振る舞いテスト
- **Infrastructure Layer**: Adapterのモック実装テスト
- **Application Layer**: ユースケースのテスト（モックリポジトリ使用）

### 統合テスト

- **API Layer**: FastAPI TestClientを使用したE2Eテスト
- **認証フロー**: ログイン→callback→ユーザー情報取得→ログアウト

### カバレッジ目標

- 95%以上（既存：98%）

## 検証方法

### 手動テスト

1. サーバー起動: `uvicorn apps.api.main:app --reload`
2. ブラウザで `/api/v1/auth/google/login` にアクセス
3. Googleログイン画面が表示されることを確認
4. ログイン後、callbackが成功することを確認
5. `/api/v1/auth/me` でユーザー情報が取得できることを確認
6. `/api/v1/auth/logout` でログアウトできることを確認

### 自動テスト

```bash
# 全テスト実行
pytest tests/

# カバレッジ付き
pytest --cov=domain --cov=infrastructure --cov=application --cov=apps tests/

# リンティング
ruff check .

# フォーマット
ruff format .
```

### 環境変数

実装時に必要な環境変数：

```bash
GOOGLE_CLIENT_ID=<Google Cloud ConsoleのクライアントID>
GOOGLE_CLIENT_SECRET=<Google Cloud Consoleのクライアントシークレット>
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
JWT_SECRET_KEY=<ランダムな秘密鍵>
```

## セキュリティ考慮事項

1. **HTTPOnly Cookie**: XSS攻撃からトークンを保護
2. **Secure Flag**: HTTPS接続でのみcookie送信
3. **SameSite属性**: CSRF攻撃を防止
4. **State Parameter**: OAuth2フローでのCSRF対策
5. **トークン有効期限**: アクセストークン30分、リフレッシュトークン7日
6. **環境変数**: 機密情報を環境変数で管理

## 既存機能への影響

- **User集約**: hashed_passwordフィールドを削除し、oauth情報を必須化（既存テストは大幅修正）
- **User登録API**: `/api/v1/users/register` エンドポイントは削除（パスワード認証を廃止）
- **RegisterUserUseCase**: 削除（不要）
- **BcryptPasswordHasher**: 削除（不要）
- **Milestone API**: 認証チェックが追加されるため、テストに認証トークンが必要

## 実装時の注意点

1. **TDDサイクルを厳守**: Red→Green→Refactorの順で進める
2. **小さなコミット**: 各フェーズ完了時にコミット
3. **Result型の活用**: エラーハンドリングはResult型で統一
4. **テストカバレッジ**: 95%以上を維持
5. **型安全性**: Pydanticモデルを活用した厳密な型定義

## 次のステップ（このプラン外）

- リフレッシュトークンによるアクセストークン更新機能
- トークンのブラックリスト機能（ログアウト時の無効化）
- 他のOAuthプロバイダー対応（GitHub、Facebook等）
