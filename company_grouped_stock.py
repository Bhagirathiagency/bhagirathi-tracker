edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add openStockCompany state",
'''  const [expandedCashDresser, setExpandedCashDresser] = useState(null);''',
'''  const [expandedCashDresser, setExpandedCashDresser] = useState(null);
  const [openStockCompany, setOpenStockCompany] = useState(null);''')

apply("Restructure Stock Overview to be company-first, expandable",
'''      <CollapsibleSection title="Stock Overview">
        {products.length === 0 ? <EmptyState text="No products yet." /> : (() => {
          const maxVal = Math.max(1, ...products.map((p) => Math.max(p.available || 0, p.used || 0)));
          return (
            <div style={{ ...styles.card, padding: "14px 16px" }}>
              {products.map((p, i) => {
                const isLow = (p.available || 0) <= LOW_STOCK_THRESHOLD;
                const availPct = Math.round(((p.available || 0) / maxVal) * 100);
                const usedPct = Math.round(((p.used || 0) / maxVal) * 100);
                return (
                  <div key={p.id} style={{ padding: "10px 0", borderBottom: i < products.length - 1 ? "1px solid #F0EEE3" : "none" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 5 }}>
                      <span style={{ fontWeight: 700, fontSize: 13 }}>{p.name}</span>
                      <span style={{ fontSize: 11, fontWeight: 700, color: isLow ? "#E1483C" : "#128577" }}>{p.available || 0} available{isLow ? " ⚠️" : ""}</span>
                    </div>
                    <div style={{ height: 7, background: "#F0EEE3", borderRadius: 6, overflow: "hidden", position: "relative" }}>
                      <div style={{ height: "100%", width: `${availPct}%`, borderRadius: 6, background: isLow ? "linear-gradient(90deg, #E1483C, #F27C6E)" : "linear-gradient(90deg, #128577, #1B6B63)", transition: "width 0.3s" }} />
                    </div>
                    <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 3 }}>
                      <span style={{ fontSize: 10, color: "#8A9A96" }}>{p.used || 0} used all-time</span>
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })()}
      </CollapsibleSection>''',
'''      <CollapsibleSection title="Stock Overview">
        {products.length === 0 ? <EmptyState text="No products yet." /> : (() => {
          const maxVal = Math.max(1, ...products.map((p) => Math.max(p.available || 0, p.used || 0)));
          const companyGroups = groupProductsByCompany(products);
          return (
            <div style={styles.list}>
              {companyGroups.map(([company, items]) => {
                const companyAvailable = items.reduce((s, p) => s + (p.available || 0), 0);
                const companyLowCount = items.filter((p) => (p.available || 0) <= LOW_STOCK_THRESHOLD).length;
                const isOpen = openStockCompany === company;
                return (
                  <div key={company} style={styles.card}>
                    <div style={{ padding: "14px 16px", cursor: "pointer", display: "flex", alignItems: "center", gap: 10 }} onClick={() => setOpenStockCompany(isOpen ? null : company)}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 700, fontSize: 14, fontFamily: "'Space Grotesk', sans-serif" }}>{company}</div>
                        <div style={{ fontSize: 11, color: "#8A9A96", marginTop: 2 }}>{items.length} product{items.length > 1 ? "s" : ""} · {companyAvailable} units available{companyLowCount > 0 ? ` · ${companyLowCount} low` : ""}</div>
                      </div>
                      {companyLowCount > 0 && <span style={{ fontSize: 11, fontWeight: 700, color: "#E1483C" }}>⚠️</span>}
                      <span style={{ fontSize: 12, color: "#8A9A96" }}>{isOpen ? "▲" : "▼"}</span>
                    </div>
                    {isOpen && (
                      <div style={{ padding: "0 16px 14px" }}>
                        {items.map((p, i) => {
                          const isLow = (p.available || 0) <= LOW_STOCK_THRESHOLD;
                          const availPct = Math.round(((p.available || 0) / maxVal) * 100);
                          return (
                            <div key={p.id} style={{ padding: "10px 0", borderTop: "1px solid #F0EEE3" }}>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 5 }}>
                                <span style={{ fontWeight: 700, fontSize: 13 }}>{p.name}</span>
                                <span style={{ fontSize: 11, fontWeight: 700, color: isLow ? "#E1483C" : "#128577" }}>{p.available || 0} available{isLow ? " ⚠️" : ""}</span>
                              </div>
                              <div style={{ height: 7, background: "#F0EEE3", borderRadius: 6, overflow: "hidden", position: "relative" }}>
                                <div style={{ height: "100%", width: `${availPct}%`, borderRadius: 6, background: isLow ? "linear-gradient(90deg, #E1483C, #F27C6E)" : "linear-gradient(90deg, #128577, #1B6B63)", transition: "width 0.3s" }} />
                              </div>
                              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 3 }}>
                                <span style={{ fontSize: 10, color: "#8A9A96" }}>{p.used || 0} used all-time</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })()}
      </CollapsibleSection>''')

with open('src/App.jsx', 'r') as f:
    content = f.read()

all_ok = True
for label, old, new in edits:
    c = content.count(old)
    print(label, "matches:", c)
    if c != 1:
        all_ok = False
    else:
        content = content.replace(old, new, 1)

if all_ok:
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("ALL_APPLIED_OK")
else:
    print("SOME_MISMATCHES_FILE_NOT_CHANGED")
