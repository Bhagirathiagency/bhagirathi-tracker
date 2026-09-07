edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("My Profile", '<CollapsibleSection title="My Profile" defaultOpen={!profile || !profile.photo}>', '<CollapsibleSection title="My Profile">')
apply("Today's Visits (dresser)", '<CollapsibleSection title="Today\'s & Tomorrow\'s Visits" defaultOpen right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{myTodaysVisits.length}</span>}>', '<CollapsibleSection title="Today\'s & Tomorrow\'s Visits" right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{myTodaysVisits.length}</span>}>')
apply("Cases on Therapy", '<CollapsibleSection title="Cases on Therapy" defaultOpen>', '<CollapsibleSection title="Cases on Therapy">')
apply("Today's Visits (owner)", '<CollapsibleSection title="Today\'s & Tomorrow\'s Visits" defaultOpen right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{todaysVisits.length}</span>}>', '<CollapsibleSection title="Today\'s & Tomorrow\'s Visits" right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{todaysVisits.length}</span>}>')
apply("Recent Cases", '<CollapsibleSection title="Recent Cases" defaultOpen>', '<CollapsibleSection title="Recent Cases">')
apply("Profit & Loss", '<CollapsibleSection title="Profit & Loss Statement" defaultOpen right={<span style={{ fontSize: 12, fontWeight: 700, color: pnlTotals.profit >= 0 ? "#128577" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}</span>}>', '<CollapsibleSection title="Profit & Loss Statement" right={<span style={{ fontSize: 12, fontWeight: 700, color: pnlTotals.profit >= 0 ? "#128577" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}</span>}>')
apply("Doctor Commission", '<CollapsibleSection title="Doctor Commission" defaultOpen={doctorCommissionStats.length > 0}', '<CollapsibleSection title="Doctor Commission"')
apply("Doctor Call Report", '<CollapsibleSection title="Doctor Call Report" defaultOpen={(doctorCalls || []).length > 0}', '<CollapsibleSection title="Doctor Call Report"')
apply("Outstanding by Patient", '<CollapsibleSection title="Outstanding Payments by Patient" defaultOpen={outstandingByPatient.length > 0}>', '<CollapsibleSection title="Outstanding Payments by Patient">')
apply("Outstanding by Hospital", '<CollapsibleSection title="Outstanding by Hospital" defaultOpen={outstandingByHospital.length > 0}>', '<CollapsibleSection title="Outstanding by Hospital">')
apply("Overdue Dressing Changes", '<CollapsibleSection title="Overdue Dressing Changes" defaultOpen={overdueCasesList.length > 0}>', '<CollapsibleSection title="Overdue Dressing Changes">')

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
