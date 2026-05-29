import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="수룡이와 함께하는 맞춤형 다이어트",
    page_icon="🐉",
    layout="centered"
)

LOG_FILE = "diet_exercise_log.csv"
GROW_FILE = "suryong_growth.csv"

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
        return 1, "🥚 알 수룡이", "아직 알 속에서 건강 습관을 배우는 중이에요."
    elif exp < 120:
        return 2, "🐣 아기 수룡이", "운동 습관이 생기면서 아기 수룡이로 성장했어요!"
    elif exp < 220:
        return 3, "🐉 청소년 수룡이", "꾸준한 운동으로 점점 강해지고 있어요!"
    else:
        return 4, "👑 성체 수룡이", "완벽한 건강 습관을 가진 멋진 성체 수룡이예요!"

def load_exp():
    if os.path.exists(GROW_FILE):
        df = pd.read_csv(GROW_FILE)
        return int(df["경험치"].iloc[-1])
    return 0

def save_exp(exp):
    df = pd.DataFrame([{"경험치": exp}])
    df.to_csv(GROW_FILE, index=False, encoding="utf-8-sig")

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

st.title("🐉 핏메이트")
st.caption("식단과 운동 기록을 매일 누적하는 수룡이 다이어트 다이어리")

st.divider()

st.header("👤 사용자 정보 입력")
name = st.text_input("이름")
gender = st.selectbox("성별", ["여자", "남자"])

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("나이", min_value=1, step=1)
with col2:
    height = st.number_input("키(cm)", min_value=1.0)
with col3:
    weight = st.number_input("몸무게(kg)", min_value=1.0)

activity = st.selectbox("활동량", ["거의 안 움직임", "가벼운 활동", "보통", "활발함", "매우 활발"])
goal = st.selectbox("목표", ["감량", "유지", "근육증가"])

allergy = st.text_input("알레르기 음식", value="없음")
dislike = st.text_input("싫어하는 음식", value="없음")
food_style = st.selectbox(
    "선호 식단",
    ["한식", "가벼운식단", "단백질", "간단식", "분식", "중식", "양식", "일식", "간식", "패스트푸드"]
)

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
healthy_count = 0
unhealthy_count = 0

for food in selected_foods:
    total += foods[food]["calorie"]
    if foods[food]["is_healthy"]:
        healthy_count += 1
    else:
        unhealthy_count += 1

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

st.header("🎮 수룡이의 현재 상태")

if total == 0:
    suryong_img = "normal_suryong.jpg"
    suryong_msg = f"배가 고파요! 오늘 먹은 음식을 기록해주세요. 현재 BMI는 {user_bmi}입니다."
    status_color = "info"
elif total > daily_calorie + 150:
    suryong_img = "fat_suryong.jpg"
    suryong_msg = f"권장 칼로리({daily_calorie}kcal)를 많이 초과했어요! 수룡이가 포동포동해졌어요. 😭"
    status_color = "error"
elif unhealthy_count > 0 and unhealthy_count >= healthy_count:
    suryong_img = "fat_suryong.jpg"
    suryong_msg = "다이어트를 방해하는 음식이 많아요! 수룡이가 걱정하고 있어요. 👿"
    status_color = "error"
elif total < daily_calorie - 400:
    suryong_img = "slim_suryong.jpg"
    suryong_msg = "영양이 너무 부족해요! 수룡이가 기운 없이 홀쭉해졌어요. 🥺"
    status_color = "warning"
else:
    suryong_img = "normal_suryong.jpg"
    suryong_msg = "좋아요! 건강하게 목표 칼로리에 가까워지고 있어요. 👍"
    status_color = "success"

col_char, col_info = st.columns([1, 1])

with col_char:
    try:
        st.image(suryong_img, use_container_width=True)
    except:
        st.error(f"⚠️ 저장소에서 '{suryong_img}' 파일을 찾을 수 없습니다.")

with col_info:
    st.subheader(f"🐲 {name if name else '사용자'}님의 수룡이")

    if status_color == "info":
        st.info(suryong_msg)
    elif status_color == "error":
        st.error(suryong_msg)
    elif status_color == "warning":
        st.warning(suryong_msg)
    else:
        st.success(suryong_msg)

    st.metric("나의 BMI 지수", f"{user_bmi}")
    st.metric("목표 권장 칼로리", f"{daily_calorie} kcal")
    st.metric("현재 섭취량", f"{total} kcal", delta=total - daily_calorie, delta_color="inverse")

st.divider()

st.header("🌱 수룡이 진화 시스템")

exp = load_exp()
level, level_name, level_msg = get_level(exp)

st.subheader(f"현재 단계: {level_name}")
st.write(level_msg)

next_goal = 50 if exp < 50 else 120 if exp < 120 else 220
if exp >= 220:
    st.progress(1.0)
    st.success("최종 진화 완료! 수룡이가 성체가 되었어요 👑")
else:
    progress_value = exp / next_goal
    st.progress(progress_value)
    st.write(f"현재 경험치: {exp} XP / 다음 진화까지 {next_goal - exp} XP")

st.caption("운동 기록을 저장하면 수룡이 경험치가 올라갑니다.")

st.divider()

tab1, tab2, tab3 = st.tabs(["🍱 추천 식단", "🏃 추천 운동 및 설정", "📅 나의 누적 다이어트 일지"])

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
        st.warning(f"선택하신 '{food_style}' 카테고리에는 다이어트 전용 추천 식단이 없습니다. 대신 추천 클린 식단을 제공합니다!")
        recommended = ["샐러드", "닭가슴살", "고구마", "계란", "현미밥"]

    for f in recommended:
        st.write(f"- {f}: {foods[f]['calorie']} kcal")

with tab2:
    st.write("🏋️ **오늘 나의 상태에 딱 맞는 맞춤형 운동 프로그램**")

    ex_col1, ex_col2, ex_col3 = st.columns(3)

    with ex_col1:
        place_style = st.selectbox("운동 장소 선택 🏢", ["홈트레이닝 (집)", "헬스장 (Gym)"])
    with ex_col2:
        target_part = st.selectbox("운동 부위 설정 🎯", ["전신", "상체 (가슴/팔)", "하체 (엉덩이/허벅지)", "코어 (복부/허리)"])
    with ex_col3:
        condition = st.selectbox("오늘의 컨디션 🌡️", ["컨디션 최고! 🔥", "보통이에요 🙂", "피곤하고 무거워요 😴"])

    exercise_time = st.slider("오늘 실제 운동한 시간(분)", 0, 120, 30)

    bmi_status = "고체중 (관절 보호)" if user_bmi >= 25.0 else ("저체중 (근력 강화)" if user_bmi < 18.5 else "정상 체중")
    st.info(f"📋 분석 리포트: {bmi_status} 상태에 맞춤형 [{place_style} - {target_part}] 프로그램을 제안합니다.")

    if condition == "컨디션 최고! 🔥":
        cond_msg = "오늘은 강도 높은 운동도 가능해요!"
        gym_set = "4세트"
        home_mission = "맨몸 스쿼트 20회 + 플랭크 1분 추가 진행!"
    elif condition == "보통이에요 🙂":
        cond_msg = "정석 자세에 집중하면서 무리하지 않게 운동해요."
        gym_set = "3세트"
        home_mission = "영상 가이드를 80% 이상 따라 하기!"
    else:
        cond_msg = "오늘은 무리하지 말고 스트레칭과 가벼운 운동 위주로 해요."
        gym_set = "2세트"
        home_mission = "힘들면 앞쪽 10분만 따라 하고 휴식하기!"

    st.warning(f"🌡️ 오늘의 컨디션 케어: {cond_msg}")

    if place_style == "홈트레이닝 (집)":
        st.success("🏠 오늘의 추천 홈트 영상")
        if target_part == "전신":
            st.markdown("- [추천 영상 1](https://youtu.be/gSz5n4sLENI?si=cF8UNYcY7O51vv3P) / [추천 영상 2](https://youtu.be/dZbPtAgofwI?si=fGf1KFgcRwkiR2LU)")
        elif target_part == "상체 (가슴/팔)":
            st.markdown("- [추천 영상 1](https://youtu.be/2swcod5RYvU?si=PiprFfrdaW4POwqI) / [추천 영상 2](https://youtu.be/T-bVqdhqW2U?si=O7RwqaDiVpioeKs7)")
        elif target_part == "하체 (엉덩이/허벅지)":
            st.markdown("- [추천 영상 1](https://youtu.be/dpBYYEhdofI?si=OGiy3ZdSSRCdd__q) / [추천 영상 2](https://youtu.be/NDsjmxTROEo?si=Kx28BPvmyhy8FS4u)")
        else:
            st.markdown("- [추천 영상 1](https://youtu.be/jpTQdM7okkI?si=Iul-MhU62OggKOCP) / [추천 영상 2](https://youtu.be/iOSYLKBk894?si=B606cM5LgWwS1T5j)")

        with st.expander("ℹ️ 홈트 가이드 설명 보기"):
            st.write(home_mission)

    else:
        st.success(f"💪 오늘의 헬스장 추천 머신 루틴 ({gym_set}씩 수행)")
        if target_part == "상체 (가슴/팔)":
            st.markdown("- [추천 강좌 보기](https://youtu.be/Dw8PbebpF9w?si=5NIbj8CspBo_FwZl)")
        elif target_part == "하체 (엉덩이/허벅지)":
            st.markdown("- [추천 강좌 보기](https://youtu.be/Na0Dhue1oqk?si=4VvIt7heeGHHV4Yd)")
        elif target_part == "코어 (복부/허리)":
            st.markdown("- [추천 숏츠 1](https://youtube.com/shorts/ocMkMZya3ac?si=p89Dw6--vfRyqRNT) / [추천 숏츠 2](https://youtube.com/shorts/bAFDWHA7fG8?si=ez9Av_2x54NiKXtj)")
        else:
            st.markdown("- [추천 숏츠 1](https://youtube.com/shorts/ul5GqyTSSIk?si=8NaZLXCPr0ykjo4M) / [추천 숏츠 2](https://youtube.com/shorts/1FZYk9OyxV0?si=ZtGUBllTgPrKHTcM)")

    st.subheader("💾 오늘의 운동 기록 저장")
    st.caption("운동을 한 날에만 저장 버튼을 누르면 수룡이 경험치가 올라갑니다.")

    if st.button("🔥 오늘 운동 완료! 기록 저장하고 경험치 받기"):
        new_data = {
            "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "이름": name if name else "사용자",
            "체중(kg)": weight,
            "BMI": user_bmi,
            "목표 칼로리": daily_calorie,
            "오늘 섭취량": total,
            "운동 장소": place_style,
            "운동 부위": target_part,
            "오늘 컨디션": condition,
            "운동 시간(분)": exercise_time
        }

        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
        else:
            df = pd.DataFrame(columns=new_data.keys())

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

        old_exp = load_exp()

        if exercise_time == 0:
            gained_exp = 0
        elif exercise_time < 20:
            gained_exp = 10
        elif exercise_time < 40:
            gained_exp = 20
        elif exercise_time < 60:
            gained_exp = 30
        else:
            gained_exp = 40

        if condition == "컨디션 최고! 🔥":
            gained_exp += 5

        new_exp = old_exp + gained_exp
        save_exp(new_exp)

        old_level, old_level_name, _ = get_level(old_exp)
        new_level, new_level_name, _ = get_level(new_exp)

        st.success(f"🎉 운동 기록 저장 완료! 수룡이가 {gained_exp} XP를 얻었어요.")

        if new_level > old_level:
            st.balloons()
            st.success(f"🎊 진화 성공! {old_level_name} → {new_level_name}")

        st.info("새로고침하면 성장 시스템에 반영된 수룡이 레벨을 확인할 수 있어요.")

with tab3:
    st.write("📅 **나의 누적 다이어트 일지**")

    if os.path.exists(LOG_FILE):
        df_log = pd.read_csv(LOG_FILE)
        st.dataframe(df_log.iloc[::-1], use_container_width=True)

        st.subheader("📊 나의 다이어트 요약")
        col_stat1, col_stat2, col_stat3 = st.columns(3)

        with col_stat1:
            st.metric("총 기록 수", f"{len(df_log)} 회")
        with col_stat2:
            avg_cal = int(df_log["오늘 섭취량"].mean())
            st.metric("평균 하루 섭취 칼로리", f"{avg_cal} kcal")
        with col_stat3:
            if "운동 시간(분)" in df_log.columns:
                total_exercise = int(df_log["운동 시간(분)"].sum())
            else:
                total_exercise = 0
            st.metric("누적 운동 시간", f"{total_exercise} 분")

        if st.checkbox("⚠️ 전체 기록 지우기"):
            if st.button("정말 삭제하시겠습니까?"):
                os.remove(LOG_FILE)
                st.warning("모든 다이어트 기록이 삭제되었습니다. 페이지를 새로고침 해주세요.")
    else:
        st.info("아직 저장된 다이어트 일지가 없습니다.")

    if st.checkbox("🐉 수룡이 성장 기록 초기화"):
        if st.button("수룡이 경험치 초기화"):
            if os.path.exists(GROW_FILE):
                os.remove(GROW_FILE)
            st.warning("수룡이 성장 기록이 초기화되었습니다. 페이지를 새로고침 해주세요.")