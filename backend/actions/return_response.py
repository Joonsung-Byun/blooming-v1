"""
Return Response Node
최종 응답 생성
"""
from typing import TypedDict
from models.user import CustomerProfile
from models.message import GeneratedMessage, MessageResponse


class GraphState(TypedDict):
    """LangGraph State 정의"""
    user_id: str
    user_data: CustomerProfile
    strategy: dict
    recommended_product_id: str
    product_data: dict
    brand_tone: dict
    channel: str
    message: str
    compliance_passed: bool
    retry_count: int
    error: str
    error_reason: str  # Compliance 실패 이유
    success: bool  # API 응답용


def return_response_node(state: GraphState) -> dict:
    """
    Return Response Node
    
    최종 응답 데이터를 생성합니다.
    
    Args:
        state: LangGraph State
        
    Returns:
        API 응답 딕셔너리
    """
    if not state.get("compliance_passed", False):
        # Compliance 실패 시 에러 응답
        print(f"❌ Compliance 실패: {state.get('error', '메시지 생성 실패')}")
        return {
            "success": False,
            "error": state.get("error", "메시지 생성 실패"),
        }
    
    # 성공 응답 생성
    print(f"✅ 최종 응답 생성: user={state['user_id']}, message={state['message'][:50]}...")
    
    return {
        "success": True,
    }
