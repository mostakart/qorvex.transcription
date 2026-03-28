import streamlit as st
import os
import time
from google import genai 
from google.genai import types
import warnings

warnings.filterwarnings("ignore")

# 1. تظبيط شكل الصفحة 
st.set_page_config(page_title="Waffarha Audio AI", page_icon="🎙️", layout="centered")

st.title("🎙️ المحلل الصوتي الذكي")
st.markdown("ارفع أي ملف صوتي (اجتماع، فويس نوت، مكالمة كول سنتر)، والذكاء الاصطناعي هيفرغه حرفياً باللهجة المصرية بدون أي هلوسة!")

# ==========================================
# 🛡️ سحب المفتاح السري بأمان من إعدادات السيرفر
# ==========================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ السيرفر مش لاقي مفتاح الـ API في الخزنة السرية (Secrets). يرجى إضافته في إعدادات Streamlit.")
    st.stop() # وقف الكود لحد ما المفتاح يتحط

# 2. مكان رفع الملف الصوتي 
uploaded_file = st.file_uploader("📂 ارفع ملف الصوت هنا...", type=["mp3", "wav", "m4a"])

# 3. التشغيل
if uploaded_file:
    st.audio(uploaded_file)
    
    if st.button("🚀 ابدأ التفريغ الدقيق"):
        status_text = st.empty()
        status_text.info("⏳ جاري حفظ الملف مؤقتاً لمعالجته...")
        
        temp_audio_path = f"temp_{uploaded_file.name}"
        with open(temp_audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        try:
            start_time = time.time()
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            status_text.warning("📤 جاري رفع الملف لعقل Gemini...")
            audio_file = client.files.upload(file=temp_audio_path)
            
            prompt = """
            أنت أداة تفريغ صوتي (Transcription Tool).
            مهمتك الوحيدة والأساسية هي الاستماع إلى ملف الصوت المرفق، وكتابة كل كلمة تسمعها حرفياً باللهجة المصرية كما هي.
            
            قواعد صارمة جداً:
            1. لا تضف أي كلمة من عندك أو تجود المعنى بأي شكل.
            2. لا تترجم الكلمات الإنجليزية إلى العربية، اكتبها كما قيلت (مثال: Done).
            3. اكتب الكلام المنطوق فقط، ولا تضع مقدمات أو خاتمات في إجابتك.
            4. إذا كان هناك كلام غير مفهوم أو ضوضاء، تجاوزه أو اكتب (كلام غير واضح).
            """

            status_text.info("🎧 جاري الاستماع والتفريغ بدقة الحرف...")
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[audio_file, prompt],
                config=types.GenerateContentConfig(temperature=0.0)
            )
            
            final_text = response.text.strip()
            end_time = time.time()
            
            status_text.success(f"✅ تمت العملية بنجاح في {round(end_time - start_time, 1)} ثانية!")
            
            st.subheader("📝 النص المُفرّغ:")
            st.text_area("يمكنك نسخ النص من هنا:", value=final_text, height=250)
            
            st.download_button(
                label="⬇️ تحميل التفريغ كملف Text",
                data=final_text,
                file_name=f"Transcript_{uploaded_file.name}.txt",
                mime="text/plain"
            )
            
            client.files.delete(name=audio_file.name)
            
        except Exception as e:
            st.error(f"⚠️ حصلت مشكلة: {e}")
            
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
