from typing import Any

import orjson
from starlette.responses import JSONResponse


def default(obj: Any):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


class CustomORJSONResponse(JSONResponse):
    """
    JSON response using the high-performance orjson library to serialize data to JSON.
    Includes support for serializing sets.

    Read more about it in the
    [FastAPI docs for Custom Response - HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/).
    """

    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(
            content,
            default=default,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )
