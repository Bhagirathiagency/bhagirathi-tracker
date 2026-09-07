old = '''                <div style={{ flex: 1 }}>
                  <div style={styles.cardTitle}>{d}</div>
                  <div style={styles.cardMeta}>{countFor(d)} dressing{countFor(d) === 1 ? "" : "s"} logged{(dresserProfiles && dresserProfiles[d] && dresserProfiles[d].phone) ? ` · ${dresserProfiles[d].phone}` : ""}</div>
                </div>'''

new = '''                <div style={{ flex: 1 }}>
                  <div style={styles.cardTitle}>{d}</div>
                  <div style={styles.cardMeta}>
                    {countFor(d)} dressing{countFor(d) === 1 ? "" : "s"} logged
                    {(dresserProfiles && dresserProfiles[d] && dresserProfiles[d].phone) && (
                      <> · <a href={`tel:${dresserProfiles[d].phone}`} onClick={(e) => e.stopPropagation()} style={{ color: "#128577", fontWeight: 600, textDecoration: "none" }}>📞 {dresserProfiles[d].phone}</a></>
                    )}
                  </div>
                </div>'''

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
