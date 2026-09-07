edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add draft persistence to CaseForm",
'''function CaseForm({ machines, products, initial, onCancel, onSave, presetDresserName, doctorsList, cases = [] }) {
  const inUseSerials = new Set(
    cases
      .filter((c) => (c.status === "active" || c.status === "reapplied") && (!initial || c.id !== initial.id))
      .map((c) => c.machineSerial)
      .filter(Boolean)
  );
  const [form, setForm] = useState(initial || {
    patientName: "", patientMobile: "", doctorName: "", doctorCommission: "", dresserName: presetDresserName || "", protocolDays: 5,
       machineSerial: "", products: [],
    applicationDate: todayISO(), applicationTime: nowTimeHM(), status: "active", endDate: "",
    billTo: "Patient", hospitalName: "", totalAmount: "", amountReceived: "", machineRentalAmount: "", notes: "",
  });''',
'''function CaseForm({ machines, products, initial, onCancel, onSave, presetDresserName, doctorsList, cases = [] }) {
  const inUseSerials = new Set(
    cases
      .filter((c) => (c.status === "active" || c.status === "reapplied") && (!initial || c.id !== initial.id))
      .map((c) => c.machineSerial)
      .filter(Boolean)
  );
  const newCaseDraftKey = `wca-new-case-draft-${(presetDresserName || "owner").replace(/\\s+/g, "_")}`;
  const loadNewCaseDraft = () => {
    if (initial) return null; // never restore a draft over an existing case being edited
    try {
      const raw = localStorage.getItem(newCaseDraftKey);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  };
  const savedDraft = loadNewCaseDraft();
  const [form, setForm] = useState(initial || savedDraft || {
    patientName: "", patientMobile: "", doctorName: "", doctorCommission: "", dresserName: presetDresserName || "", protocolDays: 5,
       machineSerial: "", products: [],
    applicationDate: todayISO(), applicationTime: nowTimeHM(), status: "active", endDate: "",
    billTo: "Patient", hospitalName: "", totalAmount: "", amountReceived: "", machineRentalAmount: "", notes: "",
  });

  useEffect(() => {
    if (initial) return; // don't draft-save while editing an existing case
    const hasContent = form.patientName || form.patientMobile || form.doctorName;
    try {
      if (hasContent) localStorage.setItem(newCaseDraftKey, JSON.stringify(form));
      else localStorage.removeItem(newCaseDraftKey);
    } catch (e) {}
    // eslint-disable-next-line
  }, [form]);''')

apply("Clear new-case draft on submit",
'''    onSave({ ...form, products: cleanedProducts, totalAmount: Number(form.totalAmount) || 0, machineRentalAmount: Number(form.machineRentalAmount) || 0, doctorCommission: Number(form.doctorCommission) || 0, protocolDays: form.machineSerial ? (Number(form.protocolDays) || 5) : 0, status: form.machineSerial ? form.status : "na" });
  };''',
'''    try { localStorage.removeItem(newCaseDraftKey); } catch (e) {}
    onSave({ ...form, products: cleanedProducts, totalAmount: Number(form.totalAmount) || 0, machineRentalAmount: Number(form.machineRentalAmount) || 0, doctorCommission: Number(form.doctorCommission) || 0, protocolDays: form.machineSerial ? (Number(form.protocolDays) || 5) : 0, status: form.machineSerial ? form.status : "na" });
  };''')

apply("Add editing state in DresserShell",
'''  const [showForm, setShowForm] = useState(false);
  const [savedConfirm, setSavedConfirm] = useState(false);''',
'''  const [showForm, setShowForm] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [savedConfirm, setSavedConfirm] = useState(false);''')

apply("Wire up edit form in DresserShell",
'''  if (showForm) {
    return (
      <CaseForm machines={machines} products={products} presetDresserName={name} doctorsList={doctorsList} cases={cases}
        onCancel={() => setShowForm(false)}
        onSave={(data) => { saveCase(data, null); setShowForm(false); setSavedConfirm(true); }} />
    );
  }''',
'''  if (showForm) {
    return (
      <CaseForm machines={machines} products={products} initial={editingCase} presetDresserName={name} doctorsList={doctorsList} cases={cases}
        onCancel={() => { setShowForm(false); setEditingCase(null); }}
        onSave={(data) => { saveCase(data, editingCase ? editingCase.id : null); setShowForm(false); setEditingCase(null); setSavedConfirm(true); }} />
    );
  }''')

apply("Pass onEdit to DresserCaseRow",
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} doctorsList={doctorsList} onAddPayment={(p) => addPayment(c.id, p)}
                  onAddDressingChange={(e) => addDressingChange(c.id, e)}
                  onDeleteDressingChange={(changeId) => deleteDressingChange(c.id, changeId)}
                  onUpdateStatus={(status, endDate) => saveCase({ ...c, status, endDate }, c.id)}''',
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} doctorsList={doctorsList} onAddPayment={(p) => addPayment(c.id, p)}
                  onAddDressingChange={(e) => addDressingChange(c.id, e)}
                  onDeleteDressingChange={(changeId) => deleteDressingChange(c.id, changeId)}
                  onUpdateStatus={(status, endDate) => saveCase({ ...c, status, endDate }, c.id)}
                  onEdit={() => { setEditingCase(c); setShowForm(true); }}''')

apply("DresserCaseRow fn signature accepts onEdit",
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onUpdateStatus, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {''',
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onUpdateStatus, onAddAdditionalItem, onAddPayment, onCapturePhoto, onEdit }) {''')

apply("Add Edit Case Details button",
'''          {canUndoLast && onDeleteDressingChange && (
            <button style={{ ...styles.smallBtn, width: "100%", marginTop: 6, background: "#E1483C" }} onClick={() => {
              if (window.confirm("Undo your last logged change for this case?")) onDeleteDressingChange(lastMyChange.id);
            }}>Undo Last Log (within 10 min)</button>
          )}

          <AdditionalItemsBlock c={c} products={products} onAddAdditionalItem={onAddAdditionalItem} />''',
'''          {canUndoLast && onDeleteDressingChange && (
            <button style={{ ...styles.smallBtn, width: "100%", marginTop: 6, background: "#E1483C" }} onClick={() => {
              if (window.confirm("Undo your last logged change for this case?")) onDeleteDressingChange(lastMyChange.id);
            }}>Undo Last Log (within 10 min)</button>
          )}
          {onEdit && (
            <button style={{ ...styles.smallBtn, width: "100%", marginTop: 6, background: "#3B5BA5" }} onClick={onEdit}>
              ✏️ Fix / Edit Case Details
            </button>
          )}

          <AdditionalItemsBlock c={c} products={products} onAddAdditionalItem={onAddAdditionalItem} />''')

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
