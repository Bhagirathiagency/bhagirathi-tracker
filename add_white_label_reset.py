edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add factoryResetApp function",
'''  const resetTestData = () => { setCases([]); setProducts([]); };''',
'''  const resetTestData = () => { setCases([]); setProducts([]); };
  const factoryResetApp = () => {
    setCases([]);
    setMachines([]);
    setProducts(DEFAULT_PRODUCTS);
    setDressers([]);
    setDresserPins({});
    setDresserStockAccessState({});
    setOwnerLogins([]);
    setDresserProfiles({});
    setQuotations([]);
    setDoctorCalls([]);
    setExpenses([]);
    setSupplierLedger([]);
    setFixedExpenses([]);
    setPreviousOutstanding([]);
    setChallans([]);
    setDoctorsList([]);
    setDiscussionTopics(["VAC Therapy", "Oxygen Therapy", "Matriderm", "Wound Dressing", "General Consultation"]);
    setPin(null);
    setAccountantPinState(null);
  };''')

apply("Pass factoryResetApp to OwnerShell call",
'''          resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding}''',
'''          resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding} factoryResetApp={factoryResetApp}''')

apply("OwnerShell fn signature",
'''resetTestData, clearAllOutstanding, doctorCalls, doctorsList, addDoctorMaster,''',
'''resetTestData, clearAllOutstanding, factoryResetApp, doctorCalls, doctorsList, addDoctorMaster,''')

apply("Pass factoryResetApp to MasterSettingsTab",
'''          <MasterSettingsTab outstandingTotal={outstandingTotal} clearAllOutstanding={clearAllOutstanding} resetTestData={resetTestData} />''',
'''          <MasterSettingsTab outstandingTotal={outstandingTotal} clearAllOutstanding={clearAllOutstanding} resetTestData={resetTestData} factoryResetApp={factoryResetApp} businessName={business.name} />''')

apply("Add factoryResetApp prop to MasterSettingsTab signature",
'''function MasterSettingsTab({ outstandingTotal, clearAllOutstanding, resetTestData }) {
  return (
    <div>
      <SectionTitle>Danger Zone</SectionTitle>
      <div style={{ ...styles.emptyState2, marginBottom: 10 }}>Destructive, irreversible actions live here — kept separate from everyday screens on purpose.</div>''',
'''function MasterSettingsTab({ outstandingTotal, clearAllOutstanding, resetTestData, factoryResetApp, businessName = "this business" }) {
  return (
    <div>
      <SectionTitle>Danger Zone</SectionTitle>
      <div style={{ ...styles.emptyState2, marginBottom: 10 }}>Destructive, irreversible actions live here — kept separate from everyday screens on purpose.</div>''')

apply("Add White Label Reset section",
'''      <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4" }}>
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
}''',
'''      <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4" }}>
        <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
          Permanently clears all cases and all stock/products — use this to wipe out testing data before going live. This cannot be undone.
        </div>
        <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={() => {
          const typed = window.prompt('This will permanently delete ALL cases and ALL stock/products. Type "RESET" to confirm:');
          if (typed === "RESET") resetTestData();
        }}>Clear All Cases &amp; Stock</button>
      </div>

      <SectionTitle>White Label — Prepare for a New Client</SectionTitle>
      <div style={{ ...styles.emptyState2, marginBottom: 10 }}>Use this only when handing this exact app off to a brand-new client. It wipes absolutely everything for {businessName} so they start with a completely clean slate.</div>
      <div style={{ ...styles.card, padding: 14, border: "2px solid #E1483C" }}>
        <div style={{ fontWeight: 700, color: "#E1483C", marginBottom: 6 }}>Reset Entire App for New Client</div>
        <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
          Deletes every case, product, machine, dresser, quotation, expense, doctor, challan, and outstanding balance — and resets both the Owner PIN and Accountant PIN so the new client can set their own. This cannot be undone.
        </div>
        <button style={{ ...styles.smallBtn, background: "#E1483C", fontWeight: 700 }} onClick={() => {
          const typed = window.prompt('This wipes EVERYTHING in this app for a new client. Type "WHITE LABEL RESET" exactly to confirm:');
          if (typed === "WHITE LABEL RESET") factoryResetApp();
        }}>Reset Entire App for New Client</button>
      </div>
    </div>
  );
}''')

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
