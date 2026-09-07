old = '''        const stockAccess = dstock && typeof dstock === "object" ? { ...dstock } : {};
        if (businessId === "bhagirathi") {
          const devashish = (drs || []).find((n) => n.trim().toLowerCase() === "devashish");
          if (devashish && stockAccess[devashish] === undefined) stockAccess[devashish] = true;
        }
        setDresserStockAccessState(stockAccess);'''

new = '''        const stockAccess = dstock && typeof dstock === "object" ? { ...dstock } : {};
        if (businessId === "bhagirathi" || businessId === "leelavac") {
          const devashish = (drs || []).find((n) => n.trim().toLowerCase() === "devashish");
          if (devashish) stockAccess[devashish] = true;
        }
        setDresserStockAccessState(stockAccess);'''

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
