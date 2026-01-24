"""Milestoneリポジトリのテスト"""

from datetime import date, time
from uuid import uuid4
import pytest
from domain.milestone.models import Milestone, MilestoneId, Title
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.milestone.repositories import InMemoryMilestoneRepository
from domain.shared.value_objects import Money
from domain.user.models import UserId


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryMilestoneRepository()


@pytest.fixture
def sample_milestone():
    """テスト用のサンプルマイルストーン"""
    return Milestone.create(
        user_id=UserId(value=uuid4()),
        title=Title(value="朝のジムトレーニング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 31),
            time=time(18, 0, 0),
            timezone="Asia/Tokyo",
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"latitude": 35.6812, "longitude": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"),
            description="朝のジム未達成",
        ),
    )


class TestInMemoryMilestoneRepository:
    """InMemoryMilestoneRepositoryのテスト"""

    def test_マイルストーンを保存して取得できること(self, repository, sample_milestone):
        """マイルストーンを保存してIDで取得できること"""
        # 保存
        result = repository.save(sample_milestone)
        assert result.is_ok()

        # 取得
        found_result = repository.find_by_id(sample_milestone.id)
        assert found_result.is_ok()
        found_milestone = found_result.unwrap()
        assert found_milestone.id == sample_milestone.id
        assert found_milestone.title == sample_milestone.title

    def test_ユーザーidでマイルストーンを検索できること(
        self, repository, sample_milestone
    ):
        """ユーザーIDでマイルストーンを検索できること"""
        # 保存
        repository.save(sample_milestone)

        # ユーザーIDで検索
        found_result = repository.find_by_user_id(sample_milestone.user_id)
        assert found_result.is_ok()
        milestones = found_result.unwrap()
        assert len(milestones) == 1
        assert milestones[0].id == sample_milestone.id

    def test_複数のマイルストーンをユーザーidで検索できること(self, repository):
        """複数のマイルストーンをユーザーIDで検索できること"""
        user_id = UserId(value=uuid4())

        # 同じユーザーの複数のマイルストーンを作成
        milestone1 = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジム"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="",
            ),
        )
        milestone2 = Milestone.create(
            user_id=user_id,
            title=Title(value="夜のランニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(20, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=500, currency="JPY"),
                description="",
            ),
        )

        repository.save(milestone1)
        repository.save(milestone2)

        # ユーザーIDで検索
        found_result = repository.find_by_user_id(user_id)
        assert found_result.is_ok()
        milestones = found_result.unwrap()
        assert len(milestones) == 2

    def test_存在しないマイルストーンのid検索はerrを返すこと(self, repository):
        """存在しないマイルストーンのID検索はErrを返すこと"""
        non_existent_id = MilestoneId(value=uuid4())
        result = repository.find_by_id(non_existent_id)
        assert result.is_err()

    def test_マイルストーンが存在しないユーザーidの検索は空リストを返すこと(
        self, repository
    ):
        """マイルストーンが存在しないユーザーIDの検索は空リストを返すこと"""
        non_existent_user_id = UserId(value=uuid4())
        result = repository.find_by_user_id(non_existent_user_id)
        assert result.is_ok()
        milestones = result.unwrap()
        assert len(milestones) == 0

    def test_マイルストーンを削除できること(self, repository, sample_milestone):
        """マイルストーンを削除できること"""
        # 保存
        repository.save(sample_milestone)

        # 削除
        delete_result = repository.delete(sample_milestone.id)
        assert delete_result.is_ok()

        # 削除後は取得できない
        found_result = repository.find_by_id(sample_milestone.id)
        assert found_result.is_err()

    def test_存在しないマイルストーンの削除はerrを返すこと(self, repository):
        """存在しないマイルストーンの削除はErrを返すこと"""
        non_existent_id = MilestoneId(value=uuid4())
        result = repository.delete(non_existent_id)
        assert result.is_err()

    def test_マイルストーンを更新できること(self, repository, sample_milestone):
        """同じIDのマイルストーンを保存すると更新されること"""
        # 最初に保存
        repository.save(sample_milestone)

        # タイトルを変更して更新
        updated_milestone = sample_milestone.update(title=Title(value="朝のランニング"))
        repository.save(updated_milestone)

        # 取得して確認
        found_result = repository.find_by_id(sample_milestone.id)
        assert found_result.is_ok()
        found_milestone = found_result.unwrap()
        assert found_milestone.title.value == "朝のランニング"
