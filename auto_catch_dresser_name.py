old = '''        <Field label="Dresser Name (applied by)"><input style={styles.input} value={form.dresserName} onChange={(e) => set("dresserName", e.target.value)} /></Field>'''

new = '''        {!presetDresserName && (
          <Field label="Dresser Name (applied by)"><input style={styles.input} value={form.dresserName} onChange={(e) => set("dresserName", e.target.value)} /></Field>
        )}'''

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
