edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Fix machineInUse to include reapplied status",
'''  const machineInUse = (serial) => cases.some((c) => c.machineSerial === serial && c.status === "active");''',
'''  const machineInUse = (serial) => cases.some((c) => c.machineSerial === serial && (c.status === "active" || c.status === "reapplied"));''')

apply("Pass cases to dresser CaseForm",
'''      <CaseForm machines={machines} products={products} presetDresserName={name} doctorsList={doctorsList}
        onCancel={() => setShowForm(false)}
        onSave={(data) => { saveCase(data, null); setShowForm(false); setSavedConfirm(true); }} />''',
'''      <CaseForm machines={machines} products={products} presetDresserName={name} doctorsList={doctorsList} cases={cases}
        onCancel={() => setShowForm(false)}
        onSave={(data) => { saveCase(data, null); setShowForm(false); setSavedConfirm(true); }} />''')

apply("Pass cases to owner CaseForm",
'''      <CaseForm machines={machines} products={products} initial={editing} doctorsList={doctorsList}
        onCancel={() => { setShowForm(false); setEditing(null); }}
        onSave={(data) => { saveCase(data, editing ? editing.id : null); setShowForm(false); setEditing(null); }} />''',
'''      <CaseForm machines={machines} products={products} initial={editing} doctorsList={doctorsList} cases={cases}
        onCancel={() => { setShowForm(false); setEditing(null); }}
        onSave={(data) => { saveCase(data, editing ? editing.id : null); setShowForm(false); setEditing(null); }} />''')

apply("CaseForm fn signature and in-use computation",
'''function CaseForm({ machines, products, initial, onCancel, onSave, presetDresserName, doctorsList }) {''',
'''function CaseForm({ machines, products, initial, onCancel, onSave, presetDresserName, doctorsList, cases = [] }) {
  const inUseSerials = new Set(
    cases
      .filter((c) => (c.status === "active" || c.status === "reapplied") && (!initial || c.id !== initial.id))
      .map((c) => c.machineSerial)
      .filter(Boolean)
  );''')

apply("Disable in-use machines in dropdown",
'''            <option value="">— None —</option>
            {machines.map((m) => <option key={m.id} value={m.serial}>{m.serial} ({m.model})</option>)}
          </select>
        </Field>''',
'''            <option value="">— None —</option>
            {machines.map((m) => (
              <option key={m.id} value={m.serial} disabled={inUseSerials.has(m.serial)}>
                {m.serial} ({m.model}){inUseSerials.has(m.serial) ? " — In Use" : ""}
              </option>
            ))}
          </select>
        </Field>''')

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
