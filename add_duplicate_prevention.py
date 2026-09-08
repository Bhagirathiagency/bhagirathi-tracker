edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Prevent duplicate machine serials",
'''  const addMachine = () => {
    if (!serial.trim()) return;
    setMachines((prev) => [...prev, { id: uid(), serial: serial.trim(), model: model.trim() || "NPWT Unit" }]);
    setSerial(""); setModel(""); setShowForm(false);
  };''',
'''  const addMachine = () => {
    if (!serial.trim()) return;
    if (machines.some((m) => m.serial.trim().toLowerCase() === serial.trim().toLowerCase())) {
      alert(`A machine with serial "${serial.trim()}" already exists.`);
      return;
    }
    setMachines((prev) => [...prev, { id: uid(), serial: serial.trim(), model: model.trim() || "NPWT Unit" }]);
    setSerial(""); setModel(""); setShowForm(false);
  };''')

apply("Fix case-insensitive duplicate product check",
'''  const addProduct = () => {
    if (!name.trim() || !initCompany.trim() || products.some((p) => p.name === name.trim())) return;''',
'''  const addProduct = () => {
    if (!name.trim() || !initCompany.trim()) return;
    if (products.some((p) => p.name.trim().toLowerCase() === name.trim().toLowerCase())) {
      alert(`A product named "${name.trim()}" already exists. Use the existing one instead of adding a duplicate.`);
      return;
    }''')

apply("Add duplicateProducts detection and merge function",
'''  const productMismatches = useMemo(() => {''',
'''  const duplicateProducts = useMemo(() => {
    const byName = {};
    products.forEach((p) => {
      const key = p.name.trim().toLowerCase();
      if (!byName[key]) byName[key] = [];
      byName[key].push(p);
    });
    return Object.values(byName).filter((group) => group.length > 1);
  }, [products]);
  const mergeDuplicateProducts = () => {
    const byName = {};
    products.forEach((p) => {
      const key = p.name.trim().toLowerCase();
      if (!byName[key]) byName[key] = [];
      byName[key].push(p);
    });
    const merged = [];
    Object.values(byName).forEach((group) => {
      if (group.length === 1) { merged.push(group[0]); return; }
      const base = group[0];
      const combined = group.reduce((acc, p) => ({
        ...acc,
        available: (acc.available || 0) + (p.available || 0),
        used: (acc.used || 0) + (p.used || 0),
        costPrice: acc.costPrice || p.costPrice || 0,
        mrp: acc.mrp || p.mrp || 0,
        receipts: [...(acc.receipts || []), ...(p.receipts || [])],
      }), { ...base, available: 0, used: 0, receipts: [] });
      merged.push(combined);
    });
    setProducts(merged);
  };

  const productMismatches = useMemo(() => {''')

apply("Add duplicate products warning UI",
'''  return (
    <div>
      {productMismatches.length > 0 && (''',
'''  return (
    <div>
      {duplicateProducts.length > 0 && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #FCE7E4", background: "#FFF7F5" }}>
          <div style={{ fontWeight: 700, color: "#E1483C", marginBottom: 6 }}>⚠️ Duplicate Products Found in Your List</div>
          <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
            The same product name appears more than once (often from typing it slightly differently, like different capitalization). Merging combines their stock counts into one clean entry.
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 12 }}>
            {duplicateProducts.map((group) => (
              <div key={group[0].id} style={{ fontSize: 13 }}>
                <strong>"{group[0].name}"</strong> — appears {group.length} times
              </div>
            ))}
          </div>
          <button style={{ ...styles.smallBtn, background: "#128577" }} onClick={mergeDuplicateProducts}>Merge Duplicate Products</button>
        </div>
      )}
      {productMismatches.length > 0 && (''')

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
