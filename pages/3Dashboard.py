import streamlit as st
import pandas as pd
import plotly.express as px


# Auth Check
if not st.session_state.get("logged_in", False):
    st.error("Please log in to access the Dashboard.")
    st.stop()

st.title(":signal_strength: :blue[ Let's take a look at the statistics of last 5 years]")
st.write("---")

df = pd.read_csv("data_csv.csv")   

ASD_traits_data = df["ASD_traits"].unique().tolist()
select_date = st.selectbox("ASD traits ?", ASD_traits_data)
df_up = df[df["ASD_traits"].isin(ASD_traits_data)]

sub_opt = df_up["Sex"].unique().tolist()
select_sub = st.multiselect("Gender", sub_opt)
df_up_sub = df_up[df_up["Sex"].isin(select_sub)]
st.write("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Jaundice statistics")
    with st.expander("See the plot"):     
        fig1 = px.bar(df_up_sub, x="Sex", color="Jaundice")
        fig1.update_layout(height=500, width=200)
        st.plotly_chart(fig1, key="jaundice_chart")

with col2:
    st.subheader("Childhood Autism Rating Scale statistics")
    with st.expander("See the plot"):        
        fig2 = px.bar(df_up_sub, x="Sex", color="Childhood Autism Rating Scale")
        fig2.update_layout(height=500, width=200)
        st.plotly_chart(fig2, key="autism_rating_chart")

st.write("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Family member with ASD statistics")
    with st.expander("See the plot"):     
        fig3 = px.bar(df_up_sub, x="Sex", color="Family_mem_with_ASD")
        fig3.update_layout(height=500, width=200)
        st.plotly_chart(fig3, key="family_asd_chart")

with col2:
    st.subheader("Social Responsiveness Scale statistics")
    with st.expander("See the plot"):        
        fig4 = px.bar(df_up_sub, x="Sex", color="Social_Responsiveness_Scale")
        fig4.update_layout(height=500, width=200)
        st.plotly_chart(fig4, key="social_responsiveness_chart")


# Sidebar logout
# Sidebar
with st.sidebar:
    if st.session_state.get("logged_in", False):
        st.success(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.switch_page("pages/8Logout.py")


