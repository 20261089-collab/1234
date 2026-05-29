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

# 🏋️ [운동 데이터베이스]
gym_details = {
    "상체": [
        {
            "name": "체스트 프레스 머신 (가슴)", "cal_10m": 60,
            "tip": "엉덩이와 등 패드를 밀착하고 허리는 아치형을 만드세요. 바를 밀 때 숨을 내쉬고, 가슴 근육의 이완을 느끼며 천천히 받아줍니다."
        },
        {
            "name": "렛 풀 다운 (등)", "cal_10m": 55,
            "tip": "바를 쇄골 방향으로 당기면서 날개뼈를 아래로 접어줍니다. 팔 힘이 아니라 광배근으로 당긴다는 느낌에 집중하세요."
        },
        {
            "name": "덤벨 숄더 프레스 (어깨)", "cal_10m": 55,
            "tip": "덤벨을 귀 높이까지 내렸다가 정수리 위로 모아주듯 밀어 올립니다."
        },
        {
            "name": "시티드 케이블 로우 (등)", "cal_10m": 50,
            "tip": "발판을 지지하고 허리를 곧게 편 상태에서 그립을 배꼽 쪽으로 당깁니다."
        }
    ],
    "하체": [
        {
            "name": "레그 프레스 머신 (허벅지 전체)", "cal_10m": 70,
            "tip": "발판에 발을 어깨너비로 대고, 밀어낼 때 무릎을 100% 다 펴서 튕기지 않도록 약간 구부린 상태를 유지합니다."
        },
        {
            "name": "스미스머신 스쿼트 (하체 전체)", "cal_10m": 80,
            "tip": "바를 승모근에 안정적으로 얹고 무릎과 고관절을 동시에 접으며 앉습니다."
        },
        {
            "name": "레그 익스텐션 (허벅지 앞쪽)", "cal_10m": 55,
            "tip": "패드를 발목에 걸치고 허벅지 앞쪽 근육을 쥐어짜듯 다리를 올려줍니다."
        },
        {
            "name": "레그 컬 (허벅지 뒤쪽)", "cal_10m": 55,
            "tip": "엎드려서 발목 패드를 엉덩이 쪽으로 당겨 뒤쪽 허벅지를 수축합니다."
        }
    ],
    "접근성_유산소": [
        {"name": "줄넘기 (또는 제자리 가볍게 뛰기)", "cal_10m": 100},
        {"name": "실내 고정식 싸이클 자전거", "cal_10m": 65},
        {"name": "가벼운 실내 조깅 / 제자리 뛰기", "cal_10m": 70},
        {"name": "빠르게 걷기 / 파워 워킹", "cal_10m": 45},
        {"name": "트레드밀 (러닝머신)", "cal_10m": 75},
        {"name": "천국의 계단 (스텝밀)", "cal_10m": 100},
        {"name": "스트레칭 및 요가 릴렉스", "cal_10m": 28},
        {"name": "땅끄부부 칼소폭 매운맛 (유튜브)", "cal_10m": 90}
    ],
    "사용자_추가용_선택옵션": [
        {"name": "정통 복싱 / 미트치기 / 샌드백 타격", "cal_10m": 95},
        {"name": "크로스핏 WOD (고강도 와드)", "cal_10m": 110},
        {"name": "실내 클라이밍 (볼더링)", "cal_10m": 85},
        {"name": "체육관 배드민턴 랠리", "cal_10m": 70},
        {"name": "주짓수 / MMA 스파링", "cal_10m": 105},
        {"name": "스피닝 체육관 클래스", "cal_10m": 115}
    ]
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

    with st.expander("💡 핏메이트 개인 스마트 처방전 사용법 안내", expanded=True):
        st.markdown("""
        1. **목표 및 장소 설정**: 오늘 운동할 장소와 본인의 다이어트 목적을 올바르게 세팅해 주세요.
        2. **식단 분석 확인**: 식사 기록 후 `✨ 오늘의 다이어트 및 운동 처방 보기` 버튼을 누릅니다.
        3. **시간 분배 매칭 엔진 가동 (`🏃 AI 목표 시간 맞춤형 루틴` 탭)**:
           * **[헬스장 + 근육증가]**: 전문 웨이트 **상체 기구 vs 하체 기구** 분할 처방전이 나옵니다.
           * **[홈트 + 감량]**: **땅끄부부 20분 코스**가 명확한 설명과 함께 고정 출력되며, 남은 시간은 설정치에 맞춰 **줄넘기, 싸이클 등으로 1분 단위까지 정밀하게 합산(오버 시간 없음)**되어 노출됩니다. 순번 꼬임도 완벽하게 패치되었습니다.
        4. **개인 운동 추가 정산**: 복싱, 크로스핏 등 외부 스포츠는 제일 하단 **'오늘 실제로 완료한 운동 체크'** 풀에서 수동 정산 가능합니다.
        """)

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
                ex_place = st.radio("오늘의 운동 장소", ["헬스장", "홈트"])
            with col_ex3:
                user_condition = st.selectbox("현재 나의 컨디션", ["최상 (에너지 넘침)", "정상 (보통)", "피곤함 (가벼운 운동 필요)", "근육통 있음"])

            st.write("")
            st.subheader("⏱️ 오늘 운동에 투자할 총 시간 설정")
            # 홈트 최소 20분(땅끄영상용) 확보를 위해 min_value를 20으로 미세조정
            target_total_time = st.slider("오늘은 총 몇 분 동안 운동을 진행하시겠습니까?", 20, 180, 60, step=5)

            st.divider()

            # --- [정밀 타임 컨트롤 패치 엔진] ---
            if ex_place == "헬스장" and goal == "근육증가":
                st.markdown(f"### 🎯 AI 헬스장 기구 루틴 처방: 오늘 당신의 선택은?")
                
                weight_total_time = round(target_total_time * 0.75)
                cardio_total_time = target_total_time - weight_total_time
                
                st.info(f"💡 설정하신 {target_total_time}분 중 **근력 기구 웨이트 {weight_total_time}분 + 마무리 유산소 {cardio_total_time}분**으로 정밀 배분했습니다.")
                
                col_upper_page, col_lower_page = st.columns(2)
                
                with col_upper_page:
                    st.markdown("#### 💪 옵션 A: 오늘 상체 기구 루틴")
                    with st.container(border=True):
                        upper_list = gym_details["상체"]
                        time_per_ex = max(5, round(weight_total_time / len(upper_list)))
                        for item in upper_list:
                            st.markdown(f"**🔹 {item['name']}**")
                            st.markdown(f"  - ⏱️ 목표 소요: **{time_per_ex}분** (8~12회 $\\times$ 4세트)")
                            with st.expander("💡 기구 사용법 및 자극 꿀팁 보기"):
                                st.caption(item["tip"])
                        if cardio_total_time > 0:
                            st.markdown(f"**🏃 마무리 유산소 ({cardio_total_time}분)**")
                            st.markdown(f"  - 추천기구: `트레드밀 (러닝머신)`")
                            
                with col_lower_page:
                    st.markdown("#### 🍗 옵션 B: 오늘 하체 기구 루틴")
                    with st.container(border=True):
                        lower_list = gym_details["하체"]
                        time_per_ex = max(5, round(weight_total_time / len(lower_list)))
                        for item in lower_list:
                            st.markdown(f"**🔸 {item['name']}**")
                            st.markdown(f"  - ⏱️ 목표 소요: **{time_per_ex}분** (8~12회 $\\times$ 4세트)")
                            with st.expander("💡 기구 사용법 및 자극 꿀팁 보기"):
                                st.caption(item["tip"])
                        if cardio_total_time > 0:
                            st.markdown(f"**🏃 마무리 유산소 ({cardio_total_time}분)**")
                            st.markdown(f"  - 추천기구: `천국의 계단 (스텝밀)`")

            # FIX: [홈트 + 감량] 루틴 번호 스와핑 에러 및 시간 초과 현상 전면 수정 완료
            elif ex_place == "홈트" and goal == "감량":
                st.markdown(f"### 🏠 AI 홈트레이닝 다원화 유산소 처방")
                st.success(f"설정 시간인 **총 {target_total_time}분**에 1분 단위까지 완벽히 정수 매칭되도록 설계된 타임라인입니다.")
                
                video_time = 20
                remaining_time = max(0, target_total_time - video_time)
                
                with st.container(border=True):
                    st.markdown(f"#### ⏱️ 오늘의 세분화 유산소 타임라인 (정확히 총 {target_total_time}분 스케줄)")
                    
                    # 1번 고정: 땅끄부부 영상 매칭 설명 패치
                    st.markdown(f"**1️⃣ 땅끄부부 칼소폭 찐 핵핵핵 매운맛 (유튜브 영상)** ➡️ ⏱️ **{video_time}분 고정 수행**")
                    st.video("https://youtu.be/gSz5n4sLENI?si=rKzqg9K7mJ9hywMo")
                    
                    if remaining_time > 0:
                        if remaining_time <= 30:
                            # 잔여 시간 30분 이하면 순번 정상화 '2번' 단일 배치
                            st.markdown(f"**2️⃣ 줄넘기 (또는 제자리 가벼운 뛰기)** ➡️ ⏱️ **{remaining_time}분 지속**")
                        elif remaining_time <= 50:
                            # 잔여 시간 31~50분 사이면 2번, 3번 균등 배분 (시간 오버 방지)
                            time1 = round(remaining_time * 0.5)
                            time2 = remaining_time - time1
                            st.markdown(f"**2️⃣ 줄넘기 (또는 제자리 가볍게 뛰기)** ➡️ ⏱️ **{time1}분**")
                            st.markdown(f"**3️⃣ 실내 고정식 싸이클 자전거** ➡️ ⏱️ **{time2}분**")
                        else:
                            # 90분 등 긴 시간 설정 시, 순번 꼬임 패치 (1번 영상 -> 2번 싸이클 -> 3번 조깅 -> 4번 줄넘기)
                            # 비율에 맞춘 정확한 연산으로 총합이 무조건 target_total_time과 일치함
                            time1 = round(remaining_time * 0.4)
                            time2 = round(remaining_time * 0.35)
                            time3 = remaining_time - (time1 + time2)
                            
                            st.markdown(f"**2️⃣ 실내 고정식 싸이클 자전거** ➡️ ⏱️ **{time1}분**")
                            st.markdown(f"**3️⃣ 가벼운 실내 조깅 / 제자리 뛰기** ➡️ ⏱️ **{time2}분**")
                            st.markdown(f"**4️⃣ 줄넘기 (또는 스트레칭 마무리)** ➡️ ⏱️ **{time3}분**")
                            
                    st.caption(f"💡 [체크] 1번 영상({video_time}분) + 이후 세션들의 합계가 정확히 {target_total_time}분으로 조율되었습니다.")

            else:
                st.markdown(f"### 🏃 AI 접근성 중심 다단계 유산소 처방")
                st.info(f"누구나 쉽게 따라 할 수 있는 대중적인 유산소 종목들입니다. 총 {target_total_time}분에 맞춰 배분되었습니다.")
                
                with st.container(border=True):
                    st.markdown(f"#### ⏱️ 오늘의 유산소 스케줄 (총 {target_total_time}분)")
                    
                    if target_total_time <= 40:
                        time_part1 = round(target_total_time * 0.6)
                        time_part2 = target_total_time - time_part1
                        ex1 = "트레드밀 걷기" if ex_place == "헬스장" else "빠르게 걷기 / 파워 워킹"
                        ex2 = "실내 싸이클" if ex_place == "헬스장" else "스트레칭 및 요가 릴렉스"
                        st.markdown(f"**1️⃣ {ex1}** ➡️ ⏱️ **{time_part1}분**")
                        st.markdown(f"**2️⃣ {ex2}** ➡️ ⏱️ **{time_part2}분**")
                    else:
                        t1 = round(target_total_time * 0.4)
                        t2 = round(target_total_time * 0.35)
                        t3 = target_total_time - (t1 + t2)
                        
                        if ex_place == "헬스장":
                            st.markdown(f"**1️⃣ 트레드밀 (러닝머신)** ➡️ ⏱️ **{t1}분**")
                            st.markdown(f"**2️⃣ 실내 고정식 싸이클 자전거** ➡️ ⏱️ **{t2}분**")
                            st.markdown(f"**3️⃣ 천국의 계단 (스텝밀 마무리)** ➡️ ⏱️ **{t3}분**")
                        else:
                            st.markdown(f"**1️⃣ 실내 고정식 싸이클 자전거** ➡️ ⏱️ **{t1}분**")
                            st.markdown(f"**2️⃣ 가벼운 실내 조깅 / 제자리 뛰기** ➡️ ⏱️ **{t2}분**")
                            st.markdown(f"**3️⃣ 빠르게 걷기 및 스트레칭** ➡️ ⏱️ **{t3}분**")

            st.divider()

            # --- [실제 수행 기록 정산기] ---
            st.subheader("🏋️ 오늘 실제로 완료한 운동 체크")
            st.caption("AI가 자동 처방한 베이직 코스 외에도, 회원님이 외부 체육관 등에서 개인적으로 완료한 복싱, 크로스핏 같은 다이내믹 스포츠 종목들을 추가하여 칼로리를 반영해 보세요.")
            
            grand_pool = []
            for category in gym_details.values():
                for item in category:
                    if item["name"] not in grand_pool:
                        grand_pool.append(item["name"])
                        
            actual_done_list = st.multiselect("오늘 실제 마친 모든 운동을 리스트에서 선택해 주세요.", grand_pool)
            
            actual_burned_calories = 0
            actual_time_sum = 0
            
            if actual_done_list:
                st.write("⏱️ **선택하신 각 운동별 실제 수행 시간(분) 설정**")
                for ex_name in actual_done_list:
                    cal_factor = 60 
                    for category in gym_details.values():
                        for item in category:
                            if item["name"] == ex_name:
                                cal_factor = item.get("cal_10m", 60)
                    
                    done_time = st.slider(f"[{ex_name}] 실제 몇 분 하셨나요?", 0, 180, 30, key=f"v6_time_{ex_name}")
                    actual_burned_calories += round((done_time / 10) * cal_factor)
                    actual_time_sum += done_time
                
                st.divider()
                st.subheader("🔥 당일 실전 운동 최종 정산 스코어")
                col_res1, col_res2 = st.columns(2)
                col_res1.metric("총 결산 운동 시간", f"{actual_time_sum} 분")
                col_res2.metric("수룡이 인증 소모 칼로리", f"{actual_burned_calories} kcal")
            else:
                st.info("실제로 진행한 운동 항목을 체크하시면 정산 타이머와 저장 액션 패널이 활성화됩니다.")

            st.divider()
            st.subheader("💾 최종 운동 기록 세이브")
            if st.button("🔥 정산된 수치로 최종 저장하고 수룡이 경험치 받기"):
                if not actual_done_list:
                    st.error("실제로 수행한 운동 종목이 선택되지 않았습니다. 리스트에서 체크해 주세요.")
                else:
                    current_time_str = datetime.now().strftime("%H:%M")
                    formatted_date = f"{select_date.strftime('%Y-%m-%d')} {current_time_str}"
                    ex_summary = ", ".join(actual_done_list)

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

                    st.success(f"🎉 오늘의 맞춤 시간표 기록 세이브 성공! 경험치 10 EXP가 정상 지급되었습니다.")

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
                if st.checkbox("⚠️ 전체 기록 지우기"):
                    if st.button("정말 삭제하시겠습니까?"):
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
    if st.checkbox("⚠️ 수룡이 경험치 초기화 활성화"):
        if st.button("💥 수룡이를 다시 알(🥚)로 되돌리기", type="primary"):
            if os.path.exists(GROW_FILE):
                os.remove(GROW_FILE)
            st.warning("수룡이의 경험치가 완전히 초기화되었습니다! 페이지를 새로고침(F5) 해주세요.")


# --- 멀티페이지 내비게이션 구성 ---
pg = st.navigation([
    st.Page(show_main_page, title="📊 다이어트 다이어리", icon="📝"),
    st.Page(show_growth_page, title="🐉 수룡이 알 키우기", icon="🥚")
])
pg.run()
