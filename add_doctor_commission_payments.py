edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("New state",
'''  const [supplierLedger, setSupplierLedger] = useState([]);''',
'''  const [supplierLedger, setSupplierLedger] = useState([]);
  const [doctorCommissionPayments, setDoctorCommissionPayments] = useState([]);''')

apply("Load key",
'''        loadKey(bkey(businessId, "wca-supplier-ledger"), []),''',
'''        loadKey(bkey(businessId, "wca-supplier-ledger"), []),
        loadKey(bkey(businessId, "wca-doctor-commission-payments"), []),''')

apply("Destructure var",
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, acctPin, chals, docsList, topics] = await Promise.all([''',
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, dcPayments, acctPin, chals, docsList, topics] = await Promise.all([''')

apply("setDoctorCommissionPayments",
'''      setSupplierLedger(Array.isArray(splLedger) ? splLedger : []);''',
'''      setSupplierLedger(Array.isArray(splLedger) ? splLedger : []);
      setDoctorCommissionPayments(Array.isArray(dcPayments) ? dcPayments : []);''')

apply("Save effect",
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-supplier-ledger"), supplierLedger); }, [supplierLedger, loaded, businessId]);''',
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-supplier-ledger"), supplierLedger); }, [supplierLedger, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-doctor-commission-payments"), doctorCommissionPayments); }, [doctorCommissionPayments, loaded, businessId]);''')

apply("Add/delete functions",
'''  const addSupplierLedgerEntry = (entry) => setSupplierLedger((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteSupplierLedgerEntry = (id) => setSupplierLedger((prev) => prev.filter((e) => e.id !== id));''',
'''  const addSupplierLedgerEntry = (entry) => setSupplierLedger((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteSupplierLedgerEntry = (id) => setSupplierLedger((prev) => prev.filter((e) => e.id !== id));
  const addDoctorCommissionPayment = (entry) => setDoctorCommissionPayments((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteDoctorCommissionPayment = (id) => setDoctorCommissionPayments((prev) => prev.filter((e) => e.id !== id));''')

apply("OwnerShell call props",
'''          supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}''',
'''          supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}
          doctorCommissionPayments={doctorCommissionPayments} addDoctorCommissionPayment={addDoctorCommissionPayment} deleteDoctorCommissionPayment={deleteDoctorCommissionPayment}''')

apply("OwnerShell fn signature",
'''expenses, addExpense, deleteExpense, supplierLedger, addSupplierLedgerEntry, deleteSupplierLedgerEntry, ownerLogins,''',
'''expenses, addExpense, deleteExpense, supplierLedger, addSupplierLedgerEntry, deleteSupplierLedgerEntry, doctorCommissionPayments, addDoctorCommissionPayment, deleteDoctorCommissionPayment, ownerLogins,''')

apply("ReportsTab call props",
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} machines={machines} addPayment={addPayment} />}''',
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} doctorCommissionPayments={doctorCommissionPayments} addDoctorCommissionPayment={addDoctorCommissionPayment} deleteDoctorCommissionPayment={deleteDoctorCommissionPayment} machines={machines} addPayment={addPayment} />}''')

apply("ReportsTab fn signature",
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, machines, addPayment, readOnly = false }) {''',
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, doctorCommissionPayments = [], addDoctorCommissionPayment, deleteDoctorCommissionPayment, machines, addPayment, readOnly = false }) {''')

apply("Add doctorCommissionLedger useMemo + filter state",
'''  const doctorCommissionTotal = useMemo(() => doctorCommissionStats.reduce((s, d) => s + d.total, 0), [doctorCommissionStats]);''',
'''  const doctorCommissionTotal = useMemo(() => doctorCommissionStats.reduce((s, d) => s + d.total, 0), [doctorCommissionStats]);

  const [commissionTab, setCommissionTab] = useState("all");
  const [commissionForm, setCommissionForm] = useState({ doctor: "", amount: "", note: "" });
  const [openCommissionDoctor, setOpenCommissionDoctor] = useState(null);
  const doctorCommissionLedger = useMemo(() => {
    const paidByDoctor = {};
    (doctorCommissionPayments || []).forEach((p) => {
      const doctor = (p.doctor || "Unknown").trim();
      paidByDoctor[doctor] = (paidByDoctor[doctor] || 0) + Number(p.amount || 0);
    });
    return doctorCommissionStats.map((d) => {
      const paid = paidByDoctor[d.doctor] || 0;
      return { ...d, paid, remaining: Math.max(0, d.total - paid) };
    }).sort((a, b) => b.remaining - a.remaining);
  },
cat > add_doctor_commission_payments.py << 'PYEOF'
edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("New state",
'''  const [supplierLedger, setSupplierLedger] = useState([]);''',
'''  const [supplierLedger, setSupplierLedger] = useState([]);
  const [doctorCommissionPayments, setDoctorCommissionPayments] = useState([]);''')

apply("Load key",
'''        loadKey(bkey(businessId, "wca-supplier-ledger"), []),''',
'''        loadKey(bkey(businessId, "wca-supplier-ledger"), []),
        loadKey(bkey(businessId, "wca-doctor-commission-payments"), []),''')

apply("Destructure var",
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, acctPin, chals, docsList, topics] = await Promise.all([''',
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, dcPayments, acctPin, chals, docsList, topics] = await Promise.all([''')

apply("setDoctorCommissionPayments",
'''      setSupplierLedger(Array.isArray(splLedger) ? splLedger : []);''',
'''      setSupplierLedger(Array.isArray(splLedger) ? splLedger : []);
      setDoctorCommissionPayments(Array.isArray(dcPayments) ? dcPayments : []);''')

apply("Save effect",
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-supplier-ledger"), supplierLedger); }, [supplierLedger, loaded, businessId]);''',
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-supplier-ledger"), supplierLedger); }, [supplierLedger, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-doctor-commission-payments"), doctorCommissionPayments); }, [doctorCommissionPayments, loaded, businessId]);''')

apply("Add/delete functions",
'''  const addSupplierLedgerEntry = (entry) => setSupplierLedger((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteSupplierLedgerEntry = (id) => setSupplierLedger((prev) => prev.filter((e) => e.id !== id));''',
'''  const addSupplierLedgerEntry = (entry) => setSupplierLedger((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteSupplierLedgerEntry = (id) => setSupplierLedger((prev) => prev.filter((e) => e.id !== id));
  const addDoctorCommissionPayment = (entry) => setDoctorCommissionPayments((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteDoctorCommissionPayment = (id) => setDoctorCommissionPayments((prev) => prev.filter((e) => e.id !== id));''')

apply("OwnerShell call props",
'''          supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}''',
'''          supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}
          doctorCommissionPayments={doctorCommissionPayments} addDoctorCommissionPayment={addDoctorCommissionPayment} deleteDoctorCommissionPayment={deleteDoctorCommissionPayment}''')

apply("OwnerShell fn signature",
'''expenses, addExpense, deleteExpense, supplierLedger, addSupplierLedgerEntry, deleteSupplierLedgerEntry, ownerLogins,''',
'''expenses, addExpense, deleteExpense, supplierLedger, addSupplierLedgerEntry, deleteSupplierLedgerEntry, doctorCommissionPayments, addDoctorCommissionPayment, deleteDoctorCommissionPayment, ownerLogins,''')

apply("ReportsTab call props",
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} machines={machines} addPayment={addPayment} />}''',
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} doctorCommissionPayments={doctorCommissionPayments} addDoctorCommissionPayment={addDoctorCommissionPayment} deleteDoctorCommissionPayment={deleteDoctorCommissionPayment} machines={machines} addPayment={addPayment} />}''')

apply("ReportsTab fn signature",
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, machines, addPayment, readOnly = false }) {''',
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, doctorCommissionPayments = [], addDoctorCommissionPayment, deleteDoctorCommissionPayment, machines, addPayment, readOnly = false }) {''')

apply("Add doctorCommissionLedger useMemo + filter state",
'''  const doctorCommissionTotal = useMemo(() => doctorCommissionStats.reduce((s, d) => s + d.total, 0), [doctorCommissionStats]);''',
'''  const doctorCommissionTotal = useMemo(() => doctorCommissionStats.reduce((s, d) => s + d.total, 0), [doctorCommissionStats]);

  const [commissionTab, setCommissionTab] = useState("all");
  const [commissionForm, setCommissionForm] = useState({ doctor: "", amount: "", note: "" });
  const [openCommissionDoctor, setOpenCommissionDoctor] = useState(null);
  const doctorCommissionLedger = useMemo(() => {
    const paidByDoctor = {};
    (doctorCommissionPayments || []).forEach((p) => {
      const doctor = (p.doctor || "Unknown").trim();
      paidByDoctor[doctor] = (paidByDoctor[doctor] || 0) + Number(p.amount || 0);
    });
    return doctorCommissionStats.map((d) => {
      const paid = paidByDoctor[d.doctor] || 0;
      return { ...d, paid, remaining: Math.max(0, d.total - paid) };
    }).sort((a, b) => b.remaining - a.remaining);
  }, [doctorCommissionStats, doctorCommissionPayments]);
  const doctorCommissionRemainingTotal = useMemo(() => doctorCommissionLedger.reduce((s, d) => s + d.remaining, 0), [doctorCommissionLedger]);
  const doctorCommissionFiltered = useMemo(() => {
    if (commissionTab === "unpaid") return doctorCommissionLedger.filter((d) => d.remaining > 0);
    if (commissionTab === "paid") return doctorCommissionLedger.filter((d) => d.remaining <= 0);
    return doctorCommissionLedger;
  }, [doctorCommissionLedger, commissionTab]);''')

apply("Insert Paid/Unpaid UI into Doctor Commission section",
'''      <CollapsibleSection title="Doctor Commission"
        right={doctorCommissionTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#D98D2B" }}>{fmtMoney(doctorCommissionTotal)}</span> : null}>
        {doctorCommissionStats.length === 0 ? <EmptyState text="No commission entered on any case yet. Add it in the case form when applicable." /> : (
          <>
            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={Math.max(160, doctorCommissionStats.length * 34)}>
                <BarChart data={doctorCommissionStats} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid stroke="#EEF1EC" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#8A9A96" }} />
                  <YAxis type="category" dataKey="doctor" width={90} tick={{ fontSize: 11, fill: "#182322" }} />
                  <Tooltip formatter={(v) => fmtMoney(v)} contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                  <Bar dataKey="total" name="Commission" fill="#D98D2B" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.list}>
              {doctorCommissionMonthly.map((d) => (
                <DoctorCommissionCard key={d.doctor} d={d} businessName={businessName} />
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>''',
'''      <CollapsibleSection title="Doctor Commission"
        right={doctorCommissionRemainingTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(doctorCommissionRemainingTotal)} due</span> : null}>
        {doctorCommissionStats.length === 0 ? <EmptyState text="No commission entered on any case yet. Add it in the case form when applicable." /> : (
          <>
            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={Math.max(160, doctorCommissionStats.length * 34)}>
                <BarChart data={doctorCommissionStats} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid stroke="#EEF1EC" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#8A9A96" }} />
                  <YAxis type="category" dataKey="doctor" width={90} tick={{ fontSize: 11, fill: "#182322" }} />
                  <Tooltip formatter={(v) => fmtMoney(v)} contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                  <Bar dataKey="total" name="Commission" fill="#D98D2B" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.list}>
              {doctorCommissionMonthly.map((d) => (
                <DoctorCommissionCard key={d.doctor} d={d} businessName={businessName} />
              ))}
            </div>

            <div style={{ ...styles.detailLabel, marginTop: 16, marginBottom: 6 }}>Commission Payments</div>
            <div style={styles.filterRow}>
              {[["all", "All"], ["unpaid", "Unpaid"], ["paid", "Paid Up"]].map(([key, label]) => (
                <button key={key} onClick={() => setCommissionTab(key)} style={{ ...styles.filterChip, ...(commissionTab === key ? styles.filterChipActive : {}) }}>{label}</button>
              ))}
            </div>
            {!readOnly && (
              <div style={styles.formGrid}>
                <div style={styles.addPaymentRow}>
                  <input type="text" placeholder="Doctor name" style={{ ...styles.smallInput, flex: 1 }} value={commissionForm.doctor} onChange={(e) => setCommissionForm((f) => ({ ...f, doctor: e.target.value }))} />
                  <input type="number" placeholder="Amount ₹" style={styles.smallInput} value={commissionForm.amount} onChange={(e) => setCommissionForm((f) => ({ ...f, amount: e.target.value }))} />
                </div>
                <div style={styles.addPaymentRow}>
                  <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={commissionForm.note} onChange={(e) => setCommissionForm((f) => ({ ...f, note: e.target.value }))} />
                  <button style={styles.smallBtn} onClick={() => {
                    const amt = Number(commissionForm.amount);
                    if (!commissionForm.doctor.trim() || !amt || amt <= 0) return;
                    addDoctorCommissionPayment({ doctor: commissionForm.doctor.trim(), amount: amt, note: commissionForm.note.trim() });
                    setCommissionForm({ doctor: "", amount: "", note: "" });
                  }}>Log Payment</button>
                </div>
              </div>
            )}
            <div style={styles.card}>
              {doctorCommissionFiltered.length === 0 ? <EmptyState text="No doctors in this view." /> : doctorCommissionFiltered.map((d) => (
                <div key={d.doctor}>
                  <div style={styles.dresserLine} onClick={() => setOpenCommissionDoctor(openCommissionDoctor === d.doctor ? null : d.doctor)}>
                    <span style={{ flex: 1, fontWeight: 600 }}>{d.doctor}</span>
                    <span style={styles.mutedSmall}>Owed {fmtMoney(d.total)} · Paid {fmtMoney(d.paid)}</span>
                    <span style={{ fontWeight: 700, color: d.remaining > 0 ? "#E1483C" : "#128577" }}>{d.remaining > 0 ? fmtMoney(d.remaining) : "Paid up"}</span>
                  </div>
                  {openCommissionDoctor === d.doctor && (doctorCommissionPayments || []).filter((p) => (p.doctor || "").trim() === d.doctor).sort((a, b) => new Date(b.date) - new Date(a.date)).map((p) => (
                    <div key={p.id} style={{ ...styles.paymentLine, paddingLeft: 24 }}>
                      <span>{fmtDate(p.date)}</span>
                      <span style={{ color: "#128577" }}>Paid {fmtMoney(p.amount)}</span>
                      <span style={styles.mutedSmall}>{p.note || ""}</span>
                      {!readOnly && <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => { if (window.confirm("Delete this payment entry?")) deleteDoctorCommissionPayment(p.id); }}>✕</button>}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </>
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
