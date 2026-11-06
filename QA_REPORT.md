# KADOMA — verification report

## 0.28.2 — external windows can take the front

Date: **6 November 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

| What was asked | What is there now |
|---|---|
| The email compose window and printer preferences must come in front of KADOMA | `app/window_front.py` drops `WS_EX_TOPMOST` via `SetWindowPos` just before a hand-off, and a watcher restores it when KADOMA is the active window again. Wired into `/api/share/email`, `/api/share/reveal`, `/api/system/print/preferences` and the default-app Settings action. |

| Check | Actual result |
|---|---|
| Engine + API tests | **350 passed, 2 skipped, 0 failures** (13 new window-front tests) |
| Dead-button audit | **235 controls, 274 static + 82 live steps, 356 passed, 0 failed** |
| Browser workflow checks | **20 / 11 / 12 / 2 / 8 passed** |
| Real-window probe (`scripts/check_window_front.py`) | **10 passed, 0 failed**: a real WebView2 window starts topmost; an external process window opened behind it (Z-order KADOMA 0 / external 1); after `release()` the external window is in front (KADOMA 1 / external 0); returning to KADOMA restores `WS_EX_TOPMOST` |
| Frozen self-test | **20/20** in each artifact — one new check asserts the hand-off module is bundled |

### What this release does **not** prove

- **The actual Outlook compose window and the real printer driver dialog were not
  opened from the shipped EXE.** The probe uses a separate process's window to
  reproduce the same foreground/Z-order situation. The routes are asserted to
  call `yield_front()` before handing off.
- **The behaviour is Windows-only.** `window_front.py` is a pure-ctypes no-op on
  macOS and Linux; those builds keep pywebview's `on_top` flag unchanged.
- An external window that never takes the foreground is covered by an 8-second
  fallback that restores the style. Once another window has been seen in front,
  no timeout applies — KADOMA stays demoted until the person comes back.

---

## 0.28.1 — unlimited combine

Date: **2 November 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

| What was asked | What is there now |
|---|---|
| Remove the 20-file cap on right-click combine | `MAX_MERGE_FILES` removed from the engine, server, shell integration, and the front-end merge window. The only guard is the 500 MB combined size limit (`MAX_UPLOAD`). |

| Check | Actual result |
|---|---|
| Engine + API tests | **337 passed, 2 skipped, 0 failures** — the count-limit assertions are gone, and a new 25-file regression test covers the Explorer endpoint |
| The 20-file refusal is gone | `read_documents`, `engine._check_batch`, `_merge_payload`, and `inspect` no longer raise `too_many_files`. The front-end no longer slices at 20 or shows a count error. |
| Remaining practical ceiling | Windows `CreateProcess` command-line limit (~32767 characters). With typical paths this is roughly 100–120 files; with short names it can be more. This is an OS wall, not a cap set by the application. |

### What this patch does **not** prove

- **No Explorer multi-select was tested with >20 files.** The code cap is gone; the OS command-line length is the next wall.
- **A context-menu shell extension was not built.** To go truly beyond the command-line limit would need a COM `DropTarget` extension, which is a much larger change.

---

## 0.28.0 — dark by default, and a right-click that combines a selection

Date: **31 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

| What was asked | What is there now |
|---|---|
| Dark mode as the default view | `theme.js` sets dark when nothing is stored, instead of following the system preference. A stored choice still wins, so switching to light sticks. The page itself stays white in both themes — it is paper. |
| Right-click several PDFs and combine them in one click | `HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\KADOMACombine`, label **Combine with KADOMA PDF**, `MultiSelectModel=Player`, command `"<exe>" --combine %*`. Written at every start for the current user, no administrator rights, removed by `unregister()`. The app reads the files, checks each for a `%PDF-` header, joins them in the order selected, and opens the result named after their folder. |

| Check | Actual result |
|---|---|
| Engine + API tests | **337 passed, 2 skipped** (13 new) |
| Dead-button audit | **235 controls, 274 static steps, 0 problems; 82 live steps, 356 passed, 0 failed** — including a new assertion that a fresh profile opens dark |
| Browser workflow checks | **20 passed** |
| Direct-edit checks | **11 passed** |
| Share / Arabic / default-app checks | **12 passed** |
| Hosted-privacy checks | **2 passed** |
| Save checks | **8 passed** |
| The registry entry, read back independently | label `Combine with KADOMA PDF`; `MultiSelectModel` `Player`; command `"…python.exe" "…desktop.py" --combine %*` |
| The command Explorer runs, run for real | three files → window opened on **combine-test.pdf, 3 pages**, page 1 of 3 reading `PART 1`, dark interface |

### What this release does **not** prove

- **The menu was not clicked in Explorer.** The entry is asserted by reading
  the registry back, and the exact command it runs was executed with three
  paths. Windows' expansion of `%*` for a multi-selection is its documented
  behaviour, not something observed here.
- **The entry is per user and silent on failure.** A policy that blocks
  `HKCU\Software\Classes` loses the menu entry; the application still runs.
- **Dark is a default, not an override.** A stored `light` choice from an
  earlier version is honoured.

## 0.27.0 — fields another reader can use, a window that fills the screen, a real draft

Date: **29 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2, Chrome 141 (PDFium), Adobe Acrobat Pro DC installed but
not driveable here. Development verification, **not independent security
certification**.

| What was asked | What is there now |
|---|---|
| The text field and the date field cannot be used by other PDF applications — they should be usable | Every field-creating path now ends in `form_prep.ensure_acroform()`, which writes the document-wide **`/AcroForm /DR`** font resources (Helv, ZaDb, TiRo), a default appearance, and a **`/P`** page reference on every widget. Without `/DR` a field's `/DA` names a font nothing can resolve, which is what stops Acrobat accepting typing at all; without `/P` a widget does not say which page it belongs to. A document whose AcroForm carries `/XFA` is left alone rather than rewritten. |
| The window should open maximised and on top | The shell passes **`maximized=True, on_top=True`** and asks again from the `loaded` event, because the WebView2 backend ignores `maximized=True` on its own. Verified against the running window: `IsZoomed` true, `WS_EX_TOPMOST` set. |
| The email option should open a draft with the PDF attached so the recipient can be chosen | The first share option now asks the mail client to **compose**: Outlook's `/c ipm.note /m "?subject=…&body=…" /a <file>` (an empty address leaves the To box empty), or Thunderbird's `-compose`. Measured in the real Outlook on this machine: To empty, Subject filled, body **“Please see the attached file”**, `Quarterly performance.pdf` attached. |

| Check | Actual result |
|---|---|
| Engine + API tests | **324 passed, 2 skipped** (13 new: 6 on the exported form's structure, 5 on the compose route, 1 on the window flags, plus the existing ones) |
| Dead-button audit | **235 controls, 274 static steps, 0 problems; 82 live steps, 356 passed, 0 failed** |
| Browser workflow checks | **20 passed** |
| Direct-edit checks | **11 passed** |
| Share / Arabic / default-app checks | **12 passed** |
| Hosted-privacy checks | **2 passed** (0 uploads before consent, 1 after) |
| Save checks | **8 passed** |
| Another reader fills the form | **4 of 4 fields** — `scripts/check_reader.py` opens the exported form in Chrome (PDFium, a different engine from KADOMA's MuPDF), clicks each field, types, and counts pixels changed inside that field's own rectangle: Name 264, Date 391, Signature 259, checkbox 52 |
| The window at runtime | `IsZoomed` true, `WS_EX_TOPMOST` set, 1295x687 on a 1280x720 desktop |
| The compose window | Opened by the real Outlook: To empty, subject “PDF: Quarterly performance.pdf”, body “Please see the attached file”, attachment present |

### What this release does **not** prove

- **Acrobat itself was not driven.** It is installed here but closes itself on
  start (trial state), so the one application the `/DR` and `/P` work is aimed at
  could not be observed opening the file. What is asserted is the structure those
  keys are documented to require, and a second engine filling the same file.
- **Chrome filled the form before this release too.** Chrome tolerates the
  missing `/DR`; that is why the defect was invisible from inside the
  application. `check_reader.py` is a regression guard, not proof that the fix
  was needed for Chrome.
- **Simple MAPI was tried and removed.** On a machine whose default mail client
  is a Store app, `MAPISendMail` neither opens a window nor returns. A hung call
  is indistinguishable from a compose window somebody is typing into, and a hang
  reported as success is worse than no feature, so the code uses the clients'
  own command lines, which return.
- **The checkbox needed a single click.** Two clicks tick and untick it; the
  first version of the check did exactly that and read as a pass because the
  focus ring moved pixels.

## 0.26.0 — Prepare Form, 500 MB, no sample, print defaults, an editable email

Date: **28 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.25.0 and earlier results below are retained. Seven requests this time.

| What was asked | What is there now |
|---|---|
| Raise the limit to 500 MB | `MAX_UPLOAD` is **500 MB** and `MAX_EXPORT_BYTES` matches it — a copy of the largest document that can be opened. Undo keeps its own 100 MB budget, so a very large file gets fewer undo steps instead of a second copy in memory. |
| Remove the default PDF included with the app | The sample is **gone from the application**: `app/demo.py` deleted, `engine.demo()` and `/api/documents/demo` removed, and `initialize()` opens nothing. The app starts on Home with an empty workspace. |
| Text and date fields a non-KADOMA user can fill | Every field Prepare Form adds is a real AcroForm widget. A **date field carries the two JavaScript actions Acrobat writes for its own date picker** (`AFDate_KeystrokeEx`, `AFDate_FormatEx`), so Acrobat shows a calendar and other readers take a typed date. |
| Add another tool: Prepare Form | A new home tool that scans for runs of underscores, drawn boxes and `Label:` lines, lists what it found with type and page, and adds the ones you keep — as one undo step. |
| Print: auto orientation, A4 default that is adjustable, two-sided | **Orientation** starts on **Auto** and follows the page on screen; **Paper** starts at **A4** with the content scaled to fit and can be changed; **Sides** offers two-sided printing when the driver reports it. |
| Email: draft with the PDF attached and an editable body, default “please see attached” | The share dialog now has a **Message** box, prefilled from the server with **“Please see the attached file”**, and both email routes send what is in it. |

| Check | Actual result |
|---|---|
| Engine/API test suite | **312 passed**, 2 skipped, **0 failed** — up from 302. **10 new tests** |
| **The scan finds the four places a field goes** | A page with `Name:`, `Date of birth:`, `Signature ____` and a drawn box asserted to yield text, **date**, text and checkbox candidates, each with a real rectangle |
| **An empty page offers nothing** | A page of prose asserted to scan to `[]` rather than inventing fields |
| **The fields are real widgets** | The exported PDF reopened and asserted to have one widget per candidate, **unique names**, a real `/AcroForm` in the catalog, and both a `CheckBox` and a `Text` widget |
| **A date field carries Acrobat's actions** | `/AA` asserted present and to contain **`AFDate_FormatEx`** and **`AFDate_KeystrokeEx`**, with the format written for Acrobat matching the one stored for KADOMA |
| **A repeated label gets its own name** | Two `Name:` lines asserted to produce two fields with two different names |
| **Preparing a form is one undo step** | The whole run asserted to be undone in one step, back to the original field count |
| **Two-sided is only offered when the driver can do it** | `duplex_options` asserted to be a subset of simplex/long/short; a driver that reports nothing must return only `simplex` |
| **A two-sided choice reaches the driver** | Written into the settings block and read back. On a driver that cannot do it, asserted to be normalised back to simplex rather than the summary claiming otherwise |
| **The print preview opens on A4 and Auto** | In a real browser: the paper select asserted to read **A4**, the note to say the sheet is A4, and the orientation select to read **auto**; a two-sided control asserted to exist |
| **Auto really follows the page** | A two-page document (portrait then landscape) previewed: page 1 asserted **595 × 842**, page 2 asserted **842 × 595**, with the select still on Auto |
| **The email draft starts with the sentence and sends what is typed** | The message box asserted to arrive as *“Please see the attached file”*; typed over, and the request asserted to carry the new text with `attach: true` |
| **The application opens with nothing open** | After a reload with every document deleted: `state.doc` asserted null, the home screen asserted on screen, the empty recent list asserted to say so, and a tool pressed asserted to answer “Open a document first.” |
| **A document still opens the way a person opens one** | The report opened through the file picker, asserted to have its pages, and the Organize card asserted to open the organizer |
| **Prepare Form, driven in a browser** | The flat form opened, the tool pressed, the dialog asserted to list all four candidates by name, one unticked, and the field count asserted to rise by exactly the rest. Screenshot: `qa/audit-prepare-form.png` |
| **Dead-button audit, static pass** | **235 controls checked, 274 static steps, 0 problems** — up from 232: the new tool card and the two controls in its dialog |
| **Dead-button audit, live pass** | **82 named steps, 0 failures** — **356 steps passed** across both passes |
| Existing 20 workflow checks | **Still 20 passed**, 0 JavaScript errors, 0 external requests |
| Existing 11 direct-edit checks | **Still 11 passed** |
| Sharing/Arabic/default-app checks | **12 passed** (was 11: the message box is now checked) |
| Existing 8 save checks | **Still 8 passed** |
| Hosted-preview privacy checks | **2 passed** — now measured from an empty start, so “nothing uploaded before consent” is proven rather than assumed |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **19 of 19 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 5 checks passed, including **every interface asset byte-identical to the source** |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What this release found and changed

1. **Removing the sample broke four checks and one promise.** The audit had
   asserted “nothing sits to the right of the page” and, elsewhere, waited for
   the sample to reappear after a reload. Both are now written against an
   application that starts empty: the audit opens the report itself, through the
   file picker, and `reopen_report()` puts it back after a reload instead of
   assuming the application did it.
2. **Opening a file sets the view twice** — once before the upload is adopted and
   once after it is rendered. Clicking Home in between put the editor back on
   screen. The audit now waits for the “Opened …” toast, which is raised only
   when the whole sequence has finished.
3. **The audit's print step had a pluralisation bug** (`Print 1 pages`) that only
   showed up once a one-page document reached it. It now builds the expected
   string the way the interface does.
4. **A date field that only KADOMA understood.** The existing date fields carried
   private keys and nothing else, so another reader saw a plain text box with no
   format. Prepare Form now writes Acrobat's own `/AA` actions as well, which is
   what makes its calendar button appear.
5. **The driver is allowed to correct the request.** A printer that reports no
   two-sided support normalises `long` back to `simplex`; the summary reports what
   the driver said, not what was asked for, and the test asserts that.

### What is honestly not covered

- **Two-sided printing could not be exercised end to end here.** Every printer
  installed on this machine is a virtual one and reports no duplex support, so
  the control is correctly shown disabled. The setting path is covered by tests;
  paper coming out on both sides is not.
- **Acrobat itself was not run.** The date actions are the ones Acrobat writes,
  and the PDF structure is asserted, but “Acrobat shows its picker” is an
  expectation, not an observation on this machine.
- **Prepare Form is rule-based.** It finds underscore rules, drawn boxes and
  `Label:` lines. It does not understand a form laid out as a table with no rules,
  and it will occasionally offer a field where a line was a separator — which is
  why every candidate is listed and can be unticked before anything is added.
- **500 MB is a limit, not a promise about memory.** A 500 MB document is held in
  memory while it is open; on a machine with little RAM, opening one will be slow
  or fail. Undo is capped separately at 100 MB of snapshots.
- **The email is still not sent by KADOMA.** The draft is handed to the mail
  program and nothing leaves the machine until somebody presses Send.

## 0.25.0 — paper and orientation in print, a 150% page, and the email draft

Date: **26 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.24.0 and earlier results below are retained. This release answers three
requests.

| What was asked | What is there now |
|---|---|
| The email option should create a draft with the PDF attached and the body “Please see the attached file” | The first share option builds a real MIME message with the PDF inside it and that sentence as the body, then hands it to the mail program. The second option is now labelled **without the file**, because `mailto` cannot carry one. |
| The default PDF view should be 150% | A document opens at **150%**. The zoom control still overrides it, and the audit asserts the opening value rather than assuming it. |
| The print preview should offer paper size, orientation and other printing preferences | **Paper** and **Orientation** are chosen in the preview, from the list the **driver itself reports** (`DeviceCapabilities`). The choice is written into the driver's own settings block, so the sheet that is drawn is the sheet that is printed. Everything else — duplex, quality, trays — stays in **Printer properties**. |

| Check | Actual result |
|---|---|
| Engine/API test suite | **302 passed**, 2 skipped, **0 failed** — up from 296. **6 new tests**: 2 for the email body, 4 for the paper settings |
| **The draft really carries the file and says the sentence** | The `.eml` is parsed back and the body asserted to be exactly `Please see the attached file`, with **one** attachment, `application/pdf`, byte-for-byte the document |
| **The `mailto` route says the same thing** | The opened URL asserted to carry `Please%20see%20the%20attached%20file` |
| **The paper list is the driver's** | `DeviceCapabilities` asserted to return sizes with numeric ids and names, including A4 or Letter — a list with neither would not be a paper list |
| **Paper and orientation really change the sheet** | Portrait asserted to be taller than wide; the same paper in landscape asserted to swap the two sides within 2 pt; a second paper asserted to change the size and to be recorded in the driver's block |
| **Impossible settings are refused with a reason** | `sideways` refused, paper `0` refused, paper `'A4'` (a name where an id belongs) refused |
| **Asking for nothing changes nothing** | The summary before and after a no-op call asserted identical |
| **The preview turns with the sheet** | In a real browser: the paper list asserted filled and enabled, A4 chosen and confirmed in the note, then landscape — the preview image asserted to go from taller-than-wide to wider-than-tall |
| **The job is printed on that paper** | The captured print job was **opened and measured**: A4 landscape, 842 × 595 pt ± 12. This is the check that stops the preview and the paper from drifting apart |
| **The document opens at 150%** | The zoom control asserted to read `1.5` on arrival, then zoom in asserted to change the page width, then 50% and Fit width, then back to 150% so later steps see the same page |
| **Dead-button audit, static pass** | **232 controls checked, 271 static steps, 0 problems** — up from 230: the paper select and the orientation select |
| **Dead-button audit, live pass** | **81 named steps, 0 failures** — **352 steps passed** across both passes |
| Existing 20 workflow checks | **Still 20 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Existing 8 save checks | **Still 8 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **19 of 19 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What this release found and changed

1. **The paper list could not be a table in the source.** A hand-written list
   would offer A3 to a driver that has never heard of it, and the driver would
   then print on whatever was loaded. It is asked of the driver, per printer, and
   the list is re-read when the printer changes.
2. **The preview and the job were two settings away from disagreeing.** Writing
   the choice into the driver's settings block — the same block `CreateDC` is
   given — is what makes them one thing. The audit proves it by measuring the
   captured job rather than the label.
3. **The audit's zoom step had a vacuous assertion.** It ended with
   `... or True`, which passes whatever happens. It now asserts the opening zoom,
   that zoom in changes the page width, and that Fit width can be chosen.
4. **The email body was wrong, not the attachment.** The `.eml` route already
   attached the PDF; what it said was “Hello, … Please find the attached
   document … Sent from KADOMA PDF”. It now says the sentence that was asked for,
   and both email routes share one constant so they cannot drift.

### What is honestly not covered

- **Paper and orientation are Windows-only.** They go through the driver's
  `DEVMODE`. On macOS and Linux the two controls are shown disabled and the
  dialog says the printer does not report its paper sizes, rather than pretending.
- **The choice belongs to the driver, for the session.** Changing the paper for
  one job leaves the printer set that way, exactly as changing it in the driver's
  own dialog would.
- **Duplex, quality, tray and colour are not in this dialog.** They stay in
  Printer properties: they differ per driver, and the driver can describe them.
- **150% is a size, not a fit.** A very large page at 150% needs horizontal
  scrolling; Fit width is one press away for that.
- **The email is still not sent by KADOMA.** The draft is handed to the mail
  program and nothing leaves the machine until somebody presses Send.

## 0.24.0 — the tool list beside the document, and one page out as a file

Date: **26 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.23.0 and earlier results below are retained. This release answers two
requests: the tool list from the home screen should also be available while
reading a PDF, and right-clicking a page should copy that page out to a file
whose name you choose.

| What was asked | What is there now |
|---|---|
| The right-hand tool list from Home, also while viewing a PDF, hideable | The same list, built from the same `HOME_TOOLS` array and calling the same handler, now sits on the **right of the workspace** in every document view. **All tools** in the menu bar puts it away and brings it back; hiding it returns its 186 px to the page. Home keeps its own copy. |
| Right-click a page while scrolling → copy that page → rename the file | **Copy page to a file…** in the page menu, on the scrolling page as well as on a thumbnail. The dialog suggests `<document> — page N.pdf`, and what is typed becomes the file name. The page is written as a one-page PDF through the same path as an export: the desktop build opens a real Save dialog, the browser preview downloads it. |

| Check | Actual result |
|---|---|
| Engine/API test suite | **296 passed**, 2 skipped, **0 failed** — up from 295 |
| **A one-page export is named after the page** | `/export/pdf` with `pages: [2]` asserted to answer with a `page-003.pdf` disposition and a document that really is **one page**; exporting the whole document asserted to keep its own name |
| **The tool list is beside the document** | Asserted visible in the editing view with **18 tools**, and hidden on the home screen, which has its own copy |
| **A tool in that list is a real action** | Pressing **Watermark** in the right-hand list asserted to switch to the Document view **and** open its dialog — not merely to highlight |
| **It can be put away** | The toggle asserted to hide the list, to report `aria-pressed="false"`, and to bring it back on the second press |
| **It costs the page its own width, and no more** | With the list away the page area was asserted to reach the right edge of the window (1500 of 1500); with it back, the list asserted to sit at the right edge, the page area to stop where the list begins, and the page to be **at least 20 px narrower** |
| **Focus now means nothing but the page** | Pressing Focus asserted to hide the tool list **and** the tools panel, and pressing it again to bring both back to the width they had before |
| **A page can be copied out with a typed name** | Right-click on the scrolling page, the menu asserted to offer the item, the dialog asserted to suggest a name ending in `.pdf` and mentioning the page, then a name with `/` and `:` in it typed and saved. The **download was captured, written to disk, opened, and counted: 1 page, with text in it** |
| **Characters a file name cannot hold are cleaned, not refused** | `audit copy: page/one` asserted to arrive as `audit copy- page-one.pdf` |
| **The copy is a copy** | The document on screen asserted to keep its page count and revision — the copy is an export, not an edit |
| **Dead-button audit, static pass** | **230 controls checked, 269 static steps, 0 problems** — up from 227: the new toggle, the rail's list, and the three fields of the copy dialog |
| **Dead-button audit, live pass** | **80 named steps, 0 failures** — **349 steps passed** across both passes |
| Existing 20 workflow checks | **Still 20 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Existing 8 save checks | **Still 8 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **19 of 19 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What this release changed, and what it broke on the way

1. **The panel layout had a promise that no longer holds.** The audit used to
   assert that *nothing* sits to the right of the page. That was true when the
   only panels were on the left; a list on the right is a thing somebody asked
   for. The check was rewritten rather than deleted: with every panel away the
   page still reaches the right edge of the window, and with the list showing it
   is a column on the right that costs the page exactly its own width.
2. **Focus was defined as "both panels hidden".** With a third panel that
   definition quietly stopped meaning "the largest page". Focus now hides the
   tool list as well, and the second press restores the tools and the list to the
   width they had — asserted as an exact width, not as "it got bigger".
3. **A single-page export was named after the whole document.** Exporting page 3
   of a report produced `Report.pdf`, which is misleading in a folder next to the
   original. It now produces `Report-page-003.pdf`, matching what the split
   export already did.

### What is honestly not covered

- **The file name is a name, not a location.** The dialog chooses what the file
  is called; where it goes is the desktop Save dialog's business, and the browser
  preview puts it wherever downloads go.
- **The copy is of one page at a time.** Two pages at once is the export dialog,
  which already has a page range.
- **The tool list is not configurable.** It shows every tool, in the same order
  as Home; it cannot be reordered or trimmed.
- **Its visibility lasts for the session.** Like every other panel arrangement
  here, it is not remembered after the application closes.

## 0.23.0 — stamps, links, page size and a document comparison

Date: **25 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.22.0 and earlier results below are retained. This release answers a request
to bring KADOMA closer to Acrobat Pro, and takes the four tools that the previous
comparison named as the most useful missing ones. `docs/ACROBAT-PARITY.md` has the
updated table.

| Tool | What it does |
|---|---|
| **Stamp** | Approved, Reviewed, Draft, Confidential, Final, For Public Release, Void — or your own text — drawn **where you click**, with an optional date underneath. |
| **Link** | Drag a box on the page, then point it at a web address or a page in the same document. Listed per page, removable one at a time. |
| **Page size** | A3 / A4 / A5 / Letter / Legal / Tabloid, or a custom size in mm, pt or in, with the content **and** every form field, comment and link scaled to fit. |
| **Compare** | Two open documents or a file, page by page and word by word: which pages differ, and what was added or removed on each. |

| Check | Actual result |
|---|---|
| Engine/API test suite | **295 passed**, 2 skipped, **0 failed** — up from 276. **19 new tests** in `tests/test_document_tools.py` |
| **A stamp is really in the page** | Asserted as extractable text on the page it was placed on **and not on the one before it**, and found at the x it was clicked at rather than in a corner |
| **A stamp near the edge stays on the page** | A stamp placed at x=560, y=830 on a 595 × 842 page asserted to be fully inside the page box |
| **A stamp with a date** | The date asserted present as text under the label |
| **An invented stamp is refused** | `label: 'Excellent'` asserted to raise rather than draw something |
| **A custom stamp needs its text** | Blank custom text asserted to raise; real text asserted to appear |
| **A link can be added, listed and removed** | Asserted: the list starts empty, one link added, listed with its address and kind, then removed and `get_links()` empty |
| **A page link points at the page chosen** | Target page 3 asserted to produce `Page 3` and link entry `page: 2` |
| **A link address must be an address** | `example.org` (no scheme) asserted to raise with the reason |
| **A link box must be clickable** | A 1 × 1 pt box asserted to raise rather than create an unusable link |
| **Removing a link that is gone says so** | Index 3 on a page with none asserted to raise |
| **Resizing really changes the paper and the drawing** | A4 → A5 asserted as a 420 × 595 page box, and the text asserted to have moved to 0.705 of its former position on both axes |
| **Resizing without scaling moves nothing** | Letter from A4 with scaling off: the page box changes and the text is asserted to stay at the same x and y |
| **Resizing carries forms, links and highlights** | A form field, a link and an underline annotation asserted present afterwards at the scaled positions — this is the check that caught links being copied instead of moved |
| **Resizing only the pages chosen** | Page 2 of 3 resized to A5 asserted to leave page 1 at 595 pt |
| **A custom size is measured in its unit** | 100 × 150 mm asserted as 283.46 pt wide; an unknown unit refused |
| **Comparing a document with itself finds nothing** | `identical: true`, 0 differing, 2 pages compared |
| **A changed page names the words that changed** | One sentence added to page 2 asserted to report exactly one differing page, `sentence.` among the added words, and nothing removed |
| **A page on one side only is reported** | 2 pages against 1 asserted `removed`, and the reverse direction `added` |
| **Comparing edits nothing** | The revision asserted unchanged after a comparison, and an empty document name refused |
| **Dead-button audit, static pass** | **227 controls checked, 266 static steps, 0 problems** — up from 206: the two new toolbar tools, two new Document cards, and every field in the four new dialogs |
| **Dead-button audit, live pass** | **78 named steps, 0 failures** — **344 steps passed** across both passes |
| **The four tools, driven in a browser** | A stamp armed from the toolbar, placed by clicking the page and asserted in the page's text; a link drawn by dragging, added, listed, a bad address refused with the reason, then removed; the page resized to A5 with the page count unchanged; a blank document opened and compared against the document under audit, asserted to report "PAGES DIFFER". Screenshots: `qa/audit-stamp.png`, `qa/audit-compare.png` |
| Existing 20 workflow checks | **Still 20 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Existing 8 save checks | **Still 8 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **19 of 19 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What this release found and fixed

1. **A stamp came out blank, and then twice.** `insert_textbox` returns a failure
   when the box is even slightly too short for one line — but it has already
   written the text. Retrying at a smaller size therefore left the label on the
   page twice, and trusting the return value alone would have shipped a bordered
   frame with nothing in it. The label is now measured and drawn with
   `insert_text`, centred by arithmetic, so there is nothing to retry.
2. **A link could not be listed straight after it was added.** PyMuPDF keeps a
   page's link list from the moment it was loaded, so `get_links()` reported an
   empty page immediately after `insert_link`. The new link is the last entry in
   the annotation array, so it is appended to the list rather than re-read, and a
   removal renumbers what is left.
3. **Resizing copied links instead of moving them.** The first version called
   `insert_link` with a scaled rectangle, which left the original behind at the
   old size — two links, one of them pointing at the wrong place. A link is an
   annotation with a `/Rect`, so it is now moved the same way a form field is.
4. **`reload_page()` is not safe to use here.** It asserts inside PyMuPDF when the
   page is still referenced elsewhere, which is a crash rather than an error. It
   was dropped; the annotation array is read from the xref instead, which is
   always current.
5. **Reading an annotation's rectangle after its page has been collected
   segfaults.** Found while writing the resize test — the test held a temporary
   page. The geometry pass now reads `/Rect` straight from the xref, so it does
   not depend on an annotation object's lifetime at all.
6. **Shrinking the paper moved the content up the page.** `set_mediabox` keeps PDF
   coordinates, so A4 → Letter moved everything 50 pt up. The drawing is now
   anchored at the top-left corner in both modes, scaled or not.
7. **The audit raced a stopwatch.** Its search step waited a fixed 800 ms for the
   engine's results and failed once on a busy machine; it now waits for the
   results, and names the document and the query if they never arrive.
8. **Two audit selectors pointed at the wrong toolbar.** The stamp and link
   buttons live on the editing toolbar, not the Document view's.

### What is honestly not covered

- **The comparison is of words, not of pixels.** A moved paragraph reads as
  removed and added. It does not render the two pages side by side, and it does
  not compare images, drawings or layout.
- **Resizing scales uniformly** — the smaller of the two factors — so a change of
  aspect ratio leaves a margin rather than stretching the content.
- **A stamp does not avoid collisions.** It is drawn where it is clicked, which
  can be on top of existing text.
- **Links are web addresses and page jumps only.** No JavaScript actions, no
  links to other files, and no editing of a link's rectangle after it is made.
- **The stamps are drawn marks, not Acrobat's standard stamp annotations.** They
  carry the right words and colour, and are real text, but a reader that lists
  "stamps" by their standard name will not find them under one.

## 0.22.0 — the Document view: watermark, numbering, crop, bookmarks, attachments, size

Date: **23 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.21.0 and earlier results below are retained. This release answers a request
to study Acrobat Pro and add the tools KADOMA was missing.

**What was studied, and what was not.** The comparison is of **capabilities**,
taken from Acrobat Pro's public tool set — the list Adobe publishes and the list a
person sees in *All tools*. The package added to the workspace is an unofficial
Acrobat Pro DC 2024 build containing a `Crack` folder; it was **not**
reverse-engineered. Taking apart commercial software is forbidden by its licence
and was not needed: the feature list is public, and every tool below is written
from scratch against PyMuPDF. The comparison, including what is still missing, is
in `docs/ACROBAT-PARITY.md`.

**What was missing, and is now there.** Seven tools, in a new **Document** view:

| Tool | What it does |
|---|---|
| **Watermark** | Text or an image; opacity, any angle, centre / tile / top / bottom, page range. Image transparency is kept and faded on top of that. |
| **Header & footer** | Six slots with `{page}`, `{pages}`, `{date}`, `{filename}`, `{title}`, `{bates}`. |
| **Page numbers / Bates** | A format string, or a prefix with padded digits and a starting number, in six positions. |
| **Crop** | Margins in mm, points or inches, per side, any page range. |
| **Bookmarks** | List, add, remove, clear, and **generate from the type sizes**. |
| **Attachments** | Add, list, extract and remove files embedded in the PDF. |
| **Reduce size** | Image downsampling and re-encoding, font subsetting, object cleanup. |

| Check | Actual result |
|---|---|
| Engine/API test suite | **276 passed**, 2 skipped, **0 failed** — up from 250. **26 new tests** in `tests/test_document_tools.py`, one or more per tool plus its refusals |
| **A watermark is really in the page** | Asserted as extractable text on every page; a 0.05-opacity watermark is asserted to be **at least 60 levels lighter** than a 1.0 one, measured on a blank page so the body text cannot be mistaken for it |
| **Tokens really expand** | `Page {page} of {pages}` asserted to read `Page 1 of 3` on page one and `Page 3 of 3` on page three; `{page}` with a start of 10 reads `Page 10`; an unknown token raises rather than printing |
| **A header is above the body and a footer below it** | Asserted by comparing the y positions of the extracted text, not by trusting the layout code |
| **Bates numbering** | `ABC-` with six digits starting at 42 asserted to produce `ABC-000042` … `ABC-000044` |
| **Crop** | 10 mm a side asserted to shrink the page box by 56.7 pt in both directions, **with the text still present** — cropping hides, it does not delete |
| **Bookmarks from headings** | A two-level document asserted to produce level 1 `Chapter 1` and level 2 `A section heading`; a first entry at level 2 asserted to be normalised to level 1 so readers accept the tree |
| **A watermark is not a heading** | Asserted on a four-page document (it repeats) **and** on a one-page document (no repetition to measure — the rotated direction excludes it). The first version offered the watermark as a chapter title; this is the fix |
| **Attachments round-trip** | Bytes attached, listed with the right size, extracted **identical**, then removed; adding the same name twice refused |
| **Compression** | A page with a noisy 1200×900 image asserted to come out **no larger**, with the page count and the text intact |
| **The tools are undoable** | A watermark asserted searchable after the operation and **gone after undo**; listing bookmarks asserted to leave the revision untouched (a read is not an edit) |
| **Dead-button audit, static pass** | **206 controls checked, 243 static steps, 0 problems** — up from 157: the Document view, its seven cards, seven toolbar buttons and every dialog field |
| **Dead-button audit, live pass** | **77 named steps, 0 failures** — **320 steps passed** across both passes |
| **The whole view, driven in a browser** | The view asserted to list seven tools and the toolbar to carry the same seven; then a watermark asserted searchable, a Bates number asserted present, the page box asserted smaller after crop, bookmarks asserted generated **without the watermark**, an attachment attached, listed and removed, and compression asserted to report a size |
| Existing 20 workflow checks | **Still 20 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **19 of 19 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What this release found and fixed

1. **The heading detector offered the watermark as a chapter title.** It looked
   for text larger than the body size, and a 54 pt watermark is the largest thing
   on the page. Two filters now: text that repeats on more than a third of the
   pages is furniture, and text whose direction is not horizontal is a watermark
   or a sidebar. The second was needed because a **one-page** document has no
   repetition to measure — which is exactly the case the audit hit.
2. **A wrapped title became two bookmarks** — "Quarterly" and "performance
   report". Consecutive lines of the same size at the same left edge are joined.
3. **The outline tree was rejected by PyMuPDF** when the first detected heading
   was not level one. Entries are normalised: the first is level one, and a level
   may never jump by more than one.
4. **`PDFError` lived in the engine**, so a separate module raising it would have
   been a circular import — visible only at run time, on whichever tool was used
   first. It moved to `app/errors.py` and is re-exported from the engine, so every
   existing `from app.engine import PDFError` still works.

### What is honest about this

- The seven tools are **tested against the engine and driven through the
  interface**, but the frozen build's self-test does not exercise them
  individually. What it does prove is that the module is bundled and the
  application starts — the engine imports it on load, so a missing import would
  fail the launch check.
- **Compression is only as good as the images.** A text-only PDF comes out a few
  per cent smaller; a scan-heavy one can halve. The dialog says what happened
  rather than promising a figure.
- **Bookmark generation is a heuristic.** It reads type sizes. A document with no
  size hierarchy produces a short outline or none — not a guess per line.
- **Attachments are embedded, not linked**, and are not compressed beyond the
  PDF's own deflate.
- **No certificate-based signatures, no document comparison, no batch actions.**
  `docs/ACROBAT-PARITY.md` lists them and says why.

### Still open / unverified

- No physical printer, the printer-properties dialog is still unopened by a
  human, no macOS build, no installer.
- The print hang reported in 0.17.0 remains unreproduced.
- The date tool places the date where it is clicked, so it can overlap existing
  text.

## 0.21.0 — closing only asks when there is something to save

Date: **23 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2, pywebview 6.2.1 (EdgeChromium). Development
verification, **not independent security certification**.

The 0.20.0 and earlier results below are retained. One request: **remove the
popup when closing the app — it should only appear if the PDF needs saving, and
otherwise close directly.**

**What was wrong.** The window was created with `confirm_close=True`, which asks
*"close this window?"* on every single close — including for a document nobody had
touched. That dialog knows nothing about the document; it is a property of the
window, not of the work. Quitting was a two-click ritual for no reason.

**What it does now.** `confirm_close=False`, and the decision moved to the
window's `closing` event, which knows whether there is anything to lose:

- **Nothing unsaved** → the window closes at once. No dialog of any kind.
- **Something unsaved** → the close is cancelled and the application's own prompt
  appears: **Save and close**, **Close without saving**, or **Cancel** (which
  leaves the window open). If the save fails or its file dialog is cancelled, the
  window stays open rather than closing over unsaved work.

The page tells the shell whether anything is unsaved whenever that answer
changes, rather than the shell asking at close time. A question asked *during*
the closing event needs the same GUI thread that is closing, which is how a close
handler deadlocks; the answer is kept ready instead.

| Check | Actual result |
|---|---|
| Engine/API test suite | **250 passed**, 2 skipped, **0 failed** — up from 245. Five new on the close decision: a fresh bridge does not ask; a page reporting changes does; a second answer re-arms the question; quitting from the page clears the flag and destroys the window; quitting without a window does not raise |
| **The real window closes with no dialog** | The built EXE is launched, its window found by title, and **WM_CLOSE posted as a person's close press would be**. The window was gone **2.7 s later** and the process exited 0 — a blocking dialog would have left it open. That is the complaint, tested |
| **pywebview's close semantics, measured here** | A probe window with the same pattern: a handler returning `False` **kept the window open**, `evaluate_js` from a timer thread **reached the page** while the close was cancelled, and allowing the close then closed it. The mechanism this release depends on, verified on this machine rather than assumed |
| **Dead-button audit, static pass** | **157 controls checked, 190 static steps, 0 problems** |
| **Dead-button audit, live pass** | **76 named steps, 0 failures** — **266 steps passed** across both passes |
| **A clean document closes with no prompt** | A fresh document is created, the shell bridge is stood in for, and the page is asserted to report **`set_unsaved(false)`**; closing is asserted to quit **without opening any dialog** |
| **A changed document asks, and Cancel keeps it open** | After a rotation the page is asserted to report **`set_unsaved(true)`**; closing is asserted to open **Save your changes?**; Cancel is asserted to leave the window open (no quit) |
| Existing 20 workflow checks | **Still 20 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **19 of 19 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What this release found and fixed

1. **The close dialog was unconditional.** `confirm_close=True` asks the window,
   not the document. Replaced with a `closing` handler driven by the page's own
   answer.
2. **Two `beforeunload` handlers** had accumulated, one from 0.17 and one older.
   There is now one, and it stays out of the desktop shell's way — otherwise a
   close with unsaved work would show two dialogs for one press.
3. **The bridge arrives after the first render**, so a change made in the first
   moment could never reach the shell. The page now re-sends its answer on
   `pywebviewready`.

### What is honest about this

- The **dirty** close was verified in two halves, not as one end-to-end run: the
  page-side decision and dialog in a real browser, and pywebview's
  cancel-then-ask mechanism in a probe window. Driving a native window's UI is not
  scriptable here, so nobody has clicked *Save and close* on the real window with
  a real edit in it.
- The **browser preview** still shows the browser's own "leave site?" prompt when
  there are unsaved changes. That is the browser's dialog, not ours, and it only
  appears when there is something to lose.
- Closing still takes about **2.7 s** while the local service shuts down; that is
  teardown, not a dialog.

### Still open / unverified

- No physical printer, the printer-properties dialog is still unopened by a
  human, no macOS build, no installer.
- The print hang reported in 0.17.0 remains unreproduced.
- The date tool places the date where it is clicked, so it can overlap existing
  text.

## 0.20.0 — a scan you can actually edit, and a date you can place

Date: **23 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2, Tesseract 5 (installed). Development verification, **not
independent security certification**.

The 0.19.0 and earlier results below are retained. Two reports: **a scanned PDF
is still not editable**, and **the date must be placed inside the PDF so it can
be selected, depending on the date chosen**.

**Why the scan was not editable.** There was exactly one way in, and it was
gated: press *Make it editable*, which ran Tesseract, which has to be installed,
and which replaces the page with a 200-DPI raster. Clicking a line did nothing —
correctly, because a scan has no text layer, but the tool did not say so where
the person was clicking. A PDF that is a picture of text therefore felt broken.

There are now two ways in, and the first needs nothing installed:

1. **Drag a box over the words.** The text tool draws instead of clicking when
   the page has no text layer. The old ink is painted over with the colour
   sampled from a ring of paper just outside the box — **not white**, which
   would leave a bright rectangle in the middle of a grey scan — and the
   replacement is written as real text on top. An empty box erases the area.
2. **Make it editable** still runs local OCR, after which every line is
   clickable. If recognition comes back empty, it now says so instead of
   claiming success.

**The date.** A new **Date** tool asks for a date — typed, or picked from a
calendar — with a format, size and colour, then writes it into the page where
you click, as real text. It is selectable, searchable and copyable in any reader,
and it works on a scan.

| Check | Actual result |
|---|---|
| Engine/API test suite | **245 passed**, 2 skipped, **0 failed** — up from 240. Five new: a page with no text layer reports no spans; erasing part of a scan leaves **no ink and the paper's own colour** (not white); a replacement is written as **real text** and is found by search; a date written onto a scan comes back as exactly one span; the sampled background of a dark scan is mid-grey |
| **The ink is really covered** | Asserted by pixel: the darkest pixel under the box is **> 180** after an erase, and the patch at a former ink pixel is **within 14/255 of the paper colour**. A white-fill implementation fails this |
| **The replacement is really text** | Asserted through `engine.search()` as well as the span list, so a version that drew the words as an image would fail |
| **Dead-button audit, static pass** | **157 controls checked, 190 static steps, 0 problems** — up from 150: the Date tool, its calendar, format, size, colour and Place button |
| **Dead-button audit, live pass** | **75 named steps, 0 failures** — **265 steps passed** across both passes |
| **A scan is edited by dragging** | A raster-only page is uploaded, asserted to have **0 text runs**, the text tool asserted to switch to **drawing**, a box dragged over the words, the panel asserted to say **Scan selection**, and the replacement asserted to be in the page as text |
| **The date is in the page** | The Date tool is asserted to open **Place a date.**; a calendar day is clicked and the value asserted to follow it; the format changed and the **date** asserted to survive (not the digits); `31/02/2026` asserted to **disable** Place with a reason; a valid date asserted to arm the tool, the hint to name it, and the click to put **`15/03/2026` in the span list** |
| Existing 20 workflow checks | **20 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **19 of 19 checks passed** (`frozen: true`) — two of them new, and both about this release: a scanned page edited **inside the packaged build** (erase, then assert by pixel that the ink is gone, then add text and find it by search), and **`pytesseract` present in the bundle**, which is what OCR needs and what a missing hidden import would break |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What this release found and fixed

1. **The calendar inside a dialog could not be clicked.** A `<dialog>` lives in
   the browser's top layer; a popover appended to `<body>` is painted underneath
   it, visible but unreachable, with every press landing on the dialog. The
   first version of the date prompt therefore had a calendar that did nothing.
   The popover is now appended to the open dialog when there is one. Found by
   the date test, not by looking at it.
2. **The capability list still advertised an 80 MB limit** after 0.17 raised it
   to 250. It reads `MAX_UPLOAD` now, like the error messages do.
3. **The OCR path claimed success on an empty result.** A skewed or
   low-resolution page can recognise nothing; the toast said "Text recognised"
   regardless. It now says nothing was recognised and points at the drag method.

### What is honest about editing a scan

- The drag method **destroys what is underneath**: the pixels are removed and
  painted over. That is the point, and the panel says so before anything runs.
- It replaces **a box**, not a reflowed paragraph. Typing more than the box holds
  makes the text shrink to fit, exactly as Add text does.
- OCR quality depends on the scan, needs Tesseract installed, and **replaces the
  page with a raster** — annotations on it are flattened and form fields removed.
- A **click** without a drag does nothing on a scan; the gesture is a drag, and
  the banner and the hint both say so.

### Still open / unverified

- No physical printer, the printer-properties dialog is still unopened by a
  human, no macOS build, no installer.
- The print hang reported in 0.17.0 remains unreproduced.
- The date tool places the date **where you click**, which can be on top of
  existing text; it does not avoid collisions.

## 0.19.0 — the window title is the name, and nothing else

Date: **22 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.18.0 and earlier results below are retained. One request: remove the
**“Offline PDF Studio”** subtitle from the top of the application.

| Check | Actual result |
|---|---|
| Engine/API test suite | **240 passed**, 2 skipped, **0 failed** — untouched by a title change |
| **Dead-button audit** | **256 passed, 0 failed** — 150 controls, 183 static steps, 73 live steps, unchanged |
| **The window title, read from the real window** | `check_exe.py` reads the title out of the running Win32 window and compares it to the string in `desktop.py`: **`KADOMA PDF`** |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled **`KADOMA PDF`** |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What changed

- The desktop window title: `KADOMA PDF — Offline PDF Studio` → **`KADOMA PDF`**.
- The browser tab title, for the preview: `KADOMA PDF — Offline PDF Studio` →
  **`KADOMA PDF`**.
- The header line of the getting-started guide: `OFFLINE PDF STUDIO / GETTING
  STARTED` → **`KADOMA PDF / GETTING STARTED`**.

### Why the offline claim was not simply deleted

It is still made, in two places where it means something: the status bar says
**“All processing happens on your device”** and **“No uploads. No account. Just
your files.”**, and the guide's scope card says the same in more detail. A
subtitle in a title bar is not where somebody checks whether their files leave
the machine.

### Still open / unverified

- No physical printer, the printer-properties dialog is still unopened by a
  human, no macOS build, no installer.
- The print hang reported in 0.17.0 remains unreproduced.

## 0.18.0 — a password prompt that asks, a quieter top bar, and scans that become editable

Date: **22 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.17.0 and earlier results below are retained. Three requests: protection
should **ask for a password to set**, the **workspace and offline labels** should
go from the top of the window, and **editing a scanned PDF** should actually work.

| Check | Actual result |
|---|---|
| Engine/API test suite | **240 passed**, 2 skipped, **0 failed** — unchanged; this release is interface and flow |
| **Dead-button audit, static pass** | **150 controls checked, 183 static steps, 0 problems** — up from 142, all from the new password prompt |
| **Dead-button audit, live pass** | **73 named steps, 0 failures** — **256 steps passed** across both passes |
| **The password prompt asks, and refuses** | The Protect button is asserted to open **“Set a password.”** with the action disabled; `abc` is asserted to produce *“The opening password needs at least 6 characters”* and keep it disabled; a valid pair is asserted to enable it |
| **The password really encrypts** | The exported copy is opened in PyMuPDF: **`needs_pass` is 1**, and `secret123` authenticates it as a user. A 4-page document stays 4 pages |
| **A scan becomes editable in one press** | A raster-only page (one image, no text layer) is uploaded: **0 text runs**, the banner appears, **Make it editable** runs local OCR, and the same page then has **5 editable runs**, the text tool armed, and a click opens the in-place editor. Added as a 20th workflow check |
| **The top bar carries neither label** | The breadcrumb and the offline badge are gone from the markup; the hosted-preview warning now lives in the status bar, which says more than the badge did |
| Existing 19 workflow checks | **20 passed** — 19 unchanged plus the scan check |
| Existing 9 direct-edit checks | **Still 9 passed**; one now waits for the render scale to settle after a zoom change, because the page stack is rebuilt then |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**; the badge assertion was removed with the badge, the status-bar assertions remain |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF — Offline PDF Studio` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |

### What changed, and why it was not working

1. **Protection was a panel, not a prompt.** The fields existed in the Protect
   panel, but nothing asked for a password: pressing the tool left you looking at
   a form you had to notice. It is now a dialog — **Set a password.** — with the
   opening password typed twice, an owner password, a reveal button, live
   validation that names the actual problem, and a button that stays disabled
   until the passwords are usable. The panel behind it still works for people who
   prefer it, with the permissions spelled out.
2. **A scan had nothing to click, and the tool said nothing.** “Edit text” on a
   page that is a picture cannot work — there is no text layer. The page now says
   so **on the page itself**, and **Make it editable** recognises the page with
   local OCR and hands the text tool straight back. One press, and clicking a line
   opens the editor. If Tesseract is not installed it goes to the OCR panel, which
   explains how to install it, instead of pretending.
3. **The top bar had two labels that earned nothing.** “Workspace › PDF editor”
   repeated the tab strip, and “Offline workspace” repeated the status bar — which
   says it better and also carries the hosted-preview warning.

### What is honest about the scan path

- It needs **Tesseract** installed locally. Without it the button routes to the
  OCR panel rather than failing silently.
- OCR **replaces the page with a searchable 200-DPI raster**: annotations on that
  page are flattened and form fields on it are removed. The confirmation says so
  before anything runs.
- Recognition is good, not perfect. The test asserts that the recognised text is
  clickable and editable, not that every word is right.

### Still open / unverified

- No physical printer, the printer-properties dialog is still unopened by a
  human, no macOS build, no installer.
- The print hang reported in 0.17.0 remains unreproduced; the deadline is still
  the mitigation.
- OCR quality depends on the scan. A skewed or low-resolution page will recognise
  less, and the tool does not tell you how confident it is.

## 0.17.0 — tabs, a scrolling page view, and nine fixes

Date: **22 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.16.0 and earlier results below are retained. This release carries nine
requests at once: tabs for open documents, a 250 MB limit, a scrolling page view,
printing that does not appear to hang, 100% as the default zoom, a right-click
page menu, showing the result of a merge, scanned pages that explain themselves,
and a save prompt when closing.

| Check | Actual result |
|---|---|
| Engine/API test suite | **240 passed**, 2 skipped, **0 failed**. One existing test was updated: the request-size guard now refuses 300 MB instead of 100 MB, because the working limit is 250 MB |
| **Dead-button audit, static pass** | **142 controls checked, 174 static steps, 0 problems** — up from 139: the tab strip, the page menu items and the scan notice's button |
| **Dead-button audit, live pass** | **71 named steps, 0 failures** — **245 steps passed** across both passes |
| **Every page is on screen** | A four-page document is asserted to put **four page sheets** in the column, scrolling is asserted to change the current page, and scrolling back to the top is asserted to return to page one |
| **Tabs** | With two documents open the strip is asserted visible, the new document to have a tab, clicking the original's tab to switch back, and closing the other tab to leave the original open and remove that tab |
| **Right-click menu** | Right-clicking a page card is asserted to open a menu containing Rotate right, Rotate left, Extract page, Duplicate page and Delete page, and Escape to close it |
| **Save before closing** | A modified document is closed and asserted to ask **Save your changes?** with both a save and a discard button; Cancel is asserted to leave it open; closing without saving is asserted to close it |
| **Scanned pages** | The demo's blank scan page is recognised: no text layer, one image — and the tools panel offers the notice and the OCR button. Verified separately by uploading a raster-only PDF: the notice appears and **Make this page searchable** opens the OCR view |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** — clicking a line still edits it, on a scrolling page |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF — Offline PDF Studio` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **Rebuilding the page stack destroyed the editing layer.** The overlay, the
   selection box and the in-place editor live inside the current page; replacing
   the stack's markup took them with it, and the next render threw *Cannot set
   properties of null*. They are now moved back to a holder before the stack is
   rebuilt. Caught by opening a second document.
2. **Page images had no session token.** They were pointed at a relative URL by
   `<img src>`, which cannot carry the bearer token, so every page after the
   first came back 401 and showed as a broken image. They now go through the same
   authenticated fetch the thumbnails use — and into a **separate blob bucket**,
   because sharing the thumbnails' bucket meant re-rendering the thumbnail panel
   revoked the page images and blanked the document.
3. **`#paper` did not exist until the first render finished.** Switching to the
   editor built the stack but never assigned the editing layer, so any code that
   read `#paper` in that window threw. `applyZoom` now focuses the current page
   as part of sizing.
4. **The audit assumed fit-width was the default.** Two steps measured the page
   against the canvas width, which is only meaningful at fit-width; they now ask
   for it explicitly. The chrome measurement now includes the tab strip.

### The nine requests, and what each actually does

- **Tabs** — one per open document, shown when more than one is open, with a dot
  for unsaved changes and a close button that asks before discarding.
- **250 MB** — up from 80 MB for working documents and uploads; combining 250 MB;
  export 300 MB. The messages read the limit from the constant.
- **Scrolling** — every page in one column, lazily fetched, with the editing
  layer following the page in the middle of the window.
- **Printing** — the overlay now says *Sending 8 sheets to …* and the request has
  a three-minute deadline, after which it says the printer has not answered.
  **The reported hang could not be reproduced here**: printing to a real printer
  driver took 0.9 s for eight sheets. What was added addresses the two ways it
  can look stuck — no feedback, and no deadline.
- **100% zoom** — the default is now actual size; Fit width is one press away.
- **Right-click** — rotate left/right, extract, duplicate, delete on any page.
- **Merge shows its result** — both merge destinations switch to the document and
  scroll to the first page that was added.
- **Scans** — the page says it is a scan, offers OCR in one press, and lists the
  tools that still work.
- **Save on close** — Save and close / Close without saving / Cancel.

### Still open / unverified

- **The print hang was not reproduced.** If it still happens on a real printer,
  the deadline now turns it into a message after three minutes rather than an
  overlay that never clears — but the underlying cause is in the driver, not in
  this code, and I could not observe it.
- **Closing the window** (rather than a tab) relies on the browser's
  `beforeunload` prompt. Whether the desktop shell shows it depends on the
  WebView; the tab path is the one that is tested.
- No physical printer, the printer-properties dialog is still unopened by a
  human, no macOS build, no installer.

## 0.16.0 — odd and even pages, selected before they are deleted

Date: **21 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.15.0 and earlier results below are retained. This release answers one
request: in the Pages view, an option to **delete all odd or all even pages**, as
well as deleting a hand-picked selection.

**What was there before.** Deleting a chosen selection already worked — click
pages, press Delete. What was missing was a way to pick *half the document*
without clicking every other page: a 60-page scan needed 30 clicks to delete the
backs.

| Check | Actual result |
|---|---|
| Engine/API test suite | **240 passed**, 2 skipped, **0 failed** — unchanged, because this is a selection rule in the interface, not engine work |
| **Dead-button audit, static pass** | **139 controls checked, 168 static steps, 0 problems** |
| **Dead-button audit, live pass** | **67 named steps, 0 failures** — **235 steps passed** across both passes |
| **Odd and even mean what they say** | On a four-page document, **Odd** is asserted to select exactly `[0, 2]` (pages 1 and 3) and **Even** exactly `[1, 3]` (pages 2 and 4), counted from page one rather than from an array index |
| **None clears it** | **None** is asserted to leave the selection empty |
| **It really deletes, and it really undoes** | With the odd pages selected, Delete is asserted to ask, to leave **half the pages**, and undo to bring the document back to its original page count |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| Existing 8 saving checks | **Still 8 passed** |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF — Offline PDF Studio` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### Why selecting and deleting are separate presses

The request was to *delete* the odd or even pages. It is built as **select, then
delete** for one reason: on a long document, "the odd pages" is a claim about
which pages those are, and the only way to check it is to see them highlighted
before they go. So **Odd** and **Even** sit in a Select group with **All** and
**None**, the pages light up, and the existing Delete button removes them with
its usual confirmation and undo. One stray press cannot remove thirty pages.

### What this release found

Nothing broken. The four chips are ordinary buttons in the organizer header, the
selection rule is one small function, and the audit step that checks it passed on
the first run — which is the outcome to hope for and the one that says least
about the code. The step is still there because the rule is easy to break later:
"odd" counted from zero is the opposite of "odd" counted from one.

### Still open / unverified

- Deleting the **last remaining page** is still refused, as before; odd/even
  selection does not change that.
- No physical printer was used at any point in this project, the printer
  properties dialog has not been opened by a human, and there is no macOS build.

## 0.15.0 — collated and uncollated copies

Date: **21 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.14.0 and earlier results below are retained. This release answers one
request: when printing more than one copy, choose whether the copies come out
**collated** or **uncollated**.

**What was there before.** 0.14.0 added a copy count, but the order was fixed:
the pages were repeated in one job, which is collated. There was no way to ask
for a stack of page 1, a stack of page 2, and so on.

| Check | Actual result |
|---|---|
| Engine/API test suite | **240 passed**, 2 skipped, **0 failed** — up from 238. Two new: the ordering rule itself (collated `1,2,3,1,2,3` versus uncollated `1,1,2,2,3,3`, and one copy having no order to choose), and an uncollated job putting all four sheets through the real driver |
| **The order is a rule, not a side effect** | `sheet_order()` is a pure function and is tested directly: two copies of three pages gives six sheets in either mode, in the two different orders, and one copy is identical either way |
| **Uncollated still prints everything** | Two pages of three, twice, uncollated, is asserted to put **four sheets** through the spooler and report `collated: false` |
| **Dead-button audit, static pass** | **139 controls checked, 167 static steps, 0 problems** — up from 138, the new one being the order control |
| **Dead-button audit, live pass** | **66 named steps, 0 failures** — **233 steps passed** across both passes |
| **The dialog says what will happen** | With a 1-2 range and two copies, the order line is asserted to read exactly **`1, 2, 1, 2`** collated and **`1, 1, 2, 2`** uncollated, the button to read **Print 2 pages × 2 copies**, the order control to be **disabled at one copy** and enabled at two, and switching back to collated to restore the collated order |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| Existing 8 saving checks | **Still 8 passed** |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF — Offline PDF Studio` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **The order preview showed the same thing twice.** The first version of the
   sentence under the control built "collated" for both choices, because the
   uncollated branch pushed every page per *copy* instead of every copy per
   *page* — the same list in the same order. The audit compares the two strings
   exactly, so it caught it.
2. **The audit's print wrapper was a copy of the real signature**, and had to be
   updated every time the real function grew an argument — twice now, each time
   showing up as a print job that silently never happened. It is `*args,
   **kwargs` now, so the next argument cannot break it.

### What collated and uncollated mean here

- **Collated**: 1, 2, 3 then 1, 2, 3 — each copy is a complete set.
- **Uncollated**: 1, 1, 2, 2, 3, 3 — a stack of each page, for handing out page
  by page.
- The order is built here and handed to the driver as a list of sheets, so it is
  the same on every printer rather than depending on a driver's collate setting.
  On macOS and Linux the job goes through CUPS with `Collate=True|False` said
  explicitly.
- With one copy the control is **disabled**, because the choice makes no
  difference — it is not hidden, so the option does not appear to come and go.

### Still open / unverified

- **No physical printer was used**, so "collated" and "uncollated" are verified
  as the order of sheets handed to the spooler, not as the order that comes out
  of a real tray.
- **The printer-properties dialog has still not been opened by a human.**
- The two native file dialogs remain unoperated, there is no macOS build, and
  there is no Inno Setup installer here.

## 0.14.0 — page tools on every page, and a print dialog that asks

Date: **19 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.13.0 and earlier results below are retained. This release carries two
requests: tools to **extract, split, delete and rotate pages**, usable **while
scrolling through them**, and a **print dialog with pages, copies and the
printer's own settings**, the way Word and Windows do it.

**What was there before.** The four page actions existed, but they lived in the
toolbar of the Pages view and acted on a selection made somewhere else, and Split
was only in the document bar. Printing sent every page to the chosen printer at
200 DPI with no page choice, no copy count, and no way to reach the driver's own
paper and orientation settings.

| Check | Actual result |
|---|---|
| Engine/API test suite | **238 passed**, 2 skipped, **0 failed** — up from 234. Four new: the page list refuses what is not a page, a range and a copy count reach the spooler as the right number of sheets, a page outside the document is refused **before** anything is spooled, and the printer settings can be read without a dialog |
| **A range and copies really print** | Two pages of four, twice, is asserted to put **four sheets** through the real driver and into the captured job, in that order |
| **A bad range never reaches the printer** | A page outside the document is refused and **no file is created**, which is the difference between a refusal and a half-printed job |
| **The driver settings round-trip** | The DEVMODE block is read from the real driver without prompting: it reports `Letter`, `portrait`, 1 copy. The same block is handed to `CreateDC` on the next job |
| **Dead-button audit, static pass** | **138 controls checked, 166 static steps, 0 problems** — up from 133: the three per-page buttons, Split in the organizer, and the print dialog's pages, copies and properties controls |
| **Dead-button audit, live pass** | **66 named steps**, **0 failures** — **232 steps passed** across both passes |
| **Page tools while scrolling** | Every page card is asserted to carry rotate, extract and delete; pressing rotate on a page is asserted to rotate the document and to be undoable; the organizer is asserted to have its own Split button |
| **The print dialog asks** | The dialog is asserted to offer a page choice, a copy count and a printer-settings button; “all pages” is asserted to say **Print 4 pages**; the current page to become **Print 1 page**; `1-2` to become **Print 2 pages**; `99` to **disable** Print with a reason; and a valid range to enable it again |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| Existing 8 saving checks | **Still 8 passed** |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA PDF — Offline PDF Studio` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **A dismissed print dialog crashed the next preview.** The preview's
   in-flight handler read `printJob` *after* awaiting the image, and the window
   can be closed while that request is in flight — so the read landed on `null`.
   The job is now captured before the first `await`, and the handler checks it is
   still the current one before touching the DOM. The audit's
   "no uncaught JavaScript errors" step is what caught it.
2. **`_render_pages` shadowed its own parameter** when it grew a `pages`
   argument: the accumulator was also called `pages`, so a job for two selected
   pages rendered none. The existing spooler test caught it immediately.
3. **The audit's print wrapper had the old signature**, so every job through it
   failed with a `TypeError` — which the audit reported as "no confirmation" and
   which then left the rest of the run clicking at a page stuck behind the busy
   overlay.
4. **A selection left behind by one step broke the next.** The new page-tools
   step left one page selected; the following step assumes "all pages", and the
   audit's own `select_all_pages` helper deliberately does nothing when anything
   is already selected. Both steps now establish their own selection instead of
   inheriting one.

### What printing does now, and what it still does not

- **Pages**: all, the current page, or a range (`1-3, 5`). The preview shows the
  first selected page, the arrows step through **only the selected pages**, and
  the button says how many sheets will come out.
- **Copies**: 1–99, drawn as repeated pages inside one job, so the output is
  collated: 1, 2, 3, then 1, 2, 3.
- **Printer properties…** opens the **driver's own dialog**. Paper size,
  orientation, duplex and quality are the driver's business; a hand-built copy of
  that dialog would silently do nothing on half the printers in the world. The
  choice is kept for the session.
- Still not offered, deliberately: **duplex and paper size in our own dialog**
  (they are in the driver's), **page scaling** and **booklet printing**.
- A range that runs past the last page **disables Print and says why** rather
  than printing something else.

### Still open / unverified

- **The printer-properties dialog itself has not been opened by a human.** The
  DEVMODE round-trip behind it is tested without prompting, and the button is
  wired to the endpoint, but no person has clicked OK in a real driver dialog.
- **No physical printer was used.** Every job went to a driver that writes a
  file.
- The two native file dialogs from 0.10.0 are still unoperated by a human, there
  is no macOS build, and there is no Inno Setup installer here.

## 0.13.0 — the application is called KADOMA PDF, and it opens on a home screen

Date: **19 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.12.0 and earlier results below are retained. This release carries three
requests: rename the application to **KADOMA PDF**, use the supplied artwork as
its logo, and lay the interface out with the tools arranged the way Acrobat
arranges them.

**What was there before.** The product was called Paperdesk, it drew its own
procedural icon, and it opened straight into a document with the editing toolbar
across the top. There was no home screen: the tools were a row of tabs and a
panel of controls, which assumes you already know what you want to do.

**What changed, and what did not.** The rename is not cosmetic in the places that
matter: the executable is `KADOMA.exe`, so the registry entries, the file
association, the installer's directory and the share folder all had to move with
it, or double-clicking a PDF would point at a program that no longer exists. The
icon is now generated from one supplied image rather than drawn in code, and the
rounded square is cut out on transparency — the source has white corners, and a
white square looks wrong on a dark taskbar.

The home screen is built from the actions the application already had. **No card
is a placeholder**: each one calls the same function the toolbar calls, and the
list of cards is the list of things this build can actually do. Send for Comments
and Request e-signatures appear in Acrobat's list and not in this one, because
this build does not have them.

| Check | Actual result |
|---|---|
| Engine/API test suite | **234 passed**, 2 skipped, **0 failed** — up from 230. The four new tests are on the icon set: the ICO carries every size Windows asks for, the ICNS is a real container that opens as an image, and both the master icon and the 128 px mark have transparent corners |
| **Dead-button audit, static pass** | **133 controls checked, 158 static steps, 0 problems** — up from 132, the new one being the Home tab |
| **Dead-button audit, live pass** | **64 named steps** driven in a real Chromium, **0 failures** — **222 steps passed** in total across both passes |
| **The home screen is the start screen** | A fresh load is asserted to be on **Home**, with the document bar and the editing toolbar **not visible**, at least eight cards and eight tools listed, a search that narrows the grid to one card while leaving the tool list complete, and a card that really opens the organizer |
| **Every card is wired** | The nine cards and the nine rail entries are pressed in the same live pass; the audit's static pass also requires every control the interface renders to have a handler |
| **The rename reaches the things that break if it does not** | The window title, the frozen self-test's product name, the registry `RegisteredApplications` value, the ProgID, the share folder and the export filenames all carry KADOMA PDF; the executable name and the default-app key agree, which is what makes a double-clicked PDF resolve |
| **The icons come from one image** | `scripts/make_icons.py` derives the 1024 px PNG, the multi-size `.ico` (16–256), a hand-assembled `.icns` and the 128 px mark; the ICO and ICNS are asserted to open as images at the expected sizes |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests — each now steps from Home into the document first, the way a person does |
| Existing 9 direct-edit checks | **Still 9 passed** |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| Existing 8 saving checks | **Still 8 passed** |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled **`KADOMA PDF — Offline PDF Studio`** |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **Every check assumed the document was on screen.** Starting on Home broke the
   dead-button audit, the workflow checks, the direct-edit checks and the save
   checks in the same way: they clicked buttons that only exist next to a
   document. Each now enters the document first, which also means the home
   screen itself is now covered — it was previously not tested at all.
2. **A reload quietly doubled the workspace.** The home-screen step reloads to
   see the start state, and every load creates a sample document, so the merge
   window later listed two copies of it and two merge steps failed on the
   duplicate. The step now closes the open documents before reloading.
3. **Placing an image returned to the wrong tool for the checks.** The reading
   view is the default after any placement, so the image handles are not shown
   until the Select tool is chosen. The workflow check now selects the tool,
   which is what a person would do.
4. **`KADOMA Sans` is still Inter.** The font family name was renamed with
   everything else; the file is the bundled Inter, so nothing changed on screen,
   but the name no longer points at a product that does not exist.

### What the home screen is, and what it is not

- It is a **map of real actions**: Create PDF, Combine Files, Organize Pages,
  Edit PDF, Export PDF, Scan & OCR, Fill & Sign, Sign, Protect.
- It is **not** a document browser: **Recent** lists the documents open in this
  workspace, which are held in memory and last for the session. There is no
  library, no history and no thumbnails of files on disk.
- It is **not** Acrobat: there is no account, no cloud, no e-signature request
  workflow and no comment-sending service, so those cards do not exist. A card
  that opened a dialog explaining the feature is unavailable would be worse than
  no card.

### Still open / unverified

- **No physical printer was used** (unchanged from 0.11.0), and the two native
  file dialogs have still not been operated by a human.
- The supplied artwork is a 1080 px JPEG, so the 1024 px PNG and the 256 px ICO
  are resampled from it. A vector original would be sharper at large sizes; the
  small sizes are indistinguishable.
- No macOS build and no Inno Setup installer were produced here.
- No real language-model provider was used (unchanged).

## 0.11.0 — a print preview, and a printer to choose

Date: **18 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.10.0 and earlier results below are retained. 0.11.0 answers one request:
pressing **Ctrl/⌘ P** or the **Print** button should show a print preview and a
way to choose the printer.

**What was there before.** Print fired a job at the default printer immediately.
The only dialog appeared when that default could not print — a driver that saves
to a file — and it offered the other installed printers as a fallback. There was
no preview at all, and no way to see which printer a job would go to before
pressing the button.

**What a preview has to be to be worth anything.** Showing the page again is not
a preview — the app already shows the page. A preview has to show the **sheet**:
the paper the printer will load, and the margin it cannot reach. So the preview is
built from the printer's own device context — `PHYSICALWIDTH/HEIGHT` for the
paper, `HORZRES/VERTRES` and `PHYSICALOFFSETX/Y` for the printable area — and the
page is rasterised exactly as the print path rasterises it, then placed inside
that area at the same fit the driver is asked for.

| Check | Actual result |
|---|---|
| Engine/API test suite | **230 passed**, 2 skipped, **0 failed** — up from 223. Seven new: five on the preview renderer and the printer classification, two on the preview endpoint |
| **The preview is the sheet** | A page painted solid black is previewed on a letter sheet with a quarter-inch margin: the image's proportions are asserted to be the **paper's**, the pixel in the margin is asserted to be **white**, and the centre **black**. Without a printer the preview is asserted to fall back to the page's own proportions instead of inventing margins |
| **The preview follows its page** | Page 1 and page 2 of the same document are asserted to produce different pixels at the same size, so a cached first page cannot pass as a second |
| **The endpoint refuses what it cannot draw** | A page that is not in the document is **404 `page_not_found`**, no document is **409**, and the whole endpoint is **403 `desktop_only`** in the browser preview |
| **Dead-button audit, static pass** | **131 controls checked, 155 static steps, 0 problems** — up from 129 |
| **Dead-button audit, live pass** | **60 named steps** driven in a real Chromium, **0 failures** — **215 steps passed** in total across both passes. The three print steps were rewritten: the preview is opened, its image is asserted to decode at more than 200 px on both sides, its page arrows are asserted to move and come back, the skipped file-only driver is asserted to be **named**, and **printing from the preview** is asserted to put a real job through the spooler |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged |
| Existing 8 saving checks | **Still 8 passed** — no regression |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | 4 checks passed: loopback listener, HTTP 401 token gate, bundled UI served, native window titled `KADOMA — Offline PDF Studio` |
| **Double-click handoff** | 5 checks passed against the real EXE |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **A printer on an ordinary port was never checked by name.** `saves_to_a_file`
   returned as soon as it found a port, so it only ever recognised
   `PORTPROMPT:`/`FILE:` ports and the name check was dead code for everything
   else. Measured here: **OneNote (Desktop)** reports the port `nul:` and was
   therefore listed as a printer that puts ink on paper. The port is now checked
   first for the two prefixes that really mean "ask for a filename", and the
   driver and printer names are always checked after that. OneNote and the PDF
   writer are skipped; a printer on an ordinary IP port is still offered.
2. **The preview went blank behind a working dialog.** The first version captured
   the preview's blob URL in the modal's dismiss handler, which runs when the
   *next* window opens — by which time `printJob` already belonged to the new
   window, so the handler cleared the new job and the image never loaded. The job
   is now captured by value and only cleared if it is still the current one.
   Caught by taking a screenshot of the second dialog opened in a session, not
   the first.
3. **The audit's print steps were driving the old flow.** They clicked Print and
   waited for a job; they now open the preview, assert the image decoded and the
   page arrows moved, and only then press Print.

### What the preview does, and what it deliberately does not

- The preview shows **one page at a time**, the page you were on when you pressed
  Print. The arrows move through the document.
- **Every page is still printed** — there is no page range in KADOMA. Paper
  size, orientation, duplex and copies belong to the printer driver.
- A printer that saves to a file is **named and skipped**, not offered. The dialog
  says which one and why, and keeps **Export instead** one press away.
- On a platform where printing goes through CUPS, or when no printer can be
  queried, the preview falls back to the page's own proportions. The margins then
  are **not** the printer's, and that is a limitation rather than a preview.

### Still open / unverified

- **No physical printer was used.** Every job in this report went to a driver that
  writes a file, and the preview was checked against paper geometry read from
  those drivers — including one that reports no margins at all. How a real
  printer's margins look on paper was not observed.
- The two native dialogs from 0.10.0 remain unoperated by a human, and no macOS
  build or Inno Setup installer exists.
- No real language-model provider was used (unchanged).

## 0.10.0 — Save and Save as, and the first way to write back to your own file

Date: **18 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.9.0 and earlier results below are retained. 0.10.0 answers one request:
add a **Save** and a **Save as** button.

**Why this was not a two-button change.** Until now the application could not
write to a file it had not just created: a document arrived as bytes, lived in
memory, and left through an export dialog that always asked for a new name. "Save"
needs three things that did not exist — a document has to remember which file it
came from, that file has to be checked before it is replaced, and the write has to
be able to fail without destroying what was already there.

| Check | Actual result |
|---|---|
| Engine/API test suite | **223 passed**, 2 skipped, **0 failed** — up from 208. The 15 new tests are all about saving, and they are mostly about the ways it must **refuse** |
| **Saving, proved rather than described** | `scripts/check_save.py` drives a real browser against a desktop-mode server: it opens a PDF by path, edits it, presses **Save**, and compares the file on disk before and after. **8 checks passed** — the overwrite reached the file, Save as wrote the copy, the document followed the copy, a later Save kept writing to the copy, a file changed by another program was **refused**, cancelling wrote nothing, and there were no JavaScript errors or external requests |
| **Dead-button audit, static pass** | **129 controls checked, 153 static steps, 0 problems** — up from 126, the three new ones being Save, Save as and their labels |
| **Dead-button audit, live pass** | **59 named steps** driven in a real Chromium, **0 failures** — **212 steps passed** in total across both passes |
| **The audit saves for real too** | The live pass stands in only for the two native dialogs, then presses the buttons: a PDF is asserted to appear on disk, the header to read **Saved**, and a second press to write in place. It also asserts that the browser preview **explains** itself instead of failing quietly |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **17 of 17 checks passed** (`frozen: true`), including *Save writes over the file on disk* and *Save refuses a file that changed since it was opened* |
| **Stand-alone EXE launch** | `KADOMA-0.10.0-Windows-x64-standalone.exe` (55,452,003 bytes) opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (18,436 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** — **4 checks passed** |
| **Double-click handoff** | **5 checks passed** against the real EXE: a second launch handed its file over, **exited by itself with code 0** (8.7 s, one-file build), started **no second service** and **no duplicate window**, and the running instance **drained the handoff queue** |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **Three documents said the original file could never change.** The engine's own
   module documentation said *"Source files on disk are never overwritten by this
   engine"*, the redaction panel said *"The original file on disk remains
   unchanged"*, and every confirmation dialog was subtitled *"Your original file
   on disk will remain unchanged."* All three were true and none of them survived
   Save. They now say what is actually true — *"Nothing is written to disk until
   you save"* — because a claim that quietly becomes false is worse than a claim
   that was never made.
2. **The encryption refusal was based on a guess, and the guess was wrong.** The
   first version of Save refused to overwrite a password-protected file, on the
   reasoning that writing it back would produce an unprotected PDF. Measured
   instead of assumed: PyMuPDF writes the document with `PDF_ENCRYPT_KEEP`, so the
   AES-256 encryption, **both passwords and the permission flags all survive** an
   overwrite. The refusal was removed — it would have blocked a safe operation
   and pushed people towards Save as, which really does produce an unprotected
   copy — and a test now asserts the encryption, the user password, the owner
   password and the permissions are all intact afterwards.
3. **The version was written in four places.** The package, the health endpoint,
   the footer and the test suite each carried their own `0.9.0`, so bumping one
   left three disagreeing. The endpoint now reports the package version, the test
   compares against the package, and the dead-button audit reads the guide's
   version from the package too — it had been asserting the literal string
   *"KADOMA 0.9"*, which would fail after every correct release and pass while
   the guide was out of date.
4. **The document bar did not fit once the buttons were added.** Measured at
   1100 px: the bar overflowed by 36 px and the document name collapsed to
   **zero width**. The three least-used buttons now drop to icon-only at 1320 px
   and three more at 1120 px, each keeping its title and its `aria-label`, and the
   bar is asserted not to overflow from 1024 px upwards. Save and Save as keep
   their words longest.
5. **`DesktopBridge` lived inside `main()`**, so the contract it has with the
   interface could not be tested at all. It is now at module level, and a test
   asserts all three answers it can give — a path, a cancellation, or a reason
   the dialog could not be shown — plus that the file filters it hands pywebview
   are ones pywebview accepts.

### What saving does, and what it deliberately does not

- **Save** writes over the file the document was opened from. **Save as** asks
  for a destination and the document follows it.
- The header says **Saved** or **Unsaved changes**, decided by the engine from
  the revision it last wrote — not from a flag in the interface that a switch
  between documents could reset.
- A file that changed on disk since it was opened is **refused**, not
  overwritten, and not even after a confirmation: there is no way for KADOMA
  to merge somebody else's edit with its own.
- The PDF is written to a temporary file beside the destination and moved into
  place with `os.replace`. A failure at any point leaves the original exactly as
  it was; the temporary file is removed.
- **There is no version history, no backup and no undo after a save.** That is
  what Save as is for, and the README says so.

### Still open / unverified

- **The two native dialogs were not operated by a human.** The save path around
  them is driven end to end in a real browser against a real file, and the
  bridge's three answers are unit-tested, but no person has clicked "Save" in
  the WebView2 window and chosen a folder. Treat the dialog itself as unverified.
- No macOS build; no Inno Setup installer.
- The one-file handoff measured 8.7 s this run versus 33.9–53.1 s in earlier
  releases; the difference is machine load, not code.
- No real language-model provider was used (unchanged from 0.9.0).

## 0.9.0 — a menu across the top, and a page as large as the window allows

Date: **16 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.8.0 and earlier results below are retained. 0.9.0 answers three requests: put
the menu on top and make the tools collapsible, take the page thumbnails out of the
way but keep them available, and show the document as large as possible while
keeping the zoom controls.

**What was actually missing, and one thing that was quietly wrong.**

The layout had the view tabs down a rail on the left and the tools panel on the
right of the page. The thumbnail column was always on screen, taking 174 px whether
or not anybody was looking at it.

The third request was not really a layout problem. **"Fit width" never filled the
width.** The scale was capped at 125%, so on a 1500 px window the page sat at
**765 px inside a 1212 px canvas** — a quarter of the window empty, on the setting
whose entire purpose is to fill it. Raising the cap alone would have made things
worse rather than better: the page image was rendered at a **fixed scale of 1.7**
and then stretched by CSS, so anything past 170% would have been a small picture
blown up. Both had to change together.

| Check | Actual result |
|---|---|
| Engine/API test suite | **208 passed**, 2 skipped, **0 failed** — unchanged, because this release changes the interface and the fit rather than the engine |
| **Dead-button audit, static pass** | **126 controls checked, 150 static steps, 0 problems** — up from 122 controls, the four new ones being the menu bar and its three switches |
| **Dead-button audit, live pass** | **57 named steps** driven in a real Chromium, **0 failures** — **207 steps passed** in total across both passes |
| **The new arrangement, measured** | The old left rail is asserted **gone**; the menu bar is asserted across the top at more than 1200 px wide; all seven view tabs are asserted inside it; the thumbnails are asserted **away at the start**; the page is asserted to fill more than 85% of the canvas it has, and the canvas to reach the right edge of the viewport |
| **Every switch does what it says** | Showing the thumbnails makes the page measurably smaller and hiding them gives the room back; hiding the tools enlarges the page and it still fills the window; **Focus** puts both away; the chevron collapses the bar to less than half its height and brings it back |
| **Zoom still has the last word** | With both panels away, 50% is asserted to be respected and Fit width to return to the largest size; 300% is asserted to be honoured exactly; the zoom in/out buttons are asserted to step up and down from a fitted page |
| **The page is rendered at the size it is shown** | The render scale is read back from the interface and asserted to have followed the fit rather than staying at its old fixed value |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests — after the thumbnail-drag step was taught to switch the panel on first |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **15 of 15 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | `KADOMA-0.9.0-Windows-x64-standalone.exe` (55,443,971 bytes) opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (17,466 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** — **4 checks passed** |
| **Double-click handoff** | **5 checks passed** against the real EXE: a second launch handed its file over, **exited by itself with code 0** (47.9 s, cold, one-file build), started **no second service** and **no duplicate window**, and the running instance **drained the handoff queue** |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **Fit width was capped at 125%, so it never fitted.** Measured: **765 px in a
   1212 px canvas**. And the page image was rendered at a fixed scale of 1.7, so
   simply raising the cap would have produced a soft, upscaled page — the fix had
   to be both together. Fit now reaches 300%, and the page is **rendered at the
   scale it is displayed at**, re-rendered only when that changes by more than a
   fifth, so a resize does not thrash the renderer.
2. **The zoom ladder stopped at 200%.** With a fit that can now reach 300%, the
   *zoom in* button from a large fitted page would have had nowhere to go and would
   have silently done nothing — a dead button, which is the exact failure the
   dead-button audit exists to catch. The ladder and the zoom menu now reach 250%
   and 300%.
3. **Two media queries overruled the new switches.** `@media(max-width:760px)`
   hid the thumbnail column and `@media(max-width:580px)` hid the tools panel,
   regardless of what had been chosen in the menu bar. Both are gone: on a narrow
   window the answer is to leave a panel off, and that is the user's decision, not
   the stylesheet's.
4. **Three checkers were driving controls that had moved.** `check_controls.py`
   asserted the existence of the old left rail and clicked the add-pages button in
   a panel that now starts hidden; `check_ui.py` dragged a thumbnail that was not on
   screen, which failed with *"element is not visible"* 59 times. All three were
   updated, and the audit gained a step that measures the new arrangement rather
   than the old one.

### Design decisions worth recording

- **One place decides the layout.** `applyPanelLayout()` sets both panels, the
  menu bar's folded state, the focus padding and every button's pressed state, so
  the switches, the panels and the page fit cannot disagree. It re-runs the fit at
  the end, because the page is measured against the width it actually has.
- **The page is never a small image stretched.** The render scale is derived from
  the displayed size, clamped to 1.2–3.2, so the page is sharp at every zoom the
  interface offers and the engine's own 20-megapixel ceiling is never approached.
- **The thumbnails are not gone, they are off.** The Pages view shows every page as
  a grid — which is where pages are reordered and selected — so the side column is
  a convenience rather than a necessity, and it is one press away.
- **Nothing about the arrangement is written to disk**, like every other preference
  in this application.

**Outstanding.** Interactive hand-on-GUI typing under WebView2 has still not been
performed by a human; the browser checks drive the same interface in Chromium, so
the gap is specifically the pywebview shell. **No real language-model provider has
been used to verify the optional model connection** — it is exercised end to end
against a stub endpoint on loopback, which proves the request, the key handling,
the reply parsing and every error path, but not how any particular provider
behaves. No macOS APP/DMG was built here, and no Inno Setup installer was
generated. The one-file build remains much slower than the portable folder build
for the double-click handoff. The window arrangement — which panels are open, and
the zoom — lasts for the session only.

---

## 0.8.0 — every tool on one side, merge what is open, and an AI reading

Date: **16 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.7.0 and earlier results below are retained. 0.8.0 answers three requests:
put the tools on one side only, let the merge tools combine files that are already
open, and include AI that can summarise a PDF and build a form from a prompt.

**What was actually missing.** The tools were split across both sides — the view
switcher and page thumbnails on the left, the settings for whichever view was
selected on the far right. The merge window could already take an open document,
but it listed them *below* the file picker, so the quicker path was the second
thing you saw. And AI was absent by design: `FEATURES.md` said, in as many words,
"AI features | Not included".

**The honest shape of the AI feature, because this is the part that could go
wrong.** This application is offline-first, ships no account, and states in
several places that nothing leaves the computer. A generative model cannot be both
real and local here — there is no bundled model and nothing is downloaded. So the
release is built in two halves and the interface never lets them be confused:

- **Offline, the default, and real.** An extractive summariser that ranks the
  document's own sentences by the frequency of the words they contain, and a
  prompt parser that turns ordinary words into real PDF form fields.
- **Optional.** An OpenAI-compatible endpoint that somebody connects themselves,
  with their own key, used only after they agree.

**The offline summary does not write prose. It quotes.** Every result is labelled
with which of the two readings produced it, in the panel and on the result itself.
Presenting an extraction as though a model wrote it would misrepresent what the
reader is looking at, and that is the one failure this feature could not survive.

| Check | Actual result |
|---|---|
| Engine/API test suite | **208 passed**, 2 skipped (LibreOffice absent; the registry round-trip is opt-in), **0 failed** — up from 167 passed |
| Tests collected | **210**, up from 169 — **41 new tests**: 33 in `tests/test_ai.py`, 8 API in `tests/test_api.py` |
| **Dead-button audit, static pass** | **122 controls checked, 146 static steps, 0 problems** |
| **Dead-button audit, live pass** | **57 named steps** driven in a real Chromium, **0 failures** — **203 steps passed** in total across both passes |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests — no regression |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **The offline reading, verified in a browser** | Summarising the sample document returns a result tagged **Offline**, says it is quoted, and lists key terms. A prompt — *"full name, email, date signed and a checkbox to agree"* — proposes exactly four fields, and adding them puts **four real PDF form fields** (`text`, `text`, `date`, `checkbox`) on a **new page**, read back from the engine rather than from the panel |
| **The model path, verified against a stub** | A stub OpenAI-compatible endpoint on loopback received the request at `/v1/chat/completions` with `Authorization: Bearer …`, the configured model name and the document's extracted text; the summary came back and was tagged **Model**. Every failure mode is covered by unit tests: an HTTP refusal with its reason, an unreachable host, a reply that is not JSON, a reply with no usable fields, and a request with no model connected |
| **Nothing is sent without an answer** | Using the model raises a confirmation first; dismissing it sends nothing and leaves the offline reading in place. Disconnecting returns the panel to offline |
| **The key never comes back** | `/api/ai/status` reports `keySet` and never the key; the connect response, the page source and every error message were checked for the key that was entered |
| **The layout, measured** | The nav rail, the thumbnails and the tools panel are asserted to be left of the page in that order, and the page to reach the right edge of the viewport — so nothing is left on the far side. The revealed tools panel is asserted to open **towards** the page without moving it |
| **Merge, open documents first** | The already-open list is asserted to precede the file picker in the DOM; **Add all** adds every addable document in one press; the document being merged into cannot be added to itself for append, and the workspace cap is asserted rather than assumed |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **The line splitter had a length gate that made it skip the case it was written
   for.** A block of *exactly* the limit was left unsplit, so a running header
   stayed glued to the sentence after it and the summary quoted the two together.
   The gate was an optimisation that had turned into a bug; the upper-case rule
   does the real work, so the gate is gone.
2. **A model running on this computer was being reached through the system
   proxy.** `urllib` honours `HTTP_PROXY` by default, so a request to `127.0.0.1`
   went to whatever proxy the machine was configured with and came back as *that
   proxy's* 502 — which would have looked like a broken endpoint. Loopback
   addresses now bypass the proxy. Found by a unit test whose "unreachable" host
   was reachable after all, through a proxy.
3. **The audit summarised a blank page.** The new step ran after earlier steps had
   left empty documents open, so the engine correctly refused with "there is no
   text in this document to summarise" and the audit reported "no summary
   appeared". The step now reloads the sample first — the engine was right.
4. **Two hand-rolled controls defeated the static wiring check.** The new panel
   built its page-range controls by hand, and the checker could not trace the
   selectors they were wired through, so it reported two controls with no handler.
   They now use the same ranged control every other panel uses.

### Design decisions worth recording

- **The offline reading is labelled wherever it appears** — in the panel, in the
  toolbar, and on every result — because the alternative is a reader believing a
  quotation is a summary.
- **One question, asked once.** Nothing is sent to a model until the person
  answers a confirmation naming the model and saying plainly that the text leaves
  the computer. Dismissing it sends nothing.
- **The key is never stored.** It is held in memory for the session, never written
  to disk, never logged, and never returned by any endpoint. A later save with a
  blank key field keeps the key already held rather than clearing it.
- **Reading a document for the model is a copy**, so it goes through the same
  export path as Convert and the engine's own permission check applies. A
  document whose owner forbids copying is refused rather than quietly read.
- **A prompt the parser does not recognise is refused, not guessed at.** The
  message names an example rather than inventing fields.
- **Fields go on a new page.** Overlaying them on existing content would be a
  silent mess; a new page at the end is predictable, visible, and one undoable
  step.

**Outstanding.** Interactive hand-on-GUI typing under WebView2 has still not been
performed by a human; the browser checks drive the same interface in Chromium, so
the gap is specifically the pywebview shell. **No real language-model provider was
used to verify this release** — the model path was exercised end to end against a
stub endpoint on loopback, which proves the request, the auth header, the reply
parsing and every error path, but not how any particular provider behaves. No
macOS APP/DMG was built here, and no Inno Setup installer was generated. The
one-file build remains much slower than the portable folder build for the
double-click handoff.

---

## 0.7.0 — several documents open at once, and a panel that can be put away

Date: **16 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.6.0 and earlier results below are retained. 0.7.0 answers two requests: the
tools on the right should be **pinnable or auto-hiding**, and the **merge tools
should be able to merge files that are already open**.

**What was actually missing.** Two things, and the second was larger than it
sounded.

The right-hand tools panel had no way to get out of the way. It held 288 px of the
window at every moment; the only escape was to narrow the window until a media
query hid it.

"Merge files that are already open" could not work at all, because **opening a
document closed the one before it**. `adoptDocument` deleted the previous document
from the engine on every open, so the workspace never held more than one and there
was nothing for the merge window to offer. The engine already supported six; the
interface was throwing them away. So this release had to change what "open" means
before the merge window had anything to list.

| Check | Actual result |
|---|---|
| Engine/API test suite | **167 passed**, 2 skipped (LibreOffice absent; the registry round-trip is opt-in), **0 failed** — up from 157 passed |
| Tests collected | **169**, up from 159 — **10 new tests** (5 documents-kept-open in `tests/test_engine.py`, 5 API in `tests/test_api.py`) |
| **Dead-button audit, static pass** | **111 controls checked, 134 static steps, 0 problems** |
| **Dead-button audit, live pass** | **53 named steps** driven in a real Chromium, **0 failures** — **187 steps passed** in total across both passes |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests — no regression |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **15 of 15 checks passed** (`frozen: true`). The first build of this release came out 11 MB too large because NumPy had leaked in from the shared virtualenv; see defect 4 below. That build was discarded and these results are from the corrected one |
| **Stand-alone EXE launch** | `KADOMA-0.7.0-Windows-x64-standalone.exe` (55,409,284 bytes) opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (16,212 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** — **4 checks passed** |
| **Double-click handoff** | **5 checks passed** against the real EXE: a second launch handed its file over, **exited by itself with code 0** (33.9 s, cold, one-file build), started **no second service** and **no duplicate window**, and the running instance **drained the handoff queue** |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

1. **The switch warning became a lie.** `confirmSwitch` told people that switching
   documents "closes this document and clears its in-memory undo history". That was
   true while opening a document closed the previous one. Once the workspace keeps
   documents open, switching is lossless and the sentence is simply wrong — and a
   warning that is wrong is worse than no warning, because it teaches people to
   click through it. It is gone from opening, creating and switching, and now
   appears only where it is true: closing a document with unexported edits.
2. **Two audit branches could never run.** `check_controls.py` waited for a
   "Switch documents?" dialog the interface no longer raises, so two steps carried
   a branch that could not execute. Removed rather than left as decoration: a check
   that cannot fail is not a check.
3. **`:focus-within` held the panel open for good.** The first cut of auto-hide
   revealed the panel with `.inspector-rail:focus-within`, and a pressed button
   keeps focus — so pressing the pin to unpin left the panel open until something
   else was clicked. The browser check caught it ("the panel stayed out after the
   pointer left"), and focus is now handled in the script, with the rail tab
   deliberately excluded so that its own click decides the state.
4. **The build silently depended on the shared virtualenv.** The first 0.7.0
   artifacts came out at **66 MB** against 55 MB for 0.6.0, with no code change to
   account for it. The difference was **NumPy — 24 MB of it**, plus its licence
   folder — which had been installed into the shared virtualenv by something else
   between the two releases. PyMuPDF's optional NumPy support is written as
   `try: import numpy`, and **PyInstaller follows that branch even though it is
   never taken**, so a package that merely happened to be present was bundled into
   the executable. That build was discarded. Two checks show the application does
   not need it: the real import graph (`pymupdf`, `PIL`, `fastapi`, `uvicorn`,
   `pptx`, `docx`, `openpyxl`, `pdfplumber` and every `app` module) reaches NumPy
   only through that optional branch, and the whole engine — rendering, Arabic
   write and read-back, and all six export formats — runs correctly with `numpy`
   blocked at the import system. NumPy, SciPy, pandas, matplotlib, schedula, tqdm
   and regex are now excluded in `kadoma.spec`, and `collect_licenses()` skips
   the same list so the shipped notices describe what is actually in the build.
   The point is not the 24 MB: it is that **the artifact's contents were being
   decided by whatever happened to be installed next to it.**

### Design decisions worth recording

- **The panel floats rather than pushes.** Revealing the tools must not move the
  page somebody is reading, so the revealed panel is positioned over the canvas and
  the check asserts the canvas width is unchanged while it is open.
- **An open document goes through the same door as an upload.** `source_of()` hands
  back bytes, name and the stored password in exactly the shape an upload has, and
  the merge then applies the same reading, password and permission checks. An open
  document cannot bypass a rule a file would have to satisfy — verified by merging
  a document that forbids page assembly and getting the same 403 an upload gets.
- **The order is carried, not inferred.** Open documents and uploads cannot be
  interleaved by position in a multipart body, so the window sends an explicit
  ordered `sources` list and refers to the uploads by index. With no `sources`
  list the previous behaviour is untouched, which is why every earlier merge test
  still passes unmodified.
- **A document cannot be merged into itself, but can build a new PDF from
  itself.** Appending a document to itself is a confusing way to duplicate it;
  building a new PDF from it is a different operation on different bytes. The rule
  is re-checked as the destination changes, not only when Add is pressed.
- **Nothing is written to disk to remember any of it.** Which documents are open,
  and whether the panel is pinned, last for the session only — consistent with the
  application writing no preferences at all.

**Outstanding.** Interactive hand-on-GUI typing — clicking into the page and typing
under WebView2 — has still not been performed by a human; the browser checks drive
the same interface in Chromium, so the gap is specifically the pywebview shell. No
macOS APP/DMG was built here (this is a Windows machine), and no Inno Setup
installer was generated (Inno Setup 6 is not installed). The one-file build remains
much slower than the portable folder build for the double-click handoff. There is
no session restore, no tabs and no side-by-side view: one document is on screen at
a time and the rest are held in memory.

---

## 0.6.0 — Splitting one PDF into several files

Date: **14 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.5.0, 0.4.0, 0.3.0, 0.2.0 and 0.1.0 results below are retained. 0.6.0 turns
splitting one document into several files into a first-class feature. Every check
below was re-run against the final source tree and the final artifacts.

**What was actually missing.** The engine could already export each selected page
as its own PDF inside a ZIP, but only as one of seven export formats, only one page
per file, and only after selecting pages. There was no way to cut a document into
equal blocks, no way to ask for a given number of files, no way to name your own
ranges, and no way to see what was about to be produced before it was produced.
The capability existed; the feature did not.

| Check | Actual result |
|---|---|
| Engine/API test suite | **157 passed**, 2 skipped (LibreOffice absent; the registry round-trip is opt-in), **0 failed** — up from 140 passed |
| Tests collected | **159**, up from 142 — **17 new tests** (12 splitting in `tests/test_engine.py`, 5 API in `tests/test_api.py`) |
| **Dead-button audit, static pass** | **108 controls checked, 128 static steps, 0 problems**. Every `id` in `index.html` and every control the interface renders from JavaScript is referenced by a handler or a delegated `data-*` attribute |
| **Dead-button audit, live pass** | **49 named steps** driven in a real Chromium, **0 failures** — **177 steps passed** in total across both passes |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests — no regression |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **15 of 15 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | `KADOMA-0.6.0-Windows-x64-standalone.exe` opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (14,917 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** — **4 checks passed** |
| **Double-click handoff** | **5 checks passed** against the real EXE: a second launch handed its file over, **exited by itself with code 0**, started **no second service** and **no duplicate window**, and the running instance **drained the handoff queue**. Measured **37.6 s** for the one-file build (cold cache; **33.1 s** on a second direct measurement) and **2.3 s** for the portable folder build, same machine, same session |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

Three defects were in the build tooling and documentation, and one was in the new
checks. Every one of them made a **correct build or a working feature look
broken**, which is the failure mode this project cares most about.

**In the build tooling**

1. **The checksum manifest was not portable.** `build.py` wrote
   `release/SHA256SUMS.txt` with `Path.write_text`, which uses the platform
   default newline. On Windows that produced CRLF, so every line ended with a
   carriage return and `sha256sum -c release/SHA256SUMS.txt` — the command a
   Linux or macOS user would naturally reach for — failed on all three artifacts
   with `'…zip'$'\r': No such file or directory`. **The hashes were right; the
   file was not.** The project's own `verify_sums.py` never noticed because it
   strips each line before parsing. Fixed by writing the manifest with an explicit
   `\n`.
2. **The handoff check's budget was hard-coded at 45 seconds, and a correct
   handoff can take longer than that.** The one-file build unpacks its whole
   ~55 MB payload before it can look for the running copy. Measured in this
   session: **33.1 s** on a cold cache, **37.6 s** on a run straight after the
   launch check. The script therefore reported *"The second instance kept
   running: it would open a duplicate window"* — a functional accusation about
   what is actually a timing budget. The budget is now `--handoff-timeout`, with
   the reason and the measured figures written into the script's own docstring.
3. **A recorded figure that could not be right.** `README.md` printed
   `source.zip`'s byte size, but that README lives *inside* `source.zip`, so
   writing the number down changed the number. Every release shipped a size that
   was already wrong. The size is no longer printed; the row points at
   `release/SHA256SUMS.txt`, which is the record that is actually generated from
   the files. The same self-reference is why `DELIVERY.json` never lists
   `source.zip`'s hash.

**In the new checks**

4. **Two of the three new audit steps assumed the split window survived the
   previous step.** The audit closes every dialog after each step by design, so
   `[data-split-mode="parts"]` and `#modal [data-close]` were clicked inside a
   dialog that was no longer open, and the audit reported two failures against a
   feature that worked. The steps now open the window themselves, exactly as the
   merge steps already did. This is the same class of defect as the two checker
   bugs found in 0.5.0: **a check that fails for the wrong reason is as bad as
   one that passes for the wrong reason.**

### Design decisions worth recording

- **The preview is the engine's answer, not the interface's.** The split window
  does not count pages itself; it posts the current settings to
  `/api/documents/{id}/split/plan` and renders what comes back. The file names,
  the page spans, the file count and the button label therefore cannot disagree
  with the bytes that are written afterwards, and a setting the engine would
  refuse is refused *before* the button is pressed rather than after. A
  generation counter drops a stale reply when somebody types faster than the
  requests complete.
- **A split is a read.** It produces files and touches nothing else: no change to
  the open document, no revision bump, no undo step. Verified directly — the
  document bytes and revision are compared before and after, and the test asserts
  the document is byte-identical.
- **A protected PDF is refused, not silently unprotected.** Re-encrypting every
  part would need both passwords again, and handing back an unprotected copy of a
  document somebody deliberately protected is worse than saying no. The message
  points at the route that does work: unlock an authorized copy first, then split
  that.
- **One part is a PDF, several are a ZIP.** An archive containing a single file is
  just a worse PDF, so `len(parts) == 1` returns the PDF directly, named after its
  page span.
- **A gap is allowed but announced.** `1-3, 7-10` leaves pages 4 to 6 out, which is
  a legitimate thing to want. Rather than refusing it or passing over it in
  silence, the window names the pages that are in no part.

**Outstanding.** Interactive hand-on-GUI typing — actually clicking into the page
and typing under WebView2 — has still not been performed by a human; the browser
checks drive the same interface in Chromium, so the gap is specifically the
pywebview shell. No macOS APP/DMG was built here (this is a Windows machine), and
no Inno Setup installer was generated (Inno Setup 6 is not installed). The
one-file build remains noticeably slower than the portable folder build for the
double-click handoff, and this release measured it at 33–38 s rather than the
6.3–6.5 s recorded in 0.5.0 — the portable folder build is the one to use as the
default PDF app.

---

## 0.5.0 — Combining several files into one

Date: **13 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.4.0, 0.3.0, 0.2.0 and 0.1.0 results below are retained. 0.5.0 turns
combining files into a first-class feature. Every check below was re-run against
the final source tree and the final artifacts.

**What was actually missing.** The engine could already copy pages from another
file, but only as a side effect of "Add pages → From files", and only by
appending. There was no way to see what was about to be combined, no way to
change the order, no way to take a page range out of a source, and no way to
unlock a protected file. Dropping several files on the window appended them in
whatever order the filesystem returned. The capability existed; the feature did
not.

| Check | Actual result |
|---|---|
| Engine/API test suite | **140 passed**, 2 skipped (LibreOffice absent; the registry round-trip is opt-in), **0 failed** — up from 122 passed |
| Tests collected | **142**, up from 124 — **18 new tests** (11 combining/inspection in `tests/test_engine.py`, 7 API in `tests/test_api.py`) |
| **Dead-button audit, static pass** | **103 controls checked, 122 static steps, 0 problems**. Every `id` in `index.html` and every control the interface renders from JavaScript is referenced by a handler or a delegated `data-*` attribute |
| **Dead-button audit, live pass** | **45 named steps** driven in a real Chromium, **0 failures** — 167 steps passed in total across both passes |
| Existing 19 workflow checks | **Still 19 passed**, 0 JavaScript errors, 0 external requests — no regression |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **15 of 15 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | `KADOMA-0.5.0-Windows-x64-standalone.exe` opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (14,584 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** — **4 checks passed** |
| **Double-click handoff** | **5 checks passed** against the real EXE: a second launch handed its file over, **exited by itself with code 0**, started **no second service** and **no duplicate window**, and the running instance **drained the handoff queue**. Measured **6.3–6.5 s** for the one-file build and **2.7 s** for the portable folder build, warm, on the same machine |
| **Real print job** | Still exercised end to end through the rendering path, the GDI API and the Windows spooler, with the resulting document reopened and inspected |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

Four defects were in the application and two were in the checkers. The two
checker defects matter more than they look: both made a **real failure
indistinguishable from a passing build**.

**In the application**

1. **The shared dialog could answer its own dismissal.** `#modal` is a single
   `<dialog>` reused by every dialog in the interface. `dialog.close()` *queues*
   the `close` event; it is not delivered until the next dialog is already on
   screen, where it is indistinguishable from that dialog being dismissed. In
   practice the combine window appeared to close itself, and — worse — a
   confirmation prompt raised from inside that window resolved `false`
   immediately, without the user ever answering. Fixed centrally in `openModal`
   with an explicit dismissal callback, so every dialog in the application
   benefits rather than just this one.
2. **Listeners piled up on the reused dialog.** Because the same element is
   reopened, handlers registered by one window were still attached when the next
   window opened, and fired against the wrong state — the visible symptom was
   `Cannot read properties of null (reading 'items')` on opening the combine
   window a second time. Fixed by tying every dialog-level listener to an
   `AbortController` that is aborted when the window reopens.
3. **Dropping files on the combine window opened a second combine window.** The
   dialog's drop handler did not stop propagation, so the page-level drop
   handler also fired. Fixed by stopping propagation inside the dialog.
4. **The page total was dishonest.** A page selection of `2-3` was counted as
   the source's whole page count, so the button promised "5 pages" for a
   two-page range. The total now reflects what will actually be copied, counting
   a repeated page once, and a range that cannot exist is refused on the client
   before the request is sent.

**In the checkers**

5. **The double-click check could not be run twice.** Every run left the
   application alive. A one-file PyInstaller build runs the application as a
   *child* of the bootloader, so terminating the process the check launched
   killed only the bootloader. The orphan kept the single-instance mutex, so the
   next run's "first" instance took the handoff path, queued its file, exited 0 —
   and opened no service. The check reported *"The first instance never opened
   its loopback service"*, which blames the build for a leftover process. Fixed
   with tree-aware termination, a pre-flight refusal to run while a copy is
   alive, and an early-exit test inside the wait loop so a silent exit is
   reported as a silent exit. The check now passes 5/5 three times in a row and
   leaves nothing behind.
6. **`tasklist` truncates the image name to 25 characters**, so the leftover
   process — `KADOMA-0.5.0-Windows-x` — was invisible to the very filter meant
   to find it. This is why the first diagnosis of the failure above was wrong.
   The filter now matches on the prefix.

### What combining actually does

Pages are copied with MuPDF's own page-insertion call, not re-rendered, so text,
vectors, images, links, annotations and form fields come across as they were. A
page range is copied in one call per consecutive run, so taking pages 1–50 of a
long document is one operation rather than fifty.

**Combining is one shared code path with merging.** Appending into the open
document and building a new one both go through `_add_sources`, so a page range,
a password or a permission cannot behave differently depending on which button
was pressed. That is a deliberate structural choice, and it is what the tests
target.

- **Order is what you set, not what the filesystem returns.** The list can be
  reordered before anything is combined.
- **A source can contribute only some of its pages** (`2-3, 7`), in the order
  typed, with a repeated page copied once.
- **A range past the end is refused, not silently shortened.** Asking for pages
  1–99 of a 3-page file is an error, because quietly returning 3 pages is how a
  user ends up with a document they did not ask for.
- **A locked file is listed with its real page count before the password is
  asked for.** A PDF's page count is readable while encrypted, so the list can
  show what the file is without decrypting it. The password is used for that
  operation only and is never stored.
- **A document that forbids page assembly is refused** rather than copied from,
  because copying its pages out anyway would ignore the owner's choice.
- **Identically named form fields from different sources are kept apart.**
  Verified: combining two files that both contain a field named `signature`
  yields `signature` and `signature [13]`, each holding its own value, so the
  second does not overwrite the first.
- **Merging into the open document is a single undo step.**

### Deliberate limits of combining

- **Combining does not shrink the result.** Pages are copied as they are; the
  output is not re-compressed or downsampled, so a combined file is
  approximately the sum of its parts. `MAX_PAGES` and the 80 MB batch limit still
  apply.
- **No file count limit** for combining. The only guard is the 500 MB combined
  size ceiling, enforced in the engine and surfaced as a plain message, not a crash.
- **Pages are not renumbered or bookmarked.** Combining produces the pages in the
  order chosen; it does not build a table of contents, merge outlines, or
  renumber existing bookmarks.
- **A password is not remembered between operations.** A locked file must be
  unlocked again for a later combine, deliberately — the alternative is storing a
  password the user did not ask to store.

## 0.4.0 — Date fields, printing, and clearing a form

Date: **12 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.3.0, 0.2.0 and 0.1.0 results below are retained. 0.4.0 adds a date field
type with a calendar picker, printing straight to a printer, and clearing a
filled-in form in one step. Every check below was re-run against the final
source tree and the final artifacts.

| Check | Actual result |
|---|---|
| Engine/API test suite | **122 passed**, 2 skipped (LibreOffice absent; the registry round-trip is opt-in), **0 failed** — up from 97 passed |
| Tests collected | **124**, up from 99 — **25 new tests** (8 forms/clearing, 6 API, 11 printing) |
| **Dead-button audit, static pass** | **98 controls checked, 0 problems**, 114 static steps. Every `id` in `index.html` and every control the interface renders from JavaScript is referenced by a handler or a delegated `data-*` attribute |
| **Dead-button audit, live pass** | **154 passed, 0 failed** across 40 named steps in a real Chromium, each requiring an observable result |
| Existing 19 workflow checks | **Still 19 passed** — no regression |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Existing 11 sharing/Arabic/default-app checks | **Still 11 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **15 of 15 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | `KADOMA-0.4.0-Windows-x64-standalone.exe` opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (14,339 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** — **4 checks passed** |
| **Double-click handoff** | **5 checks passed** against the real EXE: a second launch handed its file over, **exited by itself with code 0**, started **no second service** and **no duplicate window**, and the running instance **drained the handoff queue** |
| **Real print job** | The audit presses Print and a genuine job goes through the rendering path, the GDI API and the Windows spooler. The resulting document was reopened and inspected: **2 pages, both carrying ink**, correct orientation, correct colour order |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What this release found and fixed

Nine real defects were found and fixed, and two of them were in the **checkers
themselves**. The last two matter as much as the rest: a check that passes for
the wrong reason is worse than no check.

**In the application**

1. **Printing any A4 document crashed the print driver.** A 24-bit DIB pads every
   row to a multiple of four bytes; PyMuPDF emits exactly `width × 3` with no
   padding. A4 at 200 DPI renders 1654 px, so 4,962 bytes a row, and the driver
   read three bytes past the end of every row and faulted inside itself with
   *"access violation reading 0x…"*. US Letter happens to render 1700 px, which
   is already aligned — that is the only reason this stayed hidden. Fixed by
   padding the rows, and guarded by a test that asserts the alignment of real
   rendered pages at both paper sizes.
2. **Red and blue printed swapped.** A 24-bit `BI_RGB` bitmap stores BGR;
   PyMuPDF produces RGB. Fixed by swapping the channels, with the expected bytes
   written out by hand in a test rather than recomputed.
3. **Erasing a form field value silently did nothing.** PyMuPDF ignores
   `field_value = ''` on a text field, so deleting what you had typed and
   applying again left the old value on the page *and inside the saved file* —
   which matters most for exactly the fields people erase. The value is now
   removed from the field dictionary instead, and a test asserts the erased text
   is absent from the exported bytes.
4. **The calendar closed the instant "next month" was clicked.** Redrawing the
   popover replaces its markup, which detaches the node that was clicked, so the
   page-level close handler no longer recognised the click as being inside the
   calendar. Fixed by stopping propagation on every control inside it.
5. **A date field could never be created by dragging.** Choosing the Date field
   tool switches the active tool to `field-date`, which the list of tools that
   draw a rectangle did not include. Fixed, and a first-class Date field button
   was added to the toolbar.
6. **The typed field name was thrown away.** Typing a name and then dragging the
   rectangle re-rendered the panel and reset the name to `field_N`. Fixed with a
   draft value that survives the re-render.
7. **A press that landed right after a page change was lost.** The page change
   renders the side panel twice — once immediately, once when the page image
   arrives — so a press and its release could land on two different nodes and no
   `click` ever fired. Fixed by skipping the rebuild when the markup is
   unchanged, which also removed a visible flicker.

**In the checkers**

8. **The audit was reporting a false pass on form filling.** It read the value
   back from the side panel, which keeps whatever was typed, so it passed even
   when the engine had refused the save. It had in fact been typing a sentence
   into a *date* field, which the engine correctly refuses. The audit now reads
   the value back **from the engine**, and the refusal is a deliberate test of
   its own.
9. **The EXE launch check accepted the wrong window.** It looked for any visible
   window whose title merely contained "kadoma", and reported a File Explorer
   window open on a folder named `kadoma` as proof that the application had
   opened its own window. It now matches the shell's actual title, read out of
   `desktop.py` so the two cannot drift apart.

### How the printing path was verified without paper

Printing is verified by redirecting the job to a file **through the printer
driver**, not by stubbing it out: the real rendering, the real GDI calls, the
real device context and the real Windows spooler all run, and the resulting
document is then reopened and inspected. Nothing in the shipped application
knows the audit exists.

This is what caught both printing defects. A stub would have caught neither,
because both live in the bytes handed to the driver rather than in the code that
produces them.

### Deliberate limits of the new features

- **Printing has no page range, copy count, duplex or paper-size choice.** Every
  page is sent at 200 DPI, scaled to fit the printer's printable area and
  centred. Those settings belong to the printer driver, and KADOMA asks the
  driver for the paper it is set to use.
- **A printer that saves to a file is refused rather than started.** Sending a
  job to "Microsoft Print to PDF" or a fax driver raises a Save dialog owned by
  another process, which from here looks like a request that never returns. It
  is detected by its port and explained, and the other installed printers are
  offered instead.
- **A date field is a text field with two private keys.** Any reader can display
  it and its value; a reader that does not know the keys shows a text box and no
  calendar. The keys are verified to survive saving and reopening, because a
  marker lost on save would silently turn every date field back into a text box.
- **The date value is a string, not a PDF date object.** It is what other
  readers display, not something a form-calculation engine would compute on.
- **Clearing a form clears the whole document, not one page.** Read-only fields
  are skipped, because those hold somebody else's fixed value.

## 0.3.0 — Arabic text, sharing, and the default PDF app

Date: **12 October 2026**. Environment: Windows 11 x64 (build 10.0.26200), Python
3.13.14, PyMuPDF 1.28.2. Development verification, **not independent security
certification**.

The 0.2.0 and 0.1.0 results below are retained. 0.3.0 adds right-to-left text
support, send/share, and default-PDF-app registration, and was re-verified as
follows.

| Check | Actual result |
|---|---|
| Engine/API test suite | **97 passed**, 2 skipped (LibreOffice absent; the registry round-trip is opt-in), 0 failed — up from 41 |
| New Arabic/RTL tests | **21 passed** (`tests/test_arabic.py`) |
| New share/registration tests | **25 passed**, 1 skipped (`tests/test_share.py`) |
| Windows registry round-trip | Run deliberately with `PAPERDESK_TEST_REGISTRY=1`: registered, read back through an independent `winreg` handle, then unregistered with **0 failures and no trace left** |
| Sharing / Arabic / default-app browser checks | **11 passed** (`scripts/check_share.py`), asserting request payloads, not screenshots |
| Existing 19 workflow checks | **Still 19 passed** — no regression |
| Existing 9 direct-edit checks | **Still 9 passed** — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| **Windows x64 build, both modes** | Built here. Frozen self-test inside **each** artifact: **15 of 15 checks passed** (`frozen: true`), now including Arabic and sharing |
| **Stand-alone EXE launch** | `KADOMA-0.3.0-Windows-x64-standalone.exe` opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (13,488 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** |
| **Double-click handoff** | **5 checks passed** against the real EXE: a second launch handed its file over, **exited by itself with code 0**, started **no second service** and **no second window**, and the running instance **drained the handoff queue** |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

### What the Arabic work actually established

Four claims were measured rather than assumed, and three of them changed the
implementation:

1. **Shaping only works through the HTML/Story layout path.** Arabic written with
   the direct text-writing path comes out as disconnected letters in the wrong
   order. Verified directly, not inferred — so right-to-left text is routed
   through the layout path and never through the glyph-by-glyph writer.
2. **A plain search for Arabic returns nothing.** The document stores *shaped
   presentation forms*, not the letters typed, so searching for `الفاتورة` found
   **0 hits**. Normalising both sides and matching word windows turns that into a
   working search; a test guards the regression.
3. **Font choice is a correctness problem, not a taste problem.** MuPDF derives
   its reverse text mapping from the font, and some fonts map ligature glyphs
   back to the *wrong* characters — they look perfect on the page but read back
   corrupted the next time the line is edited. Measured on this machine with
   `"مرحبا بالعالم الفاتورة رقم ٢٠٤٨"`:

   | Font | Round-trip |
   |---|---|
   | Arial, Tahoma | **exact** |
   | Segoe UI, Dubai, Microsoft Sans Serif, Calibri | lam-alef ligature lost |
   | Noto Sans Arabic (static, bundled) | lam-alef returned as `ʜ` (U+029C) |
   | Noto Naskh Arabic | lam-alef returned as `DŽ` (U+01C4) |
   | Amiri | unusable — Ethiopic/Syriac codepoints, line fragmentation |
   | Noto variable fonts (`[wght]`, `[wdth,wght]`) | badly corrupted |

   A hard-coded "best font" list would be wrong on the next machine, so the app
   **measures** the fonts present at runtime and picks the most faithful one. On
   this machine it chose `arial.ttf`, `exact`. Amiri was removed from the bundle
   as a result of this measurement.
4. **`text-align: right` moves Arabic text to the LEFT.** Measured across eight
   CSS variants: `direction: rtl` alone right-aligns correctly, and adding
   `text-align: right` overrides it to the opposite of the intent. The working
   rule is recorded in the code with a warning against "fixing" it back.

Known and stated, not hidden: Arabic-Indic digits may return in the equivalent
Extended/Persian variant (search folds them, but extracted text is not
byte-identical), the bundled fallback font is approximate, and mixed
Arabic/Latin bidi lines rely on MuPDF and were not separately verified.

### What the sharing work actually established

- **`mailto` cannot carry an attachment** — RFC 6068 has no such parameter. This
  is why "Email with the file attached" builds a real `.eml` with
  `EmailMessage.add_attachment` instead, and why the panel says so in plain
  language. The `.eml` attachment was verified to match the source bytes exactly,
  including with a non-ASCII subject (RFC 2047 encoded, decoded correctly).
- **The clipboard payload was read back, not assumed.** `CF_HDROP` was written
  with `ctypes` and the clipboard was read back to confirm the exact path. Every
  handle type is declared explicitly, because an undeclared 64-bit return value
  truncates to 32 bits and the handle silently becomes invalid.
- **The path from the interface is untrusted.** Every share action refuses any
  path outside the share folder; the traversal guard is covered by tests using
  `C:\Windows\win.ini`, `/etc/passwd`, `..\..\Windows\win.ini` and a directory.
- **Windows will not let an app claim a file type silently.** Since Windows 8 the
  default lives in `UserChoice`, protected by a per-user hash. KADOMA
  registers itself as a *handler* under `HKCU` and then opens the Settings page
  for the user to confirm. The panel states this limitation rather than implying
  a one-click switch. Registry value types matter and were got wrong first:
  `OpenWithProgids` and `Capabilities\FileAssociations` need **named** values, not
  default values, or Windows ignores them.

### A real bug the browser check found

`check_share.py` caught a defect that no engine test would have: the share
buttons passed the clicked element into a helper that expected a CSS selector, so
`querySelector` threw `'[object HTMLButtonElement]' is not a valid selector` and
**every share option silently did nothing**. Fixed in `app/static/app.js`. This is
the reason the check drives the real interface instead of asserting on the API.

### Windows x64 artifacts actually built here

Produced by `python scripts/build.py --mode both` on Windows 11 x64 with Python
3.13.14. Sizes and hashes are the real outputs, not estimates.

| Artifact | Size (bytes) | SHA-256 |
|---|---:|---|
| `KADOMA-0.3.0-Windows-x64-standalone.exe` | 55,300,504 | `586f6fe17dc98f9e3db199db905530590d7d026898d1f7987c75d87b70bc6b1c` |
| `KADOMA-0.3.0-Windows-x64-portable.zip` | 55,272,476 | `3145da328f9d4176dffdb58f99b30b49f781eeff21a6d052370b426084e13f75` |

`release/SHA256SUMS.txt` is the authoritative record and covers all three files,
including `KADOMA-0.3.0-source.zip`. That archive is deliberately **not**
listed in this table: this report is stored inside the archive, so its own hash
would change every time the report is edited. Verify any download with:

```bash
python scripts/verify_sums.py release/SHA256SUMS.txt
```

`BUILD_INFO.json` records `buildModes: [folder, onefile]` and
`packagedEngineSelfTest: {folder: 15, onefile: 15}`.

**One measured caveat about the one-file build.** The double-click handoff takes
**32 s** in the one-file EXE and **2.6 s** in the portable-folder build, on the
same machine and the same check. The one-file build extracts its ~55 MB payload
*before* it can detect that another copy is running, so a double-clicked PDF
leaves the user looking at nothing for half a minute. The behaviour is correct in
both — no duplicate window, no duplicate service, the file is not dropped — but
the portable folder build is the better choice for everyday use as the default
PDF app. This is a consequence of one-file packaging, not of the handoff logic.

The stand-alone EXE is one file with **no sibling folder** — it unpacks itself to
a temporary directory at start-up, so its first launch is a few seconds slower
than the portable build. The portable ZIP must be extracted and kept together.

Two notes on how the launch check works, because both tripped up earlier attempts:

- The launch check **cannot** match the port to the process it started. A
  one-file build re-executes the real application as a *child* process, so the
  bootloader PID never owns the listening port. The verifier therefore snapshots
  loopback listeners before launch and accepts a port that appeared afterwards —
  which is the security-relevant property, since the shell binds `127.0.0.1` only.
- The window title is read through the Win32 API, **not** `tasklist`. `tasklist`
  reported the literal placeholder `N/A` for this window, which a naive
  truthiness test would have counted as a passing "window exists" check.

**Outstanding:** no macOS APP/DMG was built here (this is a Windows machine), and
no Inno Setup installer was generated (Inno Setup 6 is not installed). Interactive
hands-on-GUI testing — actually clicking into the page, typing Arabic under
WebView2, and clicking through the Windows default-app Settings page — has not
been performed. The automated checks prove the packaged app boots, serves its own
UI, gates its API, opens a window, hands a double-clicked file to the running
copy, writes Arabic correctly, and builds a real `.eml`; they do not simulate a
human at the keyboard. Registering as the default PDF app was verified at the
registry level and the Settings page is opened by the app, but the final
confirmation is a user action that no automated check can take on their behalf.
Typing in the real GUI on each target machine remains a release acceptance test.

---

## 0.2.0 — direct on-page text editing

Date: **12 October 2026**. Environment: Windows 11 x64, Python 3.13.14, PyMuPDF
1.28.2. Development verification, **not independent security certification**.

The 0.1.0 results below are retained. 0.2.0 adds direct in-place text editing and
was re-verified as follows.

| Check | Actual result |
|---|---|
| Engine/API test suite | **41 passed**, 1 skipped (LibreOffice not installed here), 0 failed |
| Direct-edit browser checks | **9 checks passed**; every claim asserted against the reopened exported PDF, not a screenshot |
| Existing 19 browser workflow checks | **Still 19 passed** after the interface changes — no regression |
| Hosted-preview privacy checks | **2 passed**, unchanged (0 uploads before consent, 1 after) |
| Packaged-engine smoke test | `desktop.py --self-test` passed |
| **Windows x64 build, both modes** | Built here on Windows 11 x64. Frozen self-test inside **each** artifact: **11 of 11 checks passed** (`frozen: true`) |
| **Stand-alone EXE launch** | `KADOMA-0.2.0-Windows-x64-standalone.exe` launched as a user would run it: opened a loopback service on `127.0.0.1`, refused an unauthenticated probe with **HTTP 401**, served the bundled interface (12,697 bytes), and created a native window titled **`KADOMA — Offline PDF Studio`** |
| **SHA-256 manifest** | All three artifacts re-hashed independently; **3 of 3 matched** `release/SHA256SUMS.txt` |
| JavaScript runtime errors | None in any run |
| External page requests | None; all resources came from the local app origin |

New direct-edit checks, all run in headless Chromium against a live local server:

1. Clicking a line opens an editable box whose position and width match that line,
   and whose font size follows the original 32 pt text.
2. Typing on the page writes into the document; the editor closes on Enter.
3. The exported PDF contains the new text at the **original 32 pt size**, the old
   text is gone, and the line grew wider than the original selection box.
4. Undo restores the original wording.
5. Double-click starts an edit while the Select tool is active.
6. Escape cancels without changing the document revision.
7. Clearing the box deletes only that line; other text on the page survives.
8. The side panel and the on-page editor stay in step.
9. The existing span-selection targets are still present (no regression).

Engine-level additions: page text is grouped into editable runs (sentences stay
together, table cells and right-aligned labels stay separate); an empty
`replace_text` now deletes; and a replacement box is widened into measured free
space — never past neighbouring text — so a longer line keeps its font size.
Five engine tests and one API test cover these, including a test that a grown box
never overlaps the next table cell.

### Windows x64 artifacts actually built here

Produced by `python scripts/build.py --mode both` on Windows 11 x64 with Python
3.13.14. Sizes and hashes are the real outputs, not estimates.

| Artifact | Size (bytes) | SHA-256 |
|---|---:|---|
| `KADOMA-0.2.0-Windows-x64-standalone.exe` | 55,150,870 | `071406c331b0d4ae7110ea71b29b89f605cbaea7f29edff1b9636f963ab41e20` |
| `KADOMA-0.2.0-Windows-x64-portable.zip` | 55,122,898 | `8a613a057ebb5cb4e06946724a6f876d4fda9fc6db43af7a640d3699739f7cf7` |

`release/SHA256SUMS.txt` is the authoritative record and covers all three files,
including `KADOMA-0.2.0-source.zip`. That archive is deliberately **not**
listed in this table: this report is stored inside the archive, so its own hash
would change every time the report is edited. Verify any download with:

```bash
python scripts/verify_sums.py release/SHA256SUMS.txt
```

`BUILD_INFO.json` records `buildModes: [folder, onefile]` and
`packagedEngineSelfTest: {folder: 11, onefile: 11}`.

The stand-alone EXE is one file with **no sibling folder** — it unpacks itself to
a temporary directory at start-up, so its first launch is a few seconds slower
than the portable build. The portable ZIP must be extracted and kept together.

Two notes on how this was verified, because both tripped up earlier attempts:

- The launch check **cannot** match the port to the process it started. A
  one-file build re-executes the real application as a *child* process, so the
  bootloader PID never owns the listening port. The verifier therefore snapshots
  loopback listeners before launch and accepts a port that appeared afterwards —
  which is the security-relevant property, since the shell binds `127.0.0.1` only.
- The window title is read through the Win32 API, **not** `tasklist`. `tasklist`
  reported the literal placeholder `N/A` for this window, which a naive
  truthiness test would have counted as a passing "window exists" check.

**Outstanding:** no macOS APP/DMG was built here (this is a Windows machine), and
no Inno Setup installer was generated (Inno Setup 6 is not installed). Interactive
hand-on-GUI testing — actually clicking into the page and typing under WebView2 —
has not been performed; the automated launch check above proves the packaged app
boots, serves its own UI, gates its API, and opens a window, but it does not
simulate a human typing. The one concrete risk — the desktop shell disables text
selection globally — was checked against the pywebview 6.2.1 source: it appends
`body { user-select: none; cursor: default }` to `document.head`, with no
`!important`. The editor re-enables selection with an ID selector plus
`!important`, which outranks that rule on both specificity and importance, so
the override is sound by inspection. Typing in the real GUI on each target
machine remains a release acceptance test.

---

# KADOMA 0.1.0 — verification report

Date: **11 October 2026**. Environment: Linux / Debian 13, Python 3.13.16.
This is development verification, **not independent security certification**.

## Completed checks

| Check | Actual result |
|---|---|
| Python compile and JavaScript syntax | Passed |
| Engine/API test suite | **36 passed**, 0 failed; one non-failing Starlette/httpx TestClient deprecation warning |
| Optional Office creation | Real DOCX, XLSX and PPTX converted by locally installed LibreOffice; searchable output text verified |
| Optional OCR | Real Tesseract recognition of a rendered scan; saved output PDF contains searchable text |
| Local browser workflows | **19 workflow checks passed**, including inspection of actual downloaded PDFs/XLSX files |
| Hosted-preview privacy | **2 checks passed**: accurate remote-processing label even with a fake session hash; zero upload requests before user consent and one after approval |
| JavaScript runtime errors in workflow run | None |
| External browser page-resource requests | None; all app resources came from the local app origin |
| Native-resource packaging smoke test | PyInstaller **Linux** frozen-engine smoke test passed for real PDF, DOCX, XLSX, PPTX, image ZIP exports, encryption and form operations. Linux result is not Windows/macOS certification. |
| Native dependency availability | Published PyMuPDF 1.28.2 wheels observed for Windows x64, macOS x86_64, macOS arm64; does not prove the finished app's compatibility |
| PDF image redaction | Extracted underlying image pixels in the redacted region are white, not the original red pixels beneath a cover rectangle |
| PDF text/field redaction | Target text and overlapping form values absent from reopened exported PDFs; undo/redo cleared |
| Attachment/metadata stripping | A real embedded test attachment and sensitive metadata removed from redacted output |
| Existing encryption | Normal save/export retains original password protection; owner and user permissions checked |
| Duplicated forms | Copied fields have unique names and independently fillable values, leaving originals unchanged |
| PDF permission categories | Page assembly and text modification checked independently; form filling supported without copy permission when explicitly allowed |

During packaging verification a python-pptx resource-path issue was found and
fixed: all OOXML templates are now collected, with a physical `pptx/oxml` resource
marker so its `../templates` paths work in frozen builds. The expanded packaged
smoke test exercises these paths rather than merely launching the program.

The browser preview keeps strict script CSP. The authenticated desktop shell
permits `unsafe-eval` only for pywebview's trusted native API generator, which
uses `new Function`; the policy difference is explicitly tested. Native Save
dialog behavior remains an outstanding real-OS GUI acceptance test.

## 19 browser workflow checks

1. Sample PDF, local font, thumbnails and rendering load.
2. Direct text replacement.
3. Undo/redo.
4. New text and offline document search.
5. Actual text/dropdown/checkbox form filling.
6. New fillable field creation.
7. Typed visual-signature image placement.
8. Actual highlights and PDF comments.
9. Rotate, duplicate, delete, drag-reorder pages.
10. Merge a PDF through the file picker.
11. Insert and replace an embedded image.
12. Real Excel workbook export through the UI.
13. Reopened downloaded PDF contains intended edits and field values.
14. AES-256 encrypted output requires the right password and restricts modification.
15. Reopened redacted PDF no longer contains the selected account reference.
16. OCR output contains saved searchable invoice text.
17. Localized scan-text replacement removes old OCR text in output.
18. Compact desktop layout and honest feature-limit guide.
19. No browser runtime errors or external app-resource requests.

These checks are reproducible with `scripts/check_ui.py` and
`scripts/check_preview_privacy.py`, after starting the local development server.
Optional OCR checks skip when Tesseract is unavailable. Browser testing is not a
native pywebview/WebView2/WKWebView test.

## Outstanding release acceptance tests

**No verified Windows or macOS installers are included in this delivery.**
The source/build kit has been prepared, not deployed into the user's repository.
For 0.3.0 specifically, a Windows portable ZIP and a stand-alone EXE **were**
built and launch-verified here (see the 0.3.0 section above); no installer, and
no macOS artifact, exists yet.

- Run the native Windows x64 workflow; inspect the EXE and Setup.exe outputs.
- Run the native Apple Silicon workflow; inspect its APP/DMG outputs.
- Run the native Intel Mac workflow; inspect its APP/DMG outputs.
- Launch each GUI on a real intended target machine and test the native file
  picker, Save dialog, drag-and-drop, fonts, high-DPI rendering, and keyboard shortcuts.
- Test Windows WebView2 missing/present behavior and installer uninstall/upgrade.
- Test macOS Gatekeeper, minimum OS compatibility, app copy/install, and both architectures.
- Configure Windows Authenticode and macOS Developer ID signing/notarization for
  production distribution. Current recipes are unsigned / ad-hoc signed only.
- Test large, damaged, unusual-font, rotated-text, password-protected, complex
  form, scanned-table, right-to-left, and previously signed PDFs on each platform.
- **Right-to-left on other machines.** Font availability drives round-trip quality,
  and the app measures it per machine. Check the reported `rtlQuality` on a Windows
  machine with Arabic language packs installed, and on macOS (Geeza Pro) and Linux
  (Noto/Kacst) where no Arial or Tahoma is present.
- **Bidirectional mixed Arabic/Latin lines**, which currently rely on MuPDF's bidi
  implementation and were not separately verified.
- **The default-app Settings flow end to end**: click Register, confirm in the
  Windows Settings page, then double-click a PDF in Explorer and check it opens in
  the running window. The registry state and the handoff were verified
  automatically; the Settings confirmation is a user action.
- Independently audit redaction and security with representative documents.
- Validate LibreOffice/Tesseract behavior on Windows and Mac, including temporary
  file cleanup, language-pack setup, and external-reference handling.
- Review all dependency redistribution requirements, including corresponding
  upstream sources required by applicable AGPL/native binary licenses.

## Known boundaries

See `FEATURES.md` and `README.md`. Word/Excel conversion is best-effort, PPTX is
raster slide export, signatures are visual, and cloud/AI/remote review and
signature tracking are intentionally not implemented. No precision, compliance,
or legal-equivalence claim is made for this initial version.

Hosted preview uploads are processed in a hosted workspace, **not on the
visitor's computer**. It is suitable for non-sensitive samples. Native desktop
builds use an authenticated loopback engine and are intended for local processing.
