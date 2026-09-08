old = '''      <SectionTitle>Your Doctor Calls</SectionTitle>
      {myCalls.length === 0 ? <EmptyState text="No doctor calls logged yet." /> : ('''

new = '''      <SectionTitle>Doctor Directory</SectionTitle>
      <div style={styles.emptyState2}>Class A doctors get top priority for follow-up and attention. Ask the Owner to update a doctor's class as your relationship develops.</div>
      {(doctorsList || []).length === 0 ? <EmptyState text="No doctors added yet." /> : (
        <div style={styles.card}>
          {[...(doctorsList || [])].sort((a, b) => (a.doctorClass || "A").localeCompare(b.doctorClass || "A") || a.name.localeCompare(b.name)).map((d) => {
            const classInfo = { A: { color: "#128577", bg: "#E3F3EF" }, B: { color: "#D98D2B", bg: "#FBF0DE" }, C: { color: "#E1483C", bg: "#FCE7E4" } };
            const cls = classInfo[d.doctorClass] || classInfo.A;
            return (
              <div key={d.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span>
                <span style={styles.mutedSmall}>{d.speciality || ""}</span>
                <span style={{ ...styles.badge, color: cls.color, background: cls.bg }}>{d.doctorClass || "A"} Class</span>
              </div>
            );
          })}
        </div>
      )}

      <SectionTitle>Your Doctor Calls</SectionTitle>
      {myCalls.length === 0 ? <EmptyState text="No doctor calls logged yet." /> : ('''

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
