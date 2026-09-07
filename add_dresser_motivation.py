edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Pass dresserProfiles to ReportsTab call",
'''        {tab === "reports" && <ReportsTab cases={cases} products={products} dresserStats={dresserStats} dressers={dressers} outstandingTotal={outstandingTotal} overdueCount={overdueCount} lowStock={lowStock} resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding} doctorCalls={doctorCalls} quotations={quotations} ownerLogins={ownerLogins} businessId={businessId} businessName={business.name} expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense} machines={machines} addPayment={addPayment} />}''',
'''        {tab === "reports" && <ReportsTab cases={cases} products={products} dresserStats={dresserStats} dressers={dressers} outstandingTotal={outstandingTotal} overdueCount={overdueCount} lowStock={lowStock} resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding} doctorCalls={doctorCalls} quotations={quotations} ownerLogins={ownerLogins} businessId={businessId} businessName={business.name} expenses={expenses} addExpense={addExpense} deleteExpense={deleteExpense} supplierLedger={supplierLedger} addSupplierLedgerEntry={addSupplierLedgerEntry} deleteSupplierLedgerEntry={deleteSupplierLedgerEntry} fixedExpenses={fixedExpenses} addFixedExpense={addFixedExpense} deleteFixedExpense={deleteFixedExpense} machines={machines} addPayment={addPayment} dresserProfiles={dresserProfiles} />}''')

apply("ReportsTab fn signature dresserProfiles",
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses = [], addFixedExpense, deleteFixedExpense,''',
'''function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency", expenses, addExpense, deleteExpense, supplierLedger = [], addSupplierLedgerEntry, deleteSupplierLedgerEntry, fixedExpenses = [], addFixedExpense, deleteFixedExpense, dresserProfiles = {},''')

apply("Add motivate message generator and button in per-dresser SWOT cards",
'''      <CollapsibleSection title="SWOT Analysis — Team (per Dresser)">
        {dresserSWOT.length === 0 ? <EmptyState text="No dressers added yet." /> : (
          <div style={styles.list}>
            {dresserSWOT.map((d) => (
              <CollapsibleSubcard key={d.name} title={d.name}>
                <SWOTGrid swot={d} />
              </CollapsibleSubcard>
            ))}
          </div>
        )}
      </CollapsibleSection>''',
'''      <CollapsibleSection title="SWOT Analysis — Team (per Dresser)">
        {dresserSWOT.length === 0 ? <EmptyState text="No dressers added yet." /> : (
          <div style={styles.list}>
            {dresserSWOT.map((d) => {
              const buildMotivation = () => {
                let msg = `Hi ${d.name}! 👋\\n\\n`;
                if (d.s && d.s.length && d.s[0] !== "No activity logged yet.") {
                  msg += `Great work so far — ${d.s[0]}\\n\\n`;
                } else {
                  msg += `Let's get your numbers moving this week — every case you log builds your track record.\\n\\n`;
                }
                if (d.w && d.w.length && d.w[0] !== "No activity logged yet.") {
                  msg += `One thing to focus on: ${d.w[0]}\\n\\n`;
                }
                if (d.o && d.o.length && d.o[0] !== "No specific opportunity identified from current data.") {
                  msg += `Opportunity: ${d.o[0]}\\n\\n`;
                }
                msg += `You're a key part of the team — keep it up! 💪\\n– ${businessName}`;
                return msg;
              };
              const phone = (dresserProfiles && dresserProfiles[d.name] && dresserProfiles[d.name].phone) || "";
              const waNumber = phone ? `91${phone.replace(/\\D/g, "").slice(-10)}` : OWNER_WHATSAPP;
              return (
                <CollapsibleSubcard key={d.name} title={d.name}>
                  <SWOTGrid swot={d} />
                  <button style={{ ...styles.smallBtn, marginTop: 10, background: "#3B5BA5" }} onClick={() => window.open(waLink(waNumber, buildMotivation()), "_blank")}>
                    💬 Send Motivation via WhatsApp{!phone ? " (to you — forward it on)" : ""}
                  </button>
                </CollapsibleSubcard>
              );
            })}
          </div>
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
