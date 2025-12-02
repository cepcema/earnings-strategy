import yfinance as yf
import pandas as pd
from pathlib import Path
import webbrowser
from datetime import datetime, timedelta

# -------------------------------------------------
# TICKERS
# -------------------------------------------------

tickers = {
    'BHP': 'BHP.AX','WES': 'WES.AX','NAB': 'NAB.AX','CBA': 'CBA.AX',
    'NOKIA': 'NOKIA.HE','NESTE': 'NESTE.HE',
    'LVMH': 'MC.PA','OREP': 'OR.PA','HRMS': 'RMS.PA','BNPP': 'BNP.PA',
    'AIR': 'AIR.PA','AIRP': 'AI.PA','TTEF': 'TTE.PA',
    'BEIG': 'BEI.DE','ADSGN': 'ADS.DE','MBGn': 'MBG.DE','VOW3d': 'VOW3.DE',
    'VNAn': 'VNA.DE','BMWG': 'BMW.DE','DTGGe': 'DTE.DE','BAYNd': 'BAYN.DE',
    'SIEGn': 'SIE.DE','DTEGn': 'DTE.DE','MRCG': 'MRK.DE','ALVG': 'ALV.DE',
    '700': '0700.HK','9618': '9618.HK',
    'ENI': 'ENI.MI','CRDI': 'UCG.MI','STLAM': 'STLA.MI','ISP': 'ISP.MI',
    'RACE': 'RACE.MI','ENEI': 'ENEL.MI','CNHI': None,
    '3382': '3382.T','6501': '6501.T','6594': '6594.T','4568': '4568.T',
    '7203': '7203.T','4661': '4661.T','6861': '6861.T','6981': '6981.T',
    '8035': '8035.T','6367': '6367.T','8766': '8766.T',
    'ASML': 'ASML','HEIN': 'HEIA.AS',
    'SGXL': 'S68.SI','WLIL': 'F34.SI','JCYC': 'C07.SI','CAPN': '9CI.SI',
    'SIAL': 'C6L.SI','HKLD': 'H78.SI',
    'SAN': 'SAN.MC','BBVA': 'BBVA.MC','CABK': 'CABK.MC','ITX': 'ITX.MC',
    'VOLVa': 'VOLV-A.ST',
    'BARC': 'BARC.L','HSBA': 'HSBA.L','SHEL': 'SHEL.L','AZN': 'AZN.L',
    'VOD': 'VOD.L','BATS': 'BATS.L','ULVR': 'ULVR.L','LSEG': 'LSEG.L',
    'ACN': 'ACN','COST': 'COST','NKE': 'NKE','PEP': 'PEP','BLK': 'BLK',
    'JPM': 'JPM','WFC': 'WFC','GS': 'GS','JNJ': 'JNJ','MS': 'MS','ABT': 'ABT',
    'TSLA': 'TSLA','BAC': 'BAC','BX': 'BX','ISRG': 'ISRG','UNP': 'UNP',
    'AXP': 'AXP','GE': 'GE','NFLX': 'NFLX','PM': 'PM','VZ': 'VZ','META': 'META',
    'KO': 'KO','BA': 'BA','NOW': 'NOW','T': 'T','IBM': 'IBM','NEE': 'NEE',
    'SAP': 'SAP','TMO': 'TMO','MCD': 'MCD','MA': 'MA','AAPL': 'AAPL',
    'LIN': 'LIN','AMZN': 'AMZN','HON': 'HON','INTC': 'INTC','TMUS': 'TMUS',
    'XOM': 'XOM','CVX': 'CVX','ABBV': 'ABBV','PG': 'PG','DHR': 'DHR',
    'UPS': 'UPS','GOOG': 'GOOGL','PYPL': 'PYPL','V': 'V','MMM': 'MMM',
    'TXN': 'TXN','LMT': 'LMT','RTX': 'RTX','UNH': 'UNH','MSFT': 'MSFT',
    'BKNG': 'BKNG','ABNB': 'ABNB','CVS': 'CVS','BMY': 'BMY','SHOP': 'SHOP',
    'SBUX': 'SBUX','COP': 'COP','MRK': 'MRK','LLY': 'LLY','CMCSA': 'CMCSA',
    'AMD': 'AMD','PFE': 'PFE','MDLZ': 'MDLZ','CAT': 'CAT','DIS': 'DIS',
    'QCOM': 'QCOM','HMC': 'HMC','SONY': 'SONY','CSCO': 'CSCO','BABA': 'BABA',
    'LI': 'LI','HD': 'HD','NVDA': 'NVDA','INTU': 'INTU','WMT': 'WMT',
    'CRM': 'CRM','ADBE': 'ADBE','AVGO': 'AVGO','ORCL': 'ORCL'
}

# -------------------------------------------------
# COUNTRY INFERENCE FROM SYMBOL
# -------------------------------------------------

def infer_country(symbol: str | None) -> str:
    if not symbol:
        return ""
    if symbol.endswith(".AX"):
        return "Australia"
    if symbol.endswith(".HE"):
        return "Finland"
    if symbol.endswith(".PA"):
        return "France"
    if symbol.endswith(".DE"):
        return "Germany"
    if symbol.endswith(".HK"):
        return "Hong Kong"
    if symbol.endswith(".MI"):
        return "Italy"
    if symbol.endswith(".T"):
        return "Japan"
    if symbol.endswith(".AS"):
        return "Netherlands"
    if symbol.endswith(".SI"):
        return "Singapore"
    if symbol.endswith(".MC"):
        return "Spain"
    if symbol.endswith(".ST"):
        return "Sweden"
    if symbol.endswith(".L"):
        return "United Kingdom"
    # default: no suffix (mostly US listings / ADRs)
    return "United States"


# -------------------------------------------------
# HELPER: SIMPLE TERMINAL PROGRESS BAR
# -------------------------------------------------

def print_progress(current: int, total: int, label: str) -> None:
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "#" * filled + "-" * (bar_len - filled)
    print(f"\rProcessing [{bar}] {current}/{total} {label:10s}", end="", flush=True)


# -------------------------------------------------
# BUILD DATAFRAME WITH SIGNALS
# -------------------------------------------------

def build_df() -> pd.DataFrame:
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    rows = []
    total = len(tickers)

    for i, (label, sym) in enumerate(tickers.items(), start=1):
        print_progress(i, total, sym if sym else "SKIP")

        country = infer_country(sym)

        if not sym:
            rows.append({
                "Label": label,
                "Symbol": sym,
                "Country": country,
                "Next Earnings": None,
                "Open Trade": False,
                "Close Only": False,
                "Note": "skipped (no symbol)"
            })
            continue

        next_date = None
        note = "ok"
        open_trade = False
        close_only = False

        try:
            t = yf.Ticker(sym)
            edf = t.get_earnings_dates(limit=1)

            if edf is None or edf.empty:
                next_date = None
                note = "no earnings date"
            else:
                next_date = edf.index[0].date()

                if next_date == yesterday:
                    open_trade = True     # earnings were yesterday → open today
                if next_date == tomorrow:
                    close_only = True     # earnings are tomorrow → close-only today

        except Exception as e:
            next_date = None
            note = f"error: {e}"

        rows.append({
            "Label": label,
            "Symbol": sym,
            "Country": country,
            "Next Earnings": next_date,
            "Open Trade": open_trade,
            "Close Only": close_only,
            "Note": note
        })

    print()  # newline after progress bar
    df = pd.DataFrame(rows)
    df = df.sort_values(by="Next Earnings", na_position="last")
    return df


# -------------------------------------------------
# HTML GENERATION
# -------------------------------------------------

def dataframe_to_html(df: pd.DataFrame) -> str:
    table_html = df.to_html(
        classes="earnings-table",
        index=False,
        border=0,
        justify="center"
    )
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Earnings Strategy</title>
<style>
    body {{
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #0b1120;
        color: #e5e7eb;
        margin: 0;
        padding: 0;
    }}
    .container {{
        max-width: 1200px;
        margin: 40px auto;
        padding: 24px;
        background: #020617;
        border-radius: 16px;
        border: 1px solid #1f2937;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }}
    h1 {{
        margin: 0 0 4px 0;
        font-size: 28px;
    }}
    .subtitle {{
        color: #9ca3af;
        font-size: 13px;
        margin-bottom: 16px;
    }}
    .actions {{
        margin-bottom: 16px;
    }}
    button {{
        border: none;
        border-radius: 999px;
        padding: 8px 16px;
        font-size: 13px;
        cursor: pointer;
        background: #2563eb;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(37,99,235,0.4);
    }}
    button:hover {{
        background: #1d4ed8;
    }}
    .strategy-panel {{
        display: none;
        margin-bottom: 20px;
        padding: 12px 16px;
        border-radius: 12px;
        background: #020617;
        border: 1px solid #1e293b;
    }}
    .strategy-title {{
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }}
    .strategy-section {{
        margin-bottom: 10px;
    }}
    .strategy-section h3 {{
        font-size: 13px;
        margin: 0 0 6px 0;
        color: #9ca3af;
    }}
    .chip-list {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }}
    .chip {{
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        border: 1px solid rgba(148,163,184,0.4);
    }}
    .chip-open {{
        background: rgba(6,95,70,0.6);
        border-color: rgba(16,185,129,0.9);
        color: #bbf7d0;
    }}
    .chip-close {{
        background: rgba(146,64,14,0.6);
        border-color: rgba(251,191,36,0.9);
        color: #fef3c7;
    }}
    .chip-empty {{
        opacity: 0.7;
        font-style: italic;
    }}
    table.earnings-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }}
    .earnings-table th, .earnings-table td {{
        padding: 10px 8px;
        border-bottom: 1px solid #1f2937;
        text-align: left;
        white-space: nowrap;
    }}
    .earnings-table th {{
        background: #020617;
        position: sticky;
        top: 0;
        z-index: 1;
    }}
    .earnings-table tr:nth-child(odd) {{
        background: #020617;
    }}
    .earnings-table tr:nth-child(even) {{
        background: #030712;
    }}
    .earnings-table tr:hover {{
        background: #111827;
    }}
    .row-open td {{
        box-shadow: inset 2px 0 0 #22c55e;
    }}
    .row-close td {{
        box-shadow: inset 2px 0 0 #eab308;
    }}
    .footer {{
        margin-top: 16px;
        font-size: 11px;
        color: #6b7280;
        text-align: right;
    }}
</style>
</head>
<body>
<div class="container">
    <h1>Earnings Strategy</h1>
    <div class="subtitle">Generated at {now_str}</div>

    <div class="actions">
        <button id="toggle-strategy">Show today's earnings strategy</button>
    </div>

    <div id="strategy-panel" class="strategy-panel">
        <div class="strategy-title">Today's Signals</div>
        <div class="strategy-section">
            <h3>Symbols to OPEN trade (earnings were yesterday)</h3>
            <div id="open-list" class="chip-list"></div>
        </div>
        <div class="strategy-section">
            <h3>Symbols to CLOSE only (earnings are tomorrow)</h3>
            <div id="close-list" class="chip-list"></div>
        </div>
    </div>

    {table_html}

    <div class="footer">Data via yfinance / Yahoo Finance – for informational use only.</div>
</div>

<script>
(function() {{
    const table = document.querySelector('.earnings-table');
    if (!table) return;

    const headers = Array.from(table.querySelectorAll('thead th'));
    const labelIdx = headers.findIndex(th => th.textContent.trim() === 'Label');
    const symbolIdx = headers.findIndex(th => th.textContent.trim() === 'Symbol');
    const openIdx = headers.findIndex(th => th.textContent.trim() === 'Open Trade');
    const closeIdx = headers.findIndex(th => th.textContent.trim() === 'Close Only');

    const rows = Array.from(table.querySelectorAll('tbody tr'));

    const openSymbols = [];
    const closeSymbols = [];

    rows.forEach(row => {{
        const cells = row.children;
        const label = labelIdx >= 0 ? cells[labelIdx].textContent.trim() : '';
        const symbol = symbolIdx >= 0 ? cells[symbolIdx].textContent.trim() : '';
        const openText = openIdx >= 0 ? cells[openIdx].textContent.trim().toLowerCase() : 'false';
        const closeText = closeIdx >= 0 ? cells[closeIdx].textContent.trim().toLowerCase() : 'false';

        const isOpen = (openText === 'true');
        const isClose = (closeText === 'true');

        if (isOpen) {{
            openSymbols.push({{ label, symbol }});
            row.classList.add('row-open');
        }}
        if (isClose) {{
            closeSymbols.push({{ label, symbol }});
            row.classList.add('row-close');
        }}
    }});

    function renderChipList(elem, data, extraClass) {{
        elem.innerHTML = '';
        if (!data.length) {{
            const span = document.createElement('span');
            span.className = 'chip chip-empty';
            span.textContent = 'None for today';
            elem.appendChild(span);
            return;
        }}
        data.forEach(item => {{
            const span = document.createElement('span');
            span.className = 'chip ' + extraClass;
            span.textContent = item.label + ' (' + item.symbol + ')';
            elem.appendChild(span);
        }});
    }}

    renderChipList(document.getElementById('open-list'), openSymbols, 'chip-open');
    renderChipList(document.getElementById('close-list'), closeSymbols, 'chip-close');

    const panel = document.getElementById('strategy-panel');
    const btn = document.getElementById('toggle-strategy');
    let visible = false;
    btn.addEventListener('click', () => {{
        visible = !visible;
        panel.style.display = visible ? 'block' : 'none';
        btn.textContent = visible ? "Hide today's earnings strategy" : "Show today's earnings strategy";
    }});
}})();
</script>
</body>
</html>"""
    return html


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    print("Building earnings table based on yesterday/tomorrow earnings...")
    df = build_df()

    print("\nPreview:")
    print(df.head(10).to_string(index=False))

    html = dataframe_to_html(df)
    out_path = Path("index.html")
    out_path.write_text(html, encoding="utf-8")
    print(f"\nSaved HTML to: {out_path.resolve()}")

    webbrowser.open(out_path.resolve().as_uri())


if __name__ == "__main__":
    main()
