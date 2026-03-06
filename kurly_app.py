"""
🛍️ 식품 쇼핑 인텔리전스 v7.0
마켓컬리 + 네이버 쇼핑 + OpenAI 트렌드 분석
다크모드 최적화
"""
import streamlit as st
import requests
import pandas as pd
import json
import io
import re
from datetime import datetime, date, timedelta

st.set_page_config(page_title="식품 쇼핑 인텔리전스", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

# ============================================================
# 음료 카테고리 / 브랜드
# ============================================================
BEV_CATS = ["", "제로음료", "주스/과즙음료", "사이다", "콜라", "이온음료", "과즙탄산음료",
    "에이드음료", "아이스티음료", "파우더/스무디", "녹차/홍차음료", "전통/곡물음료", "기타탄산음료"]
BEV_BRANDS = ["", "델몬트", "웅진식품", "자연은", "롯데칠성음료", "웅진", "카프리썬", "참존", "코코팜",
    "돈시몬", "풀무원", "해태에이치티비", "미닛메이드", "매일유업", "홀베리", "서울우유", "일화",
    "모구모구", "팔도", "농심", "스위트컵", "갈아만든배", "아임요", "가야농장", "코카콜라", "과일촌",
    "흥국에프엔비", "오션스프레이", "초록매실", "동원", "과수원", "차그림", "빙그레", "포모나",
    "해태제과", "아임리얼", "세미", "이롬", "노브랜드", "커클랜드", "봉봉", "나탈리스", "카고메",
    "그린트리", "피크닉", "DOLE", "오케이에프", "르씨엘", "롯데", "서울팩토리", "하니앤손스"]

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

/* 테이블 - 다크 */
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

/* 상세 패널 - 다크 */
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

/* 트렌드 카드 */
.trend-card { border: 1px solid #374151; border-radius: 12px; padding: 18px; margin-bottom: 14px; background: #1F2937; }
.trend-kw { font-size: 18px; font-weight: 900; color: #34D399; margin-bottom: 8px; }
.trend-stat { display: flex; gap: 18px; flex-wrap: wrap; font-size: 14px; color: #9CA3AF; }
.trend-stat b { color: #E5E7EB; }

/* 트렌드 테이블 */
.trend-table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 10px; background: #1F2937; }
.trend-table th { padding: 10px 8px; background: linear-gradient(90deg, #059669, #10B981); color: white; font-weight: 600; text-align: center; }
.trend-table td { padding: 9px 8px; border-bottom: 1px solid #374151; text-align: center; color: #E5E7EB; }
.trend-table tr:nth-child(even) { background: #111827; }
.trend-table tr:hover { background: #064E3B; }
.trend-rank { font-size: 18px; font-weight: 900; color: #34D399; }

/* AI 분석 박스 */
.ai-box { background: #1E1B4B; border: 1px solid #4338CA; border-radius: 14px; padding: 20px; margin: 16px 0; }
.ai-box h3 { color: #A5B4FC; font-size: 17px; font-weight: 700; margin: 0 0 12px; }
.ai-box .ai-content { color: #E0E7FF; font-size: 14px; line-height: 1.8; white-space: pre-wrap; }

/* 사이드바 */
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
KURLY_H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
           "Accept": "application/json", "Referer": "https://www.kurly.com/", "Origin": "https://www.kurly.com"}
KURLY_BASE = "https://api.kurly.com/collection/v2/home/sites/market"
KURLY_SORT = {"신상품순": "0", "추천순": "4", "판매량순": "1", "혜택순": "5", "높은가격순": "3", "낮은가격순": "2"}
NAVER_SORT = {"추천순(정확도)": "sim", "신상품순(날짜)": "date", "낮은가격순": "asc", "높은가격순": "dsc"}

def load_naver_keys():
    for sec in ["naver_shopping", "naver_search"]:
        try:
            cid = st.secrets[sec]["NAVER_CLIENT_ID"]
            csec = st.secrets[sec]["NAVER_CLIENT_SECRET"]
            if cid and cid.strip() and csec and csec.strip(): return cid.strip(), csec.strip(), sec
        except Exception: pass
    return "", "", ""

def load_openai_key():
    try:
        key = st.secrets["openai"]["OPENAI_API_KEY"]
        return key.strip() if key and key.strip() else ""
    except Exception: return ""

# ============================================================
# OpenAI 분석
# ============================================================
def ai_analyze(products_info, context="네이버 쇼핑", api_key=""):
    if not api_key: return "⚠️ OpenAI API 키가 설정되지 않았습니다."

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
- 중복 등록/멀티팩/번들 SKU를 감안하여 실질 고유 제품 수를 추정하세요.
- 동일 제품의 용량/입수 변형 여부를 구분하세요.

### 2. 입수/용량 보정 가격 분석
- 단품 vs 멀티팩 vs 대용량 가격 구조를 해석하세요.
- 가능하면 100ml당 가격 기준으로 설명하세요.
- 계산 예시가 있으면 1~2개만 간단히 제시하세요.

### 3. 판매채널 구조
- 자사몰/오픈마켓/종합몰/직영몰 등 등록 패턴을 해석하세요.
- 특정 채널 편중 여부가 보이면 언급하세요.

### 4. 번들/기획팩 구성 특성
- 묶음 상품, 세트 상품, 업소용 상품 비중과 의미를 해석하세요.

### 5. 맛/플레이버 키워드
- 제품명에서 추출 가능한 맛/향 키워드를 정리하세요.
- 단, 검색 노출 빈도와 실제 소비자 선호는 다를 수 있음을 반드시 쓰세요.

### 6. R&D 시사점
- 제품 개발 관점에서 검토할 만한 방향을 제시하세요.
- 확정 제안이 아니라 "검토 가치가 있는 방향" 수준으로 쓰세요.

### 7. 회의용 멘트
- 위 분석을 바탕으로 내부 상품기획 회의에서 바로 읽을 수 있는
  1분 브리핑용 멘트를 작성하세요.
- 5~7문장으로 작성하세요.
- 실무 보고형 문체로 작성하세요.

### 8. 마케팅 기획자 페르소나 스크립트
- 당신은 15년 경력의 음료 마케팅 기획자라는 설정으로 작성하세요.
- 아래 4개 소제목을 반드시 포함하세요.
  1) 시장 구조 해석
  2) 소비자 구매 포인트
  3) 온라인 채널 특성
  4) 제품 기획 시사점
- 실무 기획 보고서 톤으로 작성하세요.

[중요]
- 반드시 1번부터 8번까지 모두 출력하세요.
- 중간에 생략하지 마세요.
- 한국어로 답변하세요.
"""

try:
        resp = requests.post("https://api.openai.com/v1/chat/completions",            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": [
                {"role": "system", "content": "한국 식품/음료 시장 트렌드 분석 전문가. 데이터 기반으로 간결하고 실용적인 인사이트를 제공합니다."},
                {"role": "user", "content": prompt}
            ], "temperature": 0.7, "max_tokens": 2000}, timeout=30)
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
    r = requests.get(f"{KURLY_BASE}/category-groups", headers=KURLY_H, timeout=10); r.raise_for_status()
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
            resp = requests.get(f"{KURLY_BASE}/product-categories/{cat_code}/products", headers=KURLY_H,
                params={"sort_type": sort_type, "page": page, "per_page": pp, "filters": ""}, timeout=10)
            if resp.status_code != 200: break
            prods = resp.json().get("data", [])
            if not prods: break
            for rank, p in enumerate(prods, start=len(items)+1):
                items.append({"순위": rank, "카테고리코드": cat_code, "상품번호": p.get("no",""), "상품명": p.get("name",""),
                    "설명": p.get("short_description",""), "판매가": p.get("sales_price",0), "할인가": p.get("discounted_price"),
                    "할인율": p.get("discount_rate",0), "리뷰수": p.get("review_count",""),
                    "품절": "Y" if p.get("is_sold_out") else "N",
                    "배송유형": ", ".join(d.get("description","") for d in p.get("delivery_type_infos",[])),
                    "이미지URL": p.get("list_image_url",""), "상품URL": f"https://www.kurly.com/goods/{p.get('no','')}",
                    "저재고": "Y" if p.get("is_low_stock") else "N"})
            if len(items) >= max_items: break
        except Exception: break
    return items[:max_items]

@st.cache_data(ttl=600, show_spinner=False)
def kurly_detail(pno):
    try:
        r = requests.get(f"https://www.kurly.com/goods/{pno}", headers={"User-Agent": KURLY_H["User-Agent"]}, timeout=10)
        if "__NEXT_DATA__" not in r.text: return None
        mk = '__NEXT_DATA__" type="application/json">'; s = r.text.find(mk)+len(mk); e = r.text.find("</script>", s)
        return json.loads(r.text[s:e]).get("props",{}).get("pageProps",{}).get("product")
    except Exception: return None

# ============================================================
# 네이버 API
# ============================================================
@st.cache_data(ttl=300, show_spinner=False)
def naver_search(query, cid, csec, display=100, start=1, sort="sim"):
    headers = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": csec}
    items, cur = [], start
    while len(items) < display:
        batch = min(100, display - len(items))
        try:
            resp = requests.get("https://openapi.naver.com/v1/search/shop.json", headers=headers,
                params={"query": query, "display": batch, "start": cur, "sort": sort}, timeout=10)
            if resp.status_code != 200: break
            ri = resp.json().get("items", [])
            if not ri: break
            items.extend(ri); cur += batch
            if cur > 1000: break
        except Exception: break
    return items[:display]

def clean_html(t): return re.sub(r'<[^>]+>', '', t) if t else ""

def parse_naver(items, kw=""):
    return [{"순위": i, "키워드": kw, "상품명": clean_html(it.get("title","")),
        "최저가": int(it.get("lprice",0)), "최고가": int(it.get("hprice",0)) if it.get("hprice") else None,
        "쇼핑몰": it.get("mallName",""), "브랜드": it.get("brand",""), "제조사": it.get("maker",""),
        "카테고리1": it.get("category1",""), "카테고리2": it.get("category2",""),
        "카테고리3": it.get("category3",""), "카테고리4": it.get("category4",""),
        "상품ID": it.get("productId",""), "상품URL": it.get("link",""), "이미지URL": it.get("image",""),
        "상품유형": it.get("productType","")} for i, it in enumerate(items, 1)]

def calc_trend(df):
    def extract_kw(name):
        tokens = [t for t in re.findall(r'[가-힣a-zA-Z0-9]+', str(name)) if len(t) >= 2 and t not in ["ml","ML","개입","박스","캔","병","팩","세트","묶음"]]
        return " ".join(tokens[:2]) if tokens else name[:6]
    df = df.copy(); df["그룹키"] = df["상품명"].apply(extract_kw); mx = len(df)
    g = df.groupby("그룹키").agg(대표상품=("상품명","first"), 평균가격=("최저가","mean"), 최저가=("최저가","min"),
        상품수=("상품명","count"), 평균순위=("순위","mean"), 대표브랜드=("브랜드","first"), 대표쇼핑몰=("쇼핑몰","first")).reset_index()
    g["판매순위점수"] = ((mx - g["평균순위"]) / max(mx,1) * 200).clip(0,200).round(1)
    mc = g["상품수"].max() if g["상품수"].max() > 0 else 1
    g["추천점수"] = (g["상품수"] / mc * 100).round(1)
    g["종합점수"] = (g["판매순위점수"] * 0.7 + g["추천점수"] * 0.3).round(1)
    g = g.sort_values("종합점수", ascending=False).reset_index(drop=True); g.index += 1; g.index.name = "순위"
    return g

# ============================================================
# 공통 렌더링
# ============================================================
def render_metrics(cards):
    h = '<div class="metric-row">'
    for num, label, cls in cards:
        h += f'<div class="metric-card {cls}"><div class="num">{num}</div><div class="label">{label}</div></div>'
    st.markdown(h+'</div>', unsafe_allow_html=True)

def render_bars(title, tcls, data, bcls, wide=False, pct=False, total=1):
    if not data: return
    mx = max(data.values()) if data.values() else 1; lc = "bar-label-wide" if wide else "bar-label"
    h = f'<div class="section-title {tcls}">{title}</div>'
    for lb, cnt in data.items():
        w = int(cnt/mx*260) if mx > 0 else 0
        p = f" ({cnt/total*100:.0f}%)" if pct and total > 0 else ""
        h += f'<div class="bar-row"><div class="{lc}">{lb}</div><div class="bar {bcls}" style="width:{w}px;"></div><div class="bar-count">{cnt}개{p}</div></div>'
    st.markdown(h, unsafe_allow_html=True)

def to_excel(df):
    buf = io.BytesIO()
    cols = [c for c in df.columns if c not in ["이미지URL","그룹키"]]
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w: df[cols].to_excel(w, sheet_name="전체", index=False)
    return buf.getvalue()

def to_csv(df):
    cols = [c for c in df.columns if c not in ["이미지URL","그룹키"]]
    return df[cols].to_csv(index=False).encode("utf-8-sig")

def build_ai_products_text(df, platform="네이버", top_n=20):
    """AI 분석용 상품 텍스트 생성"""
    lines = []
    price_col = "최저가" if "최저가" in df.columns else "판매가"
    brand_col = "브랜드" if "브랜드" in df.columns else None
    for _, row in df.head(top_n).iterrows():
        parts = [f"{row['순위']}위: {row['상품명']}"]
        parts.append(f"₩{row[price_col]:,}")
        if brand_col and row.get(brand_col): parts.append(f"[{row[brand_col]}]")
        if "쇼핑몰" in df.columns and row.get("쇼핑몰"): parts.append(f"({row['쇼핑몰']})")
        if "카테고리명" in df.columns and row.get("카테고리명"): parts.append(f"({row['카테고리명']})")
        lines.append(" | ".join(parts))
    return "\n".join(lines)

# ============================================================
# 🟣 컬리 탭
# ============================================================
def tab_kurly():
    tree = kurly_load_tree()
    oai_key = load_openai_key()
    if "k_df" not in st.session_state: st.session_state.k_df = None
    if "k_sel" not in st.session_state: st.session_state.k_sel = None

    with st.sidebar:
        st.markdown("### 🟣 컬리 설정")
        mo = {info["name"]: code for code, info in tree.items()}
        sm_names = st.multiselect("대분류", list(mo.keys()), [], placeholder="선택", key="k_main")
        smc = [mo[n] for n in sm_names]
        so = {}
        if smc:
            for mc in smc:
                for sc, sn in tree[mc]["subs"].items(): so[f"{tree[mc]['name']} > {sn}"] = sc
        if so:
            asub = st.checkbox("✅ 하위 전체", True, key="k_allsub")
            ssn = list(so.keys()) if asub else st.multiselect("하위", list(so.keys()), [], key="k_sub")
            ssc = [so[n] for n in ssn]
        else: ssc = []
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
                    if sc in info["subs"]: nm = info["subs"][sc]; break
                tgts.append((sc, nm))
        else:
            for mc in smc: tgts.append((mc, tree[mc]["name"]))
        if tgts:
            pg = st.progress(0, "📡 수집...")
            ad = []
            for i, (code, name) in enumerate(tgts):
                pg.progress((i+1)/len(tgts), f"📡 [{i+1}/{len(tgts)}] {name}")
                its = kurly_fetch(code, KURLY_SORT[ks], km)
                for it in its: it["카테고리명"] = name
                ad.extend(its)
            pg.empty()
            if ad:
                df = pd.DataFrame(ad).drop_duplicates(subset=["상품번호"], keep="first")
                if kw.strip():
                    kws = [k.strip() for k in kw.split(",") if k.strip()]
                    df = df[df["상품명"].str.contains("|".join(kws), case=False, na=False)]
                if ke: df = df[df["품절"]=="N"]
                pmin, pmax = kp
                df = df[(df["판매가"]>=pmin)&(df["판매가"]<=pmax)].head(km).reset_index(drop=True)
                st.session_state.k_df = df; st.session_state.k_sel = None

    df = st.session_state.k_df
    if df is None or len(df) == 0:
        st.markdown('<div style="text-align:center;padding:60px;color:#6B7280;"><div style="font-size:48px;">🛍️</div><div style="font-size:18px;font-weight:600;color:#C084FC;">사이드바에서 카테고리 선택 → 수집 시작</div></div>', unsafe_allow_html=True)
        return

    total = len(df); avg_p = df["판매가"].mean()
    dc = (df["할인율"]>0).sum(); ad = df.loc[df["할인율"]>0,"할인율"].mean() if dc > 0 else 0
    lc = (df["저재고"]=="Y").sum()
    render_metrics([(f"{total:,}","총 상품","mc-purple"),(f"₩{avg_p:,.0f}","평균가격","mc-blue"),(f"{dc:,}",f"할인(평균{ad:.0f}%)","mc-red"),(f"{lc:,}","품절임박⚡","mc-amber")])

    # AI 분석
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
        if st.session_state.k_sel and st.session_state.k_sel in pn: ci = pn.index(st.session_state.k_sel)
        si = st.selectbox("🔍 상품 선택 → 우측 상세", range(len(pl)), ci, format_func=lambda i: pl[i], key="k_psel")
        st.session_state.k_sel = pn[si]
        rows = ""
        for _, row in df.iterrows():
            nm = str(row["상품명"])[:36]; url = row["상품URL"]
            if row["할인가"] and row["할인율"] and row["할인율"]>0:
                ph = f'<span class="price-original">₩{row["판매가"]:,}</span><br><span class="price-discount">₩{row["할인가"]:,}</span>'
                dh = f'<span class="discount-rate">{row["할인율"]}%</span>'
            else: ph = f'₩{row["판매가"]:,}'; dh = "-"
            bd = ""
            if row["순위"]<=10: bd += '<span class="badge badge-top10">🆕TOP10</span>'
            elif row["순위"]<=30: bd += '<span class="badge badge-new">NEW</span>'
            if row["할인율"] and row["할인율"]>=20: bd += '<span class="badge badge-sale">🔥SALE</span>'
            if row.get("저재고")=="Y": bd += '<span class="badge badge-low">⚡임박</span>'
            cn = str(row.get("카테고리명",""))[:8]
            rows += f'<tr><td style="text-align:center;color:#C084FC;font-weight:700;">{row["순위"]}</td><td style="text-align:center;font-size:12px;">{cn}</td><td class="product-name"><a href="{url}" target="_blank">{nm}</a></td><td style="text-align:right;">{ph}</td><td style="text-align:center;">{dh}</td><td style="text-align:center;">{bd}</td></tr>'
        st.markdown(f'<div style="max-height:520px;overflow-y:auto;border:1px solid #374151;border-radius:10px;"><table class="product-table"><thead><tr><th>#</th><th>카테고리</th><th>상품명</th><th>가격</th><th>할인</th><th>상태</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1: st.download_button("📥 엑셀", to_excel(df), f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", type="primary", key="k_dl")
        with d2: st.download_button("📥 CSV", to_csv(df), f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", type="secondary", key="k_csv")

    with col_r:
        st.markdown('<div class="section-title st-purple">📦 상품 상세</div>', unsafe_allow_html=True)
        pno = st.session_state.k_sel
        if pno:
            with st.spinner("로딩..."):
                det = kurly_detail(pno)
            if det:
                name=det.get("name",""); img=det.get("mainImageUrl",""); bp=det.get("basePrice",0)
                dpv=det.get("discountedPrice"); drv=det.get("discountRate",0)
                prh = f'<span class="detail-price-big">₩{dpv:,}</span> <span style="text-decoration:line-through;color:#6B7280;">₩{bp:,}</span> <span style="background:#EF4444;color:white;padding:2px 8px;border-radius:10px;font-size:13px;font-weight:700;">{drv}%</span>' if dpv and drv and drv>0 else f'<span class="detail-price-big">₩{bp:,}</span>'
                vol=det.get("volume",""); seller=det.get("sellerName","")
                brand=det.get("brandInfo",{}).get("name","-") if det.get("brandInfo") else "-"
                rc=det.get("reviewCount",0); allergy=det.get("allergy","")
                delivery=", ".join(str(d) for d in det.get("deliveryTypeNames",[]))
                opts="".join(f'<div class="detail-option"><span class="detail-option-name">{dp.get("name","")[:30]}</span><span class="detail-option-price">₩{dp.get("basePrice",0):,}</span></div>' for dp in det.get("dealProducts",[])[:6])
                alh = f'<div class="detail-allergy">⚠️ {allergy.replace(chr(10),"<br>")}</div>' if allergy and allergy.strip() else ""
                st.markdown(f'<div class="detail-panel"><div class="detail-header"><h3>📦 {name}</h3></div><div class="detail-body"><img class="detail-img" src="{img}" onerror="this.style.display=\'none\'"><div class="detail-price-box">{prh}</div><div class="detail-info-grid"><span class="detail-info-label">용량</span><span class="detail-info-value">{vol}</span><span class="detail-info-label">배송</span><span class="detail-info-value">{delivery}</span><span class="detail-info-label">판매자</span><span class="detail-info-value">{seller}</span><span class="detail-info-label">브랜드</span><span class="detail-info-value">{brand}</span><span class="detail-info-label">리뷰</span><span class="detail-info-value">⭐ {rc:,}개</span></div>{opts}{alh}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div style="text-align:center;margin-top:12px;"><a href="https://www.kurly.com/goods/{pno}" target="_blank" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#7C3AED,#A855F7);color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;">🔗 컬리에서 보기</a></div>', unsafe_allow_html=True)
            else: st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">⚠️</div><div>상세 로딩 실패</div></div></div>', unsafe_allow_html=True)
        else: st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">👆</div><div style="font-size:15px;font-weight:600;color:#C084FC;">상품을 선택하세요</div></div></div>', unsafe_allow_html=True)

# ============================================================
# 🟢 네이버 쇼핑 탭
# ============================================================
def tab_naver():
    oai_key = load_openai_key()
    if "n_df" not in st.session_state: st.session_state.n_df = None
    if "n_si" not in st.session_state: st.session_state.n_si = 0
    if "n_trend" not in st.session_state: st.session_state.n_trend = None

    auto_id, auto_sec, auto_src = load_naver_keys()
    with st.sidebar:
        st.markdown("### 🟢 네이버 쇼핑 설정")
        if auto_id and auto_sec:
            st.success(f"🔑 API 키 로딩 ({auto_src})")
            n_id, n_sec = auto_id, auto_sec
        else:
            st.warning("secrets.toml에 키 없음")
            n_id = st.text_input("Client ID", type="password", key="n_id")
            n_sec = st.text_input("Client Secret", type="password", key="n_sec")

        st.markdown("---")
        n_mode = st.radio("검색 모드", ["🔍 키워드 검색", "🍹 음료 카테고리", "📊 트렌드 비교"], key="n_mode")

        if n_mode == "🔍 키워드 검색":
            nq = st.text_input("검색어", placeholder="제로음료", key="n_q")
            ns = st.selectbox("정렬", list(NAVER_SORT.keys()), 0, key="n_sort")
            nm = st.slider("최대 결과", 10, 300, 100, 10, key="n_max")
            st.markdown("---")
            st.markdown("**📅 검색 기간**")
            nd1 = st.date_input("시작일", date.today()-timedelta(days=30), key="n_d1")
            nd2 = st.date_input("종료일", date.today(), key="n_d2")
            st.caption("※ 네이버 API 날짜 필터 미지원 → 신상품순 정렬로 최신 상품 우선 수집")
            nr = st.button("🔍 검색", type="primary", use_container_width=True, disabled=not(n_id and n_sec and nq.strip()), key="n_run")

        elif n_mode == "🍹 음료 카테고리":
            n_bev = st.selectbox("음료분류", BEV_CATS, 0, key="n_bev", format_func=lambda x: x if x else "전체 (음료)")
            n_brand = st.selectbox("브랜드", BEV_BRANDS, 0, key="n_brand", format_func=lambda x: x if x else "전체")
            ns = st.selectbox("정렬", list(NAVER_SORT.keys()), 0, key="n_csort")
            nm = st.slider("최대 결과", 10, 200, 100, 10, key="n_cmax")
            st.markdown("---")
            st.markdown("**📅 검색 기간**")
            ncd1 = st.date_input("시작일", date.today()-timedelta(days=30), key="nc_d1")
            ncd2 = st.date_input("종료일", date.today(), key="nc_d2")
            nr = st.button("🍹 카테고리 검색", type="primary", use_container_width=True, disabled=not(n_id and n_sec), key="n_crun")

        else:
            n_qs = st.text_area("비교 키워드 (줄바꿈)", "제로음료\n콤부차\n프로틴음료", height=100, key="n_qs")
            n_mt = st.slider("키워드당 최대", 10, 200, 100, 10, key="n_mt")
            st.markdown("---")
            st.markdown("**📅 검색 기간**")
            ntd1 = st.date_input("시작일", date.today()-timedelta(days=30), key="nt_d1")
            ntd2 = st.date_input("종료일", date.today(), key="nt_d2")
            nr = st.button("📊 트렌드 비교", type="primary", use_container_width=True, disabled=not(n_id and n_sec and n_qs.strip()), key="n_trun")

    st.markdown('<div class="naver-header"><h1>🟢 네이버 쇼핑 인텔리전스</h1><p>키워드 · 음료 카테고리 · 트렌드 비교 · AI 분석</p></div>', unsafe_allow_html=True)

    if not(n_id and n_sec):
        st.info("사이드바에 API 키를 설정해주세요.")
        return

    if nr:
        if n_mode == "🔍 키워드 검색" and nq.strip():
            with st.spinner(f"🔍 '{nq}' 검색 중..."):
                items = naver_search(nq, n_id, n_sec, nm, 1, NAVER_SORT[ns])
                parsed = parse_naver(items, nq)
            st.session_state.n_df = pd.DataFrame(parsed) if parsed else None
            st.session_state.n_si = 0; st.session_state.n_trend = None

        elif n_mode == "🍹 음료 카테고리":
            qp = []; 
            if n_bev: qp.append(n_bev)
            if n_brand: qp.append(n_brand)
            query = " ".join(qp) if qp else "음료"
            with st.spinner(f"🍹 '{query}' 검색 중..."):
                items = naver_search(query, n_id, n_sec, nm, 1, NAVER_SORT[ns])
                parsed = parse_naver(items, query)
            if parsed:
                st.session_state.n_df = pd.DataFrame(parsed)
                st.session_state.n_trend = calc_trend(st.session_state.n_df)
            else: st.session_state.n_df = None; st.session_state.n_trend = None
            st.session_state.n_si = 0

        elif n_mode == "📊 트렌드 비교" and n_qs.strip():
            queries = [q.strip() for q in n_qs.split("\n") if q.strip()]
            all_p = []; pg = st.progress(0, "검색 중...")
            for i, q in enumerate(queries):
                pg.progress((i+1)/len(queries), f"🔍 '{q}'...")
                all_p.extend(parse_naver(naver_search(q, n_id, n_sec, n_mt, 1, "sim"), q))
            pg.empty()
            if all_p:
                st.session_state.n_df = pd.DataFrame(all_p)
                st.session_state.n_trend = calc_trend(st.session_state.n_df)
            else: st.session_state.n_df = None; st.session_state.n_trend = None
            st.session_state.n_si = 0

    df = st.session_state.n_df; trend_df = st.session_state.n_trend
    if df is None or len(df) == 0:
        st.markdown('<div style="text-align:center;padding:60px;color:#6B7280;"><div style="font-size:48px;">🔍</div><div style="font-size:18px;font-weight:600;color:#34D399;">검색 조건을 설정하고 시작하세요</div></div>', unsafe_allow_html=True)
        return

    total = len(df); avg_p = df["최저가"].mean(); brands = df["브랜드"].nunique(); malls = df["쇼핑몰"].nunique()
    kw_cnt = df["키워드"].nunique()
    render_metrics([(f"{total:,}","총 상품","mc-green"),(f"₩{avg_p:,.0f}","평균최저가","mc-blue"),(f"{brands:,}","브랜드수","mc-teal"),(f"{malls:,}","쇼핑몰수","mc-amber")])

    # AI 분석
    if oai_key and total > 0:
        if st.button("🤖 AI 트렌드 분석 (네이버 TOP 상품)", key="n_ai"):
            with st.spinner("🤖 AI 분석 중..."):
                txt = build_ai_products_text(df, "네이버 쇼핑", 25)
                kws = ", ".join(df["키워드"].unique()[:5])
                result = ai_analyze(txt, f"네이버 쇼핑 ({kws})", oai_key)
            st.markdown(f'<div class="ai-box"><h3>🤖 AI 트렌드 분석</h3><div class="ai-content">{result}</div></div>', unsafe_allow_html=True)

    # 트렌드 TOP 10
    if trend_df is not None and len(trend_df) > 0:
        st.markdown('<div class="section-title st-green">🏆 요약 트렌드 TOP 10</div>', unsafe_allow_html=True)
        trows = ""
        for idx, row in trend_df.head(10).iterrows():
            trows += f'<tr><td><span class="trend-rank">{idx}</span></td><td style="text-align:left;font-weight:600;color:#E5E7EB;">{str(row["대표상품"])[:35]}</td><td style="color:#D1D5DB;">{row.get("대표브랜드","")}</td><td style="color:#D1D5DB;">₩{row["평균가격"]:,.0f}</td><td style="color:#D1D5DB;">{row["상품수"]}</td><td style="font-weight:700;color:#34D399;">{row["종합점수"]}</td></tr>'
        st.markdown(f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #374151;"><table class="trend-table"><thead><tr><th>#</th><th>제품군</th><th>브랜드</th><th>평균가</th><th>상품수</th><th>종합점수</th></tr></thead><tbody>{trows}</tbody></table></div>', unsafe_allow_html=True)
        st.markdown("---")

    # 키워드별 비교
    if kw_cnt > 1:
        st.markdown('<div class="section-title st-green">📊 키워드별 비교</div>', unsafe_allow_html=True)
        for kv in df["키워드"].unique():
            kdf = df[df["키워드"]==kv]
            st.markdown(f'<div class="trend-card"><div class="trend-kw">🔹 {kv}</div><div class="trend-stat"><span>상품 <b>{len(kdf)}개</b></span><span>평균가 <b>₩{kdf["최저가"].mean():,.0f}</b></span><span>최저 <b>₩{kdf["최저가"].min():,}</b></span><span>최고 <b>₩{kdf["최저가"].max():,}</b></span><span>브랜드 <b>{kdf["브랜드"].nunique()}개</b></span></div></div>', unsafe_allow_html=True)
        st.markdown("---")

    # 차트
    c1, c2 = st.columns(2)
    with c1:
        bins = [0,5000,10000,20000,30000,50000,100000,float("inf")]
        labels = ["~5천","5천~1만","1~2만","2~3만","3~5만","5~10만","10만~"]
        df["가격대"] = pd.cut(df["최저가"], bins=bins, labels=labels)
        pd_d = df["가격대"].value_counts().sort_index()
        render_bars("💰 가격대","st-green",{str(k):int(v) for k,v in pd_d.items() if v>0},"bar-green",pct=True,total=total)
    with c2:
        md = df["쇼핑몰"].value_counts().head(10)
        render_bars("🏪 쇼핑몰","st-blue",{str(k)[:12]:int(v) for k,v in md.items()},"bar-blue",wide=True)

    st.markdown("---")
    col_l, col_r = st.columns([6, 4])
    with col_l:
        plbl = [f"[{r['순위']}] {r['상품명'][:28]} | ₩{r['최저가']:,} | {r['쇼핑몰'][:8]}" for _, r in df.iterrows()]
        si = st.selectbox("🔍 상품 선택 → 우측 상세", range(len(plbl)), st.session_state.n_si, format_func=lambda i: plbl[i], key="n_psel")
        st.session_state.n_si = si
        rows = ""
        for _, row in df.head(200).iterrows():
            nm = str(row["상품명"])[:36]; url = row["상품URL"]
            bd = ""
            if row["브랜드"]: bd += f'<span class="badge badge-brand">{row["브랜드"][:8]}</span>'
            if kw_cnt > 1: bd += f'<span class="badge badge-naver">{row["키워드"][:6]}</span>'
            rows += f'<tr><td style="text-align:center;color:#34D399;font-weight:700;">{row["순위"]}</td><td class="product-name"><a href="{url}" target="_blank">{nm}</a><div class="product-desc">{row["쇼핑몰"]}</div></td><td style="text-align:right;font-weight:600;color:#E5E7EB;">₩{row["최저가"]:,}</td><td style="text-align:center;">{bd}</td></tr>'
        st.markdown(f'<div style="max-height:520px;overflow-y:auto;border:1px solid #374151;border-radius:10px;"><table class="product-table naver"><thead><tr><th>#</th><th>상품명</th><th>최저가</th><th>정보</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1: st.download_button("📥 엑셀", to_excel(df), f"naver_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", type="primary", key="n_dl")
        with d2: st.download_button("📥 CSV", to_csv(df), f"naver_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", type="secondary", key="n_csv")

    with col_r:
        st.markdown('<div class="section-title st-green">📦 상품 상세</div>', unsafe_allow_html=True)
        if si < len(df):
            row = df.iloc[si]; img=row["이미지URL"]; name=row["상품명"]; price=row["최저가"]
            cat_path = " > ".join(filter(None, [row.get(f"카테고리{i}","") for i in range(1,5)]))
            st.markdown(f'<div class="detail-panel"><div class="detail-header naver"><h3>📦 {name}</h3><p>{row["쇼핑몰"]}</p></div><div class="detail-body"><img class="detail-img" src="{img}" onerror="this.style.display=\'none\'"><div class="detail-price-box naver"><span class="detail-price-big">₩{price:,}</span></div><div class="detail-info-grid"><span class="detail-info-label">쇼핑몰</span><span class="detail-info-value">{row["쇼핑몰"]}</span><span class="detail-info-label">브랜드</span><span class="detail-info-value">{row["브랜드"] or "-"}</span><span class="detail-info-label">제조사</span><span class="detail-info-value">{row["제조사"] or "-"}</span><span class="detail-info-label">카테고리</span><span class="detail-info-value">{cat_path or "-"}</span><span class="detail-info-label">상품유형</span><span class="detail-info-value">{row["상품유형"]}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center;margin-top:12px;"><a href="{row["상품URL"]}" target="_blank" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#059669,#10B981);color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;">🔗 쇼핑몰에서 보기</a></div>', unsafe_allow_html=True)

# ============================================================
# 메인
# ============================================================
def main():
    t1, t2 = st.tabs(["🟣 마켓컬리 신제품", "🟢 네이버 쇼핑"])
    with t1: tab_kurly()
    with t2: tab_naver()

if __name__ == "__main__":
    main()
