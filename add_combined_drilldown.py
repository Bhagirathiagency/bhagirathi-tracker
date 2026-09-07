edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add expandedMetric state",
'''  const [perBusiness, setPerBusiness] = useState([]);''',
'''  const [perBusiness, setPerBusiness] = useState([]);
  const [expandedMetric, setExpandedMetric] = useState(null);''')

apply("Clickable combined cards + breakdown panel",
'''      <SectionTitle>Combined Totals</SectionTitle>
      <div style={styles.cardGrid}>
        <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(combined.revenue)}</div><div style={styles.statLabel}>Total Revenue</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#128577" }}>{fmtMoney(combined.collected)}</div><div style={styles.statLabel}>Total Collected</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(combined.outstanding)}</div><div style={styles.statLabel}>Total Outstanding</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: combined.profit >= 0 ? "#128577" : "#E1483C" }}>{fmtMoney(combined.profit)}</div><div style={styles.statLabel}>Combined Net Profit</div></div>
        <div style={styles.reportCard}><div style={styles.statValue}>{combined.activeCount}</div><div style={styles.statLabel}>Active Cases (all businesses)</div></div>
        <div style={styles.reportCard}><div style={styles.statValue}>{combined.caseCount}</div><div style={styles.statLabel}>Total Cases (all-time)</div></div>
      </div>

      <SectionTitle>Per Business</SectionTitle>''',
'''      <SectionTitle>Combined Totals</SectionTitle>
      <div style={styles.cardGrid}>
        <div style={{ ...styles.reportCard, cursor: "pointer" }} onClick={() => setExpandedMetric(expandedMetric === "revenue" ? null : "revenue")}>
          <div style={styles.statValue}>{fmtMoney(combined.revenue)}</div><div style={styles.statLabel}>Total Revenue (tap for source)</div>
        </div>
        <div style={{ ...styles.reportCard, cursor: "pointer" }} onClick={() => setExpandedMetric(expandedMetric === "collected" ? null : "collected")}>
          <div style={{ ...styles.statValue, color: "#128577" }}>{fmtMoney(combined.collected)}</div><div style={styles.statLabel}>Total Collected (tap for source)</div>
        </div>
        <div style={{ ...styles.reportCard, cursor: "pointer" }} onClick={() => setExpandedMetric(expandedMetric === "outstanding" ? null : "outstanding")}>
          <div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(combined.outstanding)}</div><div style={styles.statLabel}>Total Outstanding (tap for source)</div>
        </div>
        <div style={{ ...styles.reportCard, cursor: "pointer" }} onClick={() => setExpandedMetric(expandedMetric === "profit" ? null : "profit")}>
          <div style={{ ...styles.statValue, color: combined.profit >= 0 ? "#128577" : "#E1483C" }}>{fmtMoney(combined.profit)}</div><div style={styles.statLabel}>Combined Net Profit (tap for source)</div>
        </div>
        <div style={styles.reportCard}><div style={styles.statValue}>{combined.activeCount}</div><div style={styles.statLabel}>Active Cases (all businesses)</div></div>
        <div style={styles.reportCard}><div style={styles.statValue}>{combined.caseCount}</div><div style={styles.statLabel}>Total Cases (all-time)</div></div>
      </div>

      {expandedMetric && (
        <div style={{ ...styles.card, marginBottom: 16 }}>
          <div style={{ ...styles.detailLabel, padding: "10px 14px 0" }}>
            {expandedMetric === "revenue" && "Revenue by business"}
            {expandedMetric === "collected" && "Collected by business"}
            {expandedMetric === "outstanding" && "Outstanding by business"}
            {expandedMetric === "profit" && "Profit by business"}
          </div>
          {[...perBusiness].sort((a, b) => b[expandedMetric] - a[expandedMetric]).map((b) => (
            <div key={b.id} style={styles.dresserLine}>
              <span style={{ flex: 1, fontWeight: 600 }}>{b.name}</span>
              <span style={{
                fontWeight: 700,
                color: expandedMetric === "outstanding" ? "#E1483C" : expandedMetric === "profit" ? (b.profit >= 0 ? "#128577" : "#E1483C") : expandedMetric === "collected" ? "#128577" : "#182322"
              }}>{fmtMoney(b[expandedMetric])}</span>
            </div>
          ))}
        </div>
      )}

      <SectionTitle>Per Business</SectionTitle>''')

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
