edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Pass doctorsList and business name to Dashboard",
'''          <Dashboard cases={cases} machines={machines} outstandingTotal={outstandingTotal} activeCount={activeCount}
            machinesInUseCount={machinesInUseCount} overdueCount={overdueCount} dueSoonCount={dueSoonCount} dresserStats={dresserStats} lowStock={lowStock}
            products={products} setTab={setTab} goToCases={goToCases} />''',
'''          <Dashboard cases={cases} machines={machines} outstandingTotal={outstandingTotal} activeCount={activeCount}
            machinesInUseCount={machinesInUseCount} overdueCount={overdueCount} dueSoonCount={dueSoonCount} dresserStats={dresserStats} lowStock={lowStock}
            products={products} setTab={setTab} goToCases={goToCases} doctorsList={doctorsList} businessName={business.name} />''')

apply("Dashboard fn signature accepts doctorsList and businessName",
'''function Dashboard({ cases, machines, outstandingTotal, activeCount, machinesInUseCount, overdueCount, dueSoonCount, dresserStats, lowStock, products, setTab, goToCases }) {''',
'''function Dashboard({ cases, machines, outstandingTotal, activeCount, machinesInUseCount, overdueCount, dueSoonCount, dresserStats, lowStock, products, setTab, goToCases, doctorsList = [], businessName = "Bhagirathi Agency" }) {''')

apply("Add per-case reminder buttons",
'''      {todaysVisits.length > 0 && (
        <CollapsibleSection title="Today's & Tomorrow's Visits" right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{todaysVisits.length}</span>}>
          <div style={styles.card}>
            {todaysVisits.map((c) => (
              <div key={c.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{c.patientName}</span>
                <span style={styles.mutedSmall}>{c.dresserName || "Unassigned"}</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: c.overdue > 0 ? "#E1483C" : c.due === todayISO() ? "#D98D2B" : "#3B5BA5" }}>
                  {c.overdue > 0 ? `${c.overdue}d overdue` : c.due === todayISO() ? "Due today" : "Due tomorrow"}
                </span>
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}''',
'''      {todaysVisits.length > 0 && (
        <CollapsibleSection title="Today's & Tomorrow's Visits" right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{todaysVisits.length}</span>}>
          <div style={styles.card}>
            {todaysVisits.map((c) => {
              const isDueTomorrow = c.overdue === 0 && c.due !== todayISO();
              const matchedDoctor = doctorsList.find((d) => (d.name || "").trim().toLowerCase() === (c.doctorName || "").trim().toLowerCase());
              const doctorMobile = matchedDoctor ? matchedDoctor.mobile : "";
              const remindPatient = () => {
                const msg = `Hi ${c.patientName}, this is a reminder from ${businessName} — your next dressing change is due tomorrow. Our dresser will contact you to schedule the visit. Thank you!`;
                window.open(waLink(`91${(c.patientMobile || "").replace(/\\D/g, "").slice(-10)}`, msg), "_blank");
              };
              const remindDoctor = () => {
                const msg = `Hi Dr. ${c.doctorName}, reminder from ${businessName} — your patient ${c.patientName}'s dressing change is due tomorrow.`;
                window.open(waLink(`91${doctorMobile.replace(/\\D/g, "").slice(-10)}`, msg), "_blank");
              };
              return (
                <div key={c.id} style={{ padding: "10px 14px", borderBottom: "1px solid #EEF1EC" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ flex: 1, fontWeight: 600 }}>{c.patientName}</span>
                    <span style={styles.mutedSmall}>{c.dresserName || "Unassigned"}</span>
                    <span style={{ fontSize: 11, fontWeight: 700, color: c.overdue > 0 ? "#E1483C" : c.due === todayISO() ? "#D98D2B" : "#3B5BA5" }}>
                      {c.overdue > 0 ? `${c.overdue}d overdue` : c.due === todayISO() ? "Due today" : "Due tomorrow"}
                    </span>
                  </div>
                  {isDueTomorrow && (c.patientMobile || doctorMobile) && (
                    <div style={{ display: "flex", gap: 8, marginTop: 6, flexWrap: "wrap" }}>
                      {c.patientMobile && <button style={{ ...styles.linkBtn, color: "#128577" }} onClick={remindPatient}>📱 Remind Patient</button>}
                      {doctorMobile && <button style={{ ...styles.linkBtn, color: "#3B5BA5" }} onClick={remindDoctor}>📱 Remind Doctor</button>}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CollapsibleSection>
      )}''')

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
