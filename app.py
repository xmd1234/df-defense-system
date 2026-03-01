import streamlit as st
import hashlib
import json
import time
import pandas as pd
import datetime
import random

#streamlit run "F:\GDproject\blockchain\app.py"
# ===========================
# 底层逻辑：区块链与模拟器
# ===========================

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], str(datetime.datetime.now()), "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=str(datetime.datetime.now()),
                          previous_hash=last_block.hash)
        self.chain.append(new_block)
        self.unconfirmed_transactions = []
        return new_block.index

    def check_video_integrity(self, video_hash):
        # 在链上查找哈希
        for block in self.chain:
            for tx in block.transactions:
                if tx.get('video_hash') == video_hash:
                    return True, tx
        return False, None


# ===========================
# Streamlit 页面逻辑
# ===========================

# 1. 页面配置
st.set_page_config(
    page_title="DeepGuard 防伪系统",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 初始化 Session State (保证刷新页面后区块链数据不丢失)
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()
    # 预置一条数据用于演示
    st.session_state.blockchain.add_new_transaction({
        'video_hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # 空文件hash示例
        'device_id': 'Sony_A7M4_Demo',
        'location': 'Lab_001',
        'timestamp': str(datetime.datetime.now()),
        'author': 'System Admin'
    })
    st.session_state.blockchain.mine()


# 工具函数：计算Hash
def calculate_hash(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return hashlib.sha256(bytes_data).hexdigest()
    return None


# ===========================
# 侧边栏设计
# ===========================
st.sidebar.image("https://img.icons8.com/fluency/96/blockchain-technology.png", width=80)
st.sidebar.title("DeepGuard 系统导航")
page = st.sidebar.radio(
    "选择功能模块:",
    ["🏠 系统概览", "🔗 源端确权 (上链)", "🔍 协同核验 (检测)", "📜 区块链浏览器"]
)
st.sidebar.markdown("---")
st.sidebar.info(

    "集成 BMNet 检测算法与区块链溯源技术，"
    "实现全生命周期的多媒体内容安全防护。"
)

# ===========================
# 主页面逻辑
# ===========================

if page == "🏠 系统概览":
    st.title("🛡️ 基于区块链与深度学习的伪造防范系统")


    st.success("✅ 系统状态：在线 | 区块链节点：运行中 | 检测模型：FSCP-Enhancer + BMNet 已加载")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="当前区块高度", value=len(st.session_state.blockchain.chain))
    with col2:
        st.metric(label="保护视频数量", value=sum(len(b.transactions) for b in st.session_state.blockchain.chain))


    st.markdown("---")
    # st.image("F:/GDproject/blockchain/1.png", use_container_width=True)
    st.image("1.png", use_container_width=True)
    st.info(
        """
        1. **源端 (Source)**: 视频采集 -> 生成哈希 -> 绑定设备ID -> **上链存证**。
        2. **云端 (Cloud)**: 智能合约监听 -> 分发校验任务。
        3. **终端 (Client)**: 
            - 若链上哈希匹配 -> **直接认证为真**。
            - 若链上无记录 -> **调用 BMNet 检测** -> 输出伪造概率。
        """
    )

elif page == "🔗 源端确权 (上链)":
    st.title("🔗 源端可信上链")
    st.markdown("**功能描述**：在视频生成/采集阶段，提取数字指纹并绑定元数据，写入区块链，实现“内容防篡改”。")

    col_up, col_form = st.columns([1, 1])

    with col_up:
        st.subheader("1. 视频采集/上传")
        uploaded_file = st.file_uploader("上传原始视频文件", type=['mp4', 'avi', 'mov'])

        video_hash = None
        if uploaded_file is not None:
            st.video(uploaded_file)
            with st.spinner('正在计算 SHA-256 摘要...'):
                time.sleep(1)  # 模拟计算耗时
                video_hash = calculate_hash(uploaded_file)
            st.code(f"Hash: {video_hash}", language="text")
            st.success("数字指纹提取完成")

    with col_form:
        st.subheader("2. 元数据绑定")
        with st.form("upload_form"):
            device_id = st.text_input("采集设备 ID", value="Camera_Canon_R5_008")
            location = st.text_input("地理位置", value="Shanghai_University_Lab")
            author = st.text_input("操作员", value="Researcher_01")

            submitted = st.form_submit_button("⛓️ 生成交易并上链")

            if submitted:
                if video_hash:
                    # 写入区块链
                    tx = {
                        'video_hash': video_hash,
                        'device_id': device_id,
                        'location': location,
                        'timestamp': str(datetime.datetime.now()),
                        'author': author
                    }
                    st.session_state.blockchain.add_new_transaction(tx)
                    block_idx = st.session_state.blockchain.mine()

                    st.balloons()
                    st.success(f"✅ 上链成功！交易已被打包进区块 #{block_idx}")
                    st.json(tx)
                else:
                    st.error("请先上传视频文件")

# ... (前面的代码保持不变) ...

elif page == "🔍 协同核验 (检测)":
    st.title("🔍 智能协同核验与溯源")
    st.markdown("**功能描述**：智能合约自动执行【溯源】与【检测】双重任务。")

    verify_file = st.file_uploader("上传待检测的可疑视频", type=['mp4', 'avi', 'mov'], key="verify")

    if verify_file is not None:
        col_video, col_info = st.columns([1, 2])
        with col_video:
            st.video(verify_file)
        with col_info:
            st.info(f"文件名: {verify_file.name}")

        start_verify = st.button("🚀 启动智能合约溯源", type="primary")

        if start_verify:
            current_hash = calculate_hash(verify_file)

            # === 阶段一：区块链溯源查询 ===
            st.markdown("### 1. 区块链溯源查询 (Provenance Tracking)")
            with st.spinner("正在链上检索数字指纹..."):
                time.sleep(1)  # 模拟网络延迟
                is_on_chain, tx_data = st.session_state.blockchain.check_video_integrity(current_hash)

            if is_on_chain:
                # =========================================
                # 场景 A: 溯源成功 (展示溯源路径)
                # =========================================
                st.success("✅ 溯源成功！该视频为【原始可信文件】")

                # 1. 展示溯源路径图 (Graphviz)
                st.markdown("#### ⛓️ 全生命周期溯源路径图")
                trace_graph = f"""
                digraph G {{
                    rankdir=LR;
                    node [shape=box, style="rounded,filled", fontname="Microsoft YaHei"];

                    Source [label="采集源头\\n{tx_data['device_id']}", fillcolor="#e8f5e9"];
                    Upload [label="上链操作员\\n{tx_data['author']}", fillcolor="#e3f2fd"];
                    Block [label="区块存证\\nTimestamp: {tx_data['timestamp'][:19]}", fillcolor="#fff9c4"];
                    Verify [label="当前终端\\n核验通过", fillcolor="#ccff90", shape=doublecircle];

                    Source -> Upload [label="生成"];
                    Upload -> Block [label="哈希上链"];
                    Block -> Verify [label="哈希匹配"];
                }}
                """
                st.graphviz_chart(trace_graph)

                # 2. 展示详细的溯源信息卡片
                st.markdown("#### 📄 数字身份证书")
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.text_input("原始数字指纹 (Hash)", value=tx_data['video_hash'], disabled=True)
                    c2.text_input("所属区块高度", value=f"Block #{st.session_state.blockchain.chain[-1].index}",
                                  disabled=True)

                    c3, c4, c5 = st.columns(3)
                    c3.text_input("采集设备", value=tx_data['device_id'], disabled=True)
                    c4.text_input("拍摄地点", value=tx_data['location'], disabled=True)
                    c5.text_input("确权时间", value=tx_data['timestamp'], disabled=True)

                st.balloons()

            else:
                # =========================================
                # 场景 B: 溯源失败 (启动检测)
                # =========================================
                st.warning("⚠️ 溯源中断：链上未找到该视频记录 (Origin Unknown)")

                with st.expander("查看失败原因", expanded=True):
                    st.write(f"当前视频 Hash: `{current_hash}`")
                    st.write("状态: ❌ 未匹配到任何区块交易")
                    st.write("推断: 视频可能已被篡改、伪造，或尚未注册。")

                st.markdown("### 2. 启动深度伪造检测 (Deepfake Detection)")
                st.info("智能合约自动触发 BMNet 检测节点...")

                # 模拟模型推理
                progress_bar = st.progress(0)
                status_text = st.empty()
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("Step 1: 提取面部关键点...")
                    elif i < 70:
                        status_text.text("Step 2: FSCP 图像增强处理...")
                    else:
                        status_text.text("Step 3: BMNet 时序一致性分析...")

                # 模拟结果
                filename = verify_file.name.lower()
                if 'fake' in filename or 'manipulated' in filename:
                    st.error("🚨 最终判定：深度伪造 (Deepfake)")
                    st.metric(label="BMNet 伪造置信度", value="98.4%", delta="-High Risk")
                else:
                    st.success("✅ 最终判定：内容看似真实 (但无链上身份)")
                    st.metric(label="BMNet 伪造置信度", value="12.1%", delta="Low Risk")

# elif page == "🔍 协同核验 (检测)":
#     st.title("🔍 智能协同核验终端")
#     st.markdown("**功能描述**：智能合约自动判断逻辑。优先查询链上记录（白名单），若未命中则启动深度检测模型。")
#
#     verify_file = st.file_uploader("上传待检测的可疑视频", type=['mp4', 'avi', 'mov'], key="verify")
#
#     if verify_file is not None:
#         st.video(verify_file)
#         start_verify = st.button("🚀 启动智能合约核验流程", type="primary")
#
#         if start_verify:
#             current_hash = calculate_hash(verify_file)
#
#             # 使用 status 容器展示动态流程
#             with st.status("正在执行智能合约逻辑...", expanded=True) as status:
#
#                 # Step 1: Hash Check
#                 st.write("📝 Step 1: 提取视频特征值...")
#                 time.sleep(0.5)
#                 st.write(f"   > 视频哈希: {current_hash[:20]}...")
#
#                 st.write("🔗 Step 2: 查询区块链账本...")
#                 time.sleep(1)
#                 is_on_chain, tx_data = st.session_state.blockchain.check_video_integrity(current_hash)
#
#                 if is_on_chain:
#                     status.update(label="✅ 核验完成：链上可信视频", state="complete", expanded=False)
#                     st.success("## 认证通过：该视频为原始记录")
#                     st.markdown(f"""
#                     - **来源设备**: {tx_data['device_id']}
#                     - **拍摄时间**: {tx_data['timestamp']}
#                     - **可信度**: 🌟🌟🌟🌟🌟 (Blockchain Verified)
#                     """)
#                 else:
#                     st.write("⚠️ 链上未找到记录，正在唤醒 AI 检测节点...")
#
#                     # Step 2: AI Detection
#                     st.write("🧠 Step 3: 加载 FSCP-Enhance 增强模块...")
#                     time.sleep(0.8)
#                     st.write("🧠 Step 4: 运行 BMNet 时序检测网络...")
#
#                     # 模拟模型推理进度条
#                     progress_bar = st.progress(0)
#                     for i in range(100):
#                         time.sleep(0.01)
#                         progress_bar.progress(i + 1)
#
#                     # === 模拟逻辑：根据文件名判断真假 ===
#                     # 如果文件名包含 'fake'，则模拟高伪造率，否则模拟低伪造率
#                     filename = verify_file.name.lower()
#                     if 'fake' in filename or 'manipulated' in filename:
#                         fake_score = random.uniform(0.85, 0.99)
#                         is_fake = True
#                     else:
#                         fake_score = random.uniform(0.05, 0.20)
#                         is_fake = False
#
#                     status.update(label="❌ 核验完成：检测结束", state="complete", expanded=False)
#
#                     st.markdown("---")
#                     if is_fake:
#                         st.error(f"## ⚠️ 警告：检测到深度伪造内容")
#                         col_res1, col_res2 = st.columns(2)
#                         col_res1.metric("伪造置信度 (BMNet)", f"{fake_score:.2%}", delta="High Risk",
#                                         delta_color="inverse")
#                         col_res2.warning("建议操作：拦截并标记")
#                         st.write("**检测详情**：FSCP 模块在第 45-120 帧检测到面部纹理异常，BMNet 时序一致性评分过低。")
#                     else:
#                         st.info(f"## ✅ 通过：未发现明显伪造痕迹")
#                         st.metric("伪造置信度 (BMNet)", f"{fake_score:.2%}", delta="Safe")
#                         st.write("**检测详情**：虽然该视频未上链，但经 AI 模型分析，符合自然视频特征。")
# ... (后面的代码保持不变) ...

elif page == "📜 区块链浏览器":
    st.title("📜 区块链公共账本视图")
    st.markdown("此处展示系统中所有已确认的区块和交易信息，数据公开透明，不可篡改。")

    if st.button("🔄 刷新数据"):
        st.rerun()

    # 转换数据为 DataFrame 以便展示
    chain_data = []
    for block in st.session_state.blockchain.chain:
        for tx in block.transactions:
            row = {
                "区块高度": block.index,
                "上链时间": block.timestamp,
                "视频哈希 (前8位)": tx['video_hash'][:8] + "...",
                "设备ID": tx['device_id'],
                "地点": tx['location'],
                "操作员": tx['author']
            }
            chain_data.append(row)

    if chain_data:
        df = pd.DataFrame(chain_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("暂无交易数据，请前往“源端确权”页面上链。")

    st.markdown("### 区块原始 JSON 数据")
    st.json([b.__dict__ for b in st.session_state.blockchain.chain])


# streamlit run "F:\GDproject\blockchain\app.py"

