old = '''      {companyTotals.length > 0 && (
        <CollapsibleSection title="Stock Received by Company">
          <div style={styles.card}>
            {companyTotals.map((c) => (
              <div key={c.company} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{c.company}</span><span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 80 }}>{c.qty} units</span></div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {companyStockSales.length > 0 && (
        <CollapsibleSection title="Company-wise Stock & Sales Statement">
          <div style={{ ...styles.emptyState2, marginBottom: 8 }}>Available &amp; used are current stock-wide figures (stock isn't tracked per supplier batch once received). Est. sales = units used × MRP.</div>
          {companyStockSales.map((co) => (
            <div key={co.company} style={{ ...styles.card, marginBottom: 10 }}>
              <div style={{ padding: "12px 14px", borderBottom: "1px solid #EEF1EC", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 }}>{co.company}</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: "#D9720A" }}>Est. sales {fmtMoney(co.estSales)}</span>
              </div>
              {co.productList.map((p) => (
                <div key={p.name} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span>
                  <span style={styles.mutedSmall}>Recd {p.received}</span>
                  <span style={styles.mutedSmall}>Avail {p.available}</span>
                  <span style={styles.mutedSmall}>Used {p.used}</span>
                </div>
              ))}
            </div>
          ))}
        </CollapsibleSection>
      )}

      {reportSubTab === "financial" && (
      <CollapsibleSection title="Machine Rental Collections"'''

new = '''      {reportSubTab === "stock" && (
      <>
      {companyTotals.length > 0 && (
        <CollapsibleSection title="Stock Received by Company">
          <div style={styles.card}>
            {companyTotals.map((c) => (
              <div key={c.company} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{c.company}</span><span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 80 }}>{c.qty} units</span></div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {companyStockSales.length > 0 && (
        <CollapsibleSection title="Company-wise Stock & Sales Statement">
          <div style={{ ...styles.emptyState2, marginBottom: 8 }}>Available &amp; used are current stock-wide figures (stock isn't tracked per supplier batch once received). Est. sales = units used × MRP.</div>
          {companyStockSales.map((co) => (
            <div key={co.company} style={{ ...styles.card, marginBottom: 10 }}>
              <div style={{ padding: "12px 14px", borderBottom: "1px solid #EEF1EC", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 }}>{co.company}</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: "#D9720A" }}>Est. sales {fmtMoney(co.estSales)}</span>
              </div>
              {co.productList.map((p) => (
                <div key={p.name} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span>
                  <span style={styles.mutedSmall}>Recd {p.received}</span>
                  <span style={styles.mutedSmall}>Avail {p.available}</span>
                  <span style={styles.mutedSmall}>Used {p.used}</span>
                </div>
              ))}
            </div>
          ))}
        </CollapsibleSection>
      )}
      </>
      )}

      {reportSubTab === "financial" && (
      <CollapsibleSection title="Machine Rental Collections"'''

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
