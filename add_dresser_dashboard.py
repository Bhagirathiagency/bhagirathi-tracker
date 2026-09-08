edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add myOverdueCount computation",
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
  const myOverdueCount = useMemo(() => myCasesActive.filter((c) => overdueDays(c) > 0).length, [myCasesActive]);''')

apply("Add Dresser Dashboard stat cards above My Profile",
'''      <main style={styles.main}>
        <CollapsibleSection title={t("myProfile")}>''',
'''      <main style={styles.main}>
        <div style={styles.cardGrid}>
          <div style={{ ...styles.statCard, borderColor: "#1B6B6333", cursor: "default" }}>
            <div style={{ ...styles.statValue, color: "#1B6B63" }}>{myCasesActive.length}</div>
            <div style={styles.statLabel}>Active patients</div>
          </div>
          <div style={{ ...styles.statCard, borderColor: myOverdueCount > 0 ? "#E1483C33" : "#3B5BA533", cursor: "default" }}>
            <div style={{ ...styles.statValue, color: myOverdueCount > 0 ? "#E1483C" : "#3B5BA5" }}>{myTodaysVisits.length}</div>
            <div style={styles.statLabel}>Due today/tomorrow{myOverdueCount > 0 ? ` (${myOverdueCount} overdue)` : ""}</div>
          </div>
          <div style={{ ...styles.statCard, borderColor: myOutstandingTotal > 0 ? "#E1483C33" : "#D9720A33", cursor: "default" }}>
            <div style={{ ...styles.statValue, color: myOutstandingTotal > 0 ? "#E1483C" : "#D9720A" }}>{fmtMoney(myOutstandingTotal)}</div>
            <div style={styles.statLabel}>Outstanding on your cases</div>
          </div>
          <div style={{ ...styles.statCard, borderColor: "#D9720A33", cursor: "default" }}>
            <div style={{ ...styles.statValue, color: "#D9720A" }}>{myChanges.length}</div>
            <div style={styles.statLabel}>Dressings logged (all-time)</div>
          </div>
        </div>

        <CollapsibleSection title={t("myProfile")}>''')

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
