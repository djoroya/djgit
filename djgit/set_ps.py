import os
import argparse


def get_ps1(style: str) -> str:
    """Returns the PS1 string according to the chosen style."""
    styles = {
        "minimal": r'export PS1="(\u) \W\$ "',
        "classic": r'export PS1="(\u@\h) \w\$ "',
        "colorful": r'export PS1="(\[\033[01;33m\]${CONDA_DEFAULT_ENV}\[\033[0m\]) '
                    r'\[\033[01;32m\]\u\[\033[0m\]:\[\033[01;34m\]\W\[\033[0m\]\$ "',
    }
    if style not in styles:
        raise ValueError(f"Invalid style: {style}. Use {list(styles.keys())}")
    return styles[style]


def write_bashrc(ps1_line: str):
    """Modifies ~/.bashrc to apply the new PS1."""
    home = os.path.expanduser("~")
    bashrc = os.path.join(home, ".bashrc")

    # Read current content
    if os.path.exists(bashrc):
        with open(bashrc, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Filter previous PS1
    lines = [line for line in lines if not line.strip().startswith("export PS1=")]

    # Add new configuration
    lines.append("\n# >>> Custom PS1 config <<<\n")
    lines.append(ps1_line + "\n")
    lines.append("# <<< Custom PS1 config >>>\n")

    with open(bashrc, "w") as f:
        f.writelines(lines)

    print(f"✅ PS1 updated in {bashrc}")
    print("ℹ️  Run: source ~/.bashrc to apply the changes now.")


def main():
    parser = argparse.ArgumentParser(description="Configure PS1 in Bash with different styles.")
    parser.add_argument("--style", type=str, default="colorful",
                        help="PS1 style: minimal, classic, colorful")
    parser.add_argument("--apply", action="store_true",
                        help="If specified, writes the configuration to ~/.bashrc")
    args = parser.parse_args()

    ps1_line = get_ps1(args.style)

    if args.apply:
        write_bashrc(ps1_line)
    else:
        print(ps1_line)


if __name__ == "__main__":
    main()
