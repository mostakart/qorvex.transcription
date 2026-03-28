import streamlit as st
import os
import time
from google import genai 
from google.genai import types
import warnings

warnings.filterwarnings("ignore")

# 1. تظبيط شكل الصفحة (UI/UX)
st.set_page_config(page_title="Waffarha Audio AI", page_icon="🎙️", layout="centered")

st.title("🎙️ المحلل الصوتي الذكي")
st.markdown("ارفع أي ملف صوتي (اجتماع، فويس نوت، مكالمة كول سنتر)، والذكاء الاصطناعي هيفرغه حرفياً باللهجة المصرية بدون أي هلوسة!")

# 2. خانة آمنة لإدخال مفتاح جوجل (عشان محدش يسرقه)
api_key_input = st.text_input("🔑 أدخل مفتاح Gemini API بتاعك:", type="password")

# 3. مكان رفع الملف الصوتي
uploaded_file = st.file_uploader("📂 ارفع ملف الصوت هنا...", type=["mp3", "wav", "m4a"])

# 4. لو اليوزر رفع الملف وحط المفتاح، نظهر زرار التشغيل
if uploaded_file and api_key_input:
    # تشغيل مقطع الصوت جوه الموقع عشان اليوزر يتأكد منه
    st.audio(uploaded_file)
    
    if st.button("🚀 ابدأ التفريغ الدقيق"):
        
        # إنشاء شريط تقدم (Progress)
        status_text = st.empty()
        status_text.info("⏳ جاري حفظ الملف مؤقتاً لمعالجته...")
        
        # حفظ الملف في الجهاز مؤقتاً عشان جوجل تقدر تقرأه
        temp_audio_path = f"temp_{uploaded_file.name}"
        with open(temp_audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        try:
            start_time = time.time()
            client = genai.Client(api_key=api_key_input)
            
            # رفع الملف لجوجل
            status_text.warning("📤 جاري رفع الملف لعقل Gemini (البيانات مشفرة)...")
            audio_file = client.files.upload(file=temp_audio_path)
            
            # هندسة الأوامر الصارمة
            prompt = """
            أنت أداة تفريغ صوتي (Transcription Tool).
            مهمتك الوحيدة والأساسية هي الاستماع إلى ملف الصوت المرفق، وكتابة كل كلمة تسمعها حرفياً باللهجة المصرية كما هي.
            
            قواعد صارمة جداً:
            1. لا تضف أي كلمة من عندك أو تجود المعنى بأي شكل.
            2. لا تترجم الكلمات الإنجليزية إلى العربية، اكتبها كما قيلت (مثال: Done).
            3. اكتب الكلام المنطوق فقط، ولا تضع مقدمات أو خاتمات في إجابتك.
            4. إذا كان هناك كلام غير مفهوم أو ضوضاء، تجاوزه أو اكتب (كلام غير واضح).
            """

            status_text.info("🎧 جاري الاستماع والتفريغ بدقة الحرف... (قد يستغرق بضع ثوانٍ)")
            
            # استخدام موديل 2.5 Flash اللي بيدعم الصوت
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[audio_file, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.0 # دقة حرفية بدون هلوسة
                )
            )
            
            final_text = response.text.strip()
            end_time = time.time()
            
            # مسح رسالة التحميل وإظهار النجاح
            status_text.success(f"✅ تمت العملية بنجاح في {round(end_time - start_time, 1)} ثانية!")
            
            # عرض النتيجة جوه الصفحة
            st.subheader("📝 النص المُفرّغ:")
            st.text_area("يمكنك نسخ النص من هنا:", value=final_text, height=250)
            
            # زرار سحري لتحميل النص كملف txt
            st.download_button(
                label="⬇️ تحميل التفريغ كملف Text",
                data=final_text,
                file_name=f"Transcript_{uploaded_file.name}.txt",
                mime="text/plain"
            )
            
            # تنظيف سيرفرات جوجل للحفاظ على الخصوصية
            client.files.delete(name=audio_file.name)
            
        except Exception as e:
            st.error(f"⚠️ حصلت مشكلة: {e}")
            
        finally:
            # تنظيف اللاب توب بتاعك ومسح الملف المؤقت
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

elif not api_key_input and uploaded_file:
    st.warning("⚠️ يرجى إدخال مفتاح الـ API في الأعلى للبدء.")