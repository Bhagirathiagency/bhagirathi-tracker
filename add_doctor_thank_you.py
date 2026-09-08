edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add sendDoctorThankYou helper",
'''function waLink(number, text) { return `https://wa.me/${number}?text=${encodeURIComponent(text)}`; }''',
'''function waLink(number, text) { return `https://wa.me/${number}?text=${encodeURIComponent(text)}`; }

function sendDoctorThankYou(caseData, doctorsList, businessName) {
  const doctorName = (caseData.doctorName || "").trim();
  if (!doctorName) return;
  const matchedDoctor = (doctorsList || []).find((d) => (d.name || "").trim().toLowerCase() === doctorName.toLowerCase());
  const doctorMobile = matchedDoctor ? matchedDoctor.mobile : "";
  if (!doctorMobile) return;
  const openers = [
    `Dear Dr. ${doctorName},`,
    `Respected Dr. ${doctorName},`,
  ];
  const opener = openers[Math.floor(Math.random() * openers.length)];
  const msg = `${opener}\\n\\nThank you for trusting ${businessName} with the care of your patient, ${caseData.patientName}. We deeply appreciate your continued confidence in our wound care services, and we're committed to giving your patient the best possible care throughout their therapy.\\n\\nWe'll keep you updated on their progress.\\n\\nWith gratitude and respect,\\n${businessName}`;
  window.open(waLink(`91${doctorMobile.replace(/\\D/g, "").slice(-10)}`, msg), "_blank");
}''')

apply("Trigger thank-you on dresser's new case save",
'''        onSave={(data) => { saveCase(data, editingCase ? editingCase.id : null); setShowForm(false); setEditingCase(null); setSavedConfirm(true); }} />''',
'''        onSave={(data) => {
          saveCase(data, editingCase ? editingCase.id : null);
          if (!editingCase) sendDoctorThankYou(data, doctorsList, business.name);
          setShowForm(false); setEditingCase(null); setSavedConfirm(true);
        }} />''')

apply("Trigger thank-you on owner's new case save",
'''        onSave={(data) => { saveCase(data, editing ? editing.id : null); setShowForm(false); setEditing(null); }} />''',
'''        onSave={(data) => {
          saveCase(data, editing ? editing.id : null);
          if (!editing) sendDoctorThankYou(data, doctorsList, businessName);
          setShowForm(false); setEditing(null);
        }} />''')

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
