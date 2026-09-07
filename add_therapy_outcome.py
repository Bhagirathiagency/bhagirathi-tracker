edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Pass onUpdateStatus to DresserCaseRow",
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} doctorsList={doctorsList} onAddPayment={(p) => addPayment(c.id, p)}
                  onAddDressingChange={(e) => addDressingChange(c.id, e)}
                  onDeleteDressingChange={(changeId) => deleteDressingChange(c.id, changeId)}''',
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} doctorsList={doctorsList} onAddPayment={(p) => addPayment(c.id, p)}
                  onAddDressingChange={(e) => addDressingChange(c.id, e)}
                  onDeleteDressingChange={(changeId) => deleteDressingChange(c.id, changeId)}
                  onUpdateStatus={(status, endDate) => saveCase({ ...c, status, endDate }, c.id)}''')

apply("DresserCaseRow fn signature",
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {''',
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onUpdateStatus, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {''')

apply("Add therapyOutcome state",
'''  const [payAmount, setPayAmount] = useState("");
  const [payMode, setPayMode] = useState("Cash");
  const [payNote, setPayNote] = useState("");''',
'''  const [payAmount, setPayAmount] = useState("");
  const [payMode, setPayMode] = useState("Cash");
  const [payNote, setPayNote] = useState("");
  const [therapyOutcome, setTherapyOutcome] = useState("continue");
  const [outcomeDate, setOutcomeDate] = useState(todayISO());''')

apply("Add outcome selector and update log button",
'''          <div style={{ ...styles.detailLabel, marginTop: 14 }}>Log a dressing change</div>
          <div style={styles.addPaymentRow}>
            <input style={{ ...styles.smallInput, flex: 1 }} value={dresserName} disabled />
            <select value={protocolDays} onChange={(e) => setProtocolDays(e.target.value === "na" ? 0 : Number(e.target.value))} style={styles.smallInput}>
              {PROTOCOLS.map((p) => <option key={p} value={p}>{p}d</option>)}
              <option value="na">N/A</option>
            </select>
          </div>
          <input type="text" placeholder="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)}
            style={{ ...styles.smallInput, width: "100%", marginTop: 8, boxSizing: "border-box" }} />
          <div style={styles.mutedSmall}>Products used at this visit (select what was actually used, single or multiple)</div>
          <ProductsUsedPicker products={products} selected={changeProducts} onChange={setChangeProducts} />
          <button style={{ ...styles.smallBtn, width: "100%", marginTop: 8 }} onClick={() => {
            onAddDressingChange({ date: todayISO(), dresserName, protocolDays, note, products: changeProducts.filter((p) => Number(p.qty) > 0) });
            setNote(""); setChangeProducts([]); setOpen(false);
          }}>Log Today's Change</button>''',
'''          <div style={{ ...styles.detailLabel, marginTop: 14 }}>Log a dressing change</div>
          <div style={styles.addPaymentRow}>
            <input style={{ ...styles.smallInput, flex: 1 }} value={dresserName} disabled />
            <select value={protocolDays} onChange={(e) => setProtocolDays(e.target.value === "na" ? 0 : Number(e.target.value))} style={styles.smallInput}>
              {PROTOCOLS.map((p) => <option key={p} value={p}>{p}d</option>)}
              <option value="na">N/A</option>
            </select>
          </div>
          <input type="text" placeholder="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)}
            style={{ ...styles.smallInput, width: "100%", marginTop: 8, boxSizing: "border-box" }} />
          <div style={styles.mutedSmall}>Products used at this visit (select what was actually used, single or multiple)</div>
          <ProductsUsedPicker products={products} selected={changeProducts} onChange={setChangeProducts} />

          {onUpdateStatus && (
            <>
              <div style={{ ...styles.detailLabel, marginTop: 12 }}>After this visit, what's next for the therapy?</div>
              <div style={styles.addPaymentRow}>
                <select value={therapyOutcome} onChange={(e) => setTherapyOutcome(e.target.value)} style={{ ...styles.smallInput, flex: 1 }}>
                  <option value="continue">Continue same protocol (routine change)</option>
                  <option value="stopped">Stop Therapy</option>
                  <option value="reapplied">Reapply / Continue New Cycle</option>
                </select>
                {therapyOutcome !== "continue" && (
                  <input type="date" value={outcomeDate} onChange={(e) => setOutcomeDate(e.target.value)} style={styles.smallInput} />
                )}
              </div>
            </>
          )}

          <button style={{ ...styles.smallBtn, width: "100%", marginTop: 8 }} onClick={() => {
            onAddDressingChange({ date: todayISO(), dresserName, protocolDays, note, products: changeProducts.filter((p) => Number(p.qty) > 0) });
            if (onUpdateStatus && therapyOutcome !== "continue") {
              onUpdateStatus(therapyOutcome, outcomeDate);
            }
            setNote(""); setChangeProducts([]); setTherapyOutcome("continue"); setOpen(false);
          }}>{therapyOutcome === "continue" ? "Log Today's Change" : therapyOutcome === "stopped" ? "Log Change & Mark Stopped" : "Log Change & Mark Reapplied"}</button>''')

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
