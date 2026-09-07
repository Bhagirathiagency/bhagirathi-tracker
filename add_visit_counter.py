edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add visit counter to DresserCaseRow title",
'''        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName}</div>
          {open && (
            <>
              <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")}</div>
              <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {protocolLabel(c.protocolDays)} protocol</div>
              <div style={styles.mutedSmall}>{doneCount}/3 photos captured</div>''',
'''        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName} <span style={{ fontSize: 11, fontWeight: 600, color: "#3B5BA5" }}>· Visit #{(c.dressingChanges || []).length}</span></div>
          {open && (
            <>
              <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")}</div>
              <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {protocolLabel(c.protocolDays)} protocol</div>
              <div style={styles.mutedSmall}>{doneCount}/3 photos captured</div>''')

apply("Add visit counter to owner CaseRow title",
'''        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName}</div>
          {open && (
            <>
              <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")} · {protocolLabel(c.protocolDays)} protocol</div>''',
'''        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName} <span style={{ fontSize: 11, fontWeight: 600, color: "#3B5BA5" }}>· Visit #{(c.dressingChanges || []).length}</span></div>
          {open && (
            <>
              <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")} · {protocolLabel(c.protocolDays)} protocol</div>''')

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
