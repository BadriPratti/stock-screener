# Stock Screener.app

A standalone macOS app wrapper around `dashboard.py`. It bundles its own Python + Flask + pywebview runtime (via py2app) so it can be double-clicked from Applications/Dock/Launchpad without needing a terminal or the project's venv activated — and it opens in its own native window (via `pywebview`, using macOS's WebKit), not a browser tab.

`mac_app/main.py` runs the real `dashboard.py`'s Flask app in a background thread, then opens a `pywebview` window pointed at it — no `webbrowser.open()` call in this path at all, so launching/relaunching the app never pops open your default browser.

It still operates on the real project checkout on disk (`~/Desktop/stock-screener` by default, override with the `STOCK_SCREENER_ROOT` env var if you move the folder) — data files, git pull/push (the Sync button), and running backtest scripts all go through the real repo and its own `venv/bin/python`, exactly like running `python dashboard.py` normally. The app bundle itself only needs to run Flask + pywebview; the heavier dependencies (pandas, yfinance, etc.) are never bundled since `dashboard.py` shells out to scripts rather than importing them directly.

## Rebuilding after changes

Only needed if you change `dashboard.py`'s dependencies (not needed for changes to routes/logic/HTML/CSS/JS — those are read live from the real project folder, no rebuild required):

```bash
venv/bin/pip install py2app pywebview   # one-time
cd mac_app
rm -rf build dist
../venv/bin/python setup.py py2app
```

### Known gotcha: conda-linked native libraries

On this machine, the venv's Python is a conda-based interpreter, and several of its C extensions link against `@rpath/lib*.dylib` copies that live in `~/miniconda3/lib/` rather than a system path — py2app's dependency walker doesn't reliably follow those. Two hit so far: `ctypes` needs `libffi.8.dylib`; `ssl` (imported by `pywebview.http`) needs `libssl.3.dylib` + `libcrypto.3.dylib`. If the built app fails silently (or shows an `ImportError: ... Library not loaded` when run directly from the terminal — see Debugging below), fix each missing one the same way:

```bash
APP="dist/Stock Screener.app"
for lib in libffi.8.dylib libssl.3.dylib libcrypto.3.dylib; do
  cp ~/miniconda3/lib/"$lib" "$APP/Contents/Frameworks/"
  install_name_tool -id "@rpath/$lib" "$APP/Contents/Frameworks/$lib"
done
codesign --force --deep --sign - "$APP"
```

If a *different* missing library shows up later, the pattern is the same: `otool -L` the `.so`/`.dylib` the traceback names to find what it's looking for, locate the real one under `~/miniconda3/lib/`, copy it into `Contents/Frameworks/`, fix its `-id` to `@rpath/<name>`, re-sign.

Then reinstall: `cp -R "dist/Stock Screener.app" "/Applications/Stock Screener.app"` (or drag it in Finder).

## Debugging a launch failure

Run the binary directly to see real output instead of it failing silently:
```bash
"/Applications/Stock Screener.app/Contents/MacOS/Stock Screener"
```
