def _to_float(x, field: str) -> float:
    try:
        return float(str(x).strip().replace(",", "."))
    except Exception:
        raise ValueError(f"{field} must be numeric")

def _to_int(x, field: str) -> int:
    try:
        return int(str(x).strip())
    except Exception:
        raise ValueError(f"{field} must be integer")
