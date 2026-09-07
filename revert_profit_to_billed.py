edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Revert estimateProfit to billed amount",
'''function estimateProfit(c, products) {
  const lines = getCaseProductLines(c);
  const cost = lines.reduce((sum, line) => {
    const prod = products.find((p) => p.name === line.name);
    return sum + (prod ? Number(prod.costPrice || 0) * line.qty : 0);
  }, 0);
  const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);

    return paid + Number(c.machineRentalAmount || 0) - cost - Number(c.doctorCommission || 0);
}''',
'''function estimateProfit(c, products) {
  const lines = getCaseProductLines(c);
  const cost = lines.reduce((sum, line) => {
    const prod = products.find((p) => p.name === line.name);
    return sum + (prod ? Number(prod.costPrice || 0) * line.qty : 0);
  }, 0);

    return Number(c.totalAmount || 0) + Number(c.machineRentalAmount || 0) - cost - Number(c.doctorCommission || 0);
}''')

apply("Revert pnlRows to billed amount",
'''      const casePaid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
      tally[key].revenue += casePaid;
      tally[key].rental += Number(c.machineRentalAmount || 0);''',
'''      tally[key].revenue += Number(c.totalAmount || 0);
      tally[key].rental += Number(c.machineRentalAmount || 0);''')

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
