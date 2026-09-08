old = '''      </CollapsibleSection>
      </>
      )}

      <SectionTitle>Revenue</SectionTitle>
      <div style={styles.cardGrid}>
        <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(totalBilled)}</div><div style={styles.statLabel}>Total Billed</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#D9720A" }}>{fmtMoney(totalCollected)}</div><div style={styles.statLabel}>Total Collected</div></div>
        <div style={{ ...styles.reportCard, cursor: "pointer" }} onClick={() => setShowOutstandingDetail(showOutstandingDetail ? null : "all")}>
          <div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(outstandingTotal)}</div><div style={styles.statLabel}>Outstanding (tap for details)</div>
        </div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#128577" }}>{fmtMoney(totalProfit)}</div><div style={styles.statLabel}>Est. Profit</div></div>
      </div>

      {showOutstandingDetail && (
        <div style={{ ...styles.card, marginBottom: 16 }}>
          <div style={styles.dresserLine} onClick={() => setShowOutstandingDetail(showOutstandingDetail === "Patient" ? "all" : "Patient")}>
            <span style={{ flex: 1, fontWeight: 600 }}>Patient Outstanding</span>
            <span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(outstandingBySource.Patient.total)}</span>
          </div>
          {showOutstandingDetail === "Patient" && outstandingBySource.Patient.cases.map((c) => (
            <div key={c.id} style={{ ...styles.dresserLine, paddingLeft: 24 }}><span style={{ flex: 1 }}>{c.name}</span><span style={styles.mutedSmall}>{fmtMoney(c.due)}</span></div>
          ))}
          <div style={styles.dresserLine} onClick={() => setShowOutstandingDetail(showOutstandingDetail === "Hospital" ? "all" : "Hospital")}>
            <span style={{ flex: 1, fontWeight: 600 }}>Hospital Outstanding</span>
            <span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(outstandingBySource.Hospital.total)}</span>
          </div>
          {showOutstandingDetail === "Hospital" && outstandingBySource.Hospital.cases.map((c) => (
            <div key={c.id} style={{ ...styles.dresserLine, paddingLeft: 24 }}><span style={{ flex: 1 }}>{c.name}</span><span style={styles.mutedSmall}>{fmtMoney(c.due)}</span></div>
          ))}
        </div>
      )}

      <CollapsibleSection title="Mode of Payment Received">
        <div style={styles.card}>
          {PAY_MODES.map((m) => (
            <div key={m} style={styles.dresserLine}>
              <span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{m}</span>
              <span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 90 }}>{fmtMoney(collectedByMode[m] || 0)}</span>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      <button style={styles.primaryBtn} onClick={sendSummary}>Send Summary on WhatsApp</button>

      {reportSubTab === "financial" && (
'''

new = '''      </CollapsibleSection>
      </>
      )}

      {reportSubTab === "financial" && (
      <>
      <SectionTitle>Revenue</SectionTitle>
      <div style={styles.cardGrid}>
        <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(totalBilled)}</div><div style={styles.statLabel}>Total Billed</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#D9720A" }}>{fmtMoney(totalCollected)}</div><div style={styles.statLabel}>Total Collected</div></div>
        <div style={{ ...styles.reportCard, cursor: "pointer" }} onClick={() => setShowOutstandingDetail(showOutstandingDetail ? null : "all")}>
          <div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(outstandingTotal)}</div><div style={styles.statLabel}>Outstanding (tap for details)</div>
        </div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#128577" }}>{fmtMoney(totalProfit)}</div><div style={styles.statLabel}>Est. Profit</div></div>
      </div>

      {showOutstandingDetail && (
        <div style={{ ...styles.card, marginBottom: 16 }}>
          <div style={styles.dresserLine} onClick={() => setShowOutstandingDetail(showOutstandingDetail === "Patient" ? "all" : "Patient")}>
            <span style={{ flex: 1, fontWeight: 600 }}>Patient Outstanding</span>
            <span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(outstandingBySource.Patient.total)}</span>
          </div>
          {showOutstandingDetail === "Patient" && outstandingBySource.Patient.cases.map((c) => (
            <div key={c.id} style={{ ...styles.dresserLine, paddingLeft: 24 }}><span style={{ flex: 1 }}>{c.name}</span><span style={styles.mutedSmall}>{fmtMoney(c.due)}</span></div>
          ))}
          <div style={styles.dresserLine} onClick={() => setShowOutstandingDetail(showOutstandingDetail === "Hospital" ? "all" : "Hospital")}>
            <span style={{ flex: 1, fontWeight: 600 }}>Hospital Outstanding</span>
            <span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(outstandingBySource.Hospital.total)}</span>
          </div>
          {showOutstandingDetail === "Hospital" && outstandingBySource.Hospital.cases.map((c) => (
            <div key={c.id} style={{ ...styles.dresserLine, paddingLeft: 24 }}><span style={{ flex: 1 }}>{c.name}</span><span style={styles.mutedSmall}>{fmtMoney(c.due)}</span></div>
          ))}
        </div>
      )}

      <CollapsibleSection title="Mode of Payment Received">
        <div style={styles.card}>
          {PAY_MODES.map((m) => (
            <div key={m} style={styles.dresserLine}>
              <span style={{ flex: 1, fontWeight: 600, textAlign: "left" }}>{m}</span>
              <span style={{ ...styles.mutedSmall, textAlign: "right", minWidth: 90 }}>{fmtMoney(collectedByMode[m] || 0)}</span>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      <button style={styles.primaryBtn} onClick={sendSummary}>Send Summary on WhatsApp</button>
      </>
      )}

      {reportSubTab === "financial" && (
'''

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
