with open('src/App.jsx', 'r') as f:
    content = f.read()

edits = []

old = '''function estimateProfit(c, products) {
  const lines = getCaseProductLines(c);
  const cost = lines.reduce((sum, line) => {
    const prod = products.find((p) => p.name === line.name);
    return sum + (prod ? Number(prod.costPrice || 0) * line.qty : 0);
  }, 0);

    return Number(c.totalAmount || 0) + Number(c.machineRentalAmount || 0) - cost - Number(c.doctorCommission || 0);
}'''
new = '''function estimateProfit(c, products) {
  const lines = getCaseProductLines(c);
  const cost = lines.reduce((sum, line) => {
    const prod = products.find((p) => p.name === line.name);
    return sum + (prod ? Number(prod.costPrice || 0) * line.qty : 0);
  }, 0);
  const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);

    return paid + Number(c.machineRentalAmount || 0) - cost - Number(c.doctorCommission || 0);
}'''
edits.append(("estimateProfit formula", old, new))

old = '''      tally[key].revenue += Number(c.totalAmount || 0);
      tally[key].rental += Number(c.machineRentalAmount || 0);'''
new = '''      const casePaid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
      tally[key].revenue += casePaid;
      tally[key].rental += Number(c.machineRentalAmount || 0);'''
edits.append(("pnlRows revenue -> collected", old, new))

color_pairs = [
    ('combined.profit >= 0 ? "#D9720A" : "#E1483C"', 'combined.profit >= 0 ? "#128577" : "#E1483C"'),
    ('b.profit >= 0 ? "#D9720A" : "#E1483C"', 'b.profit >= 0 ? "#128577" : "#E1483C"'),
    ('pnlTotals.profit >= 0 ? "#D9720A" : "#E1483C"', 'pnlTotals.profit >= 0 ? "#128577" : "#E1483C"'),
    ('r.profit >= 0 ? "#D9720A" : "#E1483C"', 'r.profit >= 0 ? "#128577" : "#E1483C"'),
    ('label="Outstanding" value={fmtMoney(outstandingTotal)} accent="#D98D2B"', 'label="Outstanding" value={fmtMoney(outstandingTotal)} accent="#E1483C"'),
]
for old_c, new_c in color_pairs:
    c = content.count(old_c)
    print("Color fix matches:", c)
    if c:
        content = content.replace(old_c, new_c)

for label, old_e, new_e in edits:
    c = content.count(old_e)
    print(label, "matches:", c)
    if c:
        content = content.replace(old_e, new_e, 1)

with open('src/App.jsx', 'w') as f:
    f.write(content)
print('DONE')
