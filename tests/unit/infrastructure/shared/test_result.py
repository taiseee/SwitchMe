"""Result型のテスト"""

import pytest
from infrastructure.shared.result import Ok, Err, Result


class TestOk:
    """Okのテスト"""

    def test_ok_value_を作成できること(self):
        """Ok()で成功のResultが作成されること"""
        result: Result[int, str] = Ok(42)
        assert result.is_ok()
        assert not result.is_err()
        assert result.unwrap() == 42

    def test_ok_none_を作成できること(self):
        """Ok(None)でNoneを含む成功のResultが作成されること"""
        result: Result[None, str] = Ok(None)
        assert result.is_ok()
        assert result.unwrap() is None


class TestErr:
    """Errのテスト"""

    def test_err_value_を作成できること(self):
        """Err()で失敗のResultが作成されること"""
        result: Result[int, str] = Err("error message")
        assert not result.is_ok()
        assert result.is_err()

    def test_err_unwrap_すると例外が発生すること(self):
        """Errに対してunwrap()すると例外が発生すること"""
        result: Result[int, str] = Err("error message")
        with pytest.raises(RuntimeError, match="error message"):
            result.unwrap()


class TestResultMap:
    """Result.map()のテスト"""

    def test_ok_の値を変換できること(self):
        """map()でOkの値を変換できること"""
        result: Result[int, str] = Ok(42)
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_ok()
        assert mapped.unwrap() == 84

    def test_err_は変換されないこと(self):
        """map()でErrは変換されないこと"""
        result: Result[int, str] = Err("error")
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_err()


class TestResultAndThen:
    """Result.and_then()のテスト"""

    def test_ok_の処理を連鎖できること(self):
        """and_then()でOkの処理を連鎖できること"""
        result: Result[int, str] = Ok(42)
        chained = result.and_then(lambda x: Ok(x * 2))
        assert chained.is_ok()
        assert chained.unwrap() == 84

    def test_ok_からerr_に変換できること(self):
        """and_then()でOkからErrに変換できること"""
        result: Result[int, str] = Ok(42)
        chained = result.and_then(lambda x: Err("failed"))
        assert chained.is_err()

    def test_err_は連鎖しないこと(self):
        """and_then()でErrは連鎖しないこと"""
        result: Result[int, str] = Err("error")
        chained = result.and_then(lambda x: Ok(x * 2))
        assert chained.is_err()


class TestResultUnwrapOr:
    """Result.unwrap_or()のテスト"""

    def test_ok_の値を取得できること(self):
        """unwrap_or()でOkの値を取得できること"""
        result: Result[int, str] = Ok(42)
        value = result.unwrap_or(0)
        assert value == 42

    def test_err_の場合はデフォルト値を返すこと(self):
        """unwrap_or()でErrの場合はデフォルト値を返すこと"""
        result: Result[int, str] = Err("error")
        value = result.unwrap_or(0)
        assert value == 0
