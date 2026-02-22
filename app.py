import streamlit as st
import time
import random
import streamlit.components.v1 as components

# --- 1. 설정 및 데이터 ---
LIMITS = {"단어": 35, "단문": 12, "장문": 7, "Word": 35, "Short": 12, "Long": 7}

DATA = {
    "한글": {
        "단어": ["사과", "바다", "하늘", "고구마", "파이썬", "키보드", "자동차", "우주", "행복", "산책", "구름", "나무", "커피", "노트북", "포도", "의자", "책상", "안경", "시계", "전화기"],
        "단문": ["간장 공장 공장장은 강 공장장이다.", "오늘 날씨가 정말 화창하네요.", "작은 토끼가 산 위에서 밤새도록 춤을 춥니다.", "독서는 마음의 양식입니다.", "파이썬으로 웹 서비스를 만듭니다.", "끝까지 포기하지 않는 사람이 성공합니다.", "지나간 일은 잊고 내일을 준비합시다.", "성공은 매일 반복되는 작은 노력의 합산입니다."],
        "장문": ["대한민국은 민주공화국이다. 대한민국의 주권은 국민에게 있고, 모든 권력은 국민으로부터 나온다.", "국가는 전통문화의 계승·발전과 민족문화의 창달에 노력하여야 한다. 모든 국민은 신체의 자유를 가진다.", "모든 국민은 법 앞에 평등하다. 누구든지 성별·종교 또는 사회적 신분에 의하여 차별을 받지 아니한다."]
    },
    "English": {
        "Word": ["Apple", "Ocean", "Sky", "Python", "Keyboard", "Coffee", "Universe", "Happy", "Cloud", "Mouse", "Programming", "Code", "Water", "Forest", "Music"],
        "Short": ["The quick brown fox jumps over the lazy dog.", "Practice makes perfect.", "Stay hungry, stay foolish.", "Believe in yourself.", "Coding is a superpower.", "Life is what happens when you are busy making other plans."],
        "Long": ["The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle.", "Success is not final, failure is not fatal: it is the courage to continue that counts."]
    }
}

# --- 2. 세션 상태 관리 ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

def init_session(lang, mode):
    all_sentences = DATA[lang][mode]
    limit = LIMITS[mode]
    # 문장 개수가 부족하면 보충
    selected = [random.choice(all_sentences) for _ in range(limit)]
    
    st.session_state.current_set = selected
    st.session_state.current_idx = 0
    st.session_state.total_chars = 0
    st.session_state.start_time_total = None
    st.session_state.is_completed = False
    st.session_state.input_key = 0
    st.session_state.initialized = True

# --- 3. UI 설정 ---
st.set_page_config(page_title="Speed Typer", page_icon="⌨️")

st.title("⌨️ 무한 타자 연습 (No Mouse)")

with st.sidebar:
    st.header("⚙️ 설정")
    lang = st.selectbox("언어", ["한글", "English"])
    mode_options = ["단어", "단문", "장문"] if lang == "한글" else ["Word", "Short", "Long"]
    mode = st.selectbox("모드", mode_options)
    if st.button("연습 시작/리셋") or not st.session_state.initialized:
        init_session(lang, mode)
        st.rerun()

# --- 4. 연습 로직 ---
if st.session_state.is_completed:
    # 모든 세트 완료 후 결과 창
    total_time = st.session_state.finish_time - st.session_state.start_time_total
    avg_cpm = int((st.session_state.total_chars / total_time) * 60)
    
    st.balloons()
    st.success(f"🎊 {mode} 모드 완료!")
    st.metric("평균 타수", f"{avg_cpm} CPM")
    st.metric("총 소요 시간", f"{total_time:.2f} 초")
    
    if st.button("한 번 더 하기"):
        init_session(lang, mode)
        st.rerun()
else:
    # 진행 중
    idx = st.session_state.current_idx
    limit = LIMITS[mode]
    target_text = st.session_state.current_set[idx]

    st.write(f"**문제 {idx + 1} / {limit}**")
    st.progress((idx) / limit)

    # 목표 문장 표시
    st.markdown(f"""
    <div style='font-size: 1.5rem; border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: black; line-height: 1.6;'>
        {target_text}
    </div>
    """, unsafe_allow_html=True)

    # 입력창 (Key를 바꿔서 이전 내용을 지움)
    user_input = st.text_input(
        "", 
        key=f"input_{st.session_state.input_key}",
        placeholder="여기에 타이핑 후 엔터"
    )

    # 오타 강조 처리
    if user_input:
        if st.session_state.start_time_total is None:
            st.session_state.start_time_total = time.time()

        # 실시간 색상 피드백
        colored_text = ""
        for i, char in enumerate(target_text):
            if i < len(user_input):
                if char == user_input[i]:
                    colored_text += f'<span style="color: grey;">{char}</span>'
                else:
                    colored_text += f'<span style="color: red; font-weight: bold; background-color: #ffcccc;">{char}</span>'
            else:
                colored_text += f'<span>{char}</span>'
        st.markdown(f"<div style='font-size: 1.4rem; font-family: monospace;'>{colored_text}</div>", unsafe_allow_html=True)

        # 정답일 때 엔터 치면 (Enter는 st.text_input에서 기본 동작) 바로 다음으로
        if user_input == target_text:
            st.session_state.total_chars += len(target_text)
            st.session_state.current_idx += 1
            st.session_state.input_key += 1
            
            if st.session_state.current_idx >= limit:
                st.session_state.finish_time = time.time()
                st.session_state.is_completed = True
            
            st.rerun()

# --- 5. 커서를 입력창으로 강제 이동시키는 JS ---
components.html(
    f"""
    <script>
    function focusInput() {{
        var inputs = window.parent.document.querySelectorAll('input[type="text"]');
        if (inputs.length > 0) {{
            // 가장 마지막에 생성된 입력창(현재 문제의 키를 가진 창)에 포커스
            inputs[inputs.length - 1].focus();
        }}
    }}
    // Streamlit 렌더링 완료 후 실행되도록 지연 처리
    setTimeout(focusInput, 150);
    </script>
    """,
    height=0,
)

st.divider()
st.caption("Enter를 누르면 다음 문장으로 자동 이동하며 커서가 유지됩니다. (마우스 불필요)")
