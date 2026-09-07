edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Remove allActiveCasesDue computation",
'''  const allActiveCasesDue = useMemo(() => cases
    .filter((c) => c.status === "active")
    .map((c) => ({ ...c, due: nextDueDate(c), overdue: overdueDays(c) }))
    .sort((a, b) => (a.dresserName || "").localeCompare(b.dresserName || "") || new Date(a.due) - new Date(b.due)),
    [cases]);

  return (''',
'''  return (''')

apply("Remove Diagnostic section UI",
'''      <CollapsibleSection title="Diagnostic: All Active Cases &amp; Due Dates" right={<span style={{ fontSize: 12, fontWeight: 700, color: "#8A9A96" }}>{allActiveCasesDue.length}</span>}>
        <div style={styles.emptyState2}>Temporary tool — shows every active case's computed next-due date, so we can spot why a case isn't showing under Today's/Tomorrow's Visits.</div>
        {allActiveCasesDue.length === 0 ? <EmptyState text="No active cases." /> : (
          <div style={styles.card}>
            {allActiveCasesDue.map((c) => (
              <div key={c.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{c.patientName}</span>
                <span style={styles.mutedSmall}>{c.dresserName || "Unassigned"}</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: c.overdue > 0 ? "#E1483C" : "#3B5BA5" }}>Due: {c.due}</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      {lowStock.length > 0 && (''',
'''      {lowStock.length > 0 && (''')

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
