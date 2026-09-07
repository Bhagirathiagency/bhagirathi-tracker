edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Fix duplicate doctor grouping + track case references",
'''  const doctorMonthlyStats = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      const doctor = (c.doctorName || "Unknown").trim();
      const month = c.applicationDate ? new Date(c.applicationDate).toLocaleDateString("en-IN", { month: "short", year: "numeric" }) : "Unknown";
      const key = doctor + "||" + month;
      if (tally[key] === undefined) tally[key] = { doctor, month, count: 0, sortDate: c.applicationDate || "" };
      tally[key].count += 1;
    });
    return Object.values(tally).sort((a, b) => a.doctor.localeCompare(b.doctor) || new Date(b.sortDate) - new Date(a.sortDate));
  }, [cases]);''',
'''  const doctorMonthlyStats = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      const doctorRaw = (c.doctorName || "Unknown").trim() || "Unknown";
      const doctorKeyPart = doctorRaw.toLowerCase();
      const month = c.applicationDate ? new Date(c.applicationDate).toLocaleDateString("en-IN", { month: "short", year: "numeric" }) : "Unknown";
      const key = doctorKeyPart + "||" + month;
      if (tally[key] === undefined) tally[key] = { doctor: doctorRaw, month, count: 0, sortDate: c.applicationDate || "", cases: [] };
      tally[key].count += 1;
      tally[key].cases.push({ id: c.id, patientName: c.patientName, date: c.applicationDate });
    });
    return Object.values(tally).sort((a, b) => a.doctor.localeCompare(b.doctor) || new Date(b.sortDate) - new Date(a.sortDate));
  }, [cases]);
  const [openDoctorMonth, setOpenDoctorMonth] = useState(null);''')

apply("Add click-to-expand case reference list",
'''      <CollapsibleSection title="Doctor-wise Monthly Cases">
        {doctorMonthlyStats.length === 0 ? <EmptyState text="No cases yet." /> : (
          <div style={styles.card}>
            {doctorMonthlyStats.map((d, i) => (
              <div key={i} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{d.doctor}</span>
                <span style={styles.mutedSmall}>{d.month}</span>
                <span style={styles.mutedSmall}>{d.count} case{d.count > 1 ? "s" : ""}</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>''',
'''      <CollapsibleSection title="Doctor-wise Monthly Cases">
        {doctorMonthlyStats.length === 0 ? <EmptyState text="No cases yet." /> : (
          <div style={styles.card}>
            {doctorMonthlyStats.map((d, i) => (
              <div key={i}>
                <div style={styles.dresserLine} onClick={() => setOpenDoctorMonth(openDoctorMonth === i ? null : i)}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{d.doctor}</span>
                  <span style={styles.mutedSmall}>{d.month}</span>
                  <span style={{ ...styles.mutedSmall, textDecoration: "underline", cursor: "pointer" }}>{d.count} case{d.count > 1 ? "s" : ""}</span>
                </div>
                {openDoctorMonth === i && d.cases.map((cs) => (
                  <div key={cs.id} style={{ ...styles.dresserLine, paddingLeft: 24 }}>
                    <span style={{ flex: 1 }}>{cs.patientName}</span>
                    <span style={styles.mutedSmall}>{fmtDate(cs.date)}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>''')

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
