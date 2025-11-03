import re
from pathlib import Path

# helper to test whether index is inside any (start,end) list
def inside_any(index, spans):
    return any(s <= index < e for s, e in spans)

def extract_glossary_terms(tex_text):
    """Extract glossary entries and their names."""
    entries = re.findall(
        r'\\newglossaryentry\{(.*?)\}\s*\{.*?name=\{(.*?)\}',
        tex_text,
        re.DOTALL
    )
    return {term.strip(): name.strip() for term, name in entries}

import re

def replace_terms_with_gls(tex_text, glossary):
    """
    Replace plain term occurrences with \\gls{<term>} except:
      - inside existing \\gls{...} commands (never replace),
      - inside the glossary definition of the same term (do not replace occurrences of 'term' inside its own definition),
      - but allow replacing the term when it appears inside OTHER glossary definitions.
    Returns updated_text, changes (list of (name, start_index) for replacements).
    """

    updated_text = tex_text
    changes = []

    # 1) Find spans of every \newglossaryentry{key}{...} and record by key
    glossary_defs = {}   # key -> (start, end)
    for m in re.finditer(r'\\newglossaryentry\{(.*?)\}\s*\{.*?\}(?=\s*\\newglossaryentry|$)', tex_text, re.DOTALL):
        print(m)
        key = m.group(1)
        glossary_defs[key] = (m.start(), m.end())

    # 2) Find spans of existing \gls{...} (never replace inside these)
    gls_spans = [ (m.start(), m.end()) for m in re.finditer(r'\\gls\{.*?\}', tex_text) ]

    # 3) Collect candidate replacements from the ORIGINAL text (not updated_text)
    #    This avoids index-shift problems when applying multiple replacements.
    replacements = []  # list of (start, end, replacement_text, name)

    for term, name in glossary.items():
        # compile pattern for whole-word, case-insensitive matching of the displayed name
        # re.escape(name) - Escapes any special regex characters inside `name`.
        # For example, if name = "C++", it becomes "C\+\+"
        # so '+' is treated literally, not as a regex operator.
        pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)

        for m in pattern.finditer(tex_text):
            start, end = m.start(), m.end()

            # If inside any \gls{...}, skip
            if inside_any(start, gls_spans):
                continue

            # If inside this term's own glossary definition, skip
            # Glossary keys (term) should match the key used in \newglossaryentry{<key>}
            # Only protect if this key exists in glossary_defs
            def_span = glossary_defs.get(term)
            if def_span and def_span[0] <= start < def_span[1]:
                # match is inside its own definition -> skip replacing
                continue

            # Otherwise, this occurrence is OK to replace
            replacement_text = f'\\gls{{{term}}}'
            replacements.append((start, end, replacement_text, name))

    # 4) Sort replacements by start index descending, apply them to updated_text
    #    Applying from right to left prevents earlier replacements from shifting later spans.
    replacements.sort(key=lambda x: x[0], reverse=True)

    occupied = set()  # optional: track replaced positions to avoid overlapping replacements
    for start, end, repl, name in replacements:
        # Avoid overlapping replacements: if any position already replaced, skip this one
        # (This is a defensive measure — with whole-word patterns overlaps are unlikely.)
        if any(i in occupied for i in range(start, end)):
            continue

        updated_text = updated_text[:start] + repl + updated_text[end:]
        # mark occupied indices (relative to the original coordinates)
        # Note: indices in 'occupied' refer to original positions; because we apply right→left, they remain valid.
        for i in range(start, end):
            occupied.add(i)
        changes.append((name, start))

    # We returned changes in the order we applied (right->left). If you prefer chronological order,
    # you can sort changes by the index ascending here.
    changes.sort(key=lambda x: x[1])
    return updated_text, changes

def main():
    input_file = Path("test.tex")
    output_file = Path("out.tex")

    tex_text = input_file.read_text(encoding="utf-8")

    glossary = extract_glossary_terms(tex_text)
    print(f"Found {len(glossary)} glossary terms.")

    updated_text, changes = replace_terms_with_gls(tex_text, glossary)

    print(f"Applied {len(changes)} replacements.")
    for name, pos in changes[:10]:  # show sample
        print(f"  - {name} at position {pos}")

    output_file.write_text(updated_text, encoding="utf-8")
    print(f"Updated file written to {output_file}")

if __name__ == "__main__":
    main()
