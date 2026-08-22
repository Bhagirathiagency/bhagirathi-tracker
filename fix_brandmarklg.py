path = "src/App.jsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

original = content

old = '''brandMarkLg: { width: 60, height: 60, borderRadius: 16, background: "linear-gradient(135deg, #1B6B63 0%, #16302E 100%)", color: "#F6F5F0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 26, margin: "60px auto 14px" },'''

new = '''brandMarkLg: { width: 64, height: 64, borderRadius: 14, objectFit: "contain", margin: "60px auto 14px", cursor: "pointer" },'''

if old in content:
    content = content.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("DONE: brandMarkLg style fixed for image display.")
else:
    print("WARNING: exact brandMarkLg line not found - no changes made. Paste the grep output for line 1384 and I'll adjust.")
