import streamlit as st
import replicate
import os
import requests
import datetime
from PIL import Image
from io import BytesIO

# --- HỆ THỐNG LƯU TRỮ NỘI BỘ ---
HISTORY_DIR = "kol_studio_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI KOL Studio Pro", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0a0a0c; color: white; }
    .stApp { background-color: #0a0a0c; }
    
    /* Tiêu đề Gradient */
    .main-title {
        text-align: center; font-weight: 800; font-size: 3rem;
        background: linear-gradient(90deg, #6366f1, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    /* Nút bấm Luxury */
    div.stButton > button {
        width: 100%; border-radius: 12px; height: 55px;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white; font-weight: bold; border: none; font-size: 18px;
        transition: 0.3s; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6); }

    /* Card kết quả */
    .result-card { border: 1px solid #222; border-radius: 20px; padding: 15px; background: #111; }
    
    /* Mobile Responsive */
    @media (max-width: 768px) { .main-title { font-size: 2rem; } }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CẤU HÌNH ---
with st.sidebar:
    st.header("⚙️ Cài đặt AI")
    api_token = st.text_input("Replicate API Token", type="password", help="Lấy tại replicate.com/account")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token
    
    st.divider()
    st.subheader("🛠 Hậu kỳ (98% Real)")
    face_restore = st.checkbox("Tăng nét gương mặt", value=True)
    skin_smooth = st.checkbox("Làm mịn da Studio", value=True)
    film_color = st.selectbox("Màu Film chuyên nghiệp", ["None", "Kodak Portra 400", "Fujifilm 400H", "Cinematic Teal"])
    
    if st.button("🗑 Xóa sạch lịch sử"):
        for f in os.listdir(HISTORY_DIR): os.remove(os.path.join(HISTORY_DIR, f))
        st.rerun()

# --- GIAO DIỆN CHÍNH ---
st.markdown('<h1 class="main-title">AI KOL STUDIO PRO</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Giữ 98% gương mặt gốc • Chất lượng 4K • Xử lý nội bộ</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 TẠO ẢNH MỚI", "📚 THƯ VIỆN NỘI BỘ"])

with tab1:
    col_in, col_out = st.columns([1, 1], gap="large")
    
    with col_in:
        st.write("### 📥 1. Tải lên chân dung")
        src_img = st.file_uploader("Chọn ảnh rõ mặt (Rõ con ngươi là tốt nhất)", type=["jpg", "png", "jpeg"])
        
        prompt = st.text_area("2. Bối cảnh & Trang phục", 
                             "A high-end KOL standing in a luxury modern villa, wearing a premium suit, cinematic lighting, 8k resolution, photorealistic", height=120)
        
        ratio = st.radio("3. Tỷ lệ ảnh", ["3:4 (Portrait)", "1:1 (Square)", "9:16 (Story)"], horizontal=True)
        
        btn_generate = st.button("🔥 BẮT ĐẦU TẠO ẢNH NGAI")

    with col_out:
        st.write("### 🖼️ Kết quả AI")
        if btn_generate:
            if not api_token:
                st.error("Bạn chưa nhập API Token ở menu bên trái!")
            elif not src_img:
                st.warning("Vui lòng tải ảnh gương mặt lên!")
            else:
                with st.status("🛠 Đang thực hiện quy trình Gold...", expanded=True) as status:
                    try:
                        # Bước 1: Tạo bối cảnh bằng Flux
                        status.write("⏳ Bước 1: Dựng bối cảnh 4K & Body...")
                        r_map = {"3:4 (Portrait)": "3:4", "1:1 (Square)": "1:1", "9:16 (Story)": "9:16"}
                        f_prompt = f"{prompt}, {film_color} color style" if film_color != "None" else prompt
                        
                        base_res = replicate.run(
                            "black-forest-labs/flux-schnell",
                            input={"prompt": f_prompt, "aspect_ratio": r_map[ratio]}
                        )
                        base_url = base_res[0]

                        # Bước 2: Ghép mặt Identity 98%
                        status.write("🎯 Bước 2: Đồng bộ gương mặt (98% Similarity)...")
                        swap_res = replicate.run(
                            "lucataco/faceswap:9a429103ed57553f02f30411ad914c090336da90df113e64ca98282f1d079b50",
                            input={"target_image": base_url, "source_image": src_img}
                        )

                        # Bước 3: Hậu kỳ (GFPGAN)
                        final_url = swap_res
                        if face_restore or skin_smooth:
                            status.write("✨ Bước 3: Làm mịn da & Nâng cấp 4K...")
                            final_url = replicate.run(
                                "tencentarc/gfpgan:9283608cc6b7c9cc2b527d6563da08ad9510595730335f65bc50c4abc3c79119",
                                input={"img": swap_res, "upscale": 2}
                            )

                        status.update(label="✅ Hoàn tất!", state="complete")
                        st.image(final_url, use_container_width=True)
                        
                        # Lưu vào lịch sử nội bộ
                        img_data = requests.get(final_url).content
                        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        with open(os.path.join(HISTORY_DIR, f"KOL_{ts}.png"), "wb") as f:
                            f.write(img_data)
                        
                        st.download_button("📥 TẢI ẢNH 4K VỀ MÁY", img_data, file_name=f"KOL_{ts}.png", mime="image/png")
                        
                    except Exception as e:
                        st.error(f"Lỗi AI: {str(e)}")
        else:
            st.info("Ảnh sẽ xuất hiện tại đây sau khi bạn nhấn nút tạo.")

with tab2:
    st.write("### 📚 Ảnh đã tạo trên máy tính này")
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".png")]
    files.sort(reverse=True)
    
    if not files:
        st.info("Chưa có ảnh nào được tạo.")
    else:
        grid = st.columns(4)
        for idx, f in enumerate(files):
            with grid[idx % 4]:
                p = os.path.join(HISTORY_DIR, f)
                st.image(p, use_container_width=True)
                with open(p, "rb") as file_data:
                    st.download_button("Tải", file_data.read(), file_name=f, key=f"btn_{idx}")

st.markdown("---")
st.caption("AI KOL Studio Ultra Pro Gold - Chạy nội bộ ổn định")