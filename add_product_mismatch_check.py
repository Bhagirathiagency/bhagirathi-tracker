edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Pass cases to StockTab (Owner nav)",
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} />}''',
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} />}''')

apply("Pass cases to StockTab (Dresser view)",
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} />''',
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} />''')

apply("StockTab fn signature and mismatch detection",
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId }) {''',
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [] }) {
  const productMismatches = useMemo(() => {
    const knownNames = new Set(products.map((p) => p.name.trim().toLowerCase()));
    const found = {};
    cases.forEach((c) => {
      getCaseProductLines(c).forEach((line) => {
        const raw = (line.name || "").trim();
        if (!raw) return;
        if (!knownNames.has(raw.toLowerCase())) {
          if (!found[raw]) found[raw] = { count: 0, patients: [] };
          found[raw].count++;
          if (found[raw].patients.length < 5) found[raw].patients.push(c.patientName);
        }
      });
    });
    return Object.entries(found).map(([name, data]) => ({ name, ...data })).sort((a, b) => b.count - a.count);
  }, [cases, products]);''')

apply("Add product mismatch warning UI",
'''  return (
    <div>
      {packDupCount > 0 && (''',
'''  return (
    <div>
      {productMismatches.length > 0 && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #FCE7E4", background: "#FFF7F5" }}>
          <div style={{ fontWeight: 700, color: "#E1483C", marginBottom: 6 }}>⚠️ Product Name Mismatch Found — Profit May Be Wrong</div>
          <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
            These product names appear on cases but don't exactly match anything in your current product list below. Since profit is calculated using each product's saved cost price, any case using one of these unmatched names is being counted with ₹0 cost — overstating that case's profit. This usually happens when a product was renamed after cases were already created using the old name.
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {productMismatches.map((m) => (
              <div key={m.name} style={{ fontSize: 13 }}>
                <strong>"{m.name}"</strong> — used in {m.count} case{m.count > 1 ? "s" : ""} ({m.patients.join(", ")}{m.count > m.patients.length ? "…" : ""})
              </div>
            ))}
          </div>
        </div>
      )}
      {packDupCount > 0 && (''')

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
