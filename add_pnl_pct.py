with open('src/App.jsx', 'r') as f:
    content = f.read()

old1 = '''        {pnlRows.length === 0 ? <EmptyState text="No cases yet to calculate profit & loss." /> : (
          <>
            <div style={styles.cardGrid}>
              <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(pnlTotals.revenue + pnlTotals.rental)}</div><div style={styles.statLabel}>Total Revenue</div></div>
              <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}</div><div style={styles.statLabel}>Total Cost + Commission + Expenses</div></div>
              <div style={{ ...styles.reportCard, gridColumn: "1 / -1" }}>
                <div style={{ ...styles.statValue, color: pnlTotals.profit >= 0 ? "#D9720A" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}</div>
                <div style={styles.statLabel}>Net Profit / Loss</div>
              </div>
            </div>'''

new1 = '''        {pnlRows.length === 0 ? <EmptyState text="No cases yet to calculate profit & loss." /> : (
          <>
            {(() => {
              const pnlRevTotal = pnlTotals.revenue + pnlTotals.rental;
              const pnlPct = (v) => pnlRevTotal > 0 ? ` (${((v / pnlRevTotal) * 100).toFixed(1)}%)` : "";
              return (
            <div style={styles.cardGrid}>
              <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(pnlRevTotal)}</div><div style={styles.statLabel}>Total Revenue</div></div>
              <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}{pnlPct(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}</div><div style={styles.statLabel}>Total Cost + Commission + Expenses</div></div>
              <div style={{ ...styles.reportCard, gridColumn: "1 / -1" }}>
                <div style={{ ...styles.statValue, color: pnlTotals.profit >= 0 ? "#D9720A" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}{pnlPct(pnlTotals.profit)}</div>
                <div style={styles.statLabel}>Net Profit / Loss Margin</div>
              </div>
            </div>
              ); })()}'''

count1 = content.count(old1)
print("Totals block match:", count1)
if count1:
    content = content.replace(old1, new1, 1)

old2 = '''                  <div style={{ display: "flex", gap: 14, fontSize: 12, color: "#5B6864", flexWrap: "wrap" }}>
                    <span>{r.cases} case{r.cases > 1 ? "s" : ""}</span>
                    <span>Revenue {fmtMoney(r.revenue + r.rental)}</span>
                    <span>Cost {fmtMoney(r.cost)}</span>
                    {r.commission > 0 && <span>Commission {fmtMoney(r.commission)}</span>}
                    {r.opex > 0 && <span>Expenses {fmtMoney(r.opex)}</span>}
                  </div>'''

new2 = '''                  <div style={{ display: "flex", gap: 14, fontSize: 12, color: "#5B6864", flexWrap: "wrap" }}>
                    {(() => {
                      const rowRev = r.revenue + r.rental;
                      const rowPct = (v) => rowRev > 0 ? ` (${((v / rowRev) * 100).toFixed(1)}%)` : "";
                      return (<>
                    <span>{r.cases} case{r.cases > 1 ? "s" : ""}</span>
                    <span>Revenue {fmtMoney(rowRev)}</span>
                    <span>Cost {fmtMoney(r.cost)}{rowPct(r.cost)}</span>
                    {r.commission > 0 && <span>Commission {fmtMoney(r.commission)}{rowPct(r.commission)}</span>}
                    {r.opex > 0 && <span>Expenses {fmtMoney(r.opex)}{rowPct(r.opex)}</span>}
                    <span style={{ fontWeight: 700, color: r.profit >= 0 ? "#D9720A" : "#E1483C" }}>Profit {fmtMoney(r.profit)}{rowPct(r.profit)}</span>
                    </>); })()}
                  </div>'''

count2 = content.count(old2)
print("Row block match:", count2)
if count2:
    content = content.replace(old2, new2, 1)

with open('src/App.jsx', 'w') as f:
    f.write(content)
print('DONE')
