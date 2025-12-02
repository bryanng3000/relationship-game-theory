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
    
# -------------------------------------------------------
    # 1. 案例库定义 (保持英文键名，方便索引)
    # -------------------------------------------------------
    case_options = {
        "None (Custom Input)": "",
        
        # --- Reddit (Western Context) ---
        "1. The Bedroom Lock (Family Boundaries)": "Reddit: Husband installed lock on daughter's door...",
        "2. The Medical Bill (Money vs. Face)": "Reddit: Girlfriend negotiated hospital bill aggressively...",
        "3. The Vegan Daughter (Values Conflict)": "Reddit: Vegan daughter mad at dad for cooking bacon...",
        
        # --- Zhihu (Chinese Context) ---
        "4. 🇨🇳 [知乎] 彩礼博弈 (Bride Price Game)": "知乎: 女方要求涨彩礼至50万并买房...",
        "5. 🇨🇳 [知乎] 婆媳边界 (In-law Boundary)": "知乎: 婆婆每天早上6点进房打扫...",
        "6. 🇨🇳 [知乎] 扶弟魔 (Resource Allocation)": "知乎: 老公工资一半寄回老家养弟弟..."
    }
    
    # -------------------------------------------------------
    # 2. 完整故事映射 (这里存放真正的长文本)
    # -------------------------------------------------------
    full_text_map = {
        "None (Custom Input)": "",

        # Reddit Cases
        "1. The Bedroom Lock (Family Boundaries)": """My brother in-law (Sammy) lost his home and moved in with us along with his twin daughters. They have no respect for my daughter Zoey's privacy and kept taking her things. Zoey bought a $60 makeup kit and one of the twins ruined it. My wife and Sammy saw no issue. I installed a lock on Zoey's door. My wife shamed me for putting a lock on Zoey's door, saying it prevents them from 'spending time' with her and implies we want to kick them out. She demanded I remove it, but I said the lock stays until they leave. Now everyone is giving me the silent treatment.""",
        
        "2. The Medical Bill (Money vs. Face)": """My boyfriend went to the ER and got a $5000 bill. I offered to fight it. I went all-out: emailed the hospital board, investors, and management daily, pointing out their price gouging. Result: The bill was dropped to $26. I saved us nearly $5000. However, my boyfriend was furious. He looked at my emails and said I 'went too far' and 'harassed' the hospital. He said he authorized me to dispute the bill, not threaten the board. He is mad at me for being a hardass, even though I saved our holiday plans.""",
        
        "3. The Vegan Daughter (Values Conflict)": """My 14-year-old daughter decided to go vegan. I supported her, bought her special food and pans. But recently, she exploded because I cooked bacon in a 'family pan' (not hers). She demanded I buy her separate pans, which I did. Now, she says the dishwasher is 'contaminated' and the fridge has 'bacon grease fingers' on it. She and my wife want me to completely stop cooking meat at home. I refused. I said I will not stop eating bacon in my own house. Now there is huge tension.""",

        # Zhihu Cases (已修复标点符号)
        "4. 🇨🇳 [知乎] 彩礼博弈 (Bride Price Game)": """我和女友谈了三年，感情一直很好。她是上海本地人，我是外地来的，好不容易在上海站稳脚跟。一开始，我们谈彩礼的时候，她家说二十万就行，象征一下。可是最近，她妈妈突然说，彩礼要涨到五十万，而且必须在上海内环买一套两居室的房子，房产证上要写她的名字。我现在的积蓄根本不够，就算加上父母的钱，也只能凑个首付。我问她，她说她也不想这样，但她妈妈坚持，说怕女儿以后吃苦。现在我压力巨大，感觉喘不过气。分手吧，三年感情舍不得；不分手吧，感觉自己要被掏空。各位大佬，我该怎么办？求支招！""",
        
        "5. 🇨🇳 [知乎] 婆媳边界 (In-law Boundary)": """结婚半年，我和老公住在公婆家。房子是他们买的，所以我也没说什么。但是，我婆婆每天早上六点准时进我房间打扫卫生！不管我睡没睡醒！有时候我周末想睡个懒觉都不行。而且，她每次打扫完都要阴阳怪气地说我懒，说我不会持家。我跟老公说了好几次，他总是说让我忍忍，说他妈就这样。我白天上班已经很累了，晚上还要面对婆婆的冷嘲热讽，感觉自己快要精神崩溃了。我真的想搬出去住，但是又怕伤了老公的心。难道我真的应该为了维持这段婚姻，继续忍受下去吗？求各位姐妹支招，我该如何委婉地让婆婆别再进我房间了？""",
        
        "6. 🇨🇳 [知乎] 扶弟魔 (Resource Allocation)": """我和老公结婚五年，他是典型的凤凰男，从小家里条件不好，靠自己努力考上了大学，在大城市扎根。我很欣赏他的努力和上进心。但是，结婚后我才发现，他每个月都要把工资的一半寄回老家，说是要给弟弟攒钱买房。他弟弟好吃懒做，整天游手好闲，根本没有工作的打算。我跟他说，我们也有自己的生活，以后还要养孩子，不能一直这样无底洞似的补贴他弟弟。但他总是说，他是家里的顶梁柱，不能不管弟弟。现在我们为了钱的事情经常吵架，我感觉我们的感情已经快要走到尽头了。难道嫁给凤凰男就注定要牺牲自己的生活，来成全他的家人吗？求各位大神指点，我该如何改变现状？"""
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
