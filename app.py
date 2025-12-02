import streamlit as st
import requests
import json
import os

# ================= 1. 核心配置 =================
# ⚠️ 注意：删除了 os.environ 代理设置
# Streamlit Cloud 在美国，不需要代理即可直连 Google
# 如果你在本地运行且需要代理，请在 VS Code 的 settings.json 里配置终端代理，不要写在代码里

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

# ================= 2. 定义 REST API 请求函数 =================
def ask_gemini_rest(prompt, key):
    # 使用 gemini-2.0-flash (速度快，适合 Demo)
    # 如果你想用更强的，可以改回 gemini-1.5-pro 或 2.5-pro
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# ================= 3. 侧边栏：经典案例库 =================
st.sidebar.header("📚 Load Case Study")
case_options = {
    "None (Custom Input)": "",
    "1. The Bedroom Lock": """My brother in-law (Sammy) lost his home... (省略，保持原样即可，为了代码简洁我这里缩略了，你保留原来的) ...""",
    # ... 保持你原来的案例内容 ...
}
# (为了方便你复制，这里我不重复那一长串案例了，下面的逻辑最重要)
# 你可以直接保留你原来的 case_options 字典内容

# 简化的案例引用 (请保留你原来的完整文本)
selected_case = st.sidebar.selectbox("Select a scenario:", ["None"] + ["1. The Bedroom Lock", "2. The Medical Bill", "3. The Bacon Standoff"])

# 简单的映射逻辑 (根据你的原始代码调整)
case_text_map = {
    "1. The Bedroom Lock": "My brother in-law (Sammy) lost his home...", 
    "2. The Medical Bill": "My boyfriend went to the ER...",
    "3. The Bacon Standoff": "My 14-year-old daughter decided to go vegan..."
}
initial_text = case_text_map.get(selected_case, "") if selected_case != "None" else ""


# ================= 4. 主界面 UI =================
st.title("🧩 Dyadic Conflict Resolution Engine")
st.caption("Powered by Google Gemini | Inverse Game Theory Demo")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    story = st.text_area(
        "Context Input:",
        value=initial_text,
        height=300,
        placeholder="Paste your story here..."
    )
    analyze_btn = st.button("🚀 Analyze Conflict", type="primary")

with col2:
    if analyze_btn:
        if not api_key:
            st.error("⚠️ 请先配置 API Key！")
        elif not story:
            st.error("⚠️ 请先输入故事！")
        else:
            with st.spinner("🧮 Running Game Theory Analysis..."):
                # === 核心 Prompt ===
                prompt = f"""
                Role: Expert Game Theorist.
                Task: Analyze this relationship conflict: "{story}"
                
                Constraint: Be EXTREMELY CONCISE. Use Markdown tables.
                
                ### 1. The Payoff Matrix
                (Create a Markdown Table showing strategies and estimated payoffs -10 to 10)
                
                ### 2. Nash Equilibrium
                (Identify the stable deadlock state)
                
                ### 3. Inverse Game Theory
                (Infer the partner's hidden personality parameter based on their irrational move)
                
                ### 4. Mechanism Design
                (Suggest 1 specific move to break the deadlock)
                """
                
                result = ask_gemini_rest(prompt, api_key)
                st.markdown(result)
