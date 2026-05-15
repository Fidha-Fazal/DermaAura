import py_compile, traceback
try:
    py_compile.compile('app/routes.py', doraise=True)
    print('compiled successfully')
except Exception:
    traceback.print_exc()
