old = '''  const switchBusiness = (id) => {
    if (id === businessId) return;
    try { localStorage.setItem("wca-active-business", id); } catch (e) { /* ignore */ }
    setRolePersisted(null);
    setLoaded(false);
    setBusinessId(id);
  };'''

new = '''  const switchBusiness = (id) => {
    if (id === businessId) return;
    try { localStorage.setItem("wca-active-business", id); } catch (e) { /* ignore */ }
    // Keep the current role/session — the switcher only ever offers businesses this
    // person already has access to, so there's no need to make them log in again.
    setLoaded(false);
    setBusinessId(id);
  };'''

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
