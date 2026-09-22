"""py2app build config for Stock Screener.app.

Build (from the project root, using the project's own venv so Flask etc. are
available to bundle):
    venv/bin/pip install py2app          # one-time
    cd mac_app && ../venv/bin/python setup.py py2app
    open dist/Stock\\ Screener.app

Bundles Flask + its own dependencies, plus pywebview and its macOS backend
(pyobjc's Cocoa/WebKit bridge) — dashboard.py never imports pandas/yfinance/
etc. directly, it shells out to the project's real venv (venv/bin/python) to
run scripts, so there's no scientific-Python packaging to fight here.
"""
from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/AppIcon.icns',
    'plist': {
        'CFBundleName': 'Stock Screener',
        'CFBundleDisplayName': 'Stock Screener',
        'CFBundleIdentifier': 'com.stockscreener.dashboard',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSUIElement': False,  # show a Dock icon (it's a real app, not a background agent)
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'flask', 'jinja2', 'werkzeug', 'click', 'itsdangerous', 'markupsafe', 'blinker',
        'webview', 'objc', 'Cocoa', 'WebKit', 'Quartz', 'Security', 'UniformTypeIdentifiers',
    ],
    # py2app's dependency walker only bundles what it can see used at build
    # time. `zoneinfo` is stdlib but wasn't referenced anywhere when this app
    # was first packaged; dashboard.py picked up `from src.screening import
    # pick_history`/`market_motion` afterwards, both of which import it, and
    # a build made before that addition fails at launch with
    # "ModuleNotFoundError: No module named 'zoneinfo'" even though it's a
    # standard-library module, because the frozen stdlib zip just doesn't
    # have it. Listed explicitly so a rebuild always includes it regardless
    # of what dashboard.py's dependency graph looks like at build time.
    'includes': ['zoneinfo'],
}

setup(
    app=APP,
    name='Stock Screener',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
