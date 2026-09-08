old = '''        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName} <span style={{ fontSize: 11, fontWeight: 600, color: "#3B5BA5" }}>· Visit #{(c.dressingChanges || []).length}</span></div>
          {open && (
            <>
              <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")} · {protocolLabel(c.protocolDays)} protocol</div>
              <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {fmtDate(c.applicationDate)}{c.applicationTime ? ` ${fmtTime(c.applicationTime)}` : ""} · {days}d</div>
              {c.dresserName && <div style={styles.cardMeta}>Dresser: {c.dresserName} · Bill to: {c.billTo || "Patient"}{c.billTo === "Hospital" && c.hospitalName ? ` (${c.hospitalName})` : ""}</div>}
            </>
          )}
        </div>
        {open && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
            <span style={{ ...styles.badge, color: st.color, background: st.bg }}>{st.label}</span>
            {c.status === "active" && overdue > 0 && <span style={styles.overdueTag}>{overdue}d change overdue</span>}
            {c.status === "active" && overdue === 0 && <span style={styles.mutedSmall}>Due {fmtDate(due)}</span>}
            {outstanding > 0 ? <span style={styles.dueTag}>{fmtMoney(outstanding)} due</span> : <span style={styles.paidTag}>Paid up</span>}
          </div>
        )}
        {!open && <span style={{ fontSize: 11, color: "#8A9A96" }}>▼</span>}'''

new = '''        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName} <span style={{ fontSize: 11, fontWeight: 600, color: "#3B5BA5" }}>· Visit #{(c.dressingChanges || []).length}</span></div>
          <div style={styles.cardMeta}>Dr. {c.doctorName}{!open ? ` · ${protocolLabel(c.protocolDays)} protocol` : ""}</div>
          {open && (
            <>
              <div style={styles.cardMeta}>{getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")} · {protocolLabel(c.protocolDays)} protocol</div>
              <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {fmtDate(c.applicationDate)}{c.applicationTime ? ` ${fmtTime(c.applicationTime)}` : ""} · {days}d</div>
              {c.dresserName && <div style={styles.cardMeta}>Dresser: {c.dresserName} · Bill to: {c.billTo || "Patient"}{c.billTo === "Hospital" && c.hospitalName ? ` (${c.hospitalName})` : ""}</div>}
            </>
          )}
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <span style={{ ...styles.badge, color: st.color, background: st.bg }}>{st.label}</span>
          {c.status === "active" && overdue > 0 && <span style={styles.overdueTag}>{overdue}d change overdue</span>}
          {c.status === "active" && overdue === 0 && <span style={styles.mutedSmall}>Due {fmtDate(due)}</span>}
          {outstanding > 0 ? <span style={styles.dueTag}>{fmtMoney(outstanding)} due</span> : <span style={styles.paidTag}>Paid up</span>}
        </div>'''

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
