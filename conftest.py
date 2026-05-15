# pyre-ignore-all-errors
"""
Pytest configuration and shared fixtures for tests.
"""
import pytest  # pyre-ignore
import os
import tempfile


@pytest.fixture(scope='session', autouse=True)
def app():
    """Create a single Flask app for the entire test session.

    The routes module registers its handlers on import-time using the global
    ``app`` object. When `create_app` is invoked repeatedly (once per test),
    subsequent Flask instances never receive those routes, resulting in 404s.
    By scoping the fixture to the session we only construct the app once, and
    every test reuses the same URL map.  The database is still reset between
    tests via the ``client`` fixture below.
    """
    import tempfile

    # Create a temporary database file for the session
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    os.environ['DERMAURA_TEST_DB'] = 'sqlite:///' + db_path

    from app import create_app  # pyre-ignore
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

    yield test_app

    # Cleanup environment variable (file may remain but not needed for tests)
    if 'DERMAURA_TEST_DB' in os.environ:
        del os.environ['DERMAURA_TEST_DB']  # pyre-ignore


@pytest.fixture
def client(app):
    """Create test client and initialize database."""
    with app.app_context():
        from app import db  # pyre-ignore
        # Create all tables
        db.create_all()
    
    yield app.test_client()
    
    # Cleanup
    with app.app_context():
        from app import db  # pyre-ignore
        db.session.remove()
        db.drop_all()
