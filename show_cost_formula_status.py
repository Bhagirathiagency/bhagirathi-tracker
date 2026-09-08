edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add costFormulaProducts visibility computation",
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases, standardizeAllProductNames, applyCostFormula }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);
  const [standardizeMsg, setStandardizeMsg] = useState(null);
  const [costFormulaMsg, setCostFormulaMsg] = useState(null);''',
'''function StockTab({ products, setProducts, receiveStock, actorName = "Owner", businessId, cases = [], fixProductNamesOnCases, standardizeAllProductNames, applyCostFormula }) {
  const [fixedCasesMsg, setFixedCasesMsg] = useState(null);
  const [standardizeMsg, setStandardizeMsg] = useState(null);
  const [costFormulaMsg, setCostFormulaMsg] = useState(null);
  const costFormulaCompanies = ["solventum", "medskin solutions"];
  const costFormulaProducts = useMemo(() =>
    products.filter((p) => costFormulaCompanies.includes(productCompany(p).trim().toLowerCase())),
    [products]);
  const costFormulaMissingMrp = costFormulaProducts.filter((p) => !(Number(p.mrp) > 0));''')

apply("Add per-product MRP/Cost visibility list",
'''          <button style={{ ...styles.smallBtn, background: "#1B6B63" }} onClick={() => {
            const updated = applyCostFormula();
            setCostFormulaMsg(updated === 0 ? "No changes needed — costs already match the formula, or no MRP entered yet." : `Updated cost price on ${updated} product${updated === 1 ? "" : "s"}.`);
          }}>Apply Cost Formula</button>
          {costFormulaMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 8, fontWeight: 600 }}>✓ {costFormulaMsg}</div>}
        </div>
      )}''',
'''          <button style={{ ...styles.smallBtn, background: "#1B6B63" }} onClick={() => {
            const updated = applyCostFormula();
            setCostFormulaMsg(updated === 0 ? "No changes needed — costs already match the formula, or no MRP entered yet." : `Updated cost price on ${updated} product${updated === 1 ? "" : "s"}.`);
          }}>Apply Cost Formula</button>
          {costFormulaMsg && <div style={{ fontSize: 12, color: "#128577", marginTop: 8, fontWeight: 600 }}>✓ {costFormulaMsg}</div>}

          {costFormulaProducts.length > 0 && (
            <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid #D9E4E0" }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#5B6864", marginBottom: 8, textTransform: "uppercase", letterSpacing: 0.4 }}>
                {costFormulaProducts.length} Solventum/MedSkin product{costFormulaProducts.length === 1 ? "" : "s"} found
                {costFormulaMissingMrp.length > 0 ? ` — ${costFormulaMissingMrp.length} missing MRP` : " — all have MRP set"}
              </div>
              {costFormulaProducts.map((p) => (
                <div key={p.id} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, padding: "5px 0", borderBottom: "1px solid #EEF1EC" }}>
                  <span>{p.name}</span>
                  <span style={{ color: Number(p.mrp) > 0 ? "#5B6864" : "#E1483C", fontWeight: Number(p.mrp) > 0 ? 400 : 700 }}>
                    MRP: {Number(p.mrp) > 0 ? fmtMoney(p.mrp) : "Not set"} · Cost: {fmtMoney(p.costPrice)}
                  </span>
                </div>
              ))}
            </div>
          )}
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
