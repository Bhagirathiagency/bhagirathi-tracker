old = '''  const filtered = cases.filter((c) => {
    if (filter === "all") return true;
    if (filter === "overdue") return overdueDays(c) > 0;'''

new = '''  const filtered = cases.filter((c) => {
    if (filter === "all") return true;
    if (filter === "overdue") return c.status === "active" && nextDueDate(c) <= addDays(todayISO(), 1);'''

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
