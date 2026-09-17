"""Process-wide memo. Keys are free-form strings; callers invalidate by hand."""

_MEMO: dict[str, object] = {}


def memoize(key: str, compute):
    if key in _MEMO:
        return _MEMO[key]
    value = compute()
    _MEMO[key] = value
    return value


def drop(key: str) -> None:
    _MEMO.pop(key, None)


def clear_memo() -> None:
    _MEMO.clear()


def size() -> int:
    return len(_MEMO)
