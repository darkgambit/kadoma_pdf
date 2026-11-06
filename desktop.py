"""Native Windows/macOS shell. The PDF service is authenticated and loopback-only."""
from __future__ import annotations
import argparse
import base64
import json
import os
import secrets
import socket
import sys
import threading
import time
from pathlib import Path

MUTEX_NAME = 'Local\\KADOMASingleInstance'
OPEN_SUFFIX = '.open'
COMBINE_SUFFIX = '.combine'


def pending_dir() -> Path:
    """Where a second launch drops the file it was asked to open.

    A double-clicked PDF starts a new process, but the user expects the document
    to appear in the window they already have. The second process cannot talk to
    the first one directly (it does not have the request token), so it leaves the
    path here and exits; the running instance picks it up.
    """
    base = os.environ.get('LOCALAPPDATA') or os.environ.get('XDG_CACHE_HOME')
    root = Path(base) if base else Path.home() / '.cache'
    target = root / 'KADOMA' / 'pending'
    target.mkdir(parents=True, exist_ok=True)
    return target


def queue_open(path: str) -> None:
    name = f'{time.time_ns()}-{secrets.token_hex(4)}{OPEN_SUFFIX}'
    try:
        (pending_dir() / name).write_text(str(path), encoding='utf-8')
    except OSError:
        pass


def queue_combine(paths: list[str]) -> None:
    """Ask the running window to combine these files into one document."""
    name = f'{time.time_ns()}-{secrets.token_hex(4)}{COMBINE_SUFFIX}'
    try:
        (pending_dir() / name).write_text(json.dumps(list(paths)), encoding='utf-8')
    except OSError:
        pass


def take_pending() -> list[dict]:
    """Work queued by other launches, oldest first. Each entry is consumed once.

    Two kinds share the queue because they are the same thing: something the
    shell was asked to do, and a running window that has not done it yet. The
    timestamp in the file name keeps them in the order they were asked for.
    """
    found: list[dict] = []
    try:
        items = sorted(list(pending_dir().glob(f'*{OPEN_SUFFIX}')) +
                       list(pending_dir().glob(f'*{COMBINE_SUFFIX}')))
    except OSError:
        return []
    for item in items:
        try:
            raw = item.read_text(encoding='utf-8').strip()
            item.unlink()
        except OSError:
            continue
        if not raw:
            continue
        if item.suffix == COMBINE_SUFFIX:
            try:
                paths = json.loads(raw)
            except ValueError:
                continue
            if isinstance(paths, list) and paths:
                found.append({'action': 'combine', 'paths': [str(path) for path in paths]})
        else:
            found.append({'action': 'open', 'path': raw})
    return found


def single_instance() -> tuple[bool, object]:
    """(is_primary, handle). The handle must stay alive for the process lifetime.

    A named mutex is used rather than a lock file because Windows releases it
    automatically if the process dies, so a crashed run never blocks the next one.
    """
    if sys.platform != 'win32':
        return True, None
    try:
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.CreateMutexW.restype = ctypes.c_void_p
        kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
        handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        already_running = ctypes.get_last_error() == 183  # ERROR_ALREADY_EXISTS
        return (not already_running), handle
    except Exception:
        return True, None


def self_test_document() -> bytes:
    """The document the packaged self-test works on.

    The application ships no sample any more, so the check builds what it needs:
    four pages, a 32 pt heading to replace, a reference number to delete and undo,
    and three form fields on the last page (so duplicating that page has to
    produce six uniquely named fields).
    """
    import pymupdf

    with pymupdf.open() as doc:
        first = doc.new_page(width=612, height=792)
        first.insert_text((60, 120), 'Quarterly', fontsize=32, fontname='helv')
        first.insert_text((60, 170), 'Performance report for the packaged build', fontsize=12)
        second = doc.new_page(width=612, height=792)
        second.insert_text((60, 120), 'Reference NL-2048-9931', fontsize=12)
        doc.new_page(width=612, height=792).insert_text((60, 120), 'Third page', fontsize=12)
        fourth = doc.new_page(width=612, height=792)
        fourth.insert_text((60, 120), 'Sign here', fontsize=12)
        for name, top in (('name', 160), ('reference', 210), ('notes', 260)):
            widget = pymupdf.Widget()
            widget.rect = pymupdf.Rect(60, top, 300, top + 30)
            widget.field_name = name
            widget.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
            widget.field_value = ''
            fourth.add_widget(widget)
        return doc.tobytes()


def self_test(report_path: str | None = None):
    """Exercise the packaged engine. Writes a JSON report when asked to, because
    a windowed (console=False) build has no usable stdout to read."""
    from app import __version__
    from app.engine import Engine
    import pymupdf
    checks = []

    def done(name):
        checks.append(name)

    engine = Engine()
    info = engine.load(self_test_document(), 'self-test.pdf')
    assert info['pageCount'] == 4
    done('test document created (4 pages)')

    assert engine.render(info['id'], 0, .2).startswith(b'\x89PNG')
    done('page rendered to PNG')

    assert engine.search(info['id'], 'Quarterly')
    done('offline text search')

    runs = engine.content(info['id'], 0)['runs']
    heading = next(r for r in runs if r['text'] == 'Quarterly')
    assert heading['family'] == 'sans-serif' and heading['spanCount'] >= 1
    done('direct-edit runs exposed with font families')

    engine.operation(info['id'], {'action': 'replace_text', 'page': 0, 'rect': heading['rect'],
                                 'text': 'Packaged standalone heading', 'size': 32,
                                 'color': heading['color'], 'family': heading['family'], 'expand': True})
    assert engine.search(info['id'], 'Packaged standalone heading')
    assert not engine.search(info['id'], 'Quarterly')
    done('direct on-page text replacement')

    engine.operation(info['id'], {'action': 'replace_text', 'page': 1, 'rect': next(
        r for r in engine.content(info['id'], 1)['runs'] if 'NL-2048-9931' in r['text'])['rect'], 'text': ''})
    assert not engine.search(info['id'], 'NL-2048-9931')
    engine.operation(info['id'], {'action': 'undo'})
    assert engine.search(info['id'], 'NL-2048-9931')
    done('text deletion with undo')

    data, _, _ = engine.export(info['id'], 'pdf')
    with pymupdf.open(stream=data, filetype='pdf') as doc:
        assert len(doc) == 4
    done('PDF export')

    for format in ('docx', 'xlsx', 'pptx', 'images'):
        output, _, _ = engine.export(info['id'], format, {'pages': [0]})
        assert output.startswith(b'PK') and len(output) > 1000
    done('Word, Excel, PowerPoint and image ZIP exports')

    protected, _, _ = engine.export(info['id'], 'protected',
                                    {'openPassword': 'smoke-read', 'ownerPassword': 'smoke-owner'})
    with pymupdf.open(stream=protected, filetype='pdf') as doc:
        assert doc.needs_pass and doc.authenticate('smoke-read')
    done('AES-256 encryption export')

    # Saving is the only operation that writes over somebody's file, so it is
    # exercised inside the package rather than taken on trust. The file really
    # is written, and a file that changed behind the application really is
    # refused.
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder) / 'Packaged save.pdf'
        target.write_bytes(engine.export(info['id'], 'pdf')[0])
        working = engine.load(target.read_bytes(), target.name, path=target)['id']
        engine.operation(working, {'action': 'add_text', 'page': 0, 'rect': [60, 300, 420, 340],
                                   'text': 'WRITTEN BY SAVE', 'size': 16})
        engine.save(working)
        with pymupdf.open(target) as written:
            assert 'WRITTEN BY SAVE' in written[0].get_text(), 'Save did not reach the file on disk'
        done('Save writes over the file on disk')

        time.sleep(.02)  # so the file's stamp is unmistakably newer
        target.write_bytes(engine.export(working, 'pdf')[0])
        try:
            engine.save(working)
        except Exception as exc:
            assert getattr(exc, 'code', '') == 'file_changed', f'Save failed for the wrong reason: {exc}'
        else:
            raise AssertionError('Save overwrote a file that had changed on disk')
        done('Save refuses a file that changed since it was opened')

    fields = engine.content(info['id'], 3)['widgets']
    engine.operation(info['id'], {'action': 'fill_forms',
                                 'values': {str(fields[0]['xref']): 'Packaged smoke test'}})
    assert engine.content(info['id'], 3)['widgets'][0]['value'] == 'Packaged smoke test'
    done('form field filling')

    copied = engine.operation(info['id'], {'action': 'duplicate', 'pages': [3]})
    assert copied['formCount'] == 6
    assert engine.content(info['id'], 4)['widgets'][0]['name'] != engine.content(info['id'], 3)['widgets'][0]['name']
    done('duplicated form fields get unique names')

    # Arabic has to be checked inside the package: it depends on a font that is
    # bundled and on the HTML layout path, neither of which is exercised by any
    # of the checks above.
    from app import rtl, share, shell_integration
    chosen = rtl.choose_font()
    assert chosen['path'], 'no Arabic-capable font in the package'
    done(f'right-to-left font available ({chosen["name"]}, {chosen["quality"]} round-trip)')

    arabic = 'مرحبا بالعالم الفاتورة رقم ٢٠٤٨'
    engine.operation(info['id'], {'action': 'add_text', 'page': 0,
                                  'rect': [60, 640, 460, 680], 'text': arabic, 'size': 18})
    stored = engine.export(info['id'], 'txt')[0].decode('utf-8')
    assert 'الفاتورة' in stored and 'مرحبا' in stored, 'Arabic did not read back as logical letters'
    assert not any(0xFB50 <= ord(c) <= 0xFEFF for c in stored), 'shaped forms leaked into the text'
    assert engine.search(info['id'], 'الفاتورة'), 'Arabic is not searchable'
    run = next(r for r in engine.content(info['id'], 0)['runs'] if rtl.is_rtl(r['text']))
    assert run['rtl'] is True
    done('Arabic written, read back, searched and marked right-to-left')

    # A scanned page is the case that is easiest to break in a packaged build:
    # it needs PyMuPDF's redaction with image pixels, and the paper colour is
    # sampled from a rendered pixmap. Neither is exercised by the checks above.
    import pymupdf as fitz
    source = fitz.open()
    sheet = source.new_page(width=595, height=842)
    sheet.draw_rect(sheet.rect, color=None, fill=(0.9, 0.9, 0.88))
    sheet.insert_text((60, 120), 'SCANNED IN THE PACKAGE', fontsize=24)
    raster = sheet.get_pixmap(dpi=120).tobytes('png')
    source.close()
    scan_doc = fitz.open()
    scan_page = scan_doc.new_page(width=595, height=842)
    scan_page.insert_image(fitz.Rect(0, 0, 595, 842), stream=raster)
    scan_data = scan_doc.tobytes()
    scan_doc.close()

    scan = engine.load(scan_data, 'packaged-scan.pdf')['id']
    assert engine.content(scan, 0)['spans'] == [], 'the scan fixture has a text layer'
    box = fitz.Rect(58, 96, 340, 124)
    engine.operation(scan, {'action': 'replace_text', 'page': 0, 'rect': list(box),
                            'text': '', 'size': 24, 'color': '#1a1a1a',
                            'family': 'sans-serif', 'rotation': 0, 'expand': False})
    with fitz.open(stream=engine.export(scan, 'pdf')[0], filetype='pdf') as edited:
        patch = edited[0].get_pixmap(dpi=72, clip=box, colorspace=fitz.csRGB)
    assert min(patch.samples[0::patch.n]) > 180, 'the old ink survived the replacement'
    engine.operation(scan, {'action': 'add_text', 'page': 0, 'rect': [60, 288, 320, 311],
                            'text': 'EDITED IN THE PACKAGE', 'size': 12, 'color': '#1a1a1a'})
    assert engine.search(scan, 'EDITED IN THE PACKAGE'), 'text added to a scan is not searchable'
    done('a scanned page edited without a text layer')

    try:
        import pytesseract  # noqa: F401  (present is the point: OCR needs it)
    except Exception as exc:
        raise AssertionError(f'OCR support is missing from the package: {exc}') from exc
    done('OCR module present in the package')

    # The share folder and the .eml are the two things that touch the user's
    # other programs, so they are checked here rather than assumed.
    data, name, _mime = engine.export(info['id'], 'pdf')
    prepared = share.prepare(data, name)
    assert Path(prepared['path']).read_bytes() == data
    assert share.inside_share(prepared['path']) is not None
    assert share.inside_share(r'C:\Windows\win.ini') is None
    import email as email_module
    message = email_module.message_from_bytes(
        share.eml_bytes(Path(prepared['path']), to='someone@example.com', subject='الفاتورة'),
        policy=email_module.policy.default)
    attachment = list(message.iter_attachments())[0]
    assert attachment.get_payload(decode=True) == data
    assert attachment.get_filename() == prepared['name']
    done('share folder prepared and a real .eml built with the PDF attached')

    assert '%1' in shell_integration.command_line()
    status = shell_integration.status()
    done(f'default-app registration {"available" if status["supported"] else "not applicable on this platform"}')

    # The topmost hand-off is a real module the shell imports at runtime. If
    # PyInstaller missed it, the application would start and the Email button
    # would fail with an import error instead of opening a compose window.
    from app import window_front
    assert hasattr(window_front, 'FrontGuard') and hasattr(window_front, 'set_topmost')
    assert window_front.IS_WINDOWS == (sys.platform == 'win32')
    done('window front hand-off module present in the package')

    report = {'product': 'KADOMA PDF', 'version': __version__, 'checks': checks,
              'frozen': bool(getattr(sys, 'frozen', False)), 'executable': sys.executable,
              'python': sys.version, 'platform': sys.platform}
    if report_path:
        target = Path(report_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'KADOMA PDF packaged-engine smoke test passed ({len(checks)} checks: PDF, direct editing, '
          f'Office exports, encryption, forms, scans, Arabic, sharing).', flush=True)
    return 0


class DesktopBridge:
    """What the interface may ask the native shell to do.

    Defined at module level rather than inside `main` so the contract can be
    tested without a window: the dialogs themselves need a human, but the
    answers they produce do not.
    """
    _window = None
    # Whether the page has work that is not in a file. The page keeps this up
    # to date rather than the shell asking at close time: a question asked
    # *during* the closing event needs the same thread that is asking, which is
    # how a close handler deadlocks.
    unsaved = False
    _asking = False

    def set_unsaved(self, flag):
        """The page reporting whether there is anything to lose."""
        self.unsaved = bool(flag)
        # A fresh answer means the next close may ask again, even if the last
        # question was dismissed.
        self._asking = False
        return {'ok': True}

    def quit_app(self):
        """Close the window from the page, after a save or a deliberate discard."""
        self.unsaved = False
        self._asking = False
        window = self._window
        if window is not None:
            try:
                window.destroy()
            except Exception:
                pass
        return {'ok': True}

    def _choose(self, kind, name='', multiple=False):
        """A native dialog, reported as a path or as a reason there is none.

        Returning a reason rather than raising matters: the interface falls
        back to its own file picker when the dialog cannot be shown, and it
        must be able to tell "the person cancelled" apart from "this
        platform would not open a dialog" — one is an answer, the other is
        a reason to try something else.
        """
        import webview
        from app.engine import safe_name
        try:
            if kind == 'save':
                result = self._window.create_file_dialog(
                    webview.FileDialog.SAVE, save_filename=safe_name(name or 'Untitled.pdf'),
                    file_types=('PDF document (*.pdf)',))
            else:
                result = self._window.create_file_dialog(
                    webview.FileDialog.OPEN, allow_multiple=multiple,
                    file_types=('PDF and images (*.pdf;*.png;*.jpg;*.jpeg;*.webp;*.tif;*.tiff;*.bmp)',
                                'All files (*.*)'))
        except Exception:
            return {'error': 'The file dialog could not be opened.'}
        if not result:
            return {'cancelled': True}
        path = result[0] if isinstance(result, (tuple, list)) else result
        return {'path': str(path)}

    def choose_save_path(self, name=''):
        """Where Save as should write. The server does the writing."""
        return self._choose('save', name)

    def choose_open_path(self):
        """A file to open by path, so Save has somewhere to write back to."""
        return self._choose('open')

    def save_bytes(self, name, encoded):
        # There is no API for arbitrary filesystem paths. The user chooses
        # the destination in a real, native Save dialog for every export.
        import webview
        from app.engine import safe_name
        if not isinstance(name, str) or not isinstance(encoded, str) or len(encoded) > 336 * 1024 * 1024:
            return {'saved': False, 'error': 'The export is too large.'}
        try:
            contents = base64.b64decode(encoded, validate=True)
            result = self._window.create_file_dialog(webview.FileDialog.SAVE, save_filename=safe_name(name))
            if not result:
                return {'saved': False, 'cancelled': True}
            path = result[0] if isinstance(result, (tuple, list)) else result
            Path(path).write_bytes(contents)
            return {'saved': True}
        except Exception:
            return {'saved': False, 'error': 'The file could not be saved. Choose a writable destination.'}


def closing_would_lose_work(bridge) -> bool:
    """Whether closing the window has to ask first.

    One rule, in one place, so it can be tested without a window: the page says
    whether anything is unsaved, and nothing else decides. The shell used to ask
    every time — including for a document nobody had touched, which made quitting
    a two-click ritual for no reason.
    """
    return bool(getattr(bridge, 'unsaved', False))


def main():
    parser = argparse.ArgumentParser(description='KADOMA PDF offline PDF workspace')
    parser.add_argument('file', nargs='?', default=None,
                        help='A PDF (or other supported file) to open on start. '
                             'Windows passes this when a PDF is double-clicked.')
    parser.add_argument('--combine', nargs='*', default=None, metavar='PDF',
                        help='Combine these PDFs into one document. Explorer passes '
                             'the selected files here from the right-click menu.')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--self-test-output', default=None,
                        help='Write the self-test result as JSON (used by the build script).')
    args = parser.parse_args()
    if args.self_test:
        # A windowed build has no console, so a failed check would otherwise
        # leave the process sitting there with nothing to show for it — which
        # reads, from the build script, as a five-minute hang instead of a
        # failure. The error goes into the report and the exit code says so.
        try:
            return self_test(args.self_test_output)
        except Exception as exc:  # noqa: BLE001 - the report is the error channel
            import json
            import traceback
            if args.self_test_output:
                Path(args.self_test_output).write_text(json.dumps({
                    'version': 'unknown', 'frozen': bool(getattr(__import__('sys'), 'frozen', False)),
                    'checks': [], 'error': f'{type(exc).__name__}: {exc}',
                    'traceback': traceback.format_exc(),
                }, indent=2), encoding='utf-8')
            return 1

    import uvicorn
    import webview
    from app.server import app
    from app.engine import safe_name
    from app.window_front import FrontGuard

    requested = None
    if args.file:
        candidate = Path(args.file)
        if candidate.is_file():
            requested = str(candidate)

    # One file selected in Explorer is not a combination — it is an open.
    combining = [str(Path(item)) for item in (args.combine or []) if Path(item).is_file()]
    if len(combining) == 1:
        requested, combining = combining[0], []

    # Another copy already running? Hand the work over and leave quietly, so
    # the window the user already has is the one that does it.
    is_primary, mutex = single_instance()
    if not is_primary:
        if combining:
            queue_combine(combining)
        elif requested:
            queue_open(requested)
        return 0

    # The right-click entry is written once per start rather than at install
    # time: there is no installer, and a copy that was moved needs its command
    # line pointing at where it is now. Failure is not fatal — a locked-down
    # policy should cost the menu entry, not the application.
    try:
        from app import shell_integration
        shell_integration.register_context_menu()
    except Exception:
        pass

    token = secrets.token_urlsafe(32)
    app.state.token, app.state.desktop = token, True
    pending = []
    if combining:
        pending.append({'action': 'combine', 'paths': combining})
    elif requested:
        pending.append({'action': 'open', 'path': requested})
    app.state.pending_open = pending
    app.state.pending_lock = threading.Lock()
    # The window starts on top, but a compose window or a printer driver dialog
    # has to be able to come in front of it. Routes that open one call this
    # first; the watcher puts the style back when KADOMA is active again.
    front = FrontGuard()
    app.state.release_front = front.release
    front.start()

    def watch_for_opens(stop: threading.Event):
        """Collect work queued by later launches and hand it to the interface."""
        while not stop.wait(.6):
            for entry in take_pending():
                with app.state.pending_lock:
                    app.state.pending_open.append(entry)

    stop_watcher = threading.Event()
    watcher = threading.Thread(target=watch_for_opens, args=(stop_watcher,), daemon=True)
    watcher.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    sock.listen(128)
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port,
                                         log_level='warning', access_log=False,
                                         loop='asyncio', http='h11', ws='none'))
    thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True)
    thread.start()
    deadline = time.monotonic() + 15
    while not server.started and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(.05)
    if not server.started:
        raise RuntimeError('The local PDF service could not start.')
    bridge = DesktopBridge()
    window = webview.create_window('KADOMA PDF',
                                   f'http://127.0.0.1:{port}/#session={token}',
                                   js_api=bridge, width=1440, height=940,
                                   min_size=(1080, 680), text_select=False,
                                   background_color='#f4f4f8',
                                   # A document window opens filling the screen:
                                   # the page is the point, and a window that
                                   # starts at 1440x940 wastes the rest of a
                                   # desktop on grey.
                                   maximized=True,
                                   # ...and it stays in front, so a page being
                                   # read or copied from is not buried the moment
                                   # another window is clicked.
                                   on_top=True,
                                   # The shell used to ask "close this window?"
                                   # every single time, including for a document
                                   # nobody had touched. The question belongs to
                                   # the closing event, which knows whether there
                                   # is anything to save.
                                   confirm_close=False)
    bridge._window = window

    def on_shown():
        # `maximized=True` is passed to the window above, but the Edge WebView2
        # backend ignores it — the window comes up at its nominal 1440x940.
        # Asking once the page has loaded is what actually fills the screen:
        # asking earlier leaves the window minimized, because the form has not
        # finished being shown yet and the request lands on a window that is
        # still sizing itself.
        try:
            window.maximize()
        except Exception:
            pass

    window.events.loaded += on_shown

    def on_closing():
        if not closing_would_lose_work(bridge):
            # Nothing to lose: close at once, with no dialog at all.
            return True
        if bridge._asking:
            return False
        bridge._asking = True

        def ask():
            try:
                # Raised after this handler returns. Evaluating script from
                # inside a closing handler blocks the GUI thread the script
                # needs to run on, and the window never closes.
                window.evaluate_js('window.kadomaAskToSaveBeforeQuit()')
            except Exception:
                bridge._asking = False
                bridge.unsaved = False
                window.destroy()

        threading.Timer(0.05, ask).start()
        return False

    window.events.closing += on_closing
    try:
        backend = 'edgechromium' if sys.platform == 'win32' else 'cocoa' if sys.platform == 'darwin' else None
        webview.start(gui=backend, debug=False)
    finally:
        front.stop()
        app.state.release_front = None
        stop_watcher.set()
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
