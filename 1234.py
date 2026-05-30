import streamlit as st
import pandas as pd
from datetime import datetime
import os
import calendar
import altair as alt
import json

st.set_page_config(
    page_title="수룡이와 함께하는 맞춤형 다이어트",
    page_icon="🐉",
    layout="centered"
)

LOG_FILE = "diet_exercise_log.csv"
GROW_FILE = "suryong_growth.csv"
PROFILE_FILE = "user_profile.csv"
LOGO_FILE = "icon.png"


def calculate_bmi(weight, height):
    try:
        w = float(weight)
        h = float(height)
        if h <= 0:
            return 0.0
        return round(w / ((h / 100) ** 2), 1)
    except:
        return 0.0


def calculate_bmr_harris_benedict(weight, height, age, gender):
    try:
        w = float(weight)
        h = float(height)
        a = float(age)
        if gender == "남자":
            return round(66.47 + (13.75 * w) + (5.0 * h) - (6.76 * a), 1)
        return round(655.1 + (9.56 * w) + (1.85 * h) - (4.68 * a), 1)
    except:
        return 0.0


def calculate_tdee(bmr, activity):
    factors = {
        "거의 안 움직임": 1.2,
        "가벼운 활동": 1.375,
        "보통": 1.55,
        "활발함": 1.725,
        "매우 활발": 1.9
    }
    return round(float(bmr) * factors.get(activity, 1.2))


def get_level(exp):
    exp = int(exp)
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
        try:
            df = pd.read_csv(GROW_FILE)
            return int(df["경험치"].iloc[-1])
        except:
            return 0
    return 0


def save_exp(exp):
    pd.DataFrame([{"경험치": int(exp)}]).to_csv(
        GROW_FILE, index=False, encoding="utf-8-sig"
    )


def load_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            df = pd.read_csv(PROFILE_FILE)
            if not df.empty:
                data = df.iloc[-1].to_dict()
                for k, v in data.items():
                    if pd.isna(v):
                        data[k] = ""
                return data
        except:
            return {}
    return {}


def save_profile(profile):
    pd.DataFrame([profile]).to_csv(PROFILE_FILE, index=False, encoding="utf-8-sig")


foods = {
    "오트밀 + 바나나": {"calorie": 280, "is_healthy": True, "allergens": []},
    "현미밥 + 닭가슴살 + 구운 야채": {"calorie": 420, "is_healthy": True, "allergens": ["닭고기"]},
    "연어 아보카도 샐러드": {"calorie": 380, "is_healthy": True, "allergens": ["생선"]},
    "그릭요거트 + 블루베리 + 그래놀라": {"calorie": 310, "is_healthy": True, "allergens": ["우유", "밀"]},
    "곤약볶음밥 + 달걀후라이": {"calorie": 350, "is_healthy": True, "allergens": ["달걀", "대두"]},
    "통밀 식빵 샌드위치": {"calorie": 360, "is_healthy": True, "allergens": ["밀", "달걀"]},
    "소고기 부채살 + 버섯 구이": {"calorie": 590, "is_healthy": True, "allergens": ["쇠고기"]},
    "고구마 2개 + 샐러드": {"calorie": 420, "is_healthy": True, "allergens": []},
    "참치김밥": {"calorie": 500, "is_healthy": True, "allergens": ["생선", "달걀", "밀"]},
    "일반 김밥": {"calorie": 400, "is_healthy": True, "allergens": ["달걀", "밀"]},
    "떡볶이": {"calorie": 450, "is_healthy": False, "allergens": ["밀", "대두"]},
    "불닭볶음면": {"calorie": 530, "is_healthy": False, "allergens": ["밀", "대두"]},
    "마라탕": {"calorie": 600, "is_healthy": False, "allergens": ["밀", "대두", "쇠고기", "땅콩"]},
    "치즈케이크": {"calorie": 350, "is_healthy": False, "allergens": ["우유", "밀", "달걀"]},
    "아이스 아메리카노": {"calorie": 10, "is_healthy": True, "allergens": []},
    "제로 탄산음료": {"calorie": 0, "is_healthy": True, "allergens": []}
}


exercise_presets = {
    "홈트": {
        "감량": {
            "최상 (에너지 넘침)": [
                {"name": "고강도 전신 유산소", "cal_10m": 120, "guide": "20분 이상 고강도", "tip": "무릎에 무리 가지 않게 착지하세요."},
                {"name": "줄넘기", "cal_10m": 110, "guide": "인터벌 3세트", "tip": "발앞꿈치로 가볍게 뛰세요."}
            ],
            "정상 (보통)": [
                {"name": "전신 유산소 홈트", "cal_10m": 90, "guide": "표준 페이스", "tip": "끝까지 완주하는 것이 목표입니다."},
                {"name": "빠르게 걷기", "cal_10m": 55, "guide": "30분 지속", "tip": "호흡을 일정하게 유지하세요."}
            ],
            "피곤함 (가벼운 운동 필요)": [
                {"name": "가벼운 산책", "cal_10m": 40, "guide": "무리 없이 걷기", "tip": "회복 위주로 움직이세요."}
            ],
            "근육통 있음": [
                {"name": "전신 스트레칭", "cal_10m": 25, "guide": "부위별 30초", "tip": "반동 없이 천천히 늘리세요."}
            ]
        },
        "근육증가": {
            "최상 (에너지 넘침)": [
                {"name": "스쿼트", "cal_10m": 65, "guide": "5세트 × 20회", "tip": "무릎이 안쪽으로 말리지 않게 하세요."},
                {"name": "푸쉬업", "cal_10m": 55, "guide": "5세트 × 15회", "tip": "몸을 일직선으로 유지하세요."}
            ],
            "정상 (보통)": [
                {"name": "스쿼트", "cal_10m": 60, "guide": "4세트 × 15회", "tip": "발뒤꿈치에 체중을 실으세요."},
                {"name": "플랭크", "cal_10m": 45, "guide": "3세트 × 45초", "tip": "허리가 처지지 않게 하세요."}
            ],
            "피곤함 (가벼운 운동 필요)": [
                {"name": "벽 푸쉬업", "cal_10m": 35, "guide": "3세트 × 12회", "tip": "관절 부담을 줄여 진행하세요."}
            ],
            "근육통 있음": [
                {"name": "요가 스트레칭", "cal_10m": 25, "guide": "15분 호흡", "tip": "회복에 집중하세요."}
            ]
        }
    }
}


gym_split_presets = {
    "최상 (에너지 넘침)": {
        "상체": [
            {"name": "렛 풀 다운", "cal_10m": 65, "guide": "5세트 × 10회", "tip": "등으로 당기는 느낌을 잡으세요."},
            {"name": "체스트 프레스", "cal_10m": 65, "guide": "5세트 × 12회", "tip": "가슴 근육 수축에 집중하세요."}
        ],
        "하체": [
            {"name": "레그 프레스", "cal_10m": 85, "guide": "5세트 × 12회", "tip": "무릎을 끝까지 잠그지 마세요."},
            {"name": "레그 익스텐션", "cal_10m": 55, "guide": "4세트 × 15회", "tip": "반동 없이 천천히 올리세요."}
        ],
        "유산소": [
            {"name": "천국의 계단", "cal_10m": 110, "guide": "속도 7~9", "tip": "상체를 살짝 숙여 둔근을 사용하세요."}
        ]
    },
    "정상 (보통)": {
        "상체": [
            {"name": "렛 풀 다운", "cal_10m": 55, "guide": "4세트 × 12회", "tip": "상체를 과하게 젖히지 마세요."},
            {"name": "체스트 프레스", "cal_10m": 55, "guide": "4세트 × 12회", "tip": "가슴 중앙 자극에 집중하세요."}
        ],
        "하체": [
            {"name": "레그 프레스", "cal_10m": 70, "guide": "4세트 × 15회", "tip": "허리가 뜨지 않게 하세요."}
        ],
        "유산소": [
            {"name": "실내 자전거", "cal_10m": 65, "guide": "RPM 70 유지", "tip": "무릎에 충격 없이 굴리세요."}
        ]
    },
    "피곤함 (가벼운 운동 필요)": {
        "상체": [
            {"name": "저중량 렛 풀 다운", "cal_10m": 45, "guide": "3세트 × 12회", "tip": "무게보다 자세에 집중하세요."}
        ],
        "하체": [
            {"name": "저중량 레그 프레스", "cal_10m": 50, "guide": "3세트 × 12회", "tip": "관절 부담을 줄이세요."}
        ],
        "유산소": [
            {"name": "트레드밀 걷기", "cal_10m": 50, "guide": "속도 4.5", "tip": "가볍게 땀이 날 정도로만 하세요."}
        ]
    },
    "근육통 있음": {
        "상체": [
            {"name": "상체 스트레칭", "cal_10m": 25, "guide": "15분 이완", "tip": "통증 부위는 무리하지 마세요."}
        ],
        "하체": [
            {"name": "하체 스트레칭", "cal_10m": 25, "guide": "부위별 30초", "tip": "천천히 호흡하세요."}
        ],
        "유산소": [
            {"name": "가벼운 산책", "cal_10m": 35, "guide": "편안한 페이스", "tip": "회복 목적입니다."}
        ]
    }
}


def show_main_page():
    logo_col, title_col = st.columns([1, 4])

    with logo_col:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_container_width=True)
        else:
            st.info("🐉 LOGO")

    with title_col:
        st.title("핏메이트")
        st.caption("목적별 맞춤 식단과 스마트 운동 루틴을 제공하는 다이어트 다이어리")

    st.divider()

    profile = load_profile()

    st.header("👤 사용자 정보 입력")

    name = st.text_input("이름", value=str(profile.get("이름", "")))

    gender_options = ["여자", "남자"]
    saved_gender = profile.get("성별", "여자")
    gender = st.selectbox(
        "성별",
        gender_options,
        index=gender_options.index(saved_gender) if saved_gender in gender_options else 0
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("나이", min_value=1, step=1, value=int(profile.get("나이", 20)))

    with col2:
        height = st.number_input("키(cm)", min_value=1.0, value=float(profile.get("키(cm)", 165.0)))

    with col3:
        weight = st.number_input("몸무게(kg)", min_value=1.0, value=float(profile.get("몸무게(kg)", 55.0)))

    activity_options = ["거의 안 움직임", "가벼운 활동", "보통", "활발함", "매우 활발"]
    saved_activity = profile.get("활동량", "보통")
    activity = st.selectbox(
        "활동량",
        activity_options,
        index=activity_options.index(saved_activity) if saved_activity in activity_options else 2
    )

    goal_options = ["감량", "유지", "근육증가"]
    saved_goal = profile.get("목표", "감량")
    goal = st.selectbox(
        "현재 나의 목표",
        goal_options,
        index=goal_options.index(saved_goal) if saved_goal in goal_options else 0
    )

    allergy_options = ["밀", "달걀", "우유", "대두", "생선", "조개류", "갑각류(새우/게)", "닭고기", "돼지고기", "쇠고기", "땅콩"]

    saved_allergies_raw = profile.get("알레르기 음식", "[]")
    selected_allergies = []

    if isinstance(saved_allergies_raw, str):
        try:
            selected_allergies = json.loads(saved_allergies_raw)
            if not isinstance(selected_allergies, list):
                selected_allergies = []
        except:
            selected_allergies = []

    user_selected_allergies = st.multiselect(
        "해당하는 알레르기 음식을 선택해 주세요",
        allergy_options,
        default=[x for x in selected_allergies if x in allergy_options]
    )

    save_profile({
        "이름": name,
        "성별": gender,
        "나이": age,
        "키(cm)": height,
        "몸무게(kg)": weight,
        "활동량": activity,
        "목표": goal,
        "알레르기 음식": json.dumps(user_selected_allergies, ensure_ascii=False)
    })

    user_bmi = calculate_bmi(weight, height)
    user_bmr = calculate_bmr_harris_benedict(weight, height, age, gender)
    user_tdee = calculate_tdee(user_bmr, activity)

    if goal == "감량":
        daily_calorie = user_tdee - 350
    elif goal == "근육증가":
        daily_calorie = user_tdee + 300
    else:
        daily_calorie = user_tdee

    st.divider()

    st.header(f"🍱 오늘의 목표 [{goal}] 맞춤 추천 식단")

    safe_food_pool = []
    for food_name, info in foods.items():
        allergens = info.get("allergens", [])
        if not any(alg in allergens for alg in user_selected_allergies):
            safe_food_pool.append(food_name)

    if goal == "감량":
        breakfast_food = "오트밀 + 바나나"
        lunch_food = "현미밥 + 닭가슴살 + 구운 야채"
        dinner_food = "연어 아보카도 샐러드"
        st.caption("🔥 탄수화물과 지방을 줄인 고단백 클린 다이어트 조합")
    elif goal == "유지":
        breakfast_food = "그릭요거트 + 블루베리 + 그래놀라"
        lunch_food = "참치김밥"
        dinner_food = "곤약볶음밥 + 달걀후라이"
        st.caption("🥗 일상을 지속하기 쉬운 웰빙 일반식 조합")
    else:
        breakfast_food = "통밀 식빵 샌드위치"
        lunch_food = "소고기 부채살 + 버섯 구이"
        dinner_food = "고구마 2개 + 샐러드"
        st.caption("💪 근육 성장을 위한 고단백 에너지 식단")

    if breakfast_food not in safe_food_pool:
        breakfast_food = safe_food_pool[0] if safe_food_pool else "아이스 아메리카노"
    if lunch_food not in safe_food_pool:
        lunch_food = safe_food_pool[0] if safe_food_pool else "아이스 아메리카노"
    if dinner_food not in safe_food_pool:
        dinner_food = safe_food_pool[0] if safe_food_pool else "아이스 아메리카노"

    bf_cal = foods[breakfast_food]["calorie"]
    lc_cal = foods[lunch_food]["calorie"]
    dn_cal = foods[dinner_food]["calorie"]

    r_col1, r_col2, r_col3 = st.columns(3)

    with r_col1:
        st.markdown("### 🌅 아침")
        st.info(f"**{breakfast_food}**\n\n{bf_cal} kcal")
        chk_breakfast = st.checkbox("아침 추천대로 먹었어요", key="chk_bf")

    with r_col2:
        st.markdown("### ☀️ 점심")
        st.success(f"**{lunch_food}**\n\n{lc_cal} kcal")
        chk_lunch = st.checkbox("점심 추천대로 먹었어요", key="chk_lc")

    with r_col3:
        st.markdown("### 🌌 저녁")
        st.warning(f"**{dinner_food}**\n\n{dn_cal} kcal")
        chk_dinner = st.checkbox("저녁 추천대로 먹었어요", key="chk_dn")

    st.divider()

    st.header("🍽️ 오늘 먹은 음식 기록")
    selected_foods = st.multiselect("추가로 먹은 음식을 골라주세요.", list(foods.keys()))

    custom_food_name = st.text_input("리스트에 없는 음식 이름", placeholder="예: 엄마표 닭도리탕")
    custom_food_cal = st.number_input("직접 입력 음식 칼로리(kcal)", min_value=0, step=5, value=0)

    total = 0
    checked_items_summary = []

    if chk_breakfast:
        total += bf_cal
        checked_items_summary.append(f"{breakfast_food}(아침)")
    if chk_lunch:
        total += lc_cal
        checked_items_summary.append(f"{lunch_food}(점심)")
    if chk_dinner:
        total += dn_cal
        checked_items_summary.append(f"{dinner_food}(저녁)")

    for food in selected_foods:
        total += foods[food]["calorie"]

    if custom_food_name and custom_food_cal > 0:
        total += custom_food_cal

    st.divider()

    if st.button("✨ 오늘의 다이어트 및 운동 처방 보기", type="primary"):
        st.session_state.calc_submitted = True

    if "calc_submitted" not in st.session_state:
        st.session_state.calc_submitted = False

    if st.session_state.calc_submitted:
        st.header("🎮 수룡이의 오늘 식단 상태")

        if total == 0:
            suryong_img = "normal_suryong.jpg"
            suryong_msg = f"오늘 식사를 기록해 주세요! 현재 BMI는 {user_bmi}입니다."
            status_color = "info"
        elif total < daily_calorie - 350:
            suryong_img = "slim_suryong.jpg"
            suryong_msg = "너무 적게 먹었어요. 건강하게 챙겨 먹어야 해요! 🥺"
            status_color = "warning"
        elif total > daily_calorie + 150:
            suryong_img = "fat_suryong.jpg"
            suryong_msg = "오늘 목표치를 초과했어요. 운동 루틴으로 칼로리를 태워봐요! 🔥"
            status_color = "error"
        else:
            suryong_img = "normal_suryong.jpg"
            suryong_msg = "칼로리 밸런스가 좋아요! 👍"
            status_color = "success"

        char_col, info_col = st.columns([1, 1])

        with char_col:
            if os.path.exists(suryong_img):
                st.image(suryong_img, use_container_width=True)
            else:
                st.info("🐉 수룡이 이미지")

        with info_col:
            st.subheader(f"🐲 {name if name else '사용자'}님의 당일 영양 스코어")
            if status_color == "info":
                st.info(suryong_msg)
            elif status_color == "warning":
                st.warning(suryong_msg)
            elif status_color == "error":
                st.error(suryong_msg)
            else:
                st.success(suryong_msg)

            st.metric("나의 BMI 지수", str(user_bmi))
            st.metric("나의 기초대사량(BMR)", f"{user_bmr} kcal")
            st.metric("나의 활동대사량(TDEE)", f"{user_tdee} kcal")

            with st.expander("💡 왜 기초대사량보다 권장 칼로리가 높을까요?"):
                st.markdown(
                    """
                    <div style="color:#666; line-height:1.6;">
                    <b>기초대사량(BMR)</b>은 생존에 필요한 최소 에너지이고,
                    <b>활동대사량(TDEE)</b>은 일상 활동과 운동까지 포함한 실제 하루 소모 에너지입니다.
                    그래서 권장 칼로리는 보통 기초대사량보다 높게 계산됩니다.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.metric("오늘의 목표 권장 칼로리", f"{int(daily_calorie)} kcal")
            st.metric("현재 총 섭취량", f"{int(total)} kcal", delta=int(total - daily_calorie), delta_color="inverse")

        st.divider()

        tab1, tab2 = st.tabs(["🏃 AI 맞춤 운동 루틴", "📅 나의 누적 다이어트 일지"])

        with tab1:
            st.subheader("📋 오늘의 운동 환경 및 컨디션")

            col_ex1, col_ex2, col_ex3 = st.columns(3)

            with col_ex1:
                select_date = st.date_input("기록 날짜", datetime.now().date())

            with col_ex2:
                ex_place = st.radio("운동 장소", ["헬스장", "홈트"], key="ex_place")

            with col_ex3:
                user_condition = st.selectbox(
                    "현재 컨디션",
                    ["최상 (에너지 넘침)", "정상 (보통)", "피곤함 (가벼운 운동 필요)", "근육통 있음"]
                )

            muscle_gym_part = "상체만 진행"

            if ex_place == "헬스장" and goal == "근육증가":
                muscle_gym_part = st.radio(
                    "운동 부위 선택",
                    ["상체만 진행", "하체만 진행"],
                    horizontal=True
                )

            target_total_time = st.slider("오늘 운동할 총 시간", 20, 180, 50, step=5)

            if user_condition == "최상 (에너지 넘침)":
                condition_multiplier = 1.2
                st.success("컨디션 최상! 강도 높은 루틴을 추천합니다.")
            elif user_condition == "정상 (보통)":
                condition_multiplier = 1.0
                st.info("정상 컨디션! 표준 루틴을 추천합니다.")
            else:
                condition_multiplier = 0.8
                st.warning("회복 모드! 무리 없는 루틴을 추천합니다.")

            ai_prescribed_exercises = []
            ai_prescribed_calories = 0

            if ex_place == "홈트":
                sub_goal = "근육증가" if goal == "근육증가" else "감량"
                current_pool = exercise_presets["홈트"][sub_goal].get(
                    user_condition,
                    exercise_presets["홈트"][sub_goal]["정상 (보통)"]
                )
            else:
                pool_dict = gym_split_presets.get(user_condition, gym_split_presets["정상 (보통)"])

                if goal == "근육증가":
                    if muscle_gym_part == "상체만 진행":
                        current_pool = pool_dict.get("상체", [])
                    else:
                        current_pool = pool_dict.get("하체", [])
                else:
                    current_pool = pool_dict.get("유산소", [])

            if not current_pool:
                st.warning("추천 운동 데이터가 부족합니다.")
            else:
                time_per_ex = max(5, round(target_total_time / len(current_pool)))

                for idx, item in enumerate(current_pool):
                    st.markdown("---")
                    st.markdown(f"### {idx + 1}. {item['name']}")
                    st.write(f"⏱️ 추천 시간: **{time_per_ex}분**")
                    st.write(f"📊 수행 가이드: **{item['guide']}**")

                    with st.expander("💡 운동 팁"):
                        st.caption(item["tip"])

                    ai_prescribed_exercises.append(item["name"])
                    ai_prescribed_calories += round((time_per_ex / 10) * item["cal_10m"] * condition_multiplier)

            st.divider()

            st.subheader("🏋️ 오늘 실제로 완료한 운동 체크")

            use_ai_routine = st.checkbox("AI 추천 루틴을 그대로 완료했습니다!")

            actual_burned_calories = 0
            actual_time_sum = 0
            ex_summary = ""

            if use_ai_routine:
                actual_time_sum = target_total_time
                actual_burned_calories = ai_prescribed_calories
                ex_summary = f"[{user_condition}/{goal}] " + ", ".join(ai_prescribed_exercises)
                st.info(f"총 {actual_time_sum}분 운동, 약 {actual_burned_calories} kcal 소모로 계산됩니다.")
            else:
                actual_done_list = st.multiselect(
                    "직접 완료한 운동을 선택하세요.",
                    ["렛 풀 다운", "체스트 프레스", "레그 프레스", "스쿼트", "천국의 계단", "트레드밀", "전신 홈트", "스트레칭"]
                )

                if actual_done_list:
                    for ex_name in actual_done_list:
                        done_time = st.slider(f"{ex_name} 수행 시간(분)", 0, 180, 15, key=f"time_{ex_name}")
                        actual_burned_calories += round((done_time / 10) * 65 * condition_multiplier)
                        actual_time_sum += done_time
                    ex_summary = f"[{user_condition}/수동] " + ", ".join(actual_done_list)

            if actual_time_sum > 0:
                col_res1, col_res2 = st.columns(2)
                col_res1.metric("총 운동 시간", f"{int(actual_time_sum)} 분")
                col_res2.metric("예상 소모 칼로리", f"{int(actual_burned_calories)} kcal")

            st.divider()

            if st.button("🔥 최종 저장하고 수룡이 경험치 받기"):
                if actual_time_sum <= 0:
                    st.error("완료한 운동이 없습니다.")
                else:
                    current_time_str = datetime.now().strftime("%H:%M")
                    formatted_date = f"{select_date.strftime('%Y-%m-%d')} {current_time_str}"

                    food_log_text = ", ".join(checked_items_summary + selected_foods)
                    if custom_food_name:
                        food_log_text += f" | [직접입력] {custom_food_name}({custom_food_cal}kcal)"

                    new_data = {
                        "날짜": formatted_date,
                        "이름": name if name else "사용자",
                        "체중(kg)": weight,
                        "BMI": user_bmi,
                        "목표 칼로리": daily_calorie,
                        "오늘 섭취량": total,
                        "섭취 음식": food_log_text,
                        "수행한 운동 조합": ex_summary,
                        "소비 칼로리(kcal)": actual_burned_calories,
                        "수행 시 컨디션": user_condition,
                        "운동 시간(분)": actual_time_sum
                    }

                    df = pd.read_csv(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame(columns=new_data.keys())
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

                    old_exp = load_exp()
                    gained_exp = 10
                    new_exp = old_exp + gained_exp
                    save_exp(new_exp)

                    old_level, old_level_name, _ = get_level(old_exp)
                    new_level, new_level_name, _ = get_level(new_exp)

                    st.success(f"🎉 저장 완료! 경험치 {gained_exp} EXP가 지급되었습니다.")

                    if new_level > old_level:
                        st.balloons()
                        st.success(f"🎊 수룡이 진화 성공! {old_level_name} → {new_level_name}")

        with tab2:
            show_log_page()


def show_log_page():
    st.write("📅 **나의 누적 다이어트 일지**")

    if os.path.exists(LOG_FILE):
        try:
            df_log = pd.read_csv(LOG_FILE)

            if "오늘 섭취량" in df_log.columns:
                df_log["오늘 섭취량"] = pd.to_numeric(df_log["오늘 섭취량"], errors="coerce").fillna(0)
            if "소비 칼로리(kcal)" in df_log.columns:
                df_log["소비 칼로리(kcal)"] = pd.to_numeric(df_log["소비 칼로리(kcal)"], errors="coerce").fillna(0)
            if "운동 시간(분)" in df_log.columns:
                df_log["운동 시간(분)"] = pd.to_numeric(df_log["운동 시간(분)"], errors="coerce").fillna(0)

            st.dataframe(df_log.iloc[::-1], use_container_width=True)

            st.subheader("📊 나의 다이어트 요약")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("총 기록 수", f"{len(df_log)} 회")
            c2.metric("평균 섭취 칼로리", f"{int(df_log['오늘 섭취량'].mean())} kcal")
            c3.metric("평균 운동 소모", f"{int(df_log['소비 칼로리(kcal)'].mean())} kcal")
            c4.metric("누적 운동 시간", f"{int(df_log['운동 시간(분)'].sum())} 분")

            st.divider()

            st.subheader("📊 일자별 섭취량 vs 운동 소모량 비교")

            df_log["날짜"] = pd.to_datetime(df_log["날짜"], errors="coerce")
            df_log = df_log.dropna(subset=["날짜"])
            df_log["날짜_일만"] = df_log["날짜"].dt.strftime("%Y-%m-%d")

            df_unique_dates = df_log.groupby("날짜_일만")[["오늘 섭취량", "소비 칼로리(kcal)"]].sum().reset_index()
            available_dates = df_unique_dates["날짜_일만"].tolist()

            if available_dates:
                selected_chart_date = st.selectbox("날짜 선택", available_dates, index=len(available_dates) - 1)

                day_data = df_unique_dates[df_unique_dates["날짜_일만"] == selected_chart_date].iloc[0]

                plot_df = pd.DataFrame({
                    "구분": ["섭취 칼로리", "사용 칼로리"],
                    "칼로리(kcal)": [int(day_data["오늘 섭취량"]), int(day_data["소비 칼로리(kcal)"])]
                })

                chart = alt.Chart(plot_df).mark_bar(size=40).encode(
                    x=alt.X("구분:N", title="구분"),
                    y=alt.Y("칼로리(kcal):Q", title="칼로리"),
                    color=alt.Color("구분:N", legend=alt.Legend(title="범례"))
                ).properties(height=320)

                st.altair_chart(chart, use_container_width=True)

            st.divider()

            st.subheader("🗓️ 월별 운동 캘린더")

            if len(df_log) > 0:
                latest_date = df_log["날짜"].max()
                years = sorted(df_log["날짜"].dt.year.unique())

                cal_col1, cal_col2 = st.columns(2)

                with cal_col1:
                    selected_year = st.selectbox(
                        "연도 선택",
                        years,
                        index=years.index(latest_date.year) if latest_date.year in years else 0
                    )

                with cal_col2:
                    selected_month = st.selectbox(
                        "월 선택",
                        list(range(1, 13)),
                        index=latest_date.month - 1
                    )

                month_data = df_log[
                    (df_log["날짜"].dt.year == selected_year) &
                    (df_log["날짜"].dt.month == selected_month)
                ]

                exercise_days = set(month_data["날짜"].dt.day)
                cal = calendar.monthcalendar(selected_year, selected_month)

                st.write(f"📅 {selected_year}년 {selected_month}월")

                days_kor = ["월", "화", "수", "목", "금", "토", "일"]
                header = st.columns(7)

                for i, d in enumerate(days_kor):
                    header[i].markdown(f"**{d}**")

                for week in cal:
                    cols = st.columns(7)
                    for i, day in enumerate(week):
                        if day == 0:
                            cols[i].write("")
                        elif day in exercise_days:
                            cols[i].markdown(f"🟢 **{day}**")
                        else:
                            cols[i].markdown(f"{day}")

            st.divider()

            if st.checkbox("⚠️ 전체 기록 지우기"):
                if st.button("정말 삭제하시겠습니까?"):
                    os.remove(LOG_FILE)
                    st.warning("모든 기록이 삭제되었습니다. 새로고침 해주세요.")

        except Exception as e:
            st.error("기록을 불러오는 중 문제가 발생했습니다.")
            st.write(e)

    else:
        st.info("아직 저장된 다이어트 일지가 없습니다.")


def show_growth_page():
    logo_col, title_col = st.columns([1, 4])

    with logo_col:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_container_width=True)
        else:
            st.info("🐉 LOGO")

    with title_col:
        st.title("핏메이트")
        st.caption("운동 기록으로 수룡이를 성장시키는 다이어트 게임")

    st.divider()

    st.header("🐉 수룡이 알 키우기")

    exp = load_exp()
    level, level_name, suryong_img = get_level(exp)

    grow_col1, grow_col2 = st.columns([1, 1])

    with grow_col1:
        if os.path.exists(suryong_img):
            st.image(suryong_img, use_container_width=True)
        else:
            st.error(f"⚠️ 수룡이 이미지 파일 '{suryong_img}'을 찾을 수 없습니다.")

    with grow_col2:
        st.subheader(f"현재 단계: {level_name}")

        if exp >= 220:
            st.progress(1.0)
            st.success("🎉 축하합니다! 전설의 수룡이가 완성되었습니다!")
        else:
            next_goal = 50 if exp < 50 else 120 if exp < 120 else 220
            st.progress(exp / next_goal)
            st.write(f"📈 현재 누적 경험치: **{exp} EXP**")
            st.write(f"✨ 다음 진화까지 **{next_goal - exp} EXP** 남았어요.")

    st.divider()

    level_data = {
        "진화 단계": ["1단계", "2단계", "3단계", "4단계"],
        "이름": ["🥚 알 수룡이", "🐣 아기 수룡이", "🐉 성장한 수룡이", "👑 전설의 수룡이"],
        "필요 EXP": ["0~49", "50~119", "120~219", "220 이상"]
    }

    st.table(pd.DataFrame(level_data))

    st.divider()

    if st.checkbox("⚠️ 수룡이 경험치 초기화"):
        if st.button("💥 수룡이를 다시 알로 되돌리기"):
            if os.path.exists(GROW_FILE):
                os.remove(GROW_FILE)
            st.warning("수룡이 경험치가 초기화되었습니다. 새로고침 해주세요.")


page = st.sidebar.radio(
    "페이지 선택",
    ["📊 다이어트 다이어리", "🐉 수룡이 알 키우기"]
)

if page == "📊 다이어트 다이어리":
    show_main_page()
else:
    show_growth_page()
