import streamlit as st

def apply_sidebar_styles():
    st.markdown("""
        <style>
        .stApp {background-color: #f0f2f6; font-size: 16px;}
        .sidebar .sidebar-content {
            background-color: #40E0D0; /* تركوازي فاتح للخلفية */
            color: #1A2525; /* نص غامق */
            padding: 15px;
            max-width: 280px;
            border-radius: 0 15px 15px 0;
            box-shadow: 3px 0 8px rgba(0,0,0,0.3);
        }
        .sidebar h2 {color: #1A2525; font-size: 22px; text-align: center; margin: 10px 0; font-weight: bold;}
        .sidebar hr {border: 1px solid rgba(26, 37, 37, 0.2); margin: 10px 0;}
        .stButton>button {
            background: linear-gradient(90deg, #40E0D0, #48D1CC); /* تدرج تركوازي فاتح */
            color: #1A2525; /* نص غامق */
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-weight: 500;
            width: 100%;
            margin: 5px 0;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            transition: all 0.3s ease;
            border: none;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #48D1CC, #20B2AA); /* تدرج أغمق قليلاً عند التمرير */
            transform: translateX(5px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .stSelectbox, .stTextInput {
            background-color: #48D1CC; /* تركوازي فاتح متوسط للحقول */
            color: #1A2525; /* نص غامق */
            border-radius: 8px;
            padding: 5px;
            font-size: 14px;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        .section-title {color: #1A2525; font-size: 14px; margin: 10px 0 5px 0; text-transform: uppercase;}
        @media (max-width: 768px) {
            .stApp {font-size: 14px;}
            .sidebar .sidebar-content {max-width: 100%; border-radius: 0;}
            .stButton>button {font-size: 12px; padding: 8px;}
            .stColumn {margin-bottom: 10px;}
            .main h1 {font-size: 24px;}
            .main p {font-size: 14px;}
        }
        </style>
    """, unsafe_allow_html=True)
