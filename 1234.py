import streamlit as st
import pandas as pd
from datetime import datetime
import os
import calendar
import altair as alt

# 🚨 [중요] 최상단 고정 (에러 방지)
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

# 🏋️ [데이터베이스 고도화] 조건별 처방을 위한 기구 및 일반 종목 재정의
gym_details = {
    "상체": [
        {"name": "체스트 프레스 머신 (가슴)", "cal_10m": 60},
        {"name": "렛 풀 다운 (등)", "cal_10m": 55},
        {"name": "덤벨 숄더 프레스 (어깨)", "cal_10m": 55},
        {"name": "시티드 케이블 로우 (등)", "cal_10m": 50}
    ],
    "하체": [
        {"name": "레그 프레스 머신 (허벅지 전체)", "cal_10m": 70},
        {"name": "스미스머신 스쿼트 (하체 전체)", "cal_10m": 80},
        {"name": "레그 익스텐션 (허벅지 앞쪽)", "cal_10m": 55},
        {"name": "레그 컬 (허벅지 뒤쪽)", "cal_10m": 55}
    ],
    "헬스유산소": [
        {"name": "천국의 계단 (스텝밀)", "cal_10m": 100},
        {"name": "트레드밀 (러닝머신 인터벌)", "cal_10m": 75},
        {"name": "실내 싸이클 머신", "cal_10m": 65}
    ],
    "홈트_무산소": [
        {"name": "맨몸 스쿼트 / 런지", "cal_10m": 60},
        {"name": "플랭크 / 복근 크런치", "cal_10m": 50},
        {"name": "팔굽혀펴기 / 슬로우 버피", "cal_10m": 65}
    ],
    "홈트_유산소": [
        {"name": "줄넘기 (또는 제자리 뛰기)", "cal_10m": 100},
        {"name": "빠르게 걷기 / 파워 워킹", "cal_10m": 45},
        {"name": "가벼운 전신 실내 조깅", "cal_10m": 70},
        {"name": "스트레칭 및 요가", "cal_10m": 28}
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
        1. **목표 및 장소 설정**: `목표(근육증가/감량)`와 `오늘의 운동 장소(헬스장/홈트)`를 상황에 맞게 골라보세요.
        2. **식단 분석 확인**: 드신 음식을 선택하고 `✨ 오늘의 다이어트 및 운동 처방 보기`를 꾹 누릅니다.
        3. **상황별 맞춤 루틴 확인 (`🏃 AI 목표 시간 맞춤형 루틴` 탭)**:
           * **[헬스장 + 근육증가]** 일 때: AI가 **상체 세트 vs 하체 세트** 2가지 분할 패키지를 동시에 제안합니다! 골라서 수행하세요.
           * **[홈트]** 이거나 **[감량/유지]** 일 때: 복잡한 분할 없이 설정 시간에 맞춰 **"줄넘기 30분 + 스쿼트 20분"** 형태로 깔끔한 원코스 시간표를 짜줍니다.
        """)

    st.divider()

    profile = load_profile()

    st.header("👤 수정이 정보 입력")
    name = st.text_input("이름", value=profile.get("이름", "영범이의 아이들"))

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
    goal = st.selectbox("목표", goal_options, index=goal_options.index(profile.get("목표", "근육증가")))

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
            suryong_msg = "오늘 권장 칼로리를 초과했습니다! 웨이트 트레이닝을 더 열심히 해볼까요? 🔥"
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
            st.write("🤖 **수룡이 AI 헬스 트레이너의 고정 맞춤형 운동 처방**")

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
            target_total_time = st.slider("오늘은 총 몇 분 동안 운동을 진행하시겠습니까?", 15, 180, 50, step=5)

            st.divider()

            # --- [★ 핵심 분기 로직 개조 엔진 ★] ---
            # 오직 [헬스장] 이면서 [근육증가] 일 때만 기구 분할(상체 vs 하체) 패널 노출
            if ex_place == "헬스장" and goal == "근육증가":
                st.markdown(f"### 🎯 AI 헬스장 추천: 오늘 당신의 선택은? (상체 vs 하체 패키지 대기 중)")
                
                # 웨이트 75%, 유산소 25% 비율 분배
                weight_total_time = round(target_total_time * 0.75)
                cardio_total_time = target_total_time - weight_total_time
                
                st.info(f"💡 설정하신 {target_total_time}분 중 **근력 웨이트 {weight_total_time}분 + 마무리 유산소 {cardio_total_time}분**으로 정밀 타임 라인을 설계했습니다.")
                
                col_upper_page, col_lower_page = st.columns(2)
                
                with col_upper_page:
                    st.markdown("#### 💪 옵션 A: 오늘 상체 기구 루틴")
                    with st.container(border=True):
                        upper_list = gym_details["상체"]
                        time_per_ex = max(5, round(weight_total_time / len(upper_list)))
                        for item in upper_list:
                            st.markdown(f"**🔹 {item['name']}**")
                            st.markdown(f"  - ⏱️ 목표 소요: **{time_per_ex}분**")
                            st.markdown(f"  - 📊 가이드: **8~12회 $\\times$ 4세트** (세트 사이 1분 휴식)")
                        if cardio_total_time > 0:
                            st.markdown(f"**🏃 마무리 유산소 ({cardio_total_time}분)**")
                            st.markdown(f"  - 추천기구: `{gym_details['헬스유산소'][1]['name']}`")
                            
                with col_lower_page:
                    st.markdown("#### 🍗 옵션 B: 오늘 하체 기구 루틴")
                    with st.container(border=True):
                        lower_list = gym_details["하체"]
                        time_per_ex = max(5, round(weight_total_time / len(lower_list)))
                        for item in lower_list:
                            st.markdown(f"**🔸 {item['name']}**")
                            st.markdown(f"  - ⏱️ 목표 소요: **{time_per_ex}분**")
                            st.markdown(f"  - 📊 가이드: **8~12회 $\\times$ 4세트** (세트 사이 1분 30초 휴식)")
                        if cardio_total_time > 0:
                            st.markdown(f"**🏃 마무리 유산소 ({cardio_total_time}분)**")
                            st.markdown(f"  - 추천기구: `{gym_details['헬스유산소'][0]['name']}`")

            # 그 외의 모든 경우 (홈트레이닝 전체 혹은 헬스장이어도 감량/유지 목적일 때) -> 상하체 분할 없이 원코스로 깔끔 분배
            else:
                st.markdown(f"### 🏃 AI 맞춤형 원코스 타임라인 처방")
                
                # 목적 및 장소에 따른 최적의 2가지 종목 매칭 시스템
                if ex_place == "홈트":
                    st.info(f"🏠 홈트레이닝 환경에 맞게 상/하체 분할 없이 수행 가능한 **맨몸 근력 및 유산소** 복합 시간표를 짜드렸습니다.")
                    ex1_name = gym_details["홈트_유산소"][0]["name"] # 줄넘기
                    ex2_name = gym_details["홈트_무산소"][0]["name"] # 맨몸 스쿼트/런지
                    
                    # 6:4 비율 시간 분배
                    time_ex1 = round(target_total_time * 0.6)
                    time_ex2 = target_total_time - time_ex1
                else:
                    # 헬스장이지만 감량/유지 목적일 때
                    st.info(f"🎯 체지방 연소와 컨디션 관리에 맞춰 분할 루틴 대신 **유산소와 순환 운동** 중심 시간표를 구성했습니다.")
                    ex1_name = gym_details["헬스유산소"][1]["name"] # 트레드밀
                    ex2_name = gym_details["상체"][1]["name"] # 렛풀다운 같은 가벼운 웨이트 머신
                    
                    time_ex1 = round(target_total_time * 0.5)
                    time_ex2 = target_total_time - time_ex1

                # 가이드 박스 출력
                with st.container(border=True):
                    st.markdown(f"#### ⏱️ 오늘의 맞춤 고정 시간표 (총 {target_total_time}분 코스)")
                    st.markdown(f"**1️⃣ {ex1_name}** ➡️ ⏱️ **{time_ex1}분 동안 지속 수행**")
                    st.markdown(f"   * 안내: 일정한 페이스를 유지하며 땀이 밸 수 있도록 집중하세요.*")
                    st.markdown("")
                    st.markdown(f"**2️⃣ {ex2_name}** ➡️ ⏱️ **{time_ex2}분 동안 지속 수행**")
                    st.markdown(f"   * 안내: 무리하지 않는 선에서 정해진 타이머가 끝날 때까지 세트를 이어나가세요.*")

            st.divider()

            # --- [실제 수행 기록 정산기] ---
            st.subheader("🏋️ 오늘 실제로 완료한 운동 체크")
            st.caption("처방받은 타임라인을 참고하여, 실제로 진행을 완료한 종목들을 아래에서 선택해 칼로리를 연동해 보세요.")
            
            # 모든 종목을 풀에 통합하여 유저가 자유롭게 멀티 셀렉트 가능하도록 구성
            all_pool_options = (
                [ex["name"] for ex in gym_details["상체"]] + 
                [ex["name"] for ex in gym_details["하체"]] + 
                [ex["name"] for ex in gym_details["헬스유산소"]] +
                [ex["name"] for ex in gym_details["홈트_무산소"]] +
                [ex["name"] for ex in gym_details["홈트_유산소"]]
            )
            actual_done_list = st.multiselect("오늘 실제 끝마친 모든 운동을 체크하세요.", all_pool_options)
            
            actual_burned_calories = 0
            actual_time_sum = 0
            
            if actual_done_list:
                st.write("⏱️ **선택하신 기구 및 종목별 실제 진행 시간(분) 설정**")
                for ex_name in actual_done_list:
                    # 칼로리 계수 찾기 연산 자동화
                    cal_factor = 60 
                    for category in gym_details.values():
                        for item in category:
                            if item["name"] == ex_name:
                                cal_factor = item.get("cal_10m", 60)
                    
                    done_time = st.slider(f"[{ex_name}] 실제 진행 시간 (분 단위)", 0, 120, 20, key=f"dyn_time_{ex_name}")
                    actual_burned_calories += round((done_time / 10) * cal_factor)
                    actual_time_sum += done_time
                
                st.divider()
                st.subheader("🔥 당일 실전 운동 최종 정산 스코어")
                col_res1, col_res2 = st.columns(2)
                col_res1.metric("총 결산 운동 시간", f"{actual_time_sum} 분")
                col_res2.metric("수룡이 인증 소모 칼로리", f"{actual_burned_calories} kcal")
            else:
                st.info("운동을 하나 이상 체크하면 칼로리 정산용 시간 슬라이더와 저장 버튼이 활성화됩니다.")

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

                    st.success(f"🎉 맞춤 처방 기록 데이터베이스 세이브 성공! 수룡이 경험치가 10 EXP 상승했습니다.")

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
                    st.info("데이터를 계산하고 있습니다.")

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
