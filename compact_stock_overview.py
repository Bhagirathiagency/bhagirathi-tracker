old = '''      <CollapsibleSection title="Stock Overview">
        {products.length === 0 ? <EmptyState text="No products yet." /> : (
          <>
            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={Math.max(160, products.length * 34)}>
                <BarChart data={products.map((p) => ({ name: p.name, available: p.available || 0, used: p.used || 0, low: (p.available || 0) <= LOW_STOCK_THRESHOLD }))} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid stroke="#EEF1EC" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#8A9A96" }} />
                  <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11, fill: "#182322" }} />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="available" name="Available" radius={[0, 6, 6, 0]}>
                    {products.map((p, i) => <Cell key={i} fill={(p.available || 0) <= LOW_STOCK_THRESHOLD ? "#E1483C" : "#128577"} />)}
                  </Bar>
                  <Bar dataKey="used" name="Used" fill="#3B5BA5" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.card}>
              {products.map((p) => (
                <div key={p.id} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span>
                  <span style={{ ...styles.mutedSmall, color: (p.available || 0) <= LOW_STOCK_THRESHOLD ? "#E1483C" : undefined, fontWeight: (p.available || 0) <= LOW_STOCK_THRESHOLD ? 700 : 400 }}>{p.available || 0} avail · {p.used || 0} used</span>
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>'''

new = '''      <CollapsibleSection title="Stock Overview">
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
      </CollapsibleSection>'''

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
