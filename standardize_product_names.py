edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add standardizeAllProductNames function",
'''  const fixProductNamesOnCases = () => {''',
'''  const stripPackSuffix = (name) => {
    let cleaned = (name || "").replace(/\\s*\\d+\\s*\\/?\\s*(pack|pk|case)s?\\b\\.?/gi, "");
    cleaned = cleaned.replace(/\\s*,\\s*$/, "");
    cleaned = cleaned.replace(/,\\s*,/g, ",");
    cleaned = cleaned.replace(/\\s{2,}/g, " ").trim();
    return cleaned;
  };
  const standardizeAllProductNames = () => {
    const renameMap = {};
    products.forEach((p) => {
      const clean = stripPackSuffix(p.name);
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

  const fixProductNamesOnCases = () => {''')

apply("Pass standardizeAllProductNames to StockTab (owner)",
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} />}''',
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} />}''')

apply("Pass standardizeAllProductNames to StockTab (dresser)",
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} />''',
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} />''')

apply("StockTab fn signature accepts standardizeAllProductNames",
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);''',
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases, standardizeAllProductNames }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);
  const [standardizeMsg, setStandardizeMsg] = useState(null);''')

apply("Add Standardize Product Names button UI",
'''  return (
    <div>
      {duplicateProducts.length > 0 && (''',
'''  return (
    <div>
      {standardizeAllProductNames && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #D9E4E0", background: "#F0F8F6" }}>
          <div style={{ fontWeight: 700, color: "#1B6B63", marginBottom: 6 }}>Standardize Product Names</div>
          <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
            Removes pack-size wording (like "5 Pack", "10 Pack", "5/pk", "10/case") from every product name in one go, so everything is named per single unit. Any cases that used the old pack-style names are automatically updated too, so cost and profit stay accurate.
          </div>
          <button style={{ ...styles.smallBtn, background: "#1B6B63" }} onClick={() => {
            const result = standardizeAllProductNames();
            if (result.renamedProducts === 0) setStandardizeMsg("No pack-size wording found — all product names are already clean.");
            else setStandardizeMsg(`Cleaned ${result.renamedProducts} product name${result.renamedProducts === 1 ? "" : "s"}, and updated ${result.renamedCases} case${result.renamedCases === 1 ? "" : "s"} that referenced the old names.`);
          }}>Remove Pack-Size Wording from All Products</button>
          {standardizeMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 8, fontWeight: 600 }}>✓ {standardizeMsg}</div>}
        </div>
      )}
      {duplicateProducts.length > 0 && (''')

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
