

def load_rules(path: str) -> dict:
    rules = {}
    current = None

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                rules[current] = []
            else:
                rules[current].append(line.lower())

    return rules