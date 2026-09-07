edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Colorful header banner for New Case form",
'''  return (
    <div>
      <SectionTitle>{initial ? "Edit Case" : "New Case"}</SectionTitle>
      <div style={styles.formGrid}>
        <Field label="Patient Name"><input style={styles.input} value={form.patientName} onChange={(e) => set("patientName", e.target.value)} /></Field>''',
'''  return (
    <div>
      <div style={{
        background: initial ? "linear-gradient(135deg, #3B5BA5 0%, #2A4380 100%)" : "linear-gradient(135deg, #1B6B63 0%, #0F3D38 100%)",
        borderRadius: 16, padding: "20px 22px", marginBottom: 18, color: "#FFFFFF",
      }}>
        <div style={{ fontSize: 20, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>
          {initial ? "✏️ Edit Case" : "🩹 New Patient Case"}
        </div>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.85)", marginTop: 4 }}>
          {initial ? "Update the details below and save your changes." : "Fill in the details to get a new patient started on therapy."}
        </div>
      </div>
      <div style={styles.formGrid}>
        <Field label="Patient Name"><input style={styles.input} value={form.patientName} onChange={(e) => set("patientName", e.target.value)} /></Field>''')

apply("Bolder save button",
'''      {formError && <div style={{ color: "#E1483C", fontSize: 13, fontWeight: 600, marginBottom: 10 }}>{formError}</div>}
      <div style={styles.formActions}>
        <button style={styles.secondaryBtn} onClick={onCancel}>Cancel</button>
        <button style={styles.primaryBtn} onClick={submit}>Save Case</button>
      </div>
    </div>
  );''',
'''      {formError && <div style={{ color: "#E1483C", fontSize: 13, fontWeight: 600, marginBottom: 10 }}>{formError}</div>}
      <div style={styles.formActions}>
        <button style={styles.secondaryBtn} onClick={onCancel}>Cancel</button>
        <button style={{ ...styles.primaryBtn, background: initial ? "linear-gradient(135deg, #3B5BA5, #2A4380)" : "linear-gradient(135deg, #1B6B63, #0F3D38)", fontSize: 15, boxShadow: "0 4px 14px rgba(27,107,99,0.3)" }} onClick={submit}>
          {initial ? "💾 Save Changes" : "✅ Save New Case"}
        </button>
      </div>
    </div>
  );''')

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
