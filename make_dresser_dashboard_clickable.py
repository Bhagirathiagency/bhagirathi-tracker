edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add id prop support to CollapsibleSection",
'''function CollapsibleSection({ title, defaultOpen, right, children }) {
  const [open, setOpen] = useState(!!defaultOpen);''',
'''function CollapsibleSection({ title, defaultOpen, right, children, id }) {
  const [open, setOpen] = useState(!!defaultOpen);''')

apply("Apply id to header for programmatic scroll+open",
'''    <div style={{ marginBottom: 4 }}>
      <div onClick={() => setOpen((o) => !o)}
        style={{ ...styles.sectionTitle, cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center" }}>''',
'''    <div style={{ marginBottom: 4 }} id={id}>
      <div onClick={() => setOpen((o) => !o)} data-collapsible-header={id ? `${id}-header` : undefined}
        style={{ ...styles.sectionTitle, cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center" }}>''')

apply("Add id to Today's/Tomorrow's Visits section",
'''          <CollapsibleSection title={t("todaysVisits")} right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{myTodaysVisits.length}</span>}>''',
'''          <CollapsibleSection id="dresser-due-visits" title={t("todaysVisits")} right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{myTodaysVisits.length}</span>}>''')

apply("Add id to Cases on Therapy section",
'''        <CollapsibleSection title={t("casesOnTherapy")}>''',
'''        <CollapsibleSection id="dresser-active-cases" title={t("casesOnTherapy")}>''')

apply("Add id to Your Reporting section",
'''        <CollapsibleSection title={t("yourReporting")}>''',
'''        <CollapsibleSection id="dresser-your-reporting" title={t("yourReporting")}>''')

apply("Add goToDresserSection helper function",
'''  const myOverdueCount = useMemo(() => myCasesActive.filter((c) => overdueDays(c) > 0).length, [myCasesActive]);''',
'''  const myOverdueCount = useMemo(() => myCasesActive.filter((c) => overdueDays(c) > 0).length, [myCasesActive]);
  const goToDresserSection = (sectionId) => {
    const header = document.querySelector(`[data-collapsible-header="${sectionId}-header"]`);
    const wrapper = document.getElementById(sectionId);
    if (header && wrapper) {
      const arrow = header.querySelector("span:last-child");
      if (arrow && arrow.textContent === "▼") header.click();
      setTimeout(() => wrapper.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    }
  };''')

apply("Make dashboard stat cards clickable buttons",
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
          </div>''',
'''      <main style={styles.main}>
        <div style={styles.cardGrid}>
          <button onClick={() => goToDresserSection("dresser-active-cases")} style={{ ...styles.statCard, borderColor: "#1B6B6333" }}>
            <div style={{ ...styles.statValue, color: "#1B6B63" }}>{myCasesActive.length}</div>
            <div style={styles.statLabel}>Active patients</div>
          </button>
          <button onClick={() => goToDresserSection("dresser-due-visits")} style={{ ...styles.statCard, borderColor: myOverdueCount > 0 ? "#E1483C33" : "#3B5BA533" }}>
            <div style={{ ...styles.statValue, color: myOverdueCount > 0 ? "#E1483C" : "#3B5BA5" }}>{myTodaysVisits.length}</div>
            <div style={styles.statLabel}>Due today/tomorrow{myOverdueCount > 0 ? ` (${myOverdueCount} overdue)` : ""}</div>
          </button>
          <button onClick={() => goToDresserSection("dresser-your-reporting")} style={{ ...styles.statCard, borderColor: myOutstandingTotal > 0 ? "#E1483C33" : "#D9720A33" }}>
            <div style={{ ...styles.statValue, color: myOutstandingTotal > 0 ? "#E1483C" : "#D9720A" }}>{fmtMoney(myOutstandingTotal)}</div>
            <div style={styles.statLabel}>Outstanding on your cases</div>
          </button>
          <button onClick={() => goToDresserSection("dresser-your-reporting")} style={{ ...styles.statCard, borderColor: "#D9720A33" }}>
            <div style={{ ...styles.statValue, color: "#D9720A" }}>{myChanges.length}</div>
            <div style={styles.statLabel}>Dressings logged (all-time)</div>
          </button>''')

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
