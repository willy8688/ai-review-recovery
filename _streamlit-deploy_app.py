import os
import streamlit as st
from langchain_openai import ChatOpenAI

# 1. Page Configuration
st.set_page_config(page_title="AI Negative Review Recovery Platform", layout="wide")

# 2. Configure Aliyun DashScope Credentials (from Streamlit Cloud Secrets)
# 在 Streamlit Cloud 的 Settings -> Secrets 中配置：
# OPENAI_API_KEY = "sk-xxxx"
# OPENAI_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_API_BASE"] = st.secrets["OPENAI_API_BASE"]

# Initialize LLM Engine (qwen-max)
@st.cache_resource
def get_llm():
    return ChatOpenAI(model="qwen-max", temperature=0)

# 3. Platform Header UI
st.title("🤖 独立站 AI 差评挽回工作台")
st.caption("系统自动抓取低分评价 -> AI 自动拟写安抚信 -> 客服主管一键审批发送")
st.markdown("---")

# 4. State Management (Session DB Simulation)
if "step" not in st.session_state:
    st.session_state.step = 1
if "draft_email" not in st.session_state:
    st.session_state.draft_email = ""

# 5. Left Sidebar: Mocking Shopify Data Feed
with st.sidebar:
    st.header("📥 Shopify 数据接入模拟")
    customer_name = st.text_input("客户姓名 (Customer)", value="Emily Brown")
    rating = st.selectbox("评价星级 (Rating)", [1, 2], index=0)
    review_text = st.text_area(
        "差评原文 (Review)",
        value="The design of this dress is beautiful, but the sizing is dynamic waste! I ordered my usual Size M, but it feels like an XS. Horrible experience."
    )

    # Trigger AI Workflow Button
    if st.button("🔥 触发系统：生成挽回工单", type="primary"):
        with st.spinner("AI 正在匹配售后标准，撰写全英安抚信..."):
            try:
                llm = get_llm()
                # Master System Prompt for AI Agent Task
                system_instruction = f"""You are an expert CRM specialist for an e-commerce clothing store.

Follow the policy based on the rating:
- 1 Star (Sizing/Quality issue): Full refund OR free replacement + 15% coupon (Code: REGAIN15).
- 2 Stars: 30% coupon (Code: SORRY30), no refund.

Task: Write a professional and heartfelt email to {customer_name} responding to their review.

Review: "{review_text}"

Output format: Return ONLY the email body text without any markdown or quotes.
"""
                response = llm.invoke(system_instruction)
                st.session_state.draft_email = response.content
                st.session_state.step = 2
            except Exception as e:
                st.error(f"System Error: {str(e)}")

# 6. Main Dashboard Area: Human-in-the-Loop Gate
st.subheader("📋 待审核工单 (Pending Approval Portal)")

if st.session_state.step == 1:
    st.info("💡 暂无待处理工单。请在左侧侧边栏点击【触发系统：生成挽回工单】按钮，模拟真实业务流。")

elif st.session_state.step == 2:
    # Render Work Order Cards
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="当前待处理客户", value=customer_name)
    with col2:
        st.metric(label="触发补偿方案", value="全额退款 + 15%优惠券" if rating == 1 else "30%优惠券")

    st.markdown("### ✍ AI 拟写的邮件草稿 (支持直接修改):")
    # Supervisor can manually fine-tune the email copy right inside the web platform
    final_email = st.text_area("邮件内容 (Email Draft)", value=st.session_state.draft_email, height=300)

    st.markdown("### 🚦 主管审批卡点:")
    btn_col1, btn_col2 = st.columns([1, 10])
    with btn_col1:
        if st.button("✅ 批准发送", type="primary"):
            st.session_state.step = 3
            st.rerun()
    with btn_col2:
        if st.button("❌ 驳回拦截"):
            st.session_state.step = 4
            st.rerun()

# 7. Post-Action Status Feedback
elif st.session_state.step == 3:
    st.success("🎉 【审批通过】动作已触发！系统已成功调用 `Send_Email_API` 将安抚信投递至客户真实邮箱！")
    if st.button("处理下一条工单"):
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 4:
    st.error("🚫 【工单已驳回】邮件草稿已被气囊安全拦截并销毁。已自动切入高级人工客服组进行跟进。")
    if st.button("返回工作台"):
        st.session_state.step = 1
        st.rerun()
