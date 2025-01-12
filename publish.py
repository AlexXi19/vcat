#!/usr/bin/env python3

import os
import subprocess
import sys


def main():
    # Ensure we have twine installed
    try:
        import twine  # noqa
    except ImportError:
        print("Twine is not installed. Please run: pip install twine")
        sys.exit(1)

    # Get the token from environment variables
    username = "__token__"
    password = os.environ.get("PYPI_TOKEN")

    if not password:
        print("Error: PYPI_TOKEN environment variable not found.")
        print("Please set PYPI_TOKEN before publishing.")
        sys.exit(1)

    # 1. Build the package
    # This will create the `dist/` folder with .tar.gz and .whl files
    print("Building the distribution...")
    subprocess.run([sys.executable, "setup.py",
                   "sdist", "bdist_wheel"], check=True)

    # 2. Upload using twine
    print("Uploading to PyPI...")
    result = subprocess.run(
        [
            "twine",
            "upload",
            "dist/*",
            "-u", username,
            "-p", password
        ],
        check=False
    )

    if result.returncode == 0:
        print("\n✅ Successfully published to PyPI.")
    else:
        print("\n❌ Publishing failed.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
