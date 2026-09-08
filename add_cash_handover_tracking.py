edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add markPaymentHandedOver function",
'''  const addPayment = (caseId, payment) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, payments: [...(c.payments || []), { id: uid(), ...payment }] } : c));
  };''',
'''  const addPayment = (caseId, payment) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, payments: [...(c.payments || []), { id: uid(), ...payment }] } : c));
  };
  const markPaymentHandedOver = (caseId, paymentId) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? {
      ...c,
      payments: (c.payments || []).map((p) => p.id === paymentId ? { ...p, handedOver: true, handedOverDate: todayISO() } : p),
    } : c));
  };''')

apply("Tag dresser-collected payments with collectedBy and handedOver",
'''                  onAddPayment({ amount: amt, mode: payMode, note: payNote, date: todayISO() });
                  setPayAmount(""); setPayNote("");
                }}>Add</button>''',
'''                  onAddPayment({ amount: amt, mode: payMode, note: payNote, date: todayISO(), collectedBy: dresserName, handedOver: payMode !== "Cash" });
                  setPayAmount(""); setPayNote("");
                }}>Add</button>''')

apply("Tag owner-collected payments as already handed over",
'''                    onAddPayment({ amount: amt, mode: payMode, note: payNote.trim(), date: todayISO() });
                    setPayAmount(""); setPayNote("");
                  }}>Collect Payment</button>''',
'''                    onAddPayment({ amount: amt, mode: payMode, note: payNote.trim(), date: todayISO(), handedOver: true });
                    setPayAmount(""); setPayNote("");
                  }}>Collect Payment</button>''')

apply("Pass markPaymentHandedOver to OwnerShell call",
'''          saveCase={saveCase} deleteCase={deleteCase} addPayment={addPayment} addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem}''',
'''          saveCase={saveCase} deleteCase={deleteCase} addPayment={addPayment} markPaymentHandedOver={markPaymentHandedOver} addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem}''')

apply("OwnerShell fn signature accepts markPaymentHandedOver",
'''function OwnerShell({ cases, machines, setMachines, products, setProducts, receiveStock, dressers, addDresser, removeDresser, dresserPins, setDresserPin, dresserProfiles, dresserStockAccess, setDresserStockAccess, dresserBusinessAccess, setDresserBusinessAccess, saveCase, deleteCase, addPayment, addDressingChange,''',
'''function OwnerShell({ cases, machines, setMachines, products, setProducts, receiveStock, dressers, addDresser, removeDresser, dresserPins, setDresserPin, dresserProfiles, dresserStockAccess, setDresserStockAccess, dresserBusinessAccess, setDresserBusinessAccess, saveCase, deleteCase, addPayment, markPaymentHandedOver, addDressingChange,''')

apply("Pass markPaymentHandedOver to ReportsTab",
'''        {tab === "reports" && <ReportsTab cases={cases} products={products} dresserStats={dresserStats} dressers={dressers} outstandingTotal={outstandingTotal} overdueCount={overdueCount} lowStock={lowStock} resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding} doctorCalls={doctorCalls} quotations={quotations} ownerLogins={ownerLogins} businessId={businessId} businessName={business.name} expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense} previousOutstanding={previousOutstanding} addPreviousOutstanding={addPreviousOutstanding} deletePreviousOutstanding={deletePreviousOutstanding} addPreviousOutstandingPayment={addPreviousOutstandingPayment} machines={machines} addPayment={addPayment} dresserProfiles={dresserProfiles} />}''',
'''        {tab === "reports" && <ReportsTab cases={cases} products={products} dresserStats={dresserStats} dressers={dressers} outstandingTotal={outstandingTotal} overdueCount={overdueCount} lowStock={lowStock} resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding} doctorCalls={doctorCalls} quotations={quotations} ownerLogins={ownerLogins} businessId={businessId} businessName={business.name} expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense} previousOutstanding={previousOutstanding} addPreviousOutstanding={addPreviousOutstanding} deletePreviousOutstanding={deletePreviousOutstanding} addPreviousOutstandingPayment={addPreviousOutstandingPayment} machines={machines} addPayment={addPayment} markPaymentHandedOver={markPaymentHandedOver} dresserProfiles={dresserProfiles} />}''')

apply("ReportsTab fn signature accepts markPaymentHandedOver and computes cashPendingHandover",
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses = [], addFixedExpense, deleteFixedExpense, previousOutstanding = [], addPreviousOutstanding, deletePreviousOutstanding, addPreviousOutstandingPayment, dresserProfiles = {}, machines, addPayment, readOnly = false }) {''',
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses = [], addFixedExpense, deleteFixedExpense, previousOutstanding = [], addPreviousOutstanding, deletePreviousOutstanding, addPreviousOutstandingPayment, dresserProfiles = {}, machines, addPayment, markPaymentHandedOver, readOnly = false }) {
  const cashPendingHandover = useMemo(() => {
    const byDresser = {};
    cases.forEach((c) => {
      (c.payments || []).forEach((p) => {
        if (p.mode === "Cash" && p.collectedBy && !p.handedOver) {
          if (!byDresser[p.collectedBy]) byDresser[p.collectedBy] = { total: 0, items: [] };
          byDresser[p.collectedBy].total += Number(p.amount || 0);
          byDresser[p.collectedBy].items.push({ ...p, caseId: c.id, patientName: c.patientName });
        }
      });
    });
    return Object.entries(byDresser).map(([name, data]) => ({ name, ...data })).sort((a, b) => b.total - a.total);
  }, [cases]);
  const cashPendingTotal = cashPendingHandover.reduce((s, d) => s + d.total, 0);
  const [expandedCashDresser, setExpandedCashDresser] = useState(null);''')

apply("Add Cash Pending Handover UI section",
'''      {reportSubTab === "team" && (
      <CollapsibleSection title="SWOT Analysis — Team (per Dresser)">''',
'''      {reportSubTab === "team" && (
      <>
      <CollapsibleSection title="Cash Pending Handover" right={cashPendingTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{fmtMoney(cashPendingTotal)}</span> : null}>
        <div style={styles.emptyState2}>Cash your dressers have collected from patients/doctors/hospitals but haven't physically handed over to you yet.</div>
        {cashPendingHandover.length === 0 ? <EmptyState text="No cash pending handover — all collected cash has been received." /> : (
          <div style={styles.card}>
            {cashPendingHandover.map((d) => (
              <div key={d.name}>
                <div style={styles.dresserLine} onClick={() => setExpandedCashDresser(expandedCashDresser === d.name ? null : d.name)}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span>
                  <span style={{ fontWeight: 700, color: "#E1483C" }}>{fmtMoney(d.total)}</span>
                </div>
                {expandedCashDresser === d.name && d.items.map((p) => (
                  <div key={p.id} style={{ padding: "8px 14px 8px 24px", borderBottom: "1px solid #F0EEE3" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                      <span>{p.patientName} — {fmtMoney(p.amount)} ({fmtDate(p.date)})</span>
                    </div>
                    {!readOnly && markPaymentHandedOver && (
                      <button style={{ ...styles.linkBtn, color: "#128577", marginTop: 4 }} onClick={() => markPaymentHandedOver(p.caseId, p.id)}>
                        ✓ Mark Received from {d.name}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="SWOT Analysis — Team (per Dresser)">''')

apply("Close fragment for team subtab",
'''            })}
          </div>
        )}
      </CollapsibleSection>
      )}

      <SectionTitle>Revenue</SectionTitle>''',
'''            })}
          </div>
        )}
      </CollapsibleSection>
      </>
      )}

      <SectionTitle>Revenue</SectionTitle>''')

apply("Add Cash I'm Holding reminder to dresser's own view",
'''        <CollapsibleSection title={t("yourReporting")}>
          <div style={styles.cardGrid}>''',
'''        <CollapsibleSection title={t("yourReporting")}>
          {(() => {
            let cashPending = 0;
            cases.forEach((c) => (c.payments || []).forEach((p) => {
              if (p.mode === "Cash" && p.collectedBy === name && !p.handedOver) cashPending += Number(p.amount || 0);
            }));
            return cashPending > 0 ? (
              <div style={{ ...styles.card, padding: 14, marginBottom: 14, border: "1px solid #FCE7E4", background: "#FFF7F5" }}>
                <div style={{ fontWeight: 700, color: "#E1483C" }}>💵 Cash you're holding: {fmtMoney(cashPending)}</div>
                <div style={{ fontSize: 12, color: "#5B6864", marginTop: 4 }}>Please hand this over to the Owner as soon as possible.</div>
              </div>
            ) : null;
          })()}
          <div style={styles.cardGrid}>''')

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
