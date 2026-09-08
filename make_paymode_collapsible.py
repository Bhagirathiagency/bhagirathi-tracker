old = '''      <div style={styles.card}>
        {PAY_MODES.map((m) => (
          <div key={m} style={styles.dresserLine}>
            <span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{m}</span>
            <span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 90 }}>{fmtMoney(collectedByMode[m] || 0)}</span>
          </div>
        ))}
      </div>

      <button style={styles.primaryBtn} onClick={sendSummary}>Send Summary on WhatsApp</button>'''

new = '''      <CollapsibleSection title="Payment Received">
        <div style={styles.card}>
          {PAY_MODES.map((m) => (
            <div key={m} style={styles.dresserLine}>
              <span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{m}</span>
              <span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 90 }}>{fmtMoney(collectedByMode[m] || 0)}</span>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      <button style={styles.primaryBtn} onClick={sendSummary}>Send Summary on WhatsApp</button>'''

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
