"""SwingTrader 1.2 Nautilus: Swedish-stock screener with bespoke brass instrument UI."""
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from PIL import Image

BASE = Path(__file__).parent
ICON = Image.open(BASE / 'assets' / 'favicon.png')
st.set_page_config(page_title='SwingTrader 1.2 | Nautilus', page_icon=ICON, layout='wide', initial_sidebar_state='collapsed')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Libre+Baskerville:wght@400;700&family=DM+Sans:wght@400;500;600;700&display=swap');
:root { color-scheme: dark; --gold:#dfb771; --goldlight:#ffe5a9; --brass:#a86d2f; --ink:#0a1718; --sea:#132a2b; --paper:#f2dfb8; }
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"] {background:#091719;color:var(--paper)}
[data-testid="stAppViewContainer"] {background: radial-gradient(ellipse at 80% -4%,#1c4447 0%,transparent 42%), repeating-linear-gradient(0deg,#091718 0,#0b1a1b 3px,#091719 5px);}
[data-testid="stHeader"] {background:transparent}
[data-testid="stToolbar"]{color:#dfb771}
.block-container {max-width:1220px;padding:1.1rem 1.7rem 5rem}
h1,h2,h3,h4 {font-family:'Cinzel',Georgia,serif!important;color:var(--goldlight)!important;text-shadow:0 2px 2px #000c;letter-spacing:.02em}
h2 {font-size:clamp(1.4rem,2.6vw,2.1rem)!important;margin-top:.35rem!important}
h3 {font-size:1.2rem!important}
p,span,div,label {font-family:'DM Sans',Arial,sans-serif}
.stCaption, [data-testid="stCaptionContainer"] {color:#cbb58d!important}
[data-testid="stAppViewBlockContainer"]>div {color:#ead8ba}
.stButton>button, [data-testid="stDownloadButton"] button, [data-testid="baseButton-primary"]{ background:linear-gradient(180deg,#fff0b6 0%,#ddb573 17%,#a26829 83%,#7b491e 100%)!important; border:2px ridge #e9c487!important;box-shadow: inset 0 1px 0 #fff5c2,inset 0 -2px 0 #613b17,0 4px 1px #000a,0 7px 17px #0008!important; color:#172020!important;font-family:'Cinzel',Georgia,serif!important;font-weight:800!important;border-radius:7px!important;padding:.55rem 1rem!important;transition:filter .15s,transform .15s}
.stButton>button:hover,[data-testid="stDownloadButton"] button:hover {filter:brightness(1.15);transform:translateY(-1px)}
[data-testid="stMetric"]{background:repeating-linear-gradient(90deg,#14292a,#172d2c 2px,#172b2c 4px);border:3px double #ac793f;border-radius:11px;padding:16px 18px;box-shadow:inset 0 0 0 3px #091718,inset 0 0 0 5px #5e452b,0 4px 12px #000b}
[data-testid="stMetricLabel"]{color:#d6b47d;font-family:'Cinzel',Georgia,serif}
[data-testid="stMetricValue"]{color:#ffdc90}
[data-testid="stDataFrame"] {border:3px ridge #ad7637!important;border-radius:9px;box-shadow:0 6px 20px #000a;overflow:hidden}
[data-testid="stAlert"] {border:1px solid #9b793f;background:#17292a;color:#f6dcae}
[data-testid="stSidebar"] {background:linear-gradient(135deg,#162f30,#0b1b1d);border-right:4px ridge #9d753c}
[data-testid="stTabs"] [role="tablist"]{gap:4px;overflow-x:auto;scrollbar-width:thin;border-bottom:2px solid #75532d;padding-bottom:8px}
[data-testid="stTabs"] button[role="tab"]{font-family:'Cinzel',Georgia,serif!important;font-size:.9rem!important;color:#d2ac70!important;background:linear-gradient(#233839,#101e20);padding:12px 18px;border:1px solid #88683d;border-radius:6px 6px 0 0;white-space:nowrap}
[data-testid="stTabs"] button[aria-selected="true"]{color:#fff0bb!important;background:linear-gradient(#825a2c,#352a1d);border:1px solid #e1b973;border-bottom:3px solid #f1c476}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:#e9be73}
[data-testid="stVerticalBlock"] [data-testid="stExpander"]{border:2px ridge #9e723c;border-radius:8px;background:#122527}
[data-baseweb="select"]>div,[data-testid="stNumberInput"] input {background:#132b2b!important;border:1px solid #9a784a!important;color:#f6d9a2!important}
hr{border-color:#9f7239}
/* Bespoke Nautilus instrument deck */
.naut-assembly {margin:8px 0 26px;position:relative;border:5px ridge #a77638;border-radius:19px;background:#071619;box-shadow:0 0 0 3px #332717,0 0 0 5px #b88340,0 13px 30px #000c;overflow:hidden}
.naut-assembly:before{content:'';position:absolute;inset:9px;border:1px solid #b48e56aa;border-radius:12px;pointer-events:none;z-index:3}
.naut-inner {display:grid;grid-template-columns:minmax(0,1fr) 290px;min-height:260px;background:radial-gradient(ellipse at 70% 40%,#22484b,#10292a 50%,#0d1b1e 85%)}
.naut-copy{position:relative;z-index:2;padding:32px 20px 27px 36px}
.naut-overline{font:700 .75rem 'Cinzel',Georgia,serif;color:#cfa15f;letter-spacing:.26em}
.naut-title{font-family:'Cinzel',Georgia,serif;font-size:clamp(2.0rem,4vw,3.4rem);font-weight:800;line-height:1.25;color:#ffe6ac;text-shadow:1px 2px 0 #5a3015,2px 4px 5px #000;white-space:nowrap;margin:14px 0 8px}
.naut-title span{font-size:.48em;vertical-align:middle;color:#d5aa66}
.naut-description{font:400 .95rem/1.65 'Libre Baskerville',serif;color:#efd9ac;max-width:580px}
.naut-trim{display:flex;align-items:center;gap:12px;color:#c2924c;margin:19px 0 0;font-size:1rem;letter-spacing:.23em}
.naut-trim:before,.naut-trim:after{content:'';height:1px;width:76px;max-width:15vw;background:linear-gradient(90deg,transparent,#ba8649)}
.naut-trim:after{transform:rotate(180deg)}
.naut-porthole{position:relative;overflow:hidden;border-left:7px ridge #ac7f44;background:radial-gradient(circle at 57% 36%,#68b4bc,#1c6977 30%,#123b46 55%,#06181e 78%)}
.naut-porthole:before{content:'';position:absolute;width:242px;height:242px;border-radius:50%;left:15px;top:10px;border:15px ridge #b57a38;box-shadow:0 0 0 7px #34271a,inset 0 0 27px #061011,0 0 0 12px #8d5d2a}
.naut-porthole:after{content:'';position:absolute;width:212px;height:212px;border-radius:50%;top:25px;left:30px;background:radial-gradient(ellipse at 60% 13%,#b4ffff55 0%,transparent 42%),repeating-linear-gradient(165deg,transparent 0 15px,#aff7fd09 17px 19px);box-shadow:inset 0 0 42px #081f2b}
.naut-submarine{position:absolute;top:110px;left:69px;width:155px;height:58px;z-index:2;filter:drop-shadow(0 8px 3px #001923)}
.naut-submarine svg{width:100%;height:100%}
.naut-rivets{position:absolute;inset:0;pointer-events:none;z-index:4;background-image:radial-gradient(circle at 17px 17px,#ffe0a5 0 2px,#673e1d 3px,#0000 5px),radial-gradient(circle at calc(100% - 17px) 17px,#ffe0a5 0 2px,#673e1d 3px,#0000 5px),radial-gradient(circle at 17px calc(100% - 17px),#ffe0a5 0 2px,#673e1d 3px,#0000 5px),radial-gradient(circle at calc(100% - 17px) calc(100% - 17px),#ffe0a5 0 2px,#673e1d 3px,#0000 5px)}
.naut-ticker-strip{position:relative;display:flex;gap:10px;justify-content:center;flex-wrap:wrap;padding:11px 15px;background:linear-gradient(#594020,#1e211e);border-top:4px ridge #a77740;color:#f4d7a0;font:700 .7rem 'Cinzel',serif;letter-spacing:.12em;text-align:center}
.naut-ticker-strip i{color:#bd8b4a;font-style:normal}
.naut-alert{background:linear-gradient(100deg,#142627,#172a29);border:3px double #a77a40;border-radius:8px;padding:13px 17px 13px 21px;margin:0 0 25px;color:#dec89f;font-size:.9rem;box-shadow:inset 0 0 0 3px #202f2a,0 4px 15px #0007}
.naut-alert b{font-family:'Cinzel',Georgia,serif;color:#ffe1a5}
.naut-heading{display:flex;align-items:center;gap:14px;margin:12px 0 8px}
.naut-heading .naut-roundel{width:47px;height:47px;flex:0 0 47px;border-radius:50%;display:grid;place-items:center;border:5px ridge #d1a666;background:radial-gradient(circle,#493827,#122224);box-shadow:inset 0 0 0 2px #e0b66b,0 4px 8px #0008;color:#f5d28c;font-size:23px}
.naut-rule{height:10px;margin:14px 0 22px;border-top:2px solid #a87d44;border-bottom:1px solid #79572e;background:linear-gradient(90deg,#080f11,#654725,#080f11)}
.naut-instrument-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0 22px}
.naut-dial{border:4px ridge #a57b45;background:linear-gradient(#173135,#0b1a1d);border-radius:9px;position:relative;padding:13px 12px;text-align:center;box-shadow:inset 0 0 0 3px #142322,0 7px 14px #0008}
.naut-dial:after{content:'';position:absolute;inset:7px;border:1px solid #8d6b40;border-radius:4px;pointer-events:none}
.naut-dial .glyph{display:block;color:#d8aa67;font:700 1.5rem Georgia,serif}
.naut-dial b{display:block;font:700 1rem 'Cinzel',serif;color:#f4daa7;margin:2px 0 5px}
.naut-dial small{font-size:.75rem;color:#c8b18b}
.naut-footnote{font-size:.75rem;color:#c9ad7d;border-top:1px solid #634c2e;padding:12px 0;margin-top:28px;text-align:center;letter-spacing:.07em}
@media(max-width:780px){.block-container{padding:1rem .8rem 3rem}.naut-inner{grid-template-columns:minmax(0,1fr) 125px;min-height:225px}.naut-copy{padding:25px 9px 20px 21px}.naut-title{font-size:clamp(1.6rem,6.3vw,2.45rem);white-space:normal;overflow-wrap:anywhere}.naut-description{font-size:.77rem;line-height:1.5}.naut-overline{font-size:.58rem;letter-spacing:.14em}.naut-porthole:before{width:160px;height:160px;left:-35px;top:30px}.naut-porthole:after{width:130px;height:130px;left:-20px;top:45px}.naut-submarine{top:90px;left:0;width:100px}.naut-ticker-strip{font-size:.57rem;gap:5px}.naut-instrument-grid{grid-template-columns:1fr 1fr}.naut-instrument-grid .naut-dial:last-child{grid-column:span 2}}
@media(max-width:400px){.naut-inner{grid-template-columns:minmax(0,1fr) 85px}.naut-title{font-size:1.55rem}.naut-porthole:before{left:-52px}.naut-porthole:after{left:-37px}.naut-submarine{left:-15px}.naut-copy{padding-left:17px}.naut-description{font-size:.71rem}}
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

st.markdown('''
<div class="naut-assembly"><div class="naut-rivets"></div>
 <div class="naut-inner"><div class="naut-copy">
  <div class="naut-overline">THE NAUTILUS MARKET ENGINE · MMXXVI</div>
  <div class="naut-title">SwingTrader <span>1.2</span></div>
  <div class="naut-description">En viktoriansk analysmaskin för svenska aktier. Fyrtio instrument under luppen, med transparenta regler och historiska försök.</div>
  <div class="naut-trim">✦ ◇ ✦</div>
 </div><div class="naut-porthole"><div class="naut-submarine"><svg viewBox="0 0 240 86" xmlns="http://www.w3.org/2000/svg"><path d="M12 48 Q70 18 193 42 L229 43 L212 53 L195 58 Q80 76 12 48Z" fill="#12282c" stroke="#b18b55" stroke-width="2"/><path d="M92 30L111 9h27l15 23M46 40L56 29l51 5" fill="#19373b" stroke="#b18b55" stroke-width="3"/><path d="M154 39L163 27l8 15" fill="#b99a5c"/><g fill="#f6c377"><circle cx="72" cy="49" r="4"/><circle cx="96" cy="49" r="4"/><circle cx="120" cy="49" r="4"/><circle cx="144" cy="49" r="4"/></g><path d="M20 48L2 36v25l20-13" fill="#213c40" stroke="#c7a061" stroke-width="2"/></svg></div></div></div>
 <div class="naut-ticker-strip"><span>SWEDISH EQUITIES</span><i>◆</i><span>DAILY SIGNALS</span><i>◆</i><span>BACKTEST LABORATORY</span></div>
</div>
<div class="naut-alert"><b>OBS · EXPERIMENTVERKSTAD</b> &nbsp; Ett analys- och testverktyg, inte verifierade köpråd. Ingen riktig handel. Historiska resultat garanterar inte framtida utfall.</div>
''',unsafe_allow_html=True)

with st.sidebar:
    st.header('Maskinrummet')
    initial=st.number_input('Fiktivt kapital (kr)',1000,1000000,10000,step=1000)
    fee=st.number_input('Courtage per order (%)',0.0,5.0,0.25,step=.05)
    minimum=st.number_input('Minsta courtage (kr)',0.0,1000.0,1.0)
    spread=st.number_input('Antagen total spread (%)',0.0,10.0,.20,step=.05)
    st.metric('Tur och retur, order ⅓ kapital',f'{costs(initial/3,fee,minimum,spread):.2f} kr')
    st.caption('Förenklad kostnadsmodell. Nordnets aktuella villkor, slippage och skatter kan ge andra resultat.')

tab1,tab2,tab3=st.tabs(['Aktiescreener','Historiskt test','Om verkstaden'])
with tab1:
    st.markdown('<div class="naut-heading"><div class="naut-roundel">✧</div><h2 style="margin:0">Svensk aktiescreener</h2></div>',unsafe_allow_html=True)
    st.caption('40 svenska aktier · Yahoo Finance/yfinance · dagliga, potentiellt fördröjda data')
    if st.button('Uppdatera analys',key='refresh'):
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
        c1.metric('Analyserade',f'{len(rows)}/40');c2.metric('Trend',trend_count);c3.metric('Rekyl',pull_count)
        filter_signal=st.selectbox('Filtrera instrument', ['Alla','Trend','Rekyl','Avvakta'])
        visible=table if filter_signal=='Alla' else table[table['Signal']==filter_signal]
        st.dataframe(visible,hide_index=True,use_container_width=True,height=420,
            column_config={'20 d (%)':st.column_config.NumberColumn(format='%.1f %%'),
            '50 d (%)':st.column_config.NumberColumn(format='%.1f %%')})
        st.download_button('Ladda ned CSV',table.to_csv(index=False).encode('utf-8-sig'),'swingtrader_signaler.csv','text/csv')
        st.caption(f'Senaste körning {date.today().isoformat()}. {len(errors)} instrument kunde inte analyseras.')
    else: st.error('Inga kurser gick att hämta. Yahoo kan ha begränsat åtkomsten; försök senare.')
    with st.expander('Så fungerar signalerna'):
        st.write('**Trend:** kursen över 20-dagars medelvärde, som ligger över 50-dagars medelvärde. **Rekyl:** kursen över 50-dagars medelvärde men under 20-dagars, RSI under 45. **Avvakta:** inget villkor uppfyllt.')
        st.write('Poängen är en enkel sortering, inte en skattad vinstsannolikhet.')
with tab2:
    st.markdown('<div class="naut-heading"><div class="naut-roundel">⌁</div><h2 style="margin:0">Historiskt test</h2></div>',unsafe_allow_html=True)
    st.caption('Ett enskilt instrument i taget, inga samtidiga affärer. Testet är explorativt – inte bevis för ett statistiskt övertag.')
    a,b,c=st.columns([2,1,1]); selected=a.selectbox('Aktie',list(TICKERS),index=list(TICKERS).index('Investor B'));strategy=b.selectbox('Regel',['Trend','Rekyl']); hold=c.selectbox('Behåll (handelsdagar)',[5,10,15,20],index=1)
    if st.button('Kör historiskt test',key='test'):
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
    st.markdown('<div class="naut-heading"><div class="naut-roundel">◈</div><h2 style="margin:0">Om analysmaskinen</h2></div>',unsafe_allow_html=True)
    st.markdown('''**Version 1.2** behåller samtliga 40 aktier och två transparenta signalregler från 1.0. Här finns också ett begränsat historiskt test av ett instrument åt gången.

**Inte implementerat ännu:** automatisk handel, beständig fiktiv portfölj, notifieringar, validerad statistisk sannolikhet, AI-chatt eller fullständig indexjämförelse. Alla sådana funktioner måste byggas och verifieras separat.

**Källor:** Yahoo Finance via yfinance. Data kan vara fördröjda, saknas eller vara olämpliga för produktionshandel. Verifiera prisvillkor och datalicens innan skarp användning.''')
    st.image(str(BASE/'assets'/'favicon.png'),width=115,caption='Nautilus-märket – ett kugghjul för varje marknadsrörelse')

st.markdown(f'<div class="naut-footnote">SWINGTRADER · NAUTILUS WORKSHOP · {date.today().isoformat()} · SIMULERING / UTBILDNING</div>', unsafe_allow_html=True)
