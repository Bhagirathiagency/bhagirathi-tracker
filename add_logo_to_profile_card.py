old = '''              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 20px" }}>
                <div style={{ fontSize: 22, fontWeight: 700, color: "#FFFFFF", letterSpacing: 0.5, textAlign: "center" }}>BHAGIRATHI AGENCY</div>
                <div style={{ fontSize: 11, fontWeight: 600, color: "#CFE8E3", letterSpacing: 1.5, textTransform: "uppercase", marginTop: 6, textAlign: "center" }}>Advanced Wound Care Service</div>
              </div>'''

new = '''              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 20px" }}>
                <img src="/bhagirathi-logo.png" alt={businessName} style={{ width: 44, height: 44, objectFit: "contain", background: "#FFFFFF", borderRadius: 12, padding: 4, marginBottom: 8 }} />
                <div style={{ fontSize: 22, fontWeight: 700, color: "#FFFFFF", letterSpacing: 0.5, textAlign: "center" }}>{businessName.toUpperCase()}</div>
                <div style={{ fontSize: 11, fontWeight: 600, color: "#CFE8E3", letterSpacing: 1.5, textTransform: "uppercase", marginTop: 6, textAlign: "center" }}>Advanced Wound Care Service</div>
              </div>'''

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
