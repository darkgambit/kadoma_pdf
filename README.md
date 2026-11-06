# KADOMA PDF — Offline PDF Studio

**A working offline-first PDF application, with editing and page management as
its focus.** Original interface; not an Adobe product or an Acrobat-equivalent
implementation. Version 0.25.0. It opens on a **home screen** that lays the tools
out the way Acrobat's does, every page carries its own **rotate / extract /
delete** tools, and the print dialog offers **pages, copies and the printer's own
settings**. The
document then opens for **reading** rather than editing, the interface has a
**dark mode** that leaves the page white, and the bars around the page are
thinner so the document gets the room. The native EXE/APP still needs release QA.

> **Delivery status:** The application source, working browser preview, tests,
> and native build recipes are included, together with a Windows x64 build that
> is produced and launch-verified on this machine. macOS APP/DMG binaries must
> be built on the corresponding Mac architecture. Renaming a Linux binary to
> `.exe` would not make it compatible.

## What works

| Feature | Implementation and boundaries |
|---|---|
| Open / create PDFs | PDF viewing, drag-and-drop, new blank A4 PDFs, JPG/PNG/WebP/BMP/TIFF image import; multi-frame images use their first frame. |
| Office → PDF | Word, Excel, PowerPoint and supported OpenDocument files through **locally installed LibreOffice**. Source print/layout settings affect the output. |
| Local HTML / text → PDF | Sanitized text extraction and local Unicode layout. No live webpage fetching, scripts, external resources, or pixel-identical webpage rendering. Markdown is treated as plain text. |
| Save and Save as | **Save** writes the document over the file it was opened from; **Save as** asks where the copy should go and the document follows it, so later saves keep writing there. Both are buttons beside Export and on **Ctrl/⌘ S** and **Ctrl/⌘ Shift S**. The header says **Saved** or **Unsaved changes**, decided by the engine from the revision it last wrote rather than from what the interface remembers. An overwrite is **refused with a reason when the file changed on disk since it was opened** — a sync client or another editor is never silently replaced, and Save as is still offered. The bytes go to a temporary file beside the destination and are moved into place in one step, so a failed write cannot leave a half-written PDF where a good one was. A password-protected file keeps its encryption, both passwords and its permissions when saved over (measured). A document opened from the browser picker, created blank, or converted from `.docx` has no file to write over, so its first Save asks where to put the copy. **Desktop only**; the browser preview says so and offers the export instead. |
| A home screen, laid out like a PDF application | Opening KADOMA PDF lands on a **Home** screen rather than on a document: a **Search tools** field, a **Create & Edit** grid (Create PDF, Combine Files, Organize Pages, Edit PDF, Export PDF, Scan & OCR), a **Forms & Signatures** grid (Fill & Sign, Sign, Protect), and the same tools as a list down the right. Every card calls the action the toolbar calls — nothing is a picture of a feature. **Recent** lists the documents open in the workspace. The search narrows the grid and deliberately leaves the tool list complete. The **Edit** tab, a Recent row, or the wordmark (which goes Home) move between them. |
| Page tools while scrolling | The **Pages** view lists every page and each one carries **rotate**, **extract** and **delete** on the page itself; the toolbar still acts on a multi-page selection, **Split** is beside **Add pages**, and drag-to-reorder is unchanged. The Home screen has a **Page tools** group that opens the same view, and a **Select** group in the header picks **Odd** (1, 3, 5…), **Even** (2, 4, 6…), **All** or **None** so deleting every other page is two presses. |
| Print options | The print dialog offers **Pages** (all, current, or `1-3, 5`), **Copies** (1–99) with a **collated / uncollated** order, **Paper** (defaulting to **A4**, the content scaled to fit) and **Orientation**, which starts on **Auto** and follows the page on screen — turn to a landscape page and the sheet turns with it. **Sides** offers two-sided printing when the driver reports it. Everything else the driver knows — quality, trays — is one press away in **Printer properties…**. The preview is drawn on that paper, and the order of copies is written out page by page so it can be checked before pressing Print. |
| Tabs, a scrolling page, and a page menu | One **tab per open document** (shown when more than one is open), the editor shows **every page in one scrolling column**, and **right-clicking a page** offers rotate left/right, extract, duplicate and delete. |
| Save before closing | Closing a document with unsaved changes asks **Save and close / Close without saving / Cancel**; a clean document closes without a word. |
| 500 MB | Working documents and uploads go to **500 MB** (was 250 MB); combining 500 MB; export 500 MB. |
| Scans | A page with no text layer says so, offers **Make this page searchable** (OCR), and explains which tools still work on it. |
| Protection and scans | Protect opens a **password prompt** with live validation; a scanned page offers **Make it editable** and becomes clickable after local OCR. |
| The window title | **KADOMA PDF**, with no subtitle. The offline claim lives in the status bar and the scope card instead. |
| Scanned pages | Drag a box over the words with the text tool to replace them — the old ink is painted over with the paper colour and the new text is real, selectable text — or press **Make it editable** to OCR the page so every line can be clicked. |
| Dates | The **Date** tool writes a date you pick from a calendar into the page as selectable text, in four formats, at the size and colour you choose. |
| Closing | A document nobody has changed closes instantly with no prompt. A changed one asks **Save and close / Close without saving / Cancel**. |
| Document tools | A **Document** view with nine tools: **Watermark**, **Header & footer**, **Page numbers / Bates**, **Crop**, **Bookmarks** (generated from the headings), **Attachments**, **Reduce size**, **Page size** and **Compare**. See `docs/ACROBAT-PARITY.md` for how this compares with Acrobat Pro, and what is still missing. |
| Combine from Explorer | Select any number of PDFs in File Explorer, right-click, and choose **Combine with KADOMA PDF** — the files are read, joined in the order you selected them, and the result opens as one working document named after their folder. The entry is added per user (no administrator rights) under `SystemFileAssociations\.pdf`, with `MultiSelectModel=Player` so Explorer keeps it visible for a multi-selection, and the command is `--combine %*` — every selected file, not just the first. If KADOMA is already running the work is handed to that window instead of starting a second copy. Every file is checked for a PDF header, so a text file renamed `.pdf` is refused by name rather than combined. |
| Prepare Form | A tool for the file, not the application: it scans the document for the places a form belongs — runs of underscores, drawn boxes, and labels that end in a colon — lists what it found with the type and page, and adds the ones you keep as **real AcroForm fields**. Date fields carry the two JavaScript actions Acrobat writes for its own date picker. The form is finished off with the document-wide **`/DR` font resources** and a **`/P` page link on every widget**, which is what a strict reader needs before it will let anybody type — Chrome and MuPDF manage without them, Acrobat does not. `scripts/check_reader.py` proves it by filling the exported form in Chrome with KADOMA closed. |
| Nothing opens by itself | The application ships **no sample document**. It starts on Home with an empty workspace, and a document arrives when one is opened, created or dropped. The audit asserts both halves of that: nothing is open on start, and a tool pressed with nothing open says so instead of failing quietly. |
| The tool list, beside the document | The list of tools the home screen keeps on the right is also on the right **while a document is open**, so a tool is one press away instead of a trip back to Home. It is the same list, calling the same actions — nothing in it is a picture of a feature. **All tools** in the menu bar puts it away and brings it back, and hiding it hands the width straight back to the page. Home keeps its own copy, so the two can never disagree. |
| Copy a page out as a file | Right-clicking the page **while scrolling** offers **Copy page to a file…**: a one-page PDF, under a name typed in the dialog (suggested as `<document> — page N.pdf`). Characters a file name cannot hold are cleaned rather than refused, and `.pdf` is added once whether or not it was typed. The desktop build asks where to put it in a real Save dialog; the browser preview downloads it. The document on screen is not changed — the copy is made from the page as it stands. |
| Stamps | Seven standard marks — Approved, Reviewed, Draft, Confidential, Final, For Public Release, Void — or your own text, placed **where you click** on the page with an optional date underneath. The label goes in as **real text**, so it can be selected, searched and copied; the frame is pulled back onto the page rather than hanging over the edge. |
| Links | **Drag a box** on the page and point it at a web address or a page in the same document. The page's links are listed with a remove button each, and an address that is not an address is refused with a reason instead of being written into the file. |
| Page size | A3, A4, A5, Letter, Legal, Tabloid, or a custom size in **millimetres, points or inches**, on every page or a range. With scaling on, the content is multiplied into the new box **and** every form field, comment and link is moved with it — a signature field left behind would point at blank paper. Without scaling the paper changes and the content keeps its size, anchored at the top-left corner. |
| Compare | Two open documents or a file from disk, compared **page by page and word by word**: which pages differ, how many words were added and removed on each, and a jump to the page. It compares text, not pixels, and the dialog says so. |
| Reading view by default | A document opens **for reading** at **150%**, which is the size an ordinary page needs to be readable without leaning in; the zoom control still overrides it, and **Fit width** is one choice away. The page is shown as it is, with no text boxes, no edit cursor and nothing waiting to be clicked. **Edit text** is one press away in the toolbar, **double-clicking a line** still starts an edit immediately, and **Esc** returns to reading. A PDF whose owner forbids editing opens in the same view instead of a disabled editor. |
| Dark and light | **Dark is the default**, not the system's preference: a PDF viewer is mostly a white page, and a dark surround keeps the eye on the page. A **moon/sun button** switches the whole interface, and a choice made there is remembered and wins from then on. **The page stays white in both** — it is paper, and it should look on screen the way it will look on the printer. The theme is the **only** thing the application stores: one `localStorage` key holding `light` or `dark`, with nothing about any document. It is applied before the page is drawn, so a dark launch does not flash white. |
| A thinner frame | The five bars above the page are **61 px shorter**, and the document bar's secondary buttons are **icons with their names on hover** (Save keeps its word). The action cluster fell from 947 px to 448 px: about **70 px more height and half a screen more width** for the page, with no overflow down to 1024 px. |
| Several documents open at once | **Opening a document no longer closes the one before it.** The workspace keeps up to **6 documents** open and a button beside the document name lists them with their page count, size and whether they have been edited — switch between them, or close one. The current document asks before closing if it has unsaved changes. Past the limit the oldest closes, which the menu says rather than leaving it to be discovered. Documents are edited in memory and written only when you save or export, so nothing is recovered after a restart, and there are no tabs or side-by-side view: one document is on screen at a time. |
| Combine files | One **Merge** window handles every way of putting files together. **Documents already open in the workspace are listed in the same window** with an *Add* button, so a document in the app can be combined without being found on disk and uploaded again; its password is the one already used to open it, so an open protected document is not unlocked twice. Open documents and files from disk can be mixed in any order, and the order is carried explicitly. The document being merged into is listed but cannot be added to itself for append/insert — building a new PDF from it is allowed. | Choose PDFs, images, local text/HTML and optionally Office files; the window lists each one with its **real page count** and flags any that cannot be read. **Reorder** the list, **remove** a file you picked by mistake, and take **only some pages** of a source (`2-3, 7`) instead of all of it. A **password-protected** file is unlocked in the window rather than refused. Then either **append** the result to the end of the open document, **insert** it in front of any page, or **build a new PDF** that leaves the open document untouched. Dropping several files onto the window opens the same list. Combining is atomic: a file that fails leaves the document exactly as it was, and the whole operation is one undoable step. |
| Edit PDF text directly on the page | Click any line of text and type over it. An editable box opens over that exact line, matching its font size, colour, and rotation, with the page background sampled behind it so it blends into tinted cards. **Enter** applies, **Esc** cancels, clicking away applies, and clearing the box deletes that line. Double-clicking text starts an edit with any tool active. The original text is removed, then the replacement is laid out locally: it **grows into free space to the right** so a longer line keeps its font size, and shrinks only when it meets other text or the page margin. Substitute sans/serif/monospace families are picked from the original font. No font-identical whole-document reflow; a paragraph is edited one visual line at a time. |
| Add text / images | Draw a placement rectangle and insert actual PDF text or an embedded image. Rotated page coordinates are supported. |
| Arabic and other right-to-left text | Arabic, Hebrew, Persian and Urdu are shaped, joined and laid out right-to-left, and read back as the letters you typed. Typing in Arabic switches the in-place editor to right-to-left. Arabic text is searchable even though the document stores it in shaped form. A font that round-trips Arabic exactly is chosen by measuring the fonts on your machine; the app reports whether it found an exact or only an approximate one, and bundles a fallback so Arabic never silently fails. See the limits below. |
| Send or share a PDF | **Desktop app only.** Share writes an export into a stable temporary share folder and then offers four real options: **open a new message in your mail program with the PDF already attached** (a genuine compose window — Outlook's own `/c ipm.note … /a` command, or Thunderbird's `-compose`; the recipient box is left **empty on purpose**, the message body starts as *“Please see the attached file”*, and nothing is sent until you press Send), open a plain **`mailto` draft** without the file and with the PDF copied to your clipboard, **copy the file** itself, or **show it in its folder**. No mail password is stored and KADOMA never sends anything. |
| Be your default PDF app | **Desktop app only, Windows.** KADOMA registers itself as a PDF handler under your own user account (no administrator rights) and then opens the Windows Settings page where you confirm it. Windows deliberately does not let any application claim a file type silently, so that final confirmation is yours to make. On macOS the app declares the PDF type in its own bundle and appears under "Open With" automatically. Double-clicking a PDF opens it in the running window instead of starting a second copy. |
| Replace / delete images | Select an embedded image and update it. Changes affect **all uses of the same image object**. Inline images and arbitrary vector-object editing are not supported. |
| One side for every tool | The left rail is gone: the view tabs (Edit, Pages, Convert, Forms, Protect, OCR, Read) live in a **menu bar across the top**, so the page begins at the left edge of the window. The page thumbnails and the tools panel are both **opt-in**, both sit on the **left** when shown, and nothing is ever on the far side of the page. The tools panel also has a **pin**: pinned (the default) it stays open, unpinned it **auto-hides to a 38 px rail** and returns on hover, on keyboard focus, or from its tab — **floating over the page** so the document never shifts sideways. |
| A page as large as the window allows | **Fit width genuinely fits.** It used to stop at 125%, which left a quarter of an ordinary window empty; it now fills the width up to 300%. The page is **rendered at the size it is shown**, so a large page is a real rendering rather than a small image blown up. With both panels away the page has the whole window, and the zoom control still overrides the fit at any time — 50% to 300%, Fit width, Fit page, and zoom in/out. |
| AI reading | An **AI reading** view with two tools. **Summarise** gives an offline extractive summary — the sentences that best represent the document, ranked by word frequency and quoted as they stand — plus the document's key terms. **Build a form from a prompt** turns ordinary words ("full name, email, date signed, and a checkbox to agree") into **real PDF form fields**, laid out on a new page in one undoable step. Both run on this computer with no network, and **neither is a language model**: they do not paraphrase, invent or answer questions, and every result says so. **A model is optional and off by default** — connect your own OpenAI-compatible endpoint, model and key and summaries are written by it; only the document's extracted text is sent, only after you agree, and the key is held in memory and never written to disk. |
| Organize pages | Insert, delete, duplicate, reorder by dragging, rotate, extract selected pages, split pages into a ZIP. Cloned form fields receive unique names so values stay independent. |
| Split one PDF into several files | One **Split** window handles every way of dividing the open document. Decide the cuts by **equal blocks of pages** (`1` gives one PDF per page), by a **chosen number of files** (divided as evenly as the page count allows, longer parts first), or by **your own page ranges** (`1-3, 4-6, 7-10`, one file per range). The window **lists every file it is about to create**, with the page span in the name, and the list, the file count and the button label all come from the engine's own plan endpoint — so the preview and the result cannot disagree. A range past the last page, more files than there are pages, or a block size of zero is refused with the reason before anything is written; a range that leaves pages out is allowed but the window **names the pages that are in no part**. One part is delivered as a plain PDF, several as a single ZIP. Forms, links and annotations travel into every part, and a split only ever reads: the open document is untouched and no undo step is recorded. Protected PDFs are refused rather than silently handed back unprotected. |
| Undo / redo | In-memory snapshots, up to 12 steps / 100 MB of undo history per document. Redaction deliberately clears history. |
| Export Word | Best-effort editable text, tables and images to `.docx`; layout, fonts and reading order may differ. |
| Export Excel | Detect ruled or borderless tables and create `.xlsx` worksheets. Currency/percentage text is parsed as numeric values where simple. Formula-like untrusted strings are escaped. Verify all financial results. |
| Export PowerPoint | `.pptx` with one rendered **page image** per slide. Not editable slide text or vector graphics. |
| Export images / text | PNG/JPG page-image ZIPs and searchable text to UTF-8 `.txt`. |
| Visual e-signature | Type or draw a signature and place its image. **Not certificate-based signing**, identity verification, signature requests, or agreement tracking. |
| PDF forms | Create actual AcroForm text fields, **date fields**, checkboxes and dropdowns. A date field is a real form field that carries its own format (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, `DD.MM.YYYY`) and opens a **calendar to pick a day from** instead of making you type one; anything that is not a real date in that format is refused rather than stored as free text, and a date typed elsewhere is normalised into the field's own format. Fill supported existing fields. Read-only/unsupported fields are not filled, and emptying a field really removes the value rather than only blanking its appearance. |
| Print | **Desktop app only.** The **Print** button and **Ctrl/⌘ P** open a **print preview** with a **printer to choose**. The preview is the sheet, not the page: its paper size and its margins come from the chosen printer, and the page is drawn inside them at the scale the print path uses, so what is on screen is what comes out. The arrows step through the pages and choosing another printer redraws the sheet, because another printer may load another paper size. Pressing **Print** renders every page at print resolution (200 DPI) and sends the job straight to that printer — **no other PDF application is involved**, so this still works when KADOMA itself owns the `.pdf` association and can never start a second copy of KADOMA. The app's own interface is never part of a printout: only the document's pages are drawn. Printers that save to a file instead of printing ("Microsoft Print to PDF", XPS, OneNote, Fax) are detected and named in the preview rather than offered, because a job sent to one of those waits on a Save dialog the user cannot see. |
| Clear a filled-in form | Empty every filled text, date, checkbox and dropdown value in one step, after a confirmation. The fields themselves and all page content stay exactly where they are, and the clear is a normal undoable edit. Read-only fields are left alone. |
| Password protection | Export an AES-256 encrypted PDF with separate opening and owner passwords; choose printing/copying/editing permissions. Existing encryption is preserved by normal PDF export. |
| Real redaction | Remove selected text, overlapping image pixels and touched vector graphics; remove overlapping fields/comments. Strip attachments, JavaScript, metadata and thumbnails; save with garbage collection and clear app undo history. Original source files remain unchanged by the editing/redaction operation; save the export under a new name to preserve them. |
| Comments / highlights | Actual PDF annotations, stored in exported copies. Review feedback can be exchanged by passing these copies manually. No live multi-user collaboration. |
| OCR | Optional local **Tesseract** recognition of up to 20 selected pages per run, producing saved searchable raster PDF pages at 200 DPI. Forms/annotations on those pages are flattened. OCR text can be exported to Word; local text replacement detects Tesseract's GlyphLessFont and erases the selected raster area against white before inserting replacement text. Recognition and geometry must be checked. |
| Search | Offline search with page navigation and matching-region overlays. |
| Privacy | No cloud API, telemetry, account, remote font, or runtime CDN. Document bytes and undo history are kept in memory, not a persistent library, and nothing is written to disk until you press Save, Save as or export. Native saves and exports use a system Save dialog. |

## Not implemented

- Cloud synchronization or OneDrive / Google Drive / Dropbox / Box integrations.
- Online review sessions, automatic feedback collection, remote signature
  requests, identity verification, agreement status tracking.
- Question answering, chat, translation, rewriting or document generation. The AI
  reading summarises and builds forms; it is not a conversational assistant.
- Cryptographic certificate signing or signature validation.
- Acrobat-level conversion fidelity, arbitrary vector-object manipulation,
  font-perfect reflow, PDF/A conformance, or accessibility tagging.
- Tabs, a split view, or side-by-side comparison of the documents held open. One
  document is on screen at a time; the others are reachable from the switcher.
- A remembered window arrangement. Which panels are open, and how far the page is
  zoomed, last for the session only, because this application writes no preferences
  to disk.
- Session restore. Documents are edited in memory and only written when you save
  or export, so a restart begins with the sample document and nothing from the
  previous run comes back.
- A print dialog with a live preview, a page range, copies, duplex, or paper
  size. Printing sends **every page** to the chosen printer at print quality,
  which is what "print this document" means; the printer's own settings are
  where those choices live.

These are deliberately absent, not non-working buttons hidden behind an
“upgrade” screen.

### Right-to-left text: what is and is not guaranteed

- Shaping, joining and right-to-left order are correct. Text is stored and read
  back as the letters you typed, not as the internal shaped forms.
- **Arabic-Indic digits may come back in a different but equivalent variant.**
  A font may map the digit glyphs to the Extended/Persian block, so `٩٩٩٩` can be
  stored as `۹۹۹۹`. They render identically and searching folds the variants
  together, but the extracted text is not byte-identical to what was typed.
- The **quality of the font matters more than it looks.** MuPDF derives the
  reverse text mapping from the font itself, and some fonts map their ligature
  glyphs back to the *wrong* characters — they look perfect on the page but read
  back corrupted when the line is edited again. Measured on Windows: Arial and
  Tahoma are exact; Segoe UI, Dubai, Microsoft Sans Serif and Calibri lose the
  lam-alef ligature. KADOMA therefore **measures** the fonts present on your
  machine and picks the most faithful one, rather than trusting a fixed list.
  The app reports `exact` or `approximate` in its health response, and the
  in-app console notes when only an approximate font was available.
- The bundled fallback font (Noto Sans Arabic) is **approximate**: it renders
  correctly but does not round-trip the lam-alef ligature exactly. It exists so
  Arabic still works on a machine with no Arabic system font at all.
- RTL replacement text grows into free space **to the left**, because that is
  the direction it reads in. Growing right would push it over the page margin.
- Bidirectional mixed lines (Arabic and Latin in the same line) rely on MuPDF's
  bidi implementation and have not been separately verified.

### Sharing: what it deliberately does not do

- KADOMA never sends email itself and stores no mail credentials. It hands a
  prepared message to your own mail program.
- A `mailto:` link **cannot carry an attachment** — the standard has no such
  parameter. That is exactly why "Email with the file attached" builds a real
  `.eml` message instead. The other option is honest about the limitation: it
  opens a draft and puts the file on your clipboard to paste in.
- Sharing is a desktop feature. In the hosted browser preview these endpoints
  refuse the request rather than pretending to work.

### Printing: what it does and does not do

- The pages are rendered here and sent to the printer through the operating
  system's own print interface. KADOMA does **not** hand the file to another
  program to print it. That matters for one specific reason: once KADOMA is
  your default PDF app, "print this file" resolved through the file association
  would come straight back to KADOMA, and a print verb that reopens the
  application is a loop. Rendering and printing locally cannot recurse.
- **The preview is the sheet.** Paper size, orientation and the unprintable
  margins are read from the chosen printer, and the page is placed inside them
  at the same scale the job uses. When no printer can be queried — or on a
  platform where KADOMA prints through CUPS — the preview falls back to the
  page's own proportions, and the dialog says the margins are not the printer's.
- **Every page is printed**, at 200 DPI, scaled to fit the printer's printable
  area and centred. There is no page range, copy count, duplex, or paper-size
  choice in KADOMA — those belong to the printer driver, and KADOMA asks
  the driver for the paper it is set to use.
- The app's own buttons, panels, and toolbars are never drawn, because only the
  document's rendered pages are sent. Nothing about the interface can reach
  paper.
- A printer whose job saves to a file — "Microsoft Print to PDF", "Microsoft XPS
  Document Writer", OneNote, a fax driver — is **detected and named rather than
  offered**. Sending a job to one of those raises a Save dialog owned by another
  process, which from here looks like a request that never returns. The preview
  says which one it skipped and why, lists the printers that can actually put
  ink on paper, and keeps **Export instead** one press away.
- Printing is a desktop feature. In the hosted browser preview the print
  endpoint refuses the request.

### Date fields: how they are stored

A PDF has no date field type, so a KADOMA date field is an ordinary text
field carrying two private keys that record that it is a date field and which
format it uses. Consequences worth knowing:

- **Any PDF reader can display a date field** and its value, because it is a
  plain text field underneath. Readers that do not know the two keys will show
  it as a text box and will not offer a calendar.
- The keys **survive saving and reopening** — that is tested directly, because a
  marker that is lost on save would silently turn every date field back into a
  text box.
- The format is enforced on entry, not just displayed. `31/02/2027` is refused
  rather than rolled over into March, and a date typed in ISO form is rewritten
  into the field's own format.
- The value is a date **string**, not a PDF date object, so it is what other
  readers show rather than something a form-calculation engine would compute on.

### Combining files: what it does and does not do

- **One window, three destinations.** The same list can be appended to the open
  document, inserted in front of any page of it, or built into a new PDF. There
  is one code path behind all three, so a page range or a password behaves
  identically whichever you pick.
- **Nothing is guessed.** The window shows each file's real page count, read
  from the file itself before anything is combined, and flags a file it cannot
  read instead of quietly leaving it out. A page selection that runs past the
  end of a source — `1-9` of a 3-page document — is refused, not silently
  shortened, because dropping pages from a merge is how part of a document goes
  missing without anybody noticing. The button says how many pages the result
  will have, and that count follows the page ranges you type.
- **A password-protected source is unlocked in place.** Page counts are readable
  even in an encrypted PDF, so the file is listed with its size and a password
  box rather than rejected outright. Until the password is right, Combine stays
  disabled with a reason.
- **The whole combine is one undoable step**, and a file that fails leaves the
  document byte-for-byte as it was — nothing partial is written. Form fields,
  links and comments are carried over from the sources.
- **Limits:** 500 MB combined, and 500 pages in the resulting document. No file
  count cap.
- Combining is a local operation and works in the hosted browser preview too;
  the files are processed in that workspace, as the preview states.
- **Not included:** comparing or de-duplicating pages between files, merging
  only the annotations from another document, or reconstructing a bookmarked
  outline across the join. Bookmarks and named destinations that came from a
  source are carried by the page copy, but no new combined outline is built.

## Run from source

Python **3.11–3.13** is recommended. Dependency installation needs internet;
after installation the application itself does not require a connection.

### Windows

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
.venv\Scripts\python.exe desktop.py
```

Use 64-bit Python. Windows 10/11 x64 is the intended target. The **Microsoft Edge
WebView2 runtime** is required by the native shell and is not bundled. Install
Microsoft's official runtime if the desktop window cannot start.

### macOS — Apple Silicon or Intel

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-desktop.txt
.venv/bin/python desktop.py
```

Use native arm64 Python on Apple Silicon, native x86_64 Python on Intel. The
macOS shell uses built-in WKWebView. Native minimum-OS compatibility and GUI
behavior still need verification on the actual deployment machines.

### Browser preview / development

```bash
python -m pip install -r requirements.txt
python run_preview.py --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. A real sample report is generated when a workspace
starts. The hosted development preview binds `0.0.0.0` only so the preview proxy
can reach it. **In the hosted preview, uploads leave your computer and are processed
in the hosted workspace. Use sample or non-sensitive files only.** The interface
labels this mode and requests confirmation before the first upload. Native builds
process locally. **Do not expose this anonymous development service publicly or
use it as a production cloud server.** The desktop launcher instead binds loopback
and sets a random request-authentication token.

## Generate Windows EXE and both Mac builds

### Ready-made Windows build

A Windows x64 build is already produced and launch-verified on Windows 11:

| File | Size | What it is |
|---|---:|---|
| `release/KADOMA-0.11.0-Windows-x64-standalone.exe` | 55,456,349 B | **One file.** Copy it anywhere and run it. No companion folder. Unpacks itself at start-up, so the first launch is a few seconds slower. |
| `release/KADOMA-0.11.0-Windows-x64-portable.zip` | 55,430,946 B | Extract and run `KADOMA\KADOMA.exe` **inside** the extracted folder. **Recommended if you want KADOMA as your default PDF app** — see the note below. |
| `release/KADOMA-0.11.0-source.zip` | see manifest | Source archive. **Its size and hash are not printed here on purpose**: this README is inside that archive, so writing the number down changes it. `release/SHA256SUMS.txt` records the current value — read it there. |

**One-file vs. portable, for the default-app feature.** A double-clicked PDF
starts a second copy of the app, which must notice the running instance and hand
the path over. The one-file build extracts its whole ~55 MB payload *before* it
can do that, so the handoff measured **33.9–53.1 s** on a cold cache across versions
0.7.0 to 0.11.0 — it depends heavily on how busy the machine is; the portable
folder build does it in **2.3 s**. Both behave correctly — no
duplicate window, no duplicate service, the file is not dropped — but the
portable build is the better choice for everyday double-click use.

`release/SHA256SUMS.txt` lists the SHA-256 of each file; `release/BUILD_INFO.json`
records the toolchain and self-test counts. Verify a download with:

```bash
python scripts/verify_sums.py release/SHA256SUMS.txt
```

Windows needs **Microsoft Edge WebView2** for the native window; it ships with
Windows 11. These binaries are **not Authenticode-signed**, so SmartScreen may
warn on first run.

### Option A — automated native build jobs

1. Put the contents of this folder in a repository, including `.github/`.
2. Enable repository Actions and open **Desktop installers**.
3. Run the workflow manually. The three native jobs use:
   - `windows-2022`: Windows x64;
   - `macos-14`: Apple Silicon arm64;
   - `macos-15-intel`: Intel x86_64.
4. Download artifacts from each completed job.

The workflow is provided but **has not been run against your repository**.
Private repositories may incur runner charges depending on your account.
Runner labels follow the published reference:
<https://docs.github.com/en/actions/reference/runners/github-hosted-runners>.

Expected generated artifacts:

```text
KADOMA-0.11.0-Windows-x64-Setup.exe
KADOMA-0.11.0-Windows-x64-standalone.exe
KADOMA-0.11.0-Windows-x64-portable.zip
KADOMA-0.11.0-macOS-arm64.dmg
KADOMA-0.11.0-macOS-x86_64.dmg
KADOMA-0.11.0-source.zip
SHA256SUMS.txt
BUILD_INFO.json
```

### Option B — build on your own machines

**Windows:** Install 64-bit Python and, for `Setup.exe`, **Inno Setup 6**. Then:

```bat
build-windows.cmd                       :: portable folder + ZIP (default)
python scripts/build.py --mode onefile   :: ONE self-contained KADOMA.exe
python scripts/build.py --mode both      :: both of the above, plus source + checksums
```

The default build produces a portable folder plus a ZIP. **Keep the complete
portable folder together**; the EXE inside it is not self-contained.

`--mode onefile` produces a **single `KADOMA.exe` with no sibling folder** —
copy that one file anywhere and run it. It unpacks itself to a temporary
directory on start-up, so the first launch takes a few seconds longer than the
portable build. `--mode both` writes every artifact, `SHA256SUMS.txt` and
`BUILD_INFO.json` into `release/`.

**Mac:** Run `bash build-macos.command` on each architecture. It generates a
native `.app` and `.dmg` for that machine. A Windows EXE does not run on macOS.
One Mac artifact does not imply that the other architecture was tested.

`python scripts/build.py` refuses unsupported cross-builds. The native build
script runs a packaged-engine smoke test inside each artifact it produces and
includes source and checksums. Interactive installer and desktop QA is still
required before release.

### Code signing and distribution

Windows installers are **not Authenticode-signed**. Mac bundles are **ad-hoc
signed, not Developer ID-signed or notarized**. SmartScreen / Gatekeeper may block
downloaded binaries. For production distribution obtain the appropriate signing
certificates, sign and notarize where needed, then test installation and upgrades
on real Windows/Intel Mac/Apple Silicon machines. This kit does not bypass OS
security checks or claim a trusted production installer.

## Optional offline engines

### LibreOffice

Install the standard desktop version. KADOMA detects:

- Windows: `C:\Program Files\LibreOffice\program\soffice.exe`
- Mac: `/Applications/LibreOffice.app/Contents/MacOS/soffice`
- PATH entries `soffice` / `libreoffice`

Set `PAPERDESK_LIBREOFFICE` if installed elsewhere. Each conversion uses a fresh,
private temporary profile with macro security set high, then deletes its temporary
files. **LibreOffice is an external application, not an OS-level sandbox.** Do
not use this initial app to process malicious documents. External-reference
behavior and complex layouts need review.

### Tesseract OCR

Install Tesseract plus the languages you need. On macOS with Homebrew:

```bash
brew install tesseract tesseract-lang
```

On Windows, install a trusted Tesseract build, typically in
`C:\Program Files\Tesseract-OCR`, or set `PAPERDESK_TESSERACT` to the executable.
The app also checks PATH and common Homebrew locations. For English use `eng`;
for Arabic install its language data and use `ara`; for both use `eng+ara`.
Restart the app after installing an engine. OCR is not translation, handwriting
recognition is not guaranteed, and exported financial data must be reconciled.

## Daily workflow

1. Open a PDF, image, Office document, or local HTML/text file.
2. **Edit:** click any text on the page and type directly over it. Enter applies,
   Esc cancels; clearing the box deletes the line. The side panel offers the same
   edit with exact size, colour, and family controls, plus Delete this text.
3. **Add text:** drag a box, enter text, Add text. **Image/Sign:** choose or create
   an image first, then drag its placement area.
4. **Pages:** select pages for toolbar actions; drag previews to reorder. Use the
   plus button for a blank page or additional files.
5. **Forms:** draw new field areas or fill the current page's existing fields.
6. **Protect:** export an encrypted copy; use Redact for actual content removal.
7. **Convert/OCR:** choose a range and check the stated output limitations.
8. **Share:** press **Share** to write a copy into the share folder, then attach it
   to an email, copy the file, or show it in its folder. (Desktop app only.)
9. **Save:** **Save** writes over the file you opened; **Save as** puts the copy
   where you choose and the document follows it. **Export** always writes a new
   file in another format and leaves the document where it is.
10. **Make it your PDF app:** press the default-app button in the toolbar, register
    KADOMA, then confirm it in the Settings page that opens. After that,
    double-clicking any PDF opens it here.

Keyboard shortcuts: Ctrl/⌘ O open, **S save**, **Shift S save as**, F search,
Z undo, Shift Z redo. V select, E edit, T text, H highlight, C comment, R redact.
Use Page Up/Down for navigation. The Guide button documents the limits in-app.

## Security and limits

- This is an initial application, **not independently security audited**.
- Working files: 500 MB; 500 pages. Merge: unlimited files / 500 MB combined.
- OCR: at most 20 pages per run. Image/split export: at most 80 pages per run.
- Export size: 240 MB. Large renders are capped to avoid oversized image buffers.
- Undo is bounded and is **not a secure memory wipe**. The operating system may
  swap process memory to disk. Closing/switching clears application references,
  not all traces on a computer.
- Redaction applies to the selected area; information outside it may remain.
  The original file, external backups, and previous exports are not redacted.
  Always reopen and inspect the exported redacted PDF before sharing it.
- PDF permission flags depend on reader enforcement. Encryption, strong passwords,
  and real redaction address different threats.
- Existing certificate signatures may be invalidated by any PDF modification.
  Do not use this build to validate signed legal agreements.
- HTTP upload transport may temporarily spool large files to the OS temporary
  directory. Office conversion and OCR also use temporary files. Normal completion
  closes/removes them; this is not secure disk erasure or a RAM-only guarantee.
- **Save writes over the file you opened.** That is what Save means, and it is
  the one operation in this application that changes an existing file. Save as
  writes elsewhere and leaves the original alone. A file that changed on disk
  since it was opened is refused rather than overwritten, but a file that has
  not changed is replaced without a second confirmation — use Save as if you
  want to keep the original.
- No automatic recovery of unsaved changes. Save or export before closing; the
  native window requests confirmation before exit.

## Testing

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python desktop.py --self-test
```

The packaged self-test exercises 15 checks, including Arabic write/read-back/
search and the share folder plus `.eml` attachment, so a built EXE proves those
features on the machine it runs on.

Optional engine tests skip if LibreOffice / Tesseract are not installed. They were
also exercised in the Linux development environment. Native package creation,
GUI launch, architecture compatibility and signing are separate acceptance tests.
See `QA_REPORT.md` for the actual results and outstanding checks.

Browser workflow checks use the separately installed Playwright tool:

```bash
python -m pip install playwright
python -m playwright install chromium
# With the development server already running:
python scripts/check_ui.py --base-url http://127.0.0.1:8000
python scripts/check_direct_edit.py --base-url http://127.0.0.1:8000
python scripts/check_share.py --base-url http://127.0.0.1:8000

# Saving writes to a real file, so it needs a server in desktop mode:
python run_preview.py --port 8020 --qa-desktop
python scripts/check_save.py --base-url http://127.0.0.1:8020
```

`check_direct_edit.py` drives the in-place editor in a real browser and reopens
each exported PDF with PyMuPDF, so the direct-edit claims are checked against
actual document content rather than screenshots.

`check_save.py` is the only check that can prove saving rather than describe it:
it opens a PDF by path, edits it through the interface, presses **Save**, and
compares the file on disk before and after — then presses **Save as**, confirms
the document follows the copy, changes the file behind the app's back and
confirms the overwrite is refused. The two native dialogs are the only thing
stood in for; the request, the engine's write and the file that appears are real.

`check_share.py` covers the sharing panel, the default-app panel and Arabic
editing. Sharing and registration only run inside the desktop shell, so rather
than weakening the app to make it testable, the check stands in for the shell
from the **test** side: it rewrites the health response and stubs those
endpoints, which still exercises the real dialogs, request payloads and error
handling. It asserts that the requests carry the prepared path, recipient,
subject and attachment flag, and that Arabic added through the interface reads
back as logical letters with the editor switched to right-to-left.

The Windows registry round-trip in `tests/test_share.py` is skipped by default
because it writes to the real `HKCU` hive. Run it deliberately with:

```bash
PAPERDESK_TEST_REGISTRY=1 python -m pytest tests/test_share.py -k round_trip
```

A built executable can be launch-checked as a user would run it:

```bash
python scripts/check_exe.py release/KADOMA-0.11.0-Windows-x64-standalone.exe
python scripts/verify_sums.py release/SHA256SUMS.txt
```

`check_exe.py` starts the EXE, waits for its loopback service, confirms the token
gate refuses an unauthenticated request, fetches the bundled interface, and
reports the native window title read straight from the Win32 API.

### The dead-button audit

```bash
python scripts/check_controls.py
# or, against a server you already have running:
python scripts/check_controls.py --base-url http://127.0.0.1:8000
```

`check_controls.py` answers one question: **is every control in the interface
actually wired to something?** It runs two passes.

The **static pass** reads every `id` in `index.html` and every control the
interface renders from JavaScript, and fails if any of them is not referenced by
a handler or by a delegated `data-*` attribute. That catches a button that was
added to the markup and never connected.

The **live pass** starts the application with desktop capabilities and drives
every control in a real Chromium, requiring an observable result from each one —
not merely that the click was accepted. It also fails on an uncaught JavaScript
error, on any 5xx from the engine, and on any request leaving the machine.

Two details in it are worth knowing, because both made earlier versions of the
audit **lie**:

- It reads saved form values back **from the engine**, not from the panel. The
  panel keeps what was typed, so a panel-based check passes even when the save
  was refused. That is not hypothetical: an earlier version of the audit typed a
  sentence into a date field, the engine correctly refused it, and the check
  reported a pass. The audit now also tests that refusal deliberately.
- It types with real keystrokes rather than filling the input directly. Filling
  proved unreliable on these inputs — it can leave focus behind and store
  nothing while still reporting success.

It also builds the files it needs instead of relying on another script having run
first, so it works on a clean checkout.

Results are written to `qa/controls-results.json`. The print step really prints:
the job is redirected to a file by the printer driver, so the real engine, the
real rendering, the real GDI calls and the real spooler are all exercised, and
the resulting document is then inspected. Nothing in the shipped application
knows the audit exists.

#### One dialog element, and why closing it is not as simple as it looks

The whole application shares a single `<dialog>`. Closing an already-open dialog
**queues** its `close` event rather than delivering it immediately, so the event
arrives *after* the next dialog is already on screen — where it is
indistinguishable from that dialog being dismissed. A confirmation could
therefore answer itself the moment it appeared, which is exactly what the audit
caught when the merge window asked about unsaved edits. `openModal` now tells the
outgoing dialog directly that it has been replaced, and a `close` is only
believed when the dialog is genuinely shut. Anything that needs to run when a
dialog is dismissed registers with `onModalDismiss` rather than listening for
`close` itself.

## Architecture

```text
app/engine.py           Real PDF/Office/OCR operations and in-memory history
app/rtl.py              Arabic/right-to-left shaping, read-back and font choice
app/printing.py         Print resolution rendering and direct printing (GDI/CUPS)
app/share.py            Share folder, clipboard file copy, mailto and .eml drafts
app/shell_integration.py  Per-user PDF handler registration and status
app/server.py           Same-origin local API; desktop authentication middleware
app/demo.py             Original editable 4-page sample report
app/static/             Offline HTML/CSS/JS interface and licensed local fonts
desktop.py              Native pywebview shell, Save dialog, single-instance handoff
kadoma.spec          PyInstaller native bundling recipe (folder or one-file)
scripts/build.py        Native artifacts, smoke tests, source ZIP, checksums
scripts/check_ui.py     Browser workflow verification (Playwright)
scripts/check_direct_edit.py  In-place text editing verification (Playwright)
scripts/check_share.py  Sharing, default-app and Arabic interface verification
scripts/check_controls.py  Dead-button audit: static wiring plus a live pass
scripts/check_exe.py    Launches a built EXE and verifies service, gate, window
scripts/verify_sums.py  Re-hashes release files against SHA256SUMS.txt
.github/workflows/      Three native build jobs
scripts/windows.iss     Per-user Windows installer recipe
tests/                  Engine/API/printing verification
```

All MuPDF access is serialized, including rendering, to avoid unsafe concurrent
library access. Mutations are made on a temporary document and committed only
when a complete, valid PDF has been serialized.

Direct editing groups the text of a page into **runs**: consecutive spans on one
line stay together so a click edits a whole sentence, while wide horizontal gaps
(a table column, a right-aligned label) split them so replacing one never
swallows an unrelated cell. The same run geometry is used before the edit to
measure how far a replacement may grow, which is why a longer line keeps its
font size instead of shrinking into the original selection box.

Combining files has one implementation — `Engine._add_sources` — shared by
"append to this document" and "build a new one". A page range, a password and an
assembly permission therefore cannot behave differently depending on which
destination was chosen. Pages are copied in **runs of consecutive pages** rather
than one at a time, so combining a 200-page source is one copy operation, and the
order typed is preserved rather than sorted.

### Why Arabic needed its own module

Three separate problems have to be solved, and they are easy to confuse:

1. **Shaping.** Arabic letters change shape with their neighbours and run right
   to left. MuPDF does this correctly *only* through its HTML/Story layout path.
   The direct text-writing path emits glyphs one at a time in the order given,
   which produces disconnected letters in the wrong order — so right-to-left
   text must never take that path. Verified, not assumed.
2. **Reading it back.** After shaping, the document stores *presentation forms*
   rather than the letters typed. Text read out of the document is normalised
   back, but only when presentation forms are actually present, so an unrelated
   ligature such as `ﬁ` is never silently rewritten.
3. **Finding it.** For the same reason, a plain search for the typed Arabic word
   returns **nothing**. Searching normalises both sides and matches word windows,
   and folds Arabic-Indic and Persian digits and no-break spaces together.

Font choice is measured at runtime rather than hard-coded, because a font that
renders beautifully but reads back as garbage is worse than no font at all — the
damage only appears the next time the user edits that line.

## License

Original code: **GNU AGPL-3.0-or-later**. Read `LICENSE` and
`THIRD_PARTY_NOTICES.md`, especially the PyMuPDF/MuPDF licensing conditions, before
commercial or closed-source distribution. The local Inter font is SIL OFL.
