// 1. 앱 내에 저장된 추천 식단 데이터 (각 식단에는 'ingredients' 태그가 포함되어 있음)
const dietMenuDatabase = [
  {
    id: 1,
    name: "닭가슴살 샐러드",
    ingredients: ["닭가슴살", "양상추", "오이", "방울토마토"],
    calories: 350
  },
  {
    id: 2,
    name: "소고기 미역국과 현미밥",
    ingredients: ["소고기", "미역", "현미밥", "마늘"],
    calories: 450
  },
  {
    id: 3,
    name: "연어 구이와 아스파라거스",
    ingredients: ["연어", "아스파라거스", "올리브유"],
    calories: 500
  },
  {
    id: 4,
    name: "그릭 요거트 볼",
    ingredients: ["그릭요거트", "바나나", "꿀", "아몬드"],
    calories: 250
  }
];

/**
 * 2. 싫어하는 음식을 걸러내고 식단을 추천해주는 함수
 * @param {Array} userDislikedIngredients - 사용자가 체크박스/자동완성으로 선택한 싫어하는 음식 리스트
 * @returns {Array} 필터링된 식단 리스트
 */
function getRecommendedDiets(userDislikedIngredients) {
  // 식단 DB에서 싫어하는 음식을 포함하지 않는 식단만 걸러냅니다.
  return dietMenuDatabase.filter(menu => {
    // 식단의 원재료 중 사용자가 싫어하는 원재료가 하나라도 포함되어 있는지 확인
    const hasDislikedIngredient = menu.ingredients.some(ingredient => 
      userDislikedIngredients.includes(ingredient)
    );
    
    // 싫어하는 원재료가 '없는' 것만 남김 (false여야 pass)
    return !hasDislikedIngredient;
  });
}

// ==========================================
// 3. 실제 적용 및 테스트 호출
// ==========================================

// 예시 A: 사용자가 체크박스에서 '오이'를 선택한 경우
const userA_dislikes = ["오이"];
const recommendationForA = getRecommendedDiets(userA_dislikes);

console.log("--- 오이를 싫어하는 유저 추천 식단 ---");
console.log(recommendationForA.map(m => m.name)); 
// 출력: [ '소고기 미역국과 현미밥', '연어 구이와 아스파라거스', '그릭 요거트 볼' ] (닭가슴살 샐러드 제외됨)


// 예시 B: 사용자가 견과류 알레르기가 있어서 '아몬드'를 선택한 경우
const userB_dislikes = ["아몬드"];
const recommendationForB = getRecommendedDiets(userB_dislikes);

console.log("\n--- 아몬드를 싫어하는 유저 추천 식단 ---");
console.log(recommendationForB.map(m => m.name)); 
// 출력: [ '닭가슴살 샐러드', '소고기 미역국과 현미밥', '연어 구이와 아스파라거스' ] (그릭 요거트 볼 제외됨)
