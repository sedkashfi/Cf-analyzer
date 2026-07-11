import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="CF Analyzer", page_icon="📊", layout="wide")
st.title("🔥 Codeforces Rating Analyzer")
st.markdown("**تحلیل Accepted در ۷ روز اخیر**")

handle = st.text_input("هندل Codeforces:", placeholder="tourist")

if st.button("تحلیل کن 🚀", type="primary") and handle.strip():
    with st.spinner(f"در حال دریافت اطلاعات @{handle} ..."):
        try:
            url = f"https://codeforces.com/api/user.status?handle={handle.strip()}&count=500"
            resp = requests.get(url, timeout=20)
            data = resp.json()
            
            if data.get('status') != 'OK':
                st.error(f"خطا: {data.get('comment', 'API مشکل دارد')}")
                st.stop()
            
            subs = data['result']
            now = int(time.time())
            week_ago = now - 7 * 24 * 3600
            
            details = []
            rating_count = defaultdict(lambda: {"جدید": 0, "قدیمی": 0})
            
            for sub in subs:
                if sub.get('verdict') != 'OK':
                    continue
                    
                ctime = sub.get('creationTimeSeconds')
                if not ctime or ctime < week_ago:
                    continue
                    
                prob = sub.get('problem', {})
                rating = prob.get('rating')
                if not rating:
                    continue
                    
                contest_id = prob.get('contestId', 0)
                age = "جدید (۲۰۲۴+)" if contest_id >= 1800 else "قدیمی (قبل ۲۰۲۴)"
                
                details.append({
                    'Rating': rating,
                    'Category': age,
                    'Problem': f"{contest_id}{prob.get('index','')}",
                    'Name': prob.get('name', 'N/A'),
                    'Date': datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")
                })
                
                rating_count[rating][age] += 1
            
            if not details:
                st.info(f"@{handle} در ۷ روز اخیر Accepted نداشته است.")
            else:
                df = pd.DataFrame(details)
                
                st.success(f"@{handle} — {len(df)} Accepted")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Accepted", len(df))
                with col2:
                    st.metric("ریتینگ مختلف", len(rating_count))
                
                st.subheader("توزیع ریتینگ")
                summary = df.groupby(['Rating', 'Category']).size().unstack(fill_value=0)
                st.dataframe(summary.sort_index(ascending=False), use_container_width=True)
                
                st.subheader("جزئیات کامل")
                st.dataframe(df.sort_values(by='Rating', ascending=False), use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("دانلود CSV", csv, f"{handle}_analysis.csv", "text/csv")
                
        except Exception as e:
            st.error(f"خطای اتصال: {str(e)}")

st.caption("Made with ❤️ for Codeforces users")
