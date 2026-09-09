edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Remove Bill To and Hospital Name from current position",
'''        <Field label="Bill To">
          <select style={styles.input} value={form.billTo} onChange={(e) => set("billTo", e.target.value)}>
            <option value="Patient">Patient</option>
            <option value="Hospital">Hospital</option>
          </select>
        </Field>
        {form.billTo === "Hospital" && (
          <Field label="Hospital Name"><input style={styles.input} value={form.hospitalName} onChange={(e) => set("hospitalName", e.target.value)} /></Field>
        )}
        <Field label="Total Amount & Amount Received (₹)">''',
'''        <Field label="Total Amount & Amount Received (₹)">''')

apply("Insert Bill To and Hospital Name as 3rd field",
'''        <Field label="Machine Serial No.">
          <select style={styles.input} value={form.machineSerial} onChange={(e) => {
            const val = e.target.value;
            set("machineSerial", val);
            if (!val) set("status", "na");
            else if (form.status === "na") set("status", "active");
          }}>
            <option value="">— None —</option>
            {machines.map((m) => (
              <option key={m.id} value={m.serial} disabled={inUseSerials.has(m.serial)}>
                {m.serial} ({m.model}){inUseSerials.has(m.serial) ? " — In Use" : ""}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Patient Name & Mobile Number *">''',
'''        <Field label="Machine Serial No.">
          <select style={styles.input} value={form.machineSerial} onChange={(e) => {
            const val = e.target.value;
            set("machineSerial", val);
            if (!val) set("status", "na");
            else if (form.status === "na") set("status", "active");
          }}>
            <option value="">— None —</option>
            {machines.map((m) => (
              <option key={m.id} value={m.serial} disabled={inUseSerials.has(m.serial)}>
                {m.serial} ({m.model}){inUseSerials.has(m.serial) ? " — In Use" : ""}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Bill To">
          <select style={styles.input} value={form.billTo} onChange={(e) => set("billTo", e.target.value)}>
            <option value="Patient">Patient</option>
            <option value="Hospital">Hospital</option>
          </select>
        </Field>
        {form.billTo === "Hospital" && (
          <Field label="Hospital Name"><input style={styles.input} value={form.hospitalName} onChange={(e) => set("hospitalName", e.target.value)} /></Field>
        )}
        <Field label="Patient Name & Mobile Number *">''')

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
