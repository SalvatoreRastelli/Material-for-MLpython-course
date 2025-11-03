import re
from pathlib import Path

def extract_glossary_terms(tex_text):
    """Extract glossary entries and their names.
    . - metacharacter;  matches anything except a newline character, and there’s an alternate mode (re.DOTALL) where it will match even a newline. 
    * - doesn’t match the literal character '*'; instead, it specifies that the previous character can be matched zero or more times, instead of exactly once.
    ? -  matches either once or zero times; you can think of it as marking something as being optional. For example, home-?brew matches either 'homebrew' or 'home-brew'.
    \s - metacharacter; Matches any whitespace character
    
    When ? follows a quantifier (*, +, {}):
    (.*) - greedy matching; "<tag>first</tag><tag>second</tag>" --> re.findall(r"<tag>(.*)</tag>", text) --> first</tag><tag>second
    (.*?) non greedy; --> ['first', 'second']
    """
    entries = re.findall(
        r'\\newglossaryentry\{(.*?)\}\s*\{.*?name=\{(.*?)\}',
        tex_text,
        re.DOTALL
    )
    print(entries)
    return {term.strip(): name.strip() for term, name in entries}

def main():
    input_file = Path("test.tex")
    tex_text = input_file.read_text(encoding="utf-8")

    # glossary = extract_glossary_terms(tex_text)

    text = r"""\newglossaryentry{pseudoinverse}
    {name={pseudoinverse},
    description={The \index{pseudoinverse}Moore–Penrose {pseudoinverse} formula},
    text={pseudoinverse}}"""

    pattern = r'\\newglossaryentry\{(.*?)\}\s*\{.*?name=\{(.*?)\}'
    match = re.search(pattern, text)

    print(match.group(1))  # first capturing group
    print(match.group(2))  # second capturing group

    # print(f"Found {len(glossary)} glossary terms.")

if __name__ == "__main__":
    main()