old = '''        <Field label="Doctor Name">
          <input style={styles.input} list="doctor-master-list" value={form.doctorName} onChange={(e) => set("doctorName", e.target.value)} />
          <datalist id="doctor-master-list">
            {(doctorsList || []).map((d) => <option key={d.id} value={d.name} />)}
          </datalist>
        </Field>
        <Field label="Doctor Commission (₹, optional)">
          <input type="number" style={styles.input} value={form.doctorCommission} onChange={(e) => set("doctorCommission", e.target.value)} placeholder="0 if none" />
        </Field>'''

new = '''        <Field label="Doctor Name & Commission (₹)">
          <div style={{ display: "flex", gap: 8 }}>
            <input style={{ ...styles.input, flex: 2 }} list="doctor-master-list" value={form.doctorName} onChange={(e) => set("doctorName", e.target.value)} placeholder="Doctor name" />
            <input type="number" style={{ ...styles.input, flex: 1 }} value={form.doctorCommission} onChange={(e) => set("doctorCommission", e.target.value)} placeholder="Commission" />
          </div>
          <datalist id="doctor-master-list">
            {(doctorsList || []).map((d) => <option key={d.id} value={d.name} />)}
          </datalist>
        </Field>'''

with open('src/App.jsx', 'r') as f:
    content = f.read()

c = content.count(old)
print("Match:", c)
if c == 1:
    content = content.replace(old, new, 1)
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("APPLIED_OK")
else:
    print("NO_MATCH_FILE_NOT_CHANGED")
