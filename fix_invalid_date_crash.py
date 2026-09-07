edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Make addDays defensive against invalid dates",
'''const addDays = (dateStr, days) => {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + Number(days || 0));
  return d.toISOString().slice(0, 10);
};''',
'''const addDays = (dateStr, days) => {
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return null; // missing/invalid source date — don't crash, signal it clearly instead
  d.setDate(d.getDate() + Number(days || 0));
  return d.toISOString().slice(0, 10);
};''')

apply("nextDueDate shows fallback instead of crashing",
'''function nextDueDate(c) {
  const last = latestChange(c);
  return addDays(last.date, last.protocolDays || 5);
}''',
'''function nextDueDate(c) {
  const last = latestChange(c);
  return addDays(last.date, last.protocolDays || 5) || "No date on record";
}''')

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
