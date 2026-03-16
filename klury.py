"""
🛍️ 식품 쇼핑 인텔리전스 v8.0
마켓컬리 + 네이버 쇼핑 + OpenAI/Gemini 분석
다크모드 최적화
"""
import streamlit as st
import requests
import pandas as pd
import json
import io
import re
import time
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta
from google import genai
from pydantic import BaseModel

st.set_page_config(
    page_title="식품 쇼핑 인텔리전스",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 음료 카테고리 / 브랜드
# ============================================================
BEV_CATS = [
    "", "제로음료", "주스/과즙음료", "사이다", "콜라", "이온음료", "과즙탄산음료",
    "에이드음료", "아이스티음료", "파우더/스무디", "녹차/홍차음료", "전통/곡물음료",
    "아이스티/녹차/홍차", "기타탄산음료"
]

BEV_BRANDS = [
    "", "델몬트", "웅진식품", "자연은", "롯데칠성음료", "웅진", "카프리썬", "참존", "코코팜",
    "돈시몬", "풀무원", "해태에이치티비", "미닛메이드", "매일유업", "홀베리", "서울우유", "일화",
    "모구모구", "팔도", "농심", "스위트컵", "갈아만든배", "아임요", "가야농장", "코카콜라", "과일촌",
    "흥국에프엔비", "오션스프레이", "초록매실", "동원", "과수원", "차그림", "빙그레", "포모나",
    "해태제과", "아임리얼", "세미", "이롬", "노브랜드", "커클랜드", "봉봉", "나탈리스", "카고메",
    "그린트리", "피크닉", "DOLE", "오케이에프", "르씨엘", "롯데", "서울팩토리", "하니앤손스"
]

# ============================================================
# 다크모드 CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; font-size: 15px; }

/* 다크모드 기본 */
.stApp { background-color: #0E1117; color: #E0E0E0; }

.main-header { background: linear-gradient(135deg, #2D1B69 0%, #7B2D8E 50%, #A855F7 100%); padding: 26px 30px; border-radius: 14px; margin-bottom: 22px; }
.main-header h1 { color: #FFFFFF; font-size: 28px; font-weight: 900; margin: 0; }
.main-header p { color: #D8B4FE; font-size: 14px; margin: 5px 0 0; }
.naver-header { background: linear-gradient(135deg, #065F46 0%, #059669 50%, #10B981 100%); padding: 26px 30px; border-radius: 14px; margin-bottom: 22px; }
.naver-header h1 { color: #FFFFFF; font-size: 28px; font-weight: 900; margin: 0; }
.naver-header p { color: #A7F3D0; font-size: 14px; margin: 5px 0 0; }

.metric-row { display: flex; gap: 12px; margin: 16px 0 22px; flex-wrap: wrap; }
.metric-card { flex: 1; min-width: 130px; padding: 18px 14px; border-radius: 14px; text-align: center; color: white; box-shadow: 0 4px 16px rgba(0,0,0,0.3); }
.metric-card .num { font-size: 30px; font-weight: 900; letter-spacing: -1px; }
.metric-card .label { font-size: 12px; opacity: 0.9; margin-top: 3px; }
.mc-purple { background: linear-gradient(135deg, #7C3AED, #A855F7); }
.mc-blue { background: linear-gradient(135deg, #2563EB, #3B82F6); }
.mc-red { background: linear-gradient(135deg, #DC2626, #EF4444); }
.mc-amber { background: linear-gradient(135deg, #D97706, #F59E0B); }
.mc-green { background: linear-gradient(135deg, #059669, #10B981); }
.mc-teal { background: linear-gradient(135deg, #0D9488, #14B8A6); }

.bar-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.bar-label { width: 75px; text-align: right; font-size: 13px; color: #D1D5DB; font-weight: 500; flex-shrink: 0; }
.bar-label-wide { width: 110px; text-align: right; font-size: 13px; color: #D1D5DB; font-weight: 500; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar { height: 22px; border-radius: 5px; }
.bar-purple { background: linear-gradient(90deg, #A855F7, #7C3AED); }
.bar-blue { background: linear-gradient(90deg, #3B82F6, #2563EB); }
.bar-green { background: linear-gradient(90deg, #10B981, #059669); }
.bar-red { background: linear-gradient(90deg, #EF4444, #DC2626); }
.bar-count { font-size: 12px; color: #9CA3AF; white-space: nowrap; }

.section-title { font-size: 17px; font-weight: 700; margin: 18px 0 10px; padding-bottom: 5px; border-bottom: 2px solid #374151; color: #E5E7EB; }
.st-purple { color: #C084FC; } .st-blue { color: #60A5FA; } .st-green { color: #34D399; } .st-red { color: #F87171; }

.product-table { width: 100%; border-collapse: collapse; font-size: 13px; background: #1F2937; }
.product-table thead tr { background: linear-gradient(90deg, #7C3AED, #A855F7); color: white; }
.product-table.naver thead tr { background: linear-gradient(90deg, #059669, #10B981); color: white; }
.product-table th { padding: 11px 7px; font-weight: 600; position: sticky; top: 0; z-index: 10; font-size: 13px; }
.product-table thead tr th { background: inherit; }
.product-table td { padding: 9px 7px; border-bottom: 1px solid #374151; color: #E5E7EB; font-size: 13px; }
.product-table tr:nth-child(even) { background: #111827; }
.product-table tr:hover { background: #312E81; }
.product-table.naver tr:hover { background: #064E3B; }
.product-name a { color: #E5E7EB; text-decoration: none; font-weight: 500; font-size: 13px; }
.product-name a:hover { color: #C084FC; }
.product-table.naver .product-name a:hover { color: #34D399; }
.product-desc { font-size: 11px; color: #6B7280; margin-top: 2px; }
.price-original { text-decoration: line-through; color: #6B7280; font-size: 12px; }
.price-discount { color: #F87171; font-weight: 700; font-size: 14px; }
.discount-rate { color: #F87171; font-weight: 700; }

.badge { display: inline-block; padding: 3px 7px; border-radius: 8px; font-size: 11px; font-weight: 700; margin: 1px; }
.badge-top10 { background: #312E81; color: #C084FC; } .badge-new { background: #1E3A5F; color: #60A5FA; }
.badge-sale { background: #450A0A; color: #FCA5A5; } .badge-low { background: #451A03; color: #FCD34D; }
.badge-naver { background: #064E3B; color: #34D399; } .badge-brand { background: #1E3A5F; color: #60A5FA; }

.detail-panel { border: 1px solid #374151; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.3); background: #1F2937; }
.detail-header { background: linear-gradient(135deg, #7C3AED, #A855F7); padding: 16px 20px; color: white; }
.detail-header.naver { background: linear-gradient(135deg, #059669, #10B981); }
.detail-header h3 { margin: 0; font-size: 16px; font-weight: 700; color: white; }
.detail-header p { margin: 4px 0 0; font-size: 12px; color: rgba(255,255,255,0.8); }
.detail-body { padding: 16px 20px; }
.detail-img { width: 100%; border-radius: 10px; margin-bottom: 14px; max-height: 320px; object-fit: contain; background: #111827; }
.detail-price-box { background: #312E81; border-radius: 10px; padding: 14px; margin-bottom: 14px; }
.detail-price-box.naver { background: #064E3B; }
.detail-price-big { font-size: 24px; font-weight: 900; color: #C084FC; }
.detail-price-box.naver .detail-price-big { color: #34D399; }
.detail-info-grid { display: grid; grid-template-columns: 85px 1fr; gap: 6px 12px; font-size: 14px; margin-bottom: 14px; }
.detail-info-label { color: #9CA3AF; font-weight: 600; } .detail-info-value { color: #E5E7EB; }
.detail-option { padding: 8px 12px; margin: 4px 0; background: #111827; border-radius: 8px; font-size: 13px; display: flex; justify-content: space-between; border: 1px solid #374151; }
.detail-option-name { color: #E5E7EB; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.detail-option-price { color: #C084FC; font-weight: 700; margin-left: 8px; }
.detail-allergy { background: #451A03; border: 1px solid #78350F; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #FCD34D; margin-top: 10px; }
.detail-placeholder { text-align: center; padding: 80px 20px; color: #6B7280; }
.detail-placeholder .icon { font-size: 48px; margin-bottom: 12px; }

.trend-card { border: 1px solid #374151; border-radius: 12px; padding: 18px; margin-bottom: 14px; background: #1F2937; }
.trend-kw { font-size: 18px; font-weight: 900; color: #34D399; margin-bottom: 8px; }
.trend-stat { display: flex; gap: 18px; flex-wrap: wrap; font-size: 14px; color: #9CA3AF; }
.trend-stat b { color: #E5E7EB; }

.trend-table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 10px; background: #1F2937; }
.trend-table th { padding: 10px 8px; background: linear-gradient(90deg, #059669, #10B981); color: white; font-weight: 600; text-align: center; }
.trend-table td { padding: 9px 8px; border-bottom: 1px solid #374151; text-align: center; color: #E5E7EB; }
.trend-table tr:nth-child(even) { background: #111827; }
.trend-table tr:hover { background: #064E3B; }
.trend-rank { font-size: 18px; font-weight: 900; color: #34D399; }

.ai-box { background: #1E1B4B; border: 1px solid #4338CA; border-radius: 14px; padding: 20px; margin: 16px 0; }
.ai-box h3 { color: #A5B4FC; font-size: 17px; font-weight: 700; margin: 0 0 12px; }
.ai-box .ai-content { color: #E0E7FF; font-size: 14px; line-height: 1.8; white-space: pre-wrap; }

section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%); }
section[data-testid="stSidebar"] .stMarkdown h1, section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 { color: #F1F5F9 !important; }
section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] .stMarkdown label { color: #CBD5E1 !important; }

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# API 설정
# ============================================================
KURLY_H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.kurly.com/",
    "Origin": "https://www.kurly.com"
}
KURLY_BASE = "https://api.kurly.com/collection/v2/home/sites/market"
KURLY_SORT = {"신상품순": "0", "추천순": "4", "판매량순": "1", "혜택순": "5", "높은가격순": "3", "낮은가격순": "2"}

# 기존 컬리/OpenAI용 네이버 sort는 남겨도 되지만, 네이버 탭은 아래 NAVER_ANALYSIS_SORT를 사용
NAVER_SORT = {"추천순(정확도)": "sim", "신상품순(날짜)": "date", "낮은가격순": "asc", "높은가격순": "dsc"}

# 새 네이버 탭용 sort
NAVER_ANALYSIS_SORT = {
    "판매 많은순": "sim",   # 실제 판매량 직접값은 아님. 검색 노출 기반 대체.
    "리뷰 많은순": "sim",   # 리뷰수 직접값 미지원. 검색 노출 기반 대체.
    "신상품순": "date"
}

CATEGORY_QUERY_MAP = {
    "제로음료": "제로음료",
    "주스/과즙음료": "주스 과즙음료",
    "사이다": "사이다 음료",
    "콜라": "콜라 음료",
    "이온음료": "이온음료",
    "과즙탄산음료": "과즙탄산음료",
    "에이드음료": "에이드 음료",
    "아이스티음료": "아이스티 음료",
    "파우더/스무디": "파우더 스무디 음료",
    "녹차/홍차음료": "녹차 홍차 음료",
    "전통/곡물음료": "전통 곡물음료",
    "아이스티/녹차/홍차": "아이스티 녹차 홍차",
    "기타탄산음료": "탄산음료",
    "": "음료"
}

# ============================================================
# 키 로딩
# ============================================================
def load_naver_keys():
    for sec in ["naver_shopping", "naver_search"]:
        try:
            cid = st.secrets[sec]["NAVER_CLIENT_ID"]
            csec = st.secrets[sec]["NAVER_CLIENT_SECRET"]
            if cid and cid.strip() and csec and csec.strip():
                return cid.strip(), csec.strip(), sec
        except Exception:
            pass
    return "", "", ""

def load_openai_key():
    try:
        key = st.secrets["openai"]["OPENAI_API_KEY"]
        return key.strip() if key and key.strip() else ""
    except Exception:
        return ""

def load_gemini_key():
    try:
        key = st.secrets["gemini"]["GEMINI_API_KEY"]
        return key.strip() if key and key.strip() else ""
    except Exception:
        return ""

# ============================================================
# OpenAI 분석 (컬리용 유지)
# ============================================================
def ai_analyze(products_info, context="네이버 쇼핑", api_key=""):
    if not api_key:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다."

    prompt = f"""
당신은 한국 식품/음료 시장의 데이터 기반 분석 전문가이자,
15년 경력의 음료 마케팅 기획자입니다.

반드시 아래 규칙을 지켜 답변하세요.

[데이터 해석 주의사항]
- 아래 데이터는 {context}의 검색 노출 상품 목록이며, 시장 전체 판매 데이터가 아닙니다.
- 중복 쇼핑몰 등록, 옵션형 상품, 멀티팩, 번들 SKU가 혼재되어 있습니다.
- 따라서 검색 노출 빈도를 소비자 선호나 실제 판매량으로 단정하지 마세요.
- "인기", "대세", "소비자가 선호" 같은 단정 표현은 피하고,
  "추정", "가능성", "검색 노출 기준", "검토 필요" 같은 표현을 사용하세요.
- 데이터가 부족하거나 불완전하면 반드시 "데이터 한계"를 함께 쓰세요.

[분석 대상 데이터]
{products_info}

[출력 형식]
반드시 아래 8개 항목을 순서대로 출력하세요.
각 항목은 반드시
1) 데이터 한계
2) 분석
3) 시사점
의 3개 소항목을 포함하세요.

### 1. 고유 SKU 분석
### 2. 입수/용량 보정 가격 분석
### 3. 판매채널 구조
### 4. 번들/기획팩 구성 특성
### 5. 맛/플레이버 키워드
### 6. R&D 시사점
### 7. 회의용 멘트
### 8. 마케팅 기획자 페르소나 스크립트

[중요]
- 반드시 1번부터 8번까지 모두 출력하세요.
- 중간에 생략하지 마세요.
- 한국어로 답변하세요.
"""

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "한국 식품/음료 시장 트렌드 분석 전문가. 데이터 기반으로 간결하고 실용적인 인사이트를 제공합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=30
        )

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ API 오류 ({resp.status_code}): {resp.text[:200]}"

    except Exception as e:
        return f"⚠️ 요청 실패: {str(e)}"

# ============================================================
# 컬리 API
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def kurly_load_tree():
    r = requests.get(f"{KURLY_BASE}/category-groups", headers=KURLY_H, timeout=10)
    r.raise_for_status()
    tree = {}
    for c in r.json()["data"]["main"]:
        code, name = str(c["code"]), c["name"]
        tree[code] = {"name": name, "subs": {str(s["code"]): s["name"] for s in c.get("sub_category_groups", [])}}
    return tree

@st.cache_data(ttl=600, show_spinner=False)
def kurly_fetch(cat_code, sort_type, max_items):
    items, pp = [], 96
    for page in range(1, (max_items // pp) + 2):
        try:
            resp = requests.get(
                f"{KURLY_BASE}/product-categories/{cat_code}/products",
                headers=KURLY_H,
                params={"sort_type": sort_type, "page": page, "per_page": pp, "filters": ""},
                timeout=10
            )
            if resp.status_code != 200:
                break
            prods = resp.json().get("data", [])
            if not prods:
                break
            for rank, p in enumerate(prods, start=len(items)+1):
                items.append({
                    "순위": rank,
                    "카테고리코드": cat_code,
                    "상품번호": p.get("no",""),
                    "상품명": p.get("name",""),
                    "설명": p.get("short_description",""),
                    "판매가": p.get("sales_price",0),
                    "할인가": p.get("discounted_price"),
                    "할인율": p.get("discount_rate",0),
                    "리뷰수": p.get("review_count",""),
                    "품절": "Y" if p.get("is_sold_out") else "N",
                    "배송유형": ", ".join(d.get("description","") for d in p.get("delivery_type_infos",[])),
                    "이미지URL": p.get("list_image_url",""),
                    "상품URL": f"https://www.kurly.com/goods/{p.get('no','')}",
                    "저재고": "Y" if p.get("is_low_stock") else "N"
                })
            if len(items) >= max_items:
                break
        except Exception:
            break
    return items[:max_items]

@st.cache_data(ttl=600, show_spinner=False)
def kurly_detail(pno):
    try:
        r = requests.get(
            f"https://www.kurly.com/goods/{pno}",
            headers={"User-Agent": KURLY_H["User-Agent"]},
            timeout=10
        )
        if "__NEXT_DATA__" not in r.text:
            return None
        mk = '__NEXT_DATA__" type="application/json">'
        s = r.text.find(mk) + len(mk)
        e = r.text.find("</script>", s)
        return json.loads(r.text[s:e]).get("props",{}).get("pageProps",{}).get("product")
    except Exception:
        return None

# ============================================================
# 네이버 API 공통
# ============================================================
def clean_html(t):
    return re.sub(r'<[^>]+>', '', t) if t else ""

def safe_int(x, default=0):
    try:
        s = str(x).replace(",", "").strip()
        return int(float(s))
    except Exception:
        return default

@st.cache_data(ttl=300, show_spinner=False)
def naver_search_raw(query, cid, csec, display=100, start=1, sort="sim"):
    headers = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": csec}
    resp = requests.get(
        "https://openapi.naver.com/v1/search/shop.json",
        headers=headers,
        params={"query": query, "display": display, "start": start, "sort": sort},
        timeout=15
    )
    if resp.status_code != 200:
        return []
    return resp.json().get("items", [])

def build_naver_query(category: str, brand: str) -> str:
    base = CATEGORY_QUERY_MAP.get(category, "음료")
    if brand and brand.strip():
        return f"{brand} {base}".strip()
    return base.strip()

def normalize_title(title: str) -> str:
    t = clean_html(title).lower()
    t = re.sub(r"\[[^\]]+\]", " ", t)
    t = re.sub(r"\([^)]+\)", " ", t)

    patterns = [
        r"\b\d+(\.\d+)?\s?(ml|l|g|kg|ea|개|입|병|캔|팩|포)\b",
        r"\b\d+\s?[xX]\s?\d+\b",
        r"\b\d+\s?개입\b",
        r"\b증정\b",
        r"\b기획\b",
        r"\b세트\b",
        r"\b묶음\b",
        r"\b대용량\b",
        r"\b무료배송\b",
        r"\b정품\b",
    ]
    for p in patterns:
        t = re.sub(p, " ", t)

    t = re.sub(r"[^0-9a-zA-Z가-힣\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def extract_core_keywords(title: str, max_words=3) -> str:
    title = normalize_title(title)
    tokens = [t for t in title.split() if t]
    if not tokens:
        return "기타"
    return " ".join(tokens[:max_words])

def make_excel_hyperlink(url: str, label: str = "구매링크") -> str:
    url = (url or "").replace('"', '""')
    label = (label or "구매링크").replace('"', '""')
    if not url:
        return ""
    return f'=HYPERLINK("{url}","{label}")'

def make_excel_image_formula(url: str) -> str:
    url = (url or "").replace('"', '""')
    if not url:
        return ""
    return f'=IMAGE("{url}")'

def collect_naver_products(query: str, cid: str, csec: str, sort_label: str, limit: int = 500) -> pd.DataFrame:
    sort_api = NAVER_ANALYSIS_SORT.get(sort_label, "sim")
    rows = []

    for start in [1, 101, 201, 301, 401]:
        if len(rows) >= limit:
            break

        items = naver_search_raw(query, cid, csec, display=100, start=start, sort=sort_api)
        if not items:
            break

        for idx, item in enumerate(items, start=start):
            rows.append({
                "rank": idx,
                "query": query,
                "title": clean_html(item.get("title", "")),
                "normalized_title": normalize_title(item.get("title", "")),
                "core_group": extract_core_keywords(item.get("title", ""), 3),
                "link": item.get("link", ""),
                "image": item.get("image", ""),
                "lprice": safe_int(item.get("lprice", 0)),
                "hprice": safe_int(item.get("hprice", 0)),
                "mallName": item.get("mallName", ""),
                "brand": item.get("brand", ""),
                "maker": item.get("maker", ""),
                "category1": item.get("category1", ""),
                "category2": item.get("category2", ""),
                "category3": item.get("category3", ""),
                "category4": item.get("category4", ""),
                "productType": item.get("productType", ""),
                "productId": item.get("productId", "")
            })

        if len(items) < 100:
            break

        time.sleep(0.1)

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=[
            "rank", "query", "title", "normalized_title", "core_group", "link", "image",
            "lprice", "hprice", "mallName", "brand", "maker", "category1", "category2",
            "category3", "category4", "productType", "productId"
        ])
    return df.head(limit).reset_index(drop=True)

def aggregate_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "normalized_title", "대표상품명", "대표링크", "대표이미지", "대표판매처",
            "대표브랜드", "대표제조사", "핵심제품군", "상품수", "평균최저가",
            "최저가최소", "최저가최대", "평균순위원점수", "최고순위",
            "추천점수", "판매순위점수", "순위점수"
        ])

    work = df.copy()
    total_n = len(work)
    work["rank_score_raw"] = work["rank"].apply(lambda x: max(total_n - x + 1, 1))

    grouped = (
        work.groupby("normalized_title", dropna=False)
        .agg(
            대표상품명=("title", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
            대표링크=("link", "first"),
            대표이미지=("image", "first"),
            대표판매처=("mallName", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
            대표브랜드=("brand", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
            대표제조사=("maker", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
            핵심제품군=("core_group", lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]),
            상품수=("title", "count"),
            평균최저가=("lprice", "mean"),
            최저가최소=("lprice", "min"),
            최저가최대=("lprice", "max"),
            평균순위원점수=("rank_score_raw", "mean"),
            최고순위=("rank", "min")
        )
        .reset_index()
    )

    max_count = max(grouped["상품수"].max(), 1)
    max_rank = max(grouped["평균순위원점수"].max(), 1)

    grouped["추천점수"] = (grouped["상품수"] / max_count * 100).round(2)
    grouped["판매순위점수"] = (grouped["평균순위원점수"] / max_rank * 100).round(2)
    grouped["순위점수"] = (grouped["판매순위점수"] * 0.7 + grouped["추천점수"] * 0.3).round(2)
    grouped["평균최저가"] = grouped["평균최저가"].round(0).astype(int)

    grouped = grouped.sort_values(
        ["순위점수", "상품수", "최고순위"],
        ascending=[False, False, True]
    ).reset_index(drop=True)

    return grouped

# ============================================================
# 규칙 기반 flavor/trend 사전
# ============================================================
FLAVOR_DICT = {
    "레몬": ["레몬", "lemon"],
    "포도": ["포도", "grape"],
    "복숭아": ["복숭아", "peach"],
    "청포도": ["청포도"],
    "오렌지": ["오렌지", "orange"],
    "사과": ["사과", "apple"],
    "자몽": ["자몽", "grapefruit"],
    "망고": ["망고", "mango"],
    "딸기": ["딸기", "strawberry"],
    "파인애플": ["파인애플", "pineapple"],
    "유자": ["유자"],
    "매실": ["매실"],
    "배": ["배"],
    "석류": ["석류"],
    "블루베리": ["블루베리"],
    "콜라": ["콜라", "cola"],
    "사이다": ["사이다", "cider"],
    "녹차": ["녹차", "green tea"],
    "홍차": ["홍차", "black tea"],
    "아이스티": ["아이스티", "ice tea"],
    "커피": ["커피", "coffee"],
    "요거트": ["요거트", "yogurt", "요구르트"],
}

TREND_DICT = {
    "제로/저당": ["제로", "zero", "무설탕", "저당", "sugar free"],
    "기능성/건강": ["비타민", "콜라겐", "프로틴", "단백질", "유산균", "식이섬유", "건강"],
    "과일감성": ["과즙", "fruit", "과일", "자연은"],
    "카페형": ["에이드", "스무디", "티", "tea", "라떼"],
    "탄산/청량": ["탄산", "sparkling", "사이다", "콜라"],
    "RTD/간편": ["캔", "병", "파우치", "팩"],
    "프리미엄": ["착즙", "nfc", "100%", "프리미엄"],
}

FUNCTIONAL_DICT = {
    "비타민": ["비타민", "vitamin"],
    "에너지": ["에너지", "energy"],
    "프로틴": ["프로틴", "protein", "단백질"],
    "유산균": ["유산균", "probiotic"],
    "식이섬유": ["식이섬유", "fiber"],
    "전해질": ["전해질", "이온"],
    "제로슈거": ["제로", "zero", "무설탕", "저당"]
}

def match_tags(text: str, dictionary: dict) -> list:
    t = normalize_title(text)
    found = []
    for label, patterns in dictionary.items():
        for p in patterns:
            if p.lower() in t:
                found.append(label)
                break
    return found

def enrich_rule_based_tags(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        out = df.copy()
        out["flavor_tags"] = [[] for _ in range(len(out))]
        out["trend_tags"] = [[] for _ in range(len(out))]
        out["functional_tags"] = [[] for _ in range(len(out))]
        return out

    out = df.copy()
    out["flavor_tags"] = out["대표상품명"].apply(lambda x: match_tags(x, FLAVOR_DICT))
    out["trend_tags"] = out["대표상품명"].apply(lambda x: match_tags(x, TREND_DICT))
    out["functional_tags"] = out["대표상품명"].apply(lambda x: match_tags(x, FUNCTIONAL_DICT))
    return out

def explode_tag_stats(df: pd.DataFrame, tag_col: str, score_col="순위점수") -> pd.DataFrame:
    if df.empty or tag_col not in df.columns:
        return pd.DataFrame(columns=["태그", "빈도", "평균순위점수", "평균가격"])

    rows = []
    for _, r in df.iterrows():
        tags = r[tag_col]
        if not isinstance(tags, list):
            continue
        for t in tags:
            rows.append({
                "태그": t,
                "순위점수": r.get(score_col, 0),
                "평균최저가": r.get("평균최저가", 0)
            })

    if not rows:
        return pd.DataFrame(columns=["태그", "빈도", "평균순위점수", "평균가격"])

    temp = pd.DataFrame(rows)
    stat = (
        temp.groupby("태그", dropna=False)
        .agg(
            빈도=("태그", "count"),
            평균순위점수=("순위점수", "mean"),
            평균가격=("평균최저가", "mean")
        )
        .reset_index()
        .sort_values(["빈도", "평균순위점수"], ascending=[False, False])
        .reset_index(drop=True)
    )
    stat["평균순위점수"] = stat["평균순위점수"].round(2)
    stat["평균가격"] = stat["평균가격"].round(0).astype(int)
    return stat

# ============================================================
# Gemini structured output
# ============================================================
class ProductInsight(BaseModel):
    product_name: str
    normalized_name: str
    primary_flavor: str
    secondary_flavors: list[str]
    trend_keywords: list[str]
    functional_positioning: list[str]
    package_format: str
    sugar_positioning: str
    confidence: float

class InsightBatch(BaseModel):
    items: list[ProductInsight]

def call_gemini_extract(df: pd.DataFrame, gemini_client, batch_size: int = 25) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "normalized_title", "gemini_primary_flavor", "gemini_secondary_flavors",
            "gemini_trend_keywords", "gemini_functional_positioning",
            "gemini_package_format", "gemini_sugar_positioning", "gemini_confidence"
        ])

    results = []
    rows = df[["대표상품명", "normalized_title"]].copy()

    for start_idx in range(0, len(rows), batch_size):
        batch = rows.iloc[start_idx:start_idx+batch_size].copy()
        product_lines = []

        for _, r in batch.iterrows():
            product_lines.append({
                "product_name": r["대표상품명"],
                "normalized_name": r["normalized_title"]
            })

        prompt = f"""
다음은 한국 네이버 쇼핑 음료 상품명 목록이다.
각 상품에 대해 아래 항목을 추출하라.

규칙:
1) primary_flavor는 가장 대표적인 1개 flavor만.
2) secondary_flavors는 보조 flavor들.
3) trend_keywords는 소비자/시장 관점 키워드 2~5개.
4) functional_positioning은 건강/기능/편의/프리미엄 등의 포지셔닝.
5) package_format은 캔/병/팩/파우치/분말/기타 중 하나로 추론.
6) sugar_positioning은 제로/저당/일반/불명 중 하나.
7) confidence는 0~1.

입력 데이터:
{json.dumps(product_lines, ensure_ascii=False, indent=2)}
"""

        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": InsightBatch
                }
            )
            parsed = response.parsed
            if parsed and hasattr(parsed, "items"):
                for item in parsed.items:
                    results.append({
                        "normalized_title": item.normalized_name,
                        "gemini_primary_flavor": item.primary_flavor,
                        "gemini_secondary_flavors": item.secondary_flavors,
                        "gemini_trend_keywords": item.trend_keywords,
                        "gemini_functional_positioning": item.functional_positioning,
                        "gemini_package_format": item.package_format,
                        "gemini_sugar_positioning": item.sugar_positioning,
                        "gemini_confidence": item.confidence
                    })
        except Exception:
            for _, r in batch.iterrows():
                results.append({
                    "normalized_title": r["normalized_title"],
                    "gemini_primary_flavor": "",
                    "gemini_secondary_flavors": [],
                    "gemini_trend_keywords": [],
                    "gemini_functional_positioning": [],
                    "gemini_package_format": "",
                    "gemini_sugar_positioning": "",
                    "gemini_confidence": 0.0
                })

    out = pd.DataFrame(results)
    if out.empty:
        out = pd.DataFrame(columns=[
            "normalized_title", "gemini_primary_flavor", "gemini_secondary_flavors",
            "gemini_trend_keywords", "gemini_functional_positioning",
            "gemini_package_format", "gemini_sugar_positioning", "gemini_confidence"
        ])
    return out.drop_duplicates(subset=["normalized_title"]).reset_index(drop=True)

def make_summary_payload(agg_df: pd.DataFrame, flavor_stats: pd.DataFrame, trend_stats: pd.DataFrame) -> dict:
    top_products = []
    for _, r in agg_df.head(15).iterrows():
        top_products.append({
            "대표상품명": r.get("대표상품명", ""),
            "브랜드": r.get("대표브랜드", ""),
            "핵심제품군": r.get("핵심제품군", ""),
            "상품수": int(r.get("상품수", 0)),
            "평균최저가": int(r.get("평균최저가", 0)),
            "순위점수": float(r.get("순위점수", 0))
        })

    top_flavors = flavor_stats.head(10).to_dict(orient="records") if not flavor_stats.empty else []
    top_trends = trend_stats.head(10).to_dict(orient="records") if not trend_stats.empty else []

    return {
        "top_products": top_products,
        "top_flavors": top_flavors,
        "top_trends": top_trends,
        "product_count": int(len(agg_df))
    }

def generate_market_report(summary_payload: dict, user_query: str, sort_label: str, start_date_val, end_date_val, gemini_client) -> str:
    prompt = f"""
당신은 식품 음료 카테고리 분석가다.
아래 데이터를 바탕으로 한국 음료 시장 관점의 분석보고서를 한국어로 작성하라.

조건:
1) 보고서는 실무형으로 작성
2) '시장요약', '핵심 플레이버 트렌드', '브랜드/제품 시사점', '가격대 시사점', '신제품 개발 제안', '주의할 한계' 항목 포함
3) 과장하지 말고 데이터 기반으로만 해석
4) 최소 8문단 이상
5) 표나 마크다운 리스트를 적절히 사용
6) 네이버 쇼핑 검색 결과 기반이라는 점을 한계에 명시

분석 조건:
- 검색어: {user_query}
- 정렬: {sort_label}
- 기간표시: {start_date_val} ~ {end_date_val}

데이터:
{json.dumps(summary_payload, ensure_ascii=False, indent=2)}
"""
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text if hasattr(response, "text") else "보고서 생성 실패"
    except Exception as e:
        return f"보고서 생성 실패: {e}"

# ============================================================
# 공통 렌더링/다운로드
# ============================================================
def render_metrics(cards):
    h = '<div class="metric-row">'
    for num, label, cls in cards:
        h += f'<div class="metric-card {cls}"><div class="num">{num}</div><div class="label">{label}</div></div>'
    st.markdown(h + '</div>', unsafe_allow_html=True)

def render_bars(title, tcls, data, bcls, wide=False, pct=False, total=1):
    if not data:
        return
    mx = max(data.values()) if data.values() else 1
    lc = "bar-label-wide" if wide else "bar-label"
    h = f'<div class="section-title {tcls}">{title}</div>'
    for lb, cnt in data.items():
        w = int(cnt / mx * 260) if mx > 0 else 0
        p = f" ({cnt/total*100:.0f}%)" if pct and total > 0 else ""
        h += f'<div class="bar-row"><div class="{lc}">{lb}</div><div class="bar {bcls}" style="width:{w}px;"></div><div class="bar-count">{cnt}개{p}</div></div>'
    st.markdown(h, unsafe_allow_html=True)

def to_excel(df):
    buf = io.BytesIO()
    cols = [c for c in df.columns if c not in ["이미지URL","그룹키"]]
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        df[cols].to_excel(w, sheet_name="전체", index=False)
    return buf.getvalue()

def to_csv(df):
    cols = [c for c in df.columns if c not in ["이미지URL","그룹키"]]
    return df[cols].to_csv(index=False).encode("utf-8-sig")

def prepare_naver_csv_dataframe(agg_df: pd.DataFrame, query: str, sort_label: str, start_date_val, end_date_val) -> pd.DataFrame:
    if agg_df.empty:
        return pd.DataFrame()

    out = agg_df.copy()
    out["분석시작일"] = str(start_date_val)
    out["분석종료일"] = str(end_date_val)
    out["검색어"] = query
    out["정렬"] = sort_label
    out["구매링크"] = out["대표링크"].apply(lambda x: make_excel_hyperlink(x, "바로가기"))
    out["이미지"] = out["대표이미지"].apply(make_excel_image_formula)

    for col in [
        "flavor_tags", "trend_tags", "functional_tags",
        "gemini_secondary_flavors", "gemini_trend_keywords", "gemini_functional_positioning",
        "all_flavor_tags", "all_trend_tags"
    ]:
        if col in out.columns:
            out[col] = out[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

    rename_map = {
        "대표상품명": "상품명",
        "대표브랜드": "브랜드",
        "대표제조사": "제조사",
        "대표판매처": "판매처",
        "대표링크": "원본링크",
        "대표이미지": "원본이미지URL",
        "평균최저가": "평균최저가(원)",
        "최저가최소": "최저가최소(원)",
        "최저가최대": "최저가최대(원)"
    }
    out = out.rename(columns=rename_map)
    return out

# ============================================================
# 컬리용 AI 텍스트
# ============================================================
def build_ai_products_text(df, platform="네이버", top_n=20):
    lines = []
    price_col = "최저가" if "최저가" in df.columns else "판매가"
    brand_col = "브랜드" if "브랜드" in df.columns else None
    for _, row in df.head(top_n).iterrows():
        parts = [f"{row['순위']}위: {row['상품명']}"]
        parts.append(f"₩{row[price_col]:,}")
        if brand_col and row.get(brand_col):
            parts.append(f"[{row[brand_col]}]")
        if "쇼핑몰" in df.columns and row.get("쇼핑몰"):
            parts.append(f"({row['쇼핑몰']})")
        if "카테고리명" in df.columns and row.get("카테고리명"):
            parts.append(f"({row['카테고리명']})")
        lines.append(" | ".join(parts))
    return "\n".join(lines)

# ============================================================
# 🟣 컬리 탭 (그대로 유지)
# ============================================================
def tab_kurly():
    tree = kurly_load_tree()
    oai_key = load_openai_key()
    if "k_df" not in st.session_state:
        st.session_state.k_df = None
    if "k_sel" not in st.session_state:
        st.session_state.k_sel = None

    with st.sidebar:
        st.markdown("### 🟣 컬리 설정")
        mo = {info["name"]: code for code, info in tree.items()}
        sm_names = st.multiselect("대분류", list(mo.keys()), [], placeholder="선택", key="k_main")
        smc = [mo[n] for n in sm_names]
        so = {}
        if smc:
            for mc in smc:
                for sc, sn in tree[mc]["subs"].items():
                    so[f"{tree[mc]['name']} > {sn}"] = sc
        if so:
            asub = st.checkbox("✅ 하위 전체", True, key="k_allsub")
            ssn = list(so.keys()) if asub else st.multiselect("하위", list(so.keys()), [], key="k_sub")
            ssc = [so[n] for n in ssn]
        else:
            ssc = []
        st.markdown("---")
        ks = st.selectbox("정렬", list(KURLY_SORT.keys()), 0, key="k_sort")
        km = st.slider("최대 출력", 10, 300, 100, 10, key="k_max")
        kw = st.text_input("키워드", placeholder="콤부차,제로", key="k_kw")
        kp = st.slider("가격", 0, 100000, (0, 100000), 1000, format="₩%d", key="k_pr")
        st.markdown("---")
        st.markdown("**📅 조사 기간 (참고용)**")
        k_d1 = st.date_input("시작일", date.today() - timedelta(days=30), key="k_d1")
        k_d2 = st.date_input("종료일", date.today(), key="k_d2")
        st.caption("※ 컬리 API에 날짜 필터 미지원 → 신상품순 정렬로 최신성 확보")
        ke = st.checkbox("품절 제외", True, key="k_excl")
        kr = st.button("🔍 컬리 수집", type="primary", use_container_width=True, disabled=not smc, key="k_run")

    st.markdown('<div class="main-header"><h1>🛒 마켓컬리 신제품 인텔리전스</h1><p>카테고리별 트렌드 · 상품 선택 시 우측 상세 · AI 분석</p></div>', unsafe_allow_html=True)

    if kr and smc:
        tgts = []
        if ssc:
            for sc in ssc:
                nm = sc
                for info in tree.values():
                    if sc in info["subs"]:
                        nm = info["subs"][sc]
                        break
                tgts.append((sc, nm))
        else:
            for mc in smc:
                tgts.append((mc, tree[mc]["name"]))
        if tgts:
            pg = st.progress(0, "📡 수집...")
            ad = []
            for i, (code, name) in enumerate(tgts):
                pg.progress((i+1)/len(tgts), f"📡 [{i+1}/{len(tgts)}] {name}")
                its = kurly_fetch(code, KURLY_SORT[ks], km)
                for it in its:
                    it["카테고리명"] = name
                ad.extend(its)
            pg.empty()
            if ad:
                df = pd.DataFrame(ad).drop_duplicates(subset=["상품번호"], keep="first")
                if kw.strip():
                    kws = [k.strip() for k in kw.split(",") if k.strip()]
                    df = df[df["상품명"].str.contains("|".join(kws), case=False, na=False)]
                if ke:
                    df = df[df["품절"]=="N"]
                pmin, pmax = kp
                df = df[(df["판매가"]>=pmin)&(df["판매가"]<=pmax)].head(km).reset_index(drop=True)
                st.session_state.k_df = df
                st.session_state.k_sel = None

    df = st.session_state.k_df
    if df is None or len(df) == 0:
        st.markdown('<div style="text-align:center;padding:60px;color:#6B7280;"><div style="font-size:48px;">🛍️</div><div style="font-size:18px;font-weight:600;color:#C084FC;">사이드바에서 카테고리 선택 → 수집 시작</div></div>', unsafe_allow_html=True)
        return

    total = len(df)
    avg_p = df["판매가"].mean()
    dc = (df["할인율"]>0).sum()
    ad = df.loc[df["할인율"]>0,"할인율"].mean() if dc > 0 else 0
    lc = (df["저재고"]=="Y").sum()
    render_metrics([
        (f"{total:,}","총 상품","mc-purple"),
        (f"₩{avg_p:,.0f}","평균가격","mc-blue"),
        (f"{dc:,}",f"할인(평균{ad:.0f}%)","mc-red"),
        (f"{lc:,}","품절임박⚡","mc-amber")
    ])

    if oai_key and total > 0:
        if st.button("🤖 AI 트렌드 분석 (컬리 TOP 상품)", key="k_ai"):
            with st.spinner("🤖 AI 분석 중..."):
                txt = build_ai_products_text(df, "마켓컬리", 20)
                result = ai_analyze(txt, f"마켓컬리 ({', '.join(sm_names)})", oai_key)
            st.markdown(f'<div class="ai-box"><h3>🤖 AI 트렌드 분석</h3><div class="ai-content">{result}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        bins = [0,3000,5000,10000,20000,30000,50000,float("inf")]
        labels = ["~3천","3~5천","5천~1만","1~2만","2~3만","3~5만","5만~"]
        df["가격대"] = pd.cut(df["판매가"], bins=bins, labels=labels)
        pd_d = df["가격대"].value_counts().sort_index()
        render_bars("💰 가격대","st-purple",{str(k):int(v) for k,v in pd_d.items() if v>0},"bar-purple",pct=True,total=total)
    with c2:
        if df["카테고리명"].nunique()>1:
            cd = df["카테고리명"].value_counts().head(10)
            render_bars("📁 카테고리별","st-blue",{str(k)[:12]:int(v) for k,v in cd.items()},"bar-blue",wide=True)

    st.markdown("---")
    col_l, col_r = st.columns([6, 4])
    with col_l:
        pl = [f"[{r['순위']}] {r['상품명'][:28]} | ₩{r['판매가']:,}" for _, r in df.iterrows()]
        pn = [r["상품번호"] for _, r in df.iterrows()]
        ci = 0
        if st.session_state.k_sel and st.session_state.k_sel in pn:
            ci = pn.index(st.session_state.k_sel)
        si = st.selectbox("🔍 상품 선택 → 우측 상세", range(len(pl)), ci, format_func=lambda i: pl[i], key="k_psel")
        st.session_state.k_sel = pn[si]
        rows = ""
        for _, row in df.iterrows():
            nm = str(row["상품명"])[:36]
            url = row["상품URL"]
            if row["할인가"] and row["할인율"] and row["할인율"]>0:
                ph = f'<span class="price-original">₩{row["판매가"]:,}</span><br><span class="price-discount">₩{row["할인가"]:,}</span>'
                dh = f'<span class="discount-rate">{row["할인율"]}%</span>'
            else:
                ph = f'₩{row["판매가"]:,}'
                dh = "-"
            bd = ""
            if row["순위"]<=10:
                bd += '<span class="badge badge-top10">🆕TOP10</span>'
            elif row["순위"]<=30:
                bd += '<span class="badge badge-new">NEW</span>'
            if row["할인율"] and row["할인율"]>=20:
                bd += '<span class="badge badge-sale">🔥SALE</span>'
            if row.get("저재고")=="Y":
                bd += '<span class="badge badge-low">⚡임박</span>'
            cn = str(row.get("카테고리명",""))[:8]
            rows += f'<tr><td style="text-align:center;color:#C084FC;font-weight:700;">{row["순위"]}</td><td style="text-align:center;font-size:12px;">{cn}</td><td class="product-name"><a href="{url}" target="_blank">{nm}</a></td><td style="text-align:right;">{ph}</td><td style="text-align:center;">{dh}</td><td style="text-align:center;">{bd}</td></tr>'
        st.markdown(f'<div style="max-height:520px;overflow-y:auto;border:1px solid #374151;border-radius:10px;"><table class="product-table"><thead><tr><th>#</th><th>카테고리</th><th>상품명</th><th>가격</th><th>할인</th><th>상태</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📥 엑셀", to_excel(df), f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", type="primary", key="k_dl")
        with d2:
            st.download_button("📥 CSV", to_csv(df), f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", type="secondary", key="k_csv")

    with col_r:
        st.markdown('<div class="section-title st-purple">📦 상품 상세</div>', unsafe_allow_html=True)
        pno = st.session_state.k_sel
        if pno:
            with st.spinner("로딩..."):
                det = kurly_detail(pno)
            if det:
                name = det.get("name","")
                img = det.get("mainImageUrl","")
                bp = det.get("basePrice",0)
                dpv = det.get("discountedPrice")
                drv = det.get("discountRate",0)
                prh = f'<span class="detail-price-big">₩{dpv:,}</span> <span style="text-decoration:line-through;color:#6B7280;">₩{bp:,}</span> <span style="background:#EF4444;color:white;padding:2px 8px;border-radius:10px;font-size:13px;font-weight:700;">{drv}%</span>' if dpv and drv and drv>0 else f'<span class="detail-price-big">₩{bp:,}</span>'
                vol = det.get("volume","")
                seller = det.get("sellerName","")
                brand = det.get("brandInfo",{}).get("name","-") if det.get("brandInfo") else "-"
                rc = det.get("reviewCount",0)
                allergy = det.get("allergy","")
                delivery = ", ".join(str(d) for d in det.get("deliveryTypeNames",[]))
                opts = "".join(f'<div class="detail-option"><span class="detail-option-name">{dp.get("name","")[:30]}</span><span class="detail-option-price">₩{dp.get("basePrice",0):,}</span></div>' for dp in det.get("dealProducts",[])[:6])
                alh = f'<div class="detail-allergy">⚠️ {allergy.replace(chr(10),"<br>")}</div>' if allergy and allergy.strip() else ""
                st.markdown(f'<div class="detail-panel"><div class="detail-header"><h3>📦 {name}</h3></div><div class="detail-body"><img class="detail-img" src="{img}" onerror="this.style.display=\'none\'"><div class="detail-price-box">{prh}</div><div class="detail-info-grid"><span class="detail-info-label">용량</span><span class="detail-info-value">{vol}</span><span class="detail-info-label">배송</span><span class="detail-info-value">{delivery}</span><span class="detail-info-label">판매자</span><span class="detail-info-value">{seller}</span><span class="detail-info-label">브랜드</span><span class="detail-info-value">{brand}</span><span class="detail-info-label">리뷰</span><span class="detail-info-value">⭐ {rc:,}개</span></div>{opts}{alh}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div style="text-align:center;margin-top:12px;"><a href="https://www.kurly.com/goods/{pno}" target="_blank" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7C3AED,#A855F7);color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;">🔗 컬리에서 보기</a></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">⚠️</div><div>상세 로딩 실패</div></div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">👆</div><div style="font-size:15px;font-weight:600;color:#C084FC;">상품을 선택하세요</div></div></div>', unsafe_allow_html=True)

# ============================================================
# 🟢 네이버 쇼핑 탭 (교체 버전)
# ============================================================
def tab_naver():
    if "n_raw_df" not in st.session_state:
        st.session_state.n_raw_df = None
    if "n_agg_df" not in st.session_state:
        st.session_state.n_agg_df = None
    if "n_flavor_stats" not in st.session_state:
        st.session_state.n_flavor_stats = None
    if "n_trend_stats" not in st.session_state:
        st.session_state.n_trend_stats = None
    if "n_report" not in st.session_state:
        st.session_state.n_report = ""
    if "n_csv_df" not in st.session_state:
        st.session_state.n_csv_df = None
    if "n_query" not in st.session_state:
        st.session_state.n_query = ""
    if "n_detail_idx" not in st.session_state:
        st.session_state.n_detail_idx = 0

    auto_id, auto_sec, auto_src = load_naver_keys()
    gemini_key = load_gemini_key()

    with st.sidebar:
        st.markdown("### 🟢 네이버 쇼핑 설정")

        if auto_id and auto_sec:
            st.success(f"🔑 네이버 API 키 로딩 ({auto_src})")
            n_id, n_sec = auto_id, auto_sec
        else:
            st.warning("네이버 API 키 없음")
            n_id = st.text_input("Client ID", type="password", key="n_id")
            n_sec = st.text_input("Client Secret", type="password", key="n_sec")

        if gemini_key:
            st.success("✨ Gemini API 키 로딩")
        else:
            st.warning("Gemini API 키 없음")
            gemini_key = st.text_input("Gemini API Key", type="password", key="g_key")

        st.markdown("---")
        n_bev = st.selectbox("음료분류", BEV_CATS, 0, key="n_bev", format_func=lambda x: x if x else "전체 (음료)")
        n_brand = st.selectbox("브랜드", BEV_BRANDS, 0, key="n_brand", format_func=lambda x: x if x else "전체")
        n_sort_label = st.selectbox("검색추천순", list(NAVER_ANALYSIS_SORT.keys()), 0, key="n_sort2")
        n_limit = st.slider("최대 결과", 100, 500, 500, 100, key="n_max2")

        st.markdown("---")
        st.markdown("**📅 검색 기간**")
        nd1 = st.date_input("시작일", date.today()-timedelta(days=30), key="n_d1")
        nd2 = st.date_input("종료일", date.today(), key="n_d2")
        st.caption("※ 네이버 쇼핑 검색 API는 날짜 직접 필터를 지원하지 않음. 분석 조건 표시용으로 사용")
        nr = st.button("🟢 네이버 분석 실행", type="primary", use_container_width=True, disabled=not(n_id and n_sec and gemini_key), key="n_run2")

    st.markdown('<div class="naver-header"><h1>🟢 네이버 쇼핑 인텔리전스</h1><p>중복 통합 · 플레이버/트렌드 추출 · Gemini 분석보고서</p></div>', unsafe_allow_html=True)

    if not (n_id and n_sec):
        st.info("사이드바에 네이버 API 키를 설정해주세요.")
        return
    if not gemini_key:
        st.info("사이드바에 Gemini API 키를 설정해주세요.")
        return

    if nd1 > nd2:
        st.error("시작일이 종료일보다 늦을 수 없습니다.")
        return

    if nr:
        query = build_naver_query(n_bev, n_brand)

        try:
            gemini_client = genai.Client(api_key=gemini_key)
        except Exception as e:
            st.error(f"Gemini 클라이언트 생성 실패: {e}")
            return

        with st.spinner(f"🔍 '{query}' 검색 · 중복통합 · Gemini 분석 중..."):
            raw_df = collect_naver_products(query, n_id, n_sec, n_sort_label, n_limit)

            required_cols = [
                "rank", "query", "title", "normalized_title", "core_group", "link", "image",
                "lprice", "mallName", "brand", "maker"
            ]
            for col in required_cols:
                if col not in raw_df.columns:
                    raw_df[col] = ""

            agg_df = aggregate_duplicates(raw_df)

            for col in ["대표상품명", "normalized_title", "평균최저가", "순위점수", "상품수"]:
                if col not in agg_df.columns:
                    agg_df[col] = "" if col in ["대표상품명", "normalized_title"] else 0

            agg_df = enrich_rule_based_tags(agg_df)

            gemini_df = call_gemini_extract(agg_df, gemini_client)
            if not gemini_df.empty:
                agg_df = agg_df.merge(gemini_df, on="normalized_title", how="left")
            else:
                agg_df["gemini_primary_flavor"] = ""
                agg_df["gemini_secondary_flavors"] = [[] for _ in range(len(agg_df))]
                agg_df["gemini_trend_keywords"] = [[] for _ in range(len(agg_df))]
                agg_df["gemini_functional_positioning"] = [[] for _ in range(len(agg_df))]
                agg_df["gemini_package_format"] = ""
                agg_df["gemini_sugar_positioning"] = ""
                agg_df["gemini_confidence"] = 0.0

            def merge_flavors(row):
                vals = []
                if isinstance(row.get("flavor_tags"), list):
                    vals.extend(row["flavor_tags"])
                if row.get("gemini_primary_flavor"):
                    vals.append(row["gemini_primary_flavor"])
                if isinstance(row.get("gemini_secondary_flavors"), list):
                    vals.extend(row["gemini_secondary_flavors"])
                vals = [v for v in vals if v]
                return list(dict.fromkeys(vals))

            def merge_trends(row):
                vals = []
                if isinstance(row.get("trend_tags"), list):
                    vals.extend(row["trend_tags"])
                if isinstance(row.get("gemini_trend_keywords"), list):
                    vals.extend(row["gemini_trend_keywords"])
                vals = [v for v in vals if v]
                return list(dict.fromkeys(vals))

            agg_df["all_flavor_tags"] = agg_df.apply(merge_flavors, axis=1)
            agg_df["all_trend_tags"] = agg_df.apply(merge_trends, axis=1)

            flavor_stats = explode_tag_stats(agg_df.rename(columns={"all_flavor_tags": "flavor_stat_col"}), "flavor_stat_col")
            trend_stats = explode_tag_stats(agg_df.rename(columns={"all_trend_tags": "trend_stat_col"}), "trend_stat_col")

            summary_payload = make_summary_payload(agg_df, flavor_stats, trend_stats)
            report_text = generate_market_report(summary_payload, query, n_sort_label, nd1, nd2, gemini_client)
            csv_df = prepare_naver_csv_dataframe(agg_df, query, n_sort_label, nd1, nd2)

            st.session_state.n_raw_df = raw_df
            st.session_state.n_agg_df = agg_df
            st.session_state.n_flavor_stats = flavor_stats
            st.session_state.n_trend_stats = trend_stats
            st.session_state.n_report = report_text
            st.session_state.n_csv_df = csv_df
            st.session_state.n_query = query
            st.session_state.n_detail_idx = 0

    raw_df = st.session_state.n_raw_df
    agg_df = st.session_state.n_agg_df
    flavor_stats = st.session_state.n_flavor_stats
    trend_stats = st.session_state.n_trend_stats
    report_text = st.session_state.n_report
    csv_df = st.session_state.n_csv_df
    query = st.session_state.n_query

    if raw_df is None or agg_df is None or len(raw_df) == 0:
        st.markdown('<div style="text-align:center;padding:60px;color:#6B7280;"><div style="font-size:48px;">🔍</div><div style="font-size:18px;font-weight:600;color:#34D399;">검색 조건을 설정하고 시작하세요</div></div>', unsafe_allow_html=True)
        return

    total_raw = len(raw_df)
    total_agg = len(agg_df)
    avg_price = agg_df["평균최저가"].mean() if "평균최저가" in agg_df.columns and len(agg_df) > 0 else 0
    brand_count = agg_df["대표브랜드"].nunique() if "대표브랜드" in agg_df.columns else 0

    render_metrics([
        (f"{total_raw:,}", "원본 상품수", "mc-green"),
        (f"{total_agg:,}", "중복통합 후", "mc-teal"),
        (f"₩{avg_price:,.0f}", "평균최저가", "mc-blue"),
        (f"{brand_count:,}", "브랜드수", "mc-amber")
    ])

    st.markdown('<div class="section-title st-green">🏆 요약 트렌드 TOP 10</div>', unsafe_allow_html=True)
    trows = ""
    for idx, row in agg_df.head(10).iterrows():
        trows += f'<tr><td><span class="trend-rank">{idx+1}</span></td><td style="text-align:left;font-weight:600;color:#E5E7EB;">{str(row["대표상품명"])[:40]}</td><td style="color:#D1D5DB;">{row.get("대표브랜드","")}</td><td style="color:#D1D5DB;">₩{int(row["평균최저가"]):,}</td><td style="color:#D1D5DB;">{row["상품수"]}</td><td style="font-weight:700;color:#34D399;">{row["순위점수"]}</td></tr>'
    st.markdown(f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #374151;"><table class="trend-table"><thead><tr><th>#</th><th>제품군</th><th>브랜드</th><th>평균가</th><th>상품수</th><th>종합점수</th></tr></thead><tbody>{trows}</tbody></table></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("플레이버 통계")
    c1, c2 = st.columns([1.05, 1.2])

    with c1:
        if flavor_stats is not None and len(flavor_stats) > 0:
            st.dataframe(flavor_stats, use_container_width=True, hide_index=True)
        else:
            st.info("플레이버 통계가 없습니다.")

    with c2:
        if flavor_stats is not None and len(flavor_stats) > 0:
            fig = plt.figure(figsize=(8, 5))
            top_plot = flavor_stats.head(10).iloc[::-1]
            plt.barh(top_plot["태그"], top_plot["빈도"])
            plt.xlabel("빈도")
            plt.ylabel("플레이버")
            plt.title("Top 10 플레이버 빈도")
            st.pyplot(fig)
        else:
            st.info("그래프가 없습니다.")

    st.markdown("---")
    st.subheader("트렌드 키워드 통계")
    c3, c4 = st.columns([1.05, 1.2])

    with c3:
        if trend_stats is not None and len(trend_stats) > 0:
            st.dataframe(trend_stats, use_container_width=True, hide_index=True)
        else:
            st.info("트렌드 통계가 없습니다.")

    with c4:
        if trend_stats is not None and len(trend_stats) > 0:
            fig2 = plt.figure(figsize=(8, 5))
            top_plot2 = trend_stats.head(10).iloc[::-1]
            plt.barh(top_plot2["태그"], top_plot2["빈도"])
            plt.xlabel("빈도")
            plt.ylabel("트렌드")
            plt.title("Top 10 트렌드 키워드 빈도")
            st.pyplot(fig2)
        else:
            st.info("그래프가 없습니다.")

    st.markdown("---")
    st.subheader("가격대 분포")
    if len(agg_df) > 0:
        fig3 = plt.figure(figsize=(8, 5))
        price_series = agg_df["평균최저가"].replace(0, np.nan).dropna()
        if len(price_series) > 0:
            plt.hist(price_series, bins=15)
            plt.xlabel("평균최저가")
            plt.ylabel("제품 수")
            plt.title("중복 통합 제품 가격대 분포")
            st.pyplot(fig3)
        else:
            st.info("가격 데이터가 없습니다.")

    st.markdown("---")
    col_l, col_r = st.columns([6, 4])

    with col_l:
        st.markdown('<div class="section-title st-green">📋 중복 통합 제품 목록</div>', unsafe_allow_html=True)

        product_labels = [
            f"[{i+1}] {r['대표상품명'][:30]} | ₩{int(r['평균최저가']):,} | {r.get('대표브랜드','')[:8]}"
            for i, (_, r) in enumerate(agg_df.iterrows())
        ]
        if len(product_labels) > 0:
            selected_idx = st.selectbox(
                "🔍 제품 선택 → 우측 상세",
                range(len(product_labels)),
                index=min(st.session_state.n_detail_idx, len(product_labels)-1),
                format_func=lambda i: product_labels[i],
                key="n_detail_sel"
            )
            st.session_state.n_detail_idx = selected_idx
        else:
            selected_idx = 0

        rows = ""
        for i, row in agg_df.head(200).iterrows():
            url = row["대표링크"]
            nm = str(row["대표상품명"])[:38]
            bd = ""
            if row.get("대표브랜드"):
                bd += f'<span class="badge badge-brand">{str(row["대표브랜드"])[:8]}</span>'
            if row.get("gemini_primary_flavor"):
                bd += f'<span class="badge badge-naver">{str(row["gemini_primary_flavor"])[:8]}</span>'
            rows += f'<tr><td style="text-align:center;color:#34D399;font-weight:700;">{i+1}</td><td class="product-name"><a href="{url}" target="_blank">{nm}</a><div class="product-desc">{row.get("대표판매처","")}</div></td><td style="text-align:right;font-weight:600;color:#E5E7EB;">₩{int(row["평균최저가"]):,}</td><td style="text-align:center;">{int(row["상품수"])}</td><td style="text-align:center;">{bd}</td></tr>'
        st.markdown(f'<div style="max-height:520px;overflow-y:auto;border:1px solid #374151;border-radius:10px;"><table class="product-table naver"><thead><tr><th>#</th><th>상품명</th><th>평균가</th><th>중복수</th><th>정보</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        with d1:
            if csv_df is not None:
                st.download_button(
                    "📥 CSV",
                    csv_df.to_csv(index=False).encode("utf-8-sig"),
                    f"naver_gemini_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    type="primary",
                    key="n_csv2"
                )
        with d2:
            if csv_df is not None:
                st.download_button(
                    "📥 엑셀",
                    to_excel(csv_df),
                    f"naver_gemini_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    type="secondary",
                    key="n_xlsx2"
                )

    with col_r:
        st.markdown('<div class="section-title st-green">📦 상품 상세</div>', unsafe_allow_html=True)
        if len(agg_df) > 0:
            row = agg_df.iloc[selected_idx]
            img = row.get("대표이미지", "")
            name = row.get("대표상품명", "")
            price = int(row.get("평균최저가", 0))
            flavor = ", ".join(row.get("all_flavor_tags", [])) if isinstance(row.get("all_flavor_tags", []), list) else ""
            trends = ", ".join(row.get("all_trend_tags", [])) if isinstance(row.get("all_trend_tags", []), list) else ""
            st.markdown(
                f'<div class="detail-panel"><div class="detail-header naver"><h3>📦 {name}</h3><p>{row.get("대표판매처","")}</p></div>'
                f'<div class="detail-body"><img class="detail-img" src="{img}" onerror="this.style.display=\'none\'">'
                f'<div class="detail-price-box naver"><span class="detail-price-big">₩{price:,}</span></div>'
                f'<div class="detail-info-grid">'
                f'<span class="detail-info-label">브랜드</span><span class="detail-info-value">{row.get("대표브랜드","-") or "-"}</span>'
                f'<span class="detail-info-label">제조사</span><span class="detail-info-value">{row.get("대표제조사","-") or "-"}</span>'
                f'<span class="detail-info-label">제품군</span><span class="detail-info-value">{row.get("핵심제품군","-") or "-"}</span>'
                f'<span class="detail-info-label">중복수</span><span class="detail-info-value">{int(row.get("상품수",0))}</span>'
                f'<span class="detail-info-label">주요플레이버</span><span class="detail-info-value">{row.get("gemini_primary_flavor","-") or "-"}</span>'
                f'<span class="detail-info-label">당 포지션</span><span class="detail-info-value">{row.get("gemini_sugar_positioning","-") or "-"}</span>'
                f'<span class="detail-info-label">패키지</span><span class="detail-info-value">{row.get("gemini_package_format","-") or "-"}</span>'
                f'<span class="detail-info-label">Flavor 태그</span><span class="detail-info-value">{flavor or "-"}</span>'
                f'<span class="detail-info-label">Trend 태그</span><span class="detail-info-value">{trends or "-"}</span>'
                f'</div></div></div>',
                unsafe_allow_html=True
            )
            st.markdown(f'<div style="text-align:center;margin-top:12px;"><a href="{row["대표링크"]}" target="_blank" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#059669,#10B981);color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;">🔗 쇼핑몰에서 보기</a></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Gemini 분석보고서")
    if report_text:
        st.markdown(f'<div class="ai-box"><h3>✨ Gemini 리포트</h3><div class="ai-content">{report_text}</div></div>', unsafe_allow_html=True)
    else:
        st.info("분석보고서가 아직 없습니다.")

# ============================================================
# 메인
# ============================================================
def main():
    t1, t2 = st.tabs(["🟣 마켓컬리 신제품", "🟢 네이버 쇼핑"])
    with t1:
        tab_kurly()
    with t2:
        tab_naver()

if __name__ == "__main__":
    main()
