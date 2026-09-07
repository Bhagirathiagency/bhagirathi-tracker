edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Persist role across app reloads",
'''  const [role, setRole] = useState(null);''',
'''  const [role, setRole] = useState(() => {
    try {
      const saved = localStorage.getItem("wca-session-role");
      return saved ? JSON.parse(saved) : null;
    } catch (e) { return null; }
  });
  const setRolePersisted = (r) => {
    setRole(r);
    try {
      if (r) localStorage.setItem("wca-session-role", JSON.stringify(r));
      else localStorage.removeItem("wca-session-role");
    } catch (e) {}
  };''')

apply("Owner login uses persisted setter",
'''          onOwnerLogin={() => { logOwnerLogin(); setRole({ type: "owner" }); }}
          onDresserLogin={(name) => { setRole({ type: "dresser", name }); updateDresserLocation(name); }}
          onAccountantLogin={() => setRole({ type: "accountant" })}''',
'''          onOwnerLogin={() => { logOwnerLogin(); setRolePersisted({ type: "owner" }); }}
          onDresserLogin={(name) => { setRolePersisted({ type: "dresser", name }); updateDresserLocation(name); }}
          onAccountantLogin={() => setRolePersisted({ type: "accountant" })}''')

apply("Business switch clears persisted session",
'''    try { localStorage.setItem("wca-active-business", id); } catch (e) { /* ignore */ }
    setRole(null);
    setLoaded(false);
    setBusinessId(id);''',
'''    try { localStorage.setItem("wca-active-business", id); } catch (e) { /* ignore */ }
    setRolePersisted(null);
    setLoaded(false);
    setBusinessId(id);''')

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

# Replace all logout handlers (3 occurrences)
logout_old = '''          onLogout={() => setRole(null)}'''
logout_new = '''          onLogout={() => setRolePersisted(null)}'''
logout_count = content.count(logout_old)
print("Logout handlers found:", logout_count)
if logout_count == 3:
    content = content.replace(logout_old, logout_new)
else:
    all_ok = False

if all_ok:
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("ALL_APPLIED_OK")
else:
    print("SOME_MISMATCHES_FILE_NOT_CHANGED")
