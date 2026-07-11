import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from collections import defaultdict

# تنظیمات صفحه
st.set_page_config(page_title="CF Analyzer", page_icon="📊", layout="wide")
st.title("🔥 Codeforces Rating Analyzer")
st.markdown("**تحلیل Acceptedها — بروزرسانی خودکار هر ۳ دقیقه**")

# ورودی
handle = st.text_input("هندل Codeforces:", placeholder="tourist", value="")

# Auto Refresh
if st.checkbox("فعال کردن بروزرسانی خودکار (هر ۳ دقیقه)", value=True):
    refresh_interval = 180  # ثانیه
else:
    refresh_interval = None

if handle:
    # Container برای نمایش داده‌ها
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            st.info(f"آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                with st.spinner("در حال گرفتن اطلاعات..."):
                    url = f"https://codeforces.com/api/user.status?handle={handle}&count=500"
                    resp = requests.get(url, timeout=15)
                    data = resp.json()
                    
                    if data['status'] != 'OK':
                        st.error("هندل اشتباه است یا API مشکل دارد.")
                        st.stop()
                    
                    subs = data['result']
                    now = int(time.time())
                    week_ago = now - 7*24*3600
                    
                    details = []
                    rating_count = defaultdict(lambda: {"جدید": 0, "قدیمی": 0})
                    
                    for sub in subs:
                        if sub.get('verdict') != 'OK':
                            continue
                        ctime = sub['creationTimeSeconds']
                        if ctime < week_ago:
                            break
                            
                        prob = sub.get('problem', {})
                        rating = prob.get('rating')
                        contest_id = prob.get('contestId')
                        
                        if not rating:
                            continue
                            
                        age = "جدید (۲۰۲۴+)" if (contest_id and contest_id >= 1800) else "قدیمی (قبل ۲۰۲۴)"
                        
                        details.append({
                            'Rating': rating,
                            'Category': age,
                            'Problem': f"{contest_id}{prob.get('index','')}",
                            'Name': prob.get('name', ''),
                            'Date': datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")
                        })
                        
                        rating_count[rating][age] += 1
                    
                    if details:
                        df = pd.DataFrame(details)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Accepted در ۷ روز", len(df))
                        with col2:
                            st.metric("ریتینگ‌های جدید", sum(d['Category'] == "جدید (۲۰۲۴+)" for d in details))
                        with col3:
                            st.metric("ریتینگ‌های قدیمی", sum(d['Category'] == "قدیمی (قبل ۲۰۲۴)" for d in details))
                        
                        st.subheader("توزیع ریتینگ")
                        summary = df.groupby(['Rating', 'Category']).size().unstack(fill_value=0)
                        st.dataframe(summary.sort_index(ascending=False), use_container_width=True)
                        
                        st.subheader("جزئیات کامل")
                        st.dataframe(df.sort_values('Rating', ascending=False), use_container_width=True)
                        
                        # دانلود
                        csv = df.to_csv(index=False).encode()
                        st.download_button("دانلود CSV", csv, f"{handle}_analysis.csv", "text/csv", key="download")
                    else:
                        st.warning("در یک هفته اخیر Accepted نداشتی.")
                        
            except Exception as e:
                st.error(f"خطا: {e}")
        
        if not refresh_interval:
            break
            
        time.sleep(refresh_interval)
        st.rerun()  # بروزرسانی صفحه