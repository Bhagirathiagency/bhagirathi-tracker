edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("productCompany prefers p.company",
'''function productCompany(p) {
  const receipts = p.receipts || [];
  if (!receipts.length) return "Unspecified";
  const latest = [...receipts].sort((a, b) => new Date(b.date) - new Date(a.date))[0];
  return (latest.company || "Unspecified").trim() || "Unspecified";
}''',
'''function productCompany(p) {
  if (p.company && p.company.trim()) return p.company.trim();
  const receipts = p.receipts || [];
  if (!receipts.length) return "Unspecified";
  const latest = [...receipts].sort((a, b) => new Date(b.date) - new Date(a.date))[0];
  return (latest.company || "Unspecified").trim() || "Unspecified";
}''')

apply("Add initCompany state",
'''  const [initMrp, setInitMrp] = useState("");''',
'''  const [initMrp, setInitMrp] = useState("");
  const [initCompany, setInitCompany] = useState("");''')

apply("addProduct requires + stores company",
'''  const addProduct = () => {
    if (!name.trim() || products.some((p) => p.name === name.trim())) return;
    const qty = Number(initQty) || 0;
    setProducts((prev) => [...prev, {
      id: uid(), name: name.trim(), available: qty, used: 0, costPrice: Number(initCost) || 0, mrp: Number(initMrp) || 0,
      receipts: qty > 0 ? [{ id: uid(), date: todayISO(), time: new Date().toLocaleTimeString("en-IN"), qty, company: "Unspecified", receivedBy: actorName }] : [],
      variants: [],
    }]);
    setName(""); setInitQty(""); setInitCost(""); setInitMrp("");
  };''',
'''  const addProduct = () => {
    if (!name.trim() || !initCompany.trim() || products.some((p) => p.name === name.trim())) return;
    const qty = Number(initQty) || 0;
    const co = initCompany.trim();
    setProducts((prev) => [...prev, {
      id: uid(), name: name.trim(), company: co, available: qty, used: 0, costPrice: Number(initCost) || 0, mrp: Number(initMrp) || 0,
      receipts: qty > 0 ? [{ id: uid(), date: todayISO(), time: new Date().toLocaleTimeString("en-IN"), qty, company: co, receivedBy: actorName }] : [],
      variants: [],
    }]);
    setName(""); setInitQty(""); setInitCost(""); setInitMrp(""); setInitCompany("");
  };
  const updateCompany = (id, company) => setProducts((prev) => prev.map((p) => p.id === id ? { ...p, company: (company || "").trim() } : p));''')

apply("Add Company input to form",
'''          <input style={{ ...styles.smallInput, flex: 1 }} placeholder="Product name" value={name} onChange={(e) => setName(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 70 }} type="number" placeholder="Qty" value={initQty} onChange={(e) => setInitQty(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 90 }} type="number" placeholder="Cost ₹" value={initCost} onChange={(e) => setInitCost(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 90 }} type="number" placeholder="MRP ₹" value={initMrp} onChange={(e) => setInitMrp(e.target.value)} />
        </div>
        <button style={styles.primaryBtn} onClick={addProduct}>Add Product</button>''',
'''          <input style={{ ...styles.smallInput, flex: 1 }} placeholder="Product name" value={name} onChange={(e) => setName(e.target.value)} />
          <input style={{ ...styles.smallInput, flex: 1 }} placeholder="Company / brand *" value={initCompany} onChange={(e) => setInitCompany(e.target.value)} />
        </div>
        <div style={styles.addPaymentRow}>
          <input style={{ ...styles.smallInput, width: 70 }} type="number" placeholder="Qty" value={initQty} onChange={(e) => setInitQty(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 90 }} type="number" placeholder="Cost ₹" value={initCost} onChange={(e) => setInitCost(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 90 }} type="number" placeholder="MRP ₹" value={initMrp} onChange={(e) => setInitMrp(e.target.value)} />
        </div>
        <button style={styles.primaryBtn} onClick={addProduct} disabled={!name.trim() || !initCompany.trim()}>Add Product</button>''')

apply("Editable Company field per product",
'''                        <div style={styles.addPaymentRow}>
                          <span style={styles.mutedSmall}>Cost price ₹</span>
                          <input type="number" style={styles.smallInput} defaultValue={p.costPrice || 0} onBlur={(e) => updateCost(p.id, e.target.value)} />
                          <span style={styles.mutedSmall}>MRP ₹</span>
                          <input type="number" style={styles.smallInput} defaultValue={p.mrp || 0} onBlur={(e) => updateMrp(p.id, e.target.value)} />
                        </div>''',
'''                        <div style={styles.addPaymentRow}>
                          <span style={styles.mutedSmall}>Company / brand</span>
                          <input type="text" style={{ ...styles.smallInput, flex: 1 }} defaultValue={p.company || ""} placeholder="Required" onBlur={(e) => updateCompany(p.id, e.target.value)} />
                        </div>
                        <div style={styles.addPaymentRow}>
                          <span style={styles.mutedSmall}>Cost price ₹</span>
                          <input type="number" style={styles.smallInput} defaultValue={p.costPrice || 0} onBlur={(e) => updateCost(p.id, e.target.value)} />
                          <span style={styles.mutedSmall}>MRP ₹</span>
                          <input type="number" style={styles.smallInput} defaultValue={p.mrp || 0} onBlur={(e) => updateMrp(p.id, e.target.value)} />
                        </div>''')

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
