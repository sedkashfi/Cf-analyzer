import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CF Analyzer", page_icon="📊", layout="wide")
st.title("🔥 Codeforces Rating Analyzer")
st.markdown("**تحلیل Acceptedها — ریتینگ + سن سوال**")

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
            week_ago = now - 7 * 24 * 3600
            
            details = []
            rating_count = {}
            
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
                
                if rating not in rating_count:
                    rating_count[rating] = {"جدید": 0, "قدیمی": 0}
                rating_count[rating][age] += 1
            
            if not details:
                st.info(f"@{handle} در ۷ روز اخیر Accepted نداشته.")
            else:
                df = pd.DataFrame(details)
                
                st.success(f"@{handle} — {len(df)} Accepted")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Accepted", len(df))
                with col2:
                    st.metric("ریتینگ مختلف", len(rating_count))
                with col3:
                    st.metric("جدید", sum(d['Category'] == "جدید (۲۰۲۴+)" for d in details))
                
                st.subheader("توزیع ریتینگ")
                summary = df.groupby(['Rating', 'Category']).size().unstack(fill_value=0)
                st.dataframe(summary.sort_index(ascending=False), use_container_width=True)
                
                st.subheader("جزئیات کامل")
                st.dataframe(df.sort_values(by='Rating', ascending=False), use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("دانلود CSV", csv, f"{handle}_analysis.csv", "text/csv")
                
        except Exception as e:
            st.error(f"خطا: {str(e)}")

st.caption("Made with ❤️ for Codeforces")
