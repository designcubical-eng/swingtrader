# SwingTrader 1.0

En enkel Streamlit-screener för 40 svenska aktier, med dagliga Yahoo Finance-data via `yfinance`.

## Publicera gratis

1. Ladda upp `app.py`, `requirements.txt` och `README.md` till roten av ditt GitHub-repository.
2. Gå till https://share.streamlit.io/ och logga in med GitHub.
3. Välj **Create app / Deploy** från ditt repository. Ange `app.py` som main file path.
4. Vänta tills beroendena installerats och öppna webbadressen.

## Kör lokalt

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Viktiga begränsningar

- Endast screener; inga verkliga eller simulerade order genomförs.
- Handelslogg, backtesting och persistenta portföljer är ännu **inte** implementerade.
- Dagliga data, inte realtid. Yahoo-data kan saknas, begränsas eller ändras.
- Signalpoäng är **inte** sannolikheter eller bevis på lönsamhet.
- Courtaget och spreaden är användarinställda antaganden. Kontrollera Nordnets aktuella villkor.
- Avsett för inlärning och test, inte automatisk investeringsrådgivning eller faktisk orderläggning.
