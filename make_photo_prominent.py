old = '''            <div style={{ display: "flex", justifyContent: "center", marginTop: -64 }}>
              <img src={photo} alt={name} style={{ width: 128, height: 128, borderRadius: 30, objectFit: "cover", border: "5px solid #FFFFFF", boxShadow: "0 8px 22px rgba(15,61,56,0.35)", filter: "contrast(1.08) saturate(1.12) brightness(1.03)" }} />
            </div>'''

new = '''            <div style={{ display: "flex", justifyContent: "center", marginTop: -70, position: "relative", zIndex: 2 }}>
              <img src={photo} alt={name} style={{ width: 168, height: 168, borderRadius: 38, objectFit: "cover", border: "6px solid #FFFFFF", boxShadow: "0 10px 28px rgba(15,61,56,0.4)", filter: "contrast(1.08) saturate(1.12) brightness(1.03)" }} />
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
