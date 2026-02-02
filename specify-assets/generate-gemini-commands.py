#!/usr/bin/env python3
import os
import yaml
import re

SOURCE_DIR = ".agent/workflows"
DEST_DIR = ".gemini/commands"


def convert():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    print(f"Converting files from {SOURCE_DIR} to {DEST_DIR}...")

    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} does not exist.")
        return

    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".md")]
    if not files:
        print("No .md files found in source directory.")
        return

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by '---' to separate YAML frontmatter
            parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)

            description = ""
            handoffs = []
            prompt_body = content

            if len(parts) >= 3:
                # parts[0] is usually empty string before first ---
                frontmatter_raw = parts[1]
                prompt_body = parts[2].strip()

                try:
                    frontmatter = yaml.safe_load(frontmatter_raw)
                    if frontmatter:
                        description = frontmatter.get("description", "")
                        handoffs = frontmatter.get("handoffs", [])
                except yaml.YAMLError as ye:
                    print(f"Warning: Failed to parse YAML in {filename}: {ye}")

            # Append handoffs to prompt
            if handoffs:
                prompt_body += "\n\n## Recommended Handoffs\n"
                prompt_body += "After completing the task, verify if any of the following handoffs are appropriate:\n"
                for h in handoffs:
                    label = h.get("label", "Next Step")
                    agent = h.get("agent", "default")
                    h_prompt = h.get("prompt", "")
                    prompt_body += f"- **{label}** (Agent: `{agent}`): {h_prompt}\n"

            # TOML String Escaping Strategy for Basic Multiline Strings (""")
            # 1. Backslashes must be escaped first because they start escape sequences.
            #    We want literal backslashes from the markdown to stay literal.
            prompt_escaped = prompt_body.replace("\\", "\\\\")

            # 2. Triple double-quotes """ must be escaped to avoid ending the string prematurely.
            #    We replace them with \"""
            prompt_escaped = prompt_escaped.replace('"""', '"""')

            # Escape double quotes in description (for basic single-line string)
            desc_escaped = (
                description.replace("\\", "\\\\").replace('"', '"')
                if description
                else ""
            )

            toml_lines = []
            if desc_escaped:
                toml_lines.append(f'description = "{desc_escaped}"')

            toml_lines.append('prompt = """')
            toml_lines.append(prompt_escaped)
            toml_lines.append('"""')

            toml_content = "\n".join(toml_lines)

            dest_filename = filename.replace(".md", ".toml")
            dest_path = os.path.join(DEST_DIR, dest_filename)

            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(toml_content)

            print(f"✓ {filename} -> {dest_filename}")

        except Exception as e:
            print(f"✕ Failed to convert {filename}: {e}")


if __name__ == "__main__":
    convert()
