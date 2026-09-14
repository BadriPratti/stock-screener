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
}

setup(
    app=APP,
    name='Stock Screener',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
