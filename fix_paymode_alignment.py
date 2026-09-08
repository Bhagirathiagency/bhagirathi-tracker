old = '''        {PAY_MODES.map((m) => (
          <div key={m} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{m}</span><span style={styles.mutedSmall}>{fmtMoney(collectedByMode[m] || 0)}</span></div>
        ))}'''

new = '''        {PAY_MODES.map((m) => (
          <div key={m} style={styles.dresserLine}>
            <span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{m}</span>
            <span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 90 }}>{fmtMoney(collectedByMode[m] || 0)}</span>
          </div>
        ))}'''

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
