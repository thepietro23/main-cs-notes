"""Build a module .md -> A4 .docx and run the QC checklist.
Usage:  python build.py M02_Python_Object_Model
Run from the Notes/ directory (parent of _source_markdown).
"""
import sys, os, re, zipfile, subprocess

def build(stem):
    src = f"_source_markdown/{stem}.md"
    out = f"{stem}.docx"
    r = subprocess.run([
        "pandoc", src, "-o", out,
        "--reference-doc=_source_markdown/reference.docx",
        "--resource-path=.;_source_markdown",
        "--toc", "--toc-depth=2",
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print("PANDOC FAILED:\n", r.stderr); return False
    z = zipfile.ZipFile(out)
    doc = z.read("word/document.xml").decode("utf-8", "ignore")
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    md = open(src, encoding="utf-8").read()
    refs = set(re.findall(r"images/([\w.]+\.png)", md))
    leaks = [t for t in ["\\frac", "\\times", "\\approx", "\\sum", "\\text{", "\\begin"] if t in doc]
    a4 = 'w:w="11906"' in doc
    marg = 'w:left="1440"' in doc
    ok = (len(media) == len(refs)) and a4 and marg and not leaks
    print(f"{stem}: img {len(media)}/{len(refs)} "
          f"{'OK' if len(media)==len(refs) else 'MISMATCH'} | "
          f"A4 {a4} | margins {marg} | leaks {leaks or 'none'} | "
          f"lines {md.count(chr(10))+1} | {round(os.path.getsize(out)/1024)}KB "
          f"| {'PASS' if ok else 'CHECK'}")
    return ok

if __name__ == "__main__":
    for stem in sys.argv[1:]:
        build(stem)
