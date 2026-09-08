edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Fix Dresser Workload alignment (Dashboard version)",
'''              <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span><span style={styles.mutedSmall}>{d.count} dressing{d.count > 1 ? "s" : ""}</span></div>''',
'''              <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{d.name}</span><span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 80 }}>{d.count} dressing{d.count > 1 ? "s" : ""}</span></div>''')

apply("Fix Company Totals alignment",
'''              <div key={c.company} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{c.company}</span><span style={styles.mutedSmall}>{c.qty} units</span></div>''',
'''              <div key={c.company} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{c.company}</span><span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 80 }}>{c.qty} units</span></div>''')

apply("Fix Dresser Workload alignment (Reports version)",
'''              <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span><span style={styles.mutedSmall}>{d.count} dressings</span></div>''',
'''              <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{d.name}</span><span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 80 }}>{d.count} dressings</span></div>''')

apply("Fix Stock Activity Log column alignment",
'''              <div key={r.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{r.product}</span>
                <span style={styles.mutedSmall}>+{r.qty} · {r.company}</span>
                <span style={{ ...styles.mutedSmall, color: "#D9720A", fontWeight: 600 }}>{r.receivedBy || "Owner"}</span>
                <span style={styles.mutedSmall}>{fmtDate(r.date)}{r.time ? ` ${r.time}` : ""}</span>
              </div>''',
'''              <div key={r.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{r.product}</span>
                <span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 100 }}>+{r.qty} · {r.company}</span>
                <span style={{ ...styles.mutedSmall, color: "#D9720A", fontWeight: 600, textAlign: "right", minWidth: 70 }}>{r.receivedBy || "Owner"}</span>
                <span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 80 }}>{fmtDate(r.date)}{r.time ? ` ${r.time}` : ""}</span>
              </div>''')

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
