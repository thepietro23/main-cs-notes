# 📚 CS Notes — Interview & Exam Prep

A personal, print-ready knowledge base covering the core Computer Science subjects — Data Structures & Algorithms, DBMS, Operating Systems, OOP, Computer Networks, and ML System Design. Each topic ships as detailed notes (`.docx`), their editable Markdown source, and hand-made diagrams.

> Built for deep revision, FAANG-style interviews, and university exams.

---

## 🗂️ Contents

| Area | What's inside |
|------|---------------|
| **[ML_System_Design/](ML_System_Design/)** | 23 modules (M01–M23): foundations → data → features → training → serving → MLOps → monitoring → scaling → RecSys, Search, CV, NLP, LLMs → case studies → interview mastery |
| **[SITP/DSA-Notes/](SITP/DSA-Notes/)** | 26 modules: fundamentals, arrays, strings, linked lists, stacks/queues, trees, heaps, graphs, greedy, D&C, backtracking, DP, bit manipulation, advanced DS, competitive & FAANG prep |
| **[SITP/OOPs/](SITP/OOPs/)** | 21 modules: object model, classes, encapsulation, inheritance, polymorphism, dunder methods, descriptors, metaclasses, typing, SOLID, design patterns, UML/LLD |
| **[SITP/OS/](SITP/OS/)** | 12 modules: processes, threads, CPU scheduling, synchronization, deadlocks, memory management, virtual memory, file systems, disk management |
| **[SITP/DBMS/](SITP/DBMS/)** | 11 modules: ER/EER modeling, relational algebra, SQL, normalization, storage, indexing, query optimization, transactions, recovery, distributed/NoSQL |
| **[SITP/CN/](SITP/CN/)** | Computer Networks: layered models through backend, cloud/SDN, and AI/data-center networking |
| **[CodeDebug-DSA/](CodeDebug-DSA/)** | Hands-on Jupyter notebooks — Arrays, Linked Lists, Bit Manipulation (code + debugging practice) |
| **[SITP/PYQs/](SITP/PYQs/)** | Previous-year questions with insights and an index |
| **[mysql/](mysql/)** | MySQL quick reference / setup notes |

---

## 📄 How the notes are organized

Most subjects follow the same layout:

```
<Subject>/
├── Notes/                     # Final rendered .docx notes (read these)
│   ├── M01_*.docx
│   ├── ...
│   ├── _source_markdown/      # Editable Markdown source + generator scripts
│   │   ├── M01_*.md
│   │   └── gen_*.py
│   └── images/                # Diagrams referenced by the notes
```

- **`.docx`** — the polished, print-ready output.
- **`_source_markdown/*.md`** — the source of truth; edit here.
- **`gen_*.py` / `viz_style.py`** — scripts that generate diagrams and build the docs.
- **`images/`** — all figures (761+ diagrams across the repo).

---

## 📊 At a glance

- **128** rendered `.docx` note documents
- **129** Markdown source files
- **761** diagram images
- **14** Jupyter notebooks for coding practice
- **6** core subjects fully covered

---

## 🚀 Usage

- **Just reading?** Open the `.docx` files in any subject's `Notes/` folder.
- **Editing / rebuilding?** Edit the Markdown in `_source_markdown/`, then run the relevant `gen_*.py` / build script to regenerate diagrams and documents (requires Python + `python-docx`, `matplotlib`).

---

## 📌 Notes

- This is a personal study repository — content is curated for revision and interview prep.
- Diagrams are generated programmatically for a consistent visual style.

---

*Maintained by [@thepietro23](https://github.com/thepietro23).*
