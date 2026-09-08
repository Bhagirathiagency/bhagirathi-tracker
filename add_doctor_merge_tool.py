edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add mergeDoctors function",
'''  const removeDoctorMaster = (id) => setDoctorsList((prev) => prev.filter((d) => d.id !== id));''',
'''  const removeDoctorMaster = (id) => setDoctorsList((prev) => prev.filter((d) => d.id !== id));
  const mergeDoctors = (duplicateIds, keepId, correctName) => {
    const keeper = doctorsList.find((d) => d.id === keepId);
    if (!keeper) return { renamedCases: 0, renamedCalls: 0 };
    const duplicateDoctors = doctorsList.filter((d) => duplicateIds.includes(d.id));
    const oldNames = new Set([keeper.name.trim().toLowerCase(), ...duplicateDoctors.map((d) => d.name.trim().toLowerCase())]);

    const mobile = keeper.mobile || duplicateDoctors.find((d) => d.mobile)?.mobile || "";
    const speciality = keeper.speciality || duplicateDoctors.find((d) => d.speciality)?.speciality || "";
    setDoctorsList((prev) => prev
      .filter((d) => !duplicateIds.includes(d.id))
      .map((d) => d.id === keepId ? { ...d, name: correctName, mobile, speciality } : d));

    let renamedCases = 0;
    setCases((prev) => prev.map((c) => {
      if (c.doctorName && oldNames.has(c.doctorName.trim().toLowerCase())) {
        renamedCases++;
        return { ...c, doctorName: correctName };
      }
      return c;
    }));

    let renamedCalls = 0;
    setDoctorCalls((prev) => prev.map((call) => {
      if (call.doctorName && oldNames.has(call.doctorName.trim().toLowerCase())) {
        renamedCalls++;
        return { ...call, doctorName: correctName };
      }
      return call;
    }));

    return { renamedCases, renamedCalls };
  };''')

apply("Pass mergeDoctors and doctorCalls to DoctorsMasterTab call",
'''        {tab === "doctors" && <DoctorsMasterTab doctorsList={doctorsList} addDoctorMaster={addDoctorMaster} updateDoctorMaster={updateDoctorMaster} removeDoctorMaster={removeDoctorMaster} cases={cases} />}''',
'''        {tab === "doctors" && <DoctorsMasterTab doctorsList={doctorsList} addDoctorMaster={addDoctorMaster} updateDoctorMaster={updateDoctorMaster} removeDoctorMaster={removeDoctorMaster} cases={cases} mergeDoctors={mergeDoctors} />}''')

apply("DoctorsMasterTab fn signature accepts mergeDoctors",
'''function DoctorsMasterTab({ doctorsList, addDoctorMaster, updateDoctorMaster, removeDoctorMaster, cases }) {''',
'''function DoctorsMasterTab({ doctorsList, addDoctorMaster, updateDoctorMaster, removeDoctorMaster, cases, mergeDoctors }) {
  const [mergeSelection, setMergeSelection] = useState([]);
  const [mergeMode, setMergeMode] = useState(false);
  const [mergeMsg, setMergeMsg] = useState(null);
  const [correctedName, setCorrectedName] = useState("");''')

apply("Add merge duplicates UI to Doctors Master Tab",
'''      <SectionTitle>Doctors ({sorted.length})</SectionTitle>
      {sorted.length === 0 ? <EmptyState text="No doctors added yet." /> : (
        <div style={styles.list}>
          {sorted.map((d) => {''',
'''      <SectionTitle>Doctors ({sorted.length})</SectionTitle>
      {mergeDoctors && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 14, border: "1px solid #D9E4E0", background: "#F0F8F6" }}>
          <div style={{ fontWeight: 700, color: "#1B6B63", marginBottom: 6 }}>Merge Duplicate Doctors</div>
          {!mergeMode ? (
            <>
              <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
                If the same doctor appears more than once due to spelling differences, select the duplicates below and merge them into one — every case and doctor call referencing the old spellings is updated too.
              </div>
              <button style={{ ...styles.smallBtn, background: "#1B6B63" }} onClick={() => setMergeMode(true)}>Select Doctors to Merge</button>
            </>
          ) : (
            <>
              <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>Tap every entry below that's the same doctor (2 or more), then set the correct spelling and confirm.</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 4, marginBottom: 10, maxHeight: 220, overflowY: "auto" }}>
                {doctorsList.map((d) => (
                  <label key={d.id} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, padding: "4px 0" }}>
                    <input type="checkbox" checked={mergeSelection.includes(d.id)} onChange={() => {
                      setMergeSelection((prev) => prev.includes(d.id) ? prev.filter((x) => x !== d.id) : [...prev, d.id]);
                    }} />
                    {d.name}{d.speciality ? ` · ${d.speciality}` : ""}
                  </label>
                ))}
              </div>
              {mergeSelection.length >= 2 && (
                <input type="text" placeholder="Correct spelling (e.g. Dr. Rajendra Dhondage)" style={{ ...styles.input, marginBottom: 10 }} value={correctedName} onChange={(e) => setCorrectedName(e.target.value)} />
              )}
              <div style={{ display: "flex", gap: 10 }}>
                <button style={styles.secondaryBtn} onClick={() => { setMergeMode(false); setMergeSelection([]); setCorrectedName(""); }}>Cancel</button>
                <button style={{ ...styles.smallBtn, background: "#1B6B63", flex: 1 }} disabled={mergeSelection.length < 2 || !correctedName.trim()} onClick={() => {
                  const [keepId, ...duplicateIds] = mergeSelection;
                  const result = mergeDoctors(duplicateIds, keepId, correctedName.trim());
                  setMergeMsg(`Merged ${mergeSelection.length} entries into "${correctedName.trim()}". Updated ${result.renamedCases} case(s) and ${result.renamedCalls} doctor call(s).`);
                  setMergeMode(false); setMergeSelection([]); setCorrectedName("");
                }}>Merge Selected</button>
              </div>
            </>
          )}
          {mergeMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 8, fontWeight: 600 }}>✓ {mergeMsg}</div>}
        </div>
      )}
      {sorted.length === 0 ? <EmptyState text="No doctors added yet." /> : (
        <div style={styles.list}>
          {sorted.map((d) => {''')

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
