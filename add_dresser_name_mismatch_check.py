edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Pass cases to DressersTab call",
'''        {tab === "dressers" && <DressersTab dressers={dressers} addDresser={addDresser} removeDresser={removeDresser} dresserPins={dresserPins} setDresserPin={setDresserPin} dresserStats={dresserStats} dresserProfiles={dresserProfiles} dresserStockAccess={dresserStockAccess} setDresserStockAccess={setDresserStockAccess} dresserBusinessAccess={dresserBusinessAccess} setDresserBusinessAccess={setDresserBusinessAccess} businesses={businesses} businessId={businessId} />}''',
'''        {tab === "dressers" && <DressersTab dressers={dressers} addDresser={addDresser} removeDresser={removeDresser} dresserPins={dresserPins} setDresserPin={setDresserPin} dresserStats={dresserStats} dresserProfiles={dresserProfiles} dresserStockAccess={dresserStockAccess} setDresserStockAccess={setDresserStockAccess} dresserBusinessAccess={dresserBusinessAccess} setDresserBusinessAccess={setDresserBusinessAccess} businesses={businesses} businessId={businessId} cases={cases} />}''')

apply("DressersTab fn signature and mismatch detection",
'''function DressersTab({ dressers, addDresser, removeDresser, dresserPins, setDresserPin, dresserStats, dresserProfiles, dresserStockAccess, setDresserStockAccess, dresserBusinessAccess, setDresserBusinessAccess, businesses, businessId }) {''',
'''function DressersTab({ dressers, addDresser, removeDresser, dresserPins, setDresserPin, dresserStats, dresserProfiles, dresserStockAccess, setDresserStockAccess, dresserBusinessAccess, setDresserBusinessAccess, businesses, businessId, cases = [] }) {
  const officialNames = new Set(dressers.map((d) => d.trim().toLowerCase()));
  const mismatchedNames = useMemo(() => {
    const found = {};
    cases.forEach((c) => {
      const raw = (c.dresserName || "").trim();
      if (!raw) return;
      if (!officialNames.has(raw.toLowerCase())) {
        found[raw] = (found[raw] || 0) + 1;
      }
    });
    return Object.entries(found).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
  }, [cases, dressers]);''')

apply("Add mismatch warning UI to DressersTab",
'''  return (
    <div>
      <SectionTitle>Add Dresser</SectionTitle>''',
'''  return (
    <div>
      {mismatchedNames.length > 0 && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #FCE7E4", background: "#FFF7F5" }}>
          <div style={{ fontWeight: 700, color: "#E1483C", marginBottom: 6 }}>⚠️ Dresser Name Spelling Mismatch Found</div>
          <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
            These names appear on cases but don't exactly match anyone in your official Dressers list below. Cases tagged like this won't show up as "due" in that dresser's app — likely a typo, extra space, or nickname used when the case was created. Edit those cases in the Cases tab to fix the spelling.
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {mismatchedNames.map((m) => (
              <div key={m.name} style={{ fontSize: 13 }}>
                <strong>"{m.name}"</strong> — {m.count} case{m.count > 1 ? "s" : ""}
              </div>
            ))}
          </div>
        </div>
      )}
      <SectionTitle>Add Dresser</SectionTitle>''')

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
