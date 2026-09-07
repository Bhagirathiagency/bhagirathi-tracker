edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add myOutstandingCases + view toggle state",
'''  const myOutstandingTotal = useMemo(() => cases
    .filter((c) => (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase())
    .reduce((s, c) => {
      const paid = (c.payments || []).reduce((a, p) => a + Number(p.amount || 0), 0);
      return s + Math.max(0, Number(c.totalAmount || 0) - paid);
    }, 0), [cases, name]);''',
'''  const myOutstandingTotal = useMemo(() => cases
    .filter((c) => (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase())
    .reduce((s, c) => {
      const paid = (c.payments || []).reduce((a, p) => a + Number(p.amount || 0), 0);
      return s + Math.max(0, Number(c.totalAmount || 0) - paid);
    }, 0), [cases, name]);
  const myOutstandingCases = useMemo(() => cases
    .filter((c) => (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase())
    .map((c) => {
      const paid = (c.payments || []).reduce((a, p) => a + Number(p.amount || 0), 0);
      const due = Math.max(0, Number(c.totalAmount || 0) - paid);
      return { id: c.id, patientName: c.patientName, due };
    })
    .filter((c) => c.due > 0)
    .sort((a, b) => b.due - a.due), [cases, name]);
  const [myReportView, setMyReportView] = useState(null);''')

apply("Make cards clickable + conditional detail views",
'''        <CollapsibleSection title="Your Reporting">
          <div style={styles.cardGrid}>
            <div style={{ ...styles.statCard, cursor: "default", borderColor: "#D9720A33" }}>
              <div style={{ ...styles.statValue, color: "#D9720A" }}>{myChanges.length}</div>
              <div style={styles.statLabel}>Total dressings logged</div>
            </div>
            <div style={{ ...styles.statCard, cursor: "default", borderColor: myOutstandingTotal > 0 ? "#E1483C33" : "#D9720A33" }}>
              <div style={{ ...styles.statValue, color: myOutstandingTotal > 0 ? "#E1483C" : "#D9720A" }}>{fmtMoney(myOutstandingTotal)}</div>
              <div style={styles.statLabel}>Outstanding on your cases</div>
            </div>
          </div>
          {myChanges.length === 0 ? <EmptyState text="Your dressing changes will show up here." /> : (
            <div style={styles.card}>
              {myChanges.slice(0, 15).map((e) => (
                <div key={e.id} style={styles.dresserLine}>
                  <span style={{ flex: 1 }}>{e.patientName}</span>
                  <span style={styles.mutedSmall}>{fmtDate(e.date)}</span>
                </div>
              ))}
            </div>
          )}
        </CollapsibleSection>''',
'''        <CollapsibleSection title="Your Reporting">
          <div style={styles.cardGrid}>
            <div style={{ ...styles.statCard, borderColor: "#D9720A33" }} onClick={() => setMyReportView(myReportView === "changes" ? null : "changes")}>
              <div style={{ ...styles.statValue, color: "#D9720A" }}>{myChanges.length}</div>
              <div style={styles.statLabel}>Total dressings logged (tap for details)</div>
            </div>
            <div style={{ ...styles.statCard, borderColor: myOutstandingTotal > 0 ? "#E1483C33" : "#D9720A33" }} onClick={() => setMyReportView(myReportView === "outstanding" ? null : "outstanding")}>
              <div style={{ ...styles.statValue, color: myOutstandingTotal > 0 ? "#E1483C" : "#D9720A" }}>{fmtMoney(myOutstandingTotal)}</div>
              <div style={styles.statLabel}>Outstanding on your cases (tap for details)</div>
            </div>
          </div>
          {myReportView === "changes" && (
            myChanges.length === 0 ? <EmptyState text="Your dressing changes will show up here." /> : (
              <div style={styles.card}>
                {myChanges.slice(0, 15).map((e) => (
                  <div key={e.id} style={styles.dresserLine}>
                    <span style={{ flex: 1 }}>{e.patientName}</span>
                    <span style={styles.mutedSmall}>{fmtDate(e.date)}</span>
                  </div>
                ))}
              </div>
            )
          )}
          {myReportView === "outstanding" && (
            myOutstandingCases.length === 0 ? <EmptyState text="No outstanding balance on your cases." /> : (
              <div style={styles.card}>
                {myOutstandingCases.map((c) => (
                  <div key={c.id} style={styles.dresserLine}>
                    <span style={{ flex: 1 }}>{c.patientName}</span>
                    <span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(c.due)}</span>
                  </div>
                ))}
              </div>
            )
          )}
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
