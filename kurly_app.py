"""
🛍️ 식품 쇼핑 인텔리전스 v6.0
마켓컬리 + 네이버 쇼핑 (키워드/카테고리/트렌드) 통합
"""
import streamlit as st
import requests
import pandas as pd
import json
import io
import re
from datetime import datetime

st.set_page_config(page_title="식품 쇼핑 인텔리전스", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

# ============================================================
# 음료 카테고리 / 브랜드 데이터
# ============================================================
BEVERAGE_CATEGORIES = [
    "", "제로음료", "주스/과즙음료", "사이다", "콜라", "이온음료",
    "과즙탄산음료", "에이드음료", "아이스티음료", "파우더/스무디",
    "녹차/홍차음료", "전통/곡물음료", "아이스티/녹차/홍차", "기타탄산음료",
]
BEVERAGE_BRANDS = [
    "", "델몬트", "웅진식품", "자연은", "롯데칠성음료", "웅진", "카프리썬",
    "참존", "코코팜", "돈시몬", "풀무원", "해태에이치티비", "미닛메이드",
    "매일유업", "홀베리", "서울우유", "일화", "모구모구", "팔도", "농심",
    "스위트컵", "갈아만든배", "아임요", "가야농장", "코카콜라", "과일촌",
    "흥국에프엔비", "오션스프레이", "초록매실", "동원", "과수원", "차그림",
    "빙그레", "포모나", "해태제과", "아임리얼", "세미", "이롬", "노브랜드",
    "커클랜드", "봉봉", "나탈리스", "카고메", "그린트리", "피크닉", "DOLE",
    "오케이에프", "르씨엘", "롯데", "서울팩토리", "하니앤손스",
]

# ============================================================
# CSS (글씨 크기 확대)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; font-size: 15px; }
.main-header { background: linear-gradient(135deg, #1A1A2E 0%, #5B2C6F 50%, #8E44AD 100%); padding: 26px 30px; border-radius: 14px; margin-bottom: 22px; }
.main-header h1 { color: white; font-size: 28px; font-weight: 900; margin: 0; }
.main-header p { color: #D2B4DE; font-size: 14px; margin: 5px 0 0; }
.naver-header { background: linear-gradient(135deg, #03C75A 0%, #1EC800 100%); padding: 26px 30px; border-radius: 14px; margin-bottom: 22px; }
.naver-header h1 { color: white; font-size: 28px; font-weight: 900; margin: 0; }
.naver-header p { color: #B8F5CD; font-size: 14px; margin: 5px 0 0; }
.metric-row { display: flex; gap: 12px; margin: 16px 0 22px; flex-wrap: wrap; }
.metric-card { flex: 1; min-width: 130px; padding: 18px 14px; border-radius: 14px; text-align: center; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
.metric-card .num { font-size: 30px; font-weight: 900; letter-spacing: -1px; }
.metric-card .label { font-size: 12px; opacity: 0.85; margin-top: 3px; }
.mc-purple { background: linear-gradient(135deg, #5B2C6F, #8E44AD); }
.mc-blue { background: linear-gradient(135deg, #1A5276, #2E86C1); }
.mc-red { background: linear-gradient(135deg, #922B21, #E74C3C); }
.mc-amber { background: linear-gradient(135deg, #B9770E, #F39C12); }
.mc-green { background: linear-gradient(135deg, #03C75A, #1EC800); }
.mc-teal { background: linear-gradient(135deg, #0E6655, #1ABC9C); }
.bar-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.bar-label { width: 75px; text-align: right; font-size: 13px; color: #444; font-weight: 500; flex-shrink: 0; }
.bar-label-wide { width: 110px; text-align: right; font-size: 13px; color: #444; font-weight: 500; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar { height: 22px; border-radius: 5px; }
.bar-purple { background: linear-gradient(90deg, #8E44AD, #D2B4DE); }
.bar-blue { background: linear-gradient(90deg, #2E86C1, #AED6F1); }
.bar-green { background: linear-gradient(90deg, #03C75A, #82E0AA); }
.bar-red { background: linear-gradient(90deg, #E74C3C, #FADBD8); }
.bar-count { font-size: 12px; color: #666; white-space: nowrap; }
.section-title { font-size: 17px; font-weight: 700; margin: 18px 0 10px; padding-bottom: 5px; border-bottom: 2px solid #eee; }
.st-purple { color: #5B2C6F; } .st-blue { color: #1A5276; } .st-green { color: #03C75A; } .st-red { color: #922B21; }
.product-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.product-table thead tr { background: linear-gradient(90deg, #5B2C6F, #8E44AD); color: white; }
.product-table.naver thead tr { background: linear-gradient(90deg, #03C75A, #1EC800); color: white; }
.product-table th { padding: 11px 7px; font-weight: 600; position: sticky; top: 0; z-index: 10; font-size: 13px; }
.product-table thead tr th { background: inherit; }
.product-table td { padding: 9px 7px; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.product-table tr:nth-child(even) { background: #FAFAFA; }
.product-table tr:hover { background: #F5EEF8; }
.product-table.naver tr:hover { background: #E8F8F0; }
.product-name a { color: #333; text-decoration: none; font-weight: 500; font-size: 13px; }
.product-name a:hover { color: #8E44AD; }
.product-table.naver .product-name a:hover { color: #03C75A; }
.product-desc { font-size: 11px; color: #999; margin-top: 2px; }
.price-original { text-decoration: line-through; color: #999; font-size: 12px; }
.price-discount { color: #E74C3C; font-weight: 700; font-size: 14px; }
.discount-rate { color: #E74C3C; font-weight: 700; }
.badge { display: inline-block; padding: 3px 7px; border-radius: 8px; font-size: 11px; font-weight: 700; margin: 1px; }
.badge-top10 { background: #F5EEF8; color: #8E44AD; } .badge-new { background: #EBF5FB; color: #2E86C1; }
.badge-sale { background: #FDEDEC; color: #E74C3C; } .badge-low { background: #FEF9E7; color: #B9770E; }
.badge-naver { background: #E8F8F0; color: #03C75A; } .badge-brand { background: #EBF5FB; color: #2E86C1; }
.detail-panel { border: 1px solid #e0e0e0; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.detail-header { background: linear-gradient(135deg, #5B2C6F, #8E44AD); padding: 16px 20px; color: white; }
.detail-header.naver { background: linear-gradient(135deg, #03C75A, #1EC800); }
.detail-header h3 { margin: 0; font-size: 16px; font-weight: 700; }
.detail-header p { margin: 4px 0 0; font-size: 12px; color: rgba(255,255,255,0.7); }
.detail-body { padding: 16px 20px; }
.detail-img { width: 100%; border-radius: 10px; margin-bottom: 14px; max-height: 320px; object-fit: contain; background: #f9f9f9; }
.detail-price-box { background: #F8F4FC; border-radius: 10px; padding: 14px; margin-bottom: 14px; }
.detail-price-box.naver { background: #E8F8F0; }
.detail-price-big { font-size: 24px; font-weight: 900; color: #5B2C6F; }
.detail-price-box.naver .detail-price-big { color: #03C75A; }
.detail-info-grid { display: grid; grid-template-columns: 85px 1fr; gap: 6px 12px; font-size: 14px; margin-bottom: 14px; }
.detail-info-label { color: #888; font-weight: 600; } .detail-info-value { color: #333; }
.detail-option { padding: 8px 12px; margin: 4px 0; background: #F8F9FA; border-radius: 8px; font-size: 13px; display: flex; justify-content: space-between; }
.detail-option-name { color: #333; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.detail-option-price { color: #5B2C6F; font-weight: 700; margin-left: 8px; }
.detail-allergy { background: #FFF8E1; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #856404; margin-top: 10px; }
.detail-placeholder { text-align: center; padding: 80px 20px; color: #bbb; }
.detail-placeholder .icon { font-size: 48px; margin-bottom: 12px; }
.trend-card { border: 1px solid #e0e0e0; border-radius: 12px; padding: 18px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
.trend-kw { font-size: 18px; font-weight: 900; color: #03C75A; margin-bottom: 8px; }
.trend-stat { display: flex; gap: 18px; flex-wrap: wrap; font-size: 14px; color: #555; }
.trend-stat b { color: #333; }
.trend-table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 10px; }
.trend-table th { padding: 10px 8px; background: linear-gradient(90deg, #03C75A, #1EC800); color: white; font-weight: 600; text-align: center; }
.trend-table td { padding: 9px 8px; border-bottom: 1px solid #f0f0f0; text-align: center; }
.trend-table tr:nth-child(even) { background: #F0FFF5; }
.trend-table tr:hover { background: #E8F8F0; }
.trend-rank { font-size: 18px; font-weight: 900; color: #03C75A; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1A1A2E 0%, #2C2C54 100%); }
section[data-testid="stSidebar"] .stMarkdown h1, section[data-testid="stSidebar"] .stMarkdown h2, section[data-testid="stSidebar"] .stMarkdown h3 { color: white !important; }
section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] .stMarkdown label { color: #D2B4DE !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 컬리 API
# ============================================================
KURLY_H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
           "Accept": "application/json", "Referer": "https://www.kurly.com/", "Origin": "https://www.kurly.com"}
KURLY_BASE = "https://api.kurly.com/collection/v2/home/sites/market"
KURLY_SORT = {"신상품순": "0", "추천순": "4", "판매량순": "1", "혜택순": "5", "높은가격순": "3", "낮은가격순": "2"}

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
        mk = '__NEXT_DATA__" type="application/json">'
        s = r.text.find(mk) + len(mk); e = r.text.find("</script>", s)
        return json.loads(r.text[s:e]).get("props",{}).get("pageProps",{}).get("product")
    except Exception: return None

# ============================================================
# 네이버 쇼핑 API
# ============================================================
NAVER_SORT = {"정확도순": "sim", "날짜순": "date", "낮은가격순": "asc", "높은가격순": "dsc"}

def load_naver_keys():
    for section in ["naver_shopping", "naver_search"]:
        try:
            cid = st.secrets[section]["NAVER_CLIENT_ID"]
            csec = st.secrets[section]["NAVER_CLIENT_SECRET"]
            if cid and cid.strip() and csec and csec.strip():
                return cid.strip(), csec.strip(), section
        except Exception: pass
    return "", "", ""

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

def parse_naver(items, keyword=""):
    parsed = []
    for i, it in enumerate(items, 1):
        parsed.append({"순위": i, "키워드": keyword, "상품명": clean_html(it.get("title","")),
            "최저가": int(it.get("lprice",0)), "최고가": int(it.get("hprice",0)) if it.get("hprice") else None,
            "쇼핑몰": it.get("mallName",""), "브랜드": it.get("brand",""), "제조사": it.get("maker",""),
            "카테고리1": it.get("category1",""), "카테고리2": it.get("category2",""),
            "카테고리3": it.get("category3",""), "카테고리4": it.get("category4",""),
            "상품ID": it.get("productId",""), "상품URL": it.get("link",""), "이미지URL": it.get("image",""),
            "상품유형": it.get("productType","")})
    return parsed

def calc_trend_scores(df):
    """트렌드 점수 산출: 판매순위점수(70%) + 추천점수(30%)"""
    def extract_keywords(name):
        tokens = re.findall(r'[가-힣a-zA-Z0-9]+', str(name))
        tokens = [t for t in tokens if len(t) >= 2 and t not in ["ml","ML","개입","박스","캔","병","팩","세트","묶음"]]
        return " ".join(tokens[:2]) if tokens else name[:6]

    df = df.copy()
    df["그룹키"] = df["상품명"].apply(extract_keywords)
    max_rank = len(df)

    grouped = df.groupby("그룹키").agg(
        대표상품=("상품명", "first"), 평균가격=("최저가", "mean"),
        최저가=("최저가", "min"), 상품수=("상품명", "count"),
        평균순위=("순위", "mean"), 대표브랜드=("브랜드", "first"),
        대표쇼핑몰=("쇼핑몰", "first"),
    ).reset_index()

    grouped["판매순위점수"] = ((max_rank - grouped["평균순위"]) / max(max_rank, 1) * 200).clip(0, 200).round(1)
    max_count = grouped["상품수"].max() if grouped["상품수"].max() > 0 else 1
    grouped["추천점수"] = (grouped["상품수"] / max_count * 100).round(1)
    grouped["종합점수"] = (grouped["판매순위점수"] * 0.7 + grouped["추천점수"] * 0.3).round(1)
    grouped = grouped.sort_values("종합점수", ascending=False).reset_index(drop=True)
    grouped.index = grouped.index + 1
    grouped.index.name = "순위"
    return grouped

# ============================================================
# 공통 렌더링
# ============================================================
def render_metrics(cards):
    h = '<div class="metric-row">'
    for num, label, cls in cards:
        h += f'<div class="metric-card {cls}"><div class="num">{num}</div><div class="label">{label}</div></div>'
    st.markdown(h + '</div>', unsafe_allow_html=True)

def render_bars(title, tcls, data, bcls, wide=False, pct=False, total=1):
    if not data: return
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
    cols = [c for c in df.columns if c not in ["이미지URL", "그룹키"]]
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        df[cols].to_excel(w, sheet_name="전체", index=False)
    return buf.getvalue()

def to_csv(df):
    cols = [c for c in df.columns if c not in ["이미지URL", "그룹키"]]
    return df[cols].to_csv(index=False).encode("utf-8-sig")

# ============================================================
# 🟣 컬리 탭
# ============================================================
def tab_kurly():
    tree = kurly_load_tree()
    if "k_df" not in st.session_state: st.session_state.k_df = None
    if "k_sel" not in st.session_state: st.session_state.k_sel = None

    with st.sidebar:
        st.markdown("### 🟣 컬리 설정")
        mo = {info["name"]: code for code, info in tree.items()}
        sm = st.multiselect("대분류", list(mo.keys()), [], placeholder="선택", key="k_main")
        smc = [mo[n] for n in sm]
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
        ke = st.checkbox("품절 제외", True, key="k_excl")
        kr = st.button("🔍 컬리 수집", type="primary", use_container_width=True, disabled=not smc, key="k_run")

    st.markdown('<div class="main-header"><h1>🛒 마켓컬리 신제품 인텔리전스</h1><p>카테고리별 트렌드 · 상품 선택 시 우측 상세 표시</p></div>', unsafe_allow_html=True)

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
                if ke: df = df[df["품절"] == "N"]
                pmin, pmax = kp
                df = df[(df["판매가"] >= pmin) & (df["판매가"] <= pmax)].head(km).reset_index(drop=True)
                st.session_state.k_df = df; st.session_state.k_sel = None

    df = st.session_state.k_df
    if df is None or len(df) == 0:
        st.markdown('<div style="text-align:center;padding:60px;color:#888;"><div style="font-size:48px;">🛍️</div><div style="font-size:18px;font-weight:600;color:#5B2C6F;">사이드바에서 카테고리 선택 → 수집 시작</div></div>', unsafe_allow_html=True)
        return

    total = len(df); avg_p = df["판매가"].mean()
    dc = (df["할인율"] > 0).sum(); ad = df.loc[df["할인율"]>0,"할인율"].mean() if dc > 0 else 0
    lc = (df["저재고"]=="Y").sum()
    render_metrics([(f"{total:,}","총 상품","mc-purple"),(f"₩{avg_p:,.0f}","평균가격","mc-blue"),(f"{dc:,}",f"할인(평균{ad:.0f}%)","mc-red"),(f"{lc:,}","품절임박⚡","mc-amber")])

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
            rows += f'<tr><td style="text-align:center;color:#8E44AD;font-weight:700;">{row["순위"]}</td><td style="text-align:center;font-size:12px;">{cn}</td><td class="product-name"><a href="{url}" target="_blank">{nm}</a></td><td style="text-align:right;">{ph}</td><td style="text-align:center;">{dh}</td><td style="text-align:center;">{bd}</td></tr>'
        st.markdown(f'<div style="max-height:520px;overflow-y:auto;border:1px solid #e0e0e0;border-radius:10px;"><table class="product-table"><thead><tr><th>#</th><th>카테고리</th><th>상품명</th><th>가격</th><th>할인</th><th>상태</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
        c_dl1, c_dl2 = st.columns(2)
        with c_dl1: st.download_button("📥 엑셀", to_excel(df), f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", type="primary", key="k_dl")
        with c_dl2: st.download_button("📥 CSV", to_csv(df), f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", type="secondary", key="k_csv")

    with col_r:
        st.markdown('<div class="section-title st-purple">📦 상품 상세</div>', unsafe_allow_html=True)
        pno = st.session_state.k_sel
        if pno:
            with st.spinner("로딩..."):
                det = kurly_detail(pno)
            if det:
                name=det.get("name",""); img=det.get("mainImageUrl",""); bp=det.get("basePrice",0)
                dpv=det.get("discountedPrice"); drv=det.get("discountRate",0)
                prh = f'<span class="detail-price-big">₩{dpv:,}</span> <span style="text-decoration:line-through;color:#999;">₩{bp:,}</span> <span style="background:#E74C3C;color:white;padding:2px 8px;border-radius:10px;font-size:13px;font-weight:700;">{drv}%</span>' if dpv and drv and drv>0 else f'<span class="detail-price-big">₩{bp:,}</span>'
                vol=det.get("volume",""); seller=det.get("sellerName",""); brand=det.get("brandInfo",{}).get("name","-") if det.get("brandInfo") else "-"
                rc=det.get("reviewCount",0); allergy=det.get("allergy",""); delivery=", ".join(str(d) for d in det.get("deliveryTypeNames",[]))
                opts = "".join(f'<div class="detail-option"><span class="detail-option-name">{dp.get("name","")[:30]}</span><span class="detail-option-price">₩{dp.get("basePrice",0):,}</span></div>' for dp in det.get("dealProducts",[])[:6])
                alh = f'<div class="detail-allergy">⚠️ {allergy.replace(chr(10),"<br>")}</div>' if allergy and allergy.strip() else ""
                st.markdown(f'<div class="detail-panel"><div class="detail-header"><h3>📦 {name}</h3></div><div class="detail-body"><img class="detail-img" src="{img}" onerror="this.style.display=\'none\'"><div class="detail-price-box">{prh}</div><div class="detail-info-grid"><span class="detail-info-label">용량</span><span class="detail-info-value">{vol}</span><span class="detail-info-label">배송</span><span class="detail-info-value">{delivery}</span><span class="detail-info-label">판매자</span><span class="detail-info-value">{seller}</span><span class="detail-info-label">브랜드</span><span class="detail-info-value">{brand}</span><span class="detail-info-label">리뷰</span><span class="detail-info-value">⭐ {rc:,}개</span></div>{opts}{alh}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div style="text-align:center;margin-top:12px;"><a href="https://www.kurly.com/goods/{pno}" target="_blank" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#5B2C6F,#8E44AD);color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;">🔗 컬리에서 보기</a></div>', unsafe_allow_html=True)
            else: st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">⚠️</div><div>상세 로딩 실패</div></div></div>', unsafe_allow_html=True)
        else: st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">👆</div><div style="font-size:15px;font-weight:600;color:#8E44AD;">상품을 선택하세요</div></div></div>', unsafe_allow_html=True)

# ============================================================
# 🟢 네이버 쇼핑 탭
# ============================================================
def tab_naver():
    if "n_df" not in st.session_state: st.session_state.n_df = None
    if "n_si" not in st.session_state: st.session_state.n_si = 0
    if "n_trend" not in st.session_state: st.session_state.n_trend = None

    auto_id, auto_sec, auto_src = load_naver_keys()

    with st.sidebar:
        st.markdown("### 🟢 네이버 쇼핑 설정")
        if auto_id and auto_sec:
            st.success(f"🔑 API 키 로딩 완료 ({auto_src})")
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
            nr = st.button("🔍 검색", type="primary", use_container_width=True, disabled=not(n_id and n_sec and nq.strip()), key="n_run")

        elif n_mode == "🍹 음료 카테고리":
            n_bev = st.selectbox("음료분류", BEVERAGE_CATEGORIES, 0, key="n_bev", format_func=lambda x: x if x else "전체 (음료)")
            n_brand = st.selectbox("브랜드", BEVERAGE_BRANDS, 0, key="n_brand", format_func=lambda x: x if x else "전체 (브랜드)")
            ns = st.selectbox("정렬", list(NAVER_SORT.keys()), 0, key="n_csort")
            nm = st.slider("최대 결과", 10, 200, 100, 10, key="n_cmax")
            nr = st.button("🍹 카테고리 검색", type="primary", use_container_width=True, disabled=not(n_id and n_sec), key="n_crun")

        else:
            n_qs = st.text_area("비교 키워드 (줄바꿈)", "제로음료\n콤부차\n프로틴음료", height=100, key="n_qs")
            n_mt = st.slider("키워드당 최대", 10, 200, 100, 10, key="n_mt")
            nr = st.button("📊 트렌드 비교", type="primary", use_container_width=True, disabled=not(n_id and n_sec and n_qs.strip()), key="n_trun")

    st.markdown('<div class="naver-header"><h1>🟢 네이버 쇼핑 인텔리전스</h1><p>키워드 · 음료 카테고리 · 트렌드 비교 · 상세 정보</p></div>', unsafe_allow_html=True)

    if not(n_id and n_sec):
        st.info("사이드바에 API 키를 설정해주세요 (secrets.toml 또는 직접 입력)")
        return

    if nr:
        if n_mode == "🔍 키워드 검색" and nq.strip():
            with st.spinner(f"🔍 '{nq}' 검색 중..."):
                items = naver_search(nq, n_id, n_sec, nm, 1, NAVER_SORT[ns])
                parsed = parse_naver(items, nq)
            st.session_state.n_df = pd.DataFrame(parsed) if parsed else None
            st.session_state.n_si = 0; st.session_state.n_trend = None

        elif n_mode == "🍹 음료 카테고리":
            query_parts = []
            if n_bev: query_parts.append(n_bev)
            if n_brand: query_parts.append(n_brand)
            query = " ".join(query_parts) if query_parts else "음료"
            with st.spinner(f"🍹 '{query}' 검색 중..."):
                items = naver_search(query, n_id, n_sec, nm, 1, NAVER_SORT[ns])
                parsed = parse_naver(items, query)
            if parsed:
                st.session_state.n_df = pd.DataFrame(parsed)
                st.session_state.n_trend = calc_trend_scores(st.session_state.n_df)
            else:
                st.session_state.n_df = None; st.session_state.n_trend = None
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
                st.session_state.n_trend = calc_trend_scores(st.session_state.n_df)
            else:
                st.session_state.n_df = None; st.session_state.n_trend = None
            st.session_state.n_si = 0

    df = st.session_state.n_df
    trend_df = st.session_state.n_trend
    if df is None or len(df) == 0:
        st.markdown('<div style="text-align:center;padding:60px;color:#888;"><div style="font-size:48px;">🔍</div><div style="font-size:18px;font-weight:600;color:#03C75A;">검색 조건을 설정하고 시작하세요</div></div>', unsafe_allow_html=True)
        return

    total = len(df); avg_p = df["최저가"].mean(); brands = df["브랜드"].nunique(); malls = df["쇼핑몰"].nunique()
    kw_cnt = df["키워드"].nunique()
    render_metrics([(f"{total:,}","총 상품","mc-green"),(f"₩{avg_p:,.0f}","평균최저가","mc-blue"),(f"{brands:,}","브랜드수","mc-teal"),(f"{malls:,}","쇼핑몰수","mc-amber")])

    # 트렌드 요약 TOP 10
    if trend_df is not None and len(trend_df) > 0:
        st.markdown('<div class="section-title st-green">🏆 요약 트렌드 TOP 10</div>', unsafe_allow_html=True)
        top10 = trend_df.head(10)
        trows = ""
        for idx, row in top10.iterrows():
            trows += f'<tr><td><span class="trend-rank">{idx}</span></td><td style="text-align:left;font-weight:600;">{str(row["대표상품"])[:35]}</td><td>{row.get("대표브랜드","")}</td><td>₩{row["평균가격"]:,.0f}</td><td>{row["상품수"]}</td><td style="font-weight:700;color:#03C75A;">{row["종합점수"]}</td><td>{row["판매순위점수"]}</td><td>{row["추천점수"]}</td></tr>'
        st.markdown(f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #e0e0e0;"><table class="trend-table"><thead><tr><th>#</th><th>제품군</th><th>브랜드</th><th>평균가</th><th>상품수</th><th>종합점수</th><th>판매점수</th><th>추천점수</th></tr></thead><tbody>{trows}</tbody></table></div>', unsafe_allow_html=True)
        st.markdown("---")

    # 키워드별 비교
    if kw_cnt > 1:
        st.markdown('<div class="section-title st-green">📊 키워드별 비교</div>', unsafe_allow_html=True)
        for kw_val in df["키워드"].unique():
            kdf = df[df["키워드"]==kw_val]
            st.markdown(f'<div class="trend-card"><div class="trend-kw">🔹 {kw_val}</div><div class="trend-stat"><span>상품 <b>{len(kdf)}개</b></span><span>평균가 <b>₩{kdf["최저가"].mean():,.0f}</b></span><span>최저 <b>₩{kdf["최저가"].min():,}</b></span><span>최고 <b>₩{kdf["최저가"].max():,}</b></span><span>브랜드 <b>{kdf["브랜드"].nunique()}개</b></span></div></div>', unsafe_allow_html=True)
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

    # 상품 목록 + 상세
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
            rows += f'<tr><td style="text-align:center;color:#03C75A;font-weight:700;">{row["순위"]}</td><td class="product-name"><a href="{url}" target="_blank">{nm}</a><div class="product-desc">{row["쇼핑몰"]}</div></td><td style="text-align:right;font-weight:600;">₩{row["최저가"]:,}</td><td style="text-align:center;">{bd}</td></tr>'
        st.markdown(f'<div style="max-height:520px;overflow-y:auto;border:1px solid #e0e0e0;border-radius:10px;"><table class="product-table naver"><thead><tr><th>#</th><th>상품명</th><th>최저가</th><th>정보</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1: st.download_button("📥 엑셀", to_excel(df), f"naver_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", type="primary", key="n_dl")
        with d2: st.download_button("📥 CSV", to_csv(df), f"naver_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", type="secondary", key="n_csv")

    with col_r:
        st.markdown('<div class="section-title st-green">📦 상품 상세</div>', unsafe_allow_html=True)
        if si < len(df):
            row = df.iloc[si]; img=row["이미지URL"]; name=row["상품명"]; price=row["최저가"]
            cat_path = " > ".join(filter(None, [row.get(f"카테고리{i}","") for i in range(1,5)]))
            st.markdown(f'<div class="detail-panel"><div class="detail-header naver"><h3>📦 {name}</h3><p>{row["쇼핑몰"]}</p></div><div class="detail-body"><img class="detail-img" src="{img}" onerror="this.style.display=\'none\'"><div class="detail-price-box naver"><span class="detail-price-big">₩{price:,}</span></div><div class="detail-info-grid"><span class="detail-info-label">쇼핑몰</span><span class="detail-info-value">{row["쇼핑몰"]}</span><span class="detail-info-label">브랜드</span><span class="detail-info-value">{row["브랜드"] or "-"}</span><span class="detail-info-label">제조사</span><span class="detail-info-value">{row["제조사"] or "-"}</span><span class="detail-info-label">카테고리</span><span class="detail-info-value">{cat_path or "-"}</span><span class="detail-info-label">상품유형</span><span class="detail-info-value">{row["상품유형"]}</span><span class="detail-info-label">상품ID</span><span class="detail-info-value">{row["상품ID"]}</span></div></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center;margin-top:12px;"><a href="{row["상품URL"]}" target="_blank" style="display:inline-block;padding:10px 24px;background:linear-gradient(135deg,#03C75A,#1EC800);color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;">🔗 쇼핑몰에서 보기</a></div>', unsafe_allow_html=True)

# ============================================================
# 메인
# ============================================================
def main():
    t1, t2 = st.tabs(["🟣 마켓컬리 신제품", "🟢 네이버 쇼핑"])
    with t1: tab_kurly()
    with t2: tab_naver()

if __name__ == "__main__":
    main()
