edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Expand PAY_MODES",
'''const PAY_MODES = ["Cash", "Online", "Credit"];''',
'''const PAY_MODES = ["Cash", "Online", "Cheque", "RTGS", "Credit"];''')

apply("Pass addPayment to DresserShell call",
'''          name={role.name} cases={cases} machines={machines} products={products} setProducts={setProducts} receiveStock={receiveStock} saveCase={saveCase}
          addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem} capturePhoto={capturePhoto}''',
'''          name={role.name} cases={cases} machines={machines} products={products} setProducts={setProducts} receiveStock={receiveStock} saveCase={saveCase}
          addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem} addPayment={addPayment} capturePhoto={capturePhoto}''')

apply("DresserShell fn signature",
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem, capturePhoto, updateDresserLocation,''',
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem, addPayment, capturePhoto, updateDresserLocation,''')

apply("Pass onAddPayment into DresserCaseRow",
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products}''',
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} onAddPayment={(p) => addPayment(c.id, p)}''')

apply("DresserCaseRow fn signature",
'''function DresserCaseRow({ c, dresserName, products, onAddDressingChange, onAddAdditionalItem, onCapturePhoto }) {''',
'''function DresserCaseRow({ c, dresserName, products, onAddDressingChange, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {''')

apply("Add payment state in DresserCaseRow",
'''function DresserCaseRow({ c, dresserName, products, onAddDressingChange, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {
  const [open, setOpen] = useState(false);
  const [protocolDays, setProtocolDays] = useState(c.protocolDays || 5);
  const [note, setNote] = useState("");
  const [changeProducts, setChangeProducts] = useState([]);
  const [uploading, setUploading] = useState(null);''',
'''function DresserCaseRow({ c, dresserName, products, onAddDressingChange, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {
  const [open, setOpen] = useState(false);
  const [protocolDays, setProtocolDays] = useState(c.protocolDays || 5);
  const [note, setNote] = useState("");
  const [changeProducts, setChangeProducts] = useState([]);
  const [uploading, setUploading] = useState(null);
  const [payAmount, setPayAmount] = useState("");
  const [payMode, setPayMode] = useState("Cash");
  const [payNote, setPayNote] = useState("");
  const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
  const outstanding = Math.max(0, Number(c.totalAmount || 0) + Number(c.machineRentalAmount || 0) - paid);''')

apply("Insert payment collection UI in DresserCaseRow",
'''          <AdditionalItemsBlock c={c} products={products} onAddAdditionalItem={onAddAdditionalItem} />
        </div>
      )}
    </div>
  );
}

// ---------------- Dashboard ----------------''',
'''          <AdditionalItemsBlock c={c} products={products} onAddAdditionalItem={onAddAdditionalItem} />

          {onAddPayment && (
            <div style={{ ...styles.paymentsSection, marginTop: 14 }}>
              <div style={styles.detailLabel}>Payment collection</div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 6 }}>
                <span style={styles.mutedSmall}>Outstanding</span>
                <span style={{ fontWeight: 700, color: outstanding > 0 ? "#E1483C" : "#128577" }}>{fmtMoney(outstanding)}</span>
              </div>
              {(c.payments || []).length > 0 && (c.payments || []).slice().sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 5).map((p) => (
                <div key={p.id} style={styles.paymentLine}><span>{fmtDate(p.date)}</span><span>{fmtMoney(p.amount)}</span><span style={styles.mutedSmall}>{p.mode || "Cash"}{p.note ? ` · ${p.note}` : ""}</span></div>
              ))}
              {outstanding > 0 && (
                <div style={styles.addPaymentRow}>
                  <input type="number" placeholder="Amount" value={payAmount} onChange={(e) => setPayAmount(e.target.value)} style={styles.smallInput} />
                  <select value={payMode} onChange={(e) => setPayMode(e.target.value)} style={styles.smallInput}>
                    {PAY_MODES.map((m) => <option key={m} value={m}>{m}</option>)}
                  </select>
                  <input type="text" placeholder="Note e.g. cheque no. / UTR" value={payNote} onChange={(e) => setPayNote(e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                  <button style={styles.smallBtn} onClick={() => {
                    const amt = Number(payAmount);
                    if (!amt || amt <= 0) return;
                    onAddPayment({ amount: amt, mode: payMode, note: payNote.trim(), date: todayISO() });
                    setPayAmount(""); setPayNote("");
                  }}>Collect Payment</button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------- Dashboard ----------------''')

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
