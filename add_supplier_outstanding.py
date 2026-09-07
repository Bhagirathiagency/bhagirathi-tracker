edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("receiveStock fn",
'''  const receiveStock = (productId, qty, company, receivedBy) => {
    setProducts((prev) => prev.map((p) => p.id === productId ? {
      ...p,
      available: (p.available || 0) + qty,
      receipts: [...(p.receipts || []), { id: uid(), date: todayISO(), time: new Date().toLocaleTimeString("en-IN"), qty, company: company || "Unspecified", receivedBy: receivedBy || "Owner" }],
    } : p));
  };''',
'''  const receiveStock = (productId, qty, company, receivedBy, billAmount) => {
    setProducts((prev) => prev.map((p) => p.id === productId ? {
      ...p,
      available: (p.available || 0) + qty,
      receipts: [...(p.receipts || []), { id: uid(), date: todayISO(), time: new Date().toLocaleTimeString("en-IN"), qty, company: company || "Unspecified", receivedBy: receivedBy || "Owner", billAmount: Number(billAmount) || 0 }],
    } : p));
  };
  const addSupplierLedgerEntry = (entry) => setSupplierLedger((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);
  const deleteSupplierLedgerEntry = (id) => setSupplierLedger((prev) => prev.filter((e) => e.id !== id));''')

apply("supplierLedger state",
'''  const [expenses, setExpenses] = useState([]);''',
'''  const [expenses, setExpenses] = useState([]);
  const [supplierLedger, setSupplierLedger] = useState([]);''')

apply("load supplierLedger key",
'''        loadKey(bkey(businessId, "wca-expenses"), []),''',
'''        loadKey(bkey(businessId, "wca-expenses"), []),
        loadKey(bkey(businessId, "wca-supplier-ledger"), []),''')

apply("destructure supplierLedger var",
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, acctPin, chals, docsList, topics] = await Promise.all([''',
'''      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock, exps, splLedger, acctPin, chals, docsList, topics] = await Promise.all([''')

apply("setExpenses/setSupplierLedger",
'''      setExpenses(Array.isArray(exps) ? exps : []);''',
'''      setExpenses(Array.isArray(exps) ? exps : []);
      setSupplierLedger(Array.isArray(splLedger) ? splLedger : []);''')

apply("save supplierLedger effect",
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-expenses"), expenses); }, [expenses, loaded, businessId]);''',
'''  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-expenses"), expenses); }, [expenses, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-supplier-ledger"), supplierLedger); }, [supplierLedger, loaded, businessId]);''')

apply("OwnerShell call props",
'''          expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense}''',
'''          expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense}
          supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry}''')

apply("OwnerShell fn signature",
'''expenses, addExpense, deleteExpense, ownerLogins, businessId, business, businesses, onSwitchBusiness, pin, onChangePin, accountantPin, onChangeAccountantPin, refreshData, refreshing, onLogout }) {''',
'''expenses, addExpense, deleteExpense, supplierLedger, addSupplierLedgerEntry, deleteSupplierLedgerEntry, ownerLogins, businessId, business, businesses, onSwitchBusiness, pin, onChangePin, accountantPin, onChangeAccountantPin, refreshData, refreshing, onLogout }) {''')

apply("ReportsTab call props",
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} machines={machines} addPayment={addPayment} />}''',
'''expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} machines={machines} addPayment={addPayment} />}''')

apply("ReportsTab fn signature",
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, machines, addPayment, readOnly = false }) {''',
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, machines, addPayment, readOnly = false }) {''')

apply("doReceive billAmount",
'''  const doReceive = (id) => {
    const f = receiveForm[id] || {};
    const qty = Number(f.qty);
    if (!qty || qty <= 0) return;
    receiveStock(id, qty, f.company, actorName);
    setReceiveForm((prev) => ({ ...prev, [id]: { qty: "", company: "" } }));
  };''',
'''  const doReceive = (id) => {
    const f = receiveForm[id] || {};
    const qty = Number(f.qty);
    if (!qty || qty <= 0) return;
    receiveStock(id, qty, f.company, actorName, f.billAmount);
    setReceiveForm((prev) => ({ ...prev, [id]: { qty: "", company: "", billAmount: "" } }));
  };''')

apply("Bill Amount input field",
'''                          <input type="number" placeholder="Qty received" value={(receiveForm[p.id] || {}).qty || ""} onChange={(e) => setField(p.id, "qty", e.target.value)} style={styles.smallInput} />
                          <input type="text" placeholder="Company / supplier" value={(receiveForm[p.id] || {}).company || ""} onChange={(e) => setField(p.id, "company", e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                          <button style={styles.smallBtn} onClick={() => doReceive(p.id)}>Receive Stock</button>''',
'''                          <input type="number" placeholder="Qty received" value={(receiveForm[p.id] || {}).qty || ""} onChange={(e) => setField(p.id, "qty", e.target.value)} style={styles.smallInput} />
                          <input type="text" placeholder="Company / supplier" value={(receiveForm[p.id] || {}).company || ""} onChange={(e) => setField(p.id, "company", e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                          <input type="number" placeholder="Bill amount ₹ (optional)" value={(receiveForm[p.id] || {}).billAmount || ""} onChange={(e) => setField(p.id, "billAmount", e.target.value)} style={styles.smallInput} />
                          <button style={styles.smallBtn} onClick={() => doReceive(p.id)}>Receive Stock</button>''')

apply("Add useMemos for supplier ledger + outstanding by source",
'''  const expensesSorted = useMemo(() => [...(expenses || [])].sort((a, b) => new Date(b.date) - new Date(a.date)), [expenses]);''',
'''  const [supplierForm, setSupplierForm] = useState({ supplier: "", type: "bill", amount: "", note: "" });
  const [openSupplier, setOpenSupplier] = useState(null);
  const [showOutstandingDetail, setShowOutstandingDetail] = useState(null);

  const supplierStats = useMemo(() => {
    const tally = {};
    (products || []).forEach((p) => (p.receipts || []).forEach((r) => {
      const amt = Number(r.billAmount || 0);
      if (amt <= 0) return;
      const name = r.company || "Unspecified";
      if (!tally[name]) tally[name] = { supplier: name, billed: 0, paid: 0, entries: [] };
      tally[name].billed += amt;
      tally[name].entries.push({ id: r.id, type: "bill", amount: amt, date: r.date, note: `${r.qty} units — stock receipt` });
    }));
    (supplierLedger || []).forEach((e) => {
      const name = e.supplier || "Unspecified";
      if (!tally[name]) tally[name] = { supplier: name, billed: 0, paid: 0, entries: [] };
      if (e.type === "payment") tally[name].paid += Number(e.amount || 0);
      else tally[name].billed += Number(e.amount || 0);
      tally[name].entries.push({ id: e.id, type: e.type, amount: Number(e.amount || 0), date: e.date, note: e.note, manual: true });
    });
    return Object.values(tally).map((s) => ({
      ...s,
      outstanding: s.billed - s.paid,
      entries: s.entries.sort((a, b) => new Date(b.date) - new Date(a.date)),
    })).sort((a, b) => b.outstanding - a.outstanding);
  }, [products, supplierLedger]);
  const supplierOutstandingTotal = useMemo(() => supplierStats.reduce((s, x) => s + Math.max(0, x.outstanding), 0), [supplierStats]);

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
    return groups;
  }, [cases]);

  const expensesSorted = useMemo(() => [...(expenses || [])].sort((a, b) => new Date(b.date) - new Date(a.date)), [expenses]);''')

apply("Outstanding card + breakdown",
'''      <SectionTitle>Revenue</SectionTitle>
      <div style={styles.cardGrid}>
        <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(totalBilled)}</div><div style={styles.statLabel}>Total Billed</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#D9720A" }}>{fmtMoney(totalCollected)}</div><div style={styles.statLabel}>Total Collected</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(outstandingTotal)}</div><div style={styles.statLabel}>Outstanding</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#3B5BA5" }}>{fmtMoney(totalProfit)}</div><div style={styles.statLabel}>Est. Profit</div></div>
      </div>''',
'''      <SectionTitle>Revenue</SectionTitle>
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
      )}''')

apply("Insert Supplier Payments Due section",
'''      <CollapsibleSection title="Stock Overview">''',
'''      <CollapsibleSection title="Supplier Payments Due" right={supplierOutstandingTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(supplierOutstandingTotal)}</span> : null}>
        {!readOnly && (
          <div style={styles.formGrid}>
            <div style={styles.addPaymentRow}>
              <input type="text" placeholder="Supplier / distributor name" style={{ ...styles.smallInput, flex: 1 }} value={supplierForm.supplier} onChange={(e) => setSupplierForm((f) => ({ ...f, supplier: e.target.value }))} />
              <select style={styles.smallInput} value={supplierForm.type} onChange={(e) => setSupplierForm((f) => ({ ...f, type: e.target.value }))}>
                <option value="bill">New Bill (owed)</option>
                <option value="payment">Payment Made</option>
              </select>
            </div>
            <div style={styles.addPaymentRow}>
              <input type="number" placeholder="Amount ₹" style={styles.smallInput} value={supplierForm.amount} onChange={(e) => setSupplierForm((f) => ({ ...f, amount: e.target.value }))} />
              <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={supplierForm.note} onChange={(e) => setSupplierForm((f) => ({ ...f, note: e.target.value }))} />
              <button style={styles.smallBtn} onClick={() => {
                const amt = Number(supplierForm.amount);
                if (!supplierForm.supplier.trim() || !amt || amt <= 0) return;
                addSupplierLedgerEntry({ supplier: supplierForm.supplier.trim(), type: supplierForm.type, amount: amt, note: supplierForm.note.trim() });
                setSupplierForm({ supplier: "", type: "bill", amount: "", note: "" });
              }}>Add</button>
            </div>
          </div>
        )}
        {supplierStats.length === 0 ? <EmptyState text="No supplier bills yet. Add a bill amount when receiving stock, or log one manually above." /> : (
          <div style={styles.card}>
            {supplierStats.map((s) => (
              <div key={s.supplier}>
                <div style={styles.dresserLine} onClick={() => setOpenSupplier(openSupplier === s.supplier ? null : s.supplier)}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{s.supplier}</span>
                  <span style={styles.mutedSmall}>Billed {fmtMoney(s.billed)} · Paid {fmtMoney(s.paid)}</span>
                  <span style={{ fontWeight: 700, color: s.outstanding > 0 ? "#E1483C" : "#128577" }}>{fmtMoney(Math.max(0, s.outstanding))}</span>
                </div>
                {openSupplier === s.supplier && s.entries.map((e) => (
                  <div key={e.id} style={{ ...styles.paymentLine, paddingLeft: 24 }}>
                    <span>{fmtDate(e.date)}</span>
                    <span style={{ color: e.type === "payment" ? "#128577" : "#E1483C" }}>{e.type === "payment" ? "Paid" : "Bill"} {fmtMoney(e.amount)}</span>
                    <span style={styles.mutedSmall}>{e.note || ""}</span>
                    {!readOnly && e.manual && <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => { if (window.confirm("Delete this entry?")) deleteSupplierLedgerEntry(e.id); }}>✕</button>}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Stock Overview">''')

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
