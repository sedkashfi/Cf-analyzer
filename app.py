import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CF Analyzer", page_icon="📊", layout="wide")
st.title("🔥 Codeforces Rating Analyzer")
st.markdown("**تحلیل Accepted — ۲۴ ساعت و ۷ روز**")

handle = st.text_input("هندل Codeforces:", placeholder="tourist")

if st.button("تحلیل کن 🚀", type="primary") and handle.strip():
    with st.spinner(f"در حال دریافت @{handle} ..."):
        try:
            url = f"https://codeforces.com/api/user.status?handle={handle.strip()}&count=500"
            resp = requests.get(url, timeout=20)
            data = resp.json()
            
            if data.get('status') != 'OK':
                st.error(f"خطا: {data.get('comment', 'API مشکل دارد')}")
                st.stop()
            
            subs = data['result']
            now = int(datetime.now().timestamp())
            day_ago = now - 24 * 3600
            week_ago = now - 7 * 24 * 3600
            
            details_24h = []
            details_7d = []
            
            for sub in subs:
                if sub.get('verdict') != 'OK':
                    continue
                ctime = sub.get('creationTimeSeconds')
                if not ctime:
                    continue
                    
                prob = sub.get('problem', {})
                rating = prob.get('rating')
                if not rating:
                    continue
                    
                row = {
                    'Rating': rating,
                    'Problem': f"{prob.get('contestId','')}{prob.get('index','')}",
                    'Name': prob.get('name', 'N/A'),
                    'Date': datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")
                }
                
                if ctime >= week_ago:
                    details_7d.append(row)
                if ctime >= day_ago:
                    details_24h.append(row)
            
            # نمایش متریک‌ها
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Accepted در ۲۴ ساعت", len(details_24h))
            with col2:
                st.metric("Accepted در ۷ روز", len(details_7d))
            
            if not details_7d:
                st.info(f"@{handle} در ۷ روز اخیر Accepted نداشته.")
            else:
                df = pd.DataFrame(details_7d)
                
                st.subheader("توزیع ریتینگ (۷ روز)")
                summary = df['Rating'].value_counts().sort_index(ascending=False)
                st.bar_chart(summary)
                
                st.subheader("جزئیات کامل (۷ روز)")
                st.dataframe(df.sort_values(by='Rating', ascending=False), use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("دانلود CSV", csv, f"{handle}_7days.csv", "text/csv")
                
        except Exception as e:
            st.error(f"خطا: {str(e)}")

st.caption("Made with ❤️ for Codeforces")
