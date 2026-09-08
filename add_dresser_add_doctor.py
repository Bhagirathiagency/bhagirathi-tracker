edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add new doctor form state",
'''  const [notes, setNotes] = useState("");

  const myCalls = useMemo(''',
'''  const [notes, setNotes] = useState("");
  const [newDocName, setNewDocName] = useState("");
  const [newDocMobile, setNewDocMobile] = useState("");
  const [newDocSpeciality, setNewDocSpeciality] = useState("");
  const [newDocClass, setNewDocClass] = useState("A");
  const [addDocMsg, setAddDocMsg] = useState(null);

  const myCalls = useMemo(''')

apply("Update Doctor Directory heading and add new-doctor form",
'''      <SectionTitle>Doctor Directory</SectionTitle>
      <div style={styles.emptyState2}>Class A doctors get top priority for follow-up and attention. Ask the Owner to update a doctor's class as your relationship develops.</div>
      {(doctorsList || []).length === 0 ? <EmptyState text="No doctors added yet." /> : (''',
'''      <SectionTitle>Doctor Directory</SectionTitle>
      <div style={styles.emptyState2}>Class A doctors get top priority for follow-up and attention.</div>
      {addDoctorMaster && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 12 }}>
          <div style={{ ...styles.detailLabel, marginBottom: 8 }}>Add a New Doctor</div>
          <div style={styles.addPaymentRow}>
            <input type="text" placeholder="Doctor name" style={{ ...styles.smallInput, flex: 1 }} value={newDocName} onChange={(e) => setNewDocName(e.target.value)} />
            <input type="tel" placeholder="Mobile (optional)" style={styles.smallInput} value={newDocMobile} onChange={(e) => setNewDocMobile(e.target.value)} />
          </div>
          <div style={styles.addPaymentRow}>
            <input type="text" placeholder="Speciality (optional)" style={{ ...styles.smallInput, flex: 1 }} value={newDocSpeciality} onChange={(e) => setNewDocSpeciality(e.target.value)} />
            <select style={styles.smallInput} value={newDocClass} onChange={(e) => setNewDocClass(e.target.value)}>
              <option value="A">A Class</option>
              <option value="B">B Class</option>
              <option value="C">C Class</option>
            </select>
            <button style={styles.smallBtn} onClick={() => {
              if (!newDocName.trim()) return;
              const alreadyKnown = (doctorsList || []).some((d) => d.name.trim().toLowerCase() === newDocName.trim().toLowerCase());
              if (alreadyKnown) { setAddDocMsg("This doctor is already in the list."); return; }
              addDoctorMaster({ name: newDocName.trim(), mobile: newDocMobile.trim(), speciality: newDocSpeciality.trim(), doctorClass: newDocClass });
              setNewDocName(""); setNewDocMobile(""); setNewDocSpeciality(""); setNewDocClass("A");
              setAddDocMsg("Doctor added.");
              setTimeout(() => setAddDocMsg(null), 3000);
            }}>Add Doctor</button>
          </div>
          {addDocMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 6, fontWeight: 600 }}>✓ {addDocMsg}</div>}
        </div>
      )}
      {(doctorsList || []).length === 0 ? <EmptyState text="No doctors added yet." /> : (''')

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
