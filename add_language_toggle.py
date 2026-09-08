edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add TRANSLATIONS dictionary",
'''const BUSINESSES = [''',
'''const TRANSLATIONS = {
  en: {
    myProfile: "My Profile", todaysVisits: "Today's & Tomorrow's Visits", casesOnTherapy: "Cases on Therapy",
    patientHistory: "Patient History (Stopped / Reapplied)", yourReporting: "Your Reporting", myQuotations: "My Quotations",
    doctorCalls: "Doctor Calls", newCase: "+ New Case", callPatient: "Call Patient", callDoctor: "Call Dr.",
    logChange: "Log Today's Change", language: "Language",
  },
  hi: {
    myProfile: "मेरी प्रोफ़ाइल", todaysVisits: "आज और कल के विज़िट", casesOnTherapy: "थेरेपी पर मरीज़",
    patientHistory: "मरीज़ इतिहास (बंद / पुनः लागू)", yourReporting: "आपकी रिपोर्टिंग", myQuotations: "मेरे कोटेशन",
    doctorCalls: "डॉक्टर कॉल्स", newCase: "+ नया केस", callPatient: "मरीज़ को कॉल करें", callDoctor: "डॉ. को कॉल करें",
    logChange: "आज का बदलाव दर्ज करें", language: "भाषा",
  },
  mr: {
    myProfile: "माझी प्रोफाइल", todaysVisits: "आज आणि उद्याच्या भेटी", casesOnTherapy: "थेरपीवरील रुग्ण",
    patientHistory: "रुग्ण इतिहास (बंद / पुन्हा सुरू)", yourReporting: "तुमचा अहवाल", myQuotations: "माझी कोटेशन्स",
    doctorCalls: "डॉक्टर कॉल्स", newCase: "+ नवीन केस", callPatient: "रुग्णाला कॉल करा", callDoctor: "डॉ.ना कॉल करा",
    logChange: "आजचा बदल नोंदवा", language: "भाषा",
  },
};

const BUSINESSES = [''')

apply("Add language state and t() helper to DresserShell",
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, deleteDressingChange, addAdditionalItem, addPayment, capturePhoto, updateDresserLocation, quotations, saveQuotation, deleteQuotation, setQuotationStatus, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster, addPreviousOutstanding, discussionTopics, addDiscussionTopic, removeDiscussionTopic, profile, setDresserProfile, canManageStock, challans, createChallan, settleChallan, deleteChallan, business, businessId, businesses, myBusinesses, onSwitchBusiness, refreshData, refreshing, onLogout }) {
  const [showForm, setShowForm] = useState(false);''',
'''function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, deleteDressingChange, addAdditionalItem, addPayment, capturePhoto, updateDresserLocation, quotations, saveQuotation, deleteQuotation, setQuotationStatus, doctorCalls, addDoctorCall, doctorsList, addDoctorMaster, addPreviousOutstanding, discussionTopics, addDiscussionTopic, removeDiscussionTopic, profile, setDresserProfile, canManageStock, challans, createChallan, settleChallan, deleteChallan, business, businessId, businesses, myBusinesses, onSwitchBusiness, refreshData, refreshing, onLogout }) {
  const [lang, setLang] = useState(() => {
    try { return localStorage.getItem(`wca-lang-${name}`) || "en"; } catch (e) { return "en"; }
  });
  const t = (key) => (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) || TRANSLATIONS.en[key] || key;
  const changeLang = (newLang) => {
    setLang(newLang);
    try { localStorage.setItem(`wca-lang-${name}`, newLang); } catch (e) {}
  };
  const [showForm, setShowForm] = useState(false);''')

apply("Translate My Profile title + add language selector inside",
'''        <CollapsibleSection title="My Profile">''',
'''        <CollapsibleSection title={t("myProfile")}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
            <span style={{ ...styles.fieldLabel, marginBottom: 0 }}>{t("language")}:</span>
            <select value={lang} onChange={(e) => changeLang(e.target.value)} style={styles.smallInput}>
              <option value="en">English</option>
              <option value="hi">हिन्दी (Hindi)</option>
              <option value="mr">मराठी (Marathi)</option>
            </select>
          </div>''')

apply("Translate Today's Visits title",
'''          <CollapsibleSection title="Today's & Tomorrow's Visits" right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{myTodaysVisits.length}</span>}>''',
'''          <CollapsibleSection title={t("todaysVisits")} right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{myTodaysVisits.length}</span>}>''')

apply("Translate Cases on Therapy title",
'''        <CollapsibleSection title="Cases on Therapy">''',
'''        <CollapsibleSection title={t("casesOnTherapy")}>''')

apply("Translate Patient History title",
'''        <CollapsibleSection title="Patient History (Stopped / Reapplied)" right={myCasesHistory.length > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#8A9A96" }}>{myCasesHistory.length}</span> : null}>''',
'''        <CollapsibleSection title={t("patientHistory")} right={myCasesHistory.length > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#8A9A96" }}>{myCasesHistory.length}</span> : null}>''')

apply("Translate Your Reporting title",
'''        <CollapsibleSection title="Your Reporting">''',
'''        <CollapsibleSection title={t("yourReporting")}>''')

apply("Translate My Quotations title",
'''        <CollapsibleSection title="My Quotations">''',
'''        <CollapsibleSection title={t("myQuotations")}>''')

apply("Translate Doctor Calls title",
'''        <CollapsibleSection title="Doctor Calls">''',
'''        <CollapsibleSection title={t("doctorCalls")}>''')

apply("Translate dresser's New Case button",
'''        </CollapsibleSection>

        <button style={styles.primaryBtn} onClick={() => setShowForm(true)}>+ New Case</button>

        {myTodaysVisits.length > 0 && (''',
'''        </CollapsibleSection>

        <button style={styles.primaryBtn} onClick={() => setShowForm(true)}>{t("newCase")}</button>

        {myTodaysVisits.length > 0 && (''')

apply("Pass t to DresserCaseRow",
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} doctorsList={doctorsList} onAddPayment={(p) => addPayment(c.id, p)}''',
'''                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products} doctorsList={doctorsList} t={t} onAddPayment={(p) => addPayment(c.id, p)}''')

apply("DresserCaseRow fn signature accepts t",
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onUpdateStatus, onAddAdditionalItem, onAddPayment, onCapturePhoto, onEdit }) {''',
'''function DresserCaseRow({ c, dresserName, products, doctorsList, t = (k) => TRANSLATIONS.en[k] || k, onAddDressingChange, onDeleteDressingChange, onUpdateStatus, onAddAdditionalItem, onAddPayment, onCapturePhoto, onEdit }) {''')

apply("Translate Call Patient button",
'''                  <a href={`tel:${c.patientMobile}`} style={{ ...styles.smallBtn, textDecoration: "none", display: "inline-flex", alignItems: "center", background: "#128577" }}>📞 Call Patient</a>''',
'''                  <a href={`tel:${c.patientMobile}`} style={{ ...styles.smallBtn, textDecoration: "none", display: "inline-flex", alignItems: "center", background: "#128577" }}>📞 {t("callPatient")}</a>''')

apply("Translate Call Doctor button",
'''                  <a href={`tel:${doctorMobile}`} style={{ ...styles.smallBtn, textDecoration: "none", display: "inline-flex", alignItems: "center", background: "#3B5BA5" }}>📞 Call Dr. {c.doctorName}</a>''',
'''                  <a href={`tel:${doctorMobile}`} style={{ ...styles.smallBtn, textDecoration: "none", display: "inline-flex", alignItems: "center", background: "#3B5BA5" }}>📞 {t("callDoctor")} {c.doctorName}</a>''')

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
