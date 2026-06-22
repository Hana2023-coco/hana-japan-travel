import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime
from pathlib import Path
import base64
import json
from html import escape
import shutil

st.set_page_config(
    page_title="Hana Japan Summer Trip",
    page_icon="🍀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# 기본 경로
# -----------------------------
BASE_DIR = Path(__file__).parent
FONT_PATH = BASE_DIR / "font" / "font1.TTF"
IMAGE_DIR = BASE_DIR / "images"
ATTACH_DIR = BASE_DIR / "attachments"
DATA_DIR = BASE_DIR / "data"

IMAGE_DIR.mkdir(exist_ok=True)
ATTACH_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

METRO_MAP = IMAGE_DIR / "metro.png"
DATA_FILE = DATA_DIR / "trip_data.json"

TRIP_START = date(2026, 7, 8)
TRIP_END = date(2026, 7, 12)
D_DAY = (TRIP_START - date.today()).days


# -----------------------------
# 폰트
# -----------------------------
def make_font_css():
    if FONT_PATH.exists():
        with open(FONT_PATH, "rb") as f:
            font_base64 = base64.b64encode(f.read()).decode()
        return f"""
        @font-face {{
            font-family: 'CuteFont';
            src: url(data:font/ttf;base64,{font_base64}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        """
    return """
    @font-face {
        font-family: 'CuteFont';
        src: local('온글잎 공부잘하자나');
    }
    """


FONT_CSS = make_font_css()


# -----------------------------
# 기본 데이터
# -----------------------------
DEFAULT_EVENTS = {
    "7/8": [
        "04:20 집에서 출발",
        "04:55~06:10 미사역 공항버스",
        "08:10 김포 → 10:00 간사이",
        "JR 하루카 → 신오사카",
        "렘 신오사카 체크인",
        "저녁: 트친이랑 이자카야 후보 중 한 곳"
    ],
    "7/9": [
        "신오사카 → 교토 이동",
        "오카자키 신사 방문 🐇",
        "아라시야마 산책 🎋",
        "교토 카페 / 관광",
        "교토 → 신오사카 복귀"
    ],
    "7/10": [
        "렘 신오사카 체크아웃",
        "신오사카 → 도쿄 신칸센",
        "도쿄 10시쯤 도착 예정",
        "렘 롯폰기 체크인",
        "롯폰기 / 도쿄타워 야경"
    ],
    "7/11": [
        "12:30 낮공 입장 / 13:30 시작",
        "17:00 밤공 입장 / 18:00 시작",
        "Keio Arena TOKYO"
    ],
    "7/12": [
        "렘 롯폰기 체크아웃",
        "12:00 낮공 입장 / 13:00 시작",
        "16:30 밤공 입장 / 17:30 시작",
        "20:05 하네다 → 22:25 김포"
    ],
}

DEFAULT_ROUTES = {
    "7/8": [
        ("집 → 김포공항", "미사역 공항버스 이용", "04:55~06:10 / 여유 있게 04:20 출발"),
        ("김포 → 간사이", "제주항공 7C1325", "08:10 출발 / 10:00 도착"),
        ("간사이공항 → 신오사카", "JR 하루카 E-ticket", "간사이공항역 → 신오사카역"),
        ("렘 신오사카 → 이자카야 후보", "전철/도보", "트친과 저녁 약속")
    ],
    "7/9": [
        ("신오사카 → 교토", "JR 교토선 또는 신칸센", "교토 당일치기 시작"),
        ("교토역 → 오카자키 신사", "버스 또는 지하철+도보", "토끼 오마모리 보기 🐇"),
        ("오카자키 신사 → 아라시야마", "버스/지하철+JR 환승", "대나무숲·카페·산책 🎋"),
        ("아라시야마 → 신오사카", "JR 이용", "늦지 않게 복귀")
    ],
    "7/10": [
        ("렘 신오사카 → 신오사카역", "도보", "체크아웃 후 이동"),
        ("신오사카 → 도쿄", "신칸센", "도쿄 10시쯤 도착 목표"),
        ("도쿄역 → 렘 롯폰기", "전철/지하철", "체크인 전 짐 보관 가능성 확인")
    ],
    "7/11": [
        ("렘 롯폰기 → Keio Arena TOKYO", "지하철+전철", "낮공/밤공 입장 시간 확인"),
        ("공연장 → 숙소", "전철 또는 택시", "밤공 후 늦은 시간 안전 귀가")
    ],
    "7/12": [
        ("렘 롯폰기 → Keio Arena TOKYO", "전철 이동", "체크아웃 후 짐 보관 확인"),
        ("Keio Arena → 하네다공항", "전철/공항선", "공연 후 바로 공항 이동"),
        ("하네다 → 김포", "아시아나 OZ1035", "20:05 출발 / 22:25 도착")
    ],
}

DEFAULT_CHECKLIST = pd.DataFrame({
    "구분": ["필수", "필수", "필수", "필수", "전자기기", "전자기기", "짐", "짐", "공연", "교통"],
    "준비물": ["여권", "항공권 E-ticket", "호텔 바우처", "JR 하루카 E-ticket", "핸드폰", "보조배터리", "엔화", "이심 QR", "응원봉", "신칸센 티켓"],
    "완료": [False] * 10
})

DEFAULT_EXPENSES = pd.DataFrame({
    "날짜": ["7/8", "7/10", "7/9", "7/9", "7/11", "7/12"],
    "분류": ["항공권", "숙소", "교통", "식비", "공연", "교통"],
    "내용": ["왕복 항공권", "렘 롯폰기", "하루카/교토 이동", "교토 카페", "공연 당일 지출", "하네다 이동"],
    "엔화": [0, 0, 3500, 4650, 0, 0],
    "원화": [391615, 314699, 0, 0, 0, 0],
    "환율": [0, 0, 9.7, 9.7, 9.7, 9.7],
    "결제수단": ["카드", "카드", "카드", "현금", "기타", "카드"],
    "정산": ["완료", "완료", "예정", "예정", "예정", "예정"],
    "누가냄": ["박하나", "박하나", "박하나", "박하나", "박하나", "박하나"],
    "메모": ["제주항공+아시아나", "2박", "하루카/교통비", "교토 카페", "굿즈/식비 기록", "공항 이동"]
})

DEFAULT_INFO = {
    "항공권": """출국: 제주항공 7C1325
2026.07.08 08:10 김포 → 10:00 간사이 T2
위탁수하물 불포함

귀국: 아시아나 OZ1035
2026.07.12 20:05 하네다 T3 → 22:25 김포
기내식 포함

항공권 가격: 391,615원""",
    "교통": """JR 하루카: 간사이공항 → 신오사카
예약번호: WJP814655

오사카 지하철 핵심:
신오사카 M13 / 우메다 M16 / 혼마치 M18 / 난바 M20
미도스지선은 오사카 이동 핵심 노선

신칸센 예정:
2026.07.10 신오사카 → 도쿄
도쿄 10시쯤 도착 예정""",
    "숙소": """오사카: 렘 신오사카
7/8 체크인 → 7/10 체크아웃

도쿄: 렘 롯폰기
7/10 체크인 → 7/12 체크아웃
결제금액: 314,699원

요청사항:
가능하면 고층 / 도쿄타워 또는 야경이 보이는 객실""",
    "공연": """NCT WISH FANMEETING
장소: Keio Arena TOKYO

7/11 낮공 13:30 / 밤공 18:00
7/12 낮공 13:00 / 밤공 17:30

준비:
AnyPass / 신분증 / 응원봉 / 보조배터리"""
}

DEFAULT_PLACES = pd.DataFrame({
    "구분": [
        "이자카야", "이자카야", "쇼핑", "쇼핑", "쇼핑", "쇼핑", "카페", "카페", "관광", "관광"
    ],
    "지역": [
        "오사카", "오사카", "오사카/도쿄", "도쿄", "오사카/도쿄", "오사카/도쿄", "교토", "도쿄", "교토", "교토"
    ],
    "장소명": [
        "Yakitori & Gyoza Nonotori Umemido",
        "우메다 도야마 신장 : 육즙 만두 이자카야",
        "다이소",
        "키디랜드",
        "문구용품 가게",
        "드럭스토어",
        "예쁜 카페 후보",
        "예쁜 카페 후보",
        "오카자키 신사",
        "아라시야마"
    ],
    "우선순위": ["높음", "높음", "보통", "높음", "높음", "보통", "높음", "보통", "높음", "높음"],
    "방문예정": ["7/8", "7/8", "여유시간", "도쿄", "여유시간", "여유시간", "7/9", "도쿄", "7/9", "7/9"],
    "링크": [
        "maps.app.goo.gl",
        "maps.app.goo.gl",
        "https://www.google.com/maps/search/DAISO+Osaka",
        "https://www.google.com/maps/search/Kiddy+Land+Tokyo",
        "https://www.google.com/maps/search/stationery+store+Japan",
        "https://www.google.com/maps/search/drugstore+Japan",
        "https://www.google.com/maps/search/Kyoto+cafe",
        "https://www.google.com/maps/search/Tokyo+cafe",
        "https://www.google.com/maps/search/Okazaki+Shrine+Kyoto",
        "https://www.google.com/maps/search/Arashiyama+Kyoto"
    ],
    "메모": [
        "7/8 저녁 트친과 후보 1",
        "7/8 저녁 트친과 후보 2",
        "기념품/소품",
        "캐릭터 굿즈",
        "스티커·펜·다이어리",
        "화장품/상비약",
        "청량한 여름 감성",
        "롯폰기/신주쿠 근처",
        "토끼 오마모리",
        "대나무숲/산책"
    ]
})

DEFAULT_FX = pd.DataFrame({
    "날짜": ["7/8", "7/9", "7/10", "7/11", "7/12"],
    "환율": [9.70, 9.70, 9.70, 9.70, 9.70],
    "메모": ["직접 수정", "직접 수정", "직접 수정", "직접 수정", "직접 수정"]
})

DEFAULT_TODOS = pd.DataFrame({
    "날짜": ["출국 전", "출국 전", "7/8", "7/10", "7/12"],
    "할일": ["신칸센 예매", "도쿄 숙소 요청 메일 확인", "하루카 교환", "도쿄 이동 전 짐 정리", "공연 후 공항 이동 시간 확인"],
    "완료": [False, False, False, False, False],
})

DEFAULT_ATTACHMENTS = pd.DataFrame({
    "구분": [],
    "파일명": [],
    "저장경로": [],
    "메모": [],
})


# -----------------------------
# 저장/불러오기
# -----------------------------
def df_to_records(df):
    return df.fillna("").to_dict(orient="records")


def records_to_df(records, default_df):
    if not records:
        return default_df.copy()
    df = pd.DataFrame(records)
    for col in default_df.columns:
        if col not in df.columns:
            df[col] = default_df[col].iloc[0] if len(default_df) else ""
    return df[default_df.columns]


def get_state_data():
    return {
        "events": st.session_state.events,
        "routes": {k: [list(x) for x in v] for k, v in st.session_state.routes.items()},
        "checklist": df_to_records(st.session_state.checklist),
        "expenses": df_to_records(st.session_state.expenses),
        "info": st.session_state.info,
        "memo": st.session_state.memo,
        "places": df_to_records(st.session_state.places),
        "fx": df_to_records(st.session_state.fx),
        "todos": df_to_records(st.session_state.todos),
        "attachments": df_to_records(st.session_state.attachments),
    }


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(get_state_data(), f, ensure_ascii=False, indent=2)


def load_data():
    if not DATA_FILE.exists():
        return
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    st.session_state.events = data.get("events", {k: v.copy() for k, v in DEFAULT_EVENTS.items()})
    routes = data.get("routes", DEFAULT_ROUTES)
    st.session_state.routes = {k: [tuple(x) for x in v] for k, v in routes.items()}
    st.session_state.checklist = records_to_df(data.get("checklist", []), DEFAULT_CHECKLIST)
    st.session_state.expenses = records_to_df(data.get("expenses", []), DEFAULT_EXPENSES)
    st.session_state.info = data.get("info", DEFAULT_INFO.copy())
    st.session_state.memo = data.get("memo", "")
    st.session_state.places = records_to_df(data.get("places", []), DEFAULT_PLACES)
    st.session_state.fx = records_to_df(data.get("fx", []), DEFAULT_FX)
    st.session_state.todos = records_to_df(data.get("todos", []), DEFAULT_TODOS)
    st.session_state.attachments = records_to_df(data.get("attachments", []), DEFAULT_ATTACHMENTS)


def init_state():
    if "loaded_once" not in st.session_state:
        st.session_state.loaded_once = True
        load_data()

    if "events" not in st.session_state:
        st.session_state.events = {k: v.copy() for k, v in DEFAULT_EVENTS.items()}
    if "routes" not in st.session_state:
        st.session_state.routes = {k: v.copy() for k, v in DEFAULT_ROUTES.items()}
    if "checklist" not in st.session_state:
        st.session_state.checklist = DEFAULT_CHECKLIST.copy()
    if "expenses" not in st.session_state:
        st.session_state.expenses = DEFAULT_EXPENSES.copy()
    if "info" not in st.session_state:
        st.session_state.info = DEFAULT_INFO.copy()
    if "memo" not in st.session_state:
        st.session_state.memo = ""
    if "places" not in st.session_state:
        st.session_state.places = DEFAULT_PLACES.copy()
    if "fx" not in st.session_state:
        st.session_state.fx = DEFAULT_FX.copy()
    if "todos" not in st.session_state:
        st.session_state.todos = DEFAULT_TODOS.copy()
    if "attachments" not in st.session_state:
        st.session_state.attachments = DEFAULT_ATTACHMENTS.copy()


init_state()


# -----------------------------
# 계산 보조
# -----------------------------
def calc_krw_from_expenses(df):
    if df.empty:
        return df
    df = df.copy()
    for col in ["엔화", "원화", "환율"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["환산원화"] = df.apply(
        lambda r: int(r["원화"]) if r["원화"] > 0 else int(round(r["엔화"] * r["환율"])),
        axis=1
    )
    return df


def apply_fx_by_date(expenses, fx):
    exp = expenses.copy()
    fx_map = dict(zip(fx["날짜"].astype(str), pd.to_numeric(fx["환율"], errors="coerce").fillna(0)))
    if "환율" not in exp.columns:
        exp["환율"] = 0
    exp["환율"] = exp.apply(lambda r: fx_map.get(str(r.get("날짜", "")), r.get("환율", 0)), axis=1)
    return exp


# -----------------------------
# CSS
# -----------------------------
st.markdown(f"""
<style>
{FONT_CSS}

* {{
    font-family: 'CuteFont', 'Malgun Gothic', sans-serif !important;
    box-sizing: border-box;
}}

html, body, [class*="css"], .stApp, .stMarkdown, .stButton, .stTextInput, .stSelectbox, .stRadio, button {{
    font-family: 'CuteFont', 'Malgun Gothic', sans-serif !important;
}}

html, body, .stApp {{
    font-size: 18px;
}}

.stApp {{
    background:
        radial-gradient(circle at 8% 8%, rgba(210,231,183,0.28), transparent 20%),
        radial-gradient(circle at 92% 8%, rgba(238,248,225,0.50), transparent 22%),
        linear-gradient(180deg, #fbfaf3 0%, #ffffff 48%, #f6fbef 100%);
    color: #2f3a2f;
}}

/* Streamlit 기본 헤더/사이드바 아이콘 문제 방지 */
header[data-testid="stHeader"] {{
    background: rgba(251,250,243,0.82) !important;
}}
section[data-testid="stSidebar"] {{
    display: none !important;
}}
button[kind="header"] {{
    display: none !important;
}}

.block-container {{
    max-width: 980px;
    padding-top: 1rem;
    padding-bottom: 6.8rem;
    padding-left: 1.1rem;
    padding-right: 1.1rem;
}}

.mobile-topbar {{
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 10px 2px 12px 2px;
    margin-bottom: 4px;
    background: rgba(251,250,243,0.90);
    backdrop-filter: blur(12px);
}}

.mobile-brand {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 22px;
    font-weight: 900;
    color: #2f3a2f;
    white-space: nowrap;
}}

.mobile-icon-btn {{
    width: 36px;
    height: 36px;
    border-radius: 14px;
    border: 1px solid #dfe8cf;
    background: rgba(255,255,255,0.84);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 5px 14px rgba(127,150,94,0.10);
    font-size: 18px;
}}

.nav-select-wrap {{
    padding: 10px 14px 12px 14px;
    margin-bottom: 16px;
    border-radius: 20px;
    background: rgba(255,255,255,0.94);
    border: 1px solid #dfe8cf;
    box-shadow: 0 8px 20px rgba(127,150,94,0.10);
}}

.nav-select-wrap .nav-label {{
    color: #55714e;
    font-size: 14px;
    margin-bottom: 5px;
    font-weight: 900;
}}

.main-hero {{
    position: relative;
    padding: 22px 28px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(247,251,238,0.98));
    border: 1px solid #dfe8cf;
    box-shadow: 0 12px 28px rgba(127,150,94,0.13);
    margin-bottom: 20px;
}}

.main-hero::before {{
    content: "🍀 ✧ 𖧷";
    position: absolute;
    right: 24px;
    top: 16px;
    color: #9bbd7a;
    font-size: 28px;
}}

.main-title {{
    font-size: 42px;
    line-height: 1.08;
    font-weight: 900;
    color: #2f3a2f;
}}

.sub-title {{
    display: inline-block;
    margin-top: 8px;
    padding: 6px 13px;
    background: #ffffff;
    border: 1px dashed #b8cfa2;
    color: #55714e;
    font-size: 17px;
}}

.mood-line {{
    margin-top: 12px;
    font-size: 19px;
    color: #8aa36c;
}}

.card, .place-card {{
    position: relative;
    padding: 18px;
    border-radius: 20px;
    background: rgba(255,255,255,0.94);
    border: 1px solid #dfe8cf;
    box-shadow: 0 8px 20px rgba(127,150,94,0.10);
    margin-bottom: 14px;
}}

.card::after {{
    content: "✦";
    position: absolute;
    right: 18px;
    top: 14px;
    color: #c9dbaa;
}}

.card-soft {{
    padding: 17px;
    border-radius: 18px;
    background: linear-gradient(135deg, #ffffff, #f7fbef);
    border: 1px dashed #b8cfa2;
    margin-bottom: 12px;
}}

.sticker {{
    display: inline-block;
    padding: 5px 13px;
    border-radius: 999px;
    background: #d9eac4;
    color: #3e5b38;
    border: 1px dashed #9fbd84;
    font-weight: 900;
    margin-bottom: 10px;
}}

.memo-strip, .category-pill {{
    display: inline-block;
    background: #ffffff;
    border: 1px solid #e6e0d0;
    box-shadow: 2px 2px 0 rgba(182,196,152,0.25);
    padding: 5px 11px;
    margin: 4px;
    border-radius: 999px;
}}

.big-number {{
    font-size: 30px;
    font-weight: 900;
    color: #3e5b38;
}}

.info-line {{
    padding: 10px 13px;
    margin: 7px 0;
    border-radius: 14px;
    background: rgba(255,255,255,0.88);
    border: 1px solid #dfe8cf;
}}

.route-card {{
    padding: 14px 16px;
    border-radius: 18px;
    background: linear-gradient(135deg, #ffffff, #f8fbef);
    border: 1px solid #dfe8cf;
    box-shadow: 0 6px 14px rgba(127,150,94,0.08);
    margin-bottom: 10px;
}}

.route-arrow {{
    color: #7d9d66;
    font-weight: 900;
    font-size: 22px;
}}

.timeline-box {{
    padding: 13px 16px;
    border-left: 5px solid #b8cfa2;
    background: rgba(255,255,255,0.92);
    border-radius: 16px;
    margin-bottom: 9px;
    box-shadow: 0 6px 14px rgba(127,150,94,0.08);
}}

.expense-row {{
    display: grid;
    grid-template-columns: .7fr 1fr 1.4fr 1fr 1fr 1fr;
    gap: 8px;
    align-items: center;
    padding: 12px 14px;
    margin: 8px 0;
    border-radius: 16px;
    background: rgba(255,255,255,0.94);
    border: 1px solid #dfe8cf;
}}

.expense-head {{
    color: #55714e;
    font-weight: 900;
    background: #f2f8e8;
}}

.settle-done {{ color: #3e7c43; }}
.settle-plan {{ color: #b67b43; }}

.map-note {{
    padding: 14px;
    border-radius: 18px;
    border: 1px dashed #b8cfa2;
    background: rgba(255,255,255,0.9);
    margin-bottom: 12px;
}}

div[data-testid="stMetric"] {{
    background: rgba(255,255,255,0.94);
    padding: 15px;
    border-radius: 18px;
    border: 1px solid #dfe8cf;
    box-shadow: 0 7px 16px rgba(127,150,94,0.10);
}}

.stButton > button {{
    border-radius: 999px;
    background: linear-gradient(90deg, #d9eac4, #f4f8df);
    color: #33452f;
    border: 1px solid #b8cfa2;
    font-weight: 900;
    font-size: 18px !important;
}}

.stTextArea textarea, .stTextInput input {{
    border-radius: 14px;
    border: 1px solid #cbdcb8;
    background: rgba(255,255,255,0.96);
    font-size: 18px !important;
}}

.bottom-tabs {{
    position: fixed;
    left: 50%;
    bottom: 12px;
    transform: translateX(-50%);
    width: min(520px, calc(100% - 24px));
    z-index: 9999;
    padding: 9px 10px 6px 10px;
    border-radius: 26px;
    background: rgba(255,255,255,0.96);
    border: 1px solid #dfe8cf;
    box-shadow: 0 12px 28px rgba(88,105,70,0.18);
    backdrop-filter: blur(12px);
}}

.bottom-tabs-spacer {{
    height: 88px;
}}


.mobile-calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    gap: 7px;
    margin-top: 10px;
}

.mobile-calendar-head {
    text-align: center;
    font-weight: 900;
    color: #55714e;
    font-size: 16px;
    padding: 4px 0;
}

.mobile-day {
    min-height: 74px;
    border-radius: 18px;
    background: rgba(255,255,255,0.94);
    border: 1px solid #dfe8cf;
    box-shadow: 0 5px 12px rgba(127,150,94,0.07);
    padding: 8px 6px;
    overflow: hidden;
}

.mobile-day.blank {
    opacity: 0.38;
}

.mobile-day.trip {
    border: 2px dashed #b8cfa2;
    background: linear-gradient(135deg, #ffffff, #f2f9e8);
}

.mobile-day.concert {
    border: 2px dashed #d9b7c5;
    background: linear-gradient(135deg, #fffafc, #f4f8df);
}

.day-num {
    font-size: 18px;
    font-weight: 900;
    color: #33452f;
    line-height: 1;
}

.day-note {
    margin-top: 5px;
    font-size: 12px;
    line-height: 1.25;
    color: #55714e;
    word-break: keep-all;
}

.day-chip-row {
    display: flex;
    gap: 7px;
    overflow-x: auto;
    padding: 4px 0 12px 0;
    margin-bottom: 6px;
}

.day-chip {
    white-space: nowrap;
    border-radius: 999px;
    padding: 7px 12px;
    background: #ffffff;
    border: 1px solid #dfe8cf;
    color: #55714e;
    font-weight: 900;
    box-shadow: 0 4px 10px rgba(127,150,94,0.08);
}

.day-chip.active {
    background: #3e7c43;
    color: white;
}

.more-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin-top: 8px;
}

.more-card {
    padding: 16px;
    min-height: 92px;
    border-radius: 20px;
    background: rgba(255,255,255,0.94);
    border: 1px solid #dfe8cf;
    box-shadow: 0 8px 20px rgba(127,150,94,0.10);
}

.more-title {
    font-size: 18px;
    font-weight: 900;
    color: #2f3a2f;
}

.more-desc {
    margin-top: 5px;
    font-size: 14px;
    color: #7d9d66;
}

.bottom-tabs button {
    min-height: 54px !important;
    padding: 5px 4px !important;
    font-size: 13px !important;
    line-height: 1.15 !important;
    border-radius: 18px !important;
}


h1 {{ font-size: 32px !important; }}
h2 {{ font-size: 28px !important; }}
h3 {{ font-size: 24px !important; }}
p, label {{ font-size: 18px !important; }}

@media (max-width: 768px) {{
    .block-container {{
        max-width: 100% !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
        padding-top: 0.55rem !important;
        padding-bottom: 6.4rem !important;
    }}

    .mobile-topbar {{
        padding-top: 8px;
    }}

    .mobile-brand {{
        font-size: 19px;
    }}

    .main-hero {{
        padding: 16px 18px !important;
        border-radius: 20px !important;
        margin-bottom: 14px !important;
    }}

    .main-hero::before {{
        right: 14px !important;
        top: 12px !important;
        font-size: 18px !important;
    }}

    .main-title {{
        font-size: 27px !important;
        line-height: 1.08 !important;
        padding-right: 36px !important;
    }}

    .sub-title {{
        font-size: 14px !important;
        padding: 5px 9px !important;
        line-height: 1.35 !important;
    }}

    .mood-line {{
        font-size: 15px !important;
        line-height: 1.45 !important;
    }}

    h1 {{ font-size: 24px !important; }}
    h2 {{ font-size: 20px !important; }}
    h3 {{ font-size: 18px !important; }}
    p, label {{ font-size: 15px !important; }}

    .card, .place-card, .card-soft, .route-card, .timeline-box {{
        padding: 14px !important;
        border-radius: 16px !important;
    }}

    .big-number {{
        font-size: 22px !important;
    }}

    .sticker, .memo-strip, .category-pill {{
        font-size: 14px !important;
        padding: 4px 9px !important;
    }}

    .expense-row {{
        grid-template-columns: 1fr !important;
        gap: 4px !important;
        font-size: 14px !important;
    }}
    .bottom-tabs {{
        bottom: 8px;
        width: calc(100% - 16px);
    }}
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 공통 렌더 함수
# -----------------------------
def render_header():
    st.markdown("""
    <div class="main-hero">
      <div class="main-title">🍀 Hana’s Japan Summer Trip</div>
      <div class="sub-title">2026.07.08 ~ 2026.07.12 · Osaka · Kyoto · Tokyo</div>
      <div class="mood-line">오늘은 너랑 럭키한 하루로 해줘 · 교토의 토끼와 초록 여름 기록 🐇</div>
    </div>
    """, unsafe_allow_html=True)


def render_info_page(title, key_name, emoji, summary_items):
    st.header(f"{emoji} {title}")

    cols = st.columns(len(summary_items))
    for col, item in zip(cols, summary_items):
        with col:
            st.markdown(f"""
            <div class="card-soft">
                <div class="sticker">{item["label"]}</div>
                <div class="big-number">{item["value"]}</div>
                <p>{item["desc"]}</p>
            </div>
            """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.05, 1])

    with col1:
        st.markdown("""
        <div class="card">
            <div class="sticker">PREVIEW</div>
            <h3>저장된 정보</h3>
        </div>
        """, unsafe_allow_html=True)

        lines = [line for line in st.session_state.info[key_name].split("\n") if line.strip()]
        for line in lines:
            st.markdown(f'<div class="info-line">{escape(line)}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="sticker">EDIT</div>
            <h3>내용 수정하기</h3>
            <p>예약번호, 시간, 메모를 자유롭게 바꿀 수 있어요.</p>
        </div>
        """, unsafe_allow_html=True)

        edited_info = st.text_area(
            "내용을 자유롭게 수정할 수 있어",
            value=st.session_state.info[key_name],
            height=300
        )

        if st.button(f"{emoji} {title} 저장"):
            st.session_state.info[key_name] = edited_info
            save_data()
            st.success("저장 완료!")


def render_route_cards(day_key):
    for start, method, memo in st.session_state.routes.get(day_key, []):
        st.markdown(f"""
        <div class="route-card">
            <div class="sticker">{escape(day_key)}</div>
            <h3>{escape(start)}</h3>
            <div class="route-arrow">➜ {escape(method)}</div>
            <p>{escape(memo)}</p>
        </div>
        """, unsafe_allow_html=True)


def expense_preview(df):
    df = calc_krw_from_expenses(df)
    st.markdown("""
    <div class="expense-row expense-head">
        <div>날짜</div><div>분류</div><div>내용</div><div>엔화</div><div>환산원화</div><div>정산</div>
    </div>
    """, unsafe_allow_html=True)

    for _, row in df.iterrows():
        settle_class = "settle-done" if str(row.get("정산", "")) == "완료" else "settle-plan"
        st.markdown(f"""
        <div class="expense-row">
            <div>{escape(str(row.get("날짜", "")))}</div>
            <div><span class="category-pill">{escape(str(row.get("분류", "")))}</span></div>
            <div>{escape(str(row.get("내용", "")))}</div>
            <div>¥{int(row.get("엔화", 0)):,}</div>
            <div>{int(row.get("환산원화", 0)):,}원</div>
            <div class="{settle_class}">{escape(str(row.get("정산", "")))}</div>
        </div>
        """, unsafe_allow_html=True)


def render_place_cards(df):
    if df.empty:
        st.info("등록된 장소가 없어.")
        return

    for _, row in df.iterrows():
        link = str(row.get("링크", "")).strip()
        link_html = f'<a href="{escape(link)}" target="_blank">지도 열기</a>' if link else ''
        st.markdown(f"""
        <div class="place-card">
            <div class="sticker">{escape(str(row.get("구분", "")))} · {escape(str(row.get("지역", "")))}</div>
            <h3>{escape(str(row.get("장소명", "")))}</h3>
            <span class="memo-strip">우선순위 {escape(str(row.get("우선순위", "")))}</span>
            <span class="memo-strip">방문 {escape(str(row.get("방문예정", "")))}</span>
            <p>{escape(str(row.get("메모", "")))}</p>
            {link_html}
        </div>
        """, unsafe_allow_html=True)


MENU_ITEMS = [
    "🏠 대시보드",
    "📅 7월 달력",
    "🗓️ 상세 일정",
    "🗺️ 이동방법",
    "💴 여행 가계부",
    "⋯ 더보기",
    "📍 가고싶은 곳",
    "✈️ 항공권",
    "🚄 교통",
    "🏨 숙소",
    "🎤 공연",
    "✅ 준비물",
    "📎 파일 보관함",
    "📝 메모",
    "💾 저장/초기화",
]

BOTTOM_ITEMS = [
    ("🏠", "홈", "🏠 대시보드"),
    ("📅", "일정", "📅 7월 달력"),
    ("🗓️", "상세", "🗓️ 상세 일정"),
    ("💴", "가계부", "💴 여행 가계부"),
    ("⋯", "더보기", "⋯ 더보기"),
]

if "menu" not in st.session_state or st.session_state.menu not in MENU_ITEMS:
    st.session_state.menu = "🏠 대시보드"


def set_menu(target):
    st.session_state.menu = target
    st.rerun()


def render_app_topbar():
    st.markdown("""
    <div class="mobile-topbar">
        <div class="mobile-icon-btn">☰</div>
        <div class="mobile-brand">🍀 Hana’s Japan Summer Trip</div>
        <div class="mobile-icon-btn">🌸</div>
    </div>
    """, unsafe_allow_html=True)


def render_bottom_tabs():
    st.markdown('<div class="bottom-tabs">', unsafe_allow_html=True)
    cols = st.columns(len(BOTTOM_ITEMS))
    for col, (icon, label, target) in zip(cols, BOTTOM_ITEMS):
        with col:
            active = st.session_state.menu == target
            button_label = f"{icon}\n{label}" if not active else f"● {icon}\n{label}"
            if st.button(button_label, key=f"bottom_{target}", use_container_width=True):
                set_menu(target)
    st.markdown('</div><div class="bottom-tabs-spacer"></div>', unsafe_allow_html=True)


render_app_topbar()
render_header()
menu = st.session_state.menu

# -----------------------------
# 메뉴별 화면
# -----------------------------
if menu == "🏠 대시보드":
    today_key = f"{date.today().month}/{date.today().day}"
    completed = st.session_state.checklist["완료"].sum()
    checklist_total = len(st.session_state.checklist)
    progress = completed / checklist_total if checklist_total else 0

    exp_calc = calc_krw_from_expenses(st.session_state.expenses)
    expense_total = int(exp_calc["환산원화"].sum()) if len(exp_calc) else 0

    todo_total = len(st.session_state.todos)
    todo_done = int(st.session_state.todos["완료"].sum()) if todo_total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("여행 기간", "4박 5일")
    c2.metric("루트", "오사카 → 교토 → 도쿄")
    c3.metric("D-Day", f"D-{D_DAY}" if D_DAY > 0 else "여행 시작")
    c4.metric("기록 경비", f"{expense_total:,}원")

    col1, col2 = st.columns([1.25, 1])

    with col1:
        st.markdown("""
        <div class="card">
          <div class="sticker">TODAY FOCUS</div>
          <h3>오늘 확인할 것</h3>
          <p>출국 전에는 준비물과 예약, 여행 중에는 오늘 일정 중심으로 확인해요.</p>
        </div>
        """, unsafe_allow_html=True)

        show_day = today_key if today_key in st.session_state.events else "7/8"
        st.markdown(f'<span class="memo-strip">추천 확인 날짜: {show_day}</span>', unsafe_allow_html=True)
        for item in st.session_state.events.get(show_day, []):
            st.markdown(f'<div class="timeline-box">{escape(item)}</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
          <div class="sticker">LUCKY PLAN</div>
          <h3>이번 여행 무드</h3>
          <p>초록 클로버, 작은 별, 흰 종이 위 손그림처럼 오사카 · 교토 · 도쿄의 여름을 기록하기 🍀</p>
          <span class="memo-strip">오카자키 신사 🐇</span>
          <span class="memo-strip">아라시야마 🎋</span>
          <span class="memo-strip">이자카야 🍻</span>
          <span class="memo-strip">도쿄 야경</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
          <div class="sticker">CHECK LIST</div>
          <h3>준비 진행률</h3>
          <p>하나씩 챙기면 럭키한 여행 완성 🍀</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress)
        st.write(f"{completed}/{checklist_total}개 완료")

        todo_progress = todo_done / todo_total if todo_total else 0
        st.markdown(f"""
        <div class="card">
          <div class="sticker">TO-DO</div>
          <h3>할 일 진행률</h3>
          <div class="big-number">{todo_done}/{todo_total}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(todo_progress)

        st.markdown(f"""
        <div class="card">
          <div class="sticker">BUDGET</div>
          <h3>현재 기록된 경비</h3>
          <div class="big-number">{expense_total:,}원</div>
          <p>엔화는 날짜별 환율로 원화 환산</p>
        </div>
        """, unsafe_allow_html=True)


elif menu == "📅 7월 달력":
    st.header("📅 2026년 7월 전체 달력")

    day_summaries = {
        8: "출국 · 간사이",
        9: "교토 🐇",
        10: "도쿄 이동",
        11: "공연 🎤",
        12: "공연·귀국"
    }

    st.markdown("""
    <div class="card">
        <div class="sticker">JULY PLAN</div>
        <h3>여행 날짜 한눈에 보기</h3>
        <p>7/8~7/12 일정만 크게 표시해서 모바일에서 보기 편하게 정리했어.</p>
    </div>
    """, unsafe_allow_html=True)

    cells = []
    cells.extend([""] * 3)  # 2026년 7월 1일은 수요일
    cells.extend(list(range(1, 32)))
    while len(cells) % 7 != 0:
        cells.append("")

    html = """
    <div class="mobile-calendar-grid">
        <div class="mobile-calendar-head">일</div>
        <div class="mobile-calendar-head">월</div>
        <div class="mobile-calendar-head">화</div>
        <div class="mobile-calendar-head">수</div>
        <div class="mobile-calendar-head">목</div>
        <div class="mobile-calendar-head">금</div>
        <div class="mobile-calendar-head">토</div>
    """

    for d in cells:
        if d == "":
            html += '<div class="mobile-day blank"></div>'
            continue

        cls = "mobile-day"
        if d in [8, 9, 10]:
            cls += " trip"
        if d in [11, 12]:
            cls += " concert"

        note = day_summaries.get(d, "")
        html += f"""
        <div class="{cls}">
            <div class="day-num">{d}</div>
            <div class="day-note">{escape(note)}</div>
        </div>
        """

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("### 🍀 날짜별 일정")
    for day_key in ["7/8", "7/9", "7/10", "7/11", "7/12"]:
        first_item = st.session_state.events.get(day_key, [""])[0]
        st.markdown(f"""
        <div class="timeline-box">
            <span class="memo-strip">{day_key}</span><br>
            <b>{escape(first_item)}</b>
        </div>
        """, unsafe_allow_html=True)


elif menu == "🗓️ 상세 일정":
    st.header("🗓️ 상세 일정 수정")

    selected_day = st.selectbox(
        "날짜 선택",
        ["7/8", "7/9", "7/10", "7/11", "7/12"],
        label_visibility="collapsed"
    )

    day_titles = {
        "7/8": "✈️ 출국 · 오사카 도착",
        "7/9": "🐇 교토 · 아라시야마 당일치기",
        "7/10": "🚄 도쿄 이동",
        "7/11": "🎤 공연 Day 1",
        "7/12": "🎤 공연 Day 2 · 귀국"
    }

    col1, col2 = st.columns([1, 1.15])

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="sticker">{selected_day}</div>
            <h2>{day_titles[selected_day]}</h2>
            <p style="color:#7b9464;">오늘의 일정 미리보기 🍀</p>
        </div>
        """, unsafe_allow_html=True)

        for idx, item in enumerate(st.session_state.events[selected_day], start=1):
            st.markdown(f"""
            <div class="timeline-box">
                <span class="memo-strip">STEP {idx}</span><br>
                {escape(item)}
            </div>
            """, unsafe_allow_html=True)

        st.subheader("🗺️ 이날의 이동방법")
        render_route_cards(selected_day)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="sticker">EDIT NOTE</div>
            <h3>일정 수정하기</h3>
            <p>한 줄에 하나씩 적으면 달력에도 같이 반영돼요 ✍️</p>
        </div>
        """, unsafe_allow_html=True)

        edited = st.text_area(
            "일정 입력",
            value="\n".join(st.session_state.events[selected_day]),
            height=230
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🍀 일정 저장"):
                st.session_state.events[selected_day] = [
                    line.strip() for line in edited.split("\n") if line.strip()
                ]
                save_data()
                st.success("저장 완료! 달력에도 반영돼.")

        with b2:
            if st.button("↩ 기본 일정으로 되돌리기"):
                st.session_state.events[selected_day] = DEFAULT_EVENTS[selected_day].copy()
                save_data()
                st.warning("기본 일정으로 되돌렸어.")


elif menu == "🗺️ 이동방법":
    st.header("🗺️ 일정별 가는 방법")

    st.markdown("""
    <div class="card">
        <div class="sticker">METRO MAP</div>
        <h3>도쿄 · 오사카 지하철 노선도</h3>
        <p>공연장, 하네다공항, 교토·아라시야마, 간사이공항 이동 참고용 노선도예요.</p>
    </div>
    """, unsafe_allow_html=True)

    if METRO_MAP.exists():
        st.image(str(METRO_MAP), caption="도쿄 · 오사카 지하철 노선도", use_container_width=True)
    else:
        st.info("images/metro.png 파일을 넣으면 노선도가 표시돼.")

    day = st.selectbox("이동방법 날짜 선택", ["7/8", "7/9", "7/10", "7/11", "7/12"])
    render_route_cards(day)

    st.markdown("""
    <div class="card">
        <div class="sticker">OSAKA METRO NOTE</div>
        <h3>오사카 지하철 노선 메모</h3>
        <p>신오사카는 미도스지선 M13, 우메다는 M16, 난바는 M20. 오사카 시내 이동은 미도스지선을 중심으로 보면 편해요.</p>
        <span class="memo-strip">신오사카 M13</span>
        <span class="memo-strip">우메다 M16</span>
        <span class="memo-strip">혼마치 M18</span>
        <span class="memo-strip">난바 M20</span>
    </div>
    """, unsafe_allow_html=True)

    route_text = "\n".join([f"{a} | {b} | {c}" for a, b, c in st.session_state.routes[day]])
    edited_routes = st.text_area(
        "이동방법 수정하기 / 형식: 출발-도착 | 이용수단 | 메모",
        value=route_text,
        height=230
    )

    if st.button("🗺️ 이동방법 저장"):
        new_routes = []
        for line in edited_routes.split("\n"):
            parts = [x.strip() for x in line.split("|")]
            if len(parts) == 3:
                new_routes.append((parts[0], parts[1], parts[2]))
        if new_routes:
            st.session_state.routes[day] = new_routes
            save_data()
            st.success("이동방법 저장 완료!")
        else:
            st.warning("형식에 맞게 입력해줘. 예: 신오사카 → 교토 | JR 교토선 | 약 30분")


elif menu == "⋯ 더보기":
    st.header("⋯ 더보기")

    st.markdown("""
    <div class="card">
        <div class="sticker">MORE MENU</div>
        <h3>필요한 메뉴를 골라서 열기</h3>
        <p>하단 탭에는 자주 쓰는 메뉴만 두고, 나머지는 여기에서 빠르게 이동해.</p>
    </div>
    """, unsafe_allow_html=True)

    more_items = [
        ("📍 가고싶은 곳", "쇼핑·카페·관광 후보"),
        ("✈️ 항공권", "출국/귀국 항공편"),
        ("🚄 교통", "하루카·신칸센 메모"),
        ("🏨 숙소", "렘 신오사카·롯폰기"),
        ("🎤 공연", "Keio Arena 일정"),
        ("✅ 준비물", "여권·티켓·응원봉"),
        ("📎 파일 보관함", "바우처·영수증"),
        ("📝 메모", "자유 메모/할 일"),
        ("💾 저장/초기화", "데이터 저장 관리"),
    ]

    for i in range(0, len(more_items), 2):
        cols = st.columns(2)
        for col, (target, desc) in zip(cols, more_items[i:i+2]):
            with col:
                if st.button(f"{target}\\n{desc}", key=f"more_{target}", use_container_width=True):
                    set_menu(target)


elif menu == "📍 가고싶은 곳":
    st.header("📍 가고 싶은 곳 / 장소 카드")

    tab1, tab2 = st.tabs(["장소 카드", "장소 수정"])

    with tab1:
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            category = st.selectbox("구분 필터", ["전체"] + sorted(st.session_state.places["구분"].dropna().unique().tolist()))
        with filter_col2:
            area = st.selectbox("지역 필터", ["전체"] + sorted(st.session_state.places["지역"].dropna().unique().tolist()))

        place_df = st.session_state.places.copy()
        if category != "전체":
            place_df = place_df[place_df["구분"] == category]
        if area != "전체":
            place_df = place_df[place_df["지역"] == area]

        render_place_cards(place_df)

    with tab2:
        edited_places = st.data_editor(
            st.session_state.places,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "구분": st.column_config.SelectboxColumn(
                    "구분",
                    options=["이자카야", "쇼핑", "카페", "관광", "맛집", "기타"]
                ),
                "우선순위": st.column_config.SelectboxColumn(
                    "우선순위",
                    options=["높음", "보통", "낮음"]
                )
            }
        )
        if st.button("📍 장소 저장"):
            st.session_state.places = edited_places
            save_data()
            st.success("장소 리스트 저장 완료!")


elif menu == "✈️ 항공권":
    render_info_page(
        "항공권",
        "항공권",
        "✈️",
        [
            {"label": "GO", "value": "7C1325", "desc": "김포 → 간사이"},
            {"label": "BACK", "value": "OZ1035", "desc": "하네다 → 김포"},
            {"label": "PRICE", "value": "391,615원", "desc": "왕복 항공권"}
        ]
    )


elif menu == "🚄 교통":
    render_info_page(
        "교통",
        "교통",
        "🚄",
        [
            {"label": "HARUKA", "value": "간사이 → 신오사카", "desc": "JR 하루카"},
            {"label": "SHINKANSEN", "value": "신오사카 → 도쿄", "desc": "7/10 예정"},
            {"label": "KYOTO", "value": "오카자키+아라시야마", "desc": "7/9 당일치기"}
        ]
    )


elif menu == "🏨 숙소":
    render_info_page(
        "숙소",
        "숙소",
        "🏨",
        [
            {"label": "OSAKA", "value": "렘 신오사카", "desc": "7/8~7/10"},
            {"label": "TOKYO", "value": "렘 롯폰기", "desc": "7/10~7/12"},
            {"label": "MOOD", "value": "고층·야경", "desc": "도쿄타워뷰 희망"}
        ]
    )


elif menu == "🎤 공연":
    render_info_page(
        "공연",
        "공연",
        "🎤",
        [
            {"label": "PLACE", "value": "Keio Arena", "desc": "TOKYO"},
            {"label": "7/11", "value": "낮공·밤공", "desc": "13:30 / 18:00"},
            {"label": "7/12", "value": "낮공·밤공", "desc": "13:00 / 17:30"}
        ]
    )


elif menu == "💴 여행 가계부":
    st.header("💴 여행 가계부")

    tab1, tab2 = st.tabs(["가계부", "날짜별 환율"])

    with tab2:
        st.markdown("""
        <div class="card">
            <div class="sticker">FX RATE</div>
            <h3>날짜별 엔화 환율</h3>
            <p>결제한 날의 환율을 직접 입력하면, 가계부의 엔화 금액이 원화로 자동 환산돼요.</p>
        </div>
        """, unsafe_allow_html=True)

        edited_fx = st.data_editor(
            st.session_state.fx,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "환율": st.column_config.NumberColumn("환율", min_value=0.0, step=0.01, format="%.2f원")
            }
        )

        if st.button("💱 환율 저장"):
            st.session_state.fx = edited_fx
            st.session_state.expenses = apply_fx_by_date(st.session_state.expenses, st.session_state.fx)
            save_data()
            st.success("환율 저장 완료! 가계부에 적용했어.")

    with tab1:
        st.markdown("""
        <div class="card">
            <div class="sticker">MONEY NOTE</div>
            <h3>여행 경비 기록</h3>
            <p>엔화는 날짜별 환율로 자동 원화 환산, 원화 결제는 원화 칸에 직접 입력하면 돼요.</p>
        </div>
        """, unsafe_allow_html=True)

        expenses_for_edit = apply_fx_by_date(st.session_state.expenses, st.session_state.fx)
        edited_expenses = st.data_editor(
            expenses_for_edit,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "엔화": st.column_config.NumberColumn("엔화", min_value=0, step=100, format="¥%d"),
                "원화": st.column_config.NumberColumn("원화", min_value=0, step=1000, format="%d원"),
                "환율": st.column_config.NumberColumn("환율", min_value=0.0, step=0.01, format="%.2f원"),
                "분류": st.column_config.SelectboxColumn(
                    "분류",
                    options=["항공권", "숙소", "교통", "공연", "식비", "쇼핑", "보험", "이심", "선물", "기타"]
                ),
                "결제수단": st.column_config.SelectboxColumn(
                    "결제수단",
                    options=["현금", "카드", "계좌이체", "기타"]
                ),
                "정산": st.column_config.SelectboxColumn(
                    "정산",
                    options=["완료", "예정", "나중에"]
                ),
                "누가냄": st.column_config.SelectboxColumn(
                    "누가냄",
                    options=["박하나", "친구", "공동", "기타"]
                )
            }
        )

        calc_df = calc_krw_from_expenses(edited_expenses)
        total = int(calc_df["환산원화"].sum()) if len(calc_df) else 0
        done_total = int(calc_df[calc_df["정산"] == "완료"]["환산원화"].sum()) if len(calc_df) else 0
        plan_total = total - done_total
        max_spend = int(calc_df["환산원화"].max()) if len(calc_df) else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 경비", f"{total:,}원")
        col2.metric("정산 완료", f"{done_total:,}원")
        col3.metric("정산 예정", f"{plan_total:,}원")
        col4.metric("최대 지출", f"{max_spend:,}원")

        if st.button("💴 가계부 저장"):
            st.session_state.expenses = edited_expenses
            save_data()
            st.success("가계부 저장 완료!")

        st.subheader("🍀 경비 미리보기")
        expense_preview(edited_expenses)

        if len(calc_df) > 0:
            st.markdown("""
            <div class="card">
                <div class="sticker">SUMMARY</div>
                <h3>분류별 경비</h3>
            </div>
            """, unsafe_allow_html=True)

            category_sum = calc_df.groupby("분류")["환산원화"].sum().reset_index()

            for _, row in category_sum.iterrows():
                percent = row["환산원화"] / total if total else 0
                st.markdown(
                    f'<span class="category-pill">{escape(str(row["분류"]))} · {int(row["환산원화"]):,}원</span>',
                    unsafe_allow_html=True
                )
                st.progress(percent)


elif menu == "✅ 준비물":
    st.header("✅ 준비물 체크리스트")

    edited_checklist = st.data_editor(
        st.session_state.checklist,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "구분": st.column_config.SelectboxColumn(
                "구분",
                options=["필수", "전자기기", "짐", "공연", "화장품", "교통", "기타"]
            ),
            "완료": st.column_config.CheckboxColumn("완료")
        }
    )

    completed = edited_checklist["완료"].sum()
    total = len(edited_checklist)
    progress = completed / total if total else 0

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div class="card">
          <div class="sticker">PACKING</div>
          <h3>준비 현황</h3>
          <div class="big-number">{completed}/{total}</div>
          <p>완료된 준비물</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.progress(progress)
        st.write(f"완료율: {progress * 100:.0f}%")

    if st.button("✅ 체크리스트 저장"):
        st.session_state.checklist = edited_checklist
        save_data()
        st.success("체크리스트 저장 완료!")


elif menu == "📎 파일 보관함":
    st.header("📎 파일/영수증 보관함")

    uploaded_files = st.file_uploader(
        "항공권, 숙소 바우처, 영수증 이미지를 업로드해줘",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "pdf"]
    )

    memo = st.text_input("업로드 메모", placeholder="예: 렘 롯폰기 바우처 / 교토 카페 영수증")

    if st.button("📎 파일 저장"):
        if uploaded_files:
            new_rows = []
            for file in uploaded_files:
                safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
                save_path = ATTACH_DIR / safe_name
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                new_rows.append({
                    "구분": "업로드",
                    "파일명": file.name,
                    "저장경로": str(save_path),
                    "메모": memo
                })
            st.session_state.attachments = pd.concat(
                [st.session_state.attachments, pd.DataFrame(new_rows)],
                ignore_index=True
            )
            save_data()
            st.success("파일 저장 완료!")
        else:
            st.warning("업로드할 파일을 선택해줘.")

    if not st.session_state.attachments.empty:
        st.subheader("보관된 파일")
        st.dataframe(st.session_state.attachments, width="stretch")
    else:
        st.info("아직 보관된 파일이 없어.")


elif menu == "📝 메모":
    st.header("📝 자유 메모")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="card">
            <div class="sticker">MEMO</div>
            <h3>여행 중 기억할 것</h3>
            <p>티켓 거래, 맛집, 선물 리스트, 현장 확인사항을 적어두기 좋아요.</p>
        </div>
        """, unsafe_allow_html=True)

        memo = st.text_area("여행 메모", value=st.session_state.memo, height=360)

        if st.button("📝 메모 저장"):
            st.session_state.memo = memo
            save_data()
            st.success("메모 저장 완료!")

    with col2:
        st.markdown("""
        <div class="card">
            <div class="sticker">TO-DO</div>
            <h3>여행 할 일</h3>
        </div>
        """, unsafe_allow_html=True)

        edited_todos = st.data_editor(
            st.session_state.todos,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "완료": st.column_config.CheckboxColumn("완료")
            }
        )

        if st.button("📝 할 일 저장"):
            st.session_state.todos = edited_todos
            save_data()
            st.success("할 일 저장 완료!")


elif menu == "💾 저장/초기화":
    st.header("💾 데이터 저장 / 초기화")

    st.markdown(f"""
    <div class="card">
        <div class="sticker">SAVE DATA</div>
        <h3>현재 저장 파일</h3>
        <p>{escape(str(DATA_FILE))}</p>
        <p>저장 버튼을 누르면 수정한 일정, 장소, 가계부, 메모가 JSON 파일로 보관돼요.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 전체 저장"):
            save_data()
            st.success("전체 저장 완료!")

    with col2:
        if st.button("🧹 기본값으로 초기화"):
            st.session_state.events = {k: v.copy() for k, v in DEFAULT_EVENTS.items()}
            st.session_state.routes = {k: v.copy() for k, v in DEFAULT_ROUTES.items()}
            st.session_state.checklist = DEFAULT_CHECKLIST.copy()
            st.session_state.expenses = DEFAULT_EXPENSES.copy()
            st.session_state.info = DEFAULT_INFO.copy()
            st.session_state.memo = ""
            st.session_state.places = DEFAULT_PLACES.copy()
            st.session_state.fx = DEFAULT_FX.copy()
            st.session_state.todos = DEFAULT_TODOS.copy()
            st.session_state.attachments = DEFAULT_ATTACHMENTS.copy()
            save_data()
            st.warning("기본값으로 초기화했어.")


render_bottom_tabs()
