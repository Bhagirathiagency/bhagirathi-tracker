with open('src/App.jsx', 'r') as f:
    content = f.read()

old = '''      <SectionTitle>Revenue</SectionTitle>'''
new = '''      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
        <button style={{ ...styles.smallBtn, background: "#3B5BA5" }} onClick={() => window.print()}>Download as PDF</button>
      </div>

      <SectionTitle>Revenue</SectionTitle>'''

count = content.count(old)
print('Button match count:', count)
if count:
    content = content.replace(old, new, 1)

old2 = '''const fontImport = `'''
new2 = '''const printStyles = `
@media print {
  header, nav, .no-print { display: none !important; }
  body, .app-root { background: #fff !important; }
  main { max-width: 100% !important; padding: 0 !important; }
}
`;

const fontImport = `'''

count2 = content.count(old2)
print('Print CSS match count:', count2)
if count2:
    content = content.replace(old2, new2, 1)

old3 = '''      <style>{fontImport}</style>'''
new3 = '''      <style>{fontImport}</style>
      <style>{printStyles}</style>'''
count3 = content.count(old3)
print('Style tag match count:', count3)
if count3:
    content = content.replace(old3, new3, 1)

with open('src/App.jsx', 'w') as f:
    f.write(content)
print('DONE')
