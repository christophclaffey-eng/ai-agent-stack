import re
import sys
from typing import Iterable


SKIP_PATTERN = re.compile(r"\b(pip install|git pull)\b")


def sanitize_lines(lines: Iterable[str]) -> list[str]:
    sanitized: list[str] = []
    for line in lines:
        if SKIP_PATTERN.search(line):
            print(f"[SKIPPED] {line.rstrip()}", file=sys.stderr)
            continue
        sanitized.append(line.rstrip("\n"))
    return sanitized


def sanitize_script(input_code: str) -> str:
    return "\n".join(sanitize_lines(input_code.splitlines()))


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python ScriptSanitizer.py <input_script.py>")
        return

    input_file = sys.argv[1]
    try:
        with open(input_file, "r", encoding="utf-8") as handle:
            input_code = handle.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return

    sanitized_code = sanitize_script(input_code)

    output_file = input_file.replace(".py", "_sanitized.py")
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write(sanitized_code)
    print(f"Sanitized script saved to: {output_file}")


if __name__ == "__main__":
    main()
