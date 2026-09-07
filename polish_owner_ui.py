edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Upgrade StatCard visual design",
'''function StatCard({ label, value, accent, icon, onClick }) {
  return (
    <button onClick={onClick} style={{ ...styles.statCard, borderColor: accent + "26" }}>
      {icon && (
        <div style={{ width: 32, height: 32, borderRadius: 9, background: accent + "1A", color: accent, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 10 }}>
          <Icon name={icon} size={17} />
        </div>
      )}
      <div style={{ ...styles.statValue, color: accent }}>{value}</div>
      <div style={styles.statLabel}>{label}</div>
    </button>
  );
}''',
'''function StatCard({ label, value, accent, icon, onClick }) {
  return (
    <button onClick={onClick} style={{
      ...styles.statCard,
      borderColor: accent + "26",
      background: `linear-gradient(155deg, ${accent}0F 0%, #FFFFFF 55%)`,
      boxShadow: `0 2px 4px rgba(14,36,34,0.05), 0 10px 24px ${accent}1A`,
    }}>
      {icon && (
        <div style={{ width: 36, height: 36, borderRadius: 11, background: `linear-gradient(135deg, ${accent} 0%, ${accent}CC 100%)`, color: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 10, boxShadow: `0 4px 10px ${accent}40` }}>
          <Icon name={icon} size={18} />
        </div>
      )}
      <div style={{ ...styles.statValue, color: accent }}>{value}</div>
      <div style={styles.statLabel}>{label}</div>
    </button>
  );
}''')

apply("Add colored accent bar to section headers",
'''  sectionTitle: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 15, color: "#182322", margin: "20px 0 8px" },''',
'''  sectionTitle: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 15, color: "#182322", margin: "20px 0 8px", paddingLeft: 12, borderLeft: "4px solid #1B6B63", letterSpacing: 0.2 },''')

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
