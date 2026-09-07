old = '''              const pieData = [
                { name: "Outstanding", value: outstandingTotal, color: "#E1483C" },
                { name: "Investment", value: overallInvestment, color: "#D98D2B" },
                { name: "Profit", value: Math.max(0, overallProfit), color: "#128577" },
              ].filter((d) => d.value > 0);'''
new = '''              const pieData = [
                { name: "Patient Outstanding", value: outstandingBySource.Patient.total, color: "#E1483C" },
                { name: "Hospital Outstanding", value: outstandingBySource.Hospital.total, color: "#B3542F" },
                { name: "Investment", value: overallInvestment, color: "#D98D2B" },
                { name: "Profit", value: Math.max(0, overallProfit), color: "#128577" },
              ].filter((d) => d.value > 0);'''

with open('src/App.jsx', 'r') as f:
    content = f.read()

c = content.count(old)
print("Match:", c)
if c == 1:
    content = content.replace(old, new, 1)
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("APPLIED_OK")
else:
    print("NO_MATCH_FILE_NOT_CHANGED")
