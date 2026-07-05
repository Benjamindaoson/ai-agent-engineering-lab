from __future__ import annotations

from fastapi import HTTPException


def bad_request(message: str, code: str = "bad_request") -> HTTPException:
    return HTTPException(status_code=400, detail={"code": code, "message": message, "details": {}})


def not_found(message: str, code: str = "not_found") -> HTTPException:
    return HTTPException(status_code=404, detail={"code": code, "message": message, "details": {}})
