edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Persist and restore dressing-change draft",
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onUpdateStatus, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {
  const [open, setOpen] = useState(false);
  const [protocolDays, setProtocolDays] = useState(c.protocolDays || 5);
  const [note, setNote] = useState("");
  const [changeProducts, setChangeProducts] = useState([]);''',
'''function DresserCaseRow({ c, dresserName, products, doctorsList, onAddDressingChange, onDeleteDressingChange, onUpdateStatus, onAddAdditionalItem, onAddPayment, onCapturePhoto }) {
  const draftKey = `wca-draft-${c.id}`;
  const loadDraft = () => {
    try {
      const raw = localStorage.getItem(draftKey);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  };
  const draft = loadDraft();
  const [open, setOpen] = useState(false);
  const [protocolDays, setProtocolDays] = useState((draft && draft.protocolDays) || c.protocolDays || 5);
  const [note, setNote] = useState((draft && draft.note) || "");
  const [changeProducts, setChangeProducts] = useState((draft && draft.changeProducts) || []);

  useEffect(() => {
    if (note || (changeProducts && changeProducts.length)) {
      try { localStorage.setItem(draftKey, JSON.stringify({ note, protocolDays, changeProducts })); } catch (e) {}
    } else {
      try { localStorage.removeItem(draftKey); } catch (e) {}
    }
    // eslint-disable-next-line
  }, [note, protocolDays, changeProducts]);''')

apply("Clear draft on successful log",
'''            onAddDressingChange({ date: todayISO(), dresserName, protocolDays, note, products: changeProducts.filter((p) => Number(p.qty) > 0) });
            if (onUpdateStatus && therapyOutcome !== "continue") {
              onUpdateStatus(therapyOutcome, outcomeDate);
            }
            setNote(""); setChangeProducts([]); setTherapyOutcome("continue"); setOpen(false);''',
'''            onAddDressingChange({ date: todayISO(), dresserName, protocolDays, note, products: changeProducts.filter((p) => Number(p.qty) > 0) });
            if (onUpdateStatus && therapyOutcome !== "continue") {
              onUpdateStatus(therapyOutcome, outcomeDate);
            }
            try { localStorage.removeItem(draftKey); } catch (e) {}
            setNote(""); setChangeProducts([]); setTherapyOutcome("continue"); setOpen(false);''')

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
