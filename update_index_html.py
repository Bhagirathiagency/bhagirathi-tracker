old = '''    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>bhagirathi-tracker-real</title>'''

new = '''    <meta charset="UTF-8" />
    <link rel="icon" type="image/png" href="/bhagirathi-logo.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="/bhagirathi-logo.png" />
    <link rel="manifest" href="/manifest.json" />
    <meta name="theme-color" content="#1B6B63" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Bhagirathi Tracker</title>'''

with open('index.html', 'r') as f:
    content = f.read()

c = content.count(old)
print("Match:", c)
if c == 1:
    content = content.replace(old, new, 1)
    with open('index.html', 'w') as f:
        f.write(content)
    print("APPLIED_OK")
else:
    print("NO_MATCH_FILE_NOT_CHANGED")
