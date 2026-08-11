from __future__ import annotations

import time
import uuid
import re

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Xóa context cũ để tránh leak giữa các request
        clear_contextvars()

        # 2. Lấy từ header hoặc tạo mới, format: req-<8 ký tự hex>
        supplied_id = request.headers.get("x-request-id", "")
        # Never mirror arbitrary client text into every log line or response.
        correlation_id = (
            supplied_id
            if re.fullmatch(r"req-[a-f0-9]{8,64}", supplied_id)
            else f"req-{uuid.uuid4().hex[:8]}"
        )

        # 3. Bind vào structlog context — mọi log sau đó tự động có trường này
        bind_contextvars(correlation_id=correlation_id)

        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)

        # 4. Trả correlation ID và thời gian xử lý trong response header
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"

        return response
