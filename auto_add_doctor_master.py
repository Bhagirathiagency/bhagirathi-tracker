edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Pass addDoctorMaster to DresserShell call",
'''          doctorCalls={doctorCalls} addDoctorCall={addDoctorCall}
          doctorsList={doctorsList}''',
'''          doctorCalls={doctorCalls} addDoctorCall={addDoctorCall}
          doctorsList={doctorsList} addDoctorMaster={addDoctorMaster}''')

apply("DresserShell fn signature",
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem, addPayment, capturePhoto, updateDresserLocation, quotations, saveQuotation, deleteQuotation, setQuotationStatus, doctorCalls, addDoctorCall, doctorsList,''',
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem, addPayment, capturePhoto, updateDresserLocation, quotations, saveQuotation, deleteQuotation, setQuotationStatus, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster,''')

apply("Pass addDoctorMaster to DoctorCallTab",
'''          <DoctorCallTab name={name} products={products} doctorCalls={doctorCalls} addDoctorCall={addDoctorCall} doctorsList={doctorsList}''',
'''          <DoctorCallTab name={name} products={products} doctorCalls={doctorCalls} addDoctorCall={addDoctorCall} doctorsList={doctorsList} addDoctorMaster={addDoctorMaster}''')

apply("DoctorCallTab fn signature",
'''function DoctorCallTab({ name, products, doctorCalls, addDoctorCall, doctorsList, discussionTopics, addDiscussionTopic, removeDiscussionTopic }) {''',
'''function DoctorCallTab({ name, products, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster, discussionTopics, addDiscussionTopic, removeDiscussionTopic }) {''')

apply("Auto-add doctor to master list on submit",
'''  const submit = () => {
    if (!doctorName.trim()) return;
    addDoctorCall({
      dresserName: name, doctorName: doctorName.trim(), doctorMobile: doctorMobile.trim(),
      speciality: speciality.trim(), products: selectedProducts, date, notes: notes.trim(),
    });
    setDoctorName(""); setDoctorMobile(""); setSpeciality(""); setSelectedProducts([]); setNotes("");
  };''',
'''  const submit = () => {
    if (!doctorName.trim()) return;
    addDoctorCall({
      dresserName: name, doctorName: doctorName.trim(), doctorMobile: doctorMobile.trim(),
      speciality: speciality.trim(), products: selectedProducts, date, notes: notes.trim(),
    });
    const alreadyKnown = (doctorsList || []).some((d) => d.name.trim().toLowerCase() === doctorName.trim().toLowerCase());
    if (!alreadyKnown && addDoctorMaster) {
      addDoctorMaster({ name: doctorName.trim(), mobile: doctorMobile.trim(), speciality: speciality.trim(), doctorClass: "B" });
    }
    setDoctorName(""); setDoctorMobile(""); setSpeciality(""); setSelectedProducts([]); setNotes("");
  };''')

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
