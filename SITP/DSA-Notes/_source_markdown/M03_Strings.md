---
title: "Module 3 — Strings"
subtitle: "DSA Mastery: Google / FAANG / GATE / ICPC — In-Depth Notes (with visuals)"
author: "Prepared for nidhi.sharma@forensiccybertech.com"
date: "2026"
---

# Module 3 — Strings

> **Why strings get their own module.**
> A string is just an **array of characters** — so everything from Module 2
> (two pointers, sliding window, prefix ideas) applies. But strings add their own
> superpowers: **hashing** (turn a substring into a number), and **smart pattern
> matching** (KMP, Z, Rabin-Karp) that avoid re-checking characters. These show
> up in search engines, editors, compilers, DNA analysis, and a huge share of
> interview questions.

This module is **P0–P1**: basics and hashing are must-know; KMP/Z/Boyer-Moore are
"know the idea + when to use" for interviews, and directly tested in GATE/CP.

> **How to read each technique.** We go **Brute force → Better → Optimal** with
> pseudocode + complexity, plus a memory hook to make it stick.

### Quick technique selector

![Flowchart: which string technique to use — trie, KMP/Z, rolling hash, or char-count hashmap.](images/35_fc_string_selector.png)

---

## 3.1 String Basics

### Definition

A **string** is a sequence of characters stored as an array. Each character is a
number under the hood (its **code point**): `'A'` = 65, `'a'` = 97, `'0'` = 48
(ASCII). Unicode/UTF-8 extends this to every language and emoji.

### Encodings (know the difference)

- **ASCII:** 1 byte, 128 characters (English letters, digits, symbols).
- **UTF-8:** variable length (1–4 bytes); the standard on the web. An emoji can
  be 4 bytes — so "length in characters" ≠ "length in bytes". (A classic bug.)

> **Memory hook:** `'a' - 'a' = 0`, `'b' - 'a' = 1` … so `c - 'a'` gives a
> letter's index 0–25. This one trick powers most "count letters" problems.

### Immutability & the StringBuilder trap

In **Java, Python, C#**, strings are **immutable** — you cannot change a
character in place; every "edit" makes a **new** string.

```text
# BAD: building a string with += in a loop      Time O(n^2)!
result = ""
for c in chars:
    result += c        # each += copies the whole string so far

# GOOD: use a list / StringBuilder, join once    Time O(n)
parts = []
for c in chars:
    parts.append(c)
result = "".join(parts)     # Java: StringBuilder; C++: string is mutable
```

> **Why O(n²)?** The `i`-th `+=` copies `i` characters, so total = 1+2+…+n =
> O(n²). This is the **most common hidden-cost bug** in interviews. Always
> mention it.

### Character frequency & anagrams (the bread-and-butter pattern)

Two strings are **anagrams** if they have the same letters with the same counts.

```text
# OPTIMAL: count characters                      Time O(n), Space O(1) (26 letters)
count = int[26]
for c in s: count[c - 'a'] += 1
for c in t: count[c - 'a'] -= 1
return all counts == 0
```

- A fixed-size `int[26]` (or a hashmap for Unicode) is the key idea.
- **Problems:** Valid Anagram (LC 242); Group Anagrams (LC 49 — sort each word or
  use the count as a key); Find All Anagrams in a String (LC 438 — sliding window
  of counts).

### Edge cases & common mistakes

- Building strings with `+=` in a loop (O(n²)).
- Assuming 1 char = 1 byte (false for UTF-8).
- Case sensitivity, spaces, punctuation in palindrome/anagram problems.
- Empty string and single character.

### MCQs

1. `s += c` inside a loop on an immutable string is? → **O(n²)**.
2. `c - 'a'` gives? → the letter's **0–25 index**.
3. Anagram check space with only lowercase letters? → **O(1)** (26 counts).

---

## 3.2 String Hashing (turn a substring into a number)

### Definition

**String hashing** maps a string to a number so that comparing two strings
becomes comparing two numbers (O(1) instead of O(length)). The standard is a
**polynomial rolling hash**:

```
hash(s) = (s[0]·b^(m-1) + s[1]·b^(m-2) + … + s[m-1]·b^0)  mod  M
```

where `b` is a base (e.g. 31 or 131) and `M` is a large prime modulus.

### Intuition

Think of the string as a **number written in base b**, just like `345` =
`3·100 + 4·10 + 5`. Two different strings *usually* get different numbers; the
`mod M` keeps the value from overflowing.

### Why a prime base and modulus?

- A **prime base** spreads values out and reduces accidental collisions.
- A **large prime modulus** keeps numbers in range and makes collisions rare.
- Using **two different mods** ("double hashing") makes collisions astronomically
  unlikely — a common CP trick.

### Prefix hashing → compare any substring in O(1)

Precompute prefix hashes once; then the hash of any substring `s[L..R]` is a
quick formula (like prefix sums, but with powers of `b`). This lets you compare
two substrings for equality in **O(1)**.

### Complexity

- Build prefix hashes: O(n)
- Compare any two substrings: O(1) (after precompute)

### When NOT to use / risks

- **Collisions:** two different strings sharing a hash. Mitigate with a big prime
  mod (and double hashing). For guaranteed-correct matching, prefer KMP/Z.
- Adversarial inputs (anti-hash tests in CP) — randomise the base.

### MCQs

1. Why a prime modulus in hashing? → fewer **collisions**, value stays in range.
2. Substring equality after prefix-hash precompute? → **O(1)**.

### Problems

- Longest Duplicate Substring (LC 1044 — binary search + hashing); Repeated DNA
  Sequences (LC 187); Distinct substrings count.

---

## 3.3 Pattern Matching — Naive (the baseline)

### Problem

Find all positions where a **pattern** `P` (length m) occurs in a **text** `T`
(length n).

### Naive method

Try every shift `0..n-m`; at each shift compare the pattern character by
character.

![Naive matching: slide the pattern by one each time and re-check it fully against the text.](images/30_naive_matching.png)

```text
# BRUTE FORCE / NAIVE                      Time O(n*m) worst, Space O(1)
for shift = 0 .. n-m:
    j = 0
    while j < m and T[shift+j] == P[j]: j += 1
    if j == m: report match at shift
```

- **Worst case O(n·m):** e.g. `T = "aaaaaa…"`, `P = "aaab"` — every shift compares
  almost the whole pattern before failing.
- **The waste:** when a mismatch happens, naive throws away everything it just
  learned and restarts. KMP, Z, and Boyer-Moore each fix this waste differently.

---

## 3.4 Rabin-Karp (hashing for matching)

### Idea

Instead of comparing the pattern to each window character by character, compare
their **hashes** first (O(1)). Only when hashes match do a real character check
(to rule out a collision). Use a **rolling hash** so each window's hash updates
in O(1).

![Rabin-Karp: keep a rolling hash of the text window; on a hash match, verify the actual characters.](images/31_rolling_hash.png)

```text
# Rabin-Karp                               Avg O(n+m), worst O(n*m), Space O(1)
hp = hash(P)
hw = hash(T[0..m-1])
for shift = 0 .. n-m:
    if hw == hp and T[shift..shift+m-1] == P:   # verify on hash hit
        report match
    if shift < n-m:
        hw = roll(hw, T[shift], T[shift+m])      # remove old char, add new char
```

- **Rolling update:** `new = (old − leaving·b^(m-1))·b + entering` (mod M).
- **Average O(n+m)**; worst O(n·m) only with many hash collisions (rare with a
  good mod).
- **Best for:** multiple-pattern search, plagiarism/duplicate detection, 2D
  pattern search.

> **Memory hook:** a moving train window — one car leaves the back, one enters
> the front; you don't recount all the cars.

### MCQs

1. Rabin-Karp average time? → **O(n+m)**.
2. Why verify characters after a hash match? → to rule out a **collision**.

---

## 3.5 KMP (Knuth–Morris–Pratt)

### The key insight

When a mismatch happens, we already know the characters that matched so far. KMP
uses that knowledge to **skip ahead without moving the text pointer backward**.
It precomputes an **LPS array** (Longest proper Prefix that is also a Suffix) for
the pattern.

![KMP LPS array: for each position, the length of the longest proper prefix that is also a suffix; mismatches jump using it.](images/32_kmp_lps.png)

### What LPS means

`LPS[i]` = length of the longest proper prefix of `P[0..i]` that is also a suffix
of `P[0..i]`. For `P = "ababaca"` → `LPS = [0,0,1,2,3,0,1]`.

It answers: *"if I fail after matching `j` characters, how many of them still form
a valid prefix I can reuse?"* — so I jump `j = LPS[j-1]` instead of restarting.

### Brute force → Optimal

```text
# BRUTE FORCE: naive matching             O(n*m)  (Section 3.3)

# OPTIMAL: KMP                             Build LPS O(m), search O(n) -> O(n+m)
build_lps(P):
    lps = int[m]; length = 0; i = 1
    while i < m:
        if P[i] == P[length]: length += 1; lps[i] = length; i += 1
        elif length > 0:      length = lps[length-1]        # fall back
        else:                 lps[i] = 0; i += 1

search(T, P):
    build lps; i = 0 (text); j = 0 (pattern)
    while i < n:
        if T[i] == P[j]: i += 1; j += 1
        if j == m: report match at i-m; j = lps[j-1]
        elif i < n and T[i] != P[j]:
            if j > 0: j = lps[j-1]      # jump using LPS, DON'T move i back
            else: i += 1
```

- **Why O(n+m):** the text pointer `i` only ever moves forward.
- **Memory hook:** LPS remembers "how much of my own start I've already matched",
  so after a mismatch I never recheck those characters.

### MCQs

1. What does KMP precompute? → the **LPS / prefix function**.
2. KMP time? → **O(n+m)**.
3. On mismatch at pattern index j (j>0), set j = ? → **LPS[j−1]**.

---

## 3.6 Z-Algorithm

### Idea

The **Z-array** of a string: `Z[i]` = length of the longest substring starting at
`i` that **matches the prefix** of the string. Build it in O(n) using a sliding
`[L,R]` window (the "Z-box").

![Z-array: each Z[i] is how far the substring from i matches the prefix; Z[3]=3 means 'aab' matches the prefix 'aab'.](images/33_z_array.png)

### How to match with it

To find pattern `P` in text `T`: build the Z-array of `P + '#' + T` (a separator
not in either). Any position where `Z[i] == m` (the pattern length) is a match.

```text
# Z-based matching                         O(n+m) time, O(n+m) space
S = P + '#' + T
compute Z array of S
for each i: if Z[i] == m: match in T at (i - m - 1)
```

- **KMP vs Z:** both O(n+m). Z is often **easier to code/remember**; KMP is more
  standard in textbooks. Pick whichever you recall under pressure.

### MCQs

1. `Z[i]` measures? → match length with the **prefix** starting at i.
2. Z-matching trick? → build Z of `P + '#' + T`, look for `Z[i] == m`.

---

## 3.7 Boyer-Moore (the fast one in practice)

### Idea

Compare the pattern to the window **right to left**, and on a mismatch **skip
ahead by a lot** using two heuristics:

- **Bad character rule:** align the mismatched text character with its last
  occurrence in the pattern (or skip past it entirely).
- **Good suffix rule:** reuse the suffix that already matched.

### Why it matters

Boyer-Moore can be **sub-linear** in practice (it often skips characters it never
even looks at) — which is why **`grep` and many editors use it**. Worst case is
still O(n·m), but the average is excellent, especially for long patterns over
large alphabets.

> **Interview takeaway:** you usually won't code full Boyer-Moore in an
> interview, but knowing *"right-to-left + skip on mismatch → used by grep"* is a
> great signal.

### MCQs

1. Boyer-Moore compares the pattern in which direction? → **right to left**.
2. Which real tool famously uses it? → **grep** (and many text editors).

---

## 3.8 Trie (Prefix Tree)

### Definition

A **trie** stores a set of strings as a tree where each **edge is a character**
and each **path from the root spells a prefix**. Words that share a prefix share
the same nodes. A flag marks the end of a complete word.

![Trie storing cat, car, card, dog: shared prefixes share nodes; green nodes mark the end of a word.](images/34_trie.png)

### Why it exists

A hashmap can check "is this exact word present?" But a trie also answers
**prefix** questions instantly: *"which words start with `ca`?"*, *"is `ca` a
prefix of any word?"* — perfect for **autocomplete and spell-check**.

### Operations & complexity

```text
insert(word):  walk/create a node per character;  mark last node as end
search(word):  walk per character; true if path exists AND last node is end
startsWith(p): walk per character; true if the whole path exists
```

| Operation | Time | Space |
|---|---|---|
| insert | O(L) | O(L·alphabet) per word worst case |
| search | O(L) | — |
| startsWith (prefix) | O(L) | — |

(`L` = word length. Time does **not** depend on how many words are stored.)

### Trie vs Hashmap (interview comparison)

| | Trie | Hashmap |
|---|---|---|
| Exact lookup | O(L) | O(L) average (to hash) |
| Prefix search | **O(L)** ✓ | not supported directly |
| Memory | more (many node pointers) | less |
| Ordering | sorted traversal possible | unordered |

> **Memory hook:** a trie is a **shared family tree of prefixes** — relatives
> (words) share ancestors (common starts).

### Production usage

Autocomplete (search bars, IDEs), spell-checkers, IP routing tables, dictionary
word games, and as a base for **Aho-Corasick** (multi-pattern search) and suffix
trees (Module 8/17).

### Common mistakes

- Forgetting the **end-of-word** flag → `search("ca")` wrongly true when only
  `"cat"` was inserted.
- Memory blow-up with 26-pointer arrays per node for sparse data → use a hashmap
  per node instead.

### MCQs

1. Trie search time for a word of length L? → **O(L)** (independent of word
   count).
2. Prefix query a hashmap can't do but a trie can? → **startsWith / autocomplete**.
3. What marks a complete word in a trie? → the **end-of-word flag**.

### Problems

- **Medium:** Implement Trie (LC 208); Replace Words (LC 648); Map Sum Pairs
  (LC 677); Design Add and Search Words (LC 211 — wildcard).
- **Hard:** Word Search II (LC 212 — trie + DFS on a grid); Stream of Characters
  (LC 1032).

---

## 3.9 Palindromes (a FAANG favourite)

A **palindrome** reads the same forwards and backwards (`"racecar"`). These are
asked constantly at Google/Meta/Amazon, so know the three levels.

### Check if a string is a palindrome — two pointers

```text
# OPTIMAL                                  Time O(n), Space O(1)
L = 0; R = n-1
while L < R:
    if s[L] != s[R]: return false
    L += 1; R -= 1
return true
```

(For "valid palindrome ignoring punctuation/case", skip non-alphanumerics and
lowercase as you go — LC 125.)

### Longest Palindromic Substring — expand around centre

**Intuition (memory hook — "grow from the middle"):** every palindrome has a
centre. There are `2n−1` centres (each character, and each gap between two
characters). From each centre, expand outwards while both sides match.

```text
# BRUTE FORCE: check every substring        Time O(n^3)
for each (i,j): check if s[i..j] is a palindrome  -> O(n^2) substrings * O(n) check

# OPTIMAL (interview standard): expand around centre   Time O(n^2), Space O(1)
best = ""
for centre in 0 .. n-1:
    expand(centre, centre)      # odd-length palindrome
    expand(centre, centre+1)    # even-length palindrome
# expand(L,R): while L>=0 and R<n and s[L]==s[R]: grow; update best

# ADVANCED: Manacher's algorithm              Time O(n)
# clever reuse of mirror info; rarely required to code, good to name-drop
```

- **Interview note:** "expand around centre" (O(n²)) is the expected answer;
  mentioning **Manacher's O(n)** as the optimal shows depth.
- **DP alternative:** `dp[i][j] = (s[i]==s[j]) and dp[i+1][j-1]` — O(n²) time and
  space (covered in Module 14).
- **Problems:** Longest Palindromic Substring (LC 5); Palindromic Substrings
  count (LC 647); Valid Palindrome (LC 125); Palindrome Partitioning (LC 131 —
  backtracking, Module 13).

### MCQs

1. How many centres does expand-around-centre check? → **2n−1** (odd + even).
2. Longest palindromic substring optimal time? → **O(n)** with Manacher (O(n²)
   expand-around-centre is the usual interview answer).

---

## Module 3 — Concept Review (one page)

- A string is a **char array**; `c - 'a'` → 0–25 index; UTF-8 length ≠ byte
  length.
- Immutable strings: building with `+=` in a loop is **O(n²)** → use a
  list/StringBuilder + join.
- **Anagram/frequency** → `int[26]` count, O(n)/O(1).
- **Polynomial rolling hash** → substring as a number; prefix hashing → O(1)
  substring compare; beware collisions.
- **Naive matching** O(n·m) wastes matched info. The fixes:
  - **Rabin-Karp** → rolling hash, avg O(n+m); great for multi-pattern.
  - **KMP** → LPS array, O(n+m); text pointer never goes back.
  - **Z-algorithm** → Z-array, O(n+m); often easiest to code.
  - **Boyer-Moore** → right-to-left + skip; sub-linear in practice (grep).
- **Trie** → tree of shared prefixes; insert/search/prefix all O(L); powers
  autocomplete.
- **Palindromes** → check with two pointers O(n); longest = expand around centre
  O(n²) (Manacher O(n)); 2n−1 centres.

## Module 3 — Flash Cards

- Q: `+=` in a loop on a string? **A: O(n²); use join/StringBuilder.**
- Q: Anagram check space (lowercase)? **A: O(1), int[26].**
- Q: What does KMP precompute? **A: LPS (prefix function).**
- Q: KMP / Z / Rabin-Karp time? **A: O(n+m).**
- Q: Rabin-Karp risk? **A: hash collisions → verify on match.**
- Q: Which matcher does grep use? **A: Boyer-Moore (right-to-left skip).**
- Q: Trie search time? **A: O(L), independent of #words.**
- Q: Prefix query structure? **A: trie (hashmap can't do prefixes).**

## Module 3 — Pattern Recognition

- "Count letters / anagrams / permutations of letters" → **int[26] / hashmap**.
- "Find a pattern in a text once" → **KMP or Z** (O(n+m)).
- "Compare many substrings / detect duplicates" → **rolling hash**.
- "Autocomplete / prefix / many words" → **Trie**.
- "Search many patterns at once" → **Rabin-Karp / Aho-Corasick**.
- "Longest/shortest substring with a condition" → **sliding window** (Module 2).
- "Palindrome / longest palindrome" → **two pointers / expand around centre**.

## Module 3 — Interview Questions (with follow-ups)

1. *Check if two strings are anagrams.* FU: *Unicode? streaming?*
2. *Find a substring in a string.* FU: *do it in O(n+m)* → KMP/Z; *explain LPS.*
3. *Design autocomplete.* FU: *rank suggestions; memory at scale* → trie (+heap).
4. *Detect a duplicate substring of length k.* FU: *rolling hash; collisions?*
5. *Why is `s += c` in a loop slow?* FU: *fix it* → join/StringBuilder.

## Module 3 — GATE / SEBI / RBI / ISRO Perspective

- **GATE favourites:** computing the **KMP LPS/failure function** by hand,
  tracing **naive vs KMP** comparisons, and **trie** structure questions.
- **Complexity:** know naive O(nm) vs KMP/Z/Rabin-Karp O(n+m) cold.
- **SEBI/RBI IT:** conceptual MCQs on pattern matching and tries.

---

*End of Module 3. Next: Module 4 — Linked Lists (singly/doubly/circular, fast &
slow pointers, cycle detection, reversal, LRU cache) — with visuals.*
