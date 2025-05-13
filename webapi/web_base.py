from common.Responses.typed_response import TypedResponse
from fastapi import Response
from typing import List
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class WebBase:

    def generate_result_response(self, result: str, status_code: int = 200):
        response_body = TypedResponse(
            has_error=False,
            status_code=status_code,
            result=result
        )
        return Response(content=response_body.json(), media_type="application/json", status_code=status_code)
    
    def generate_error_response(self, errors: List[str], status_code: int):
        response_body = TypedResponse(
            has_error=True,
            status_code=status_code,
            errors=errors
        )
        return Response(content=response_body.json(), media_type="application/json", status_code=status_code)
    
    async def http_exception_handler(self, request: Request, exc: HTTPException):
        response = TypedResponse(
            has_error=True,
            status_code=exc.status_code,
            errors=[exc.detail] if isinstance(exc.detail, str) else exc.detail,
            result=None
        )
        return JSONResponse(content=response.dict(), status_code=exc.status_code)
    
    async def global_exception_handler(request: Request, exc: Exception):
        error_message = str(exc) if str(exc).strip() else "An unexpected error occurred"
        response = TypedResponse(
            has_error=True,
            status_code=500,
            errors=[error_message],
            result=None
        )
        return JSONResponse(content=response.dict(), status_code=500)