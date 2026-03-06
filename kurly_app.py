"""
🛒 마켓컬리 신제품 인텔리전스 대시보드 v4.0
Streamlit 기반 — 상품 상세 패널 포함
"""
import streamlit as st
import requests
import pandas as pd
import json
import io
from datetime import datetime

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="마켓컬리 신제품 인텔리전스",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 커스텀 CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #1A1A2E 0%, #5B2C6F 50%, #8E44AD 100%);
    padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;
}
.main-header h1 { color: white; font-size: 26px; font-weight: 900; margin: 0; letter-spacing: -0.5px; }
.main-header p { color: #D2B4DE; font-size: 12px; margin: 6px 0 0; }

.metric-row { display: flex; gap: 12px; margin: 16px 0 24px; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 120px; padding: 18px 14px; border-radius: 14px;
    text-align: center; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}
.metric-card .num { font-size: 28px; font-weight: 900; letter-spacing: -1px; }
.metric-card .label { font-size: 11px; opacity: 0.85; margin-top: 3px; }
.mc-purple { background: linear-gradient(135deg, #5B2C6F, #8E44AD); }
.mc-blue { background: linear-gradient(135deg, #1A5276, #2E86C1); }
.mc-red { background: linear-gradient(135deg, #922B21, #E74C3C); }
.mc-amber { background: linear-gradient(135deg, #B9770E, #F39C12); }

.bar-row { display: flex; align-items: center; gap: 8px; margin: 3px 0; }
.bar-label { width: 70px; text-align: right; font-size: 12px; color: #444; font-weight: 500; flex-shrink: 0; }
.bar-label-wide { width: 100px; text-align: right; font-size: 12px; color: #444; font-weight: 500; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar { height: 20px; border-radius: 5px; }
.bar-purple { background: linear-gradient(90deg, #8E44AD, #D2B4DE); }
.bar-blue { background: linear-gradient(90deg, #2E86C1, #AED6F1); }
.bar-red { background: linear-gradient(90deg, #E74C3C, #FADBD8); }
.bar-count { font-size: 11px; color: #666; white-space: nowrap; }

.section-title { font-size: 15px; font-weight: 700; margin: 18px 0 10px; padding-bottom: 5px; border-bottom: 2px solid #eee; }
.st-purple { color: #5B2C6F; }
.st-blue { color: #1A5276; }
.st-red { color: #922B21; }

.product-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.product-table thead tr { background: linear-gradient(90deg, #5B2C6F, #8E44AD); color: white; }
.product-table th { padding: 10px 6px; font-weight: 600; position: sticky; top: 0; z-index: 10; background: linear-gradient(90deg, #5B2C6F, #8E44AD); }
.product-table td { padding: 8px 6px; border-bottom: 1px solid #f0f0f0; }
.product-table tr:nth-child(even) { background: #FAFAFA; }
.product-table tr:hover { background: #F5EEF8; }
.product-name a { color: #333; text-decoration: none; font-weight: 500; }
.product-name a:hover { color: #8E44AD; }
.product-desc { font-size: 10px; color: #999; margin-top: 2px; }
.price-original { text-decoration: line-through; color: #999; font-size: 11px; }
.price-discount { color: #E74C3C; font-weight: 700; }
.discount-rate { color: #E74C3C; font-weight: 700; }

.badge { display: inline-block; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: 700; margin: 1px; }
.badge-top10 { background: #F5EEF8; color: #8E44AD; }
.badge-new { background: #EBF5FB; color: #2E86C1; }
.badge-sale { background: #FDEDEC; color: #E74C3C; }
.badge-low { background: #FEF9E7; color: #B9770E; }

/* 상세 패널 */
.detail-panel { border: 1px solid #e0e0e0; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.detail-header { background: linear-gradient(135deg, #5B2C6F, #8E44AD); padding: 16px 20px; color: white; }
.detail-header h3 { margin: 0; font-size: 15px; font-weight: 700; }
.detail-header p { margin: 4px 0 0; font-size: 11px; color: #D2B4DE; }
.detail-body { padding: 16px 20px; }
.detail-img { width: 100%; border-radius: 10px; margin-bottom: 14px; }
.detail-price-box { background: #F8F4FC; border-radius: 10px; padding: 14px; margin-bottom: 14px; }
.detail-price-big { font-size: 24px; font-weight: 900; color: #5B2C6F; }
.detail-price-original { font-size: 13px; text-decoration: line-through; color: #999; margin-left: 8px; }
.detail-discount-badge { display: inline-block; background: #E74C3C; color: white; padding: 3px 10px; border-radius: 12px; font-size: 13px; font-weight: 700; margin-left: 8px; }
.detail-info-grid { display: grid; grid-template-columns: 85px 1fr; gap: 6px 12px; font-size: 13px; margin-bottom: 14px; }
.detail-info-label { color: #888; font-weight: 600; }
.detail-info-value { color: #333; }
.detail-option { padding: 8px 12px; margin: 4px 0; background: #F8F9FA; border-radius: 8px; font-size: 12px; display: flex; justify-content: space-between; }
.detail-option-name { color: #333; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.detail-option-price { color: #5B2C6F; font-weight: 700; white-space: nowrap; margin-left: 8px; }
.detail-option-soldout { color: #999; text-decoration: line-through; }
.detail-allergy { background: #FFF8E1; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #856404; margin-top: 10px; }
.detail-placeholder { text-align: center; padding: 80px 20px; color: #bbb; }
.detail-placeholder .icon { font-size: 48px; margin-bottom: 12px; }

section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1A1A2E 0%, #2C2C54 100%); }
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 { color: white !important; }
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown label { color: #D2B4DE !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# API
# ============================================================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.kurly.com/",
    "Origin": "https://www.kurly.com",
}
BASE = "https://api.kurly.com/collection/v2/home/sites/market"
SORT_OPTIONS = {"신상품순": "0", "추천순": "4", "판매량순": "1", "혜택순": "5", "높은가격순": "3", "낮은가격순": "2"}


@st.cache_data(ttl=3600, show_spinner=False)
def load_category_tree():
    r = requests.get(f"{BASE}/category-groups", headers=HEADERS, timeout=10)
    r.raise_for_status()
    main_cats = r.json()["data"]["main"]
    tree = {}
    for cat in main_cats:
        code, name = str(cat["code"]), cat["name"]
        subs = cat.get("sub_category_groups", [])
        tree[code] = {"name": name, "subs": {str(s["code"]): s["name"] for s in subs}}
    return tree


@st.cache_data(ttl=600, show_spinner=False)
def fetch_products(cat_code, sort_type, max_items):
    items, per_page = [], 96
    for page in range(1, (max_items // per_page) + 2):
        try:
            resp = requests.get(
                f"{BASE}/product-categories/{cat_code}/products",
                headers=HEADERS,
                params={"sort_type": sort_type, "page": page, "per_page": per_page, "filters": ""},
                timeout=10,
            )
            if resp.status_code != 200:
                break
            prods = resp.json().get("data", [])
            if not prods:
                break
            for rank, p in enumerate(prods, start=len(items) + 1):
                items.append({
                    "순위": rank, "카테고리코드": cat_code,
                    "상품번호": p.get("no", ""),
                    "상품명": p.get("name", ""),
                    "설명": p.get("short_description", ""),
                    "판매가": p.get("sales_price", 0),
                    "할인가": p.get("discounted_price"),
                    "할인율": p.get("discount_rate", 0),
                    "리뷰수": p.get("review_count", ""),
                    "품절": "Y" if p.get("is_sold_out") else "N",
                    "배송유형": ", ".join(d.get("description", "") for d in p.get("delivery_type_infos", [])),
                    "이미지URL": p.get("list_image_url", ""),
                    "상품URL": f"https://www.kurly.com/goods/{p.get('no', '')}",
                    "스티커": ", ".join(s.get("text", str(s)) if isinstance(s, dict) else str(s) for s in p.get("stickers_v2", [])),
                    "태그": ", ".join(str(t) for t in p.get("tags", [])),
                    "저재고": "Y" if p.get("is_low_stock") else "N",
                })
            if len(items) >= max_items:
                break
        except Exception:
            break
    return items[:max_items]


@st.cache_data(ttl=600, show_spinner=False)
def fetch_product_detail(product_no):
    """__NEXT_DATA__에서 상품 상세 추출"""
    try:
        r = requests.get(
            f"https://www.kurly.com/goods/{product_no}",
            headers={"User-Agent": HEADERS["User-Agent"]},
            timeout=10,
        )
        if "__NEXT_DATA__" not in r.text:
            return None
        marker = '__NEXT_DATA__" type="application/json">'
        start = r.text.find(marker) + len(marker)
        end = r.text.find("</script>", start)
        return json.loads(r.text[start:end]).get("props", {}).get("pageProps", {}).get("product")
    except Exception:
        return None


# ============================================================
# 렌더링
# ============================================================
def render_metric_cards(total, avg_price, disc_cnt, avg_disc, low_cnt):
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card mc-purple"><div class="num">{total:,}</div><div class="label">총 상품</div></div>
        <div class="metric-card mc-blue"><div class="num">₩{avg_price:,.0f}</div><div class="label">평균 가격</div></div>
        <div class="metric-card mc-red"><div class="num">{disc_cnt:,}</div><div class="label">할인 (평균 {avg_disc:.0f}%)</div></div>
        <div class="metric-card mc-amber"><div class="num">{low_cnt:,}</div><div class="label">품절임박 ⚡</div></div>
    </div>""", unsafe_allow_html=True)


def render_bar_chart(title, title_class, data_dict, bar_class, label_wide=False, show_pct=False, total=1):
    if not data_dict:
        return
    max_val = max(data_dict.values()) if data_dict.values() else 1
    lcls = "bar-label-wide" if label_wide else "bar-label"
    html = f'<div class="section-title {title_class}">{title}</div>'
    for label, cnt in data_dict.items():
        w = int(cnt / max_val * 260) if max_val > 0 else 0
        pct = f" ({cnt/total*100:.0f}%)" if show_pct and total > 0 else ""
        html += f'<div class="bar-row"><div class="{lcls}">{label}</div><div class="bar {bar_class}" style="width:{w}px;"></div><div class="bar-count">{cnt}개{pct}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_product_table(df):
    rows = ""
    for idx, row in df.iterrows():
        nm = str(row["상품명"])[:38]
        desc = str(row["설명"])[:25] if row["설명"] else ""
        url = row["상품URL"]
        if row["할인가"] and row["할인율"] and row["할인율"] > 0:
            ph = f'<span class="price-original">₩{row["판매가"]:,}</span><br><span class="price-discount">₩{row["할인가"]:,}</span>'
            dh = f'<span class="discount-rate">{row["할인율"]}%</span>'
        else:
            ph = f'₩{row["판매가"]:,}'
            dh = "-"
        badges = ""
        if row["순위"] <= 10:
            badges += '<span class="badge badge-top10">🆕TOP10</span>'
        elif row["순위"] <= 30:
            badges += '<span class="badge badge-new">NEW</span>'
        if row["할인율"] and row["할인율"] >= 20:
            badges += '<span class="badge badge-sale">🔥SALE</span>'
        if row.get("저재고") == "Y":
            badges += '<span class="badge badge-low">⚡임박</span>'
        cn = str(row.get("카테고리명", ""))[:8]
        rows += f'<tr><td style="text-align:center;color:#8E44AD;font-weight:700;">{row["순위"]}</td><td style="text-align:center;font-size:11px;">{cn}</td><td class="product-name"><a href="{url}" target="_blank">{nm}</a><div class="product-desc">{desc}</div></td><td style="text-align:right;font-size:12px;">{ph}</td><td style="text-align:center;">{dh}</td><td style="text-align:center;font-size:11px;">{row["리뷰수"]}</td><td style="text-align:center;">{badges}</td></tr>'
    st.markdown(f"""
    <div style="max-height:550px;overflow-y:auto;border:1px solid #e0e0e0;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
    <table class="product-table"><thead><tr>
        <th style="width:35px;">#</th><th style="width:60px;">카테고리</th><th>상품명</th>
        <th style="width:85px;">가격</th><th style="width:42px;">할인</th><th style="width:42px;">리뷰</th><th style="width:85px;">상태</th>
    </tr></thead><tbody>{rows}</tbody></table></div>
    """, unsafe_allow_html=True)


def render_detail_panel(product):
    if product is None:
        st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">⚠️</div><div>상세 정보를 불러올 수 없습니다</div></div></div>', unsafe_allow_html=True)
        return

    name = product.get("name", "")
    desc = product.get("shortDescription", "")
    img = product.get("mainImageUrl", "")
    base_price = product.get("basePrice", 0)
    disc_price = product.get("discountedPrice")
    disc_rate = product.get("discountRate", 0)
    volume = product.get("volume", "")
    sales_unit = product.get("salesUnit", "")
    seller = product.get("sellerName", "")
    origin = product.get("productOrigin", "")
    allergy = product.get("allergy", "")
    review_count = product.get("reviewCount", 0)
    is_soldout = product.get("isSoldOut", False)
    storage_types = product.get("storageTypes", [])
    delivery_names = product.get("deliveryTypeNames", [])
    deal_products = product.get("dealProducts", [])
    brand_info = product.get("brandInfo", {})

    if disc_price and disc_rate and disc_rate > 0:
        price_html = f'<span class="detail-price-big">₩{disc_price:,}</span><span class="detail-price-original">₩{base_price:,}</span><span class="detail-discount-badge">{disc_rate}% OFF</span>'
    else:
        price_html = f'<span class="detail-price-big">₩{base_price:,}</span>'

    storage_str = ", ".join(t.get("label", t) if isinstance(t, dict) else str(t) for t in storage_types) if storage_types else "-"
    delivery_str = ", ".join(str(d) for d in delivery_names) if delivery_names else "-"
    brand_name = brand_info.get("name", "-") if brand_info else "-"
    status = "🔴 품절" if is_soldout else "🟢 판매중"

    options_html = ""
    if deal_products:
        options_html = '<div style="font-weight:700;font-size:13px;color:#5B2C6F;margin:14px 0 8px;">📦 옵션 상품</div>'
        for dp in deal_products[:8]:
            dp_name = dp.get("name", "")[:35]
            dp_price = dp.get("basePrice", 0)
            dp_disc = dp.get("discountedPrice")
            dp_soldout = dp.get("isSoldOut", False)
            if dp_soldout:
                options_html += f'<div class="detail-option"><span class="detail-option-name detail-option-soldout">{dp_name}</span><span style="color:#999;font-size:11px;">품절</span></div>'
            elif dp_disc:
                options_html += f'<div class="detail-option"><span class="detail-option-name">{dp_name}</span><span class="detail-option-price">₩{dp_disc:,}</span></div>'
            else:
                options_html += f'<div class="detail-option"><span class="detail-option-name">{dp_name}</span><span class="detail-option-price">₩{dp_price:,}</span></div>'

    allergy_html = ""
    if allergy and allergy.strip():
        allergy_html = f'<div class="detail-allergy">⚠️ <b>알레르기</b><br>{allergy.replace(chr(10), "<br>")}</div>'

    st.markdown(f"""
    <div class="detail-panel">
        <div class="detail-header">
            <h3>📦 {name}</h3>
            <p>{desc}</p>
        </div>
        <div class="detail-body">
            <img class="detail-img" src="{img}" alt="{name}" onerror="this.style.display='none'">
            <div class="detail-price-box">{price_html}</div>
            <div class="detail-info-grid">
                <span class="detail-info-label">상태</span><span class="detail-info-value">{status}</span>
                <span class="detail-info-label">판매단위</span><span class="detail-info-value">{sales_unit}</span>
                <span class="detail-info-label">중량/용량</span><span class="detail-info-value">{volume}</span>
                <span class="detail-info-label">배송</span><span class="detail-info-value">{delivery_str}</span>
                <span class="detail-info-label">보관</span><span class="detail-info-value">{storage_str}</span>
                <span class="detail-info-label">판매자</span><span class="detail-info-value">{seller}</span>
                <span class="detail-info-label">브랜드</span><span class="detail-info-value">{brand_name}</span>
                <span class="detail-info-label">원산지</span><span class="detail-info-value">{origin}</span>
                <span class="detail-info-label">리뷰</span><span class="detail-info-value">⭐ {review_count:,}개</span>
            </div>
            {options_html}
            {allergy_html}
        </div>
    </div>""", unsafe_allow_html=True)


def to_excel_bytes(df):
    output = io.BytesIO()
    ecols = [c for c in ["순위", "카테고리명", "상품번호", "상품명", "설명", "판매가", "할인가", "할인율", "리뷰수", "품절", "배송유형", "저재고", "상품URL"] if c in df.columns]
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[ecols].to_excel(writer, sheet_name="전체", index=False)
        if "카테고리명" in df.columns and df["카테고리명"].nunique() > 1:
            sm = df.groupby("카테고리명").agg(상품수=("상품번호", "count"), 평균가격=("판매가", "mean"), 할인상품=("할인율", lambda x: (x > 0).sum())).round(0).sort_values("상품수", ascending=False).reset_index()
            sm.to_excel(writer, sheet_name="카테고리별요약", index=False)
    return output.getvalue()


# ============================================================
# 메인
# ============================================================
def main():
    tree = load_category_tree()

    if "result_df" not in st.session_state:
        st.session_state.result_df = None
    if "selected_product_no" not in st.session_state:
        st.session_state.selected_product_no = None

    # 사이드바
    with st.sidebar:
        st.markdown("## 🛒 컬리 신제품 인텔리전스")
        st.markdown("---")

        st.markdown("### 📁 STEP 1. 대분류")
        main_options = {info["name"]: code for code, info in tree.items()}
        selected_main_names = st.multiselect("대분류 카테고리", list(main_options.keys()), [], placeholder="선택하세요")
        selected_main_codes = [main_options[n] for n in selected_main_names]

        st.markdown("### 📂 STEP 2. 하위 카테고리")
        sub_options = {}
        if selected_main_codes:
            for mc in selected_main_codes:
                for sc, sn in tree[mc]["subs"].items():
                    sub_options[f"{tree[mc]['name']} > {sn}"] = sc
        if sub_options:
            select_all = st.checkbox("✅ 하위 전체 선택", value=True, key="chk_all")
            if select_all:
                selected_sub_names = list(sub_options.keys())
            else:
                selected_sub_names = st.multiselect("하위 카테고리", list(sub_options.keys()), [], placeholder="선택", key="ms_sub")
            selected_sub_codes = [sub_options[n] for n in selected_sub_names]
        else:
            selected_sub_codes = []

        st.markdown("---")
        st.markdown("### 🔧 STEP 3. 조건")
        sort_name = st.selectbox("정렬", list(SORT_OPTIONS.keys()), index=0)
        max_n = st.slider("최대 출력", 10, 300, 100, step=10)
        keyword = st.text_input("키워드", placeholder="콤부차,제로,프로틴")
        price_range = st.slider("가격 범위", 0, 100_000, (0, 100_000), step=1000, format="₩%d")
        exclude_soldout = st.checkbox("품절 제외", value=True)

        st.markdown("---")
        run_btn = st.button("🔍 수집 시작", type="primary", use_container_width=True, disabled=len(selected_main_codes) == 0)
        if len(selected_main_codes) == 0:
            st.caption("⬆️ 대분류를 선택하세요")

    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🛒 마켓컬리 신제품 인텔리전스</h1>
        <p>카테고리별 트렌드 분석 · 상품 선택 시 우측에 상세 정보 표시</p>
    </div>""", unsafe_allow_html=True)

    # 수집
    if run_btn:
        targets = []
        if selected_sub_codes:
            for sc in selected_sub_codes:
                nm = sc
                for info in tree.values():
                    if sc in info["subs"]:
                        nm = info["subs"][sc]
                        break
                targets.append((sc, nm))
        else:
            for mc in selected_main_codes:
                targets.append((mc, tree[mc]["name"]))

        if targets:
            sort_code = SORT_OPTIONS[sort_name]
            progress = st.progress(0, text="📡 수집 시작...")
            all_data = []
            for i, (code, name) in enumerate(targets):
                progress.progress((i + 1) / len(targets), text=f"📡 [{i+1}/{len(targets)}] {name}")
                items = fetch_products(code, sort_code, max_n)
                for item in items:
                    item["카테고리명"] = name
                all_data.extend(items)
            progress.empty()

            if all_data:
                df = pd.DataFrame(all_data)
                df = df.drop_duplicates(subset=["상품번호"], keep="first")
                if keyword.strip():
                    kws = [k.strip() for k in keyword.split(",") if k.strip()]
                    df = df[df["상품명"].str.contains("|".join(kws), case=False, na=False)]
                if exclude_soldout:
                    df = df[df["품절"] == "N"]
                pmin, pmax = price_range
                df = df[(df["판매가"] >= pmin) & (df["판매가"] <= pmax)]
                df = df.head(max_n).reset_index(drop=True)
                st.session_state.result_df = df
                st.session_state.selected_product_no = None

    # 결과
    df = st.session_state.result_df
    if df is None or len(df) == 0:
        if df is not None and len(df) == 0:
            st.warning("조건에 맞는 상품이 없습니다.")
        else:
            st.markdown("""
            <div style="text-align:center;padding:80px 20px;color:#888;">
                <div style="font-size:48px;margin-bottom:16px;">🛍️</div>
                <div style="font-size:18px;font-weight:600;color:#5B2C6F;">사이드바에서 카테고리 선택 후 수집 시작</div>
                <div style="font-size:13px;margin-top:8px;color:#999;">대분류 → 하위 → 조건 → 🔍 수집 시작</div>
            </div>""", unsafe_allow_html=True)
        return

    total = len(df)
    avg_price = df["판매가"].mean()
    disc_cnt = (df["할인율"] > 0).sum()
    avg_disc = df.loc[df["할인율"] > 0, "할인율"].mean() if disc_cnt > 0 else 0
    low_cnt = (df["저재고"] == "Y").sum()

    render_metric_cards(total, avg_price, disc_cnt, avg_disc, low_cnt)

    # 차트
    cc1, cc2 = st.columns(2)
    with cc1:
        bins = [0, 3000, 5000, 10000, 20000, 30000, 50000, float("inf")]
        labels = ["~3천", "3~5천", "5천~1만", "1~2만", "2~3만", "3~5만", "5만~"]
        df["가격대"] = pd.cut(df["판매가"], bins=bins, labels=labels)
        pd_d = df["가격대"].value_counts().sort_index()
        render_bar_chart("💰 가격대 분포", "st-purple", {str(k): int(v) for k, v in pd_d.items() if v > 0}, "bar-purple", show_pct=True, total=total)
    with cc2:
        if df["카테고리명"].nunique() > 1:
            cd = df["카테고리명"].value_counts().head(10)
            render_bar_chart("📁 카테고리별", "st-blue", {str(k)[:12]: int(v) for k, v in cd.items()}, "bar-blue", label_wide=True)

    st.markdown("---")

    # ============================================================
    # 메인: 상품 목록 (왼쪽 60%) + 상세 패널 (오른쪽 40%)
    # ============================================================
    col_list, col_detail = st.columns([6, 4])

    with col_list:
        st.markdown('<div class="section-title st-purple">📋 상품 목록 — 상품을 선택하면 우측에 상세 표시</div>', unsafe_allow_html=True)

        # 상품 선택 드롭다운
        product_labels = []
        product_nos = []
        for _, row in df.iterrows():
            disc_tag = f" 🔥{row['할인율']}%" if row["할인율"] and row["할인율"] > 0 else ""
            label = f"[{row['순위']}위] {row['상품명'][:28]}{disc_tag}  |  ₩{row['판매가']:,}"
            product_labels.append(label)
            product_nos.append(row["상품번호"])

        current_idx = 0
        if st.session_state.selected_product_no and st.session_state.selected_product_no in product_nos:
            current_idx = product_nos.index(st.session_state.selected_product_no)

        selected_idx = st.selectbox(
            "🔍 상품 선택 → 우측 상세 보기",
            range(len(product_labels)),
            index=current_idx,
            format_func=lambda i: product_labels[i],
            key="prod_sel",
        )
        st.session_state.selected_product_no = product_nos[selected_idx]

        # 테이블
        render_product_table(df)

        st.markdown('<div style="margin-top:8px;font-size:11px;color:#999;">🆕TOP10: 1~10위 | NEW: 1~30위 | 🔥SALE: 할인20%↑ | ⚡임박</div>', unsafe_allow_html=True)

        fname = f"kurly_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        st.download_button("📥 엑셀 다운로드", to_excel_bytes(df), fname,
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")

    with col_detail:
        st.markdown('<div class="section-title st-purple">📦 상품 상세 정보</div>', unsafe_allow_html=True)

        pno = st.session_state.selected_product_no
        if pno:
            with st.spinner("📡 상세 정보 로딩 중..."):
                detail = fetch_product_detail(pno)
            if detail:
                render_detail_panel(detail)
                st.markdown(
                    f'<div style="text-align:center;margin-top:14px;">'
                    f'<a href="https://www.kurly.com/goods/{pno}" target="_blank" '
                    f'style="display:inline-block;padding:10px 28px;background:linear-gradient(135deg,#5B2C6F,#8E44AD);'
                    f'color:white;border-radius:10px;text-decoration:none;font-weight:700;font-size:13px;'
                    f'box-shadow:0 3px 10px rgba(142,68,173,0.3);">🔗 컬리에서 보기</a></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<div class="detail-panel"><div class="detail-placeholder"><div class="icon">⚠️</div><div>상세 정보를 불러올 수 없습니다</div></div></div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="detail-panel">
                <div class="detail-placeholder">
                    <div class="icon">👆</div>
                    <div style="font-size:14px;font-weight:600;color:#8E44AD;">상품을 선택하세요</div>
                    <div style="font-size:12px;margin-top:6px;color:#bbb;">왼쪽에서 상품을 선택하면<br>여기에 상세 정보가 표시됩니다</div>
                </div>
            </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
