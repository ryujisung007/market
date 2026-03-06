"""
🛍️ 식품 쇼핑 인텔리전스 v5.1
마켓컬리 신제품 + 네이버 쇼핑 통합 대시보드
- secrets.toml 자동 키 로딩
"""
import streamlit as st
import requests
import pandas as pd
import json
import io
import re
from datetime import datetime
from urllib.parse import quote

st.set_page_config(page_title="식품 쇼핑 인텔리전스", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.main-header { background: linear-gradient(135deg, #1A1A2E 0%, #5B2C6F 50%, #8E44AD 100%); padding: 24px 28px; border-radius: 14px; margin-bottom: 20px; }
.main-header h1 { color: white; font-size: 24px; font-weight: 900; margin: 0; }
.main-header p { color: #D2B4DE; font-size: 12px; margin: 5px 0 0; }
.naver-header { background: linear-gradient(135deg, #03C75A 0%, #1EC800 100%); padding: 24px 28px; border-radius: 14px; margin-bottom: 20px; }
.naver-header h1 { color: white; font-size: 24px; font-weight: 900; margin: 0; }
.naver-header p { color: #B8F5CD; font-size: 12px; margin: 5px 0 0; }
.metric-row { display: flex; gap: 10px; margin: 14px 0 20px; flex-wrap: wrap; }
.metric-card { flex: 1; min-width: 110px; padding: 16px 12px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }
.metric-card .num { font-size: 26px; font-weight: 900; letter-spacing: -1px; }
.metric-card .label { font-size: 10px; opacity: 0.85; margin-top: 2px; }
.mc-purple { background: linear-gradient(135deg, #5B2C6F, #8E44AD); }
.mc-blue { background: linear-gradient(135deg, #1A5276, #2E86C1); }
.mc-red { background: linear-gradient(135deg, #922B21, #E74C3C); }
.mc-amber { background: linear-gradient(135deg, #B9770E, #F39C12); }
.mc-green { background: linear-gradient(135deg, #03C75A, #1EC800); }
.mc-teal { background: linear-gradient(135deg, #0E6655, #1ABC9C); }
.bar-row { display: flex; align-items: center; gap: 6px; margin: 3px 0; }
.bar-label { width: 70px; text-align: right; font-size: 11px; color: #444; font-weight: 500; flex-shrink: 0; }
.bar-label-wide { width: 100px; text-align: right; font-size: 11px; color: #444; font-weight: 500; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar { height: 19px; border-radius: 4px; }
.bar-purple { background: linear-gradient(90deg, #8E44AD, #D2B4DE); }
.bar-blue { background: linear-gradient(90deg, #2E86C1, #AED6F1); }
.bar-green { background: linear-gradient(90deg, #03C75A, #82E0AA); }
.bar-red { background: linear-gradient(90deg, #E74C3C, #FADBD8); }
.bar-count { font-size: 10px; color: #666; white-space: nowrap; }
.section-title { font-size: 14px; font-weight: 700; margin: 16px 0 8px; padding-bottom: 4px; border-bottom: 2px solid #eee; }
.st-purple { color: #5B2C6F; } .st-blue { color: #1A5276; } .st-green { color: #03C75A; } .st-red { color: #922B21; }
.product-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.product-table thead tr { background: linear-gradient(90deg, #5B2C6F, #8E44AD); color: white; }
.product-table.naver thead tr { background: linear-gradient(90deg, #03C75A, #1EC800); color: white; }
.product-table th { padding: 9px 5px; font-weight: 600; position: sticky; top: 0; z-index: 10; }
.product-table thead tr th { background: inherit; }
.product-table td { padding: 7px 5px; border-bottom: 1px solid #f0f0f0; }
.product-table tr:nth-child(even) { background: #FAFAFA; }
.product-table tr:hover { background: #F5EEF8; }
.product-table.naver tr:hover { background: #E8F8F0; }
.product-name a { color: #333; text-decoration: none; font-weight: 500; }
.product-name a:hover { color: #8E44AD; }
.product-table.naver .product-name a:hover { color: #03C75A; }
.product-desc { font-size: 10px; color: #999; margin-top: 1px; }
.price-original { text-decoration: line-through; color: #999; font-size: 10px; }
.price-discount { color: #E74C3C; font-weight: 700; }
.discount-rate { color: #E74C3C; font-weight: 700; }
.badge { display: inline-block; padding: 2px 6px; border-radius: 7px; font-size: 9px; font-weight: 700; margin: 1px; }
.badge-top10 { background: #F5EEF8; color: #8E44AD; } .badge-new { background: #EBF5FB; color: #2E86C1; }
.badge-sale { background: #FDEDEC; color: #E74C3C; } .badge-low { background: #FEF9E7; color: #B9770E; }
.badge-naver { background: #E8F8F0; color: #03C75A; } .badge-brand { background: #EBF5FB; color: #2E86C1; }
.detail-panel { border: 1px solid #e0e0e0; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
.detail-header { background: linear-gradient(135deg, #5B2C6F, #8E44AD); padding: 14px 18px; color: white; }
.detail-header.naver { background: linear-gradient(135deg, #03C75A, #1EC800); }
.detail-header h3 { margin: 0; font-size: 14px; font-weight: 700; }
.detail-header p { margin: 3px 0 0; font-size: 10px; color: rgba(255,255,255,0.7); }
.detail-body { padding: 14px 18px; }
.detail-img { width: 100%; border-radius: 10px; margin-bottom: 12px; max-height: 300px; object-fit: contain; background: #f9f9f9; }
.detail-price-box { background: #F8F4FC; border-radius: 10px; padding: 12px; margin-bottom: 12px; }
.detail-price-box.naver { background: #E8F8F0; }
.detail-price-big { font-size: 22px; font-weight: 900; color: #5B2C6F; }
.detail-price-box.naver .detail-price-big { color: #03C75A; }
.detail-info-grid { display: grid; grid-template-columns: 80px 1fr; gap: 5px 10px; font-size: 12px; margin-bottom: 12px; }
.detail-info-label { color: #888; font-weight: 600; } .detail-info-value { color: #333; }
.detail-option { padding: 7px 10px; margin: 3px 0; background: #F8F9FA; border-radius: 7px; font-size: 11px; display: flex; justify-content: space-between; }
.detail-option-name { color: #333; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.detail-option-price { color: #5B2C6F; font-weight: 700; margin-left: 8px; }
.detail-allergy { background: #FFF8E1; border-radius: 7px; padding: 8px 12px; font-size: 11px; color: #856404; margin-top: 8px; }
.detail-placeholder { text-align: center; padding: 70px 20px; color: #bbb; }
.detail-placeholder .icon { font-size: 44px; margin-bottom: 10px; }
.trend-card { border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
.trend-kw { font-size: 16px; font-weight: 900; color: #03C75A; margin-bottom: 8px; }
.trend-stat { display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; color: #555; }
.trend-stat b { color: #333; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1A1A2E 0%, #2C2C54 100%); }
section[data-testid="stSidebar"] .stMarkdown h1, section[data-testid="stSidebar"] .stMarkdown h2, section[data-testid="stSidebar"] .stMarkdown h3 { color: white !important; }
section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] .stMarkdown label { color: #D2B4DE !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 컬리 API
# ============================================================
KURLY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json", "Referer": "https://www.kurly.com/", "Origin": "https://www.kurly.com",
}
KURLY_BASE = "https://api.kurly.com/collection/v2/home/sites/market"
KURLY_SORT = {"신상품순": "0", "추천순": "4", "판매량순": "1", "혜택순": "5", "높은가격순": "3", "낮은가격순": "2"}


@st.cache_data(ttl=3600, show_spinner=False)
def kurly_load_tree():
    r = requests.get(f"{KURLY_BASE}/category-groups", headers=KURLY_HEADERS, timeout=10)
    r.raise_for_status()
    tree = {}
    for cat in r.json()["data"]["main"]:
        code, name = str(cat["code"]), cat["name"]
        subs = cat.get("sub_category_groups", [])
        tree[code] = {"name": name, "subs": {str(s["code"]): s["name"] for s in subs}}
    return tree


@st.cache_data(ttl=600, show_spinner=False)
def kurly_fetch_products(cat_code, sort_type, max_items):
    items, per_page = [], 96
    for page in range(1, (max_items // per_page) + 2):
        try:
            resp = requests.get(f"{KURLY_BASE}/product-categories/{cat_code}/products", headers=KURLY_HEADERS,
                params={"sort_type": sort_type, "page": page, "per_page": per_page, "filters": ""}, timeout=10)
            if resp.status_code != 200:
                break
            prods = resp.json().get("data", [])
            if not prods:
                break
            for rank, p in enumerate(prods, start=len(items) + 1):
                items.append({
                    "순위": rank, "카테고리코드": cat_code, "상품번호": p.get("no", ""),
                    "상품명": p.get("name", ""), "설명": p.get("short_description", ""),
                    "판매가": p.get("sales_price", 0), "할인가": p.get("discounted_price"),
                    "할인율": p.get("discount_rate", 0), "리뷰수": p.get("review_count", ""),
                    "품절": "Y" if p.get("is_sold_out") else "N",
                    "배송유형": ", ".join(d.get("description", "") for d in p.get("delivery_type_infos", [])),
                    "이미지URL": p.get("list_image_url", ""),
                    "상품URL": f"https://www.kurly.com/goods/{p.get('no', '')}",
                    "저재고": "Y" if p.get("is_low_stock") else "N",
                })
            if len(items) >= max_items:
                break
        except Exception:
            break
    return items[:max_items]


@st.cache_data(ttl=600, show_spinner=False)
def kurly_fetch_detail(product_no):
    try:
        r = requests.get(f"https://www.kurly.com/goods/{product_no}",
                         headers={"User-Agent": KURLY_HEADERS["User-Agent"]}, timeout=10)
        if "__NEXT_DATA__" not in r.text:
            return None
        marker = '__NEXT_DATA__" type="application/json">'
        start = r.text.find(marker) + len(marker)
        end = r.text.find("</script>", start)
        return json.loads(r.text[start:end]).get("props", {}).get("pageProps", {}).get("product")
    except Exception:
        return None


# ============================================================
# 네이버 쇼핑 API
# ============================================================
NAVER_SORT = {"정확도순": "sim", "날짜순": "date", "낮은가격순": "asc", "높은가격순": "dsc"}


def load_naver_keys():
    """secrets.toml에서 네이버 API 키 자동 로딩 (naver_shopping → naver_search 순서)"""
    try:
        cid = st.secrets["naver_shopping"]["NAVER_CLIENT_ID"]
        csec = st.secrets["naver_shopping"]["NAVER_CLIENT_SECRET"]
        if cid and csec:
            return cid, csec, "naver_shopping"
    except Exception:
        pass
    try:
        cid = st.secrets["naver_search"]["NAVER_CLIENT_ID"]
        csec = st.secrets["naver_search"]["NAVER_CLIENT_SECRET"]
        if cid and csec:
            return cid, csec, "naver_search"
    except Exception:
        pass
    return "", "", ""


@st.cache_data(ttl=300, show_spinner=False)
def naver_search(query, client_id, client_secret, display=100, start=1, sort="sim"):
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    items = []
    current_start = start
    while len(items) < display:
        batch = min(100, display - len(items))
        try:
            resp = requests.get("https://openapi.naver.com/v1/search/shop.json",
                headers=headers, params={"query": query, "display": batch, "start": current_start, "sort": sort}, timeout=10)
            if resp.status_code != 200:
                break
            data = resp.json()
            result_items = data.get("items", [])
            if not result_items:
                break
            items.extend(result_items)
            current_start += batch
            if current_start > 1000:
                break
        except Exception:
            break
    return items[:display]


def clean_html(text):
    return re.sub(r'<[^>]+>', '', text) if text else ""


def parse_naver_items(items, keyword=""):
    parsed = []
    for i, item in enumerate(items, 1):
        title = clean_html(item.get("title", ""))
        lprice = int(item.get("lprice", 0))
        hprice = int(item.get("hprice", 0)) if item.get("hprice") else None
        parsed.append({
            "순위": i, "키워드": keyword,
            "상품명": title, "최저가": lprice, "최고가": hprice,
            "쇼핑몰": item.get("mallName", ""),
            "브랜드": item.get("brand", ""),
            "제조사": item.get("maker", ""),
            "카테고리1": item.get("category1", ""),
            "카테고리2": item.get("category2", ""),
            "카테고리3": item.get("category3", ""),
            "카테고리4": item.get("category4", ""),
            "상품ID": item.get("productId", ""),
            "상품URL": item.get("link", ""),
            "이미지URL": item.get("image", ""),
            "상품유형": item.get("productType", ""),
        })
    return parsed


# ============================================================
# 공통 렌더링
# ============================================================
def render_metrics(cards):
    html = '<div class="metric-row">'
    for num, label, cls in cards:
        html += f'<div class="metric-card {cls}"><div class="num">{num}</div><div class="label">{label}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_bars(title, tcls, data, bcls, wide=False, pct=False, total=1):
    if not data:
        return
    mx = max(data.values()) if data.values() else 1
    lc = "bar-label-wide" if wide else "bar-label"
    h = f'<div class="section-title {tcls}">{title}</div>'
    for lb, cnt in data.items():
        w = int(cnt / mx * 240) if mx > 0 else 0
        p = f" ({cnt/total*100:.0f}%)" if pct and total > 0 else ""
        h += f'<div class="bar-row"><div class="{lc}">{lb}</div><div class="bar {bcls}" style="width:{w}px;"></div><div class="bar-count">{cnt}개{p}</div></div>'
    st.markdown(h, unsafe_allow_html=True)


def to_excel(df):
    buf = io.BytesIO()
    cols = [c for c in df.columns if c not in ["이미지URL"]]
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df[cols].to_excel(w, sheet_name="전체", index=False)
    return buf.getvalue()


# ============================================================
# 🟣 컬리 탭
# ============================================================
def tab_kurly():
    tree = kurly_load_tree()
    if "k_df" not in st.session_state:
        st.session_state.k_df = None
    if "k_sel" not in st.session_state:
        st.session_state.k_sel = None

    with st.sidebar:
        st.markdown("### 🟣 컬리 설정")
        main_opts = {info["name"]: code for code, info in tree.items()}
        sel_mains = st.multiselect("대분류", list(main_opts.keys()), [], placeholder="선택", key="k_main")
        sel_main_codes = [main_opts[n] for n in sel_mains]

        sub_opts = {}
        if sel_main_codes:
            for mc in sel_main_codes:
                for sc, sn in tree[mc]["subs"].items():
                    sub_opts[f"{tree[mc]['name']} > {sn}"] = sc
        if sub_opts:
            all_sub = st.checkbox("✅ 하위 전체", True, key="k_allsub")
            if all_sub:
                sel_sub_names = list(sub_opts.keys())
            else:
                sel_sub_names = st.multiselect("하위", list(sub_opts.keys()), [], key="k_sub")
            sel_sub_codes = [sub_opts[n] for n in sel_sub_names]
        else:
            sel_sub_codes = []

        st.markdown("---")
        k_sort = st.selectbox("정렬", list(KURLY_SORT.keys()), 0, key="k_sort")
        k_max = st.slider("최대 출력", 10, 300, 100, 10, key="k_max")
        k_kw = st.text_input("키워드", placeholder="콤부차,제로", key="k_kw")
        k_price = st.slider("가격", 0, 100000, (0, 100000), 1000, format="₩%d", key="k_pr")
        k_excl = st.checkbox("품절 제외", True, key="k_excl")
        k_run = st.button("🔍 컬리 수집", type="primary", use_container_width=True,
                          disabled=not sel_main_codes, key="k_run")

    st.markdown(
        '<div class="main-header"><h1>🛒 마켓컬리 신제품 인텔리전스</h1>'
        '<p>카테고리별 트렌드 · 상품 선택 시 우측 상세 표시</p></div>',
        unsafe_allow_html=True,
    )

    if k_run and sel_main_codes:
        targets = []
        if sel_sub_codes:
            for sc in sel_sub_codes:
                nm = sc
                for info in tree.values():
                    if sc in info["subs"]:
                        nm = info["subs"][sc]
                        break
                targets.append((sc, nm))
        else:
            for mc in sel_main_codes:
                targets.append((mc, tree[mc]["name"]))
        if targets:
            prog = st.progress(0, "📡 수집...")
            all_d = []
            for i, (code, name) in enumerate(targets):
                prog.progress((i + 1) / len(targets), f"📡 [{i+1}/{len(targets)}] {name}")
                items = kurly_fetch_products(code, KURLY_SORT[k_sort], k_max)
                for it in items:
                    it["카테고리명"] = name
                all_d.extend(items)
            prog.empty()
            if all_d:
                df = pd.DataFrame(all_d).drop_duplicates(subset=["상품번호"], keep="first")
                if k_kw.strip():
                    kws = [k.strip() for k in k_kw.split(",") if k.strip()]
                    df = df[df["상품명"].str.contains("|".join(kws), case=False, na=False)]
                if k_excl:
                    df = df[df["품절"] == "N"]
                pmin, pmax = k_price
                df = df[(df["판매가"] >= pmin) & (df["판매가"] <= pmax)].head(k_max).reset_index(drop=True)
                st.session_state.k_df = df
                st.session_state.k_sel = None

    df = st.session_state.k_df
    if df is None or len(df) == 0:
        st.markdown(
            '<div style="text-align:center;padding:60px;color:#888;">'
            '<div style="font-size:40px;">🛍️</div>'
            '<div style="font-size:16px;font-weight:600;color:#5B2C6F;">사이드바에서 카테고리 선택 → 수집 시작</div></div>',
            unsafe_allow_html=True,
        )
        return

    total = len(df)
    avg_p = df["판매가"].mean()
    dc = (df["할인율"] > 0).sum()
    ad = df.loc[df["할인율"] > 0, "할인율"].mean() if dc > 0 else 0
    lc = (df["저재고"] == "Y").sum()
    render_metrics([
        (f"{total:,}", "총 상품", "mc-purple"),
        (f"₩{avg_p:,.0f}", "평균가격", "mc-blue"),
        (f"{dc:,}", f"할인 (평균{ad:.0f}%)", "mc-red"),
        (f"{lc:,}", "품절임박⚡", "mc-amber"),
    ])

    c1, c2 = st.columns(2)
    with c1:
        bins = [0, 3000, 5000, 10000, 20000, 30000, 50000, float("inf")]
        labels = ["~3천", "3~5천", "5천~1만", "1~2만", "2~3만", "3~5만", "5만~"]
        df["가격대"] = pd.cut(df["판매가"], bins=bins, labels=labels)
        pd_d = df["가격대"].value_counts().sort_index()
        render_bars("💰 가격대", "st-purple",
                    {str(k): int(v) for k, v in pd_d.items() if v > 0}, "bar-purple",
                    pct=True, total=total)
    with c2:
        if df["카테고리명"].nunique() > 1:
            cd = df["카테고리명"].value_counts().head(10)
            render_bars("📁 카테고리별", "st-blue",
                        {str(k)[:12]: int(v) for k, v in cd.items()}, "bar-blue", wide=True)

    st.markdown("---")
    col_l, col_r = st.columns([6, 4])

    with col_l:
        plabels = [f"[{r['순위']}] {r['상품명'][:28]} | ₩{r['판매가']:,}" for _, r in df.iterrows()]
        pnos = [r["상품번호"] for _, r in df.iterrows()]
        cidx = 0
        if st.session_state.k_sel and st.session_state.k_sel in pnos:
            cidx = pnos.index(st.session_state.k_sel)
        si = st.selectbox("🔍 상품 선택 → 우측 상세", range(len(plabels)), cidx,
                          format_func=lambda i: plabels[i], key="k_psel")
        st.session_state.k_sel = pnos[si]

        rows = ""
        for _, row in df.iterrows():
            nm = str(row["상품명"])[:36]
            url = row["상품URL"]
            if row["할인가"] and row["할인율"] and row["할인율"] > 0:
                ph = (f'<span class="price-original">₩{row["판매가"]:,}</span><br>'
                      f'<span class="price-discount">₩{row["할인가"]:,}</span>')
                dh = f'<span class="discount-rate">{row["할인율"]}%</span>'
            else:
                ph = f'₩{row["판매가"]:,}'
                dh = "-"
            bd = ""
            if row["순위"] <= 10:
                bd += '<span class="badge badge-top10">🆕TOP10</span>'
            elif row["순위"] <= 30:
                bd += '<span class="badge badge-new">NEW</span>'
            if row["할인율"] and row["할인율"] >= 20:
                bd += '<span class="badge badge-sale">🔥SALE</span>'
            if row.get("저재고") == "Y":
                bd += '<span class="badge badge-low">⚡임박</span>'
            cn = str(row.get("카테고리명", ""))[:8]
            rows += (f'<tr><td style="text-align:center;color:#8E44AD;font-weight:700;">{row["순위"]}</td>'
                     f'<td style="text-align:center;font-size:10px;">{cn}</td>'
                     f'<td class="product-name"><a href="{url}" target="_blank">{nm}</a></td>'
                     f'<td style="text-align:right;font-size:11px;">{ph}</td>'
                     f'<td style="text-align:center;">{dh}</td>'
                     f'<td style="text-align:center;">{bd}</td></tr>')
        st.markdown(
            f'<div style="max-height:500px;overflow-y:auto;border:1px solid #e0e0e0;border-radius:10px;">'
            f'<table class="product-table"><thead><tr><th>#</th><th>카테고리</th><th>상품명</th>'
            f'<th>가격</th><th>할인</th><th>상태</th></tr></thead><tbody>{rows}</tbody></table></div>',
            unsafe_allow_html=True,
        )
        st.download_button("📥 엑셀", to_excel(df),
                           f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                           type="primary", key="k_dl")

    with col_r:
        st.markdown('<div class="section-title st-purple">📦 상품 상세</div>', unsafe_allow_html=True)
        pno = st.session_state.k_sel
        if pno:
            with st.spinner("로딩..."):
                det = kurly_fetch_detail(pno)
            if det:
                name = det.get("name", "")
                img = det.get("mainImageUrl", "")
                bp = det.get("basePrice", 0)
                dp_val = det.get("discountedPrice")
                dr_val = det.get("discountRate", 0)
                if dp_val and dr_val and dr_val > 0:
                    prh = (f'<span class="detail-price-big">₩{dp_val:,}</span> '
                           f'<span style="text-decoration:line-through;color:#999;font-size:12px;">₩{bp:,}</span> '
                           f'<span style="background:#E74C3C;color:white;padding:2px 8px;border-radius:10px;'
                           f'font-size:12px;font-weight:700;">{dr_val}%</span>')
                else:
                    prh = f'<span class="detail-price-big">₩{bp:,}</span>'
                vol = det.get("volume", "")
                seller = det.get("sellerName", "")
                brand = det.get("brandInfo", {}).get("name", "-") if det.get("brandInfo") else "-"
                rc = det.get("reviewCount", 0)
                allergy = det.get("allergy", "")
                delivery = ", ".join(str(d) for d in det.get("deliveryTypeNames", []))
                opts = ""
                for dp_item in det.get("dealProducts", [])[:6]:
                    dpn = dp_item.get("name", "")[:30]
                    dpp = dp_item.get("basePrice", 0)
                    opts += (f'<div class="detail-option">'
                             f'<span class="detail-option-name">{dpn}</span>'
                             f'<span class="detail-option-price">₩{dpp:,}</span></div>')
                alh = ""
                if allergy and allergy.strip():
                    alh = f'<div class="detail-allergy">⚠️ {allergy.replace(chr(10), "<br>")}</div>'
                st.markdown(
                    f'<div class="detail-panel"><div class="detail-header"><h3>📦 {name}</h3></div>'
                    f'<div class="detail-body">'
                    f'<img class="detail-img" src="{img}" onerror="this.style.display=\'none\'">'
                    f'<div class="detail-price-box">{prh}</div>'
                    f'<div class="detail-info-grid">'
                    f'<span class="detail-info-label">용량</span><span class="detail-info-value">{vol}</span>'
                    f'<span class="detail-info-label">배송</span><span class="detail-info-value">{delivery}</span>'
                    f'<span class="detail-info-label">판매자</span><span class="detail-info-value">{seller}</span>'
                    f'<span class="detail-info-label">브랜드</span><span class="detail-info-value">{brand}</span>'
                    f'<span class="detail-info-label">리뷰</span><span class="detail-info-value">⭐ {rc:,}개</span>'
                    f'</div>{opts}{alh}</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="text-align:center;margin-top:10px;">'
                    f'<a href="https://www.kurly.com/goods/{pno}" target="_blank" '
                    f'style="display:inline-block;padding:9px 22px;'
                    f'background:linear-gradient(135deg,#5B2C6F,#8E44AD);'
                    f'color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:12px;">'
                    f'🔗 컬리에서 보기</a></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="detail-panel"><div class="detail-placeholder">'
                    '<div class="icon">⚠️</div><div>상세 로딩 실패</div></div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="detail-panel"><div class="detail-placeholder">'
                '<div class="icon">👆</div>'
                '<div style="font-size:13px;font-weight:600;color:#8E44AD;">상품을 선택하세요</div>'
                '</div></div>',
                unsafe_allow_html=True,
            )


# ============================================================
# 🟢 네이버 쇼핑 탭
# ============================================================
def tab_naver():
    if "n_df" not in st.session_state:
        st.session_state.n_df = None
    if "n_sel_idx" not in st.session_state:
        st.session_state.n_sel_idx = 0

    # secrets.toml 자동 로딩
    auto_id, auto_secret, auto_source = load_naver_keys()

    with st.sidebar:
        st.markdown("### 🟢 네이버 쇼핑 설정")

        if auto_id and auto_secret:
            st.success(f"🔑 API 키 자동 로딩 ({auto_source})")
            n_id = auto_id
            n_secret = auto_secret
        else:
            st.warning("secrets.toml에 키 없음 — 직접 입력")
            n_id = st.text_input("Client ID", type="password", key="n_id")
            n_secret = st.text_input("Client Secret", type="password", key="n_sec")

        st.markdown("---")
        n_mode = st.radio("검색 모드", ["🔍 키워드 검색", "📊 트렌드 비교"], key="n_mode")

        if n_mode == "🔍 키워드 검색":
            n_query = st.text_input("검색어", placeholder="제로음료", key="n_q")
            n_sort = st.selectbox("정렬", list(NAVER_SORT.keys()), 0, key="n_sort")
            n_max = st.slider("최대 결과", 10, 300, 100, 10, key="n_max")
            n_run = st.button("🔍 네이버 검색", type="primary", use_container_width=True,
                              disabled=not (n_id and n_secret and n_query.strip()), key="n_run")
        else:
            n_queries = st.text_area("비교 키워드 (줄바꿈 구분)",
                                     "제로음료\n콤부차\n프로틴음료", height=100, key="n_qs")
            n_max_t = st.slider("키워드당 최대", 10, 100, 50, 10, key="n_maxt")
            n_run = st.button("📊 트렌드 비교", type="primary", use_container_width=True,
                              disabled=not (n_id and n_secret and n_queries.strip()), key="n_trun")

    st.markdown(
        '<div class="naver-header"><h1>🟢 네이버 쇼핑 인텔리전스</h1>'
        '<p>키워드 검색 · 트렌드 비교 · 상품 상세</p></div>',
        unsafe_allow_html=True,
    )

    if not (n_id and n_secret):
        st.info("사이드바에 네이버 API 키를 입력하거나 secrets.toml에 설정해주세요.")
        return

    if n_run:
        if n_mode == "🔍 키워드 검색" and n_query.strip():
            with st.spinner(f"🔍 '{n_query}' 검색 중..."):
                items = naver_search(n_query, n_id, n_secret, n_max, 1, NAVER_SORT[n_sort])
                parsed = parse_naver_items(items, n_query)
            if parsed:
                st.session_state.n_df = pd.DataFrame(parsed)
                st.session_state.n_sel_idx = 0
            else:
                st.warning("검색 결과가 없습니다.")
                st.session_state.n_df = None
        elif n_mode == "📊 트렌드 비교" and n_queries.strip():
            queries = [q.strip() for q in n_queries.split("\n") if q.strip()]
            all_parsed = []
            prog = st.progress(0, "검색 중...")
            for i, q in enumerate(queries):
                prog.progress((i + 1) / len(queries), f"🔍 '{q}' 검색...")
                items = naver_search(q, n_id, n_secret, n_max_t, 1, "sim")
                all_parsed.extend(parse_naver_items(items, q))
            prog.empty()
            if all_parsed:
                st.session_state.n_df = pd.DataFrame(all_parsed)
                st.session_state.n_sel_idx = 0
            else:
                st.warning("검색 결과가 없습니다.")
                st.session_state.n_df = None

    df = st.session_state.n_df
    if df is None or len(df) == 0:
        st.markdown(
            '<div style="text-align:center;padding:60px;color:#888;">'
            '<div style="font-size:40px;">🔍</div>'
            '<div style="font-size:16px;font-weight:600;color:#03C75A;">검색어를 입력하고 검색 시작</div></div>',
            unsafe_allow_html=True,
        )
        return

    total = len(df)
    avg_p = df["최저가"].mean()
    brands = df["브랜드"].nunique()
    malls = df["쇼핑몰"].nunique()
    kw_cnt = df["키워드"].nunique()

    render_metrics([
        (f"{total:,}", "총 상품", "mc-green"),
        (f"₩{avg_p:,.0f}", "평균 최저가", "mc-blue"),
        (f"{brands:,}", "브랜드 수", "mc-teal"),
        (f"{malls:,}", "쇼핑몰 수", "mc-amber"),
    ])

    # 트렌드 비교
    if kw_cnt > 1:
        st.markdown('<div class="section-title st-green">📊 키워드별 트렌드 비교</div>', unsafe_allow_html=True)
        for kw in df["키워드"].unique():
            kdf = df[df["키워드"] == kw]
            st.markdown(
                f'<div class="trend-card">'
                f'<div class="trend-kw">🔹 {kw}</div>'
                f'<div class="trend-stat">'
                f'<span>상품 <b>{len(kdf)}개</b></span>'
                f'<span>평균가 <b>₩{kdf["최저가"].mean():,.0f}</b></span>'
                f'<span>최저 <b>₩{kdf["최저가"].min():,}</b></span>'
                f'<span>최고 <b>₩{kdf["최저가"].max():,}</b></span>'
                f'<span>브랜드 <b>{kdf["브랜드"].nunique()}개</b></span>'
                f'<span>쇼핑몰 <b>{kdf["쇼핑몰"].nunique()}개</b></span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown("---")

    # 차트
    c1, c2 = st.columns(2)
    with c1:
        bins = [0, 5000, 10000, 20000, 30000, 50000, 100000, float("inf")]
        labels = ["~5천", "5천~1만", "1~2만", "2~3만", "3~5만", "5~10만", "10만~"]
        df["가격대"] = pd.cut(df["최저가"], bins=bins, labels=labels)
        pd_d = df["가격대"].value_counts().sort_index()
        render_bars("💰 가격대 분포", "st-green",
                    {str(k): int(v) for k, v in pd_d.items() if v > 0}, "bar-green",
                    pct=True, total=total)
    with c2:
        mall_d = df["쇼핑몰"].value_counts().head(10)
        render_bars("🏪 쇼핑몰 분포", "st-blue",
                    {str(k)[:12]: int(v) for k, v in mall_d.items()}, "bar-blue", wide=True)

    st.markdown("---")

    # 상품 목록 + 상세
    col_l, col_r = st.columns([6, 4])

    with col_l:
        plabels = [f"[{r['순위']}] {r['상품명'][:28]} | ₩{r['최저가']:,} | {r['쇼핑몰'][:8]}"
                   for _, r in df.iterrows()]
        si = st.selectbox("🔍 상품 선택 → 우측 상세", range(len(plabels)),
                          st.session_state.n_sel_idx,
                          format_func=lambda i: plabels[i], key="n_psel")
        st.session_state.n_sel_idx = si

        rows = ""
        for _, row in df.head(200).iterrows():
            nm = str(row["상품명"])[:36]
            url = row["상품URL"]
            bd = ""
            if row["브랜드"]:
                bd += f'<span class="badge badge-brand">{row["브랜드"][:8]}</span>'
            if kw_cnt > 1:
                bd += f'<span class="badge badge-naver">{row["키워드"][:6]}</span>'
            rows += (f'<tr><td style="text-align:center;color:#03C75A;font-weight:700;">{row["순위"]}</td>'
                     f'<td class="product-name"><a href="{url}" target="_blank">{nm}</a>'
                     f'<div class="product-desc">{row["쇼핑몰"]}</div></td>'
                     f'<td style="text-align:right;font-weight:600;">₩{row["최저가"]:,}</td>'
                     f'<td style="text-align:center;">{bd}</td></tr>')
        st.markdown(
            f'<div style="max-height:500px;overflow-y:auto;border:1px solid #e0e0e0;border-radius:10px;">'
            f'<table class="product-table naver"><thead><tr><th>#</th><th>상품명</th>'
            f'<th>최저가</th><th>정보</th></tr></thead><tbody>{rows}</tbody></table></div>',
            unsafe_allow_html=True,
        )
        st.download_button("📥 엑셀", to_excel(df),
                           f"naver_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                           type="primary", key="n_dl")

    with col_r:
        st.markdown('<div class="section-title st-green">📦 상품 상세</div>', unsafe_allow_html=True)
        if si < len(df):
            row = df.iloc[si]
            img = row["이미지URL"]
            name = row["상품명"]
            price = row["최저가"]
            cat_path = " > ".join(filter(None, [row.get(f"카테고리{i}", "") for i in range(1, 5)]))
            st.markdown(
                f'<div class="detail-panel">'
                f'<div class="detail-header naver"><h3>📦 {name}</h3><p>{row["쇼핑몰"]}</p></div>'
                f'<div class="detail-body">'
                f'<img class="detail-img" src="{img}" onerror="this.style.display=\'none\'">'
                f'<div class="detail-price-box naver">'
                f'<span class="detail-price-big">₩{price:,}</span></div>'
                f'<div class="detail-info-grid">'
                f'<span class="detail-info-label">쇼핑몰</span><span class="detail-info-value">{row["쇼핑몰"]}</span>'
                f'<span class="detail-info-label">브랜드</span><span class="detail-info-value">{row["브랜드"] or "-"}</span>'
                f'<span class="detail-info-label">제조사</span><span class="detail-info-value">{row["제조사"] or "-"}</span>'
                f'<span class="detail-info-label">카테고리</span><span class="detail-info-value">{cat_path or "-"}</span>'
                f'<span class="detail-info-label">상품유형</span><span class="detail-info-value">{row["상품유형"]}</span>'
                f'<span class="detail-info-label">상품ID</span><span class="detail-info-value">{row["상품ID"]}</span>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="text-align:center;margin-top:10px;">'
                f'<a href="{row["상품URL"]}" target="_blank" '
                f'style="display:inline-block;padding:9px 22px;'
                f'background:linear-gradient(135deg,#03C75A,#1EC800);'
                f'color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:12px;">'
                f'🔗 쇼핑몰에서 보기</a></div>',
                unsafe_allow_html=True,
            )


# ============================================================
# 메인
# ============================================================
def main():
    tab1, tab2 = st.tabs(["🟣 마켓컬리 신제품", "🟢 네이버 쇼핑"])
    with tab1:
        tab_kurly()
    with tab2:
        tab_naver()


if __name__ == "__main__":
    main()
