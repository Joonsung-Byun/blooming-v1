"""
Orchestrator 테스트 스크립트
가상의 페르소나를 생성하여 브랜드 추천 결과 확인
"""
from models.user import CustomerProfile, LastPurchase, ShoppingBehavior, CouponProfile, LastEngagement, PurchaseHistoryItem, CartItem
from actions.orchestrator import orchestrator_node, GraphState


def create_test_persona_1():
    """
    테스트 페르소나 1: 신규 고객 (Cold Start)
    - 20대 여성, 구매 이력 없음, 장바구니 비어있음
    - 예상 결과: Case 0, 연령대 기반 브랜드 추천
    """
    return CustomerProfile(
        user_id="test_001",
        name="이신규",
        age_group="20s",
        gender="F",
        membership_level="Bronze",
        skin_type=["Combination"],
        skin_concerns=["Pore", "Oiliness"],
        preferred_tone="Warm_Spring",
        keywords=["Natural", "Budget-friendly"],
        acquisition_channel="Instagram_Ad",
        average_order_value=0,
        average_repurchase_cycle_days=0,
        repurchase_cycle_alert=False,
        last_purchase=None,
        purchase_history=[],
        shopping_behavior=ShoppingBehavior(
            event_participation="Low",
            cart_abandonment_rate="None",
            price_sensitivity="High"
        ),
        coupon_profile=CouponProfile(
            history=[],
            propensity="Discount_Seeker",
            preferred_type="Percentage_Off"
        ),
        last_engagement=LastEngagement(
            visit_date="2024-12-15",
            click_date="2024-12-15",
            last_visit_category="Cleanser"
        ),
        cart_items=[],
        recently_viewed_items=[]
    )


def create_test_persona_2():
    """
    테스트 페르소나 2: 적극적 탐색 고객 (Behavioral)
    - 30대 남성, 구매 이력 없지만 장바구니와 최근 본 상품 있음
    - 예상 결과: Case 1, 장바구니 기반 브랜드 + 연령대 브랜드
    """
    return CustomerProfile(
        user_id="test_002",
        name="김탐색",
        age_group="30s",
        gender="M",
        membership_level="Silver",
        skin_type=["Oily"],
        skin_concerns=["Acne", "Pore"],
        preferred_tone="Cool_Summer",
        keywords=["Men's_Skincare", "Simple_Routine"],
        acquisition_channel="Naver_Search",
        average_order_value=0,
        average_repurchase_cycle_days=0,
        repurchase_cycle_alert=False,
        last_purchase=None,
        purchase_history=[],
        shopping_behavior=ShoppingBehavior(
            event_participation="Medium",
            cart_abandonment_rate="Frequent",
            price_sensitivity="Medium"
        ),
        coupon_profile=CouponProfile(
            history=["FIRST_ORDER"],
            propensity="Cautious_Buyer",
            preferred_type="Fixed_Amount"
        ),
        last_engagement=LastEngagement(
            visit_date="2024-12-14",
            click_date="2024-12-14",
            last_visit_category="Toner"
        ),
        cart_items=[
            CartItem(
                id="cart_001",
                name="IOPE 맨 에센스",
                brand="IOPE",
                added_at="2024-12-14"
            )
        ],
        recently_viewed_items=["IOPE 맨 에센스", "헤라 옴므 토너"]
    )


def create_test_persona_3():
    """
    테스트 페르소나 3: 프로필 기반 고객 (Profile-based)
    - 40대 여성, 구매 이력 2번, 명확한 뷰티 프로필
    - 예상 결과: Case 2, 구매 이력 브랜드 + 프로필 기반 추천
    """
    return CustomerProfile(
        user_id="test_003",
        name="최안티",
        age_group="40s",
        gender="F",
        membership_level="VIP",
        skin_type=["Dry", "Sensitive"],
        skin_concerns=["Wrinkle", "Sagging", "Dullness"],
        preferred_tone="Warm_Autumn",
        keywords=["Anti-aging", "Hydration", "Premium"],
        acquisition_channel="Direct",
        average_order_value=120000,
        average_repurchase_cycle_days=40,
        repurchase_cycle_alert=False,
        last_purchase=LastPurchase(
            date="2024-11-01",
            product_id="SW-CREAM-001",
            product_name="설화수 윤조에센스"
        ),
        purchase_history=[
            PurchaseHistoryItem(
                brand="Sulwhasoo",
                category="Essence",
                purchase_date="2024-11-01"
            ),
            PurchaseHistoryItem(
                brand="HERA",
                category="Serum",
                purchase_date="2024-09-20"
            )
        ],
        shopping_behavior=ShoppingBehavior(
            event_participation="High",
            cart_abandonment_rate="Rare",
            price_sensitivity="Low"
        ),
        coupon_profile=CouponProfile(
            history=["BDAY_2024", "VVIP_SPECIAL"],
            propensity="Quality_First",
            preferred_type="Gift_with_Purchase"
        ),
        last_engagement=LastEngagement(
            visit_date="2024-12-10",
            click_date="2024-12-10",
            last_visit_category="Eye Cream"
        ),
        cart_items=[],
        recently_viewed_items=["설화수 자음생크림", "한율 수액크림"]
    )


def create_test_persona_4():
    """
    테스트 페르소나 4: 단골 고객 (Hybrid)
    - 50대 여성, 구매 이력 5번 이상, 충성 고객
    - 예상 결과: Case 3, 재구매 + 프로필 + 행동 데이터 종합
    """
    return CustomerProfile(
        user_id="test_004",
        name="박로열",
        age_group="50s+",
        gender="F",
        membership_level="VVIP",
        skin_type=["Dry"],
        skin_concerns=["Wrinkle", "Elasticity", "Dark_Spot"],
        preferred_tone="Cool_Winter",
        keywords=["Luxury", "Anti-aging", "Proven_Results"],
        acquisition_channel="Referral",
        average_order_value=200000,
        average_repurchase_cycle_days=30,
        repurchase_cycle_alert=True,
        last_purchase=LastPurchase(
            date="2024-11-20",
            product_id="SW-LUXURY-001",
            product_name="설화수 자음생 라인"
        ),
        purchase_history=[
            PurchaseHistoryItem(
                brand="Sulwhasoo",
                category="Serum",
                purchase_date="2024-11-20"
            ),
            PurchaseHistoryItem(
                brand="Sulwhasoo",
                category="Cream",
                purchase_date="2024-10-15"
            ),
            PurchaseHistoryItem(
                brand="HERA",
                category="Foundation",
                purchase_date="2024-09-01"
            ),
            PurchaseHistoryItem(
                brand="Sulwhasoo",
                category="Essence",
                purchase_date="2024-08-10"
            ),
            PurchaseHistoryItem(
                brand="IOPE",
                category="Cushion",
                purchase_date="2024-07-05"
            )
        ],
        shopping_behavior=ShoppingBehavior(
            event_participation="High",
            cart_abandonment_rate="Rare",
            price_sensitivity="Low"
        ),
        coupon_profile=CouponProfile(
            history=["VVIP_2024", "BDAY_2024", "LOYALTY_REWARD"],
            propensity="Quality_First",
            preferred_type="Gift_with_Purchase"
        ),
        last_engagement=LastEngagement(
            visit_date="2024-12-14",
            click_date="2024-12-14",
            last_visit_category="Anti-aging"
        ),
        cart_items=[
            CartItem(
                id="cart_002",
                name="설화수 자음생 아이크림",
                brand="Sulwhasoo",
                added_at="2024-12-14"
            )
        ],
        recently_viewed_items=["설화수 자음생 아이크림", "프리메라 옵티멀 세럼"]
    )


def test_orchestrator(persona: CustomerProfile, test_name: str):
    """
    Orchestrator 테스트 실행
    
    Args:
        persona: 테스트할 고객 프로필
        test_name: 테스트 이름
    """
    print(f"\n{'='*80}")
    print(f"🧪 {test_name}")
    print(f"{'='*80}")
    print(f"👤 고객 정보:")
    print(f"  - 이름: {persona.name}")
    print(f"  - 연령대: {persona.age_group}")
    print(f"  - 멤버십: {persona.membership_level}")
    print(f"  - 구매 이력: {len(persona.purchase_history)}건")
    print(f"  - 장바구니: {len(persona.cart_items)}개")
    print(f"  - 최근 본 상품: {len(persona.recently_viewed_items)}개")
    print(f"  - 피부 타입: {', '.join(persona.skin_type)}")
    print(f"  - 피부 고민: {', '.join(persona.skin_concerns)}")
    
    # GraphState 초기화
    state: GraphState = {
        "user_id": persona.user_id,
        "user_data": persona,
        "recommended_brand": [],
        "strategy": 0,
        "recommended_product_id": "",
        "product_data": {},
        "brand_tone": {},
        "channel": "SMS",
        "message": "",
        "compliance_passed": False,
        "retry_count": 0,
        "error": ""
    }
    
    # Orchestrator 실행
    result = orchestrator_node(state)
    
    print(f"\n📊 분석 결과:")
    print(f"  - Strategy: Case {result['strategy']}")
    print(f"  - Recommended Brands: {', '.join(result['recommended_brand'])}")
    print()


def main():
    """메인 테스트 실행"""
    print("🎨 Blooming v1 - Orchestrator 테스트")
    print("=" * 80)
    
    # 테스트 실행
    test_orchestrator(create_test_persona_1(), "테스트 1: 신규 고객 (Cold Start)")
    test_orchestrator(create_test_persona_2(), "테스트 2: 탐색 고객 (Behavioral)")
    test_orchestrator(create_test_persona_3(), "테스트 3: 프로필 고객 (Profile-based)")
    test_orchestrator(create_test_persona_4(), "테스트 4: 단골 고객 (Hybrid)")
    
    print(f"\n{'='*80}")
    print("✅ 모든 테스트 완료!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()