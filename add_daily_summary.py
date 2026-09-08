edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add dailySummary computation before businessSWOT",
'''  const businessSWOT = useMemo(() => {''',
'''  const dailySummary = useMemo(() => {
    const today = todayISO();
    const newCasesToday = cases.filter((c) => c.applicationDate === today);
    let paymentsToday = [];
    cases.forEach((c) => (c.payments || []).forEach((p) => { if (p.date === today) paymentsToday.push(p); }));
    const collectedToday = paymentsToday.reduce((s, p) => s + Number(p.amount || 0), 0);
    let changesToday = 0;
    cases.forEach((c) => (c.dressingChanges || []).forEach((e) => { if (e.date === today) changesToday++; }));
    const dueTodayOrOverdue = cases.filter((c) => c.status === "active" && nextDueDate(c) <= today);
    const overdueToday = dueTodayOrOverdue.filter((c) => overdueDays(c) > 0);
    const doctorOwed = (doctorCommissionStats || []).reduce((s, d) => s + Math.max(0, d.owed - d.paid), 0);
    return {
      date: today, newCasesToday: newCasesToday.length, collectedToday, paymentsCountToday: paymentsToday.length,
      changesToday, dueTodayOrOverdueCount: dueTodayOrOverdue.length, overdueCount: overdueToday.length,
      lowStockCount: lowStock.length, doctorOwed,
    };
  }, [cases, lowStock, doctorCommissionStats]);

  const businessSWOT = useMemo(() => {''')

apply("Add Daily Summary UI section",
'''      {reportSubTab === "overview" && (
      <CollapsibleSection title="SWOT Analysis — Business">
        <SWOTGrid swot={businessSWOT} />
      </CollapsibleSection>
      )}''',
'''      {reportSubTab === "overview" && (
      <>
      <CollapsibleSection title={`Daily Summary — ${fmtDate(dailySummary.date)}`}>
        <div style={{ ...styles.card, padding: 18, background: "linear-gradient(160deg, #E7F1EF 0%, #FFFFFF 55%)" }}>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 16, color: "#0F3D38", marginBottom: 12 }}>
            {businessName} — Today at a Glance
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
            <div><div style={{ fontSize: 20, fontWeight: 700, color: "#1B6B63" }}>{dailySummary.newCasesToday}</div><div style={styles.mutedSmall}>New patients today</div></div>
            <div><div style={{ fontSize: 20, fontWeight: 700, color: "#1B6B63" }}>{fmtMoney(dailySummary.collectedToday)}</div><div style={styles.mutedSmall}>Collected today ({dailySummary.paymentsCountToday} payment{dailySummary.paymentsCountToday === 1 ? "" : "s"})</div></div>
            <div><div style={{ fontSize: 20, fontWeight: 700, color: "#3B5BA5" }}>{dailySummary.changesToday}</div><div style={styles.mutedSmall}>Dressing changes logged today</div></div>
            <div><div style={{ fontSize: 20, fontWeight: 700, color: dailySummary.overdueCount > 0 ? "#E1483C" : "#3B5BA5" }}>{dailySummary.dueTodayOrOverdueCount}</div><div style={styles.mutedSmall}>Due today/tomorrow ({dailySummary.overdueCount} overdue)</div></div>
          </div>
          <div style={{ borderTop: "1px solid #D9E4E0", paddingTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
            <div style={{ fontSize: 13 }}>💰 <strong>Outstanding:</strong> {fmtMoney(outstandingTotal)}</div>
            {dailySummary.lowStockCount > 0 && <div style={{ fontSize: 13, color: "#E1483C" }}>📦 <strong>{dailySummary.lowStockCount}</strong> product{dailySummary.lowStockCount > 1 ? "s" : ""} running low on stock</div>}
            {dailySummary.doctorOwed > 0 && <div style={{ fontSize: 13 }}>🩺 <strong>{fmtMoney(dailySummary.doctorOwed)}</strong> in doctor commission still owed</div>}
            {dailySummary.overdueCount > 0 && <div style={{ fontSize: 13, color: "#E1483C" }}>⚠️ <strong>{dailySummary.overdueCount}</strong> patient{dailySummary.overdueCount > 1 ? "s" : ""} overdue for a dressing change</div>}
          </div>
          <button style={{ ...styles.smallBtn, width: "100%", marginTop: 14, background: "#128577" }} onClick={() => {
            let msg = `📋 ${businessName} — Daily Summary (${fmtDate(dailySummary.date)})\\n\\n`;
            msg += `New patients today: ${dailySummary.newCasesToday}\\n`;
            msg += `Collected today: ${fmtMoney(dailySummary.collectedToday)} (${dailySummary.paymentsCountToday} payments)\\n`;
            msg += `Dressing changes logged: ${dailySummary.changesToday}\\n`;
            msg += `Due today/tomorrow: ${dailySummary.dueTodayOrOverdueCount} (${dailySummary.overdueCount} overdue)\\n`;
            msg += `Outstanding: ${fmtMoney(outstandingTotal)}\\n`;
            if (dailySummary.lowStockCount > 0) msg += `Low stock: ${dailySummary.lowStockCount} product(s)\\n`;
            if (dailySummary.doctorOwed > 0) msg += `Doctor commission owed: ${fmtMoney(dailySummary.doctorOwed)}\\n`;
            window.open(waLink(waNumberFor(businessName), msg), "_blank");
          }}>📤 Send Daily Summary on WhatsApp</button>
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="SWOT Analysis — Business">
        <SWOTGrid swot={businessSWOT} />
      </CollapsibleSection>
      </>
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
