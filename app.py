import streamlit as st
import time
import random
import json
import streamlit.components.v1 as components

# --- 1. 설정 및 데이터 ---
LIMITS = {"단어": 35, "단문": 12, "장문": 7, "Word": 35, "Short": 12, "Long": 7}

DATA = {
    "한글": {
        "단어": ["사과", "바다", "하늘", "고구마", "파이썬", "키보드", "자동차", "우주", "행복", "산책", "구름", "나무", "커피", "노트북", "포도", "의자", "책상", "안경", "시계", "전화기", "무지개", "태양", "비행기", "고향", "가족", "친구", "음악", "영화", "학교", "병원", "시장", "별", "달", "해바라기", "김치", "비빔밥", "불고기", "냉면", "떡볶이"],
        "단문": [
            "간장 공장 공장장은 강 공장장이다.", "오늘 날씨가 정말 화창하네요.", "작은 토끼가 산 위에서 밤새도록 춤을 춥니다.", "독서는 마음의 양식입니다.", "파이썬으로 웹 서비스를 만듭니다.", "끝까지 포기하지 않는 사람이 성공합니다.", "지나간 일은 잊고 내일을 준비합시다.", "성공은 매일 반복되는 작은 노력의 합산입니다.",
            "내일은 오늘보다 더 나은 날이 될 것입니다.", "포기하지 말고 꿈을 향해 나아가세요.", "당신의 노력이 언젠가는 빛을 발할 것입니다.", "소중한 사람들과 함께 행복한 시간을 보내세요.", "건강이 가장 큰 재산입니다.", "항상 긍정적인 마음가짐을 가지세요.", "새로운 도전을 두려워하지 마세요.", "배움에는 끝이 없습니다."
        ],
        "장문": [
            "대한민국은 민주공화국이다. 대한민국의 주권은 국민에게 있고, 모든 권력은 국민으로부터 나온다.", "국가는 전통문화의 계승·발전과 민족문화의 창달에 노력하여야 한다. 모든 국민은 신체의 자유를 가진다.", "모든 국민은 법 앞에 평등하다. 누구든지 성별·종교 또는 사회적 신분에 의하여 차별을 받지 아니한다.",
            "국민의 자유와 권리는 헌법에 열거되지 아니한 이유로 경시되지 아니한다.", "모든 국민은 거주·이전의 자유를 가진다. 모든 국민은 주거의 자유를 침해받지 아니한다.", "국가는 재해를 예방하고 그 위험으로부터 국민을 보호하기 위하여 노력하여야 한다."
        ]
    },
    "English": {
        "Word": ["apple", "ocean", "sky", "python", "keyboard", "coffee", "universe", "happy", "cloud", "mouse", "programming", "code", "water", "forest", "music", "banana", "camera", "desktop", "exercise", "flower", "guitar", "health", "island", "jungle", "laptop", "mountain", "nature", "orange", "picnic", "rainbow", "sunrise", "umbrella", "valley", "zebra", "architecture"],
        "Short": [
            "the quick brown fox jumps over the lazy dog.", "practice makes perfect.", "stay hungry, stay foolish.", "believe in yourself.", "coding is a superpower.", "life is what happens when you are busy making other plans.",
            "don't count the days, make the days count.", "the best way to predict the future is to create it.", "it always seems impossible until it's done.", "quality is not an act, it is a habit.", "dream big and dare to fail.", "success usually comes to those who are too busy to be looking for it."
        ],
        "Long": [
            "the only way to do great work is to love what you do. if you haven't found it yet, keep looking. don't settle.", "success is not final, failure is not fatal: it is the courage to continue that counts.",
            "in the end, it's not the years in your life that count. it's the life in your years.", "excellence is never an accident. it is always the result of high intention, sincere effort, and intelligent execution; it represents the wise choice of many alternatives."
        ]
    }
}

# --- 2. 세션 상태 관리 ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

def init_session(lang, mode):
    all_sentences = DATA[lang][mode]
    # 영어의 경우 모든 텍스트를 소문자로 변환 (사용자 요청)
    if lang == "English":
        all_sentences = [s.lower() for s in all_sentences]
        
    limit = LIMITS[mode]
    
    # 중복 없이 섞기
    shuffled = all_sentences.copy()
    random.shuffle(shuffled)
    
    # 데이터가 부족하면 부족한 만큼 더 채우기
    while len(shuffled) < limit:
        extra = all_sentences.copy()
        random.shuffle(extra)
        shuffled.extend(extra)
        
    st.session_state.current_set = shuffled[:limit]
    st.session_state.initialized = True
    st.session_state.game_finished = False

# --- 3. UI 설정 ---
st.set_page_config(page_title="Speed Typer Pro", page_icon="⌨️", layout="centered")

st.title("⌨️ 무한 타자 연습 (No Mouse)")

with st.sidebar:
    st.header("⚙️ 설정")
    lang = st.selectbox("언어", ["한글", "English"])
    mode_options = ["단어", "단문", "장문"] if lang == "한글" else ["Word", "Short", "Long"]
    mode = st.selectbox("모드", mode_options)
    if st.button("연습 시작/리셋") or not st.session_state.initialized:
        init_session(lang, mode)
        st.rerun()

# --- 4. 엔진 (Custom Web Component) ---
def typing_engine(sentences):
    sentences_json = json.dumps(sentences)
    
    html_code = f"""
    <div id="typing-root" style="font-family: 'Malgun Gothic', sans-serif; max-width: 800px; margin: auto;">
        <div id="progress-bar" style="width: 100%; height: 5px; background: #eee; border-radius: 5px; margin-bottom: 20px;">
            <div id="progress-inner" style="width: 0%; height: 100%; background: #4CAF50; border-radius: 5px; transition: width 0.3s;"></div>
        </div>
        
        <div id="status-text" style="font-size: 0.9rem; color: #666; margin-bottom: 10px;">문제 1 / {len(sentences)}</div>
        
        <div id="target-box" style="font-size: 1.6rem; border: 2px solid #4CAF50; padding: 25px; border-radius: 12px; background-color: #fcfcfc; color: #333; line-height: 1.6; min-height: 60px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div id="target-text"></div>
        </div>

        <input type="text" id="typing-input" autocomplete="off" placeholder="여기에 타이핑 후 Enter"
               style="width: 100%; padding: 15px; font-size: 1.4rem; border: 2px solid #ddd; border-radius: 10px; outline: none; transition: all 0.2s; box-sizing: border-box;">
        
        <div id="feedback-box" style="font-size: 1.4rem; font-family: monospace; margin-top: 15px; min-height: 30px; letter-spacing: 1px;"></div>
    </div>

    <script>
    const sentences = {sentences_json};
    let currentIdx = 0;
    let totalChars = 0;
    let startTime = null;

    const targetTextEl = document.getElementById('target-text');
    const inputEl = document.getElementById('typing-input');
    const feedbackEl = document.getElementById('feedback-box');
    const progressEl = document.getElementById('progress-inner');
    const statusEl = document.getElementById('status-text');

    function updateSentence() {{
        if (currentIdx >= sentences.length) {{
            finishGame();
            return;
        }}
        targetTextEl.textContent = sentences[currentIdx];
        inputEl.value = '';
        feedbackEl.innerHTML = '';
        statusEl.textContent = `문제 ${{currentIdx + 1}} / ${{sentences.length}}`;
        progressEl.style.width = `${{(currentIdx / sentences.length) * 100}}%`;
        
        // 브라우저 네이티브 포커스 강제 (안정적)
        setTimeout(() => inputEl.focus(), 10);
    }}

    function finishGame() {{
        const endTime = Date.now();
        const totalTime = (endTime - startTime) / 1000;
        const cpm = Math.round((totalChars / totalTime) * 60);
        
        document.getElementById('typing-root').innerHTML = `
            <div style="text-align: center; padding: 40px; background: #e8f5e9; border-radius: 20px;">
                <h2 style="color: #2e7d32;">🎊 연습 완료!</h2>
                <div style="font-size: 2.5rem; font-weight: bold; margin: 20px 0;">${{cpm}} <span style="font-size: 1rem;">CPM</span></div>
                <p style="color: #666;">총 소요 시간: ${{totalTime.toFixed(2)}}초</p>
                <button onclick="parent.location.reload()" style="background: #4CAF50; color: white; border: none; padding: 10px 25px; border-radius: 5px; cursor: pointer; font-size: 1rem;">다시 하기</button>
            </div>
        `;
    }}

    inputEl.addEventListener('input', (e) => {{
        if (!startTime) startTime = Date.now();
        
        const target = sentences[currentIdx];
        const val = e.target.value;
        let html = '';
        
        for (let i = 0; i < target.length; i++) {{
            if (i < val.length) {{
                if (target[i] === val[i]) {{
                    html += `<span style="color: grey;">${{target[i]}}</span>`;
                }} else {{
                    html += `<span style="color: red; font-weight: bold; background: #ffcccc;">${{target[i]}}</span>`;
                }}
            }} else {{
                html += `<span>${{target[i]}}</span>`;
            }}
        }}
        feedbackEl.innerHTML = html;

        // 정답 체크 (실시간 다음 단계 이동)
        if (val === target) {{
            totalChars += target.length;
            currentIdx++;
            updateSentence();
        }}
    }});

    // 초기 포커스 및 상시 포커스 유지 처리
    inputEl.focus();
    document.addEventListener('click', () => inputEl.focus());
    
    // 스타일 포커스 피드백
    inputEl.addEventListener('focus', () => {{
        inputEl.style.borderColor = '#4CAF50';
        inputEl.style.boxShadow = '0 0 10px rgba(76, 175, 80, 0.3)';
    }});
    inputEl.addEventListener('blur', () => {{
        inputEl.style.borderColor = '#ddd';
        inputEl.style.boxShadow = 'none';
        // 강제로 포커스 복구 (단, 사용자가 다른 조작을 할 때는 방해되지 않게 지연)
        setTimeout(() => inputEl.focus(), 100);
    }});

    updateSentence();
    </script>
    """
    components.html(html_code, height=450)

if st.session_state.initialized:
    typing_engine(st.session_state.current_set)

st.divider()
st.caption("이 버전은 브라우저 엔진을 직접 컨트롤하여 '마우스 없는 환경'에 최적화되어 있습니다.")