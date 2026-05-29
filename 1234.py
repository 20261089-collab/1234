import streamlit as st
import pandas as pd
from datetime import datetime, time
import os
import calendar
import altair as alt  # 👈 가로 막대그래프를 위해 내장된 altair 사용

# [중요] 모든 st 함수 중 최상단에 위치해야 에러가 나지 않습니다.
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

# 🏋️ [데이터셋] 60kg 기준 운동 종목별 10분당 소비 칼로리 데이터
exercises_db = {
    "산책 / 가벼운 걷기": {"cal_10m": 30, "url": "https://youtu.be/jpTQdM7okkI"},
    "빠르게 걷기 (파워워킹)": {"cal_10m": 40, "url": "https://youtu.be/jpTQdM7okkI"},
    "가벼운 조깅 (러닝머신)": {"cal_10m": 75, "url": "https://youtu.be/dZbPtAgofwI"},
    "계단 오르기": {"cal_10m": 75, "url": "https://youtu.be/ul5GqyTSSIk"},
    "실내 자전거": {"cal_10m": 68, "url": "https://youtu.be/gSz5n4sLENI"},
    "줄넘기": {"cal_10m": 100, "url": "https://youtu.be/gSz5n4sLENI"},
    "수영 (자유형)": {"cal_10m": 95, "url": "https://youtu.be/gSz5n4sLENI"},
    "스트레칭 / 요가": {"cal_10m": 28, "url": "https://youtu.be/jpTQdM7okkI"},
    "필라테스": {"cal_10m": 35, "url": "https://youtu.be/iOSYLKBk894"},
    "웨이트 트레이닝 (헬스장 머신)": {"cal_10m": 55, "url": "https://youtu.be/Dw8PbebpF9w"},
    "맨몸 스쿼트 / 런지": {"cal_10m": 60, "url": "https://youtu.be/dpBYYEhdofI"},
    "플랭크 / 복근 운동": {"cal_10m": 50, "url": "https://youtu.be/iOSYLKBk894"},
    "팔굽혀펴기 / 상체 홈트": {"cal_10m": 55, "url": "https://youtu.be/2swcod5RYvU"},
    "버피 테스트": {"cal_10m": 100, "url": "https://youtu.be/gSz5n4sLENI"},
    "복싱": {"cal_10m": 95, "url": "https://youtube.com/shorts/ocMkMZya3ac"}
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

        tab1, tab2, tab3 = st.tabs(["🍱 추천 식단", "🏃 맞춤 운동 추천 및 계산", "📅 나의 누적 다이어트 일지"])

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
            st.write("🏋️ **오늘 나의 상태에 딱 맞는 운동 종목별 맞춤 계산기**")

            st.subheader("📅 운동 날짜 지정")
            select_date = st.date_input("기록을 입력할 날짜를 선택하세요", datetime.now().date())

            st.divider()
            st.subheader("👟 오늘 진행할 운동 조합 선택")
            
            selected_ex_list = st.multiselect("오늘 어떤 운동들을 묶어서 조합하실 건가요? (복수 선택 가능)", list(exercises_db.keys()))
            
            total_burned_calories = 0
            total_time_sum = 0
            exercise_time_dict = {}
            
            if selected_ex_list:
                st.write("⏱️ **선택한 운동 조합별 진행 시간(분)을 설정하세요**")
                
                for ex_name in selected_ex_list:
                    cal_per_10m = exercises_db[ex_name]["cal_10m"]
                    ex_time = st.slider(f"[{ex_name}] 진행 시간 (10분당 {cal_per_10m} kcal 소모)", 0, 120, 20, key=f"time_{ex_name}")
                    
                    ex_burned = round((ex_time / 10) * cal_per_10m)
                    total_burned_calories += ex_burned
                    total_time_sum += ex_time
                    exercise_time_dict[ex_name] = ex_time
                
                st.divider()
                
                st.subheader("🔥 오늘의 맞춤 운동 총 소비 칼로리 결과")
                col_calc1, col_calc2 = st.columns(2)
                col_calc1.metric("선택한 총 운동 시간", f"{total_time_sum} 분")
                col_calc2.metric("예상 총 소비 칼로리", f"{total_burned_calories} kcal")
                
                st.info(f"💡 선택한 조합 계측: 60kg 기준, 오늘 설정하신 루틴을 완수하면 총 **{total_burned_calories} kcal**가 소비됩니다!")
                
                st.write("📺 **추천 운동 가이드 영상 안내 (참고용)**")
                for ex_name in selected_ex_list:
                    url = exercises_db[ex_name]["url"]
                    st.markdown(f"- **{ex_name}** 영상 보러가기: [링크 클릭]({url}) *(참고용)*")
            else:
                st.info("운동 리스트에서 오늘 수행할 종목 조합을 먼저 선택해 주세요!")

            st.divider()
            st.subheader("💾 운동 기록 저장")
            if st.button("🔥 지정된 날짜로 기록 저장하고 경험치 받기"):
                if not selected_ex_list:
                    st.error("저장할 운동 조합이 없습니다. 종목을 선택해 주세요.")
                else:
                    current_time_str = datetime.now().strftime("%H:%M")
                    formatted_date = f"{select_date.strftime('%Y-%m-%d')} {current_time_str}"
                    
                    ex_summary = ", ".join(selected_ex_list)

                    new_data = {
                        "날짜": formatted_date, "이름": name if name else "사용자",
                        "체중(kg)": weight, "BMI": user_bmi, "목표 칼로리": daily_calorie, "오늘 섭취량": total,
                        "운동 장소": ex_summary, "운동 부위": total_burned_calories, "오늘 컨디션": "정상", "운동 시간(분)": total_time_sum
                    }
                    df = pd.read_csv(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame(columns=new_data.keys())
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

                    old_exp = load_exp()
                    gained_exp = 10
                    new_exp = old_exp + gained_exp
                    save_exp(new_exp)

                    st.success(f"🎉 {select_date.strftime('%m월 %d일')} 운동 조합 기록 완료! 수룡이가 10 EXP를 얻었어요.")

        with tab3:
            st.write("📅 **나의 누적 다이어트 일지**")
            if os.path.exists(LOG_FILE):
                df_log = pd.read_csv(LOG_FILE)
                
                df_log["오늘 섭취량"] = pd.to_numeric(df_log["오늘 섭취량"], errors="coerce").fillna(0)
                df_log["운동 부위"] = pd.to_numeric(df_log["운동 부위"], errors="coerce").fillna(0)
                df_log["운동 시간(분)"] = pd.to_numeric(df_log["운동 시간(분)"].fillna(0), errors="coerce")
                
                df_display = df_log.copy()
                df_display = df_display.rename(columns={"운동 장소": "수행한 운동 조합", "운동 부위": "소비 칼로리(kcal)"})
                st.dataframe(df_display.iloc[::-1], use_container_width=True)

                st.subheader("📊 나의 다이어트 요약")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                col_stat1.metric("총 기록 수", f"{len(df_log)} 회")
                col_stat2.metric("평균 하루 섭취 칼로리", f"{int(df_log['오늘 섭취량'].mean())} kcal")
                col_stat3.metric("평균 운동 소모 칼로리", f"{int(df_log['운동 부위'].mean())} kcal")
                col_stat4.metric("누적 운동 시간", f"{int(df_log['운동 시간(분)'].sum())} 분")

                st.divider()
                
                # 📈 [요청 사항 반영] 가로형 막대그래프 개편 파트 (안정적인 Altair 사용)
                st.subheader("📊 일자별 섭취량 vs 운동 소모량 비교")

                df_log["날짜_일만"] = pd.to_datetime(df_log["날짜"]).dt.strftime("%m-%d")
                df_chart = df_log.groupby("날짜_일만")[["오늘 섭취량", "운동 부위"]].sum().reset_index()
                
                # 데이터를 차트 그리기용(Melt)으로 변환
                df_melted = df_chart.melt(id_vars="날짜_일만", var_name="구분", value_name="칼로리")
                df_melted["구분"] = df_melted["구분"].replace({"오늘 섭취량": "섭취 칼로리", "운동 부위": "운동 소모 칼로리"})

                # 💡 가로 막대그래프 생성 (y축에 날짜, x축에 칼로리 배치)
                # properties를 통해 너무 뚱뚱해지지 않게 높이(height)를 데이터 개수에 맞춰 슬림하게 조절했습니다.
                chart_height = max(150, len(df_chart) * 60) # 데이터가 적어도 기본 150px, 많아지면 늘어남
                
                horizontal_bar = alt.Chart(df_melted).mark_bar().encode(
                    y=alt.Y("날짜_일만:N", title="날짜"),
                    x=alt.X("칼로리:Q", title="칼로리(kcal)"),
                    color=alt.Color("구분:N", scale=alt.Scale(range=["#4A90E2", "#FF8C00"])), # 파랑, 주황
                    offset=alt.XOffset("구분:N"), # 막대를 날짜별로 나란히 배치
                ).properties(height=chart_height, width=500) # 슬림한 너비 유지

                st.altair_chart(horizontal_bar, use_container_width=False)
                st.caption("💡 주황색(운동 소모) 막대가 파란색(섭취) 막대보다 길수록 다이어트 효과가 높습니다.")

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
    st.title("🐉 수룡이 성장 룸")
    st.caption("운동 기록으로 획득한 경험치($EXP$)에 따라 진화하는 진짜 수룡이의 방입니다.")
    st.divider()

    exp = load_exp()
    level, level_name, suryong_img = get_level(exp)

    grow_col1, grow_col2 = st.columns([1, 1])

    with grow_col1:
        try:
            st.image(suryong_img, use_container_width=True)
        except:
            st.error(f"⚠️ 수룡이 진화 이미지 파일('{suryong_img}')을 찾을 수 없습니다. 파일명을 확인해 주세요.")

    with grow_col2:
        st.subheader(f"현재 단계: {level_name}")
        if exp >= 720:
            st.progress(1.0)
            st.success("🎉 축하합니다! 최종 단계인 전설의 수룡이가 완성되었습니다! 👑")
        else:
            next_goal = 120 if exp < 120 else 360 if exp < 360 else 720
            st.progress(exp / next_goal)
            st.write(f"📈 현재 누적 경험치: **{exp} EXP**")
            st.write(f"✨ 다음 진화까지 **{next_goal - exp} EXP** 남았어요.")

    st.divider()
    st.write("📌 **수룡이 진화 단계 안내 (알 키우기)**")
    st.write("- **1단계 (0 EXP 이상):** 🥚 알 수룡이")
    st.write("- **2단계 (120 EXP 이상):** 🐣 아기 수룡이")
    st.write("- **3단계 (360 EXP 이상):** 🐉 성장한 수룡이")
    st.write("- **4단계 (720 EXP 이상):** 👑 전설의 수룡이")

    st.divider()
    if st.checkbox("⚠️ 수룡이 성장 기록 초기화"):
        if st.button("수룡이 경험치 초기화"):
            if os.path.exists(GROW_FILE):
                os.remove(GROW_FILE)
            st.warning("수룡이 성장 기록이 초기화되었습니다. 해당 페이지를 새로고침 해주세요.")


# --- 멀티페이지 내비게이션 구성 ---
pg = st.navigation([
    st.Page(show_main_page, title="📊 다이어트 다이어리", icon="📝"),
    st.Page(show_growth_page, title="🐉 수룡이 알 키우기", icon="🥚")
])
pg.run()
