"""
Message Generation API
GET /message 엔드포인트
"""
from fastapi import APIRouter, Header, HTTPException, Query
from models.message import MessageResponse, ErrorResponse
from services.mock_data import get_mock_customer
from graph import message_workflow
from typing import Optional

router = APIRouter()


@router.get(
    "/message",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="개인화 메시지 생성",
    description="고객 ID를 기반으로 페르소나에 맞춘 개인화 CRM 메시지를 생성합니다.",
)
async def generate_message(
    x_user_id: str = Header(..., description="고객 ID"),
    channel: Optional[str] = Query("SMS", description="메시지 채널 (SMS, KAKAO, EMAIL)"),
):
    """
    개인화 메시지 생성 API
    
    Args:
        x_user_id: Header에서 추출한 고객 ID
        channel: 메시지 채널 (기본값: SMS)
        
    Returns:
        MessageResponse: 생성된 메시지 응답
        
    Raises:
        HTTPException: 고객 정보를 찾을 수 없거나 메시지 생성 실패 시
    """
    # 1. 고객 데이터 조회
    customer = get_mock_customer(x_user_id)
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"고객 ID '{x_user_id}'를 찾을 수 없습니다."
        )
    
    # 2. LangGraph 워크플로우 실행
    try:
        initial_state = {
            "user_id": x_user_id,
            "user_data": customer,
            "channel": channel,
            "strategy": {},
            "recommended_product_id": "",
            "product_data": {},
            "brand_tone": {},
            "message": "",
            "compliance_passed": False,
            "retry_count": 0,
            "error": "",
        }
        print(f"🚀 메시지 생성 워크플로우 시작, {initial_state}")
        
        result = message_workflow.invoke(initial_state)
        
        # 3. 결과 검증
        if result.get("success", False):
            return result
        else:
            # 에러 응답
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "메시지 생성 중 알 수 없는 오류가 발생했습니다.")
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"메시지 생성 중 오류 발생: {str(e)}"
        )
