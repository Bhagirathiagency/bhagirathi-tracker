edits = []

def apply(label, old, new, count=1):
    edits.append((label, old, new, count))

apply("New previousOutstanding state",
'''  const [fixedExpenses, setFixedExpenses] = useState([]);''',
'''  const [fixedExpenses, setFixedExpenses] = useState([]);
  const [previousOutstanding, setPreviousOutstanding] = useState([]);''', 1)

apply("Load key",
'''        loadKey(bkey(businessId, "wca-fixed-expenses"), []),''',
'''        loadKey(bkey(businessId, "wca-fixed-expenses"), []),
        loadKey(bkey(businessId, "wca-previous-outstanding"), []),''', 1)

apply("Destructure var",
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, fixedExps, acctPin, chals, docsList, topics] = await Promise.all([''',
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, fixedExps, prevOut, acctPin, chals, docsList, topics] = await Promise.all([''', 1)

apply("setPreviousOutstanding",
'''      setFixedExpenses(Array.isArray(fixedExps) ? fixedExps : []);''',
'''      setFixedExpenses(Array.isArray(fixedExps) ? fixedExps : []);
      setPreviousOutstanding(Array.isArray(prevOut) ? prevOut : []);''', 1)

apply("Save effect",
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-fixed-expenses"), fixedExpenses); }, [fixedExpenses, loaded, businessId]);''',
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-fixed-expenses"), fixedExpenses); }, [fixedExpenses, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-previous-outstanding"), previousOutstanding); }, [previousOutstanding, loaded, businessId]);''', 1)

apply("Add/delete/payment functions",
'''  const addFixedExpense = (entry) => setFixedExpenses((prev) => [...prev, { id: uid(), ...entry }]);
  const deleteFixedExpense = (id) => setFixedExpenses((prev) => prev.filter((e) => e.id !== id));''',
'''  const addFixedExpense = (entry) => setFixedExpenses((prev) => [...prev, { id: uid(), ...entry }]);
  const deleteFixedExpense = (id) => setFixedExpenses((prev) => prev.filter((e) => e.id !== id));
  const addPreviousOutstanding = (entry) => setPreviousOutstanding((prev) => [...prev, { id: uid(), date: todayISO(), payments: [], ...entry }]);
  const deletePreviousOutstanding = (id) => setPreviousOutstanding((prev) => prev.filter((e) => e.id !== id));
  const addPreviousOutstandingPayment = (id, payment) => setPreviousOutstanding((prev) => prev.map((e) => e.id === id ? { ...e, payments: [...(e.payments || []), { id: uid(), date: todayISO(), ...payment }] } : e));''', 1)

apply("Pass previousOutstanding props at all call sites",
'''fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense}''',
'''fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense} previousOutstanding={previousOutstanding} addPreviousOutstanding={addPreviousOutstanding} deletePreviousOutstanding={deletePreviousOutstanding} addPreviousOutstandingPayment={addPreviousOutstandingPayment}''', 0)

apply("OwnerShell fn signature",
'''fixedExpenses, addFixedExpense, deleteFixedExpense, ownerLogins,''',
'''fixedExpenses, addFixedExpense, deleteFixedExpense, previousOutstanding, addPreviousOutstanding, deletePreviousOutstanding, addPreviousOutstandingPayment, ownerLogins,''', 1)

apply("ReportsTab fn signature",
'''fixedExpenses = [], addFixedExpense, deleteFixedExpense, dresserProfiles = {},''',
'''fixedExpenses = [], addFixedExpense, deleteFixedExpense, previousOutstanding = [], addPreviousOutstanding, deletePreviousOutstanding, addPreviousOutstandingPayment, dresserProfiles = {},''', 1)

apply("Extend outstandingBySource with previousOutstanding",
'''  const outstandingBySource = useMemo(() => {
    const groups = { Patient: { total: 0, cases: [] }, Hospital: { total: 0, cases: [] } };
    cases.forEach((c) => {
      const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
      const due = Math.max(0, Number(c.totalAmount || 0) + Number(c.machineRentalAmount || 0) - paid);
      if (due <= 0) return;
      const key = c.billTo === "Hospital" ? "Hospital" : "Patient";
      groups[key].total += due;
      groups[key].cases.push({ id: c.id, name: c.billTo === "Hospital" ? (c.hospitalName || c.patientName) : c.patientName, due });
    });
    return groups;
  }, [cases]);''',
'''  const previousOutstandingWithRemaining = useMemo(() => (previousOutstanding || []).map((e) => {
    const paid = (e.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
    return { ...e, paid, remaining: Math.max(0, Number(e.amount || 0) - paid) };
  }), [previousOutstanding]);
  const previousOutstandingTotal = useMemo(() => previousOutstandingWithRemaining.reduce((s, e) => s + e.remaining, 0), [previousOutstandingWithRemaining]);

  const outstandingBySource = useMemo(() => {
    const groups = { Patient: { total: 0, cases: [] }, Hospital: { total: 0, cases: [] } };
    cases.forEach((c) => {
      const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
      const due = Math.max(0, Number(c.totalAmount || 0) + Number(c.machineRentalAmount || 0) - paid);
      if (due <= 0) return;
      const key = c.billTo === "Hospital" ? "Hospital" : "Patient";
      groups[key].total += due;
      groups[key].cases.push({ id: c.id, name: c.billTo === "Hospital" ? (c.hospitalName || c.patientName) : c.patientName, due });
    });
    previousOutstandingWithRemaining.forEach((e) => {
      if (e.remaining <= 0) return;
      const key = e.billTo === "Hospital" ? "Hospital" : "Patient";
      groups[key].total += e.remaining;
      groups[key].cases.push({ id: e.id, name: e.name + " (previous due)", due: e.remaining });
    });
    return groups;
  }, [cases, previousOutstandingWithRemaining]);''', 1)

apply("Add form state",
'''  const [supplierForm, setSupplierForm] = useState({ supplier: "", type: "bill", amount: "", note: "" });''',
'''  const [prevOutForm, setPrevOutForm] = useState({ name: "", billTo: "Patient", amount: "", note: "" });
  const [prevOutPayForm, setPrevOutPayForm] = useState({});
  const [openPrevOut, setOpenPrevOut] = useState(null);
  const [supplierForm, setSupplierForm] = useState({ supplier: "", type: "bill", amount: "", note: "" });''', 1)

apply("Insert Previous Outstanding UI section",
'''      <CollapsibleSection title="Outstanding Payments by Patient">''',
'''      <CollapsibleSection title="Previous Outstanding (Before This App)" right={previousOutstandingTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(previousOutstandingTotal)}</span> : null}>
        <div style={styles.emptyState2}>Old dues from before you started using this app — add them here so they're included in your Outstanding totals and the pie chart above.</div>
        {!readOnly && (
          <div style={styles.formGrid}>
            <div style={styles.addPaymentRow}>
              <input type="text" placeholder="Patient / Hospital name" style={{ ...styles.smallInput, flex: 1 }} value={prevOutForm.name} onChange={(e) => setPrevOutForm((f) => ({ ...f, name: e.target.value }))} />
              <select style={styles.smallInput} value={prevOutForm.billTo} onChange={(e) => setPrevOutForm((f) => ({ ...f, billTo: e.target.value }))}>
                <option value="Patient">Patient</option>
                <option value="Hospital">Hospital</option>
              </select>
            </div>
            <div style={styles.addPaymentRow}>
              <input type="number" placeholder="Amount owed ₹" style={styles.smallInput} value={prevOutForm.amount} onChange={(e) => setPrevOutForm((f) => ({ ...f, amount: e.target.value }))} />
              <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={prevOutForm.note} onChange={(e) => setPrevOutForm((f) => ({ ...f, note: e.target.value }))} />
              <button style={styles.smallBtn} onClick={() => {
                const amt = Number(prevOutForm.amount);
                if (!prevOutForm.name.trim() || !amt || amt <= 0) return;
                addPreviousOutstanding({ name: prevOutForm.name.trim(), billTo: prevOutForm.billTo, amount: amt, note:
npm run build
git add src/App.jsx combined_pending.py
git commit -m "Add Previous Outstanding tracking and give Devashish access to add entries"
git push origin main
cd ~/Desktop/bhagirathi-tracker-real
git pull origin main
npm run build
git add src/App.jsx combined_pending.py
git commit -m "Add Previous Outstanding tracking and give Devashish access to add entries"
git push origin main
npm run build
git add src/App.jsx combined_pending.py
git commit -m "Add Previous Outstanding tracking and give Devashish access to add entries"
git push origin main
cd ~/Desktop/bhagirathi-tracker-real
git pull origin main
cat > fix_outstanding_hospital_patient.py << 'PYEOF'
edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Filter Patient list to exclude Hospital-billed cases",
'''  const outstandingByPatient = useMemo(() => {
    return cases
      .map((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        const balance = Math.max(0, Number(c.totalAmount || 0) - paid);
        const daysOutstanding = c.applicationDate ? daysBetween(c.applicationDate, todayISO()) : 0;
        return { ...c, balance, daysOutstanding };
      })
      .filter((c) => c.balance > 0)
      .sort((a, b) => b.daysOutstanding - a.daysOutstanding || b.balance - a.balance);
  }, [cases]);''',
'''  const outstandingByPatient = useMemo(() => {
    return cases
      .filter((c) => c.billTo !== "Hospital")
      .map((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        const balance = Math.max(0, Number(c.totalAmount || 0) - paid);
        const daysOutstanding = c.applicationDate ? daysBetween(c.applicationDate, todayISO()) : 0;
        return { ...c, balance, daysOutstanding };
      })
      .filter((c) => c.balance > 0)
      .sort((a, b) => b.daysOutstanding - a.daysOutstanding || b.balance - a.balance);
  }, [cases]);
  const outstandingByPatientForHospitalGrouping = useMemo(() => {
    return cases
      .map((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        const balance = Math.max(0, Number(c.totalAmount || 0) - paid);
        const daysOutstanding = c.applicationDate ? daysBetween(c.applicationDate, todayISO()) : 0;
        return { ...c, balance, daysOutstanding };
      })
      .filter((c) => c.balance > 0)
      .sort((a, b) => b.daysOutstanding - a.daysOutstanding || b.balance - a.balance);
  }, [cases]);''')

apply("Hospital grouping uses unfiltered source",
'''  const outstandingByHospital = useMemo(() => {
    const tally = {};
    outstandingByPatient
      .filter((c) => c.billTo === "Hospital")
      .forEach((c) => {''',
'''  const outstandingByHospital = useMemo(() => {
    const tally = {};
    outstandingByPatientForHospitalGrouping
      .filter((c) => c.billTo === "Hospital")
      .forEach((c) => {''')

apply("Dependency array update",
'''  }, [outstandingByPatient]);''',
'''  }, [outstandingByPatientForHospitalGrouping]);''')

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
