import os
import json
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
import httpx
from config import settings
from sentence_transformers import CrossEncoder
import torch
from datetime import datetime

# Cross-Encoder 설정
TOP_K = 3
CANDIDATE_POOL = 30
EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536
CE_MODEL = "BAAI/bge-reranker-v2-m3"
KW_BONUS_ALPHA = 1.2
CUSTOMER_ID_COL = "user_id"
PRODUCT_VECTOR_FK_COL = "product_id"

# 동의어 매핑
SKIN_TYPE_MAP = {
    "Sensitive": "민감성",
    "Dry": "건성",
    "Oily": "지성",
    "Combination": "복합성",
    "Neutral": "중성",
    "Normal": "중성",
}

CONCERN_MAP = {
    "Pores": "모공",
    "Sebum": "피지",
    "Acne": "여드름",
    "Redness": "홍조",
    "Dryness": "건조",
    "Wrinkle": "주름",
    "Elasticity": "탄력",
    "Dullness": "칙칙함",
    "Anti-aging": "안티에이징",
    "Antiaging": "안티에이징",
    "Sensitive": "민감",
    "Sensitivity": "민감",
}

TONE_MAP = {
    "Cool_Summer": "쿨톤 여름",
    "Cool_Winter": "쿨톤 겨울",
    "Warm_Spring": "웜톤 봄",
    "Warm_Autumn": "웜톤 가을",
    "Neutral": "뉴트럴",
}

# 영어 키워드 -> 한글 동의어 매핑 (키워드 매칭률 개선)
KEYWORD_TRANSLATION = {
    # 효능 키워드
    "antiaging": ["안티에이징", "안티", "주름", "주름개선", "주름케어", "탄력", "탄력케어", "탄력개선", "어려보이는", "항산화", "리프팅", "노화", "안티에이지", "개선효과"],
    "anti_aging": ["안티에이징", "안티", "주름", "주름개선", "주름케어", "탄력", "탄력케어", "탄력개선", "어려보이는", "항산화", "리프팅", "노화", "개선효과"],
    "firming": ["탄력", "탄력케어", "탄력개선", "리프팅", "퍼밍", "탄탄", "elasticity", "firmness", "긴장", "피부탄력"],
    "whitening": ["화이트닝", "미백", "브라이트닝", "톤업", "brightening", "브라이트", "화사", "피부톤", "톤개선"],
    "brightening": ["브라이트닝", "화이트닝", "미백", "톤업", "화사", "피부톤", "밝은"],
    "nutrition": ["영양", "nutrition", "영양감", "영양공급", "영양크림", "nourishing"],
    "moisturizing": ["보습", "보습감", "보습력", "수분", "수분감", "수분공급", "촉촉", "촉촉한", "hydrating", "하이드레이팅", "moisturize"],
    "hydrating": ["수분", "수분감", "수분공급", "보습", "보습감", "촉촉", "촉촉한"],
    "nourishing": ["영양", "영양감", "영양공급", "영양크림"],
    "exfoliating": ["각질", "각질제거", "각질케어", "각질관리", "peeling", "필링"],
    "peeling": ["필링", "각질제거", "각질케어", "각질"],
    "soothing": ["진정", "수딩", "편안", "편안한", "calm", "calming", "진정효과"],
    "calming": ["진정", "수딩", "편안", "편안한", "calm"],
    
    # 피부타입/고민
    "sensitive": ["민감", "민감성", "순한", "자극없는", "gentle", "센시티브", "민감성피부", "민감피부"],
    "acne": ["여드름", "트러블", "아크네", "피지", "모공", "trouble"],
    "pore": ["모공", "pore", "피지", "블랙헤드", "모공케어"],
    "sebum": ["피지", "유분", "sebum", "오일", "유분조절"],
    "dry": ["건조", "건성", "수분부족", "건조함"],
    "oily": ["지성", "유분", "피지", "오일리"],
    
    # 품질/등급
    "premium": ["프리미엄", "고급", "고급스러운", "럭셔리", "명품", "최고급"],
    "luxury": ["럭셔리", "고급", "프리미엄", "명품"],
    "glow": ["광채", "윤기", "빛나는", "글로우", "radiance", "래디언스", "빛", "생기", "피부톤", "톤", "톤개선"],
    "radiance": ["래디언스", "광채", "윤기", "빛나는", "생기"],
    "dermatologisttested": ["피부과", "임상", "테스트", "dermatologist", "피부과테스트", "전문가"],
    "dermatologist_tested": ["피부과", "임상", "테스트", "전문가", "피부과테스트"],
    
    # 텍스처/사용감
    "lightweight": ["가벼운", "가벼운사용감", "가벼운텍스처", "가벼운제형", "light"],
    "light": ["가벼운", "가볍고", "가벼운사용감"],
    "soft": ["부드러운", "soft", "소프트", "부드럽게"],
    "gentle": ["순한", "부드러운", "자극없는", "젠틀"],
    "rich": ["풍부한", "농축", "진한", "리치"],
    "creamy": ["크리미한", "부드러운", "크림같은", "크림"],
    "absorption": ["흡수", "흡수력", "스며듦", "빠른흡수"],
    "nonsticky": ["끈적임없는", "산뜻한", "가벼운"],
    "nondrying": ["건조하지않은", "촉촉한", "보습"],
    
    # 가격/가성비
    "affordable": ["가성비", "가격저렴한", "합리적", "가격대비", "저렴"],
    "valueformoney": ["가성비", "가격대비", "가성비좋은"],
    "value_for_money": ["가성비", "가격대비", "합리적"],
}

# 날씨/시즌별 제품 키워드 매핑
WEATHER_KEYWORDS = {
    "spring": [
        "봄", "미세먼지", "황사", "꽃가루", "알러지", "알레르기", "진정", "보호", "보호막", 
        "배리어", "클렌징", "세안", "딥클렌징", "민감", "민감성", "자극완화", "순한", 
        "저자극", "항산화", "비타민C", "진정효과", "피부진정", "피부보호"
    ],
    "summer": [
        "여름", "폭염", "자외선", "장마", "습도", "UV", "SPF", "PA", "선크림", "썬", 
        "선케어", "쿨링", "시원한", "산뜻한", "가벼운", "땀", "피지", "모공", "유분", 
        "지성", "수분", "젤", "에센스", "자외선차단", "유분조절", "모공케어", "피지조절", 
        "청량", "청량감", "가벼운제형", "산뜻한발림성"
    ],
    "fall": [
        "가을", "환절기", "일교차", "건조", "건조한", "보습", "수분", "진정", "밸런스", 
        "장벽", "배리어", "회복", "리페어", "영양", "케어", "피부장벽", "세라마이드", 
        "히알루론산", "크림", "보습감", "탄력", "촉촉한", "부드러운", "영양공급", 
        "장벽리페어", "피부밀도", "밀도"
    ],
    "winter": [
        "겨울", "한파", "건조", "극건조", "보습", "고보습", "수분", "크림", "오일", "밤", 
        "농축", "리치", "영양", "영양크림", "리프팅", "탄력", "밀착", "피부장벽", 
        "세라마이드", "촉촉한보습감", "부드러운발림성", "장벽리페어", "피부밀도", "밀도"
    ]
}

# 계절별 핵심 키워드 (추가 가중치 2배 적용)
WEATHER_PRIORITY_KEYWORDS = {
    "spring": [
        # 미세먼지/황사 대응
        "진정", "민감", "순한", "저자극", "보호", "배리어", "피부보호",
        "클렌징", "딥클렌징", "세안",
        "알러지", "알레르기", "자극완화", "진정효과", "피부진정"
    ],
    "summer": [
        # 땀/피지 관리 + 자외선 차단
        "산뜻", "산뜻한", "가벼운", "끈적임없는", "논스티키", "쿨링", "시원한",
        "SPF", "PA", "자외선", "자외선차단", "선크림", "선케어", "UV",
        "피지", "피지조절", "모공", "모공케어", "유분조절", "지성",
        "젤", "청량", "청량감", "가벼운제형", "산뜻한발림성"
    ],
    "fall": [
        # 환절기 건조 + 피부장벽
        "보습", "수분", "촉촉", "촉촉한", "건조",
        "장벽", "배리어", "피부장벽", "장벽리페어", "회복", "리페어",
        "진정", "밸런스", "영양", "영양공급",
        "세라마이드", "히알루론산"
    ],
    "winter": [
        # 극건조 대응 + 고보습
        "보습", "고보습", "수분", "극건조", "건조",
        "크림", "리치", "농축", "밀착", "오일", "밤",
        "영양", "영양크림", "영양공급",
        "촉촉한보습감", "부드러운발림성",
        "세라마이드", "피부장벽", "장벽리페어"
    ]
}

# Cross-Encoder 캐싱 (한 번만 로드)
_cross_encoder_cache = None

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_cross_encoder() -> CrossEncoder:
    """Cross-Encoder를 로드하거나 캐시된 인스턴스 반환"""
    global _cross_encoder_cache
    if _cross_encoder_cache is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[CrossEncoder] loading: {CE_MODEL} on device={device}")
        _cross_encoder_cache = CrossEncoder(CE_MODEL, device=device)
    return _cross_encoder_cache


def normalize_list(v: Any) -> List[str]:
    """리스트 정규화"""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str):
        s = v.strip()
        if s.startswith("{") and s.endswith("}"):
            s = s[1:-1]
        return [x.strip().strip('"') for x in s.split(",") if x.strip()]
    return [str(v).strip()]


def with_kr(items: List[str], mapping: Dict[str, str]) -> List[str]:
    """영어 키워드에 한글 매핑 추가"""
    out = []
    for x in items:
        k = mapping.get(x)
        out.append(f"{x}({k})" if k else x)
    return out


def build_user_query_text(customer: Dict[str, Any]) -> str:
    """유저 정보를 기반으로 쿼리 텍스트 생성"""
    skin_types = with_kr(normalize_list(customer.get("skin_type")), SKIN_TYPE_MAP)
    concerns = with_kr(normalize_list(customer.get("skin_concerns")), CONCERN_MAP)
    keywords = normalize_list(customer.get("keywords"))
    
    # preferred_tone이 리스트일 수 있음 (DB 스키마 차이)
    tone = customer.get("preferred_tone")
    if isinstance(tone, list):
        tone = tone[0] if tone else None
    
    tone_kr = TONE_MAP.get(tone, tone) if tone else None

    lines = [
        "스킨케어 제품 추천 쿼리 (키워드 최우선)",
        "",
        "[중요 키워드 TOP - 최우선 반영]",
        f"- {', '.join(keywords)}" if keywords else "- (없음)",
        "※ 위 키워드와 직접적으로 연결되는 효능/특징/제품 키워드가 포함된 제품을 최우선으로 평가한다.",
        "",
        "[피부타입]",
        f"- {', '.join(skin_types)}" if skin_types else "- 정보 없음",
        "",
        "[피부고민]",
        f"- {', '.join(concerns)}" if concerns else "- 정보 없음",
        "",
        "[추구 톤]",
        f"- {tone_kr}" if tone_kr else "- 정보 없음",
        "",
        "[평가 기준 재강조]",
        f"- 핵심 키워드({', '.join(keywords)})와 연관성이 높은 제품을 우선 추천" if keywords else "- 키워드 기반 우선 추천",
    ]
    return "\n".join(lines)


def embed_text(oa: OpenAI, text: str) -> List[float]:
    """텍스트를 임베딩 벡터로 변환"""
    res = oa.embeddings.create(
        model=EMBED_MODEL,
        input=[text],
        encoding_format="float",
    )
    emb = res.data[0].embedding
    if len(emb) != EMBED_DIM:
        raise ValueError(f"임베딩 차원 불일치: got {len(emb)} expected {EMBED_DIM}")
    return emb


def truncate_for_ce(text: str, max_chars: int = 1800) -> str:
    """Cross-Encoder 입력 길이 제한"""
    text = text or ""
    return text if len(text) <= max_chars else text[:max_chars]


def expand_keywords(keywords: List[str]) -> List[str]:
    """영어 키워드를 한글 동의어로 확장하여 매칭률 향상"""
    expanded = []
    for kw in keywords:
        # 원본 키워드 추가
        expanded.append(kw)
        
        # 정규화: 소문자 변환, 언더스코어 제거
        normalized = kw.lower().replace("_", "").replace("-", "").replace(" ", "")
        
        # 매핑된 한글 동의어 추가
        if normalized in KEYWORD_TRANSLATION:
            expanded.extend(KEYWORD_TRANSLATION[normalized])
    
    return expanded


def get_current_season() -> str:
    """현재 날짜를 기준으로 시즌 반환"""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:  # 12, 1, 2
        return "winter"


def keyword_bonus(
    user_keywords: List[str], 
    product_content: str, 
    product_keywords: List[str], 
    skin_concerns: List[str] = None,
    weather_keywords: List[str] = None,
    current_season: str = None
) -> Tuple[float, Dict[str, Any]]:
    """키워드 매칭 보너스 계산 (0~1) - 단순 카운트 방식 + 날씨 우선순위 가중치
    
    유저의 키워드 + 피부고민이 제품 본문 + 제품 키워드에서 몇 번 나오는지 카운트
    
    Args:
        user_keywords: 유저의 키워드 리스트 (확장된 것)
        product_content: 제품 본문 (products_vector.content)
        product_keywords: 제품 키워드 리스트 (products.keywords)
        skin_concerns: 유저의 피부고민 (추가 검색 키워드)
        weather_keywords: 날씨/시즌 관련 키워드 (intent=weather일 때)
        current_season: 현재 계절 (spring/summer/fall/winter)
    
    Returns:
        (score, details): 0~1 점수와 상세 정보
    """
    # 검색할 키워드 수집
    kws = [k.strip() for k in (user_keywords or []) if k and str(k).strip()]
    
    # 피부고민 추가
    if skin_concerns:
        kws.extend([k.strip() for k in skin_concerns if k and str(k).strip()])
    
    # weather intent일 경우 weather_keywords 추가
    if weather_keywords:
        kws.extend([k.strip() for k in weather_keywords if k and str(k).strip()])
    
    if not kws:
        return 0.0, {"matched_keywords": [], "hit_count": 0, "total_keywords": 0, "priority_hits": 0}

    # 검색 대상: 제품 본문 + 제품 키워드 합치기
    search_text = (product_content or "").lower()
    if product_keywords:
        search_text += " " + " ".join([str(k).lower() for k in product_keywords])
    
    # 띄어쓰기 제거한 정규화 버전
    search_text_normalized = search_text.replace(" ", "")

    # 계절별 우선순위 키워드 가져오기
    priority_kws = []
    if current_season and current_season in WEATHER_PRIORITY_KEYWORDS:
        priority_kws = [k.lower() for k in WEATHER_PRIORITY_KEYWORDS[current_season]]

    # 키워드 매칭 카운트 (우선순위 키워드는 2배 가중치)
    hit_count = 0.0
    matched_keywords = []
    priority_matched = []
    
    for kw in kws:
        k = kw.lower()
        k_normalized = k.replace(" ", "")
        
        # 원본 매칭 OR 정규화 매칭
        if (k in search_text) or (k_normalized in search_text_normalized):
            matched_keywords.append(kw)
            
            # 우선순위 키워드인지 확인 (계절별 핵심 키워드)
            is_priority = any(pk in k or k in pk for pk in priority_kws)
            
            if is_priority:
                hit_count += 2.0  # 우선순위 키워드는 2배 가중치
                priority_matched.append(kw)
            else:
                hit_count += 1.0  # 일반 키워드

    # 0~1 정규화 (우선순위 키워드가 있을 수 있으므로 최대값 조정)
    # 모든 키워드가 우선순위라면 max = len(kws) * 2
    max_possible_score = len(kws) * 2.0 if priority_kws else len(kws)
    score = hit_count / max(max_possible_score, 1)
    
    details = {
        "matched_keywords": matched_keywords,
        "hit_count": int(hit_count),  # 실제 가중치 적용된 값
        "total_keywords": len(kws),
        "priority_hits": len(priority_matched)  # 우선순위 키워드 매칭 수
    }
    
    return float(min(1.0, max(0.0, score))), details


async def fetch_products_from_supabase() -> Dict[str, str]:
    """
    Fetch products from Supabase and format them for the LLM.
    (Deprecated - 이제 recommend_product_with_brands 사용)
    """
    return {}

    # url = f"{settings.SUPABASE_URL}/rest/v1/products"
    # headers = {
    #     "apikey": settings.SUPABASE_KEY,
    #     "Authorization": f"Bearer {settings.SUPABASE_KEY}",
    # }

    # try:
    #     async with httpx.AsyncClient() as http_client:
    #         response = await http_client.get(url, headers=headers)
    #         response.raise_for_status()
    #         products_data = response.json()
            
    #         # Format: "ID": "Name (Brand, Category, Description)"
    #         formatted_products = {}
    #         full_data = {}  # Store full product data
    #         for p in products_data:
    #             # Adjust field names based on actual DB schema
    #             # Schema: id, product_code, brand, name, category_major, category_middle, category_small, 
    #             # price_original, price_final, discount_rate, review_score, review_count, features, analytics, keywords
                
    #             p_id = p.get("product_code") or str(p.get("id"))
    #             name = p.get("name")
    #             brand = p.get("brand", "")
                
    #             # Construct category string
    #             cats = [p.get("category_major"), p.get("category_middle"), p.get("category_small")]
    #             category = " > ".join([c for c in cats if c])
                
    #             # Construct description from keywords and features
    #             keywords = p.get("keywords", "")
    #             price = p.get("price_final")
    #             review_score = p.get("review_score")
                
    #             desc_parts = []
    #             if keywords:
    #                 desc_parts.append(f"Keywords: {keywords}")
    #             if price:
    #                 desc_parts.append(f"Price: {price}")
    #             if review_score:
    #                 desc_parts.append(f"Rating: {review_score}")
                
    #             desc = ", ".join(desc_parts)
                
    #             if p_id and name:
    #                 info = f"{name} (Brand: {brand}, Category: {category}, {desc})"
    #                 formatted_products[p_id] = info
    #                 # Store full product data
    #                 full_data[p_id] = p
            
    #         PRODUCTS_CACHE = formatted_products
    #         PRODUCTS_FULL_DATA = full_data
            
    #         # Debug: Print first 3 products to verify format
    #         print("DEBUG: Sample products from DB:")
    #         for i, (pid, info) in enumerate(formatted_products.items()):
    #             if i >= 3: break
    #             print(f" - {pid}: {info}")
                
    #         return formatted_products
            
    # except Exception as e:
    #     print(f"Failed to fetch products from Supabase: {e}")
    #     # Fallback to empty dict or hardcoded list if needed
    #     return {}

async def recommend_product_with_brands(
    user_id: str,
    user_data: Any,
    target_brands: List[str] = None,
    top_k: int = 1,
    intent: str = ""
) -> Optional[Dict[str, Any]]:
    """
    유저 ID와 브랜드 리스트를 받아 Cross-Encoder 기반으로 최고의 상품을 추천합니다.
    
    Args:
        user_id: 사용자 ID
        user_data: CustomerProfile 객체 (user_data에서 추출한 정보)
        target_brands: 추천할 브랜드 리스트 (None이면 모든 브랜드)
        top_k: 반환할 상품 개수 (기본값: 1)
        intent: 추천 의도 ("": regular, "event": 할인율 높은 제품, "weather": 날씨별 제품)
        
    Returns:
        추천 상품 정보 dict 또는 None
    """
    try:
        # Supabase 및 OpenAI 클라이언트 초기화
        from supabase import create_client, Client
        sb: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        oa = OpenAI(api_key=settings.OPENAI_API_KEY)
        ce = get_cross_encoder()
        
        # 1) 고객 정보 조회
        customer_resp = (
            sb.table("customers")
            .select("user_id, skin_type, skin_concerns, keywords, preferred_tone")
            .eq(CUSTOMER_ID_COL, user_id)
            .limit(1)
            .execute()
        )

        print(f"customer_resp: {customer_resp}")

        
        if not customer_resp.data:
            print(f"[WARN] customers에서 {CUSTOMER_ID_COL}={user_id}를 찾지 못함")
            return None
        
        customer = customer_resp.data[0]
        user_keywords_raw = normalize_list(customer.get("keywords"))
        
        # 키워드 확장: 영어 -> 한글 동의어 추가
        user_keywords = expand_keywords(user_keywords_raw)
        print(f"  🔍 키워드 확장: {user_keywords_raw} → {len(user_keywords)}개")
        
        # intent 처리: weather일 경우 시즌별 키워드 추가
        weather_keywords = []
        if intent == "weather":
            current_season = get_current_season()
            weather_keywords = WEATHER_KEYWORDS.get(current_season, [])
            print(f"  🌡️ Weather Intent: {current_season} season - 키워드: {weather_keywords[:3]}...")
        
        # 2) 쿼리 텍스트 생성
        query_text = build_user_query_text(customer)
        
        # 3) 임베딩 생성
        query_emb = embed_text(oa, query_text)
        
        # 4) 벡터 유사도 검색 (후보 풀)
        rpc_payload = {
            "filter": {},
            "match_count": CANDIDATE_POOL,
            "query_embedding": query_emb,
        }
        match_resp = sb.rpc("match_products", rpc_payload).execute()
        matches = match_resp.data or []
        
        if not matches:
            print("[WARN] 유사도 검색 결과가 없습니다.")
            return None
        
        matches.sort(key=lambda m: float(m.get("similarity", 0.0)), reverse=True)
        candidate_ids = [m["product_id"] for m in matches]
        sim_map = {m["product_id"]: float(m["similarity"]) for m in matches}
        
        # 5) products 상세 정보 조회 (브랜드 필터링 적용)
        query = (
            sb.table("products")
            .select("id, brand, name, category_major, category_middle, category_small, price_final, discount_rate, review_score, review_count")
            .in_("id", candidate_ids)
        )
        
        if target_brands and len(target_brands) > 0:
            query = query.in_("brand", target_brands)
            print(f"  🏷️ 브랜드 필터링 적용: {target_brands}")
        
        products_resp = query.execute()
        products = products_resp.data or []
        
        if not products:
            if target_brands:
                print(f"[WARN] 지정된 브랜드({target_brands})에서 상품을 찾지 못함")
            else:
                print("[WARN] 상품을 찾지 못함")
            return None
        
        prod_map = {p["id"]: p for p in products}
        filtered_ids = list(prod_map.keys())
        
        # 6) products_vector content 가져오기
        pv_resp = (
            sb.table("products_vector")
            .select(f"{PRODUCT_VECTOR_FK_COL}, content")
            .in_(PRODUCT_VECTOR_FK_COL, filtered_ids)
            .execute()
        )
        pv_rows = pv_resp.data or []
        pv_map = {r[PRODUCT_VECTOR_FK_COL]: r.get("content") for r in pv_rows}
        
        # 7) Cross-Encoder rerank + keyword bonus
        pairs: List[Tuple[str, str]] = []
        valid_ids: List[int] = []
        
        for pid in filtered_ids:
            content = pv_map.get(pid)
            if not content:
                continue
            valid_ids.append(pid)
            pairs.append((truncate_for_ce(query_text), truncate_for_ce(content)))
        
        if not pairs:
            print("[WARN] 브랜드 필터링 후 products_vector.content가 비어있습니다.")
            return None
        
        ce_scores = ce.predict(pairs)
        
        reranked = []
        for pid, ce_score in zip(valid_ids, ce_scores):
            content = pv_map.get(pid, "")
            p = prod_map.get(pid)
            
            # 제품 키워드 가져오기
            product_keywords = normalize_list(p.get("keywords"))
            
            # 키워드 보너스 계산 (피부고민 + 날씨 우선순위 키워드 포함)
            kwb, kw_details = keyword_bonus(
                user_keywords=user_keywords,
                product_content=content,
                product_keywords=product_keywords,
                skin_concerns=concerns,
                weather_keywords=weather_keywords if intent == "weather" else None,
                current_season=current_season if intent == "weather" else None
            )
            
            final_score = float(ce_score) + KW_BONUS_ALPHA * kwb
            
            reranked.append({
                "product_id": str(pid),
                "brand": p.get("brand"),
                "name": p.get("name"),
                "category_major": p.get("category_major"),
                "category_middle": p.get("category_middle"),
                "category_small": p.get("category_small"),
                "price_final": p.get("price_final"),
                "discount_rate": p.get("discount_rate"),
                "review_score": p.get("review_score"),
                "review_count": p.get("review_count"),
                "ce_score": float(ce_score),
                "kw_bonus": float(kwb),
                "final_score": float(final_score),
                "similarity": float(sim_map.get(pid, 0.0)),
            })
        
        # intent에 따른 정렬
        if intent == "event":
            # Event Intent: final_score로 Top 5 추출 후, Top 5 중 할인율 우선
            reranked.sort(key=lambda r: r["final_score"], reverse=True)
            if len(reranked) >= 5:
                top_5 = reranked[:5]
                top_5.sort(key=lambda r: (r.get("discount_rate") or 0), reverse=True)
                reranked = top_5 + reranked[5:]
            print(f"  🎁 Event Intent: Top 5 중 할인율 우선 (1위 할인율: {reranked[0].get('discount_rate', 0)}%)")
        else:
            # regular 또는 weather: final_score로 정렬
            reranked.sort(key=lambda r: r["final_score"], reverse=True)
        
        # 9) 디버그 출력 (상위 3개)
        if reranked:
            print(f"\n  📊 Top 3 추천 결과:")
            for i, r in enumerate(reranked[:3], 1):
                match_rate = kwb if i == 1 else 0.0  # 1위만 출력
                print(f"    {i}. {r['name'][:30]}... (키워드: {match_rate*100:.0f}%, 최종: {r['final_score']:.3f})")
        
        # 8) top_k 개수만큼 반환
        if top_k == 1:
            return reranked[0] if reranked else None
        else:
            return reranked[:top_k]
            
    except Exception as e:
        print(f"❌ 상품 추천 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


async def get_recommendation(request_data: Any) -> Dict[str, Any]:
    """
    Get recommendation using Cross-Encoder based system.
    """
    user_id = request_data.user_id
    intention = getattr(request_data, 'intention', None) or ""
    user_data = request_data.user_data
    target_brands = getattr(request_data, 'target_brand', None)
    
    print(f"\n🎯 추천 요청 수신:")
    print(f"  - User ID: {user_id}")
    print(f"  - Intention: {intention}")
    print(f"  - Target Brands: {target_brands}")
    
    # Cross-Encoder 기반 추천 시스템 호출
    recommendation = await recommend_product_with_brands(
        user_id=user_id,
        user_data=user_data,
        target_brands=target_brands if target_brands else [],
        top_k=1,
        intent=intention
    )
    
    if recommendation:
        print(f"  ✅ 상품 추천 성공: {recommendation['name']} (ID: {recommendation['product_id']})")
        print(f"  📊 Score: ce={recommendation['ce_score']:.4f}, kw_bonus={recommendation['kw_bonus']:.3f}, final={recommendation['final_score']:.4f}")
        
        result = {
            "product_id": recommendation['product_id'],
            "product_name": recommendation['name'],
            "score": recommendation['final_score'],
            "reason": f"Cross-Encoder 점수: {recommendation['ce_score']:.4f}, 키워드 매칭: {recommendation['kw_bonus']:.3f}",
            "product_data": {
                "product_id": recommendation['product_id'],
                "brand": recommendation['brand'],
                "name": recommendation['name'],
                "category": {
                    "major": recommendation['category_major'],
                    "middle": recommendation['category_middle'],
                    "small": recommendation['category_small'],
                },
                "price": {
                    "original_price": recommendation['price_final'],
                    "discounted_price": recommendation['price_final'],
                    "discount_rate": recommendation['discount_rate'],
                },
                "review": {
                    "score": recommendation['review_score'],
                    "count": recommendation['review_count'],
                    "top_keywords": [],
                },
                "description_short": f"{recommendation['name']} - {recommendation['brand']}",
            }
        }
        return result
    
    # 추천 실패 시 기본값 반환
    print("  ⚠️ 추천 실패, 기본값 반환")
    return {
        "product_id": "UNKNOWN",
        "product_name": "추천 실패",
        "score": 0.0,
        "reason": "상품 추천에 실패했습니다.",
    }


