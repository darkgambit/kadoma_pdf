# Third-party notices

KADOMA's original application code is licensed under **GNU AGPL-3.0-or-later**.
The full license is in `LICENSE`. KADOMA is not an Adobe product and uses no
Adobe logos, artwork, or proprietary SDKs.

## Important PDF-engine license

**PyMuPDF / MuPDF** is available under the GNU AGPL or an appropriate commercial
license from its vendor. This project follows the open-source AGPL path. If you
intend to make a closed-source commercial application, obtain licensing advice
and, where necessary, the appropriate commercial license before distribution.
Merely packaging the application into an EXE or APP does not remove obligations.

- PyMuPDF source and license: <https://github.com/pymupdf/PyMuPDF>
- MuPDF source and license: <https://mupdf.com/licensing/>
- AGPL text: `LICENSE`

## Runtime libraries

Each dependency retains its own copyright and license. The following is an
orientation list, not a substitute for those licenses:

| Component | Purpose | License family / source |
|---|---|---|
| PyMuPDF / MuPDF | PDF rendering and modification | AGPL / commercial; see above |
| FastAPI | Local HTTP API | MIT; <https://github.com/fastapi/fastapi> |
| Starlette | ASGI transport | BSD; <https://github.com/Kludex/starlette> |
| Uvicorn | Loopback HTTP server | BSD; <https://github.com/encode/uvicorn> |
| python-multipart | File uploads | Apache-2.0; <https://github.com/Kludex/python-multipart> |
| Pydantic / pydantic-core | API validation | MIT; <https://github.com/pydantic/pydantic> |
| Pillow | Image processing | HPND and bundled-code notices; <https://github.com/python-pillow/Pillow> |
| ReportLab | Original sample PDF | BSD; <https://www.reportlab.com/> |
| python-docx | Editable Word export | MIT; <https://github.com/python-openxml/python-docx> |
| python-pptx | Slide-image export | MIT; <https://github.com/scanny/python-pptx> |
| openpyxl | Excel export | MIT; <https://openpyxl.readthedocs.io/> |
| lxml | OOXML support | BSD and linked-library notices; <https://lxml.de/> |
| pytesseract | Local OCR wrapper | Apache-2.0; <https://github.com/madmaze/pytesseract> |
| pywebview | Native desktop window | BSD; <https://github.com/r0x0r/pywebview> |
| Python.NET (Windows) | Native Windows bridge | MIT; <https://github.com/pythonnet/pythonnet> |
| PyObjC (macOS) | Native macOS bridge | MIT; <https://github.com/ronaldoussoren/pyobjc> |
| PyInstaller | Application packaging | GPL with bootloader exception; <https://pyinstaller.org/> |
| Inter | Locally bundled interface font | SIL Open Font License; full text in `app/static/fonts/OFL.txt` |
| Noto Sans Arabic | Bundled right-to-left fallback font, used only when no Arabic system font is present | SIL Open Font License 1.1; full text in `app/static/fonts/NotoSansArabic-OFL.txt`; <https://fonts.google.com/noto/specimen/Noto+Sans+Arabic> |

## Printing and combining add no new dependency

Neither feature introduces a third-party library or a redistributed binary.

**Direct printing** (`app/printing.py`):

- On Windows it calls the operating system's print API (`gdi32` and
  `winspool.drv`) through `ctypes`, which is part of the Python standard library.
  Nothing from the printer vendor is bundled or linked.
- On macOS and Linux it pipes the PDF to the system print client (`lpr` or `lp`),
  which is part of the operating system and is invoked as an external process,
  not redistributed with KADOMA.

**Combining files** adds no dependency at all. It uses MuPDF's own page copy
through the PyMuPDF binding already listed above, plus `re` and `pathlib` from
the Python standard library. The interface side uses `AbortController` and
`<dialog>`, both browser built-ins, so the offline no-CDN rule still holds.

So neither feature changes the licensing position described above.

The build script copies installed dependency metadata and available full license
texts into `assets/third_party_licenses/` before packaging. Check that directory,
the generated manifest, and linked upstream licenses when preparing a release.
Review any additional redistribution requirements for native binary components.

## Optional external engines — not bundled

- **LibreOffice**: Office-to-PDF conversion. Separately installed by the user;
  see <https://www.libreoffice.org/about-us/licenses/>.
- **Tesseract**: OCR executable and language data. Separately installed by the
  user; see <https://github.com/tesseract-ocr/tesseract> (Apache-2.0).
- **Microsoft Edge WebView2**: Windows browser runtime, separately installed
  under Microsoft's terms. Not bundled in this source/build kit.
- **Apple WKWebView**: An operating-system framework, not redistributed here.
- **Inno Setup**: Optional Windows installer compiler; see
  <https://jrsoftware.org/isinfo.php>. The compiler is not bundled.

Corresponding KADOMA source and build scripts are included with the build
artifacts by `scripts/build.py`. Include these notices and source when distributing
under the project's license. This document is not legal advice.

## Upstream corresponding source for native releases

The generated source ZIP contains KADOMA application source and build scripts;
it does not automatically assemble all upstream dependency source packages.
When distributing native binaries, supply the corresponding upstream sources
required by AGPL and other applicable licenses, or use appropriate alternative
commercial licensing. License collection and source links alone are not a
guarantee of complete release compliance.
