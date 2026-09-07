old = '''        <div style={{ position: "fixed", left: -9999, top: 0 }}>
          <div ref={cardRef} style={{ width: 360, padding: 28, background: "linear-gradient(160deg, #E7F1EF 0%, #FFFFFF 60%)", fontFamily: "'Space Grotesk', sans-serif" }}>
            <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: 1, color: "#3B5BA5", textTransform: "uppercase", marginBottom: 4 }}>{businessName}</div>
            <div style={{ fontSize: 11, color: "#8A9A96", marginBottom: 18 }}>Wound Care Field Dresser</div>
            <div style={{ display: "flex", justifyContent: "center", marginBottom: 16 }}>
              <img src={photo} alt={name} style={{ width: 120, height: 120, borderRadius: 24, objectFit: "cover", border: "4px solid #FFFFFF", boxShadow: "0 6px 18px rgba(27,107,99,0.25)", filter: "contrast(1.08) saturate(1.12) brightness(1.03)" }} />
            </div>
            <div style={{ textAlign: "center", fontSize: 22, fontWeight: 700, color: "#0E2422", marginBottom: 4 }}>{name}</div>
            {phone && <div style={{ textAlign: "center", fontSize: 13, color: "#3B5BA5", fontWeight: 600, marginBottom: 10 }}>📞 {phone}</div>}
            {bio && <div style={{ textAlign: "center", fontSize: 12, color: "#5B6864", lineHeight: 1.5, padding: "0 8px" }}>{bio}</div>}
            <div style={{ marginTop: 22, paddingTop: 14, borderTop: "1px solid #D9E4E0", textAlign: "center", fontSize: 10, color: "#8A9A96" }}>Verified team member — {businessName}</div>
          </div>
        </div>
      )}'''

new = '''        <div style={{ position: "fixed", left: -9999, top: 0 }}>
          <div ref={cardRef} style={{ width: 380, background: "#FFFFFF", fontFamily: "'Space Grotesk', sans-serif" }}>
            <div style={{
              position: "relative", height: 190, overflow: "hidden",
              backgroundColor: "#1B6B63",
              backgroundImage: "linear-gradient(135deg, #0F3D38 0%, #1B6B63 55%, #3B5BA5 100%), url(\\"data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'60\\' height=\\'60\\'%3E%3Cg fill=\\'%23FFFFFF\\' fill-opacity=\\'0.08\\'%3E%3Crect x=\\'26\\' y=\\'14\\' width=\\'8\\' height=\\'32\\'/%3E%3Crect x=\\'14\\' y=\\'26\\' width=\\'32\\' height=\\'8\\'/%3E%3C/g%3E%3C/svg%3E\\")",
            }}>
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 20px" }}>
                <div style={{ fontSize: 22, fontWeight: 700, color: "#FFFFFF", letterSpacing: 0.5, textAlign: "center" }}>BHAGIRATHI AGENCY</div>
                <div style={{ fontSize: 11, fontWeight: 600, color: "#CFE8E3", letterSpacing: 1.5, textTransform: "uppercase", marginTop: 6, textAlign: "center" }}>Advanced Wound Care Service</div>
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "center", marginTop: -64 }}>
              <img src={photo} alt={name} style={{ width: 128, height: 128, borderRadius: 30, objectFit: "cover", border: "5px solid #FFFFFF", boxShadow: "0 8px 22px rgba(15,61,56,0.35)", filter: "contrast(1.08) saturate(1.12) brightness(1.03)" }} />
            </div>
            <div style={{ padding: "16px 28px 28px" }}>
              <div style={{ textAlign: "center", fontSize: 22, fontWeight: 700, color: "#0E2422", marginBottom: 2 }}>{name}</div>
              <div style={{ textAlign: "center", fontSize: 11, fontWeight: 600, color: "#8A9A96", textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 10 }}>Wound Care Field Dresser</div>
              {phone && <div style={{ textAlign: "center", fontSize: 13, color: "#3B5BA5", fontWeight: 600, marginBottom: 10 }}>📞 {phone}</div>}
              {bio && <div style={{ textAlign: "center", fontSize: 12, color: "#5B6864", lineHeight: 1.5, padding: "0 8px" }}>{bio}</div>}
              <div style={{ marginTop: 22, paddingTop: 14, borderTop: "1px solid #D9E4E0", textAlign: "center", fontSize: 10, color: "#8A9A96" }}>Verified team member — {businessName}</div>
            </div>
          </div>
        </div>
      )}'''

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
