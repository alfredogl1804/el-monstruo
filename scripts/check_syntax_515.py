import ast

files = ['kernel/embrion_loop.py', 'kernel/main.py', 'tools/github.py']
ok = 0
for f in files:
    try:
        with open(f) as fh:
            ast.parse(fh.read())
        print(f"  OK: {f}")
        ok += 1
    except SyntaxError as e:
        print(f"  FAIL: {f} -- line {e.lineno}: {e.msg}")
print(f"\n{ok}/{len(files)} syntax OK")
