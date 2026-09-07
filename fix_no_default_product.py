old = '''    patientName: "", patientMobile: "", doctorName: "", doctorCommission: "", dresserName: presetDresserName || "", protocolDays: 5,
       machineSerial: "", products: products[0] ? [{ name: products[0].name, qty: 1 }] : [],'''
new = '''    patientName: "", patientMobile: "", doctorName: "", doctorCommission: "", dresserName: presetDresserName || "", protocolDays: 5,
       machineSerial: "", products: [],'''

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
