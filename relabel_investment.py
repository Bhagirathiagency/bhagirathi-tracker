with open('src/App.jsx', 'r') as f:
    content = f.read()

old = '''              <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}{pnlPct(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}</div><div style={styles.statLabel}>Total Cost + Commission + Expenses</div></div>'''
new = '''              <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#5B6864" }}>{fmtMoney(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}{pnlPct(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}</div><div style={styles.statLabel}>Total Investment (Cost + Commission + Expenses)</div></div>'''

c = content.count(old)
print("Match:", c)
if c:
    content = content.replace(old, new, 1)
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("APPLIED_OK")
else:
    print("NO_MATCH_FILE_NOT_CHANGED")
