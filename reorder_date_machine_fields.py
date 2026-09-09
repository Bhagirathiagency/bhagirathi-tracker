edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Remove Date & Time from current position",
'''        <Field label="Application Date & Time">
          <div style={{ display: "flex", gap: 8 }}>
            <input type="date" style={{ ...styles.input, flex: 1 }} value={form.applicationDate} onChange={(e) => set("applicationDate", e.target.value)} />
            <input type="time" style={{ ...styles.input, flex: 1 }} value={form.applicationTime} onChange={(e) => set("applicationTime", e.target.value)} />
          </div>
        </Field>
        <Field label="Status">''',
'''        <Field label="Status">''')

apply("Remove Machine Serial No from current position",
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
        {form.machineSerial && (
          <Field label="Machine Rental Amount (₹)">''',
'''        {form.machineSerial && (
          <Field label="Machine Rental Amount (₹)">''')

apply("Insert Date&Time and Machine Serial No at the top",
'''      <div style={styles.formGrid}>
        <Field label="Patient Name & Mobile Number *">''',
'''      <div style={styles.formGrid}>
        <Field label="Application Date & Time">
          <div style={{ display: "flex", gap: 8 }}>
            <input type="date" style={{ ...styles.input, flex: 1 }} value={form.applicationDate} onChange={(e) => set("applicationDate", e.target.value)} />
            <input type="time" style={{ ...styles.input, flex: 1 }} value={form.applicationTime} onChange={(e) => set("applicationTime", e.target.value)} />
          </div>
        </Field>
        <Field label="Machine Serial No.">
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
