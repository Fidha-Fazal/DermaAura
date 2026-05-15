try:
    import app.routes
    print('routes import succeeded')
except Exception as e:
    import traceback
    traceback.print_exc()
