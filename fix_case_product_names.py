edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add fixProductNamesOnCases function",
'''  const resetTestData = () => { setCases([]); setProducts([]); };''',
'''  const resetTestData = () => { setCases([]); setProducts([]); };
  const fixProductNamesOnCases = () => {
    let fixedCount = 0;
    setCases((prev) => prev.map((c) => {
      let changed = false;
      const fixLine = (line) => {
        const raw = typeof line === "string" ? line : line.name;
        const target = PACK_NAME_CLEANUP[(raw || "").trim().toLowerCase()];
        if (target && target !== raw) {
          changed = true;
          return typeof line === "string" ? target : { ...line, name: target };
        }
        return line;
      };
      let newProducts = c.products;
      if (Array.isArray(c.products) && c.products.length) {
        newProducts = c.products.map(fixLine);
      }
      let newProduct = c.product;
      if (c.product) {
        const target = PACK_NAME_CLEANUP[(c.product || "").trim().toLowerCase()];
        if (target && target !== c.product) { newProduct = target; changed = true; }
      }
      if (changed) fixedCount++;
      return changed ? { ...c, products: newProducts, product: newProduct } : c;
    }));
    return fixedCount;
  };''')

apply("Pass fixProductNamesOnCases to StockTab (owner)",
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} />}''',
'''        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} />}''')

apply("Pass fixProductNamesOnCases to StockTab (dresser)",
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} />''',
'''            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} businessId={businessId} cases={cases} fixProductNamesOnCases={fixProductNamesOnCases} />''')

apply("StockTab fn signature accepts fixProductNamesOnCases",
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [] }) {''',
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);''')

apply("Add Fix button to mismatch warning box",
'''          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {productMismatches.map((m) => (
              <div key={m.name} style={{ fontSize: 13 }}>
                <strong>"{m.name}"</strong> — used in {m.count} case{m.count > 1 ? "s" : ""} ({m.patients.join(", ")}{m.count > m.patients.length ? "…" : ""})
              </div>
            ))}
          </div>
        </div>
      )}''',
'''          <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 12 }}>
            {productMismatches.map((m) => (
              <div key={m.name} style={{ fontSize: 13 }}>
                <strong>"{m.name}"</strong> — used in {m.count} case{m.count > 1 ? "s" : ""} ({m.patients.join(", ")}{m.count > m.patients.length ? "…" : ""})
              </div>
            ))}
          </div>
          {fixProductNamesOnCases && (
            <button style={{ ...styles.smallBtn, background: "#128577" }} onClick={() => {
              const fixed = fixProductNamesOnCases();
              setFixedCasesMsg(`Updated ${fixed} case${fixed === 1 ? "" : "s"} to use the current product names. Profit will now recalculate correctly.`);
            }}>Fix Old Product Names on These Cases</button>
          )}
          {fixedCasesMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 8, fontWeight: 600 }}>✓ {fixedCasesMsg}</div>}
        </div>
      )}''')

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
