import streamlit as st
import pandas as pd
from datetime import datetime
import os
import calendar
import altair as alt

# 🚨 [중요] 최상단 고정
st.set_page_config(
    page_title="수룡이와 함께하는 맞춤형 다이어트",
    page_icon="🐉",
    layout="centered"
)

LOG_FILE = "diet_exercise_log.csv"
GROW_FILE = "suryong_growth.csv"
PROFILE_FILE = "user_profile.csv"
LOGO_FILE = "icon.png"


# --- 공통 함수 정의 ---
def calculate_bmi(weight, height):
    h = height / 100
    return round(weight / (h ** 2), 1)


def calculate_bmr(weight, height, age, gender):
    if gender == "남자":
        return round(10 * weight + 6.25 * height - 5 * age + 5)
    return round(10 * weight + 6.25 * height - 5 * age - 161)


def calculate_tdee(bmr, activity):
    factors = {
        "거의 안 움직임": 1.2,
        "가벼운 활동": 1.375,
        "보통": 1.55,
        "활발함": 1.725,
        "매우 활발": 1.9
    }
    return round(bmr * factors[activity])


def get_level(exp):
    if exp < 50:
        return 1, "🥚 알 수룡이", "a.jpg"
    elif exp < 120:
        return 2, "🐣 아기 수룡이", "b.jpg"
    elif exp < 220:
        return 3, "🐉 성장한 수룡이", "c.jpg"
    else:
        return 4, "👑 전설의 수룡이", "d.jpg"


def load_exp():
    if os.path.exists(GROW_FILE):
        df = pd.read_csv(GROW_FILE)
        return int(df["경험치"].iloc[-1])
    return 0


def save_exp(exp):
    df = pd.DataFrame([{"경험치": exp}])
    df.to_csv(GROW_FILE, index=False, encoding="utf-8-sig")


def load_profile():
    if os.path.exists(PROFILE_FILE):
        df = pd.read_csv(PROFILE_FILE)
        return df.iloc[-1].to_dict()
    return {}


def save_profile(profile):
    df = pd.DataFrame([profile])
    df.to_csv(PROFILE_FILE, index=False, encoding="utf-8-sig")


# [데이터셋] 음식 데이터
foods = {
    "김밥": {"calorie": 450, "type": "한식", "is_healthy": True},
    "참치김밥": {"calorie": 500, "type": "한식", "is_healthy": True},
    "치즈김밥": {"calorie": 530, "type": "한식", "is_healthy": False},
    "샐러드": {"calorie": 250, "type": "가벼운식단", "is_healthy": True},
    "닭가슴살": {"calorie": 165, "type": "단백질", "is_healthy": True},
    "고구마": {"calorie": 130, "type": "가벼운식단", "is_healthy": True},
    "현미밥": {"calorie": 320, "type": "한식", "is_healthy": True},
    "라면": {"calorie": 500, "type": "분식", "is_healthy": False},
    "불닭볶음면": {"calorie": 530, "type": "분식", "is_healthy": False},
    "짜장면": {"calorie": 700, "type": "중식", "is_healthy": False},
    "짬뽕": {"calorie": 650, "type": "중식", "is_healthy": False},
    "햄버거": {"calorie": 550, "type": "패스트푸드", "is_healthy": False},
    "치킨": {"calorie": 700, "type": "패스트푸드", "is_healthy": False},
    "피자": {"calorie": 800, "type": "패스트푸드", "is_healthy": False},
    "떡볶이": {"calorie": 450, "type": "분식", "is_healthy": False},
    "순대": {"calorie": 300, "type": "분식", "is_healthy": False},
    "계란": {"calorie": 80, "type": "단백질", "is_healthy": True},
    "바나나": {"calorie": 90, "type": "간식", "is_healthy": True},
    "사과": {"calorie": 100, "type": "간식", "is_healthy": True},
    "요거트": {"calorie": 120, "type": "간식", "is_healthy": True},
    "연어": {"calorie": 250, "type": "단백질", "is_healthy": True},
    "스테이크": {"calorie": 600, "type": "단백질", "is_healthy": True},
    "파스타": {"calorie": 650, "type": "양식", "is_healthy": False},
    "샌드위치": {"calorie": 400, "type": "간단식", "is_healthy": True},
    "초밥": {"calorie": 500, "type": "일식", "is_healthy": True}
}

# --- 🏋️ 오리지널 프리셋 데이터베이스 (홈트 분기) ---
exercise_presets = {
    "홈트": {
        "근육증가": {
            "최상 (에너지 넘침)": [
                {"name": "정석 맨몸 스쿼트", "cal_10m": 65, "guide": "🔥 5세트 × 20회", "rest": "⏱️ 휴식 45초", "tip": "어깨너비로 벌리고 무릎이 안으로 말리지 않게 엉덩이를 깊숙이 내리세요."},
                {"name": "워킹 런지 / 백 런지", "cal_10m": 60, "guide": "🔥 5세트 × 양발 12회", "rest": "⏱️ 휴식 45초", "tip": "한 발을 크게 디디며 무릎을 90도로 내리되, 앞 무릎이 발끝을 넘지 않게 주의하세요."},
                {"name": "정석 푸쉬업", "cal_10m": 55, "guide": "🔥 5세트 × 15회", "rest": "⏱️ 휴식 45초", "tip": "머리부터 발끝까지 수평을 유지하고 가슴을 바닥 직전까지 내렸다가 밀어내세요."},
                {"name": "정식 엘보우 플랭크", "cal_10m": 45, "guide": "🔥 4세트 × 60초 버티기", "rest": "⏱️ 휴식 30초", "tip": "팔꿈치로 바닥을 밀어내며 복부와 엉덩이에 힘을 주어 몸을 일직선으로 만드세요."}
            ],
            "정상 (보통)": [
                {"name": "정석 맨몸 스쿼트", "cal_10m": 65, "guide": "✨ 4세트 × 15회", "rest": "⏱️ 휴식 60초", "tip": "체중을 발뒤꿈치에 싣고 일어날 때 둔근을 강하게 수축합니다."},
                {"name": "워킹 런지 / 백 런지", "cal_10m": 60, "guide": "✨ 4세트 × 양발 10회", "rest": "⏱️ 휴식 60초", "tip": "상체를 곧게 세우고 수직 방향으로 체중을 내려 자극을 줍니다."},
                {"name": "정석 푸쉬업", "cal_10m": 55, "guide": "✨ 4세트 × 10회", "rest": "⏱️ 휴식 60초", "tip": "힘들 경우 무릎을 대고 정자세로 가슴 자극을 느끼며 진행하세요."},
                {"name": "정식 엘보우 플랭크", "cal_10m": 45, "guide": "✨ 3세트 × 45초 버티기", "rest": "⏱️ 휴식 45초", "tip": "허리가 아래로 처지면 부상 위험이 있으니 복부에 긴장을 유지하세요."}
            ],
            "피곤함 (가벼운 운동 필요)": [
                {"name": "맨몸 와이드 스쿼트 (저강도)", "cal_10m": 50, "guide": "🔋 3세트 × 12회", "rest": "⏱️ 휴식 90초", "tip": "다리를 넓게 벌려 관절 부담을 줄이고 허벅지 안쪽 자극에 집중합니다."},
                {"name": "매트 복부 크런치", "cal_10m": 40, "guide": "🔋 3세트 × 15회", "rest": "⏱️ 휴식 90초", "tip": "허리를 바닥에 붙인 채 상체 윗부분만 살짝 들어 올려 복부를 쥡니다."},
                {"name": "벽 푸쉬업 (Wall Push-Up)", "cal_10m": 35, "guide": "🔋 3세트 × 12회", "rest": "⏱️ 휴식 90초", "tip": "벽을 짚고 서서 진행하여 어깨와 손목의 부담을 최소화합니다."},
                {"name": "가벼운 제자리 걷기", "cal_10m": 30, "guide": "🔋 10분 지속 페이스", "rest": "⏱️ 여유롭게 호흡", "tip": "팔을 앞뒤로 흔들며 가볍게 몸을 움직여 혈액 순환을 돕습니다."}
            ],
            "근육통 있음": [
                {"name": "하체 전신 스트레칭", "cal_10m": 25, "guide": "🩹 부위별 30초 유지", "rest": "⏱️ 제한 없음", "tip": "뭉친 허벅지와 둔근 유연성을 늘려 피로 물질을 제거합니다."},
                {"name": "상체 및 어깨 회전 리커버리", "cal_10m": 25, "guide": "🩹 3세트 반복", "rest": "⏱️ 편안하게 휴식", "tip": "가슴과 회전근개를 부드럽게 풀어주어 통증을 완화합니다."},
                {"name": "코어 데드버그 코스", "cal_10m": 35, "guide": "🩹 3세트 × 10회", "rest": "⏱️ 휴식 90초", "tip": "누운 자세에서 팔다리를 교차해 움직이며 척추 부담 없이 코어를 깨웁니다."},
                {"name": "요가 릴렉스 가이드", "cal_10m": 25, "guide": "🩹 15분 전신 호흡", "rest": "⏱️ 릴렉스", "tip": "호흡에 집중하며 전신의 긴장을 풀어주는 힐링 타임입니다."}
            ]
        },
        "감량": {
            "최상 (에너지 넘침)": [
                {"name": "땅끄부부 칼소폭 매운맛", "cal_10m": 90, "guide": "🔥 20분 풀버전 올인", "rest": "⏱️ 영상 페이스 유지", "tip": "동작을 크고 확실하게 하여 칼로리 버닝을 극대화합니다."},
                {"name": "버피 테스트 (고강도 전신)", "cal_10m": 120, "guide": "🔥 4세트 × 15회", "rest": "⏱️ 휴식 45초", "tip": "속도보다는 정자세로 착지하여 관절을 보호하세요."},
                {"name": "고속 제자리 무릎 높여 뛰기", "cal_10m": 100, "guide": "🔥 4세트 × 45초", "rest": "⏱️ 휴식 45초", "tip": "팔꿈치를 흔들며 무릎을 골반 높이까지 빠르게 끌어올립니다."}
            ],
            "정상 (보통)": [
                {"name": "땅끄부부 칼소폭 매운맛", "cal_10m": 90, "guide": "✨ 20분 표준 수행", "rest": "⏱️ 표준 호흡 구사", "tip": "무리가 가지 않는 선에서 끝까지 완주하는 것을 목표로 합니다."},
                {"name": "가벼운 실내 조깅 / 제자리 뛰기", "cal_10m": 70, "guide": "✨ 20분 지속", "rest": "⏱️ 일정하게 유지", "tip": "발바닥 전체가 부드럽게 닿도록 가볍게 리듬을 탑니다."}
            ],
            "피곤함 (가벼운 운동 필요)": [
                {"name": "빠르게 걷기 / 파워 워킹", "cal_10m": 45, "guide": "🔋 30분 산책 페이스", "rest": "⏱️ 무리하지 않기", "tip": "땀이 가볍게 날 정도로만 속도를 조절해 걸어줍니다."},
                {"name": "폼롤러 전신 근막 이완 코스", "cal_10m": 25, "guide": "🩹 20분 전신 순환", "rest": "⏱️ 힐링 템포", "tip": "아픈 부위를 지그시 누르며 호흡을 내쉬어 몸을 이완합니다."}
            ],
            "근육통 있음": [
                {"name": "빠르게 걷기 / 파워 워킹", "cal_10m": 45, "guide": "🔋 30분 산책 페이스", "rest": "⏱️ 무리하지 않기", "tip": "땀이 가볍게 날 정도로만 속도를 조절해 걸어줍니다."},
                {"name": "폼롤러 전신 근막 이완 코스", "cal_10m": 25, "guide": "🩹 20분 전신 순환", "rest": "⏱️ 힐링 템포", "tip": "아픈 부위를 지그시 누르며 호흡을 내쉬어 몸을 이완합니다."}
            ]
        }
    }
}

# --- 🏋️ [핵심 수정] 헬스장 근육증가 전용 상체/하체 분할형 컨디션 조절 데이터베이스 ---
gym_split_presets = {
    "최상 (에너지 넘침)": {
        "상체": [
            {"name": "렛 풀 다운 (등)", "cal_10m": 65, "guide": "🔥 고중량 5세트 × 10~12회 (실패지점 타겟)", "rest": "⏱️ 휴식 50초", "tip": "광배근을 강하게 이완하고 바를 쇄골 쪽으로 깊숙이 당기세요."},
            {"name": "체스트 프레스 머신 (가슴)", "cal_10m": 65, "guide": "🔥 고중량 5세트 × 10~12회", "rest": "⏱️ 휴식 50초", "tip": "어깨를 패드에 밀착하고 겨드랑이에 힘을 주며 강하게 밀어줍니다."}
        ],
        "하체": [
            {"name": "레그 프레스 머신 (허벅지 전체)", "cal_10m": 85, "guide": "🔥 고중량 5세트 × 12회 (강한 수축)", "rest": "⏱️ 휴식 60초", "tip": "발판을 밀 때 무릎이 다 펴지기 직전까지만 밀어 관절을 보호하세요."},
            {"name": "천국의 계단 (스텝밀 마무리)", "cal_10m": 110, "guide": "🏃 인터벌 페이스 15분", "rest": "⏱️ 지속 가동", "tip": "상체를 약간 숙이고 둔근의 힘을 이용해 계단을 디디세요."}
        ]
    },
    "정상 (보통)": {
        "상체": [
            {"name": "렛 풀 다운 (등)", "cal_10m": 55, "guide": "✨ 정석 4세트 × 12회 (적정 중량)", "rest": "⏱️ 휴식 60초", "tip": "상체가 뒤로 과도하게 눕지 않도록 복부에 긴장을 유지하세요."},
            {"name": "체스트 프레스 머신 (가슴)", "cal_10m": 55, "guide": "✨ 정석 4세트 × 12회", "rest": "⏱️ 휴식 60초", "tip": "수축 시 가슴 중앙이 모이는 자극에 집중하며 지그시 밀어줍니다."}
        ],
        "하체": [
            {"name": "레그 프레스 머신 (허벅지 전체)", "cal_10m": 70, "guide": "✨ 정석 4세트 × 15회 (표준 중량)", "rest": "⏱️ 휴식 60초", "tip": "내려올 때 허리가 패드에서 뜨지 않도록 엉덩이를 꽉 밀착하세요."},
            {"name": "천국의 계단 (스텝밀 마무리)", "cal_10m": 90, "guide": "🏃 일정 페이스 15분", "rest": "⏱️ 지속 가동", "tip": "하체 근력을 쥐어짜 유산소 마무리를 완수합니다."}
        ]
    },
    "피곤함 (가벼운 운동 필요)": {
        "상체": [
            {"name": "렛 풀 다운 (저중량)", "cal_10m": 45, "guide": "🔋 라이트 3세트 × 12회 (자극 위주)", "rest": "⏱️ 휴식 90초", "tip": "무게를 낮추고 등의 날개뼈가 부드럽게 움직이는 것에만 집중합니다."},
            {"name": "가벼운 가슴 머신 스트레칭", "cal_10m": 35, "guide": "🔋 3세트 × 15회 수월하게", "rest": "⏱️ 휴식 90초", "tip": "반동 없이 가슴 근육에 혈류를 보내준다는 느낌으로 가볍게 움직입니다."}
        ],
        "하체": [
            {"name": "레그 프레스 머신 (저중량)", "cal_10m": 50, "guide": "🔋 라이트 3세트 × 12회 (관절 보호)", "rest": "⏱️ 휴식 90초", "tip": "중량을 대폭 낮추고 가동 범위를 무리하지 않게 가져갑니다."},
            {"name": "실내 고정식 싸이클 자전거", "cal_10m": 50, "guide": "🚶 가벼운 페달링 20분", "rest": "⏱️ 릴렉스", "tip": "하체의 젖산과 피로를 부드럽게 분해하는 페이스입니다."}
        ]
    },
    "근육통 있음": {
        "상체": [
            {"name": "폼롤러 등/어깨 상체 이완", "cal_10m": 25, "guide": "🩹 15분 전신 스트레칭", "rest": "⏱️ 여유롭게", "tip": "뭉친 광배근과 가슴 근막을 문질러 통증을 완화시킵니다."},
            {"name": "맨몸 회전근개 리커버리", "cal_10m": 25, "guide": "🩹 3세트 반복", "rest": "⏱️ 편안하게", "tip": "관절을 가볍게 돌려주어 상체 피로 물질을 제거합니다."}
        ],
        "하체": [
            {"name": "하체 전신 스트레칭", "cal_10m": 25, "guide": "🩹 부위별 30초 유지", "rest": "⏱️ 제한 없음", "tip": "뭉친 허벅지와 골반 유연성을 늘려 피로를 회복합니다."},
            {"name": "폼롤러 하체 근막 이완 코스", "cal_10m": 25, "guide": "🩹 20분 둔근/대퇴 이완", "rest": "⏱️ 힐링 템포", "tip": "아픈 부위를 지그시 누르며 호흡을 내쉬어 몸을 풉니다."}
        ]
    }
}


# --- 페이지 1: 메인 다이어리 ---
def show_main_page():
    log_col1, log_col2 = st.columns([1, 4])
    with log_col1:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_container_width=True)
        else:
            st.info("🐉 LOGO")
    with log_col2:
        st.title("핏메이트")
        st.caption("식단과 운동 기록을 매일 누적하는 수룡이 다이어트 다이어리")

    st.divider()

    profile = load_profile()

    st.header("👤 수정이 정보 입력")
    name = st.text_input("이름", value=profile.get("이름", "에융이"))

    gender_options = ["여자", "남자"]
    gender = st.selectbox("성별", gender_options, index=gender_options.index(profile.get("성별", "여자")))

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("나이", min_value=1, step=1, value=int(profile.get("나이", 20)))
    with col2:
        height = st.number_input("키(cm)", min_value=1.0, value=float(profile.get("키(cm)", 165.0)))
    with col3:
        weight = st.number_input("몸무게(kg)", min_value=1.0, value=float(profile.get("몸무게(kg)", 60.0)))

    activity_options = ["거의 안 움직임", "가벼운 활동", "보통", "활발함", "매우 활발"]
    activity = st.selectbox("활동량", activity_options, index=activity_options.index(profile.get("활동량", "보통")))

    goal_options = ["감량", "유지", "근육증가"]
    goal = st.selectbox("목표", goal_options, index=goal_options.index(profile.get("목표", "감량")))

    allergy = st.text_input("알레르기 음식", value=profile.get("알레르기 음식", "없음"))
    dislike = st.text_input("싫어하는 음식", value=profile.get("싫어하는 음식", "없음"))

    food_style_options = ["한식", "가벼운식단", "단백질", "간단식", "분식", "중식", "양식", "일식", "간식", "패스트푸드"]
    food_style = st.selectbox("선호 식단", food_style_options, index=food_style_options.index(profile.get("선호 식단", "단백질")))

    save_profile({
        "이름": name, "성별": gender, "나이": age, "키(cm)": height, "몸무게(kg)": weight,
        "활동량": activity, "목표": goal, "알레르기 음식": allergy, "싫어하는 음식": dislike, "선호 식단": food_style
    })

    user_bmi = calculate_bmi(weight, height)
    user_bmr = calculate_bmr(weight, height, age, gender)
    user_tdee = calculate_tdee(user_bmr, activity)

    if goal == "감량":
        daily_calorie = user_tdee - 300
    elif goal == "근육증가":
        daily_calorie = user_tdee + 300
    else:
        daily_calorie = user_tdee

    st.divider()

    st.header("🍽️ 오늘 먹은 음식 기록")
    selected_foods = st.multiselect("오늘 어떤 음식을 드셨나요?", list(foods.keys()))

    total = 0
    for food in selected_foods:
        total += foods[food]["calorie"]

    if selected_foods:
        col_h, col_uh = st.columns(2)
        with col_h:
            st.write("🍏 **다이어트 및 근성장 식단**")
            for food in selected_foods:
                if foods[food]["is_healthy"]:
                    st.write(f"- {food} ({foods[food]['calorie']} kcal)")
        with col_uh:
            st.write("😈 **주의가 필요한 일반 식단**")
            for food in selected_foods:
                if not foods[food]["is_healthy"]:
                    st.write(f"- {food} ({foods[food]['calorie']} kcal)")

    st.divider()

    st.subheader("💡 분석 및 맞춤 제안 받기")
    if "calc_submitted" not in st.session_state:
        st.session_state.calc_submitted = False

    if st.button("✨ 오늘의 다이어트 및 운동 처방 보기", type="primary"):
        st.session_state.calc_submitted = True

    if st.session_state.calc_submitted:
        st.header("🎮 수룡이의 오늘 식단 상태")

        if total == 0:
            suryong_img = "normal_suryong.jpg"
            suryong_msg = f"오늘 식사를 기록해 주세요! 현재 BMI는 {user_bmi}입니다."
            status_color = "info"
        elif total < daily_calorie - 400:
            suryong_img = "slim_suryong.jpg"
            suryong_msg = "근육을 늘리거나 건강을 유지하려면 조금 더 든든하게 드셔야 해요! 🥺"
            status_color = "warning"
        elif total > daily_calorie + 150:
            suryong_img = "fat_suryong.jpg"
            suryong_msg = "오늘 권장 칼로리를 초과했습니다! 유산소 타임라인을 길게 구성해 체지방을 지워봐요! 🔥"
            status_color = "error"
        else:
            suryong_img = "normal_suryong.jpg"
            suryong_msg = "완벽합니다! 근성장 및 체력 유지를 위한 아주 훌륭한 칼로리 밸런스예요. 👍"
            status_color = "success"

        col_char, col_info = st.columns([1, 1])
        with col_char:
            try:
                st.image(suryong_img, use_container_width=True)
            except:
                st.error(f"⚠️ 캐릭터 이미지를 불러올 수 없습니다.")

        with col_info:
            st.subheader(f"🐲 {name}님의 당일 영양 스코어")
            if status_color == "info": st.info(suryong_msg)
            elif status_color == "error": st.error(suryong_msg)
            elif status_color == "warning": st.warning(suryong_msg)
            else: st.success(suryong_msg)

            st.metric("나의 BMI 지수", f"{user_bmi}")
            st.metric("목표 권장 칼로리", f"{daily_calorie} kcal")
            st.metric("현재 섭취량", f"{total} kcal", delta=total - daily_calorie, delta_color="inverse")

        st.divider()

        tab1, tab2, tab3 = st.tabs(["🍱 추천 식단", "🏃 AI 목표 시간 맞춤형 루틴", "📅 나의 누적 다이어트 일지"])

        with tab1:
            st.write("✨ **수룡이가 엄선한 선호 타겟 맞춤 식단**")
            recommended = [
                f for f in foods
                if foods[f]["type"] == food_style
                   and foods[f]["is_healthy"] == True
                   and (allergy == "없음" or allergy not in f)
                   and (dislike == "없음" or dislike not in f)
            ]
            if not recommended:
                recommended = ["닭가슴살", "연어", "계란", "현미밥", "샐러드"]

            for f in recommended:
                st.write(f"- {f}: {foods[f]['calorie']} kcal")

        with tab2:
            st.write("🤖 **수룡이 AI 스포츠 닥터의 상황별 유연 분배 처방**")

            st.subheader("📋 오늘의 환경 및 신체 컨디션")
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1:
                select_date = st.date_input("기록 날짜", datetime.now().date())
            with col_ex2:
                ex_place = st.radio("오늘의 운동 장소", ["헬스장", "홈트"], key="main_ex_place")
            with col_ex3:
                user_condition = st.selectbox("현재 나의 컨디션", ["최상 (에너지 넘침)", "정상 (보통)", "피곤함 (가벼운 운동 필요)", "근육통 있음"], key="main_condition")

            st.write("")
            st.subheader("⏱️ 오늘 운동에 투자할 총 시간 설정")
            target_total_time = st.slider("오늘은 총 몇 분 동안 운동을 진행하시겠습니까?", 20, 180, 60, step=5, key="main_time_slider")

            st.divider()

            # --- 💡 컨디션 가중치 가동 조건문 ---
            condition_multiplier = 1.0
            if user_condition == "최상 (에너지 넘침)":
                condition_multiplier = 1.2
                st.success("🚀 **컨디션 최상 버프 가동!** 신체 에너지가 충만하므로 세트 수와 강도를 높이고 칼로리 소모 보너스($\times 1.2$)를 부여합니다!")
            elif user_condition == "정상 (보통)":
                condition_multiplier = 1.0
                st.info("🟢 **정상 컨디션 가동:** 무리 없는 정석 세트 수와 표준 휴식 템포를 제공합니다.")
            else:
                condition_multiplier = 0.8
                st.warning("🩹 **안전 제일 리커버리 모드 전환:** 부상 방지와 피로 물질 제거를 위해 세트 강도가 완화된 맞춤 루틴으로 자동 스위칭했습니다.")

            ai_prescribed_exercises = []
            ai_prescribed_calories = 0

            # 🚨 가상 DOM 오류 차단을 위한 안전 키 컴포넌트 인덱스 변환
            cond_idx = "max" if "최상" in user_condition else "norm" if "정상" in user_condition else "low"

            # --- 💡 메인 엔진 렌더링 파트 ---
            with st.container():
                if ex_place == "홈트":
                    sub_goal = "근육증가" if goal == "근육증가" else "감량"
                    current_pool = exercise_presets["홈트"][sub_goal].get(user_condition, exercise_presets["홈트"][sub_goal]["피곤함 (가벼운 운동 필요)"])
                    
                    st.markdown(f"### 🏠 오늘 컨디션([{user_condition}])에 맞춘 맞춤형 {sub_goal} 홈트레이닝")
                    time_per_ex = max(5, round(target_total_time / len(current_pool)))
                    
                    col_hw1, col_hw2 = st.columns(2)
                    for idx, item in enumerate(current_pool):
                        target_col = col_hw1 if idx % 2 == 0 else col_hw2
                        with target_col:
                            st.markdown(f"🎯 **{item['name']}**")
                            st.markdown(f"  - ⏱️ 추천 시간: **{time_per_ex}분**")
                            st.markdown(f"  - 📊 수행 가이드: **{item['guide']}**")
                            st.markdown(f"  - {item['rest']}")
                            with st.expander("📖 정석 자세 및 부상방지 꿀팁", key=f"exp_h_{cond_idx}_{idx}"):
                                st.caption(item["tip"])
                            
                            ai_prescribed_exercises.append(item['name'])
                            ai_prescribed_calories += round((time_per_ex / 10) * item["cal_10m"] * condition_multiplier)

                else:  # 🚨 [완벽 해결] 헬스장 선택 시 상체/하체 분할 구조 유지 + 컨디션 강도 조절 분기
                    pool_dict = gym_split_presets.get(user_condition, gym_split_presets["정상 (보통)"])
                    
                    st.markdown(f"### 🏋️ 오늘 컨디션([{user_condition}])에 맞춤 조절된 [상체 / 하체] 분할 머신 루틴")
                    
                    # 상체와 하체 풀의 총 종목 수 합산하여 시간 균등 배분
                    total_items = len(pool_dict["상체"]) + len(pool_dict["하체"])
                    time_per_ex = max(5, round(target_total_time / total_items))
                    
                    col_split1, col_split2 = st.columns(2)
                    
                    # --- [좌측 열: 상체 타겟 머신 라인업] ---
                    with col_split1:
                        st.markdown("#### 🦾 상체 타겟 라인")
                        for idx, item in enumerate(pool_dict["상체"]):
                            st.markdown(f"🔹 **{item['name']}**")
                            st.markdown(f"  - ⏱️ 분배 시간: **{time_per_ex}분**")
                            st.markdown(f"  - 📊 강도 세팅: **{item['guide']}**")
                            st.markdown(f"  - {item['rest']}")
                            with st.expander("💡 기구 사용 가이드", key=f"exp_split_upper_{cond_idx}_{idx}"):
                                st.caption(item["tip"])
                            
                            ai_prescribed_exercises.append(item['name'])
                            ai_prescribed_calories += round((time_per_ex / 10) * item["cal_10m"] * condition_multiplier)
                    
                    # --- [우측 열: 하체 타겟 머신 라인업] ---
                    with col_split2:
                        st.markdown("#### 🦿 하체 타겟 라인")
                        for idx, item in enumerate(pool_dict["하체"]):
                            st.markdown(f"🔸 **{item['name']}**")
                            st.markdown(f"  - ⏱️ 분배 시간: **{time_per_ex}분**")
                            st.markdown(f"  - 📊 강도 세팅: **{item['guide']}**")
                            st.markdown(f"  - {item['rest']}")
                            with st.expander("💡 기구 사용 가이드", key=f"exp_split_lower_{cond_idx}_{idx}"):
                                st.caption(item["tip"])
                            
                            ai_prescribed_exercises.append(item['name'])
                            ai_prescribed_calories += round((time_per_ex / 10) * item["cal_10m"] * condition_multiplier)

            st.divider()

            # --- [실제 수행 기록 정산기 단락] ---
            st.subheader("🏋️ 오늘 실제로 완료한 운동 체크")
            use_ai_routine = st.checkbox("✅ 오늘 AI가 추천해 준 컨디션 루틴을 그대로 완료했습니다! (원클릭 자동 등록)", value=False, key="checkbox_ai_routine")

            actual_burned_calories = 0
            actual_time_sum = 0
            ex_summary = ""

            if use_ai_routine:
                actual_time_sum = target_total_time
                actual_burned_calories = ai_prescribed_calories
                ex_summary = f"[{user_condition}] " + ", ".join(ai_prescribed_exercises)
                
                st.info(f"✨ 연동 완료: 현재 내 몸 상태([{user_condition}]) 정보가 주입되어 총 **{actual_time_sum}분** 운동, 총 **{actual_burned_calories} kcal**가 정밀 자동 결산되었습니다!")
            else:
                st.caption("일부만 수행하셨거나 다른 운동을 하셨다면 아래 풀에서 직접 골라 입력하실 수 있습니다.")
                grand_pool = ["레그 프레스 머신 (허벅지 전체)", "렛 풀 다운 (등)", "체스트 프레스 머신 (가슴)", "트레드밀 (러닝머신)", "천국의 계단 (스텝밀)", "실내 고정식 싸이클 자전거"]
                actual_done_list = st.multiselect("오늘 실제 마친 항목들을 선택해 주세요.", grand_pool, key="manual_select_ex")
                
                if actual_done_list:
                    for ex_name in actual_done_list:
                        done_time = st.slider(f"[{ex_name}] 수행 시간(분)", 0, 180, 30, key=f"v15_time_{ex_name}")
                        actual_burned_calories += round((done_time / 10) * 60 * condition_multiplier)
                        actual_time_sum += done_time
                    ex_summary = f"[{user_condition}/수동] " + ", ".join(actual_done_list)

            if use_ai_routine or (not use_ai_routine and 'actual_done_list' in locals() and actual_done_list):
                st.divider()
                st.subheader("🔥 당일 실전 운동 최종 정산 스코어")
                col_res1, col_res2 = st.columns(2)
                col_res1.metric("총 결산 운동 시간", f"{actual_time_sum} 분")
                col_res2.metric("수룡이 인증 소모 칼로리", f"{actual_burned_calories} kcal (컨디션 가중치 연동)")

            st.divider()
            st.subheader("💾 최종 운동 기록 세이브")
            if st.button("🔥 정산된 수치로 최종 저장하고 수룡이 경험치 받기", key="btn_save_exercise"):
                if not use_ai_routine and ('actual_done_list' not in locals() or not actual_done_list):
                    st.error("완료한 운동 수치가 정산되지 않았습니다. AI 원클릭 체크박스를 누르거나 수동 운동을 골라주세요.")
                else:
                    current_time_str = datetime.now().strftime("%H:%M")
                    formatted_date = f"{select_date.strftime('%Y-%m-%d')} {current_time_str}"

                    new_data = {
                        "날짜": formatted_date, "이름": name if name else "사용자",
                        "체중(kg)": weight, "BMI": user_bmi, "목표 칼로리": daily_calorie, "오늘 섭취량": total,
                        "운동 장소": ex_summary, "운동 부위": actual_burned_calories, "오늘 컨디션": user_condition, "운동 시간(분)": actual_time_sum
                    }
                    df = pd.read_csv(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame(columns=new_data.keys())
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

                    old_exp = load_exp()
                    new_exp = old_exp + 10
                    save_exp(new_exp)

                    st.success(f"🎉 맞춤 일지 저장 성공! 수룡이 경험치 10 EXP가 정상 지급되었습니다!")

        with tab3:
            st.write("📅 **나의 누적 다이어트 일지**")
            if os.path.exists(LOG_FILE):
                df_log = pd.read_csv(LOG_FILE)
                
                df_log["오늘 섭취량"] = pd.to_numeric(df_log["오늘 섭취량"], errors="coerce").fillna(0)
                df_log["운동 부위"] = pd.to_numeric(df_log["운동 부위"], errors="coerce").fillna(0)
                df_log["운동 시간(분)"] = pd.to_numeric(df_log["운동 시간(분)"].fillna(0), errors="coerce")
                
                df_display = df_log.copy()
                df_display = df_display.rename(columns={"운동 장소": "수행한 운동 조합", "운동 부위": "소비 칼로리(kcal)", "오늘 컨디션": "수행 시 컨디션"})
                st.dataframe(df_display.iloc[::-1], use_container_width=True)

                st.subheader("📊 나의 다이어트 요약")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                col_stat1.metric("총 기록 수", f"{len(df_log)} 회")
                col_stat2.metric("평균 하루 섭취 칼로리", f"{int(df_log['오늘 섭취량'].mean())} kcal")
                col_stat3.metric("평균 운동 소모 칼로리", f"{int(df_log['운동 부위'].mean())} kcal")
                col_stat4.metric("누적 운동 시간", f"{int(df_log['운동 시간(분)'].sum())} 분")

                st.divider()
                
                st.subheader("📊 일자별 섭취량 vs 운동 소모량 비교")
                try:
                    df_log["날짜_일만"] = pd.to_datetime(df_log["날짜"]).dt.strftime("%Y-%m-%d")
                    df_unique_dates = df_log.groupby("날짜_일만")[["오늘 섭취량", "운동 부위"]].sum().reset_index()
                    available_dates = df_unique_dates["날짜_일만"].tolist()
                    
                    if available_dates:
                        chart_col1, chart_col2 = st.columns([3, 1.5])
                        with chart_col2:
                            selected_chart_date = st.selectbox("날짜를 클릭하세요", options=available_dates, index=len(available_dates)-1, key="chart_date_selector")
                        with chart_col1:
                            day_data = df_unique_dates[df_unique_dates["날짜_일만"] == selected_chart_date].iloc[0]
                            plot_df = pd.DataFrame({
                                "구분": ["섭취 칼로리", "사용 칼로리"],
                                "칼로리(kcal)": [int(day_data["오늘 섭취량"]), int(day_data["운동 부위"])]
                            })
                            custom_chart = alt.Chart(plot_df).mark_bar(size=40).encode(
                                x=alt.X("구분:N", title="데이터 분류", axis=alt.Axis(labelAngle=0)),
                                y=alt.Y("칼로리(kcal):Q", title="에너지 수치 (kcal)"),
                                color=alt.Color("구분:N", scale=alt.Scale(domain=["섭취 칼로리", "사용 칼로리"], range=["#1f77b4", "#aec7e8"]), legend=alt.Legend(title="범례"))
                            ).properties(width="container", height=320)
                            st.altair_chart(custom_chart, use_container_width=True)
                except Exception as e:
                    st.info("데이터를 안전하게 동기화하고 있습니다.")

                st.divider()
                st.subheader("🗓️ 월별 운동 캘린더")
                df_log["날짜"] = pd.to_datetime(df_log["날짜"], errors="coerce")
                df_log = df_log.dropna(subset=["날짜"])

                if len(df_log) > 0:
                    latest_date = df_log["날짜"].max()
                    years = sorted(df_log["날짜"].dt.year.unique())
                    cal_col1, cal_col2 = st.columns(2)
                    selected_year = cal_col1.selectbox("연도 선택", years, index=years.index(latest_date.year))
                    selected_month = cal_col2.selectbox("월 선택", list(range(1, 13)), index=latest_date.month - 1)

                    month_data = df_log[(df_log["날짜"].dt.year == selected_year) & (df_log["날짜"].dt.month == selected_month)]
                    exercise_days = set(month_data["날짜"].dt.day)
                    cal = calendar.monthcalendar(selected_year, selected_month)

                    st.write(f"📅 {selected_year}년 {selected_month}월")
                    days_kor = ["월", "화", "수", "목", "금", "토", "일"]
                    header = st.columns(7)
                    for i, d in enumerate(days_kor): header[i].markdown(f"**{d}**")

                    for week in cal:
                        cols = st.columns(7)
                        for i, day in enumerate(week):
                            if day == 0: cols[i].write("")
                            elif day in exercise_days: cols[i].markdown(f"🟢 **{day}**")
                            else: cols[i].markdown(f"{day}")

                st.divider()
                if st.checkbox("⚠️ 전체 기록 지우기", key="delete_all_logs_check"):
                    if st.button("정말 삭제하시겠습니까?", key="btn_delete_logs_confirm"):
                        os.remove(LOG_FILE)
                        st.warning("모든 다이어트 기록이 삭제되었습니다. 새로고침 해주세요.")
            else:
                st.info("아직 저장된 다이어트 일지가 없습니다.")


# --- 페이지 2: 수룡이 키우기 ---
def show_growth_page():
    log_col1, log_col2 = st.columns([1, 4])
    with log_col1:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_container_width=True)
        else:
            st.info("🐉 LOGO")
    with log_col2:
        st.title("핏메이트")
        st.caption("식단과 운동 기록을 매일 누적하는 수룡이 다이어트 다이어리")

    st.divider()

    st.header("🐉 수룡이 알 키우기")
    st.caption("운동 기록으로 획득한 경험치(EXP)에 따라 진화하는 진짜 수룡이의 방입니다.")
    st.write("")

    exp = load_exp()
    level, level_name, suryong_img = get_level(exp)

    grow_col1, grow_col2 = st.columns([1, 1])
    with grow_col1:
        try:
            st.image(suryong_img, use_container_width=True)
        except:
            st.error(f"⚠️ 수룡이 이미지 파일('{suryong_img}')을 찾을 수 없습니다.")

    with grow_col2:
        st.subheader(f"현재 단계: {level_name}")
        if exp >= 220:
            st.progress(1.0)
            st.success("🎉 축하합니다! 전설의 수룡이가 완성되었습니다! 👑")
        else:
            next_goal = 50 if exp < 50 else 120 if exp < 120 else 220
            st.progress(exp / next_goal)
            st.write(f"📈 현재 누적 경험치: **{exp} EXP**")
            st.write(f"✨ 다음 진화까지 **{next_goal - exp} EXP** 남았어요.")

    st.divider()
    level_data = {
        "진화 단계": ["1단계", "2단계", "3단계", "4단계 (최종)"],
        "이름": ["🥚 알 수룡이", "🐣 아기 수룡이", "🐉 성장한 수룡이", "👑 전설의 수룡이"],
        "필요 EXP 범위": ["0 ~ 49 EXP", "50 ~ 119 EXP", "120 ~ 219 EXP", "220 EXP 이상"]
    }
    st.table(pd.DataFrame(level_data))

    st.divider()
    if st.checkbox("⚠️ 수룡이 경험치 초기화 활성화", key="reset_exp_check"):
        if st.button("💥 수룡이를 다시 알(🥚)로 되돌리기", type="primary", key="btn_reset_exp"):
            if os.path.exists(GROW_FILE):
                os.remove(GROW_FILE)
            st.warning("수룡이의 경험치가 완전히 초기화되었습니다! 페이지를 새로고침(F5) 해주세요.")


# --- 멀티페이지 내비게이션 구성 ---
pg = st.navigation([
    st.Page(show_main_page, title="📊 다이어트 다이어리", icon="📝"),
    st.Page(show_growth_page, title="🐉 수룡이 알 키우기", icon="🥚")
])
pg.run()
