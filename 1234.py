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
LOGO_FILE = "icon.png"  # 로고 이미지 파일명


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

# 🏋️ [데이터셋 고도화] 유튜브 링크는 완전 '참고용' 링크로 격하, 자세한 타임라인은 AI가 독립적으로 생성
exercises_db = {
    "산책 / 가벼운 걷기": {"cal_10m": 30, "url": "https://youtu.be/MWnD6DhLjyc?si=-2IDpUQ8fYxQguKv", "type": "유산소", "place": "홈트", "intensity": "하", "target_goals": ["감량", "유지"]},
    "빠르게 걷기 (파워워킹)": {"cal_10m": 40, "url": "https://youtu.be/Me3IaZS3CdY?si=sGAMVjvBxPmokg01", "type": "유산소", "place": "홈트", "intensity": "중", "target_goals": ["감량", "유지"]},
    "가벼운 조깅 (러닝머신)": {"cal_10m": 75, "url": "https://youtu.be/O3GU4hMK75w?si=foZpMfnW9iu39OAP", "type": "유산소", "place": "헬스장", "intensity": "중", "target_goals": ["감량", "유지"]},
    "계단 오르기": {"cal_10m": 75, "url": "https://youtu.be/iRfeov-7KeQ?si=rW4bzFABsSlnhAM-", "type": "유산소", "place": "홈트", "intensity": "상", "target_goals": ["감량"]},
    "실내 자전거": {"cal_10m": 68, "url": "https://youtu.be/xEhPT6ydXRY?si=645qR1WgmixDdFRI", "type": "유산소", "place": "홈트", "intensity": "중", "target_goals": ["감량", "유지"]},
    "줄넘기": {"cal_10m": 100, "url": "https://youtu.be/7A_XOU4FkIk?si=-4SwZkx474jk-ARY", "type": "유산소", "place": "홈트", "intensity": "상", "target_goals": ["감량"]},
    "수영 (자유형)": {"cal_10m": 95, "url": "https://youtu.be/tVhe4wXsn5I?si=r7D7QuYyJgaLJ8zt", "type": "유산소", "place": "헬스장", "intensity": "상", "target_goals": ["감량", "유지"]},
    "스트레칭 / 요가": {"cal_10m": 28, "url": "https://youtu.be/Kk7TQGqQ3nA?si=_dSuiQeCyyB3Ojib", "type": "유산소", "place": "홈트", "intensity": "하", "target_goals": ["유지"]},
    "필라테스": {"cal_10m": 35, "url": "https://youtu.be/sb51gF18cYo?si=g65fbxnREHItwbQ-", "type": "무산소", "place": "홈트", "intensity": "중", "target_goals": ["감량", "유지"]},
    "웨이트 트레이닝 (헬스장 머신)": {"cal_10m": 55, "url": "https://youtu.be/e7fOcatby_k?si=GnUzZIBQ-DlMSXnx", "type": "무산소", "place": "헬스장", "intensity": "상", "target_goals": ["근육증가", "유지"]},
    "맨몸 스쿼트 / 런지": {"cal_10m": 60, "url": "https://youtu.be/Xcu271Ia720?si=o7ZDniBYeCamqRT2", "type": "무산소", "place": "홈트", "intensity": "중", "target_goals": ["근육증가", "감량", "유지"]},
    "플랭크 / 복근 운동": {"cal_10m": 50, "url": "https://youtu.be/USJgKSLxDRc?si=OAkWcADFXofRdvRg", "type": "무산소", "place": "홈트", "intensity": "중", "target_goals": ["근육증가", "유지"]},
    "팔굽혀펴기 / 상체 홈트": {"cal_10m": 55, "url": "https://youtu.be/XmxpYKKlokok?si=MjtgeJUSRYkRqTBV", "type": "무산소", "place": "홈트", "intensity": "중", "target_goals": ["근육증가"]},
    "버피 테스트": {"cal_10m": 100, "url": "https://youtu.be/UeVDx20Jbs8?si=XEXhU_FPG2yCr5zw", "type": "무산소", "place": "홈트", "intensity": "상", "target_goals": ["근육증가", "감량"]},
    "복싱": {"cal_10m": 95, "url": "https://youtu.be/p7IetTCzUUQ?si=Mco-GJrZ0NHMkAW_", "type": "유산소", "place": "헬스장", "intensity": "상", "target_goals": ["감량"]}
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

    # 🌟 [신규 추가] 직관적인 앱 간단 사용법 안내 박스
    with st.expander("💡 핏메이트 200% 활용하는 간단 사용법 보기", expanded=True):
        st.markdown("""
        1. **신체 정보 및 운동 목표 입력**: 성별, 체중 및 다이어트 **목표(감량/근육증가/유지)**를 선택하세요.
        2. **식단 입력**: 오늘 내가 먹은 음식을 다중 선택하면, 목표치 대비 현재 칼로리 상태가 실시간 분석됩니다.
        3. **처방 버튼 클릭**: 맨 아래 `✨ 오늘의 다이어트 및 운동 처방 보기`를 꾹 누르세요!
        4. **AI 맞춤형 시간 추천 루틴 확인**: `🏃 AI 목표 시간 맞춤형 루틴` 탭으로 이동한 뒤, **오늘 내가 운동할 총 시간**을 슬라이더로 조절하면 수룡이가 분 단위 개인 처방을 실시간으로 설계해 줍니다.
        5. **완료 기록 저장**: 실제 수행한 운동을 체크 및 저장하면 데이터베이스에 누적되고 수룡이가 성장합니다!
        """)

    st.divider()

    profile = load_profile()

    st.header("👤 수정이 정보 입력")
    name = st.text_input("이름", value=profile.get("이름", "영범이의 아이들"))

    gender_options = ["여자", "남자"]
    gender = st.selectbox(
        "성별", gender_options,
        index=gender_options.index(profile.get("성별", "여자"))
    )

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
    food_style = st.selectbox("선호 식단", food_style_options, index=food_style_options.index(profile.get("선호 식단", "한식")))

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
            st.write("🍏 **다이어트에 좋은 식단**")
            for food in selected_foods:
                if foods[food]["is_healthy"]:
                    st.write(f"- {food} ({foods[food]['calorie']} kcal)")
        with col_uh:
            st.write("😈 **다이어트를 방해하는 식단**")
            for food in selected_foods:
                if not foods[food]["is_healthy"]:
                    st.write(f"- {food} ({foods[food]['calorie']} kcal)")

    st.divider()

    st.subheader("💡 분석 및 맞춤 제안 받기")
    st.caption("정보 입력 및 오늘 먹은 음식 선택을 완료한 후 아래 버튼을 클릭하세요.")

    if "calc_submitted" not in st.session_state:
        st.session_state.calc_submitted = False

    if st.button("✨ 오늘의 다이어트 및 운동 처방 보기", type="primary"):
        st.session_state.calc_submitted = True

    if st.session_state.calc_submitted:
        st.header("🎮 수룡이의 오늘 식단 상태")

        if total == 0:
            suryong_img = "normal_suryong.jpg"
            suryong_msg = f"배가 고파요! 오늘 먹은 음식을 기록해주세요. 현재 BMI는 {user_bmi}입니다."
            status_color = "info"
        elif total < daily_calorie - 400:
            suryong_img = "slim_suryong.jpg"
            suryong_msg = "목표 칼로리에 비해 영양이 너무 부족해요! 수룡이가 기운 없이 홀쭉해졌어요. 🥺"
            status_color = "warning"
        elif total > daily_calorie + 150:
            suryong_img = "fat_suryong.jpg"
            suryong_msg = f"권장 목표 칼로리({daily_calorie}kcal)를 초과했어요! 수룡이가 포동포동해졌어요. 😭"
            status_color = "error"
        else:
            suryong_img = "normal_suryong.jpg"
            suryong_msg = "좋아요! 오늘 목표 칼로리에 딱 맞게 아주 건강하게 드셨네요! 👍"
            status_color = "success"

        col_char, col_info = st.columns([1, 1])
        with col_char:
            try:
                st.image(suryong_img, use_container_width=True)
            except:
                st.error(f"⚠️ 저장소에서 '{suryong_img}' 파일을 찾을 수 없습니다.")

        with col_info:
            st.subheader(f"🐲 {name if name else '사용자'}님의 수룡이 식단 체크")
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
            st.write("✨ **수룡이가 엄선한 건강한 다이어트 추천 메뉴**")
            recommended = [
                f for f in foods
                if foods[f]["type"] == food_style
                   and foods[f]["is_healthy"] == True
                   and (allergy == "없음" or allergy not in f)
                   and (dislike == "없음" or dislike not in f)
            ]
            if not recommended:
                st.warning(f"선택하신 '{food_style}' 카테고리에는 다이어트 전용 추천 식단이 없습니다. 대신 클린 식단을 제공합니다!")
                recommended = ["샐러드", "닭가슴살", "고구마", "계란", "현미밥"]

            for f in recommended:
                st.write(f"- {f}: {foods[f]['calorie']} kcal")

        with tab2:
            st.write("🤖 **수룡이 AI의 타임 슬라이스 개인 비서 처방**")

            # 환경 및 컨디션 입력 받기
            st.subheader("📋 오늘의 환경 및 신체 컨디션")
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1:
                select_date = st.date_input("기록 날짜", datetime.now().date())
            with col_ex2:
                ex_place = st.radio("오늘의 운동 장소", ["홈트", "헬스장"])
            with col_ex3:
                user_condition = st.selectbox("현재 나의 컨디션", ["최상 (에너지 넘침)", "정상 (보통)", "피곤함 (가벼운 운동 필요)", "근육통 있음"])

            st.write("")
            st.subheader("⏱️ 오늘 운동에 투자할 총 시간 설정")
            target_total_time = st.slider("오늘은 총 몇 분 동안 운동을 하고 싶으신가요?", 10, 180, 50, step=5)

            st.divider()

            # --- [AI 내부 필터링 및 시간 독립 매칭 엔진] ---
            # 1. 목표 타겟팅 기반 필터링 (골격근 증가 시 필라테스/요가 원천 차단)
            available_pool = {
                k: v for k, v in exercises_db.items() 
                if v["place"] == ex_place and goal in v["target_goals"]
            }
            
            # 2. 컨디션 필터링
            if user_condition in ["피곤함 (가벼운 운동 필요)", "근육통 있음"]:
                available_pool = {k: v for k, v in available_pool.items() if v["intensity"] != "상"}
            
            # 3. 유산소 / 무산소 풀 분리
            aerobic_pool = [k for k, v in available_pool.items() if v["type"] == "유산소"]
            anaerobic_pool = [k for k, v in available_pool.items() if v["type"] == "무산소"]

            st.subheader(f"🎯 AI가 추천하는 오늘의 정밀 분배 타임라인 루틴")
            
            routine_items = []

            # 🌟 [보완 완성] 영상 재생시간 매치 구조를 버리고 고정된 할당 시간에 완벽 대응하는 디테일 텍스트 가이드 생성
            def build_routine_guide(ex_name, allocated_time):
                url = exercises_db[ex_name]["url"]
                guide_text = f"정확히 **{allocated_time}분** 타이머를 맞춰 두고 페이스를 유지하며 끝까지 수행하세요."
                return (ex_name, guide_text, url, allocated_time)

            if goal == "감량":
                aerobic_time = round(target_total_time * 0.7)
                anaerobic_time = target_total_time - aerobic_time
                st.info(f"💡 목표가 **[감량]**이므로 입력하신 {target_total_time}분 중 **유산소 {aerobic_time}분 + 무산소 {anaerobic_time}분**으로 타임라인을 정밀 계산했습니다.")
                
                if aerobic_pool and aerobic_time > 0:
                    routine_items.append(build_routine_guide(aerobic_pool[0], aerobic_time))
                if anaerobic_pool and anaerobic_time > 0:
                    routine_items.append(build_routine_guide(anaerobic_pool[0], anaerobic_time))
                    
            elif goal == "근육증가":
                anaerobic_time = round(target_total_time * 0.7)
                aerobic_time = target_total_time - anaerobic_time
                st.info(f"💡 목표가 **[근육증가]**이므로 입력하신 {target_total_time}분 중 **무산소 {anaerobic_time}분 + 유산소 {aerobic_time}분**으로 구성했습니다. (필라테스/요가 완전 제외)")
                
                if anaerobic_pool and anaerobic_time > 0:
                    routine_items.append(build_routine_guide(anaerobic_pool[0], anaerobic_time))
                if aerobic_pool and aerobic_time > 0:
                    routine_items.append(build_routine_guide(aerobic_pool[0], aerobic_time))
                    
            else:  # 유지
                aerobic_time = round(target_total_time * 0.5)
                anaerobic_time = target_total_time - aerobic_time
                st.info(f"💡 목표가 **[유지]**이므로 입력하신 {target_total_time}분 중 **유산소 {aerobic_time}분 + 무산소 {anaerobic_time}분**을 5:5 밸런스로 나누었습니다.")
                
                if aerobic_pool and aerobic_time > 0:
                    routine_items.append(build_routine_guide(aerobic_pool[0], aerobic_time))
                if anaerobic_pool and anaerobic_time > 0:
                    routine_items.append(build_routine_guide(anaerobic_pool[0], anaerobic_time))

            # 처방 가이드박스 출력
            if routine_items:
                with st.container(border=True):
                    st.markdown(f"### 📋 수룡이 AI의 타임 슬롯 스포츠 처방")
                    for idx, (ex_title, guide_text, link_url, allocated_time) in enumerate(routine_items, 1):
                        st.markdown(f"**{idx}. {ex_title}** ➡️ ⏱️ **{allocated_time}분 동안 수행하기**")
                        st.markdown(f"   *안내: {guide_text}*")
                        st.markdown(f"   🔗 [자세나 동작 방법이 헷갈릴 때 참고할 영상 링크]({link_url})")
            else:
                st.warning("조건에 부합하는 정밀 운동 풀이 부족합니다. 다른 운동 장소나 컨디션을 선택해 보세요.")

            st.divider()

            # --- [실제 수행 기록 섹션] ---
            st.subheader("🏋️ 오늘 실제로 완료한 운동 기록하기")
            st.caption("추천 시간을 토대로 수행하셨거나, 개인 사정으로 조정하여 수행했을 수 있으니 실제 진행 완료한 타임을 입력하세요!")
            
            actual_done_list = st.multiselect("오늘 실제 수행 완료한 모든 종목을 자유롭게 선택하세요", list(exercises_db.keys()))
            
            actual_burned_calories = 0
            actual_time_sum = 0
            
            if actual_done_list:
                st.write("⏱️ **선택하신 운동별 실제 수행 시간(분)을 입력하세요**")
                for ex_name in actual_done_list:
                    cal_per_10m = exercises_db[ex_name]["cal_10m"]
                    
                    done_time = st.slider(f"[{ex_name}] 실제 몇 분 진행하셨나요?", 0, 150, 30, key=f"actual_time_{ex_name}")
                    
                    ex_burned = round((done_time / 10) * cal_per_10m)
                    actual_burned_calories += ex_burned
                    actual_time_sum += done_time
                
                st.divider()
                st.subheader("🔥 실제 운동 정산 스코어")
                col_res1, col_res2 = st.columns(2)
                col_res1.metric("오늘 실전 운동 시간", f"{actual_time_sum} 분")
                col_res2.metric("정산 소모 칼로리", f"{actual_burned_calories} kcal")
            else:
                st.info("오늘 완료한 운동 종목을 체크하시면 정산 칼로리 연동용 계산기가 활성화됩니다.")

            st.divider()
            st.subheader("💾 최종 운동 기록 세이브")
            if st.button("🔥 정산된 수치로 최종 저장하고 수룡이 경험치 받기"):
                if not actual_done_list:
                    st.error("실제로 수행한 운동이 선택되지 않았습니다. 리스트에서 체크해 주세요.")
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

                    st.success(f"🎉 {select_date.strftime('%m월 %d일')} 최종 실전 운동 데이터베이스 기록 세이브 완료!")

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
                            st.write("📅 **조회할 날짜 선택**")
                            selected_chart_date = st.selectbox(
                                "날짜를 클릭하세요", 
                                options=available_dates, 
                                index=len(available_dates)-1,
                                key="chart_date_selector"
                            )
                        
                        with chart_col1:
                            day_data = df_unique_dates[df_unique_dates["날짜_일만"] == selected_chart_date].iloc[0]
                            
                            plot_df = pd.DataFrame({
                                "구분": ["섭취 칼로리", "사용 칼로리"],
                                "칼로리(kcal)": [int(day_data["오늘 섭취량"]), int(day_data["운동 부위"])]
                            })
                            
                            custom_chart = alt.Chart(plot_df).mark_bar(size=40).encode(
                                x=alt.X("구분:N", title="데이터 분류", axis=alt.Axis(labelAngle=0)),
                                y=alt.Y("칼로리(kcal):Q", title="에너지 수치 (kcal)"),
                                color=alt.Color(
                                    "구분:N", 
                                    scale=alt.Scale(
                                        domain=["섭취 칼로리", "사용 칼로리"],
                                        range=["#1f77b4", "#aec7e8"]
                                    ),
                                    legend=alt.Legend(title="범례")
                                )
                            ).properties(
                                width="container",
                                height=320
                            )
                            
                            st.altair_chart(custom_chart, use_container_width=True)
                            st.caption(f"💡 선택된 일자 **[{selected_chart_date}]**의 식단 대비 운동 소모량 지표입니다.")
                except Exception as e:
                    st.info("데이터를 계산하고 있습니다. 기록을 한 번 더 등록하면 활성화됩니다.")

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
    
    st.subheader("📋 수룡이 진화 단계별 EXP 가이드")
    level_data = {
        "진화 단계": ["1단계", "2단계", "3단계", "4단계 (최종)"],
        "이름": ["🥚 알 수룡이", "🐣 아기 수룡이", "🐉 성장한 수룡이", "👑 전설의 수룡이"],
        "필요 EXP 범위": ["0 ~ 49 EXP", "50 ~ 119 EXP", "120 ~ 219 EXP", "220 EXP 이상"]
    }
    st.table(pd.DataFrame(level_data))

    st.divider()
    
    st.subheader("⚙️ 수룡이 성장방 관리")
    st.caption("수룡이의 레벨과 경험치를 처음부터 다시 시작하고 싶을 때 사용하세요.")
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
