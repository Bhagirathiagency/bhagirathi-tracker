old = '''          <input type="file" accept="image/*" capture="user" style={{ display: "none" }} onChange={(e) => handlePhoto(e.target.files[0])} />'''
new = '''          <input type="file" accept="image/*" style={{ display: "none" }} onChange={(e) => handlePhoto(e.target.files[0])} />'''

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
