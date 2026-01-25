# MVP0.3 位置情報検証機能 実装プラン

## 実装戦略

### 戦略的判断：PostgreSQL永続化を先に実施

**理由**：
1. 位置情報検証で新しい集約（Verification、AchievementRecord）が必要
2. 最初からPostgreSQLで実装する方が、後で3つの集約を同時移行するより効率的
3. PostgreSQL基盤は70%完成済み（Docker、Alembic、ORM完備）
4. 移行難易度: 4/10（リポジトリ抽象化済み、テスト全通過を維持しながら移行可能）

**前提条件**：
- 現在のリポジトリは同期実装だが、PostgreSQLでは非同期が望ましい
- Phase 0でリポジトリインターフェースを非同期化する

---

## フェーズ1: PostgreSQL永続化（Phase 0-6）

### Phase 0: リポジトリインターフェースの非同期化

**目標**：全リポジトリとユースケースを非同期化し、FastAPIの非同期機能を活用

#### 重要な設計判断

**現状**：
- リポジトリインターフェース: 同期（`def save()`, `def find_by_id()`）
- ユースケース: 同期（`def execute()`）
- APIルーター: 同期

**問題**：
- PostgreSQLは非同期操作（asyncpg）が推奨
- FastAPIは非同期フレームワークで、同期操作はブロッキング
- 同期ラッパーを使うと非同期の恩恵を受けられない

**解決策**：
- リポジトリProtocolを非同期化（`async def`）
- InMemoryリポジトリを非同期化
- ユースケースを非同期化
- APIエンドポイントを非同期化

#### TDDサイクル

**RED: テスト修正**
- ファイル: `tests/unit/application/milestone/test_use_cases.py`
- 変更: すべてのテスト関数を `async def` に変更、`await` 追加

**GREEN: 実装**

1. **リポジトリインターフェース変更**
   - ファイル: `domain/user/repositories.py`, `domain/milestone/repositories.py`
   - 変更内容:
     ```python
     class UserRepository(Protocol):
         async def save(self, user: User) -> Result[None, Exception]: ...
         async def find_by_id(self, user_id: UserId) -> Result[User, EntityNotFoundError]: ...
         async def find_by_email(self, email: Email) -> Result[User, EntityNotFoundError]: ...
         async def delete(self, user_id: UserId) -> Result[None, Exception]: ...

     class MilestoneRepository(Protocol):
         async def save(self, milestone: Milestone) -> Result[None, Exception]: ...
         async def find_by_id(self, milestone_id: MilestoneId) -> Result[Milestone, EntityNotFoundError]: ...
         async def find_by_user_id(self, user_id: UserId) -> Result[list[Milestone], Exception]: ...
         async def delete(self, milestone_id: MilestoneId) -> Result[None, Exception]: ...
     ```

2. **InMemoryリポジトリ非同期化**
   - ファイル: `domain/user/repositories.py`, `domain/milestone/repositories.py`（同じファイル内）
   - 変更: すべてのメソッドに `async` キーワード追加
   ```python
   class InMemoryMilestoneRepository:
       async def save(self, milestone: Milestone) -> Result[None, Exception]:
           self._milestones[str(milestone.id.value)] = milestone
           return Ok(None)

       async def find_by_id(self, milestone_id: MilestoneId) -> Result[Milestone, EntityNotFoundError]:
           # ...
   ```

3. **ユースケース非同期化**
   - ファイル: `application/milestone/use_cases.py`, `application/user/use_cases.py`, `application/auth/use_cases.py`
   - 変更: `execute()` メソッドを `async def` に変更、リポジトリ呼び出しに `await` 追加
   ```python
   class CreateMilestoneUseCase:
       async def execute(self, input_data: CreateMilestoneInput) -> Result[Milestone, Exception]:
           milestone = Milestone.create(...)
           result = await self._milestone_repository.save(milestone)
           # ...
   ```

4. **APIルーター非同期化**
   - ファイル: `apps/api/routers/milestone_router.py`, `apps/api/routers/auth_router.py`
   - 変更: エンドポイントを `async def` に変更、ユースケース呼び出しに `await` 追加
   ```python
   @router.post("", status_code=201)
   async def create_milestone(
       request: CreateMilestoneRequest,
       current_user = Depends(get_current_user),
       milestone_repository = Depends(get_milestone_repository),
   ):
       use_case = CreateMilestoneUseCase(milestone_repository)
       result = await use_case.execute(...)
       # ...
   ```

**REFACTOR**:
```bash
ruff check . --fix
ruff format .
pytest tests/ -v
```

**成功基準**:
- 全113テスト成功（非同期化後も動作）
- カバレッジ90%以上維持

**成果物**:
- 修正: `domain/user/repositories.py`
- 修正: `domain/milestone/repositories.py`
- 修正: `application/milestone/use_cases.py`
- 修正: `application/user/use_cases.py`
- 修正: `application/auth/use_cases.py`
- 修正: `apps/api/routers/milestone_router.py`
- 修正: `apps/api/routers/auth_router.py`
- 修正: `tests/unit/application/milestone/test_use_cases.py`
- 修正: `tests/unit/application/auth/test_use_cases.py`

---

### Phase 1: PostgreSQL User Repository実装

**目標**: UserリポジトリをPostgreSQLで実装

#### TDDサイクル

**RED: テスト作成**
- ファイル: `tests/integration/test_user_repository.py`
- テスト内容:
  ```python
  async def test_ユーザーを保存して取得できること(db_session):
      # Given
      repository = PostgresUserRepository(db_session)
      user = User.create(...)

      # When
      await repository.save(user)
      result = await repository.find_by_id(user.id)

      # Then
      assert result.is_ok()
      assert result.unwrap().email == user.email

  async def test_メールアドレスでユーザーを検索できること(db_session):
  async def test_存在しないユーザーはEntityNotFoundErrorを返すこと(db_session):
  async def test_ユーザーを削除できること(db_session):
  ```

**GREEN: 実装**
- ファイル: `infrastructure/user/persistence/repository.py`
- 実装内容:
  ```python
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy import select
  from infrastructure.shared.models import UserModel

  class PostgresUserRepository:
      def __init__(self, session: AsyncSession):
          self._session = session

      async def save(self, user: User) -> Result[None, Exception]:
          try:
              # ドメインモデル → ORMモデル変換
              user_model = user_to_orm(user)

              # 既存チェック
              stmt = select(UserModel).where(UserModel.id == user_model.id)
              result = await self._session.execute(stmt)
              existing = result.scalar_one_or_none()

              if existing:
                  # UPDATE
                  existing.email = user_model.email
                  existing.status = user_model.status
                  existing.last_login_at = user_model.last_login_at
                  existing.updated_at = datetime.utcnow()
              else:
                  # INSERT
                  self._session.add(user_model)

              await self._session.commit()
              return Ok(None)
          except Exception as e:
              await self._session.rollback()
              return Err(e)

      async def find_by_id(self, user_id: UserId) -> Result[User, EntityNotFoundError]:
          stmt = select(UserModel).where(UserModel.id == user_id.value)
          result = await self._session.execute(stmt)
          model = result.scalar_one_or_none()

          if model is None:
              return Err(EntityNotFoundError("User", str(user_id.value)))

          return Ok(orm_to_user(model))
  ```

- マッパー: `infrastructure/user/persistence/mappers.py`
  ```python
  def user_to_orm(user: User) -> UserModel:
      """ドメインモデル → ORMモデル"""
      return UserModel(
          id=user.id.value,
          email=user.email.value,
          oauth_provider=user.oauth_provider,
          oauth_user_id=user.oauth_user_id,
          status=user.status,
          last_login_at=user.last_login_at,
          created_at=user.created_at,
          updated_at=user.updated_at,
      )

  def orm_to_user(model: UserModel) -> User:
      """ORMモデル → ドメインモデル"""
      return User(
          id=UserId(value=model.id),
          email=Email(value=model.email),
          oauth_provider=model.oauth_provider,
          oauth_user_id=model.oauth_user_id,
          status=model.status,
          last_login_at=model.last_login_at,
          created_at=model.created_at,
          updated_at=model.updated_at,
      )
  ```

**REFACTOR**:
```bash
ruff check infrastructure/user/persistence/ --fix
ruff format infrastructure/user/persistence/
pytest tests/integration/test_user_repository.py --cov
```

**成果物**:
- `infrastructure/user/persistence/repository.py`
- `infrastructure/user/persistence/mappers.py`
- `infrastructure/user/persistence/__init__.py`
- `tests/integration/test_user_repository.py`

---

### Phase 2: PostgreSQL Milestone Repository実装

**目標**: MilestoneリポジトリをPostgreSQLで実装

#### TDDサイクル

**RED: テスト作成**
- ファイル: `tests/integration/test_milestone_repository.py`
- テスト内容:
  ```python
  async def test_マイルストーンを保存して取得できること(db_session):
  async def test_ユーザーIDでマイルストーンを検索できること(db_session):
  async def test_マイルストーンを更新できること(db_session):
  async def test_マイルストーンを削除できること(db_session):
  ```

**GREEN: 実装**
- ファイル: `infrastructure/milestone/persistence/repository.py`
- マッパー: `infrastructure/milestone/persistence/mappers.py`
- 実装ポイント:
  - DeadlineInfo: `deadline_date`, `deadline_time`, `timezone` を3カラムに展開
  - VerificationCriteria: `verification_type`, `verification_conditions` (JSON), `verification_threshold`
  - PenaltyInfo: `penalty_amount`, `penalty_currency`, `penalty_description`（Money → int + str）

**マッパー例**:
```python
def milestone_to_orm(milestone: Milestone) -> MilestoneModel:
    """ドメインモデル → ORMモデル"""
    return MilestoneModel(
        id=milestone.id.value,
        user_id=milestone.user_id.value,
        title=milestone.title.value,
        # DeadlineInfo展開
        deadline_date=milestone.deadline.deadline_date.isoformat(),
        deadline_time=milestone.deadline.deadline_time.isoformat(),
        timezone=milestone.deadline.timezone,
        # VerificationCriteria展開
        verification_type=milestone.verification_criteria.type,
        verification_conditions=milestone.verification_criteria.conditions,
        verification_threshold=milestone.verification_criteria.threshold,
        # PenaltyInfo展開
        penalty_amount=milestone.penalty.amount.amount,
        penalty_currency=milestone.penalty.amount.currency,
        penalty_description=milestone.penalty.description,
        status=milestone.status,
    )

def orm_to_milestone(model: MilestoneModel) -> Milestone:
    """ORMモデル → ドメインモデル"""
    return Milestone(
        id=MilestoneId(value=model.id),
        user_id=UserId(value=model.user_id),
        title=Title(value=model.title),
        deadline=DeadlineInfo(
            deadline_date=date.fromisoformat(model.deadline_date),
            deadline_time=time.fromisoformat(model.deadline_time),
            timezone=model.timezone,
        ),
        verification_criteria=VerificationCriteria(
            type=model.verification_type,
            conditions=model.verification_conditions,
            threshold=model.verification_threshold,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=model.penalty_amount, currency=model.penalty_currency),
            description=model.penalty_description,
        ),
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
```

**成果物**:
- `infrastructure/milestone/persistence/repository.py`
- `infrastructure/milestone/persistence/mappers.py`
- `infrastructure/milestone/persistence/__init__.py`
- `tests/integration/test_milestone_repository.py`

---

### Phase 3: 依存性注入の切り替え

**目標**: InMemoryリポジトリからPostgreSQLリポジトリへの切り替え

**実装**:
- ファイル: `apps/api/dependencies.py`
- 変更内容:
  ```python
  from infrastructure.user.persistence.repository import PostgresUserRepository
  from infrastructure.milestone.persistence.repository import PostgresMilestoneRepository

  async def get_user_repository(session: AsyncSession = Depends(get_session)):
      return PostgresUserRepository(session)

  async def get_milestone_repository(session: AsyncSession = Depends(get_session)):
      return PostgresMilestoneRepository(session)
  ```

**成果物**:
- 修正: `apps/api/dependencies.py`

---

### Phase 4: テスト環境のセットアップ

**目標**: PostgreSQL使用時のテストfixtureを作成

**実装**:
- ファイル: `tests/conftest.py`
- 実装内容:
  ```python
  import pytest
  from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
  from infrastructure.shared.database import get_database_url
  from infrastructure.shared.models import Base

  @pytest.fixture(scope="session")
  async def engine():
      """テスト用エンジン"""
      test_db_url = get_database_url().replace("/switchme", "/switchme_test")
      engine = create_async_engine(test_db_url, echo=False)

      # テーブル作成
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.create_all)

      yield engine

      # テーブル削除
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.drop_all)

      await engine.dispose()

  @pytest.fixture
  async def db_session(engine):
      """各テストで独立したセッション"""
      from sqlalchemy.orm import sessionmaker

      async_session = sessionmaker(
          engine, class_=AsyncSession, expire_on_commit=False
      )

      async with async_session() as session:
          async with session.begin():
              yield session
              await session.rollback()
  ```

**既存テストの修正**:
- `tests/integration/test_milestone_api.py`: fixtureを活用、DBクリア処理削除

**成果物**:
- `tests/conftest.py`
- 修正: `tests/integration/test_milestone_api.py`

---

### Phase 5: 統合テスト実行

**検証手順**:
```bash
# 1. PostgreSQL起動
docker-compose up -d

# 2. マイグレーション実行
alembic upgrade head

# 3. テストDB作成
createdb -h localhost -U switchme_user switchme_test

# 4. 統合テスト実行
pytest tests/integration/ -v

# 5. E2Eテスト実行（全体）
pytest tests/ -v

# 6. カバレッジ確認
pytest tests/ --cov=. --cov-report=term-missing
```

**成功基準**:
- 全113テスト成功
- カバレッジ90%以上維持

---

### Phase 6: InMemoryリポジトリの保持（テスト用）

**目標**: 単体テスト用にInMemoryリポジトリを保持

**実装**:
- InMemoryリポジトリを削除せず、ドメイン層に残す（テスト用として活用可能）
- 単体テスト（`tests/unit/`）では引き続きInMemoryを使用
- 統合テスト（`tests/integration/`）ではPostgreSQLを使用

**ファイル配置**:
```
domain/
├── user/
│   └── repositories.py  # UserRepository Protocol + InMemoryUserRepository
├── milestone/
│   └── repositories.py  # MilestoneRepository Protocol + InMemoryMilestoneRepository
```

**成果物**: なし（既存構造を維持）

---

## フェーズ2: 位置情報検証機能（Phase 7-12）

### Phase 7: Verificationドメインモデルの実装

**目標**: 位置情報検証のドメインモデルを実装

#### TDDサイクル

**RED: テスト作成**
- ファイル: `tests/unit/domain/verification/test_models.py`
- テスト内容:
  ```python
  def test_位置情報値オブジェクトが作成できること():
  def test_無効な緯度経度は拒否されること():
  def test_検証を開始できること():
  def test_位置情報データを記録できること():
  def test_検証を完了できること():
  ```

**GREEN: 実装**
- ファイル: `domain/verification/models.py`
- 実装内容:
  ```python
  from pydantic import BaseModel, Field
  from uuid import UUID, uuid4
  from datetime import datetime, timezone
  from typing import Literal, Any

  class Location(BaseModel):
      """位置情報（値オブジェクト）"""
      model_config = {"frozen": True}
      latitude: float = Field(..., ge=-90, le=90)
      longitude: float = Field(..., ge=-180, le=180)

  class Distance(BaseModel):
      """距離（値オブジェクト）"""
      model_config = {"frozen": True}
      meters: float = Field(..., ge=0)

  class VerificationResult(BaseModel):
      """検証結果（値オブジェクト）"""
      model_config = {"frozen": True}
      success: bool
      score: float = Field(..., ge=0, le=1)
      confidence: float = Field(..., ge=0, le=1)
      evidence: dict[str, Any]

  class SensorData(BaseModel):
      """センサーデータ（エンティティ）"""
      id: UUID = Field(default_factory=uuid4)
      location: Location
      timestamp: datetime
      accuracy: float | None = None

  VerificationStatus = Literal["pending", "in_progress", "completed", "failed"]

  class Verification(BaseModel):
      """検証プロセス（集約ルート）"""
      model_config = {"frozen": True}

      id: UUID
      milestone_id: UUID
      user_id: UUID
      status: VerificationStatus
      sensor_data: list[SensorData] = Field(default_factory=list)
      result: VerificationResult | None = None
      started_at: datetime
      completed_at: datetime | None = None

      @classmethod
      def create(cls, milestone_id: UUID, user_id: UUID) -> "Verification":
          return cls(
              id=uuid4(),
              milestone_id=milestone_id,
              user_id=user_id,
              status="pending",
              started_at=datetime.now(timezone.utc),
          )

      def submit_location(self, location: Location, accuracy: float | None = None) -> "Verification":
          sensor = SensorData(location=location, timestamp=datetime.now(timezone.utc), accuracy=accuracy)
          return self.model_copy(update={"sensor_data": [*self.sensor_data, sensor], "status": "in_progress"})

      def complete(self, result: VerificationResult) -> "Verification":
          return self.model_copy(update={"result": result, "status": "completed", "completed_at": datetime.now(timezone.utc)})

      def fail(self, reason: str) -> "Verification":
          result = VerificationResult(success=False, score=0.0, confidence=1.0, evidence={"reason": reason})
          return self.model_copy(update={"result": result, "status": "failed", "completed_at": datetime.now(timezone.utc)})
  ```

**成果物**:
- `domain/verification/models.py`
- `domain/verification/__init__.py`
- `tests/unit/domain/verification/test_models.py`

---

### Phase 8: GPS検証サービスの実装

**目標**: Haversine公式による距離計算とGPS検証

#### TDDサイクル

**RED: テスト作成**
- ファイル: `tests/unit/domain/verification/test_services.py`
- テスト内容:
  ```python
  def test_Haversine公式で距離を計算できること():
      tokyo = Location(latitude=35.6812, longitude=139.7671)
      shinjuku = Location(latitude=35.6896, longitude=139.7006)
      distance = GPSVerificationService.calculate_distance(tokyo, shinjuku)
      assert 6000 < distance.meters < 7000  # 約6.5km

  def test_位置情報検証が成功すること():
  def test_位置情報検証が失敗すること():
  ```

**GREEN: 実装**
- ファイル: `domain/verification/services.py`
- 実装内容:
  ```python
  import math

  class GPSVerificationService:
      """GPS検証ドメインサービス"""

      EARTH_RADIUS_METERS = 6371000

      @staticmethod
      def calculate_distance(loc1: Location, loc2: Location) -> Distance:
          """Haversine公式で2点間の距離を計算"""
          lat1 = math.radians(loc1.latitude)
          lat2 = math.radians(loc2.latitude)
          delta_lat = math.radians(loc2.latitude - loc1.latitude)
          delta_lon = math.radians(loc2.longitude - loc1.longitude)

          a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
          c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
          meters = GPSVerificationService.EARTH_RADIUS_METERS * c

          return Distance(meters=meters)

      @staticmethod
      def verify(current_location: Location, criteria: VerificationCriteria) -> VerificationResult:
          """位置情報を検証"""
          target = Location(latitude=criteria.conditions["lat"], longitude=criteria.conditions["lon"])
          distance = GPSVerificationService.calculate_distance(current_location, target)
          success = distance.meters <= criteria.threshold

          # スコア計算（閾値内なら0.5-1.0、超えたら0.0-0.5）
          if distance.meters <= criteria.threshold:
              score = 1.0 - (distance.meters / criteria.threshold) * 0.5
          else:
              score = max(0.0, 0.5 - (distance.meters - criteria.threshold) / criteria.threshold * 0.5)

          return VerificationResult(
              success=success,
              score=score,
              confidence=1.0,
              evidence={
                  "distance_meters": distance.meters,
                  "threshold_meters": criteria.threshold,
                  "target": {"lat": target.latitude, "lon": target.longitude},
                  "current": {"lat": current_location.latitude, "lon": current_location.longitude},
              },
          )
  ```

**成果物**:
- `domain/verification/services.py`
- `tests/unit/domain/verification/test_services.py`

---

### Phase 9: Verificationリポジトリの実装

**目標**: VerificationとSensorDataをPostgreSQLで永続化

#### Alembicマイグレーション

```bash
alembic revision --autogenerate -m "Add verifications and sensor_data tables"
```

**テーブル定義**:
- `infrastructure/shared/models.py` に追加:
  ```python
  class VerificationModel(Base):
      __tablename__ = "verifications"

      id = Column(UUID(as_uuid=True), primary_key=True)
      milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False, index=True)
      user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
      status = Column(String, nullable=False)
      result_success = Column(Boolean, nullable=True)
      result_score = Column(Float, nullable=True)
      result_confidence = Column(Float, nullable=True)
      result_evidence = Column(JSON, nullable=True)
      started_at = Column(DateTime(timezone=True), nullable=False)
      completed_at = Column(DateTime(timezone=True), nullable=True)
      created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
      updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

      sensor_data = relationship("SensorDataModel", back_populates="verification", cascade="all, delete-orphan")

  class SensorDataModel(Base):
      __tablename__ = "sensor_data"

      id = Column(UUID(as_uuid=True), primary_key=True)
      verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id", ondelete="CASCADE"), nullable=False, index=True)
      latitude = Column(Float, nullable=False)
      longitude = Column(Float, nullable=False)
      accuracy = Column(Float, nullable=True)
      timestamp = Column(DateTime(timezone=True), nullable=False)
      created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

      verification = relationship("VerificationModel", back_populates="sensor_data")
  ```

#### TDDサイクル

**RED: テスト作成**
- ファイル: `tests/integration/test_verification_repository.py`

**GREEN: 実装**
- Protocol: `domain/verification/repositories.py`
- PostgreSQL実装: `infrastructure/verification/persistence/repository.py`
- マッパー: `infrastructure/verification/persistence/mappers.py`

**成果物**:
- `domain/verification/repositories.py`
- `infrastructure/verification/persistence/repository.py`
- `infrastructure/verification/persistence/mappers.py`
- `tests/integration/test_verification_repository.py`
- `alembic/versions/XXXX_add_verifications_and_sensor_data_tables.py`

---

### Phase 10: AchievementRecordドメインモデルの実装

**目標**: 達成記録のドメインモデルとリポジトリを実装

#### ドメインモデル

- ファイル: `domain/achievement/models.py`
- 実装内容:
  ```python
  class AchievementStatus(BaseModel):
      model_config = {"frozen": True}
      achieved: bool
      reason: str = Field(default="")
      score: float = Field(..., ge=0, le=1)

  class Evidence(BaseModel):
      model_config = {"frozen": True}
      type: str
      references: list[UUID] = Field(default_factory=list)
      metadata: dict[str, Any] = Field(default_factory=dict)

  class AchievementRecord(BaseModel):
      model_config = {"frozen": True}
      id: UUID
      milestone_id: UUID
      user_id: UUID
      status: AchievementStatus
      evidence: Evidence
      recorded_at: datetime

      @classmethod
      def record_achievement(cls, milestone_id: UUID, user_id: UUID, verification_id: UUID, score: float) -> "AchievementRecord":
          return cls(
              id=uuid4(),
              milestone_id=milestone_id,
              user_id=user_id,
              status=AchievementStatus(achieved=True, score=score, reason="Verified by GPS"),
              evidence=Evidence(type="verification", references=[verification_id]),
              recorded_at=datetime.now(timezone.utc),
          )

      @classmethod
      def record_failure(cls, milestone_id: UUID, user_id: UUID, reason: str) -> "AchievementRecord":
          return cls(
              id=uuid4(),
              milestone_id=milestone_id,
              user_id=user_id,
              status=AchievementStatus(achieved=False, score=0.0, reason=reason),
              evidence=Evidence(type="manual", metadata={"reason": reason}),
              recorded_at=datetime.now(timezone.utc),
          )
  ```

#### Alembicマイグレーション

```bash
alembic revision --autogenerate -m "Add achievement_records table"
```

**成果物**:
- `domain/achievement/models.py`
- `domain/achievement/repositories.py`
- `infrastructure/achievement/persistence/repository.py`
- `tests/unit/domain/achievement/test_models.py`
- `alembic/versions/XXXX_add_achievement_records_table.py`

---

### Phase 11: 検証ユースケースの実装

**目標**: 位置情報検証のユースケースを実装

#### ユースケース

1. **StartVerificationUseCase**: 検証開始
2. **SubmitLocationUseCase**: 位置情報送信
3. **CompleteVerificationUseCase**: 検証完了と達成記録作成

**実装例（CompleteVerificationUseCase）**:
```python
class CompleteVerificationUseCase:
    def __init__(
        self,
        milestone_repository: MilestoneRepository,
        verification_repository: VerificationRepository,
        achievement_repository: AchievementRepository,
    ):
        self._milestone_repository = milestone_repository
        self._verification_repository = verification_repository
        self._achievement_repository = achievement_repository

    async def execute(self, input_data: CompleteVerificationInput) -> Result[tuple[Verification, AchievementRecord], Exception]:
        # 1. 検証取得
        verification_result = await self._verification_repository.find_by_id(UUID(input_data.verification_id))
        if verification_result.is_err():
            return Err(Exception("Verification not found"))

        verification = verification_result.unwrap()

        # 2. 認可チェック
        if verification.user_id != UUID(input_data.user_id):
            return Err(UnauthorizedError("Not authorized"))

        # 3. マイルストーン取得
        milestone_result = await self._milestone_repository.find_by_id(MilestoneId(value=verification.milestone_id))
        if milestone_result.is_err():
            return Err(Exception("Milestone not found"))

        milestone = milestone_result.unwrap()

        # 4. GPS検証
        if len(verification.sensor_data) == 0:
            failed_verification = verification.fail("No sensor data")
            await self._verification_repository.save(failed_verification)
            achievement = AchievementRecord.record_failure(milestone.id.value, verification.user_id, "No sensor data")
            await self._achievement_repository.save(achievement)
            return Ok((failed_verification, achievement))

        last_sensor = verification.sensor_data[-1]
        result = GPSVerificationService.verify(last_sensor.location, milestone.verification_criteria)

        # 5. 検証完了
        completed_verification = verification.complete(result)
        await self._verification_repository.save(completed_verification)

        # 6. 達成記録
        if result.success:
            achievement = AchievementRecord.record_achievement(milestone.id.value, verification.user_id, verification.id, result.score)
        else:
            achievement = AchievementRecord.record_failure(milestone.id.value, verification.user_id, f"Distance: {result.evidence['distance_meters']}m")

        await self._achievement_repository.save(achievement)

        # 7. マイルストーンステータス更新
        updated_milestone = milestone.complete() if result.success else milestone.fail()
        await self._milestone_repository.save(updated_milestone)

        return Ok((completed_verification, achievement))
```

**成果物**:
- `application/verification/use_cases.py`
- `tests/unit/application/verification/test_use_cases.py`

---

### Phase 12: 位置情報検証API実装

**目標**: 位置情報検証のAPIエンドポイントを実装

#### エンドポイント

1. `POST /api/v1/verifications` - 検証開始
2. `POST /api/v1/verifications/{verification_id}/location` - 位置情報送信
3. `POST /api/v1/verifications/{verification_id}/complete` - 検証完了

**実装**:
- ファイル: `apps/api/routers/verification_router.py`
- 依存性注入: `apps/api/dependencies.py` に追加
- ルーター登録: `apps/api/main.py` に追加

**E2Eテスト**:
- ファイル: `tests/integration/test_verification_api.py`
- テスト内容:
  ```python
  async def test_検証開始から完了までのフロー():
      # Given: 認証済みユーザーとマイルストーン
      # When: 検証開始 → 位置情報送信 → 検証完了
      # Then: 成功、達成記録作成

  async def test_位置情報が遠すぎる場合は失敗すること():
  ```

**成果物**:
- `apps/api/routers/verification_router.py`
- `tests/integration/test_verification_api.py`
- 修正: `apps/api/dependencies.py`
- 修正: `apps/api/main.py`

---

## データベーススキーマ

### マイグレーション一覧

```bash
# 既存
8dcce90f4112_initial_schema_users_and_milestones_.py

# 新規
XXXX_add_verifications_and_sensor_data_tables.py
XXXX_add_achievement_records_table.py
```

### ER図

```
users
  ├── milestones (FK: user_id)
  ├── verifications (FK: user_id)
  └── achievement_records (FK: user_id)

milestones
  ├── verifications (FK: milestone_id)
  └── achievement_records (FK: milestone_id)

verifications
  └── sensor_data (FK: verification_id)
```

---

## テスト戦略

### テストレベル

1. **単体テスト（`tests/unit/`）**: InMemoryリポジトリ使用
   - ドメインモデル
   - ユースケース
   - GPS検証サービス

2. **統合テスト（`tests/integration/`）**: PostgreSQL使用
   - リポジトリ（CRUD操作）
   - マッパー（ドメイン↔ORM変換）

3. **E2Eテスト（`tests/integration/test_*_api.py`）**: Full Stack
   - APIエンドポイント
   - 認証フロー
   - エンドツーエンドビジネスフロー

### カバレッジ目標

- 全体: 90%以上
- ドメイン層: 95%以上
- アプリケーション層: 90%以上

---

## 完了基準

### フェーズ1（PostgreSQL永続化）完了基準

1. 既存の113テスト全通過
2. 統合テスト追加（User, Milestoneリポジトリ）
3. カバレッジ90%以上維持
4. Docker ComposeでPostgreSQL起動可能
5. Alembicマイグレーション成功

### フェーズ2（位置情報検証）完了基準

1. 全テスト通過（単体 + 統合 + E2E）
2. GPS距離計算の精度テスト（誤差±10m以内）
3. 位置情報検証APIが動作
4. 達成記録が正しく保存される
5. カバレッジ90%以上

### 全体の完了基準

1. PostgreSQL永続化完了
2. 位置情報検証機能完全実装
3. E2Eテストでフルフロー確認
   - ユーザー登録 → マイルストーン作成 → 検証開始 → 位置情報送信 → 検証完了 → 達成記録確認
4. すべてのテスト通過

---

## 検証手順

### 開発環境セットアップ

```bash
# 1. PostgreSQL起動
docker-compose up -d

# 2. マイグレーション実行
alembic upgrade head

# 3. テストDB作成
createdb -h localhost -U switchme_user switchme_test

# 4. テスト実行
pytest tests/ -v --cov=. --cov-report=term-missing
```

### E2Eフローテスト

```bash
# APIサーバー起動
uvicorn apps.api.main:app --reload

# 1. ユーザー登録（Google OAuth2）
curl -X GET http://localhost:8000/api/v1/auth/google/login

# 2. マイルストーン作成
curl -X POST http://localhost:8000/milestones \
  -H "Content-Type: application/json" \
  -b "access_token=..." \
  -d '{...}'

# 3. 検証開始
curl -X POST http://localhost:8000/api/v1/verifications \
  -H "Content-Type: application/json" \
  -b "access_token=..." \
  -d '{"milestone_id": "..."}'

# 4. 位置情報送信
curl -X POST http://localhost:8000/api/v1/verifications/{verification_id}/location \
  -H "Content-Type: application/json" \
  -b "access_token=..." \
  -d '{"latitude": 35.6812, "longitude": 139.7671}'

# 5. 検証完了
curl -X POST http://localhost:8000/api/v1/verifications/{verification_id}/complete \
  -b "access_token=..."
```

---

## Critical Files

### Phase 0（非同期化）
- `domain/user/repositories.py`
- `domain/milestone/repositories.py`
- `application/milestone/use_cases.py`
- `apps/api/routers/milestone_router.py`

### Phase 1-2（PostgreSQL永続化）
- `infrastructure/user/persistence/repository.py`
- `infrastructure/milestone/persistence/repository.py`
- `infrastructure/user/persistence/mappers.py`
- `infrastructure/milestone/persistence/mappers.py`

### Phase 7-8（位置情報検証ドメイン）
- `domain/verification/models.py`
- `domain/verification/services.py`

### Phase 11（検証ユースケース）
- `application/verification/use_cases.py`

### Phase 12（検証API）
- `apps/api/routers/verification_router.py`
