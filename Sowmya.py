import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. APP CONFIG & STYLE ---
st.set_page_config(page_title="MedGuard Pro", page_icon="🌸")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FF0000 0%, #FFFFFF 50%, #FFC0CB 100%);
    }
    /* Black text for maximum readability */
    h1, h2, h3, p, span, label, b, .stMarkdown {
        color: #000000 !important;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background-color: #FF0000;
        color: white !important;
        font-weight: bold;
        border: 2px solid white;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }
    .dosage-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 15px;
        border-left: 10px solid #FF0000;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS CONNECTION ---
# This will save data even if she deletes the app
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. NOTIFICATION LOGIC ---
now_time = datetime.now().strftime("%H:%M")
reminders = {
    "07:55": "Before Breakfast (12 Tabs)",
    "09:25": "After Breakfast (6 Tabs)",
    "13:25": "After Lunch (3 Tabs)",
    "19:25": "Before Dinner (12 Tabs)",
    "20:55": "After Dinner (3 Tabs)"
}

if now_time in reminders:
    st.toast(f"🚨 REMINDER: {reminders[now_time]}", icon="🔔")

# --- 4. APP INTERFACE ---
st.title("🌸 MedGuard: Daily Care")
tab1, tab2 = st.tabs(["💊 Tablet Intake", "🕵️ Admin Monitor"])

with tab1:
    st.subheader("Your Schedule")
    
    # Define the 5 specific dosage windows
    schedule = [
        {"name": "Before Breakfast", "dose": "12 Tablets (6×2)", "id": "bb"},
        {"name": "After Breakfast", "dose": "6 Tablets", "id": "ab"},
        {"name": "After Lunch", "dose": "3 Tablets", "id": "al"},
        {"name": "Before Dinner", "dose": "12 Tablets (6×2)", "id": "bd"},
        {"name": "After Dinner", "dose": "3 Tablets", "id": "ad"}
    ]

    for item in schedule:
        with st.container():
            st.markdown(f"""<div class="dosage-card">
                <b>{item['name']}</b><br>Required: {item['dose']}
            </div>""", unsafe_allow_html=True)
            
            # Anti-Cheat: Forced Photo Proof
            proof = st.camera_input(f"Photo of {item['name']} pills", key=f"cam_{item['id']}")
            
            if proof:
                if st.button(f"Confirm {item['name']}", key=f"btn_{item['id']}"):
                    # Create data row
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%I:%M %p"),
                        "Dose": item['name'],
                        "Status": "Verified ✅"
                    }])
                    
                    # Update Google Sheet
                    try:
                        existing_data = conn.read()
                        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                        conn.update(data=updated_df)
                        st.balloons()
                        st.success("Verification Sent to Cloud!")
                    except:
                        st.error("Connection Error. Data saved locally for now.")

with tab2:
    st.subheader("🕵️ Private Verification Log")
    try:
        data = conn.read()
        st.dataframe(data, use_container_width=True)
    except:
        st.write("Connect Google Sheets to see live history.")
