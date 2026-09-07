edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add myCasesStopped computation",
'''  const myCasesActive = cases.filter((c) => c.status === "active" && (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase());''',
'''  const myCasesActive = cases.filter((c) => c.status === "active" && (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase());
  const myCasesHistory = cases.filter((c) => c.status !== "active" && (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase())
    .sort((a, b) => new Date(b.endDate || b.applicationDate) - new Date(a.endDate || a.applicationDate));
  const [showPatientHistory, setShowPatientHistory] = useState(false);''')

apply("Add Patient History section",
'''        <CollapsibleSection title="Your Reporting">''',
'''        <CollapsibleSection title="Patient History (Stopped / Reapplied)" right={myCasesHistory.length > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#8A9A96" }}>{myCasesHistory.length}</span> : null}>
          {myCasesHistory.length === 0 ? <EmptyState text="Patients you've treated will show up here once their therapy is stopped or reapplied." /> : (
            <div style={styles.list}>
              {myCasesHistory.map((c) => (
                <div key={c.id} style={styles.card}>
                  <div style={styles.cardTop} onClick={() => setShowPatientHistory(showPatientHistory === c.id ? false : c.id)}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={styles.cardTitle}>{c.patientName}</div>
                      <div style={styles.cardMeta}>Dr. {c.doctorName} · {STATUS[c.status] ? STATUS[c.status].label : c.status}</div>
                      <div style={styles.mutedSmall}>{c.endDate ? `Ended ${fmtDate(c.endDate)}` : `Started ${fmtDate(c.applicationDate)}`}</div>
                    </div>
                  </div>
                  {showPatientHistory === c.id && (
                    <div style={styles.cardExpanded}>
                      <div style={styles.detailLabel}>Dressing change history</div>
                      {(c.dressingChanges || []).length === 0 ? <div style={styles.mutedSmall}>No changes logged.</div> : (
                        (c.dressingChanges || []).slice().sort((a, b) => new Date(b.date) - new Date(a.date)).map((e) => (
                          <div key={e.id} style={styles.paymentLine}><span>{fmtDate(e.date)}</span><span style={styles.mutedSmall}>{e.note || ""}</span></div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CollapsibleSection>

        <CollapsibleSection title="Your Reporting">''')

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
