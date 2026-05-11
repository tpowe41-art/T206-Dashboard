import streamlit as st
import pandas as pd
import plotly.express as px

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXo-9WVw3i64Pf79GpYaeEt-Dr5NBIId1KxNcpzj3J6tnChVsGP83pZRrafLrsTNMl9ivkV091P5DD/pub?gid=276008118&single=true&output=csv"

st.set_page_config(page_title="T206 Minor League Collection", layout="wide")
st.title("T206 Minor League Collection")

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL, header=1)
    df.columns = ['Owned','Card','Year','Name','City','Team','League','Back','Series','Factory','Company','Grade','CertNum','Cost','Notes']
    df = df[df['Card'].notna() & (df['Card'] != 'Card #')]
    df['Owned'] = df['Owned'].astype(str).str.upper() == 'TRUE'
    df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
    return df

df = load_data()
owned = df[df['Owned']]
needed = df[~df['Owned']]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Cards Owned", f"{len(owned)} / {len(df)}", f"{round(len(owned)/len(df)*100)}% complete")
col2.metric("Total Invested", f"${owned['Cost'].sum():,.0f}", f"avg ${owned['Cost'].mean():,.0f}/card")
col3.metric("Graded (SGC)", len(owned[owned['Company']=='SGC']), f"{len(owned[owned['Grade']=='raw'])} raw")
col4.metric("Still Needed", len(needed), f"across {needed['League'].nunique()} leagues")

st.divider()
col1, col2 = st.columns([3, 2])

with col1:
    league = df.groupby(['League','Owned']).size().reset_index(name='Count')
    league['Status'] = league['Owned'].map({True:'Owned', False:'Needed'})
    fig = px.bar(league, x='Count', y='League', color='Status', orientation='h',
                 color_discrete_map={'Owned':'#185fa5','Needed':'#d3d1c7'},
                 title='League completion')
    fig.update_layout(legend_title='', showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    grade_df = owned[owned['Grade'] != 'raw'].copy()
    grade_df['Grade'] = pd.to_numeric(grade_df['Grade'], errors='coerce')
    grade_counts = grade_df['Grade'].value_counts().sort_index().reset_index()
    grade_counts.columns = ['Grade','Count']
    fig2 = px.bar(grade_counts, x='Grade', y='Count', title='SGC grade distribution',
                  color_discrete_sequence=['#185fa5'])
    st.plotly_chart(fig2, use_container_width=True)

col3, col4, col5 = st.columns(3)

with col3:
    back = owned[owned['Back'].notna()]['Back'].value_counts().reset_index()
    back.columns = ['Back','Count']
    fig3 = px.pie(back, values='Count', names='Back', title='Card back type', hole=0.6)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    bins = [0,50,75,100,150,999]
    labels = ['<$50','$50-75','$75-100','$100-150','>$150']
    owned_copy = owned.copy()
    owned_copy['Range'] = pd.cut(owned_copy['Cost'], bins=bins, labels=labels)
    cost_counts = owned_copy['Range'].value_counts().sort_index().reset_index()
    cost_counts.columns = ['Range','Count']
    fig4 = px.bar(cost_counts, x='Range', y='Count', title='Cost distribution',
                  color_discrete_sequence=['#185fa5'])
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    st.markdown("**Top 5 by cost**")
    top5 = owned.nlargest(5, 'Cost')[['Name','Grade','Cost']].reset_index(drop=True)
    top5['Cost'] = top5['Cost'].apply(lambda x: f"${x:.2f}")
    st.dataframe(top5, use_container_width=True, hide_index=True)
