import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXo-9WVw3i64Pf79GpYaeEt-Dr5NBIId1KxNcpzj3J6tnChVsGP83pZRrafLrsTNMl9ivkV091P5DD/pub?gid=276008118&single=true&output=csv"

st.set_page_config(page_title="T206 Minor League", layout="wide", page_icon="⚾")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  .stApp {
    background-color: #0f0e0c;
    color: #e8e4db;
  }

  section[data-testid="stSidebar"] { display: none; }

  .block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
  }

  h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

  .hero {
    border-bottom: 1px solid #2a2820;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }

  .hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: #e8e4db;
    letter-spacing: -0.02em;
    margin: 0;
  }

  .hero p {
    font-size: 0.8rem;
    color: #73726c;
    margin: 4px 0 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .kpi-box {
    background: #1a1814;
    border: 1px solid #2a2820;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
  }

  .kpi-box .label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #73726c;
    margin-bottom: 8px;
  }

  .kpi-box .number {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #e8e4db;
    line-height: 1;
  }

  .kpi-box .sub {
    font-size: 0.72rem;
    color: #c5a96e;
    margin-top: 6px;
  }

  .kpi-box.accent { border-left: 3px solid #c5a96e; }

  .section-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #73726c;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
  }

  div[data-testid="stDataFrame"] {
    border: 1px solid #2a2820;
    border-radius: 8px;
    overflow: hidden;
  }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(SHEET_URL, header=1)
    df.columns = ['Owned','Card','Year','Name','City','Team','League','Back','Series','Factory','Company','Grade','CertNum','Cost','Notes']
    df = df[df['Card'].notna() & (df['Card'] != 'Card #')]
    df['Owned'] = df['Owned'].astype(str).str.upper() == 'TRUE'
    df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
    df['Name'] = df['Name'].astype(str).str.replace('★','').str.replace('  ',' ').str.strip()
    df['Star'] = df['Name'].astype(str).str.contains('★')
    return df

df = load_data()
owned = df[df['Owned']]
needed = df[~df['Owned']]

GOLD = '#c5a96e'
BLUE = '#3a7bd5'
DARK = '#1a1814'
GRID = '#2a2820'
TEXT = '#e8e4db'
MUTED = '#73726c'

CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color=TEXT, size=12),
    margin=dict(l=0, r=0, t=30, b=0),
    title_font=dict(family='Playfair Display', color=TEXT, size=15),
)

st.markdown("""
<div class="hero">
  <h1>T206 Minor League Collection</h1>
  <p>Live inventory · American Association · Eastern League · and more</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
pct = round(len(owned)/len(df)*100)
avg = owned['Cost'].mean()
graded = len(owned[owned['Company']=='SGC'])
raw = len(owned[owned['Grade']=='raw'])

with c1:
    st.markdown(f"""<div class="kpi-box accent">
      <div class="label">Cards owned</div>
      <div class="number">{len(owned)}<span style="font-size:1rem;color:{MUTED};"> / {len(df)}</span></div>
      <div class="sub">{pct}% of full set</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="kpi-box">
      <div class="label">Total invested</div>
      <div class="number">${owned['Cost'].sum():,.0f}</div>
      <div class="sub">avg ${avg:,.0f} per card</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="kpi-box">
      <div class="label">Graded (SGC)</div>
      <div class="number">{graded}</div>
      <div class="sub">{raw} raw · all SGC</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="kpi-box">
      <div class="label">Still needed</div>
      <div class="number">{len(needed)}</div>
      <div class="sub">across {needed['League'].nunique()} leagues</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("<div class='section-label'>League completion</div>", unsafe_allow_html=True)
    leagues = df.groupby('League').agg(
        Owned=('Owned', 'sum'),
        Total=('Owned', 'count')
    ).reset_index()
    leagues['Needed'] = leagues['Total'] - leagues['Owned']
    leagues = leagues.sort_values('Total', ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Owned', y=leagues['League'], x=leagues['Owned'],
                         orientation='h', marker_color=GOLD, marker_line_width=0))
    fig.add_trace(go.Bar(name='Needed', y=leagues['League'], x=leagues['Needed'],
                         orientation='h', marker_color=GRID, marker_line_width=0))
    fig.update_layout(**CHART_LAYOUT, barmode='stack', height=280,
                      legend=dict(orientation='h', y=1.1, x=0, font=dict(size=11)),
                      xaxis=dict(gridcolor=GRID, showgrid=True),
                      yaxis=dict(gridcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("<div class='section-label'>SGC grade distribution</div>", unsafe_allow_html=True)
    grade_df = owned[owned['Grade'] != 'raw'].copy()
    grade_df['Grade'] = pd.to_numeric(grade_df['Grade'], errors='coerce')
    grade_counts = grade_df['Grade'].value_counts().sort_index().reset_index()
    grade_counts.columns = ['Grade', 'Count']
    fig2 = px.bar(grade_counts, x='Grade', y='Count',
                  color_discrete_sequence=[GOLD])
    fig2.update_layout(**CHART_LAYOUT, height=280,
                       xaxis=dict(gridcolor=GRID, tickmode='array', tickvals=grade_counts['Grade']),
                       yaxis=dict(gridcolor=GRID))
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("<div class='section-label'>Card back type</div>", unsafe_allow_html=True)
    back = owned[owned['Back'].notna() & (owned['Back'] != 'nan')]['Back'].value_counts().reset_index()
    back.columns = ['Back', 'Count']
    fig3 = px.pie(back, values='Count', names='Back', hole=0.65,
                  color_discrete_sequence=[GOLD, BLUE, '#888780', '#5DCAA5', '#D85A30'])
    fig3.update_layout(**CHART_LAYOUT, height=240,
                       legend=dict(font=dict(size=11), orientation='v'))
    fig3.update_traces(textinfo='none')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("<div class='section-label'>Cost distribution</div>", unsafe_allow_html=True)
    bins = [0, 50, 75, 100, 150, 999]
    labels = ['<$50', '$50–75', '$75–100', '$100–150', '>$150']
    owned_c = owned.copy()
    owned_c['Range'] = pd.cut(owned_c['Cost'], bins=bins, labels=labels)
    cost_counts = owned_c['Range'].value_counts().sort_index().reset_index()
    cost_counts.columns = ['Range', 'Count']
    fig4 = px.bar(cost_counts, x='Range', y='Count', color_discrete_sequence=[GOLD])
    fig4.update_layout(**CHART_LAYOUT, height=240,
                       xaxis=dict(gridcolor=GRID),
                       yaxis=dict(gridcolor=GRID))
    fig4.update_traces(marker_line_width=0)
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    st.markdown("<div class='section-label'>Top 5 by cost</div>", unsafe_allow_html=True)
    top5 = owned.nlargest(5, 'Cost')[['Name', 'Grade', 'Cost']].reset_index(drop=True)
    top5.index = top5.index + 1
    top5['Cost'] = top5['Cost'].apply(lambda x: f"${x:.2f}")
    st.dataframe(top5, use_container_width=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-label'>Full inventory</div>", unsafe_allow_html=True)

show_needed = st.checkbox("Show cards still needed", value=False)
display_df = df if show_needed else owned
display_df = display_df[['Name','City','Team','League','Back','Grade','Company','Cost','Notes']].copy()
display_df['Cost'] = display_df['Cost'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else '—')
st.dataframe(display_df.reset_index(drop=True), use_container_width=True, height=300)

st.markdown(f"<div style='text-align:center;color:{MUTED};font-size:0.7rem;margin-top:2rem;'>T206 Minor League · {len(df)} cards tracked · data via Google Sheets</div>", unsafe_allow_html=True)
