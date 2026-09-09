old = '''        <Field label="Application Date"><input type="date" style={styles.input} value={form.applicationDate} onChange={(e) => set("applicationDate", e.target.value)} /></Field>
        <Field label="Application Time"><input type="time" style={styles.input} value={form.applicationTime} onChange={(e) => set("applicationTime", e.target.value)} /></Field>'''

new = '''        <Field label="Application Date & Time">
          <div style={{ display: "flex", gap: 8 }}>
            <input type="date" style={{ ...styles.input, flex: 1 }} value={form.applicationDate} onChange={(e) => set("applicationDate", e.target.value)} />
            <input type="time" style={{ ...styles.input, flex: 1 }} value={form.applicationTime} onChange={(e) => set("applicationTime", e.target.value)} />
          </div>
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
