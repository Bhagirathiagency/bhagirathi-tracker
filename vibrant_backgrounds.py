edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Vibrant gradient app background",
'''  app: { fontFamily: "'Inter', -apple-system, sans-serif", background: "#FBF6EC", minHeight: "100vh", color: "#182322", paddingBottom: 40 },''',
'''  app: { fontFamily: "'Inter', -apple-system, sans-serif", background: "linear-gradient(160deg, #E9F5F2 0%, #FBF6EC 35%, #FDF1E4 70%, #FBF6EC 100%)", minHeight: "100vh", color: "#182322", paddingBottom: 40 },''')

apply("Warmer nav button base",
'''  navBtn: { display: "inline-flex", alignItems: "center", gap: 6, border: "1px solid #E3E7E2", background: "#fff", color: "#5B6864", padding: "8px 14px", borderRadius: 20, fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap" },''',
'''  navBtn: { display: "inline-flex", alignItems: "center", gap: 6, border: "1px solid #E3E7E2", background: "linear-gradient(160deg, #FFFFFF 0%, #F3F8F6 100%)", color: "#5B6864", padding: "8px 14px", borderRadius: 20, fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap" },''')

apply("Add subtle gradient tint to report cards",
'''  reportCard: { textAlign: "left", border: "1px solid #E3E7E2", background: "#fff", borderRadius: 16, padding: "16px 14px", boxShadow: "0 1px 2px rgba(14,36,34,0.04), 0 8px 20px rgba(14,36,34,0.05)" },''',
'''  reportCard: { textAlign: "left", border: "1px solid #E3E7E2", background: "linear-gradient(160deg, #FFFFFF 0%, #F0F8F6 100%)", borderRadius: 16, padding: "16px 14px", boxShadow: "0 1px 2px rgba(14,36,34,0.04), 0 8px 20px rgba(14,36,34,0.05)" },''')

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
