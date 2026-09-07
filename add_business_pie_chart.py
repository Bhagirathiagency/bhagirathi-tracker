old = '''        {pnlRows.length === 0 ? <EmptyState text="No cases yet to calculate profit & loss." /> : (
          <>
            {(() => {
              const pnlRevTotal = pnlTotals.revenue + pnlTotals.rental;
              const pnlPct = (v) => pnlRevTotal > 0 ? ` (${((v / pnlRevTotal) * 100).toFixed(1)}%)` : "";
              return (
            <div style={styles.cardGrid}>
              <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(pnlRevTotal)}</div><div style={styles.statLabel}>Total Revenue</div></div>
              <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#5B6864" }}>{fmtMoney(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}{pnlPct(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}</div><div style={styles.statLabel}>Total Investment (Cost + Commission + Expenses)</div></div>
              <div style={{ ...styles.reportCard, gridColumn: "1 / -1" }}>
                <div style={{ ...styles.statValue, color: pnlTotals.profit >= 0 ? "#128577" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}{pnlPct(pnlTotals.profit)}</div>
                <div style={styles.statLabel}>Net Profit / Loss Margin</div>
              </div>
            </div>
              ); })()}

            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={[...pnlRows].reverse().map((r) => ({ label: pnlPeriodLabel(r.key, pnlGranularity), Revenue: r.revenue + r.rental, Cost: r.cost + r.commission + (r.opex || 0), Profit: r.profit }))}>'''

new = '''        {pnlRows.length === 0 ? <EmptyState text="No cases yet to calculate profit & loss." /> : (
          <>
            {(() => {
              const pnlRevTotal = pnlTotals.revenue + pnlTotals.rental;
              const pnlPct = (v) => pnlRevTotal > 0 ? ` (${((v / pnlRevTotal) * 100).toFixed(1)}%)` : "";
              return (
            <div style={styles.cardGrid}>
              <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(pnlRevTotal)}</div><div style={styles.statLabel}>Total Revenue</div></div>
              <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#5B6864" }}>{fmtMoney(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}{pnlPct(pnlTotals.cost + pnlTotals.commission + pnlTotals.opex)}</div><div style={styles.statLabel}>Total Investment (Cost + Commission + Expenses)</div></div>
              <div style={{ ...styles.reportCard, gridColumn: "1 / -1" }}>
                <div style={{ ...styles.statValue, color: pnlTotals.profit >= 0 ? "#128577" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}{pnlPct(pnlTotals.profit)}</div>
                <div style={styles.statLabel}>Net Profit / Loss Margin</div>
              </div>
            </div>
              ); })()}

            {(() => {
              const overallCost = cases.reduce((s, c) => {
                const names = getCaseProducts(c);
                return s + names.reduce((sub, name) => {
                  const prod = products.find((p) => p.name === name);
                  return sub + (prod ? Number(prod.costPrice || 0) : 0);
                }, 0);
              }, 0);
              const overallCommission = cases.reduce((s, c) => s + Number(c.doctorCommission || 0), 0);
              const overallInvestment = overallCost + overallCommission + expensesTotal;
              const overallProfit = totalCollected - overallInvestment;
              const totalBusiness = outstandingTotal + overallInvestment + Math.max(0, overallProfit);
              const pieData = [
                { name: "Outstanding", value: outstandingTotal, color: "#E1483C" },
                { name: "Investment", value: overallInvestment, color: "#D98D2B" },
                { name: "Profit", value: Math.max(0, overallProfit), color: "#128577" },
              ].filter((d) => d.value > 0);
              return totalBusiness > 0 ? (
                <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
                  <div style={{ ...styles.detailLabel, padding: "0 8px 8px" }}>Total Business Done — {fmtMoney(totalBusiness)}</div>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={(d) => `${d.name} ${((d.value / totalBusiness) * 100).toFixed(1)}%`}>
                        {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
                      </Pie>
                      <Tooltip formatter={(v) => fmtMoney(v)} contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                    </PieChart>
                  </ResponsiveContainer>
                  {overallProfit < 0 && <div style={{ ...styles.mutedSmall, padding: "0 8px", color: "#E1483C" }}>Note: overall investment currently exceeds amount collected — profit slice is ₹0 in the chart, actual shortfall is {fmtMoney(Math.abs(overallProfit))}.</div>}
                </div>
              ) : null;
            })()}

            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={[...pnlRows].reverse().map((r) => ({ label: pnlPeriodLabel(r.key, pnlGranularity), Revenue: r.revenue + r.rental, Cost: r.cost + r.commission + (r.opex || 0), Profit: r.profit }))}>'''

with open('src/App.jsx', 'r') as f:
    content = f.read()

c = content.count(old)
print("Match:", c)
if c == 1:
    content = content.replace(old, new, 1)
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("APPLIED_OK")
else:
    print("NO_MATCH_FILE_NOT_CHANGED")
