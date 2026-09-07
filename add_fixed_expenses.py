edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("New fixedExpenses state",
'''  const [supplierLedger, setSupplierLedger] = useState([]);''',
'''  const [supplierLedger, setSupplierLedger] = useState([]);
  const [fixedExpenses, setFixedExpenses] = useState([]);''')

apply("Load key",
'''        loadKey(bkey(businessId, "wca-supplier-ledger"), []),''',
'''        loadKey(bkey(businessId, "wca-supplier-ledger"), []),
        loadKey(bkey(businessId, "wca-fixed-expenses"), []),''')

apply("Destructure var",
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, acctPin, chals, docsList, topics] = await Promise.all([''',
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, fixedExps, acctPin, chals, docsList, topics] = await Promise.all([''')

apply("setFixedExpenses",
'''      setSupplierLedger(Array.isArray(splLedger) ? splLedger : []);''',
'''      setSupplierLedger(Array.isArray(splLedger) ? splLedger : []);
      setFixedExpenses(Array.isArray(fixedExps) ? fixedExps : []);''')

apply("Save effect",
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-supplier-ledger"), supplierLedger); }, [supplierLedger, loaded, businessId]);''',
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-supplier-ledger"), supplierLedger); }, [supplierLedger, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-fixed-expenses"), fixedExpenses); }, [fixedExpenses, loaded, businessId]);''')

apply("Add/delete fixedExpense functions",
'''  const addSupplierLedgerEntry = (entry) => setSupplierLedger((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteSupplierLedgerEntry = (id) => setSupplierLedger((prev) => prev.filter((e) => e.id !== id));''',
'''  const addSupplierLedgerEntry = (entry) => setSupplierLedger((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteSupplierLedgerEntry = (id) => setSupplierLedger((prev) => prev.filter((e) => e.id !== id));
  const addFixedExpense = (entry) => setFixedExpenses((prev) => [...prev, { id: uid(), ...entry }]);
  const deleteFixedExpense = (id) => setFixedExpenses((prev) => prev.filter((e) => e.id !== id));''')

apply("OwnerShell call props",
'''          supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}''',
'''          supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}
          fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense}''')

apply("OwnerShell fn signature",
'''expenses, addExpense, deleteExpense, supplierLedger, addSupplierLedgerEntry, deleteSupplierLedgerEntry, ownerLogins,''',
'''expenses, addExpense, deleteExpense, supplierLedger, addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses, addFixedExpense, deleteFixedExpense, ownerLogins,''')

apply("ReportsTab call props",
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}''',
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense}''')

apply("ReportsTab fn signature",
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry,''',
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses = [], addFixedExpense, deleteFixedExpense,''')

apply("pnlRows auto-calc fixed expenses",
'''  const pnlRows = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      if (!c.applicationDate) return;
      const key = pnlPeriodKey(c.applicationDate, pnlGranularity);
      if (!tally[key]) tally[key] = { key, revenue: 0, rental: 0, cost: 0, commission: 0, opex: 0, cases: 0 };
      const names = getCaseProducts(c);
      const cost = names.reduce((s, name) => {
        const prod = products.find((p) => p.name === name);
        return s + (prod ? Number(prod.costPrice || 0) : 0);
      }, 0);
      tally[key].revenue += Number(c.totalAmount || 0);
      tally[key].rental += Number(c.machineRentalAmount || 0);
      tally[key].cost += cost;
      tally[key].commission += Number(c.doctorCommission || 0);
      tally[key].cases += 1;
    });
    (expenses || []).forEach((e) => {
      if (!e.date) return;
      const key = pnlPeriodKey(e.date, pnlGranularity);
      if (!tally[key]) tally[key] = { key, revenue: 0, rental: 0, cost: 0, commission: 0, opex: 0, cases: 0 };
      tally[key].opex += Number(e.amount || 0);
    });
    return Object.values(tally)
      .map((r) => ({ ...r, profit: r.revenue + r.rental - r.cost - r.commission - (r.opex || 0) }))
      .sort((a, b) => (a.key < b.key ? 1 : -1));
  }, [cases, products, pnlGranularity, expenses]);''',
'''  const fixedExpensesMonthlyTotal = useMemo(() => (fixedExpenses || []).reduce((s, e) => s + Number(e.amount || 0), 0), [fixedExpenses]);
  const pnlRows = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      if (!c.applicationDate) return;
      const key = pnlPeriodKey(c.applicationDate, pnlGranularity);
      if (!tally[key]) tally[key] = { key, revenue: 0, rental: 0, cost: 0, commission: 0, opex: 0, cases: 0 };
      const names = getCaseProducts(c);
      const cost = names.reduce((s, name) => {
        const prod = products.find((p) => p.name === name);
        return s + (prod ? Number(prod.costPrice || 0) : 0);
      }, 0);
      tally[key].revenue += Number(c.totalAmount || 0);
      tally[key].rental += Number(c.machineRentalAmount || 0);
      tally[key].cost += cost;
      tally[key].commission += Number(c.doctorCommission || 0);
      tally[key].cases += 1;
    });
    (expenses || []).forEach((e) => {
      if (!e.date) return;
      const key = pnlPeriodKey(e.date, pnlGranularity);
      if (!tally[key]) tally[key] = { key, revenue: 0, rental: 0, cost: 0, commission: 0, opex: 0, cases: 0 };
      tally[key].opex += Number(e.amount || 0);
    });
    if (fixedExpensesMonthlyTotal > 0 && (pnlGranularity === "monthly" || pnlGranularity === "yearly")) {
      const now = new Date();
      const curYear = now.getFullYear();
      const curMonthKey = `${curYear}-${String(now.getMonth() + 1).padStart(2, "0")}`;
      if (pnlGranularity === "monthly") {
        if (!tally[curMonthKey]) tally[curMonthKey] = { key: curMonthKey, revenue: 0, rental: 0, cost: 0, commission: 0, opex: 0, cases: 0 };
        Object.values(tally).forEach((r) => { r.opex += fixedExpensesMonthlyTotal; });
      } else {
        const curYearKey = `${curYear}`;
        if (!tally[curYearKey]) tally[curYearKey] = { key: curYearKey, revenue: 0, rental: 0, cost: 0, commission: 0, opex: 0, cases: 0 };
        Object.values(tally).forEach((r) => {
          const yr = Number(r.key);
          const monthsElapsed = yr < curYear ? 12 : yr === curYear ? (now.getMonth() + 1) : 0;
          r.opex += fixedExpensesMonthlyTotal * monthsElapsed;
        });
      }
    }
    return Object.values(tally)
      .map((r) => ({ ...r, profit: r.revenue + r.rental - r.cost - r.commission - (r.opex || 0) }))
      .sort((a, b) => (a.key < b.key ? 1 : -1));
  }, [cases, products, pnlGranularity, expenses, fixedExpensesMonthlyTotal]);''')

apply("Add fixed expense form state",
'''  const [supplierForm, setSupplierForm] = useState({ supplier: "", type: "bill", amount: "", note: "" });''',
'''  const [fixedExpForm, setFixedExpForm] = useState({ category: "Salary", amount: "", note: "" });
  const [supplierForm, setSupplierForm] = useState({ supplier: "", type: "bill", amount: "", note: "" });''')

apply("Insert Fixed Monthly Expenses UI",
'''      <CollapsibleSection title="Expenses" right={expensesTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(expensesTotal)}</span> : null}>''',
'''      <CollapsibleSection title="Fixed Monthly Expenses" right={fixedExpensesMonthlyTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(fixedExpensesMonthlyTotal)}/mo</span> : null}>
        <div style={styles.emptyState2}>Recurring costs like Salary or Office Rent — enter once, and they're auto-added to Monthly and Yearly Profit & Loss every period, without re-entering each month.</div>
        {!readOnly && (
          <div style={styles.formGrid}>
            <div style={styles.addPaymentRow}>
              <select style={{ ...styles.smallInput, flex: 1 }} value={fixedExpForm.category} onChange={(e) => setFixedExpForm((f) => ({ ...f, category: e.target.value }))}>
                {["Salary", "Office Rent", "Utilities", "Internet/Phone", "Other"].map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <input type="number" placeholder="Amount ₹/month" style={{ ...styles.smallInput, width: 120 }} value={fixedExpForm.amount} onChange={(e) => setFixedExpForm((f) => ({ ...f, amount: e.target.value }))} />
            </div>
            <div style={styles.addPaymentRow}>
              <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={fixedExpForm.note} onChange={(e) => setFixedExpForm((f) => ({ ...f, note: e.target.value }))} />
              <button style={styles.smallBtn} onClick={() => {
                const amt = Number(fixedExpForm.amount);
                if (!amt || amt <= 0) return;
                addFixedExpense({ category: fixedExpForm.category, amount: amt, note: fixedExpForm.note.trim() });
                setFixedExpForm({ category: "Salary", amount: "", note: "" });
              }}>Add Fixed Expense</button>
            </div>
          </div>
        )}
        {(fixedExpenses || []).length === 0 ? <EmptyState text="No fixed monthly expenses set up yet." /> : (
          <div style={styles.card}>
            {(fixedExpenses || []).map((e) => (
              <div key={e.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{e.category}{e.note ? ` · ${e.note}` : ""}</span>
                <span style={{ fontWeight: 700 }}>{fmtMoney(e.amount)}/mo</span>
                {!readOnly && <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => { if (window.confirm("Remove this fixed expense?")) deleteFixedExpense(e.id); }}>✕</button>}
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Expenses" right={expensesTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(expensesTotal)}</span> : null}>''')

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
