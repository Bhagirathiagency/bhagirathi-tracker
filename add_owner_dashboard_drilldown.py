edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add casesInitialFilter state",
'''  const [tab, setTab] = useState("dashboard");''',
'''  const [tab, setTab] = useState("dashboard");
  const [casesInitialFilter, setCasesInitialFilter] = useState(null);
  const goToCases = (filterValue) => { setCasesInitialFilter(filterValue); setTab("cases"); };''')

apply("Pass goToCases to Dashboard",
'''          <Dashboard cases={cases} machines={machines} outstandingTotal={outstandingTotal} activeCount={activeCount}
            machinesInUseCount={machinesInUseCount} overdueCount={overdueCount} dueSoonCount={dueSoonCount} dresserStats={dresserStats} lowStock={lowStock}
            products={products} setTab={setTab} />''',
'''          <Dashboard cases={cases} machines={machines} outstandingTotal={outstandingTotal} activeCount={activeCount}
            machinesInUseCount={machinesInUseCount} overdueCount={overdueCount} dueSoonCount={dueSoonCount} dresserStats={dresserStats} lowStock={lowStock}
            products={products} setTab={setTab} goToCases={goToCases} />''')

apply("Pass initialFilter to CasesTab",
'''          <CasesTab cases={cases} machines={machines} products={products} saveCase={saveCase} deleteCase={deleteCase}
            addPayment={addPayment} addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem}
            generateInvoiceNumber={generateInvoiceNumber} businessName={business.name} doctorsList={doctorsList} />''',
'''          <CasesTab cases={cases} machines={machines} products={products} saveCase={saveCase} deleteCase={deleteCase}
            addPayment={addPayment} addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem}
            generateInvoiceNumber={generateInvoiceNumber} businessName={business.name} doctorsList={doctorsList} initialFilter={casesInitialFilter} />''')

apply("CasesTab fn signature + initial filter state + outstanding filter logic",
'''function CasesTab({ cases, machines, products, saveCase, deleteCase, addPayment, addDressingChange, addAdditionalItem, generateInvoiceNumber, businessName, doctorsList }) {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [filter, setFilter] = useState("all"); const [search, setSearch] = useState("");

  const filtered = cases.filter((c) => {
    if (filter === "all") return true;
    if (filter === "overdue") return overdueDays(c) > 0;
    return c.status === filter;
  });''',
'''function CasesTab({ cases, machines, products, saveCase, deleteCase, addPayment, addDressingChange, addAdditionalItem, generateInvoiceNumber, businessName, doctorsList, initialFilter }) {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [filter, setFilter] = useState(initialFilter || "all"); const [search, setSearch] = useState("");

  const filtered = cases.filter((c) => {
    if (filter === "all") return true;
    if (filter === "overdue") return overdueDays(c) > 0;
    if (filter === "outstanding") {
      const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
      return Math.max(0, Number(c.totalAmount || 0) - paid) > 0;
    }
    return c.status === filter;
  });''')

apply("Add Outstanding chip to filter row",
'''        {["all", "active", "overdue", "stopped", "reapplied"].map((f) => (
          <button key={f} onClick={() => setFilter(f)} style={{ ...styles.filterChip, ...(filter === f ? styles.filterChipActive : {}) }}>
            {f === "all" ? "All" : f === "overdue" ? "Change Due" : STATUS[f].label}
          </button>
        ))}''',
'''        {["all", "active", "overdue", "outstanding", "stopped", "reapplied"].map((f) => (
          <button key={f} onClick={() => setFilter(f)} style={{ ...styles.filterChip, ...(filter === f ? styles.filterChipActive : {}) }}>
            {f === "all" ? "All" : f === "overdue" ? "Change Due" : f === "outstanding" ? "Outstanding" : STATUS[f].label}
          </button>
        ))}''')

apply("Update Dashboard fn signature",
'''function Dashboard({ cases, machines, outstandingTotal, activeCount, machinesInUseCount, overdueCount, dueSoonCount, dresserStats, lowStock, products, setTab }) {''',
'''function Dashboard({ cases, machines, outstandingTotal, activeCount, machinesInUseCount, overdueCount, dueSoonCount, dresserStats, lowStock, products, setTab, goToCases }) {''')

apply("Dashboard StatCard onClick handlers",
'''        <StatCard label="Active Cases" value={activeCount} accent="#D9720A" icon="cases" onClick={() => setTab("cases")} />
        <StatCard label="Change Due / Overdue" value={dueSoonCount} accent="#E1483C" icon="reports" onClick={() => setTab("cases")} />
        <StatCard label="Outstanding" value={fmtMoney(outstandingTotal)} accent="#E1483C" icon="quotes" onClick={() => setTab("cases")} />
        <StatCard label="Machines In Use" value={`${machinesInUseCount} / ${machines.length}`} accent="#3B5BA5" icon="machines" onClick={() => setTab("machines")} />''',
'''        <StatCard label="Active Cases" value={activeCount} accent="#D9720A" icon="cases" onClick={() => goToCases("active")} />
        <StatCard label="Change Due / Overdue" value={dueSoonCount} accent="#E1483C" icon="reports" onClick={() => goToCases("overdue")} />
        <StatCard label="Outstanding" value={fmtMoney(outstandingTotal)} accent="#E1483C" icon="quotes" onClick={() => goToCases("outstanding")} />
        <StatCard label="Machines In Use" value={`${machinesInUseCount} / ${machines.length}`} accent="#3B5BA5" icon="machines" onClick={() => setTab("machines")} />''')

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
