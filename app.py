import streamlit as st
import requests
import json
import os

# ================= 1. 核心配置 (代理与模型) =================
# 强制让 Python 走 Clash 代理 (双重保险)
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 页面基础配置
st.set_page_config(
    page_title="Project Cupid: Game Theory Engine",
    page_icon="🧩",
    layout="wide"
)

# 获取 API Key
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("请输入 Google API Key:", type="password")

# ================= 2. 定义稳定的 REST API 请求函数 =================
def ask_gemini_rest(prompt, key):
   # 👇 换成 2.0 Flash：兼顾高智商与极速响应
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
   # 发送请求 (延长到120秒，给 Pro 模型足够的运算时间)
    response = requests.post(url, headers=headers, json=data, timeout=120)
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        # 如果出错，返回错误代码方便调试
        return f"❌ Error {response.status_code}: {response.text}"

# ================= 3. 侧边栏：经典案例库 =================
st.sidebar.header("📚 Load Case Study (加载案例)")
st.sidebar.info("选择一个经典博弈场景，或者在右侧输入你自己的故事。")

case_options = {
    "None (Custom Input)": "",
    
    "1. The Bedroom Lock (Boundaries vs. Face)": """My brother in-law (Sammy) lost his home and moved in with us along with his twin daughters. They have no respect for my daughter Zoey's privacy and kept taking her things. Zoey bought a $60 makeup kit and one of the twins ruined it. My wife and Sammy saw no issue, saying 'girls borrow stuff.'
I installed a lock on Zoey's door. Sammy and his daughters were upset. My wife shamed me for putting a lock on Zoey's door, saying it prevents them from 'spending time' with her and implies we want to kick them out. She demanded I remove it, but I said the lock stays until they leave. Now everyone is giving me the silent treatment.""",
    
    "2. The Medical Bill (Efficiency vs. Norms)": """My boyfriend went to the ER and got a $5000 bill. I offered to fight it. I went all-out: emailed the hospital board, investors, and management daily, pointing out their price gouging.
Result: The bill was dropped to $26. I saved us nearly $5000.
However, my boyfriend was furious. He looked at my emails and said I 'went too far' and 'harassed' the hospital. He said he authorized me to dispute the bill, not threaten the board. He is mad at me for being a hardass, even though I saved our holiday plans.""",

    "3. The Bacon Standoff (Values Conflict)": """My 14-year-old daughter decided to go vegan. I supported her, bought her special food and pans. But recently, she exploded because I cooked bacon in a 'family pan' (not hers).
She demanded I buy her separate pans, which I did. Now, she says the dishwasher is 'contaminated' and the fridge has 'bacon grease fingers' on it. She and my wife want me to completely stop cooking meat at home. I refused. I said I will not stop eating bacon in my own house. Now there is huge tension."""
}

selected_case = st.sidebar.selectbox(
    "Select a scenario:",
    options=list(case_options.keys())
)

# ================= 4. 主界面 UI =================
st.title("🧩 Dyadic Conflict Resolution Engine")
st.caption("Powered by Gemini 2.5 Pro | Inverse Game Theory & Mechanism Design")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    # 自动填入案例内容
    initial_text = case_options[selected_case]
    story = st.text_area(
        "Context Input (请输入冲突故事):",
        value=initial_text,
        height=300,
        placeholder="Paste your story here..."
    )
    
    analyze_btn = st.button("🚀 Analyze Conflict (启动博弈分析)", type="primary")

with col2:
    if analyze_btn:
        if not api_key:
            st.error("⚠️ 请先配置 API Key！")
        elif not story:
            st.error("⚠️ 请先输入或选择一个故事！")
        else:
            with st.spinner("🧮 Running Nash Equilibrium Analysis on Gemini 2.0 flash..."):
                try:
                    # === 核心学术 Prompt ===
                    # === 核心 Prompt (优化版：极简 + Markdown表格) ===
                    prompt = f"""
                    Role: Expert Game Theorist.
                    Task: Analyze this relationship conflict: "{story}"
                    
                    Constraint: Be EXTREMELY CONCISE. No fluff. Use bullet points.
                    
                    Output exactly in this format:
                    
                    ### 1. The Payoff Matrix
                    (Use a standard Markdown Table. Do NOT use LaTeX arrays.)
                    | | Partner: Cooperate | Partner: Defect |
                    |---|---|---|
                    | **User: Cooperate** | (U, P) | (U, P) |
                    | **User: Defect** | (U, P) | (U, P) |
                    
                    *(Briefly state the conflict type, e.g., "Prisoner's Dilemma" or "Chicken Game", in 1 sentence.)*
                    
                    ### 2. Nash Equilibrium
                    * **State:** [User Strategy, Partner Strategy]
                    * **Reason:** (Explain in 1 sentence why they are stuck here.)
                    
                    ### 3. Inverse Game Theory (Hidden Parameter)
                    * **Inference:** (e.g., "Partner's 'Face-Saving' utility > Relationship utility")
                    * **Evidence:** (Cite 1 specific behavior from text)
                    
                    ### 4. Mechanism Design (Solution)
                    * **Action 1:** (Specific move to change payoffs)
                    * **Action 2:** (Specific move to change payoffs)
                    """
                    
                    # 调用 REST API 函数
                    result_text = ask_gemini_rest(prompt, api_key)
                    
                    st.success("✅ Analysis Complete")
                    st.markdown(result_text)
                    
                except Exception as e:
                    st.error(f"System Error: {e}")

    elif not analyze_btn:
        st.info("👈 Select a case study or type your own story to see the Game Theory model.")