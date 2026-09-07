edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Filter Patient list to exclude Hospital-billed cases",
'''  const outstandingByPatient = useMemo(() => {
    return cases
      .map((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        const balance = Math.max(0, Number(c.totalAmount || 0) - paid);
        const daysOutstanding = c.applicationDate ? daysBetween(c.applicationDate, todayISO()) : 0;
        return { ...c, balance, daysOutstanding };
      })
      .filter((c) => c.balance > 0)
      .sort((a, b) => b.daysOutstanding - a.daysOutstanding || b.balance - a.balance);
  }, [cases]);''',
'''  const outstandingByPatient = useMemo(() => {
    return cases
      .filter((c) => c.billTo !== "Hospital")
      .map((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        const balance = Math.max(0, Number(c.totalAmount || 0) - paid);
        const daysOutstanding = c.applicationDate ? daysBetween(c.applicationDate, todayISO()) : 0;
        return { ...c, balance, daysOutstanding };
      })
      .filter((c) => c.balance > 0)
      .sort((a, b) => b.daysOutstanding - a.daysOutstanding || b.balance - a.balance);
  }, [cases]);
  const outstandingByPatientForHospitalGrouping = useMemo(() => {
    return cases
      .map((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        const balance = Math.max(0, Number(c.totalAmount || 0) - paid);
        const daysOutstanding = c.applicationDate ? daysBetween(c.applicationDate, todayISO()) : 0;
        return { ...c, balance, daysOutstanding };
      })
      .filter((c) => c.balance > 0)
      .sort((a, b) => b.daysOutstanding - a.daysOutstanding || b.balance - a.balance);
  }, [cases]);''')

apply("Hospital grouping uses unfiltered source",
'''  const outstandingByHospital = useMemo(() => {
    const tally = {};
    outstandingByPatient
      .filter((c) => c.billTo === "Hospital")
      .forEach((c) => {''',
'''  const outstandingByHospital = useMemo(() => {
    const tally = {};
    outstandingByPatientForHospitalGrouping
      .filter((c) => c.billTo === "Hospital")
      .forEach((c) => {''')

apply("Dependency array update",
'''  }, [outstandingByPatient]);''',
'''  }, [outstandingByPatientForHospitalGrouping]);''')

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
