edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add Expenses nav tab",
'''        {[["dashboard", "Command Center", "overview"], ["cases", "Cases", "cases"], ["challans", "Challans", "stock"], ["quotations", "Quotes", "quotes"], ["machines", "Machines", "machines"], ["stock", "Stock", "stock"], ["dressers", "Dressers", "dressers"], ["doctors", "Doctors", "dressers"], ["reports", "Reports", "reports"], ["combined", "All Business", "overview"]].map(([key, label, icon]) => (''',
'''        {[["dashboard", "Command Center", "overview"], ["cases", "Cases", "cases"], ["challans", "Challans", "stock"], ["quotations", "Quotes", "quotes"], ["machines", "Machines", "machines"], ["stock", "Stock", "stock"], ["expenses", "Expenses", "reports"], ["dressers", "Dressers", "dressers"], ["doctors", "Doctors", "dressers"], ["reports", "Reports", "reports"], ["combined", "All Business", "overview"]].map(([key, label, icon]) => (''')

apply("Render ExpensesTab",
'''        {tab === "reports" && <ReportsTab cases={cases} products={products}''',
'''        {tab === "expenses" && (
          <ExpensesTab
            expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense}
            fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense}
          />
        )}
        {tab === "reports" && <ReportsTab cases={cases} products={products}''')

apply("Insert ExpensesTab component",
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses = [], addFixedExpense, deleteFixedExpense,''',
'''function ExpensesTab({ expenses, addExpense, deleteExpense, fixedExpenses, addFixedExpense, deleteFixedExpense }) {
  const [fixedExpForm, setFixedExpForm] = useState({ category: "Salary", amount: "", note: "" });
  const [expCategory, setExpCategory] = useState("Salary");
  const [expAmount, setExpAmount] = useState("");
  const [expDate, setExpDate] = useState(todayISO());
  const [expNote, setExpNote] = useState("");

  const fixedExpensesMonthlyTotal = useMemo(() => (fixedExpenses || []).reduce((s, e) => s + Number(e.amount || 0), 0), [fixedExpenses]);
  const expensesSorted = useMemo(() => [...(expenses || [])].sort((a, b) => new Date(b.date) - new Date(a.date)), [expenses]);
  const expensesByCategory = useMemo(() => {
    const tally = {};
    (expenses || []).forEach((e) => { tally[e.category || "Other"] = (tally[e.category || "Other"] || 0) + Number(e.amount || 0); });
    return Object.entries(tally).map(([category, amount]) => ({ category, amount })).sort((a, b) => b.amount - a.amount);
  }, [expenses]);
  const expensesTotal = useMemo(() => (expenses || []).reduce((s, e) => s + Number(e.amount || 0), 0), [expenses]);

  return (
    <div>
      <CollapsibleSection title="Fixed Monthly Expenses" defaultOpen right={fixedExpensesMonthlyTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(fixedExpensesMonthlyTotal)}/mo</span> : null}>
        <div style={styles.emptyState2}>Recurring costs like Salary or Office Rent — enter once, and they're auto-added to Monthly and Yearly Profit & Loss every period, without re-entering each month.</div>
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
        {(fixedExpenses || []).length === 0 ? <EmptyState text="No fixed monthly expenses set up yet." /> : (
          <div style={styles.card}>
            {(fixedExpenses || []).map((e) => (
              <div key={e.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{e.category}{e.note ? ` · ${e.note}` : ""}</span>
                <span style={{ fontWeight: 700 }}>{fmtMoney(e.amount)}/mo</span>
                <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => { if (window.confirm("Remove this fixed expense?")) deleteFixedExpense(e.id); }}>✕</button>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Variable Expenses" defaultOpen right={expensesTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(expensesTotal)}</span> : null}>
        <div style={styles.formGrid}>
          <div style={styles.addPaymentRow}>
            <select style={{ ...styles.smallInput, flex: 1 }} value={expCategory} onChange={(e) => setExpCategory(e.target.value)}>
              {["Salary", "Rent", "Transport/Fuel", "Machine Maintenance", "Utilities", "Marketing", "Other"].map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <input type="number" placeholder="Amount ₹" style={{ ...styles.smallInput, width: 100 }} value={expAmount} onChange={(e) => setExpAmount(e.target.value)} />
          </div>
          <div style={styles.addPaymentRow}>
            <input type="date" style={styles.smallInput} value={expDate} onChange={(e) => setExpDate(e.target.value)} />
            <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={expNote} onChange={(e) => setExpNote(e.target.value)} />
            <button style={styles.smallBtn} onClick={() => {
              const amt = Number(expAmount);
              if (!amt || amt <= 0) return;
              addExpense({ category: expCategory, amount: amt, date: expDate, note: expNote.trim() });
              setExpAmount(""); setExpNote("");
            }}>Add Expense</button>
          </div>
        </div>
        {expensesByCategory.length === 0 ? <EmptyState text="No expenses logged yet. Salaries, rent, fuel, maintenance — anything beyond product cost." /> : (
          <>
            <div style={{ ...styles.card, marginBottom: 12 }}>
              {expensesByCategory.map((c) => (
                <div key={c.category} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{c.category}</span><span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(c.amount)}</span></div>
              ))}
            </div>
            <div style={styles.card}>
              {expensesSorted.slice(0, 40).map((e) => (
                <div key={e.id} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{e.category}{e.note ? ` · ${e.note}` : ""}</span>
                  <span style={styles.mutedSmall}>{fmtDate(e.date)}</span>
                  <span style={{ fontWeight: 700 }}>{fmtMoney(e.amount)}</span>
                  <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => { if (window.confirm("Delete this expense entry?")) deleteExpense(e.id); }}>✕</button>
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>
    </div>
  );
}

function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses = [], addFixedExpense, deleteFixedExpense,''')

apply("Make Reports Fixed+Variable Expenses sections read-only",
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

      <CollapsibleSection title="Expenses" right={expensesTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(expensesTotal)}</span> : null}>
        {!readOnly && (
          <div style={styles.formGrid}>
            <div style={styles.addPaymentRow}>
              <select style={{ ...styles.smallInput, flex: 1 }} value={expCategory} onChange={(e) => setExpCategory(e.target.value)}>
                {["Salary", "Rent", "Transport/Fuel", "Machine Maintenance", "Utilities", "Marketing", "Other"].map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <input type="number" placeholder="Amount ₹" style={{ ...styles.smallInput, width: 100 }} value={expAmount} onChange={(e) => setExpAmount(e.target.value)} />
            </div>
            <div style={styles.addPaymentRow}>
              <input type="date" style={styles.smallInput} value={expDate} onChange={(e) => setExpDate(e.target.value)} />
              <input type="text" placeholder="Note (optional)" style={{ ...styles.smallInput, flex: 1 }} value={expNote} onChange={(e) => setExpNote(e.target.value)} />
              <button style={styles.smallBtn} onClick={() => {
                const amt = Number(expAmount);
                if (!amt || amt <= 0) return;
                addExpense({ category: expCategory, amount: amt, date: expDate, note: expNote.trim() });
                setExpAmount(""); setExpNote("");
              }}>Add Expense</button>
            </div>
          </div>
        )}
        {expensesByCategory.length === 0 ? <EmptyState text="No expenses logged yet. Salaries, rent, fuel, maintenance — anything beyond product cost." /> : (
          <>
            <div style={{ ...styles.card, marginBottom: 12 }}>
              {expensesByCategory.map((c) => (
                <div key={c.category} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{c.category}</span><span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(c.amount)}</span></div>
              ))}
            </div>
            <div style={styles.card}>
              {expensesSorted.slice(0, 40).map((e) => (
                <div key={e.id} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{e.category}{e.note ? ` · ${e.note}` : ""}</span>
                  <span style={styles.mutedSmall}>{fmtDate(e.date)}</span>
                  <span style={{ fontWeight: 700 }}>{fmtMoney(e.amount)}</span>
                  {!readOnly && <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => { if (window.confirm("Delete this expense entry?")) deleteExpense(e.id); }}>✕</button>}
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>''',
'''      <CollapsibleSection title="Fixed Monthly Expenses" right={fixedExpensesMonthlyTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(fixedExpensesMonthlyTotal)}/mo</span> : null}>
        <div style={styles.emptyState2}>View only — add or edit these in the Expenses tab.</div>
        {(fixedExpenses || []).length === 0 ? <EmptyState text="No fixed monthly expenses set up yet." /> : (
          <div style={styles.card}>
            {(fixedExpenses || []).map((e) => (
              <div key={e.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{e.category}{e.note ? ` · ${e.note}` : ""}</span>
                <span style={{ fontWeight: 700 }}>{fmtMoney(e.amount)}/mo</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Expenses" right={expensesTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(expensesTotal)}</span> : null}>
        <div style={styles.emptyState2}>View only — add or edit these in the Expenses tab.</div>
        {expensesByCategory.length === 0 ? <EmptyState text="No expenses logged yet." /> : (
          <>
            <div style={{ ...styles.card, marginBottom: 12 }}>
              {expensesByCategory.map((c) => (
                <div key={c.category} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{c.category}</span><span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(c.amount)}</span></div>
              ))}
            </div>
            <div style={styles.card}>
              {expensesSorted.slice(0, 40).map((e) => (
                <div key={e.id} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{e.category}{e.note ? ` · ${e.note}` : ""}</span>
                  <span style={styles.mutedSmall}>{fmtDate(e.date)}</span>
                  <span style={{ fontWeight: 700 }}>{fmtMoney(e.amount)}</span>
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
