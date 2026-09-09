old = '''        <Field label="Total Amount (₹)">
          <input type="number" style={styles.input} value={form.totalAmount}
            onChange={(e) => { setAmountTouched(true); set("totalAmount", e.target.value); }} />
          {mrpTotal > 0 && (
            <span style={styles.mutedSmall}>
              MRP for selected item(s): {fmtMoney(mrpTotal)}
              {Number(form.totalAmount) !== mrpTotal && (
                <> · <span style={{ ...styles.linkBtn, fontSize: 11 }} onClick={() => { setAmountTouched(false); set("totalAmount", mrpTotal); }}>use MRP</span></>
              )}
            </span>
          )}
        </Field>
        <Field label="Amount Received (₹)"><input type="number" style={styles.input} value={form.amountReceived} onChange={(e) => set("amountReceived", e.target.value)} placeholder="0 if none yet" /></Field>'''

new = '''        <Field label="Total Amount & Amount Received (₹)">
          <div style={{ display: "flex", gap: 8 }}>
            <input type="number" style={{ ...styles.input, flex: 1 }} value={form.totalAmount} placeholder="Total"
              onChange={(e) => { setAmountTouched(true); set("totalAmount", e.target.value); }} />
            <input type="number" style={{ ...styles.input, flex: 1 }} value={form.amountReceived} onChange={(e) => set("amountReceived", e.target.value)} placeholder="Received (0 if none)" />
          </div>
          {mrpTotal > 0 && (
            <span style={styles.mutedSmall}>
              MRP for selected item(s): {fmtMoney(mrpTotal)}
              {Number(form.totalAmount) !== mrpTotal && (
                <> · <span style={{ ...styles.linkBtn, fontSize: 11 }} onClick={() => { setAmountTouched(false); set("totalAmount", mrpTotal); }}>use MRP</span></>
              )}
            </span>
          )}
        </Field>'''

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
