edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add timestamp to addDressingChange",
'''  const addDressingChange = (caseId, entry) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, dressingChanges: [...(c.dressingChanges || []), { id: uid(), ...entry }] } : c));
    // Deduct stock for whatever was actually used at this specific visit.''',
'''  const addDressingChange = (caseId, entry) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, dressingChanges: [...(c.dressingChanges || []), { id: uid(), loggedAt: new Date().toISOString(), ...entry }] } : c));
    // Deduct stock for whatever was actually used at this specific visit.''')

apply("Add deleteDressingChange function",
'''  const addAdditionalItem = (caseId, entry) => {''',
'''  const deleteDressingChange = (caseId, changeId) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, dressingChanges: (c.dressingChanges || []).filter((e) => e.id !== changeId) } : c));
  };
  const addAdditionalItem = (caseId, entry) => {''')

apply("Pass deleteDressingChange to DresserShell call",
'''          addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem} addPayment={addPayment} capturePhoto={capturePhoto}''',
'''          addDressingChange={addDressingChange} deleteDressingChange={deleteDressingChange} addAdditionalItem={addAdditionalItem} addPayment={addPayment} capturePhoto={capturePhoto}''')

apply("DresserShell fn signature",
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem,''',
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, deleteDressingChange, addAdditionalItem,''')

apply("Pass deleteDressingChange to DresserCaseRow",
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} onAddPayment={(p) => addPayment(c.id, p)}
                  onAddDressingChange={(e) => addDressingChange(c.id, e)}''',
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} doctorsList={doctorsList} onAddPayment={(p) => addPayment(c.id, p)}
                  onAddDressingChange={(e) => addDressingChange(c.id, e)}
                  onDeleteDressingChange={(changeId) => deleteDressingChange(c.id, changeId)}''')

apply("DresserCaseRow fn signature",
'''function DresserCaseRow({ c, dresserName, products, onAddDressingChange, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {''',
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {''')

apply("Add doctorMobile lookup",
'''  const flags = c.photoFlags || {};
  const doneCount = PHOTO_STAGES.filter((s) => flags[s.key]).length;''',
'''  const flags = c.photoFlags || {};
  const doneCount = PHOTO_STAGES.filter((s) => flags[s.key]).length;
  const matchedDoctor = (doctorsList || []).find((d) => (d.name || "").trim().toLowerCase() === (c.doctorName || "").trim().toLowerCase());
  const doctorMobile = matchedDoctor ? matchedDoctor.mobile : "";
  const myRecentChanges = (c.dressingChanges || []).filter((e) => (e.dresserName || "").trim().toLowerCase() === dresserName.trim().toLowerCase() && e.loggedAt);
  const lastMyChange = myRecentChanges.length ? myRecentChanges[myRecentChanges.length - 1] : null;
  const canUndoLast = lastMyChange && (Date.now() - new Date(lastMyChange.loggedAt).getTime()) < 10 * 60 * 1000;''')

apply("Add click-to-call buttons in expanded header",
'''              <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")}</div>
              <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {protocolLabel(c.protocolDays)} protocol</div>
              <div style={styles.mutedSmall}>{doneCount}/3 photos captured</div>''',
'''              <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProductLines(c).map((l) => l.qty > 1 ? `${l.name} x${l.qty}` : l.name).join(", ")}</div>
              <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {protocolLabel(c.protocolDays)} protocol</div>
              <div style={styles.mutedSmall}>{doneCount}/3 photos captured</div>
              <div style={{ display: "flex", gap: 8, marginTop: 8 }} onClick={(e) => e.stopPropagation()}>
                {c.patientMobile && (
                  <a href={`tel:${c.patientMobile}`} style={{ ...styles.smallBtn, textDecoration: "none", display: "inline-flex", alignItems: "center", background: "#128577" }}>📞 Call Patient</a>
                )}
                {doctorMobile && (
                  <a href={`tel:${doctorMobile}`} style={{ ...styles.smallBtn, textDecoration: "none", display: "inline-flex", alignItems: "center", background: "#3B5BA5" }}>📞 Call Dr. {c.doctorName}</a>
                )}
              </div>''')

apply("Add undo-last-log button after Log Today's Change",
'''          <button style={{ ...styles.smallBtn, width: "100%", marginTop: 8 }} onClick={() => {
            onAddDressingChange({ date: todayISO(), dresserName, protocolDays, note, products: changeProducts.filter((p) => Number(p.qty) > 0) });
            setNote(""); setChangeProducts([]); setOpen(false);
          }}>Log Today's Change</button>''',
'''          <button style={{ ...styles.smallBtn, width: "100%", marginTop: 8 }} onClick={() => {
            onAddDressingChange({ date: todayISO(), dresserName, protocolDays, note, products: changeProducts.filter((p) => Number(p.qty) > 0) });
            setNote(""); setChangeProducts([]); setOpen(false);
          }}>Log Today's Change</button>
          {canUndoLast && onDeleteDressingChange && (
            <button style={{ ...styles.smallBtn, width: "100%", marginTop: 6, background: "#E1483C" }} onClick={() => {
              if (window.confirm("Undo your last logged change for this case?")) onDeleteDressingChange(lastMyChange.id);
            }}>Undo Last Log (within 10 min)</button>
          )}''')

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
