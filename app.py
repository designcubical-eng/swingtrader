"""SwingTrader 1.1: educational Swedish-stock screener and illustrative backtester."""
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from PIL import Image

BASE = Path(__file__).parent
ICON = Image.open(BASE / 'assets' / 'favicon.png')
st.set_page_config(page_title='SwingTrader 1.1 | Nautilus', page_icon=ICON, layout='wide', initial_sidebar_state='collapsed')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');
:root {color-scheme:dark}
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {background:#101c1d;color:#f0dfbd}
[data-testid="stAppViewContainer"] {background:radial-gradient(ellipse at 90% 0%, #20444a 0%,transparent 40%),linear-gradient(130deg,#0d1819,#192522 60%,#0c1618)}
[data-testid="stHeader"] {background:transparent}
.block-container {max-width:1140px;padding-top:1.2rem;padding-bottom:4rem}
h1,h2,h3 {color:#edc987 !important;font-family:'Cinzel',Georgia,serif !important;letter-spacing:.015em}
p,span,div,label {font-family:'DM Sans',Arial,sans-serif}
.stCaption {color:#c9b998 !important}
.stButton > button, [data-testid="stDownloadButton"] button {background:linear-gradient(#d3a45d,#986128) !important;border:1px solid #f0c783 !important;color:#111a19 !important;border-radius:9px !important;font-weight:800 !important;box-shadow:inset 0 1px 0 #ffe6a1,0 2px 12px #0008}
.stButton > button:hover {border-color:#ffe3a6 !important;filter:brightness(1.08)}
[data-testid="stMetric"] {background:linear-gradient(145deg,#203536,#111f20);border:1px solid #8b642e;border-radius:11px;padding:18px 20px;box-shadow:inset 0 0 0 3px #243230}
[data-testid="stMetricLabel"] {color:#d3bc8c}
[data-testid="stMetricValue"] {color:#f8dc99}
[data-testid="stDataFrame"], [data-testid="stTable"] {border:1px solid #936a38;border-radius:9px;overflow:hidden}
[data-testid="stAlert"] {border:1px solid #816a41;background:#242d2b}
[data-testid="stSidebar"] {background:#162728;border-right:2px solid #a8793c}
[data-testid="stTabs"] button {font-family:'Cinzel',Georgia,serif;color:#e6c485}
[data-testid="stTabs"] [aria-selected="true"] {color:#ffe0a0;border-bottom-color:#d7a453}
hr {border-color:#76542b}
.hero {position:relative;overflow:hidden;border:2px solid #b47b3c;border-radius:16px;padding:28px 30px;margin-bottom:24px;background:radial-gradient(circle at 88% 50%,#20708080 0%,#123038 20%,transparent 43%),linear-gradient(115deg,#132727,#091617);box-shadow:0 6px 24px #0009,inset 0 0 0 5px #392b1d}
.hero::before {content:'⚙';position:absolute;right:-20px;top:-100px;font-size:285px;color:#b98a4033;line-height:1}
.hero .eyebrow {color:#d0af75;font-size:.78rem;letter-spacing:.2em;font-weight:800}
.hero h1 {font-size:clamp(2rem,5vw,3.6rem);margin:.25rem 0 .1rem;text-shadow:0 2px 4px #000}
.hero p {color:#ddc8a3;margin:0;max-width:560px}
.hero .seal {font-size:1.6rem;color:#e7b960;letter-spacing:.25rem;margin-top:1rem}
.plate {padding:12px 17px;background:linear-gradient(135deg,#213635,#172423);border:1px solid #9b713b;border-radius:9px;color:#e9d5ad;margin:12px 0 22px;box-shadow:inset 0 0 0 2px #2d322a}
.plate strong {color:#f4d28d}
.section-tag {color:#c5a777;font-size:.75rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;margin:10px 0 0}
@media(max-width:640px) {.block-container {padding:1rem .85rem 3rem} .hero {padding:22px 18px}.hero::before {right:-36px;top:-30px;font-size:180px} .hero h1 {font-size:2rem} [data-testid="stMetric"]{padding:12px}}
</style>''', unsafe_allow_html=True)

TICKERS = {
 'ABB':'ABB.ST','Alfa Laval':'ALFA.ST','Assa Abloy B':'ASSA-B.ST','Atlas Copco A':'ATCO-A.ST',
 'Autoliv':'ALIV-SDB.ST','Axfood':'AXFO.ST','Boliden':'BOL.ST','Castellum':'CAST.ST',
 'Epiroc A':'EPI-A.ST','Ericsson B':'ERIC-B.ST','Essity B':'ESSITY-B.ST','Evolution':'EVO.ST',
 'Getinge B':'GETI-B.ST','Handelsbanken A':'SHB-A.ST','H&M B':'HM-B.ST','Hexagon B':'HEXA-B.ST',
 'Husqvarna B':'HUSQ-B.ST','Industrivärden C':'INDU-C.ST','Investor B':'INVE-B.ST','Kinnevik B':'KINV-B.ST',
 'Latour B':'LATO-B.ST','Lifco B':'LIFCO-B.ST','Nibe B':'NIBE-B.ST','Nordea':'NDA-SE.ST',
 'Saab B':'SAAB-B.ST','Sandvik':'SAND.ST','SCA B':'SCA-B.ST','SEB A':'SEB-A.ST',
 'Securitas B':'SECU-B.ST','Sinch':'SINCH.ST','SKF B':'SKF-B.ST','SSAB A':'SSAB-A.ST',
 'Swedbank A':'SWED-A.ST','Tele2 B':'TEL2-B.ST','Telia':'TELIA.ST','Trelleborg B':'TREL-B.ST',
 'Volvo B':'VOLV-B.ST','Volvo Cars B':'VOLCAR-B.ST','Vitec B':'VIT-B.ST','Sivers Semiconductors':'SIVE.ST',
}

@st.cache_data(ttl=60*60*4,show_spinner=False)
def prices(symbol, period='2y'):
    raw=yf.download(symbol,period=period,interval='1d',auto_adjust=True,progress=False,threads=False)
    if raw is None or raw.empty: return pd.DataFrame()
    if isinstance(raw.columns,pd.MultiIndex): raw.columns=raw.columns.get_level_values(0)
    if not {'Open','Close'}.issubset(raw.columns): return pd.DataFrame()
    return raw.dropna(subset=['Open','Close']).sort_index()

def indicators(df):
    x=df.copy(); c=x['Close'].astype(float)
    x['MA20']=c.rolling(20).mean(); x['MA50']=c.rolling(50).mean()
    diff=c.diff(); up=diff.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); down=(-diff.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    ratio=up/down.replace(0,np.nan); x['RSI']=100-100/(1+ratio)
    x['Trend']=(c>x['MA20'])&(x['MA20']>x['MA50'])
    x['Rekyl']=(c>x['MA50'])&(c<x['MA20'])&(x['RSI']<45)
    x['20 d (%)']=(c/c.shift(20)-1)*100
    x['50 d (%)']=(c/c.shift(50)-1)*100
    return x

def evaluate(df):
    if len(df)<65:return None
    x=indicators(df); last=x.iloc[-1]; price=float(last['Close'])
    trend=bool(last['Trend']); pull=bool(last['Rekyl']); mom=float(last['20 d (%)'])
    return {'Senaste kurs (SEK)':round(price,2),'20 d (%)':round(mom,1),
      '50 d (%)':round(float(last['50 d (%)']),1),'RSI 14':round(float(last['RSI']),1) if pd.notna(last['RSI']) else None,
      'Signal':'Trend' if trend else 'Rekyl' if pull else 'Avvakta',
      'Poäng':(2 if trend else 0)+(2 if pull else 0)+(1 if mom>3 else 0),
      'Senaste handelsdag':x.index[-1].strftime('%Y-%m-%d')}

def costs(notional, fee_percent,min_fee,spread_percent):
    return 2*max(notional*fee_percent/100,min_fee)+notional*spread_percent/100

def backtest(df, strategy, hold, initial, fee_percent,min_fee,spread_percent):
    """Nonoverlapping daily-bar test: signal after close t, enter at open t+1, exit at close t+hold.
    Fixed original notional; no leverage; fills illustrative, not execution realistic."""
    x=indicators(df); flag=x['Trend'] if strategy=='Trend' else x['Rekyl']
    records=[]; i=60
    while i+hold<len(x):
        if bool(flag.iloc[i]) and not pd.isna(flag.iloc[i]):
            buy=float(x['Open'].iloc[i+1]); sell=float(x['Close'].iloc[i+hold]);
            if buy>0:
                gross=(sell/buy-1); expense=costs(initial,fee_percent,min_fee,spread_percent)/initial
                records.append({'Signal':x.index[i].date(),'Köp':x.index[i+1].date(),'Sälj':x.index[i+hold].date(),
                    'Köpkurs':round(buy,2),'Säljkurs':round(sell,2),'Brutto %':round(gross*100,2),'Netto %':round((gross-expense)*100,2)})
            i+=hold+1
        else: i+=1
    return pd.DataFrame(records)

st.markdown('''<div class="hero"><div class="eyebrow">⚙ THE NAUTILUS MARKET ENGINE · EST. 2026</div><h1>SWINGTRADER <span style="color:#eac07d">1.1</span></h1><p>En viktoriansk analysmaskin för svenska aktier. Verkliga dagskurser, transparenta regler och experimentella tester.</p><div class="seal">⚙ · ◈ · ⚙</div></div>''',unsafe_allow_html=True)
st.markdown('<div class="plate"><strong>⚠ Experimentverkstad.</strong> Det här är ett analys- och testverktyg, inte verifierade köpråd. Inga riktiga order läggs. Historiska tester garanterar inte framtida utfall.</div>',unsafe_allow_html=True)

with st.sidebar:
    st.header('⚙ Maskinrummet')
    initial=st.number_input('Fiktivt kapital (kr)',1000,1000000,10000,step=1000)
    fee=st.number_input('Courtage per order (%)',0.0,5.0,0.25,step=.05)
    minimum=st.number_input('Minsta courtage (kr)',0.0,1000.0,1.0)
    spread=st.number_input('Antagen total spread (%)',0.0,10.0,.20,step=.05)
    st.metric('Tur och retur, order ⅓ kapital',f'{costs(initial/3,fee,minimum,spread):.2f} kr')
    st.caption('Förenklad kostnadsmodell. Nordnets aktuella villkor, slippage och skatter kan ge andra resultat.')

tab1,tab2,tab3=st.tabs(['🔭 Aktiescreener','⚗ Historiskt test','⚙ Om verkstaden'])
with tab1:
    st.subheader('Svensk aktiescreener')
    st.caption('40 svenska aktier · Yahoo Finance/yfinance · dagliga, potentiellt fördröjda data')
    if st.button('⟳ Uppdatera analys',key='refresh'):
        prices.clear();st.rerun()
    rows=[];errors=[]
    with st.spinner('Växlar upp analysmaskinen – hämtar 40 kurser …'):
        for name,symbol in TICKERS.items():
            try:
                res=evaluate(prices(symbol))
                if res: rows.append({'Bolag':name,'Ticker':symbol,**res})
                else: errors.append(symbol)
            except Exception: errors.append(symbol)
    if rows:
        table=pd.DataFrame(rows).sort_values(['Poäng','20 d (%)'],ascending=False)
        trend_count=int((table['Signal']=='Trend').sum());pull_count=int((table['Signal']=='Rekyl').sum())
        c1,c2,c3=st.columns(3)
        c1.metric('⚙ Analyserade',f'{len(rows)}/40');c2.metric('↗ Trend',trend_count);c3.metric('↘ Rekyl',pull_count)
        filter_signal=st.selectbox('Filtrera instrument', ['Alla','Trend','Rekyl','Avvakta'])
        visible=table if filter_signal=='Alla' else table[table['Signal']==filter_signal]
        st.dataframe(visible,hide_index=True,use_container_width=True,height=420,
            column_config={'20 d (%)':st.column_config.NumberColumn(format='%.1f %%'),
            '50 d (%)':st.column_config.NumberColumn(format='%.1f %%')})
        st.download_button('↓ Ladda ned CSV',table.to_csv(index=False).encode('utf-8-sig'),'swingtrader_signaler.csv','text/csv')
        st.caption(f'Senaste körning {date.today().isoformat()}. {len(errors)} instrument kunde inte analyseras.')
    else: st.error('Inga kurser gick att hämta. Yahoo kan ha begränsat åtkomsten; försök senare.')
    with st.expander('📜 Så fungerar signalerna'):
        st.write('**Trend:** kursen över 20-dagars medelvärde, som ligger över 50-dagars medelvärde. **Rekyl:** kursen över 50-dagars medelvärde men under 20-dagars, RSI under 45. **Avvakta:** inget villkor uppfyllt.')
        st.write('Poängen är en enkel sortering, inte en skattad vinstsannolikhet.')
with tab2:
    st.subheader('Historiskt test · försökslaboratoriet')
    st.caption('Ett enskilt instrument i taget, inga samtidiga affärer. Testet är explorativt – inte bevis för ett statistiskt övertag.')
    a,b,c=st.columns([2,1,1]); selected=a.selectbox('Aktie',list(TICKERS),index=list(TICKERS).index('Investor B'));strategy=b.selectbox('Regel',['Trend','Rekyl']); hold=c.selectbox('Behåll (handelsdagar)',[5,10,15,20],index=1)
    if st.button('⚗ Kör historiskt test',key='test'):
        with st.spinner('Beräknar testet …'):
            try: raw=prices(TICKERS[selected],period='5y')
            except Exception: raw=pd.DataFrame()
        if len(raw)<100:st.error('Otillräckliga historiska kurser för testet.')
        else:
            trade=backtest(raw,strategy,hold,initial/3,fee,minimum,spread)
            if trade.empty:st.info('Inga historiska affärer uppfyllde regeln under perioden.')
            else:
                ret=trade['Netto %']/100
                st.markdown('<div class="section-tag">Historiskt försöksresultat · inte framtidsprognos</div>',unsafe_allow_html=True)
                k1,k2,k3=st.columns(3);k1.metric('Antal affärer',len(trade));k2.metric('Positiva nettoaffärer',f'{(ret>0).mean()*100:.0f} %');k3.metric('Genomsnitt per affär',f'{ret.mean()*100:+.2f} %')
                st.dataframe(trade.iloc[::-1],hide_index=True,use_container_width=True)
                st.caption('Signal beräknas efter stängning; köp nästa handelsdag vid öppning, sälj efter valt antal dagar vid stängning. Förenklad spread och courtage per affär. Ingen skatt, eventuell slippage eller påverkan av utdelningar/övernattningsgap utöver prisserien. Affärer återinvesteras inte i detta test.')
                st.warning('Resultaten bygger på historiska data för dagens valda aktie. Urvalsbias och strategijustering kan ge överoptimistiska resultat. Testa på ny, ej använd data innan några slutsatser dras.')
    else:
        st.info('Välj aktie, regel och innehavstid. Kör sedan ett historiskt test med dina kostnadsantaganden från Maskinrummet.')
with tab3:
    st.subheader('Om analysmaskinen')
    st.markdown('''**Version 1.1** behåller samtliga 40 aktier och två transparenta signalregler från 1.0. Här finns också ett begränsat historiskt test av ett instrument åt gången.

**Inte implementerat ännu:** automatisk handel, beständig fiktiv portfölj, notifieringar, validerad statistisk sannolikhet, AI-chatt eller fullständig indexjämförelse. Alla sådana funktioner måste byggas och verifieras separat.

**Källor:** Yahoo Finance via yfinance. Data kan vara fördröjda, saknas eller vara olämpliga för produktionshandel. Verifiera prisvillkor och datalicens innan skarp användning.''')
    st.image(str(BASE/'assets'/'favicon.png'),width=115,caption='Nautilus-märket – ett kugghjul för varje marknadsrörelse')

st.caption(f'⚙ SWINGTRADER · NAUTILUS WORKSHOP · {date.today().isoformat()} · Simulering / utbildning')
