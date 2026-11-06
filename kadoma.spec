# PyInstaller builds MUST run on the target operating system and architecture.
import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH)
IS_MAC = sys.platform == 'darwin'
IS_WIN = sys.platform == 'win32'

# KADOMA_BUILD_MODE=onefile produces ONE stand-alone executable that can be
# copied anywhere on its own. The default folder build starts faster and is the
# documented portable layout. Neither is a cross-build: both run natively.
ONE_FILE = os.environ.get('KADOMA_BUILD_MODE', 'folder').strip().lower() in ('onefile', 'one-file', 'standalone')

# Only what the frozen application reads at runtime. The icon sources are
# inputs to scripts/make_icons.py, not assets: the platform icon is embedded in
# the executable by PyInstaller, and shipping the other two would add 2.2 MB of
# files nothing ever opens. The licence texts stay, because they must.
datas = [(str(ROOT / 'app' / 'static'), 'app/static'),
         (str(ROOT / 'assets' / 'third_party_licenses'), 'assets/third_party_licenses'),
         (str(ROOT / 'assets' / 'INSTALL_NOTES.txt'), 'assets'),
         (str(ROOT / 'LICENSE'), '.'),
         (str(ROOT / 'THIRD_PARTY_NOTICES.md'), '.'),
         (str(ROOT / 'README.md'), '.')]
datas += collect_data_files('webview')
# Include all OOXML templates, notably notesMaster.xml/notes.xml. The default
# python-pptx hook alone does not collect every template used by notes slides.
datas += collect_data_files('pptx')
datas += collect_data_files('docx')
# python-pptx constructs oxml/../templates without normalizing the path.
# Frozen Python code has no physical oxml directory unless a data file creates it.
datas += [(str(ROOT / 'assets' / 'pptx-resource-marker.txt'), 'pptx/oxml')]
hidden = ['uvicorn.logging', 'uvicorn.loops.asyncio',
          'uvicorn.protocols.http.h11_impl', 'uvicorn.lifespan.on',
          'pymupdf', 'pytesseract', 'PIL.Image', 'multipart']
if IS_WIN:
    hidden += ['webview.platforms.winforms', 'webview.platforms.edgechromium', 'pythonnet', 'clr']
elif IS_MAC:
    hidden += ['webview.platforms.cocoa', 'objc', 'AppKit', 'WebKit', 'Foundation']

# Packages this application never imports, excluded so the build does not depend
# on what happens to be installed alongside it. PyMuPDF's optional NumPy support
# is written as `try: import numpy`, and PyInstaller follows that branch even
# when the branch is never taken — so on a machine where NumPy happens to be
# present, 24 MB of NumPy binaries and SciPy were silently bundled into the
# executable. Nothing in this application imports any of these; verified by
# running the real import graph (pymupdf, PIL, fastapi, uvicorn) and checking
# that not one of them appears. If a future feature genuinely needs NumPy, add it
# back deliberately rather than letting the environment decide.
UNUSED_PACKAGES = ['IPython', 'jupyter', 'notebook', 'tkinter',
                   'numpy', 'scipy', 'pandas', 'matplotlib', 'schedula', 'tqdm', 'regex']

analysis = Analysis([str(ROOT / 'desktop.py')], pathex=[str(ROOT)],
                    binaries=[], datas=datas, hiddenimports=hidden,
                    hookspath=[], hooksconfig={}, runtime_hooks=[],
                    excludes=UNUSED_PACKAGES,
                    noarchive=False)
pyz = PYZ(analysis.pure)

ICON = str(ROOT / 'assets' / ('KADOMA.icns' if IS_MAC else 'KADOMA.ico'))
MAC_INFO = {
    'CFBundleName': 'KADOMA PDF',
    'CFBundleDisplayName': 'KADOMA PDF',
    'CFBundleShortVersionString': '0.28.2',
    'CFBundleVersion': '1',
    'NSHighResolutionCapable': True,
    'NSAppTransportSecurity': {'NSAllowsLocalNetworking': True},
    'NSRequiresAquaSystemAppearance': False,
    # Declares PDF as a type this bundle can open, so macOS offers KADOMA in
    # "Open With". LSHandlerRank is deliberately 'Alternate' rather than 'Owner':
    # the app can be chosen as a PDF handler, but it does not claim to own the
    # type on a machine that already has Preview.
    'CFBundleDocumentTypes': [
        {
            'CFBundleTypeName': 'PDF Document',
            'CFBundleTypeRole': 'Editor',
            'LSHandlerRank': 'Alternate',
            'LSItemContentTypes': ['com.adobe.pdf'],
        },
    ],
}

if ONE_FILE:
    # Binaries and data are embedded in the executable and unpacked to a private
    # temporary directory at start-up, so one file is the whole application.
    # Trade-off: a slower first launch while that unpack happens.
    exe = EXE(pyz, analysis.scripts, analysis.binaries, analysis.datas, [],
              name='KADOMA', debug=False, bootloader_ignore_signals=False,
              strip=False, upx=False, console=False, icon=ICON,
              disable_windowed_traceback=False, argv_emulation=False,
              exclude_binaries=False)
    if IS_MAC:
        bundle = BUNDLE(exe, name='KADOMA.app', icon=ICON,
                        bundle_identifier='org.kadoma.pdfstudio', info_plist=MAC_INFO)
else:
    exe = EXE(pyz, analysis.scripts, [], exclude_binaries=True,
              name='KADOMA', debug=False, bootloader_ignore_signals=False,
              strip=False, upx=False, console=False,
              icon=ICON,
              disable_windowed_traceback=False,
              argv_emulation=False)
    collection = COLLECT(exe, analysis.binaries, analysis.datas,
                         strip=False, upx=False, name='KADOMA')
    if IS_MAC:
        bundle = BUNDLE(collection, name='KADOMA.app', icon=ICON,
                        bundle_identifier='org.kadoma.pdfstudio', info_plist=MAC_INFO)
