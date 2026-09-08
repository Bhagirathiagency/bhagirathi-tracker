edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add applyCostFormula function",
'''  const standardizeAllProductNames = () => {''',
'''  const COST_FORMULA_COMPANIES = ["solventum", "medskin solutions"];
  const applyCostFormula = () => {
    let updatedCount = 0;
    setProducts((prev) => prev.map((p) => {
      const company = productCompany(p).trim().toLowerCase();
      if (!COST_FORMULA_COMPANIES.includes(company)) return p;
      const mrp = Number(p.mrp || 0);
      if (mrp <= 0) return p;
      const newCost = Math.round(mrp * 0.6 * 1.05);
      if (newCost === Number(p.costPrice || 0)) return p;
      updatedCount++;
      return { ...p, costPrice: newCost };
    }));
    return updatedCount;
  };

  const standardizeAllProductNames = () => {''')

apply("Pass applyCostFormula to StockTab (owner)",
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} />}''',
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} applyCostFormula={applyCostFormula} />}''')

apply("Pass applyCostFormula to StockTab (dresser)",
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} />''',
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} standardizeAllProductNames={standardizeAllProductNames} applyCostFormula={applyCostFormula} />''')

apply("StockTab fn signature accepts applyCostFormula",
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases, standardizeAllProductNames }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);
  const [standardizeMsg, setStandardizeMsg] = useState(null);''',
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases, standardizeAllProductNames, applyCostFormula }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);
  const [standardizeMsg, setStandardizeMsg] = useState(null);
  const [costFormulaMsg, setCostFormulaMsg] = useState(null);''')

apply("Add Apply Cost Formula button UI",
'''  return (
    <div>
      {standardizeAllProductNames && (''',
'''  return (
    <div>
      {applyCostFormula && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #D9E4E0", background: "#F0F8F6" }}>
          <div style={{ fontWeight: 700, color: "#1B6B63", marginBottom: 6 }}>Apply Cost Formula — Solventum &amp; MedSkin Solutions</div>
          <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
            Sets each product's cost price to 63% of its MRP (MRP minus 40% trade discount, plus 5% added on that discounted price) — for every product from Solventum or MedSkin Solutions that has an MRP entered.
          </div>
          <button style={{ ...styles.smallBtn, background: "#1B6B63" }} onClick={() => {
            const updated = applyCostFormula();
            setCostFormulaMsg(updated === 0 ? "No changes needed — costs already match the formula, or no MRP entered yet." : `Updated cost price on ${updated} product${updated === 1 ? "" : "s"}.`);
          }}>Apply Cost Formula</button>
          {costFormulaMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 8, fontWeight: 600 }}>✓ {costFormulaMsg}</div>}
        </div>
      )}
      {standardizeAllProductNames && (''')

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
