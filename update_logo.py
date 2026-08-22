import re

path = "src/App.jsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

original = content
changes = []

# 1. Replace canvas-generated favicon with the real logo file
old_favicon = '''  useEffect(() => {
    document.title = "Bhagirathi Agency";
    try {
      const canvas = document.createElement("canvas");
      canvas.width = 180; canvas.height = 180;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#1B6B63";
      ctx.fillRect(0, 0, 180, 180);
      ctx.fillStyle = "#F6F5F0";
      ctx.font = "bold 100px 'Space Grotesk', sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("B", 90, 98);
      const dataUrl = canvas.toDataURL("image/png");
      [
        { rel: "icon", sizes: "180x180" },
        { rel: "apple-touch-icon", sizes: "180x180" },
        { rel: "shortcut icon" },
      ].forEach(({ rel, sizes }) => {
        let link = document.querySelector(`link[rel="${rel}"]`);
        if (!link) { link = document.createElement("link"); link.rel = rel; document.head.appendChild(link); }
        if (sizes) link.sizes = sizes;
        link.href = dataUrl;
      });
    } catch (e) { /* icon injection best-effort only */ }
  }, []);'''

new_favicon = '''  useEffect(() => {
    document.title = "Bhagirathi Agency";
    try {
      const dataUrl = "/bhagirathi-logo.png";
      [
        { rel: "icon", sizes: "180x180" },
        { rel: "apple-touch-icon", sizes: "180x180" },
        { rel: "shortcut icon" },
      ].forEach(({ rel, sizes }) => {
        let link = document.querySelector(`link[rel="${rel}"]`);
        if (!link) { link = document.createElement("link"); link.rel = rel; document.head.appendChild(link); }
        if (sizes) link.sizes = sizes;
        link.href = dataUrl;
      });
    } catch (e) { /* icon injection best-effort only */ }
  }, []);'''

if old_favicon in content:
    content = content.replace(old_favicon, new_favicon, 1)
    changes.append("Favicon (browser tab icon)")
else:
    print("WARNING: favicon block not found - skipped")

# 2. Login screen big logo mark
old_gate = '<div style={styles.brandMarkLg} onClick={handleLogoTap}>B</div>'
new_gate = '<img src="/bhagirathi-logo.png" alt="Bhagirathi Agency" style={styles.brandMarkLg} onClick={handleLogoTap} />'
if old_gate in content:
    content = content.replace(old_gate, new_gate, 1)
    changes.append("Login screen logo")
else:
    print("WARNING: login screen logo line not found - skipped")

# 3. Owner header logo (identified by surrounding "Owner view" text)
old_owner = '''          <div style={styles.brandMark}>B</div>
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>Bhagirathi Agency</div>
            <div style={styles.brandSub}>Owner view</div>'''
new_owner = '''          <div style={styles.brandMark}><img src="/bhagirathi-logo.png" alt="Bhagirathi Agency" style={styles.brandMarkImg} /></div>
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>Bhagirathi Agency</div>
            <div style={styles.brandSub}>Owner view</div>'''
if old_owner in content:
    content = content.replace(old_owner, new_owner, 1)
    changes.append("Owner header logo")
else:
    print("WARNING: owner header logo block not found - skipped")

# 4. Dresser header logo (identified by surrounding "Hi, {name}" text)
old_dresser = '''          <div style={styles.brandMark}>B</div>
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>Bhagirathi Agency</div>
            <div style={styles.brandSub}>Hi, {name}</div>'''
new_dresser = '''          <div style={styles.brandMark}><img src="/bhagirathi-logo.png" alt="Bhagirathi Agency" style={styles.brandMarkImg} /></div>
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>Bhagirathi Agency</div>
            <div style={styles.brandSub}>Hi, {name}</div>'''
if old_dresser in content:
    content = content.replace(old_dresser, new_dresser, 1)
    changes.append("Dresser header logo")
else:
    print("WARNING: dresser header logo block not found - skipped")

# 5. Update styles: brandMark becomes an image container, brandMarkLg becomes plain sizing, add brandMarkImg
old_style_mark = 'brandMark: { width: 38, height: 38, borderRadius: 10, background: "#1B6B63", color: "#F6F5F0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "\\'Space Grotesk\\', sans-serif", fontWeight: 700, fontSize: 18 },'
new_style_mark = 'brandMark: { width: 38, height: 38, borderRadius: 10, background: "#fff", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" },\n  brandMarkImg: { width: "82%", height: "82%", objectFit: "contain" },'
if old_style_mark in content:
    content = content.replace(old_style_mark, new_style_mark, 1)
    changes.append("brandMark style updated")
else:
    print("WARNING: brandMark style line not found - skipped")

old_style_marklg = 'brandMarkLg: { width: 56, height: 56, borderRadius: 14, background: "#1B6B63", color: "#F6F5F0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "\\'Space Grotesk\\', sans-serif", fontWeight: 700, fontSize: 26, margin: "60px auto 14px" },'
new_style_marklg = 'brandMarkLg: { width: 64, height: 64, borderRadius: 14, objectFit: "contain", margin: "60px auto 14px", cursor: "pointer" },'
if old_style_marklg in content:
    content = content.replace(old_style_marklg, new_style_marklg, 1)
    changes.append("brandMarkLg style updated")
else:
    print("WARNING: brandMarkLg style line not found - skipped")

if content != original:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("\nDONE. Applied changes:")
    for c in changes:
        print(" -", c)
else:
    print("\nNo changes were applied. Nothing matched - file may differ from expected.")
