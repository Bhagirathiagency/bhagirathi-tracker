edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Make discount percentage-based in quoteTotals",
'''function quoteTotals(q) {
  const items = q.items || [];
  const subtotal = items.reduce((s, it) => s + Number(it.qty || 0) * Number(it.rate || 0), 0);
  const discount = Number(q.discount || 0);
  const taxable = Math.max(0, subtotal - discount);
  const gstAmount = (taxable * Number(q.gstPercent || 0)) / 100;
  const total = taxable + gstAmount;
  return { subtotal, discount, taxable, gstAmount, total };
}''',
'''function quoteTotals(q) {
  const items = q.items || [];
  const subtotal = items.reduce((s, it) => s + Number(it.qty || 0) * Number(it.rate || 0), 0);
  const discountPercent = Number(q.discount || 0);
  const discount = subtotal * (discountPercent / 100);
  const taxable = Math.max(0, subtotal - discount);
  const gstAmount = (taxable * Number(q.gstPercent || 0)) / 100;
  const total = taxable + gstAmount;
  return { subtotal, discount, discountPercent, taxable, gstAmount, total };
}''')

apply("Update discount input to show percentage",
'''          <div style={styles.field}><span style={styles.fieldLabel}>Discount (₹)</span>
            <input style={styles.input} type="number" value={form.discount} onChange={(e) => set("discount", e.target.value)} /></div>''',
'''          <div style={styles.field}><span style={styles.fieldLabel}>Discount (%)</span>
            <input style={styles.input} type="number" min="0" max="100" value={form.discount} onChange={(e) => set("discount", e.target.value)} /></div>''')

apply("Show discount percent in quote form summary",
'''          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}><span>After discount</span><span>{fmtMoney(taxable)}</span></div>''',
'''          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}><span>Discount ({Number(form.discount) || 0}%)</span><span>-{fmtMoney(discount)}</span></div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}><span>After discount</span><span>{fmtMoney(taxable)}</span></div>''')

apply("Show discount percent on printed quotation",
'''          {discount > 0 && <div style={{ display: "flex", justifyContent: "space-between" }}><span>Discount</span><span>-{fmtMoney(discount)}</span></div>}''',
'''          {discount > 0 && <div style={{ display: "flex", justifyContent: "space-between" }}><span>Discount ({q.discount || 0}%)</span><span>-{fmtMoney(discount)}</span></div>}''')

apply("Add A4 page size and print color settings",
'''const printStyles = `
@media print {
  header, nav, .no-print { display: none !important; }
  body, .app-root { background: #fff !important; }
  main { max-width: 100% !important; padding: 0 !important; }
}
`;''',
'''const printStyles = `
@media print {
  @page { size: A4; margin: 12mm; }
  header, nav, .no-print { display: none !important; }
  body, .app-root { background: #fff !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  main { max-width: 100% !important; padding: 0 !important; }
  * { box-shadow: none !important; }
}
`;''')

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
