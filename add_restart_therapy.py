old = '''                  {showPatientHistory === c.id && (
                    <div style={styles.cardExpanded}>
                      <div style={styles.detailLabel}>Dressing change history</div>
                      {(c.dressingChanges || []).length === 0 ? <div style={styles.mutedSmall}>No changes logged.</div> : (
                        (c.dressingChanges || []).slice().sort((a, b) => new Date(b.date) - new Date(a.date)).map((e) => (
                          <div key={e.id} style={styles.paymentLine}><span>{fmtDate(e.date)}</span><span style={styles.mutedSmall}>{e.note || ""}</span></div>
                        ))
                      )}
                    </div>
                  )}'''

new = '''                  {showPatientHistory === c.id && (
                    <div style={styles.cardExpanded}>
                      <div style={styles.detailLabel}>Dressing change history</div>
                      {(c.dressingChanges || []).length === 0 ? <div style={styles.mutedSmall}>No changes logged.</div> : (
                        (c.dressingChanges || []).slice().sort((a, b) => new Date(b.date) - new Date(a.date)).map((e) => (
                          <div key={e.id} style={styles.paymentLine}><span>{fmtDate(e.date)}</span><span style={styles.mutedSmall}>{e.note || ""}</span></div>
                        ))
                      )}
                      {c.status !== "active" && (
                        <button style={{ ...styles.smallBtn, width: "100%", marginTop: 10, background: "#3B5BA5" }} onClick={() => {
                          if (window.confirm(`Doctor asked to restart therapy for ${c.patientName}? This reopens the same case — full history stays attached.`)) {
                            saveCase({ ...c, status: "active", endDate: "" }, c.id);
                          }
                        }}>Doctor Asked to Reapply — Restart Therapy</button>
                      )}
                    </div>
                  )}'''

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
