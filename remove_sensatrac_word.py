edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add removeSensaTRACFromNames function",
'''  const standardizeAllProductNames = () => {''',
'''  const removeWordFromAllProductNames = (word) => {
    const wordRegex = new RegExp(`\\\\b${word}\\\\b`, "gi");
    const renameMap = {};
    products.forEach((p) => {
      let clean = p.name.replace(wordRegex, "").replace(/\\s{2,}/g, " ").trim();
      clean = clean.replace(/^[-,]\\s*/, "").replace(/\\s*[-,]\\s*$/, "");
      if (clean && clean.toLowerCase() !== p.name.trim().toLowerCase()) {
        renameMap[p.name.trim().toLowerCase()] = clean;
      }
    });
    if (Object.keys(renameMap).length === 0) return { renamedProducts: 0, renamedCases: 0 };

    const renamed = products.map((p) => {
      const target = renameMap[p.name.trim().toLowerCase()];
      return target ? { ...p, name: target } : p;
    });
    const byName = {};
    renamed.forEach((p) => {
      const key = p.name.trim().toLowerCase();
      if (!byName[key]) byName[key] = [];
      byName[key].push(p);
    });
    const merged = [];
    Object.values(byName).forEach((group) => {
      if (group.length === 1) { merged.push(group[0]); return; }
      const combined = group.reduce((acc, p) => ({
        ...acc,
        available: (acc.available || 0) + (p.available || 0),
        used: (acc.used || 0) + (p.used || 0),
        costPrice: acc.costPrice || p.costPrice || 0,
        mrp: acc.mrp || p.mrp || 0,
        receipts: [...(acc.receipts || []), ...(p.receipts || [])],
      }), { ...group[0], available: 0, used: 0, receipts: [] });
      merged.push(combined);
    });
    setProducts(merged);

    let renamedCases = 0;
    setCases((prev) => prev.map((c) => {
      let changed = false;
      const fixLine = (line) => {
        const raw = typeof line === "string" ? line : line.name;
        const target = renameMap[(raw || "").trim().toLowerCase()];
        if (target && target !== raw) { changed = true; return typeof line === "string" ? target : { ...line, name: target }; }
        return line;
      };
      let newProducts = c.products;
      if (Array.isArray(c.products) && c.products.length) newProducts = c.products.map(fixLine);
      let newProduct = c.product;
      if (c.product) {
        const target = renameMap[(c.product || "").trim().toLowerCase()];
        if (target && target !== c.product) { newProduct = target; changed = true; }
      }
      if (changed) renamedCases++;
      return changed ? { ...c, products: newProducts, product: newProduct } : c;
    }));

    return { renamedProducts: Object.keys(renameMap).length, renamedCases };
  };
  const removeSensaTRACFromNames = () => removeWordFromAllProductNames("SensaTRAC");

  const standardizeAllProductNames = () => {''')

apply("Pass removeSensaTRACFromNames to StockTab (owner)",
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} applyCostFormula={applyCostFormula} />}''',
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} applyCostFormula={applyCostFormula} removeSensaTRACFromNames={removeSensaTRACFromNames} />}''')

apply("Pass removeSensaTRACFromNames to StockTab (dresser)",
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} applyCostFormula={applyCostFormula} />''',
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} applyCostFormula={applyCostFormula} removeSensaTRACFromNames={removeSensaTRACFromNames} />''')

apply("StockTab fn signature accepts removeSensaTRACFromNames",
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases, standardizeAllProductNames, applyCostFormula }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);
  const [standardizeMsg, setStandardizeMsg] = useState(null);
  const [costFormulaMsg, setCostFormulaMsg] = useState(null);''',
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases, standardizeAllProductNames, applyCostFormula, removeSensaTRACFromNames }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);
  const [standardizeMsg, setStandardizeMsg] = useState(null);
  const [costFormulaMsg, setCostFormulaMsg] = useState(null);
  const [sensaTracMsg, setSensaTracMsg] = useState(null);''')

apply("Add Remove SensaTRAC button UI",
'''      {standardizeAllProductNames && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #D9E4E0", background: "#F0F8F6" }}>
          <div style={{ fontWeight: 700, color: "#1B6B63", marginBottom: 6 }}>Standardize Product Names</div>''',
'''      {removeSensaTRACFromNames && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #D9E4E0", background: "#F0F8F6" }}>
          <div style={{ fontWeight: 700, color: "#1B6B63", marginBottom: 6 }}>Remove "SensaTRAC" from Product Names</div>
          <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
            Removes the word "SensaTRAC" from every product name in one go. Any cases that used the old names are automatically updated too, so cost and profit stay accurate.
          </div>
          <button style={{ ...styles.smallBtn, background: "#1B6B63" }} onClick={() => {
            const result = removeSensaTRACFromNames();
            if (result.renamedProducts === 0) setSensaTracMsg('No product names contain "SensaTRAC".');
            else setSensaTracMsg(`Cleaned ${result.renamedProducts} product name${result.renamedProducts === 1 ? "" : "s"}, and updated ${result.renamedCases} case${result.renamedCases === 1 ? "" : "s"} that referenced the old names.`);
          }}>Remove "SensaTRAC" from All Products</button>
          {sensaTracMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 8, fontWeight: 600 }}>✓ {sensaTracMsg}</div>}
        </div>
      )}
      {standardizeAllProductNames && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #D9E4E0", background: "#F0F8F6" }}>
          <div style={{ fontWeight: 700, color: "#1B6B63", marginBottom: 6 }}>Standardize Product Names</div>''')

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
