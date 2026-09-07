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
        <div style={styles.emptyState2}>Old dues from before you started using this app \u2014 add them here so they're included in your Outstanding totals and the pie chart above.</div>
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
              <input type="number" placeholder="Amount owed \u20b9" style={styles.smallInput} value={prevOutForm.amount} onChange={(e) => setPrevOutForm((f) => ({ ...f, amount: e.target.value }))} />
              <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={prevOutForm.note} onChange={(e) => setPrevOutForm((f) => ({ ...f, note: e.target.value }))} />
              <button style={styles.smallBtn} onClick={() => {
                const amt = Number(prevOutForm.amount);
                if (!prevOutForm.name.trim() || !amt || amt <= 0) return;
                addPreviousOutstanding({ name: prevOutForm.name.trim(), billTo: prevOutForm.billTo, amount: amt, note: prevOutForm.note.trim() });
                setPrevOutForm({ name: "", billTo: "Patient", amount: "", note: "" });
              }}>Add</button>
            </div>
          </div>
        )}
        {previousOutstandingWithRemaining.length === 0 ? <EmptyState text="No previous outstanding added yet." /> : (
          <div style={styles.card}>
            {previousOutstandingWithRemaining.map((e) => (
              <div key={e.id}>
                <div style={styles.dresserLine} onClick={() => setOpenPrevOut(openPrevOut === e.id ? null : e.id)}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{e.name} ({e.billTo})</span>
                  <span style={styles.mutedSmall}>Owed {fmtMoney(e.amount)} \u00b7 Paid {fmtMoney(e.paid)}</span>
                  <span style={{ fontWeight: 700, color: e.remaining > 0 ? "#E1483C" : "#128577" }}>{e.remaining > 0 ? fmtMoney(e.remaining) : "Cleared"}</span>
                </div>
                {openPrevOut === e.id && (
                  <div style={{ padding: "0 14px 14px" }}>
                    {(e.payments || []).map((p) => (
                      <div key={p.id} style={styles.paymentLine}><span>{fmtDate(p.date)}</span><span>{fmtMoney(p.amount)}</span></div>
                    ))}
                    {!readOnly && e.remaining > 0 && (
                      <div style={styles.addPaymentRow}>
                        <input type="number" placeholder="Payment amount" style={styles.smallInput} value={(prevOutPayForm[e.id] || "")} onChange={(ev) => setPrevOutPayForm((f) => ({ ...f, [e.id]: ev.target.value }))} />
                        <button style={styles.smallBtn} onClick={() => {
                          const amt = Number(prevOutPayForm[e.id]);
                          if (!amt || amt <= 0) return;
                          addPreviousOutstandingPayment(e.id, { amount: amt });
                          setPrevOutPayForm((f) => ({ ...f, [e.id]: "" }));
                        }}>Log Payment</button>
                      </div>
                    )}
                    {!readOnly && <button style={{ ...styles.linkBtn, color: "#E1483C", marginTop: 8 }} onClick={() => { if (window.confirm("Delete this previous outstanding entry?")) deletePreviousOutstanding(e.id); }}>Delete Entry</button>}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Outstanding Payments by Patient">''', 1)

apply("Pass addPreviousOutstanding to DresserShell call",
'''          doctorCalls={doctorCalls} addDoctorCall={addDoctorCall}
          doctorsList={doctorsList} addDoctorMaster={addDoctorMaster}''',
'''          doctorCalls={doctorCalls} addDoctorCall={addDoctorCall}
          doctorsList={doctorsList} addDoctorMaster={addDoctorMaster} addPreviousOutstanding={addPreviousOutstanding}''', 1)

apply("DresserShell fn signature",
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem, addPayment, capturePhoto, updateDresserLocation, quotations, saveQuotation, deleteQuotation, setQuotationStatus, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster,''',
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem, addPayment, capturePhoto, updateDresserLocation, quotations, saveQuotation, deleteQuotation, setQuotationStatus, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster, addPreviousOutstanding,''', 1)

apply("Add Previous Outstanding section for Devashish",
'''        {canManageStock && (
          <CollapsibleSection title="Stock">
            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} />
          </CollapsibleSection>
        )}''',
'''        {name.trim().toLowerCase() === "devashish" && (
          <CollapsibleSection title="Add Previous Outstanding">
            <PreviousOutstandingQuickAdd addPreviousOutstanding={addPreviousOutstanding} />
          </CollapsibleSection>
        )}
        {canManageStock && (
          <CollapsibleSection title="Stock">
            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} />
          </CollapsibleSection>
        )}''', 1)

apply("Insert PreviousOutstandingQuickAdd component",
'''function DoctorCallTab({ name, products, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster, discussionTopics, addDiscussionTopic, removeDiscussionTopic }) {''',
'''function PreviousOutstandingQuickAdd({ addPreviousOutstanding }) {
  const [form, setForm] = useState({ name: "", billTo: "Patient", amount: "", note: "" });
  const [confirm, setConfirm] = useState(false);
  const submit = () => {
    const amt = Number(form.amount);
    if (!form.name.trim() || !amt || amt <= 0) return;
    addPreviousOutstanding({ name: form.name.trim(), billTo: form.billTo, amount: amt, note: form.note.trim() });
    setForm({ name: "", billTo: "Patient", amount: "", note: "" });
    setConfirm(true);
    setTimeout(() => setConfirm(false), 2000);
  };
  return (
    <div>
      <div style={styles.emptyState2}>Add old dues from before the app was used \u2014 this goes to the Owner's Reports for tracking.</div>
      <div style={styles.formGrid}>
        <div style={styles.addPaymentRow}>
          <input type="text" placeholder="Patient / Hospital name" style={{ ...styles.smallInput, flex: 1 }} value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
          <select style={styles.smallInput} value={form.billTo} onChange={(e) => setForm((f) => ({ ...f, billTo: e.target.value }))}>
            <option value="Patient">Patient</option>
            <option value="Hospital">Hospital</option>
          </select>
        </div>
        <div style={styles.addPaymentRow}>
          <input type="number" placeholder="Amount owed \u20b9" style={styles.smallInput} value={form.amount} onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))} />
          <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={form.note} onChange={(e) => setForm((f) => ({ ...f, note: e.target.value }))} />
        </div>
        <button style={styles.primaryBtn} onClick={submit}>Add Previous Outstanding</button>
        {confirm && <div style={{ ...styles.mutedSmall, color: "#128577" }}>\u2713 Added</div>}
      </div>
    </div>
  );
}

function DoctorCallTab({ name, products, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster, discussionTopics, addDiscussionTopic, removeDiscussionTopic }) {''', 1)

with open('src/App.jsx', 'r') as f:
    content = f.read()

all_ok = True
for label, old, new, count in edits:
    c = content.count(old)
    print(label, "matches:", c)
    if count and c != count:
        all_ok = False
    elif not count and c == 0:
        all_ok = False
    else:
        content = content.replace(old, new, count if count else c)

if all_ok:
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("ALL_APPLIED_OK")
else:
    print("SOME_MISMATCHES_FILE_NOT_CHANGED")
