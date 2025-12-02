import streamlit as st
import requests
import json
import os

# ================= 1. 核心配置 =================
st.set_page_config(page_title="Project Cupid", page_icon="🧩", layout="wide")

# 获取 API Key
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("请输入 Google API Key:", type="password")

# ================= 2. 定义 REST API 函数 =================
def ask_gemini_rest(prompt, key):
    # 使用 gemini-2.0-flash (速度快，双语能力强)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# ================= 3. 侧边栏设置 =================
with st.sidebar:
    st.header("⚙️ Settings / 设置")
    
    # [关键功能] 语言切换开关
    language = st.radio("Output Language (输出语言)", ["English", "中文"], index=0)
    
    st.markdown("---")
    st.header("📚 Load Case / 加载案例")
    
    # 案例库 (保持英文原文，因为训练数据是英文的，AI 能读懂)
    case_options = {
        "None (Custom Input)": "",
        "1. The Bedroom Lock (Family Boundaries)": """My brother in-law (Sammy) lost his home and moved in with us along with his twin daughters. They have no respect for my daughter Zoey's privacy... (User installed lock, Wife is mad)""",
        "2. The Medical Bill (Money vs. Face)": """My boyfriend went to the ER and got a $5000 bill. I offered to fight it... Result: Bill dropped to $26... Boyfriend is furious I 'harassed' them.""",
        "3. The Vegan Daughter (Values Conflict)": """My 14-year-old daughter decided to go vegan... She exploded because I cooked bacon in a 'family pan'... She says dishwasher is contaminated."""
    }
    
    # 稍微恢复一下完整文本，方便演示效果
    full_text_map = {
        "1. The Bedroom Lock (Family Boundaries)": """My brother in-law (Sammy) lost his home and moved in with us along with his twin daughters. They have no respect for my daughter Zoey's privacy and kept taking her things. Zoey bought a $60 makeup kit and one of the twins ruined it. My wife and Sammy saw no issue. I installed a lock on Zoey's door. My wife shamed me for putting a lock on Zoey's door, saying it prevents them from 'spending time' with her and implies we want to kick them out. She demanded I remove it, but I said the lock stays until they leave. Now everyone is giving me the silent treatment.""",
        "2. The Medical Bill (Money vs. Face)": """My boyfriend went to the ER and got a $5000 bill. I offered to fight it. I went all-out: emailed the hospital board, investors, and management daily, pointing out their price gouging. Result: The bill was dropped to $26. I saved us nearly $5000. However, my boyfriend was furious. He looked at my emails and said I 'went too far' and 'harassed' the hospital. He said he authorized me to dispute the bill, not threaten the board. He is mad at me for being a hardass, even though I saved our holiday plans.""",
        "3. The Vegan Daughter (Values Conflict)": """My 14-year-old daughter decided to go vegan. I supported her, bought her special food and pans. But recently, she exploded because I cooked bacon in a 'family pan' (not hers). She demanded I buy her separate pans, which I did. Now, she says the dishwasher is 'contaminated' and the fridge has 'bacon grease fingers' on it. She and my wife want me to completely stop cooking meat at home. I refused. I said I will not stop eating bacon in my own house. Now there is huge tension."""
    }
    
    selected_case_label = st.selectbox("Select a scenario:", options=list(case_options.keys()))
    initial_text = full_text_map.get(selected_case_label, "")

# ================= 4. 主界面 UI (根据语言动态变化标题) =================
if language == "English":
    st.title("🧩 Dyadic Conflict Resolution Engine")
    st.caption("Based on Inverse Game Theory & Mechanism Design | SJTU Research Demo")
    input_label = "Context Input (Describe the conflict):"
    btn_label = "🚀 Analyze Conflict"
else:
    st.title("🧩 二元冲突博弈决策引擎")
    st.caption("基于逆向博弈论与机制设计 | 上海交通大学科研 Demo")
    input_label = "输入冲突背景 (可以直接粘贴中文或英文故事):"
    btn_label = "🚀 启动博弈分析"

st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    story = st.text_area(input_label, value=initial_text, height=300, placeholder="Paste your story here...")
    analyze_btn = st.button(btn_label, type="primary")

with col2:
    if analyze_btn:
        if not api_key:
            st.error("⚠️ API Key Missing / 缺失密钥")
        elif not story:
            st.error("⚠️ Input Story Missing / 请输入故事")
        else:
            with st.spinner("🧮 Calculating Nash Equilibrium..." if language == "English" else "🧮 正在构建博弈矩阵并计算纳什均衡..."):
                
                # === 核心逻辑：根据语言选择不同的 Prompt ===
                if language == "English":
                    # 英文 Prompt (原有逻辑)
                    prompt = f"""
                    Role: Expert Game Theorist.
                    Task: Analyze this relationship conflict: "{story}"
                    
                    Constraint: Be EXTREMELY CONCISE. Use Markdown tables.
                    
                    Output Structure:
                    ### 1. The Payoff Matrix
                    (Markdown Table showing strategies and utilities -10 to 10)
                    
                    ### 2. Nash Equilibrium
                    (Identify the deadlock state and why)
                    
                    ### 3. Inverse Game Theory (Personality Inference)
                    (Infer the partner's hidden parameter, e.g., 'Face-Saving' coefficient)
                    
                    ### 4. Mechanism Design
                    (Suggest a Pareto Improvement move)
                    """
                else:
                    # 中文 Prompt (交大汇报专用)
                    prompt = f"""
                    角色：博弈论与计算社会科学专家。
                    任务：分析以下亲密关系冲突案例："{story}"
                    
                    要求：
                    1. **语言**：必须使用**中文**回答。
                    2. **风格**：学术、理性、客观。使用 LaTeX 展示数学公式。
                    3. **简洁**：不要长篇大论，直接给出分析结果。
                    
                    输出格式：
                    
                    ### 1. 支付矩阵构建 (Payoff Matrix)
                    请构建一个 2x2 博弈矩阵（Markdown表格）。
                    - 定义双方策略（例如：强硬 vs 妥协）。
                    - 预估效用值（范围 -10 到 +10）。
                    
                    ### 2. 纳什均衡分析 (Nash Equilibrium)
                    - 识别当前的稳定状态（僵局）。
                    - 数学解释：为什么双方都无法单方面改变策略？
                    
                    ### 3. 逆向博弈推论 (Inverse Game Theory)
                    - 基于对方的非理性行为，反推其**隐性效用参数**（例如：“推测对方的‘面子系数’ $\\alpha > 8$，远高于‘解决问题’的效用”）。
                    
                    ### 4. 机制设计与优化 (Mechanism Design)
                    - 提出一个**帕累托改进 (Pareto Improvement)** 方案。
                    - 建议用户如何通过引入外部变量（如台阶、补偿）来改变博弈结构，从而打破僵局。
                    """
                
                result = ask_gemini_rest(prompt, api_key)
                st.success("Analysis Complete / 分析完成")
                st.markdown(result)
