"""Result型の実装

成功（Ok）または失敗（Err）を表現する型。
エラーハンドリングを明示的にするための関数型プログラミングパターン。
"""

from typing import TypeVar, Generic, Callable, Union


T = TypeVar("T")  # 成功時の値の型
E = TypeVar("E")  # エラーの型
U = TypeVar("U")  # map後の値の型


class Ok(Generic[T, E]):
    """成功を表すResult"""

    def __init__(self, value: T) -> None:
        self._value = value

    def is_ok(self) -> bool:
        """成功かどうかを判定"""
        return True

    def is_err(self) -> bool:
        """失敗かどうかを判定"""
        return False

    def unwrap(self) -> T:
        """値を取り出す"""
        return self._value

    def unwrap_or(self, default: T) -> T:
        """値を取り出す。失敗の場合はデフォルト値を返す"""
        return self._value

    def map(self, f: Callable[[T], U]) -> "Result[U, E]":
        """成功の値を変換する"""
        return Ok(f(self._value))

    def and_then(self, f: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """成功の処理を連鎖させる"""
        return f(self._value)


class Err(Generic[T, E]):
    """失敗を表すResult"""

    def __init__(self, error: E) -> None:
        self._error = error

    def is_ok(self) -> bool:
        """成功かどうかを判定"""
        return False

    def is_err(self) -> bool:
        """失敗かどうかを判定"""
        return True

    def unwrap(self) -> T:
        """値を取り出す（失敗時は例外を発生）"""
        raise RuntimeError(str(self._error))

    def unwrap_or(self, default: T) -> T:
        """値を取り出す。失敗の場合はデフォルト値を返す"""
        return default

    def map(self, f: Callable[[T], U]) -> "Result[U, E]":
        """失敗の場合は何もしない"""
        return Err(self._error)

    def and_then(self, f: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """失敗の場合は連鎖しない"""
        return Err(self._error)


# Result型のエイリアス
Result = Union[Ok[T, E], Err[T, E]]
