import streamlit as st
import pandas as pd
from datetime import datetime
import os
import calendar
import altair as alt

# 🚨 Streamlit 최상단 환경 설정
st.set_page_config(
    page_title="수룡이와 함께하는 맞춤형 다이어트",
    page_icon="🐉",
    layout="centered"
)

LOG_FILE = "diet_exercise_log.csv"
GROW_FILE = "suryong_growth.csv"
PROFILE_FILE = "user_profile.csv"
LOGO_FILE = "icon.png"


# --- 공통 연산 함수 ---
def calculate_bmi(weight, height):
    h = height / 100
    return round(weight / (h ** 2), 1)


# 🧮 개정된 해리스-베네딕트 공식
def calculate_bmr_harris_benedict(weight, height, age, gender):
    if gender == "남자":
        return round(66.47 + (13.75 * weight) + (5.0 * height) - (6.76 * age), 1)
    return round(655.1 + (9.56 * weight) + (1.85 * height) - (4.68 * age), 1)


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


# 🍱 음식 데이터베이스
foods = {
    "오트밀 + 바나나": {"calorie": 280, "is_healthy": True, "allergens": []},
    "현미밥 + 닭가슴살 + 구운 야채": {"calorie": 420, "is_healthy": True, "allergens": ["닭고기"]},
    "연어 아보카도 샐러드": {"calorie": 380, "is_healthy": True, "allergens": ["생선"]},
    "그릭요거트 + 블루베리 + 그래놀라": {"calorie": 310, "is_healthy": True, "allergens": ["우유", "밀"]},
    "사과 + 땅콩버터 1스푼": {"calorie": 240, "is_healthy": True, "allergens": ["땅콩"]},
    "곤약볶음밥 + 달걀후라이": {"calorie": 350, "is_healthy": True, "allergens": ["달걀", "대두"]},
    "통밀 식빵 샌드위치 (닭가슴살 햄)": {"calorie": 360, "is_healthy": True, "allergens": ["밀", "닭고기", "달걀"]},
    "스리라차 닭가슴살 통밀 브리또": {"calorie": 340, "is_healthy": True, "allergens": ["밀", "닭고기"]},
    
    "소고기 부채살 + 버섯 구이 (곱빼기)": {"calorie": 590, "is_healthy": True, "allergens": ["쇠고기"]},
    "고구마 2개 + 훈제오리 샐러드 대짜": {"calorie": 580, "is_healthy": True, "allergens": ["오리고기"]},
    "두부면 토마토 파스타 + 닭가슴살 소시지": {"calorie": 440, "is_healthy": True, "allergens": ["대두", "닭고기"]},

    "참치김밥": {"calorie": 500, "is_healthy": True, "allergens": ["생선", "달걀", "밀"]},
    "일반 그냥 김밥": {"calorie": 400, "is_healthy": True, "allergens": ["달걀", "밀"]},
    "떡볶이": {"calorie": 450, "is_healthy": False, "allergens": ["밀", "대두"]},
    "불닭볶음면": {"calorie": 530, "is_healthy": False, "allergens": ["밀", "대두"]},
    "마라탕 (야채+소고기 기본)": {"calorie": 600, "is_healthy": False, "allergens": ["밀", "대두", "쇠고기", "땅콩"]},
    "로제 찜닭 (소량)": {"calorie": 650, "is_healthy": False, "allergens": ["닭고기", "우유", "대두"]},
    "치즈케이크 1조각": {"calorie": 350, "is_healthy": False, "allergens": ["우유", "밀", "달걀"]},
    "연세우유 생크림빵 (반 개)": {"calorie": 230, "is_healthy": False, "allergens": ["밀", "우유", "달걀"]},
    "아이스 아메리카노": {"calorie": 10, "is_healthy": True, "allergens": []},
    "프로틴 어니언 칩 / 다이어트 스낵": {"calorie": 120, "is_healthy": True, "allergens": ["대두"]},
    "제로 탄산음료": {"calorie": 0, "is_healthy": True, "allergens": []}
}

# 🏋️ 프리셋 데이터베이스
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
                {"name": "맨몸 와이드 스쿼트 (저강도)", "cal_10m": 50, "guide": "🔋 3세트 × 12회", "rest": "⏱️ 휴식 90초", "tip": "다리를 넓게 벌려 관절 부담을 줄이지 마시고 허벅지 안쪽 자극에 집중합니다."},
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
                {"name": "전신 다이어트 최고의 운동 [칼소폭 찐 핵핵핵 매운맛]", "cal_10m": 120, "url": "https://youtu.be/gSz5n4sLENI", "guide": "🔥 설정된 시간 동안 올인 타겟", "rest": "⏱️ 영상 페이스 유지", "tip": "층간 소음 및 무릎 부담이 적은 전신 루틴입니다. 지치지 않게 호흡을 길게 가져가세요."},
                {"name": "멜킨 튜닝 줄넘기 / 고속 줄넘기", "cal_10m": 110, "guide": "🔥 인터벌 페이스 집중 수행", "rest": "⏱️ 휴식 40초", "tip": "발앞꿈치로 가볍게 착지하며 손목 회전력을 유지하세요."},
                {"name": "실내 싸이클 / 러닝 스퍼트", "cal_10m": 85, "guide": "🔥 강력한 페달링 속도 유지", "rest": "⏱️ 지속 가동", "tip": "코어에 힘을 주고 하체의 폭발적인 에너지를 사용합니다."}
            ],
            "정상 (보통)": [
                {"name": "전신 다이어트 최고의 운동 [칼소폭 찐 핵핵핵 매운맛]", "cal_10m": 100, "url": "https://youtu.be/gSz5n4sLENI", "guide": "✨ 표준 완주 배분 수행", "rest": "⏱️ 표준 호흡 구사", "tip": "중간에 완전히 멈추지 않고 끝까지 동작을 완수하는 것을 목표로 템포를 맞춥니다."},
                {"name": "실내 자전거 (싸이클링)", "cal_10m": 65, "guide": "✨ 일정한 RPM 75 유지", "rest": "⏱️ 릴렉스 템포", "tip": "가볍게 음악을 들으며 무릎 관절에 충격이 가지 않게 굴려줍니다."},
                {"name": "실외 빠르게 뛰기 및 걷기", "cal_10m": 70, "guide": "✨ 🏃 속도 6.0 지속 페이스", "rest": "⏱️ 호흡 유지", "tip": "발바닥 전체가 부드럽게 땅에 닿도록 리듬을 탑니다."}
            ],
            "피곤함 (가벼운 운동 필요)": [
                {"name": "전신 다이어트 최고의 운동 [칼소폭 찐 핵핵핵 매운맛] (저강도 페이스)", "cal_10m": 80, "url": "https://youtu.be/gSz5n4sLENI", "guide": "🔋 무리하지 않고 시간 완주하기", "rest": "⏱️ 동작 크기 줄이기", "tip": "피로도가 높으므로 관절에 과한 힘을 빼고 가벼운 마음으로 전신 순환 위주로 따라 하세요."},
                {"name": "동네 한바퀴 가벼운 산책", "cal_10m": 45, "guide": "🔋 산책 페이스 워킹", "rest": "⏱️ 여유롭게 호흡", "tip": "맑은 공기를 마시며 전신 순환을 돕는 가벼운 속도입니다."},
                {"name": "제자리 걷기 힐링 루틴", "cal_10m": 40, "guide": "🔋 집안에서 가볍게 걷기", "rest": "⏱️ 편안히 가동", "tip": "팔을 앞뒤로 흔들며 몸에 열을 가볍게 내어줍니다."}
            ],
            "근육통 있음": [
                {"name": "전신 다이어트 최고의 운동 [칼소폭 찐 핵핵핵 매운맛] (리커버리 모드)", "cal_10m": 70, "url": "https://youtu.be/gSz5n4sLENI", "guide": "🩹 전신 스트레칭 리커버리 코스", "rest": "⏱️ 호흡 집중", "tip": "근육통이 심한 부위는 반동을 주지 말고 가볍게 몸을 풀어준다는 느낌으로 움직입니다."},
                {"name": "폼롤러 전신 근막 이완 코스", "cal_10m": 30, "guide": "🩹 전신 순환 지점 압박", "rest": "⏱️ 힐링 템포", "tip": "아픈 부위를 지그시 누르며 숨을 깊게 내쉬어 이완합니다."},
                {"name": "동네 가벼운 산책 및 리프레시", "cal_10m": 40, "guide": "🩹 가볍게 발걸음 옮기기", "rest": "⏱️ 무리 금지", "tip": "관절을 가볍게 써주어 혈류 공급을 원활하게 만듭니다."}
            ]
        }
    }
}

# 🏋️ 헬스장 기구 루틴 데이터베이스
gym_split_presets = {
    "최상 (에너지 넘침)": {
        "상체": [
            {"name": "렛 풀 다운 (등 광배근 타겟)", "cal_10m": 65, "guide": "🔥 고중량 5세트 × 10회 (실패지점)", "rest": "⏱️ 휴식 50초", "tip": "날개뼈를 강하게 내리며 바를 쇄골 쪽으로 당겨 넓은 등 프레임을 만듭니다."},
            {"name": "체스트 프레스 머신 (대흉근 타겟)", "cal_10m": 65, "guide": "🔥 고중량 5세트 × 12회", "rest": "⏱️ 휴식 50초", "tip": "어깨를 패드에 밀착시키고 가슴의 힘으로 수축과 이완을 끝까지 통제하세요."},
            {"name": "시티드 케이블 로우 (등 중하부 타겟)", "cal_10m": 60, "guide": "🔥 4세트 × 12회 중량 강화", "rest": "⏱️ 휴식 45초", "tip": "허리가 굽지 않게 세우고 아랫배 쪽으로 손잡이를 당기며 견갑을 접어줍니다."},
            {"name": "덤벨 숄더 프레스 (어깨 전면/측면 타겟)", "cal_10m": 55, "guide": "🔥 4세트 × 12회 고강도", "rest": "⏱️ 휴식 50초", "tip": "덤벨을 수직으로 밀어 올리되 승모근이 과하게 개입되지 않도록 컨트롤하세요."}
        ],
        "하체": [
            {"name": "레그 프레스 머신 (대퇴사두 및 둔근)", "cal_10m": 85, "guide": "🔥 고중량 5세트 × 12회 (최대 가동)", "rest": "⏱️ 휴식 60초", "tip": "발판을 밀 때 무릎 관절을 다 펴서 퉁 튕기지 말고 근육의 긴장감을 유지하세요."},
            {"name": "바벨 백 스쿼트 (하체 전신 코어)", "cal_10m": 90, "guide": "🔥 5세트 × 10회 고중량", "rest": "⏱️ 휴식 70초", "tip": "복압을 꽉 잡고 뒤꿈치로 바닥을 뚫는 느낌으로 수직 지지하며 일어나세요."},
            {"name": "레그 익스텐션 머신 (허벅지 앞쪽 고립)", "cal_10m": 55, "guide": "🔥 4세트 × 15회 펌핑 강타", "rest": "⏱️ 휴식 45초", "tip": "발끝을 몸쪽으로 당긴 상태에서 대퇴사두근 상단까지 쥐어짜듯 올려줍니다."},
            {"name": "시티드 레그 컬 머신 (허벅지 뒤쪽 햄스트링)", "cal_10m": 55, "guide": "🔥 4세트 × 15회 수축 집중", "rest": "⏱️ 휴식 45초", "tip": "엉덩이가 시트에서 뜨지 않게 패드를 고정하고 발뒤꿈치를 엉덩이 쪽으로 깊게 당깁니다."}
        ],
        "유산소": [
            {"name": "천국의 계단 (스텝밀)", "cal_10m": 110, "guide": "🔥 속도 7~9 인터벌 페이스", "rest": "⏱️ 지속 가동", "tip": "상체를 약간 숙이고 둔근의 힘을 이용해 계단을 디디세요."},
            {"name": "트레드밀 마이마운틴 (고경사 러닝)", "cal_10m": 95, "guide": "🔥 경사도 12% / 속도 5.5", "rest": "⏱️ 지속 가동", "tip": "손잡이를 살짝만 쥐고 뒤꿈치까지 밀착해 밀며 걸어주세요."}
        ]
    },
    "정상 (보통)": {
        "상체": [
            {"name": "렛 풀 다운 (등 광배근 타겟)", "cal_10m": 55, "guide": "✨ 정석 4세트 × 12회 (적정 중량)", "rest": "⏱️ 휴식 60초", "tip": "상체가 뒤로 과도하게 눕지 않도록 복부에 긴장을 유지하세요."},
            {"name": "체스트 프레스 머신 (대흉근 타겟)", "cal_10m": 55, "guide": "✨ 정석 4세트 × 12회", "rest": "⏱️ 휴식 60초", "tip": "수축 시 가슴 중앙이 모이는 자극에 집중하며 지그시 밀어줍니다."},
            {"name": "시티드 케이블 로우 (등 중하부 타겟)", "cal_10m": 50, "guide": "✨ 정석 4세트 × 12회 안정화", "rest": "⏱️ 휴식 60초", "tip": "광배근이 늘어날 때 이완 템포를 천천히 가져가며 버텨줍니다."},
            {"name": "덤벨 숄더 프레스 (어깨 전면/측면 타겟)", "cal_10m": 45, "guide": "✨ 정석 4세트 × 12회 컨트롤", "rest": "⏱️ 휴식 60초", "tip": "팔꿈치가 뒤로 빠지면 어깨 전면에 부상이 올 수 있으니 살짝 앞으로 유지하세요."}
        ],
        "하체": [
            {"name": "레그 프레스 머신 (대퇴사두 및 둔근)", "cal_10m": 70, "guide": "✨ 정석 4세트 × 15회 (표준 중량)", "rest": "⏱️ 휴식 60초", "tip": "내려올 때 허리가 패드에서 뜨지 않도록 엉덩이를 꽉 밀착하세요."},
            {"name": "바벨 백 스쿼트 (하체 전신 코어)", "cal_10m": 75, "guide": "✨ 정석 4세트 × 12회 표준 볼륨", "rest": "⏱️ 휴식 60초", "tip": "무릎이 안쪽으로 모이지 않도록 발끝 방향과 일치시키며 내려갑니다."},
            {"name": "레그 익스텐션 머신 (허벅지 앞쪽 고립)", "cal_10m": 45, "guide": "✨ 정석 4세트 × 15회 일정한 속도", "rest": "⏱️ 휴식 45초", "tip": "반동을 이용해 차지 말고 정점에서 1초간 멈춰 자극을 각인시킵니다."},
            {"name": "시티드 레그 컬 머신 (허벅지 뒤쪽 햄스트링)", "cal_10m": 45, "guide": "✨ 정석 4세트 × 15회 템포 통제", "rest": "⏱️ 휴식 45초", "tip": "다리가 펴질 때도 무게를 매달고 버틴다는 느낌으로 천천히 풀어줍니다."}
        ],
        "유산소": [
            {"name": "천국의 계단 (스텝밀)", "cal_10m": 90, "guide": "✨ 속도 5~6 일정 페이스", "rest": "⏱️ 지속 가동", "tip": "발바닥 전체가 발판에 닿도록 고르게 디뎌 안정성을 높입니다."},
            {"name": "실내 고정식 싸이클 자전거", "cal_10m": 65, "guide": "✨ 회전수(RPM) 70~80 유지", "rest": "⏱️ 지속 가동", "tip": "가슴을 펴고 허벅지 앞쪽과 둔근의 고른 힘으로 페달 굴립니다."}
        ]
    },
    "피곤함 (가벼운 운동 필요)": {
        "상체": [
            {"name": "렛 풀 다운 (저중량 등 자극)", "cal_10m": 45, "guide": "🔋 라이트 3세트 × 12회", "rest": "⏱️ 휴식 90초", "tip": "무게를 낮추고 등의 날개뼈가 부드럽게 움직이는 것에만 집중합니다."},
            {"name": "체스트 프레스 머신 (저중량 가슴)", "cal_10m": 45, "guide": "🔋 라이트 3세트 × 12회", "rest": "⏱️ 휴식 90초", "tip": "반동 없이 가슴 근육에 혈류를 보내준다는 느낌으로 가볍게 밀어줍니다."}
        ],
        "하체": [
            {"name": "레그 프레스 머신 (저중량)", "cal_10m": 50, "guide": "🔋 라이트 3세트 × 12회 (관절 보호)", "rest": "⏱️ 휴식 90초", "tip": "중량을 대폭 낮추고 무릎 관절에 피로가 가지 않도록 부드럽게 움직입니다."},
            {"name": "레그 익스텐션 머신 (저중량 스트레칭 겸용)", "cal_10m": 35, "guide": "🔋 라이트 3세트 × 15회 관절 윤활", "rest": "⏱️ 휴식 60초", "tip": "허벅지 관절을 부드럽게 풀어주어 혈액순환을 극대화합니다."}
        ],
        "유산소": [
            {"name": "트레드밀 파워 워킹 (경사도 가볍게)", "cal_10m": 50, "guide": "🚶 속도 4.5~5.0 힐링 워킹", "rest": "⏱️ 편안히 가동", "tip": "호흡을 길게 내쉬며 가볍게 땀이 맺힐 정도로만 걸어줍니다."},
            {"name": "실내 고정식 싸이클 자전거", "cal_10m": 45, "guide": "🚶 저항 2~3단계로 가벼운 페달링", "rest": "⏱️ 릴렉스", "tip": "하체의 젖산과 피로를 부드럽게 분해하는 힐링 페이스입니다."}
        ]
    },
    "근육통 있음": {
        "상체": [
            {"name": "폼롤러 등/어깨 상체 이완", "cal_10m": 25, "guide": "🩹 15분 전신 스트레칭", "rest": "⏱️ 여유롭게", "tip": "뭉친 광배근 및 가슴 근막을 문질러 통증을 완화시킵니다."},
            {"name": "맨몸 회전근개 리커버리", "cal_10m": 25, "guide": "🩹 3세트 반복", "rest": "⏱️ 편안하게", "tip": "관절을 가볍게 돌려주어 상체 피로 물질을 제거합니다."}
        ],
        "하체": [
            {"name": "하체 전신 스트레칭 & 모빌리티", "cal_10m": 25, "guide": "🩹 부위별 30초 유지", "rest": "⏱️ 제한 없음", "tip": "뭉친 허벅지와 골반 유연성을 늘려 피로를 회복합니다."},
            {"name": "폼롤러 하체 근막 이완 코스", "cal_10m": 25, "guide": "🩹 20분 둔근/대퇴 이완", "rest": "⏱️ 힐링 템포", "tip": "아픈 부위를 지그시 누르며 호흡을 내쉬어 몸을 풉니다."}
        ],
        "유산소": [
            {"name": "트레드밀 평지 가벼운 산책", "cal_10m": 35, "guide": "🚶 속도 4.0 전신 순환 워킹", "rest": "⏱️ 편안히 호흡", "tip": "전신에 가벼운 혈류를 공급하여 근육통 회복을 유도합니다."}
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
        st.caption("목적별 자동 맞춤 식단과 스마트 운동 루틴을 제공하는 수정이 전용 다이어리")

    st.divider()

    profile = load_profile()

    st.header("👤 수정이 정보 입력")
    name = st.text_input("이름", value=profile.get("이름", "에융이"))

    gender_options = ["여자", "남자"]
    gender = st.selectbox("성별", gender_options, index=gender_options.index(profile.get("성별", "여자")))

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("나이", min_value=1, step=1, value=int(profile.get("나이", 22)))
    with col2:
        height = st.number_input("키(cm)", min_value=1.0, value=float(profile.get("키(cm)", 163.0)))
    with col3:
        weight = st.number_input("몸무게(kg)", min_value=1.0, value=float(profile.get("몸무게(kg)", 54.0)))

    activity_options = ["거의 안 움직임", "가벼운 활동", "보통", "활발함", "매우 활발"]
    activity = st.selectbox("활동량", activity_options, index=activity_options.index(profile.get("활동량", "보통")))

    goal_options = ["감량", "유지", "근육증가"]
    goal = st.selectbox("현재 나의 목표", goal_options, index=goal_options.index(profile.get("목표", "감량")))

    allergy_options = ["밀", "달걀", "우유", "대두", "생선", "조개류", "갑각류(새우/게)", "닭고기", "돼지고기", "쇠고기", "땅콩"]
    
    saved_allergies = profile.get("알레르기 음식", "[]")
    if isinstance(saved_allergies, str):
        if saved_allergies.startswith("[") and saved_allergies.endswith("]"):
            import ast
            try: saved_allergies = ast.literal_eval(saved_allergies)
            except: saved_allergies = []
        else:
            saved_allergies = [saved_allergies] if saved_allergies in allergy_options else []
    
    selected_allergies = st.multiselect(
        "해당하는 알레르기 음식을 선택해 주세요",
        allergy_options,
        default=saved_allergies
    )

    save_profile({
        "이름": name, "성별": gender, "나이": age, "키(cm)": height, "몸무게(kg)": weight,
        "활동량": activity, "목표": goal, "알레르기 음식": str(selected_allergies)
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
    for f, info in foods.items():
        food_allergens = info.get("allergens", [])
        if not any(alg in food_allergens for alg in selected_allergies):
            safe_food_pool.append(f)

    if goal == "감량":
        st.caption("🔥 **탄수화물과 지방을 줄인 고단백 클린 다이어트 조합**")
        breakfast_food = "오트밀 + 바나나" if "오트밀 + 바나나" in safe_food_pool else "사과 + 땅콩버터 1스푼"
        lunch_food = "현미밥 + 닭가슴살 + 구운 야채" if "현미밥 + 닭가슴살 + 구운 야채" in safe_food_pool else "곤약볶음밥 + 달걀후라이"
        dinner_food = "연어 아보카도 샐러드" if "연어 아보카도 샐러드" in safe_food_pool else "그릭요거트 + 블루베리 + 그래놀라"
    elif goal == "유지":
        st.caption("🥗 **부담 없이 일상을 지속하는 20대 맞춤형 웰빙 일반식 조합**")
        breakfast_food = "그릭요거트 + 블루베리 + 그래놀라" if "그릭요거트 + 블루베리 + 그래놀라" in safe_food_pool else "사과 + 땅콩버터 1스푼"
        lunch_food = "참치김밥" if "참치김밥" in safe_food_pool else "통밀 식빵 샌드위치 (닭가슴살 햄)"
        dinner_food = "곤약볶음밥 + 달걀후라이" if "곤약볶음밥 + 달걀후라이" in safe_food_pool else "스리라차 닭가슴살 통밀 브리또"
    else:
        st.caption("💪 **근육 성장을 위해 양을 늘리고 에너지를 가득 채운 고칼로리 단백질 조합**")
        breakfast_food = "통밀 식빵 샌드위치 (닭가슴살 햄)" if "통밀 식빵 샌드위치 (닭가슴살 햄)" in safe_food_pool else "오트밀 + 바나나"
        lunch_food = "소고기 부채살 + 버섯 구이 (곱빼기)" if "소고기 부채살 + 버섯 구이 (곱빼기)" in safe_food_pool else "현미밥 + 닭가슴살 + 구운 야채"
        dinner_food = "고구마 2개 + 훈제오리 샐러드 대짜" if "고구마 2개 + 훈제오리 샐러드 대짜" in safe_food_pool else "두부면 토마토 파스타 + 닭가슴살 소시지"

    bf_cal = foods.get(breakfast_food, {"calorie": 280})["calorie"]
    lc_cal = foods.get(lunch_food, {"calorie": 420})["calorie"]
    dn_cal = foods.get(dinner_food, {"calorie": 380})["calorie"]

    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        st.markdown("### 🌅 아침 식단")
        st.info(f"**{breakfast_food}**\n\n({bf_cal} kcal)")
        chk_breakfast = st.checkbox("아침 추천대로 먹었어요", key="chk_bf_diet_v12")

    with r_col2:
        st.markdown("### ☀️ 점심 식단")
        st.success(f"**{lunch_food}**\n\n({lc_cal} kcal)")
        chk_lunch = st.checkbox("점심 추천대로 먹었어요", key="chk_lc_diet_v12")

    with r_col3:
        st.markdown("### 🌌 저녁 식단")
        st.warning(f"**{dinner_food}**\n\n({dn_cal} kcal)")
        chk_dinner = st.checkbox("저녁 추천대로 먹었어요", key="chk_dn_diet_v12")

    st.divider()

    st.header("🍽️ 오늘 먹은 음식 기록 (+추가 및 직접 입력)")
    selected_foods = st.multiselect("오늘 추가로 더 드신 기성 음식을 골라주세요.", list(foods.keys()), key="multiselect_foods_v12")

    st.markdown("#### ✍️ 리스트에 없는 음식을 직접 입력하기")
    c_col1, c_col2 = st.columns([2, 1])
    with c_col1:
        custom_food_name = st.text_input("음식 이름 입력", placeholder="예: 엄마표 닭도리탕", key="custom_food_name_v12")
    with c_col2:
        custom_food_cal = st.number_input("칼로리(kcal)", min_value=0, step=5, value=0, key="custom_food_cal_v12")

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
        elif total < daily_calorie - 350:
            suryong_img = "slim_suryong.jpg"
            suryong_msg = "건강하고 이쁜 라인을 위해 너무 굶지 마시고 추천 식단을 좀 더 챙겨 드셔보세요! 🥺"
            status_color = "warning"
        elif total > daily_calorie + 150:
            suryong_img = "fat_suryong.jpg"
            suryong_msg = "오늘 목표치를 살짝 초과했습니다! 아래 AI 맞춤 루틴으로 칼로리를 싹 태워버려요! 🔥"
            status_color = "error"
        else:
            suryong_img = "normal_suryong.jpg"
            suryong_msg = "대박! 칼로리 밸런스가 정말 완벽해요. 이대로만 유지하면 다이어트 무조건 성공입니다! 👍"
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

            # 📊 [요구사항 반영 완료] 메트릭 순서 정렬 및 텍스트 설명 아코디언 추가
            st.metric("나의 BMI 지수", f"{user_bmi}")
            st.metric("나의 기초대사량 (BMR)", f"{user_bmr} kcal")
            st.metric("나의 활동대사량 (TDEE)", f"{user_tdee} kcal")
            
            st.write("") # 가독성을 위한 공백
            
            # 💡 접고 펼칠 수 있는 연회색 톤의 이유 설명란 박스
            with st.expander("💡 왜 기초대사량보다 권장 칼로리가 높을까요?", expanded=False):
                st.markdown(
                    """
                    <div style="color: #666666; font-size: 0.95em; line-height: 1.6; padding: 5px;">
                    많은 분들이 다이어트를 할 때 '기초대사량보다 적게 먹어야 살이 빠진다'고 오해하곤 합니다. 하지만 실제로는 그렇지 않습니다!<br><br>
                    <ul>
                        <li><b>기초대사량(BMR):</b> 하루 종일 누워서 숨만 쉴 때 장기를 돌리기 위해 필요한 최소한의 생존 연료입니다.</li>
                        <li><b>활동대사량(TDEE):</b> 출퇴근, 공부, 산책 등 일상적인 움직임과 운동을 모두 포함해 하루에 <b>진짜로 소모하는 총에너지</b>입니다.</li>
                    </ul>
                    따라서 몸이 하루 동안 실제로 쓰는 양(활동대사량)에서 안전하게 칼로리를 뺀 <b>목표 권장 칼로리</b>는 당연히 기초대사량보다 높게 설정됩니다.<br><br>
                    만약 기초대사량보다도 적게 먹으며 극단적으로 굶는 다이어트를 하면, 우리 몸은 기근 상태(비상사태)로 인식해 <b>지방 대신 근육을 먼저 분해</b>하고 기초대사량 자체를 낮춰버려 결국 <b>요요가 오기 쉬운 체질</b>로 변하게 됩니다.<br><br>
                    지금 설정된 권장 칼로리는 몸의 대사율과 건강을 지키면서 <b>지방만 효과적으로 빠지도록 계산된 정밀한 수치</b>이니 안심하고 규칙적으로 챙겨 드셔도 됩니다! 👍
                    </div>
                    """, 
                    unsafe_html=True
                )
            
            st.divider()
            st.metric("오늘의 목표 권장 칼로리", f"{daily_calorie} kcal")
            st.metric("현재 총 섭취량", f"{total} kcal", delta=total - daily_calorie, delta_color="inverse")

        st.divider()

        tab1, tab2 = st.tabs(["🏃 AI 목표 시간 맞춤형 다중 기구 루틴", "📅 나의 누적 다이어트 일지"])

        with tab1:
            st.write("🤖 **수룡이 AI 스포츠 닥터의 부위별 기구 다중 분배 시스템**")

            st.subheader("📋 오늘의 환경 및 신체 컨디션")
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1:
                select_date = st.date_input("기록 날짜", datetime.now().date())
            with col_ex2:
                ex_place = st.radio("오늘의 운동 장소", ["헬스장", "홈트"], key="main_ex_place_v12")
            with col_ex3:
                user_condition = st.selectbox("현재 나의 컨디션", ["최상 (에너지 넘침)", "정상 (보통)", "피곤함 (가벼운 운동 필요)", "근육통 있음"], key="main_condition_v12")

            muscle_gym_part = "상체만 진행"
            if ex_place == "헬스장" and goal == "근육증가":
                st.write("")
                st.subheader("🔀 오늘 진행할 분할 루틴 선택")
                muscle_gym_part = st.radio(
                    "오늘은 상체 and 하체 중 어느 부위를 집중 타겟팅하시겠습니까?", 
                    ["상체만 진행", "하체만 진행"], 
                    key="muscle_gym_part_selector_v12",
                    horizontal=True
                )

            st.write("")
            st.subheader("⏱️ 오늘 운동에 투자할 총 시간 설정")
            target_total_time = st.slider("오늘은 총 몇 분 동안 운동을 진행하시겠습니까?", 20, 180, 50, step=5, key="main_time_slider_v12")

            st.divider()

            condition_multiplier = 1.0
            if user_condition == "최상 (에너지 넘침)":
                condition_multiplier = 1.2
                st.success("🚀 **컨디션 최상 버프 가동!** 신체 에너지가 완벽하므로 다중 기구의 중량/세트 목표가 상향되며 칼로리 소모 보너스가 부여됩니다!")
            elif user_condition == "정상 (보통)":
                condition_multiplier = 1.0
                st.info("🟢 **정상 컨디션 가동:** 무리 없는 부위별 정석 기구 로테이션과 표준 휴식 템포를 제공합니다.")
            else:
                condition_multiplier = 0.8
                st.warning("🩹 **안전 제일 리커버리 모드 전환:** 근골격계 부담 완화를 위해 저중량 고립 및 릴렉스 순환 루틴으로 전환되었습니다.")

            ai_prescribed_exercises = []
            ai_prescribed_calories = 0
            
            safe_prefix = f"v12_{ex_place}_{goal}_{user_condition}_{muscle_gym_part}".replace(" ", "_").replace("(", "").replace(")", "")

            with st.container():
                if ex_place == "홈트":
                    sub_goal = "근육증가" if goal == "근육증가" else "감량"
                    
                    if sub_goal == "감량":
                        st.markdown(f"### 🏃 **[목표: {goal}]** 컨디션 맞춤형 홈트레이닝 유산소 타임라인")
                        raw_pool = exercise_presets["홈트"]["감량"].get(user_condition, exercise_presets["홈트"]["감량"]["정상 (보통)"])
                        
                        has_youtube = user_condition in ["최상 (에너지 넘침)", "정상 (보통)"]
                        if not has_youtube:
                            current_pool = [item for item in raw_pool if "url" not in item]
                        else:
                            current_pool = list(raw_pool)

                        num_exercises = len(current_pool)
                        
                        for idx, item in enumerate(current_pool):
                            st.markdown("---")
                            if "url" in item and has_youtube:
                                time_per_ex = 20
                                st.markdown(f"## 🏃 {idx+1}단계 유산소 트랙 (필수 고정): {item['name']}")
                                st.markdown(f"  - ⏱️ 집중 수행 시간: **{time_per_ex}분**")
                            else:
                                if has_youtube:
                                    rem_time = max(5, target_total_time - 20)
                                    time_per_ex = max(5, round(rem_time / (num_exercises - 1)))
                                else:
                                    time_per_ex = max(5, round(target_total_time / max(1, num_exercises)))
                                    
                                st.markdown(f"## 🏃 {idx+1}단계 유산소 트랙: {item['name']}")
                                st.markdown(f"  - ⏱️ 집중 수행 시간: **{time_per_ex}분**")
                                
                            st.markdown(f"  - 📊 페이스 가이드: **{item['guide']}** | {item['rest']}")
                            
                            if "url" in item and has_youtube:
                                st.video(item["url"])
                                st.info(f"🔗 [유튜브 앱에서 직접 보기]({item['url']})")
                                
                            with st.expander("💡 유산소 효과 배가 꿀팁", key=f"exp_{safe_prefix}_home_cardio_{idx}"):
                                st.caption(item["tip"])
                                
                            ai_prescribed_exercises.append(item['name'])
                            ai_prescribed_calories += round((time_per_ex / 10) * item["cal_10m"] * condition_multiplier)
                    
                    else:
                        st.markdown(f"### 🏠 오늘 신체 컨디션에 맞춘 {sub_goal} 전신 홈트레이닝")
                        current_pool = exercise_presets["홈트"]["근육증가"].get(user_condition, exercise_presets["홈트"]["근육증가"]["정상 (보통)"])
                        time_per_ex = max(5, round(target_total_time / len(current_pool)))
                        
                        for idx, item in enumerate(current_pool):
                            st.markdown("---")
                            st.markdown(f"## 🎯 {idx+1}단계 코스: {item['name']}")
                            st.markdown(f"  - ⏱️ 추천 할당 시간: **{time_per_ex}분**")
                            st.markdown(f"  - 📊 수행 가이드: **{item['guide']}** | {item['rest']}")
                            with st.expander("📖 정석 자세 및 부상방지 꿀팁", key=f"exp_{safe_prefix}_home_muscle_{idx}"):
                                st.caption(item["tip"])
                            ai_prescribed_exercises.append(item['name'])
                            ai_prescribed_calories += round((time_per_ex / 10) * item["cal_10m"] * condition_multiplier)

                else: 
                    pool_dict = gym_split_presets.get(user_condition, gym_split_presets["정상 (보통)"])
                    
                    if goal == "근육증가":
                        if muscle_gym_part == "상체만 진행":
                            st.markdown(f"### 🏋️ **[목표: 근육증가 - 상체 분할]** 오늘 진행하는 4종 상체 기구 집중 타겟 라인")
                            target_list = pool_dict.get("상체", [])
                        else:
                            st.markdown(f"### 🏋️ **[목표: 근육증가 - 하체 분할]** 오늘 진행하는 4종 하체 기구 집중 타겟 라인")
                            target_list = pool_dict.get("하체", [])

                        time_per_machine = max(4, round(target_total_time / len(target_list))) if target_list else target_total_time
                        st.markdown("---")
                        
                        for idx, item in enumerate(target_list):
                            st.markdown(f"### 🔹 {item['name']}")
                            st.markdown(f"  - ⏱️ 권장 할당 시간: **{time_per_machine}분**")
                            st.markdown(f"  - 📊 수행 가이드: **{item['guide']}** | {item['rest']}")
                            with st.expander(f"💡 {item['name']} 기구 사용 가이드", key=f"exp_{safe_prefix}_gym_muscle_{idx}"):
                                st.caption(item["tip"])
                            ai_prescribed_exercises.append(item['name'])
                            ai_prescribed_calories += round((time_per_machine / 10) * item["cal_10m"] * condition_multiplier)
                            st.write("")
                                
                    else:
                        st.markdown(f"### 🏃 **[목표: {goal}]** 컨디션 맞춤형 고효율 다중 유산소 트랙")
                        cardio_list = pool_dict.get("유산소", [])
                        num_cardio = len(cardio_list) if len(cardio_list) > 0 else 1
                        time_per_ex = max(5, round(target_total_time / num_cardio))
                        
                        for idx, item in enumerate(cardio_list):
                            st.markdown("---")
                            st.markdown(f"## 🏃 {idx+1}단계 유산소 트랙: {item['name']}")
                            st.markdown(f"  - ⏱️ 집중 수행 시간: **{time_per_ex}분**")
                            st.markdown(f"  - 📊 페이스 가이드: **{item['guide']}** | {item['rest']}")
                            with st.expander("💡 유산소 효과 배가 꿀팁", key=f"exp_{safe_prefix}_gym_cardio_{idx}"):
                                st.caption(item["tip"])
                            ai_prescribed_exercises.append(item['name'])
                            ai_prescribed_calories += round((time_per_ex / 10) * item["cal_10m"] * condition_multiplier)
                            st.write("")

            st.divider()

            st.subheader("🏋️ 오늘 실제로 완료한 운동 체크")
            use_ai_routine = st.checkbox("✅ 오늘 AI가 추천해 준 균형 있는 다중 기구 루틴을 그대로 완료했습니다!", value=False, key="checkbox_ai_routine_v12")

            actual_burned_calories = 0
            actual_time_sum = 0
            ex_summary = ""

            if use_ai_routine:
                actual_time_sum = target_total_time
                actual_burned_calories = ai_prescribed_calories
                part_tag = f"[{muscle_gym_part}] " if (ex_place == "Helvetica" and goal == "근육증가") else ""
                ex_summary = f"[{user_condition}/{goal}] " + part_tag + ", ".join(ai_prescribed_exercises)
                st.info(f"✨ 연동 완료: 설정하신 총 **{actual_time_sum}분** 운동, 총 **{actual_burned_calories} kcal** 소모로 정밀 연산되었습니다!")
            else:
                st.caption("특정 기구만 따로 골라서 시간을 입력하려면 아래 리스트를 활용하세요.")
                grand_pool = [
                    "렛 풀 다운 (등 광배근 타겟)", "체스트 프레스 머신 (대흉근 타겟)", 
                    "시티드 케이블 로우 (등 중하부 타겟)", "덤벨 숄더 프레스 (어깨 전면/측면 타겟)",
                    "레그 프레스 머신 (대퇴사두 및 둔근)", "바벨 백 스쿼트 (하체 전신 코어)",
                    "레그 익스텐션 머신 (허벅지 앞쪽 고립)", "시티드 레그 컬 머신 (허벅지 뒤쪽 햄스트링)",
                    "천국의 계단 (스텝밀)", "트레드밀 (러닝머신)", "전신 다이어트 최고의 운동 [칼소폭 찐 핵핵핵 매운맛]"
                ]
                actual_done_list = st.multiselect("오늘 실제 마친 항목들을 골라주세요.", grand_pool, key="manual_select_ex_v12")
                
                if actual_done_list:
                    for ex_name in actual_done_list:
                        done_time = st.slider(f"[{ex_name}] 수행 시간(분)", 0, 180, 15, key=f"fix_time_v12_{ex_name}")
                        actual_burned_calories += round((done_time / 10) * 65 * condition_multiplier)
                        actual_time_sum += done_time
                    ex_summary = f"[{user_condition}/수동] " + ", ".join(actual_done_list)

            if use_ai_routine or (not use_ai_routine and 'actual_done_list' in locals() and actual_done_list):
                st.divider()
                st.subheader("🔥 당일 실전 운동 최종 정산 스코어")
                col_res1, col_res2 = st.columns(2)
                col_res1.metric("총 결산 운동 시간", f"{actual_time_sum} 분")
                col_res2.metric("수룡이 인증 소모 칼로리", f"{actual_burned_calories} kcal")

            st.divider()
            st.subheader("💾 최종 운동 기록 세이브")
            if st.button("🔥 정산된 수치로 최종 저장하고 수룡이 경험치 받기", key="btn_save_exercise_v12"):
                if not use_ai_routine and ('actual_done_list' not in locals() or not actual_done_list):
                    st.error("완료한 운동 수치가 정산되지 않았습니다.")
                else:
                    current_time_str = datetime.now().strftime("%H:%M")
                    formatted_date = f"{select_date.strftime('%Y-%m-%d')} {current_time_str}"

                    food_log_text = ", ".join(checked_items_summary + selected_foods)
                    if custom_food_name:
                        food_log_text += f" | [직접입력] {custom_food_name}({custom_food_cal}kcal)"

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
                    st.success(f"🎉 성공! 지정 분할 기구 조합이 로그에 누적되었으며, 경험치 10 EXP가 지급되었습니다!")

        with tab2:
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
                            selected_chart_date = st.selectbox("날짜를 클릭하세요", options=available_dates, index=len(available_dates)-1, key="chart_date_selector_v12")
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
                except:
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
                if st.checkbox("⚠️ 전체 기록 지우기", key="delete_all_logs_check_v12"):
                    if st.button("정말 삭제하시겠습니까?", key="btn_delete_logs_confirm_v12"):
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
    if st.checkbox("⚠️ 수룡이 경험치 초기화 활성화", key="reset_exp_check_v12"):
        if st.button("💥 수룡이를 다시 알(🥚)로 되돌리기", type="primary", key="btn_reset_exp_v12"):
            if os.path.exists(GROW_FILE):
                os.remove(GROW_FILE)
            st.warning("수룡이의 경험치가 완전히 초기화되었습니다!")


# --- 멀티페이지 내비게이션 구성 ---
pg = st.navigation([
    st.Page(show_main_page, title="📊 다이어트 다이어리", icon="📝"),
    st.Page(show_growth_page, title="🐉 수룡이 알 키우기", icon="🥚")
])
pg.run()
