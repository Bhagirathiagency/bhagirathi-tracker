edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Move Reports to front of nav array",
'''        {[["dashboard", "Command Center", "overview"], ["cases", "Cases", "cases"], ["challans", "Challans", "stock"], ["quotations", "Quotes", "quotes"], ["machines", "Machines", "machines"], ["stock", "Stock", "stock"], ["expenses", "Expenses", "reports"], ["dressers", "Dressers", "dressers"], ["doctors", "Doctors", "dressers"], ["reports", "Reports", "reports"], ["combined", "All Business", "overview"]].map(([key, label, icon]) => (''',
'''        {[["reports", "Reports", "reports"], ["dashboard", "Command Center", "overview"], ["cases", "Cases", "cases"], ["challans", "Challans", "stock"], ["quotations", "Quotes", "quotes"], ["machines", "Machines", "machines"], ["stock", "Stock", "stock"], ["expenses", "Expenses", "reports"], ["dressers", "Dressers", "dressers"], ["doctors", "Doctors", "dressers"], ["combined", "All Business", "overview"]].map(([key, label, icon]) => (''')

apply("Default landing tab is Reports",
'''  const [tab, setTab] = useState("dashboard");''',
'''  const [tab, setTab] = useState("reports");''')

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
