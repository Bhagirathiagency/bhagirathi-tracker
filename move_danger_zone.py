edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add Master Settings nav entry",
'''        {[["reports", "Reports", "reports"], ["dashboard", "Command Center", "overview"], ["cases", "Cases", "cases"], ["challans", "Challans", "stock"], ["quotations", "Quotes", "quotes"], ["machines", "Machines", "machines"], ["stock", "Stock", "stock"], ["expenses", "Expenses", "reports"], ["dressers", "Dressers", "dressers"], ["doctors", "Doctors", "dressers"], ["combined", "All Business", "overview"]].map(([key, label, icon]) => (''',
'''        {[["reports", "Reports", "reports"], ["dashboard", "Command Center", "overview"], ["cases", "Cases", "cases"], ["challans", "Challans", "stock"], ["quotations", "Quotes", "quotes"], ["machines", "Machines", "machines"], ["stock", "Stock", "stock"], ["expenses", "Expenses", "reports"], ["dressers", "Dressers", "dressers"], ["doctors", "Doctors", "dressers"], ["combined", "All Business", "overview"], ["settings", "Master Settings", "reports"]].map(([key, label, icon]) => (''')

apply("Render MasterSettingsTab",
'''        {tab === "reports" && <ReportsTab cases={cases} products={products}''',
'''        {tab === "settings" && (
          <MasterSettingsTab outstandingTotal={outstandingTotal} clearAllOutstanding={clearAllOutstanding} resetTestData={resetTestData} />
        )}
        {tab === "reports" && <ReportsTab cases={cases} products={products}''')

apply("Remove Danger Zone from ReportsTab",
'''      {!readOnly && (
        <>
          <SectionTitle>Danger Zone</SectionTitle>
          <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4", marginBottom: 10 }}>
            <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
              Marks every case's outstanding balance as paid (adds a settling payment entry to each). Case history stays intact — only outstanding drops to zero. Currently outstanding: {fmtMoney(outstandingTotal)}.
            </div>
            <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={() => {
              const typed = window.prompt('This will mark ALL outstanding balances as paid. Type "CLEAR" to confirm:');
              if (typed === "CLEAR") clearAllOutstanding();
            }}>Zero Out All Outstanding</button>
          </div>
          <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4" }}>
            <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
              Permanently clears all cases and all stock/products — use this to wipe out testing data before going live. This cannot be undone.
            </div>
            <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={() => {
              const typed = window.prompt('This will permanently delete ALL cases and ALL stock/products. Type "RESET" to confirm:');
              if (typed === "RESET") resetTestData();
            }}>Clear All Cases &amp; Stock</button>
          </div>
        </>
      )}
    </div>
  );
}
// ---------------- styles ----------------''',
'''    </div>
  );
}

function MasterSettingsTab({ outstandingTotal, clearAllOutstanding, resetTestData }) {
  return (
    <div>
      <SectionTitle>Danger Zone</SectionTitle>
      <div style={{ ...styles.emptyState2, marginBottom: 10 }}>Destructive, irreversible actions live here — kept separate from everyday screens on purpose.</div>
      <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4", marginBottom: 10 }}>
        <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
          Marks every case's outstanding balance as paid (adds a settling payment entry to each). Case history stays intact — only outstanding drops to zero. Currently outstanding: {fmtMoney(outstandingTotal)}.
        </div>
        <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={() => {
          const typed = window.prompt('This will mark ALL outstanding balances as paid. Type "CLEAR" to confirm:');
          if (typed === "CLEAR") clearAllOutstanding();
        }}>Zero Out All Outstanding</button>
      </div>
      <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4" }}>
        <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
          Permanently clears all cases and all stock/products — use this to wipe out testing data before going live. This cannot be undone.
        </div>
        <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={() => {
          const typed = window.prompt('This will permanently delete ALL cases and ALL stock/products. Type "RESET" to confirm:');
          if (typed === "RESET") resetTestData();
        }}>Clear All Cases &amp; Stock</button>
      </div>
    </div>
  );
}
// ---------------- styles ----------------''')

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
