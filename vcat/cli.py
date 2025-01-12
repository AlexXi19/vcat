import re
import argparse
from openai import OpenAI
import os
import subprocess
import hashlib
import time
import sys
import threading
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(
    api_key=OPENAI_API_KEY,
)


class Logger:
    """Custom logger to format and display logs with timestamps."""
    @staticmethod
    def log(message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"
        if os.getenv("VERBOSE"):
            print(formatted_message)

    @staticmethod
    def success(message):
        Logger.log(message, level="SUCCESS")

    @staticmethod
    def error(message):
        Logger.log(message, level="ERROR")

    @staticmethod
    def warning(message):
        Logger.log(message, level="WARNING")


def read_file(file_path, max_chars=32000, max_lines=None):
    """Read lines from a file until the max character count or line count is reached."""
    lines = []
    total_chars = 0
    line_count = 0

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            line_length = len(line)

            if total_chars + line_length > max_chars or (max_lines is not None and line_count >= max_lines):
                break

            lines.append(line)
            total_chars += line_length
            line_count += 1

    return lines


def extract_python_code(generation: str):
    """Extract Python code from a response by looking for code blocks."""
    generation = generation.replace(
        "[PYTHON]", '```python').replace("[/PYTHON]", '```')
    if '```python' in generation:
        p_code = re.compile(r'```python\n(.*?)\n```', flags=re.DOTALL)
        code_block = p_code.findall(generation)[0]
        return code_block
    else:
        # Fallback for code that's not clearly in triple-backticks
        codelist = re.split(r"\ndef|\nclass|\nif|\n#|\nprint", generation)
        return codelist[0]


def generate_python_visualization_code(file_path, file_content, target_path, large_file=False,
                                       previous_code=None, error_message=None):
    """
    Generate Python code that processes raw data into an HTML visualization.
    If large_file is True, we add an extra instruction to handle pagination or chunk-based approach.
    """
    file_type = os.path.splitext(file_path)[1][1:]
    base_prompt = f"""
        The following is a snippet of a {file_type} file:
        {file_content},
        with the location of the file: {file_path}.

        Please write a Python script that reads the data from the {file_type} file and
        generates a human-readable HTML file to visualize it.

        Generate the code to {target_path}. Please only use the python standard library,
        do not use any extra libraries! Bonus points if you make it look good!
    """

    # If the file is large, add a prompt to handle pagination
    if large_file:
        base_prompt += (
            "\n\nThe file is quite large. Please ensure your solution uses pagination or "
            "other techniques so that the HTML does not freeze up the user's computer."
        )

    messages = [
        {"role": "developer", "content": "You are a helpful assistant to help generate code for the user to visualize files."},
        {"role": "user", "content": base_prompt}
    ]

    if previous_code:
        messages.append({"role": "assistant", "content": previous_code})
    if error_message:
        messages.append(
            {"role": "user", "content": f"The previous script failed with the following error:\n{error_message}"})

    Logger.log("Messages sent to LLM:\n" + str(messages))

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    response = completion.choices[0].message.content
    Logger.log("LLM Response:\n" + response)
    return response


def save_code_to_file(code, output_path):
    """Save generated code to a file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(code)
    Logger.success(f"Code saved to {output_path}")


def get_cache_path(file_content):
    """Get a unique cache path based on the content hash."""
    cache_home = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    content_hash = hashlib.md5(file_content.encode('utf-8')).hexdigest()
    return os.path.join(cache_home, "vcat", content_hash)


def get_html_cache_path(file_content):
    """Get the path for the generated HTML file based on the content hash in the cache directory."""
    cache_home = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    content_hash = hashlib.md5(file_content.encode('utf-8')).hexdigest()
    return os.path.join(cache_home, "vcat", f"{content_hash}.html")


def run_generated_code(python_script_path, output_html_path):
    """Run the generated Python code to produce the HTML output, suppressing stdout but capturing stderr."""
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.run(["python", python_script_path],
                           stdout=devnull, stderr=subprocess.PIPE, check=True)
        Logger.success(f"HTML file generated at {output_html_path}")
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode() if e.stderr else str(e)


def open_html_file(html_path):
    """Open the HTML file using the system's default application."""
    try:
        subprocess.run(["open", html_path], check=True)
    except Exception as e:
        Logger.error(f"Error opening HTML file: {e}")


def loading_animation(message, stop_event):
    """Display a loading animation."""
    spinner_frames = ["|", "/", "-", "\\"]
    while not stop_event.is_set():
        for frame in spinner_frames:
            if stop_event.is_set():
                break
            sys.stdout.write(f"\r{message} {frame} ")
            sys.stdout.flush()
            time.sleep(0.2)
    sys.stdout.write("\r")
    sys.stdout.flush()


def append_css_to_html(html_path):
    """Append a link to an external CSS file to the generated HTML file."""
    link_tag = '<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">\n'
    try:
        with open(html_path, 'r+') as f:
            content = f.read()
            if "<head>" in content:
                updated_content = content.replace(
                    "<head>", f"<head>\n{link_tag}")
            else:
                updated_content = f"{link_tag}{content}"
            f.seek(0)
            f.write(updated_content)
            f.truncate()
    except Exception as e:
        Logger.error(f"Error appending Tailwind CSS to HTML: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize a file using generated Python code."
    )
    parser.add_argument('file', help="Path to the input file")
    parser.add_argument('--chars', type=int, default=32000,
                        help="Maximum number of characters to read from the file")
    parser.add_argument('--lines', type=int, default=None,
                        help="Maximum number of lines to read from the file")

    args = parser.parse_args()

    args.file = os.path.abspath(args.file)

    file_size_bytes = os.path.getsize(args.file)
    file_size_mb = file_size_bytes / (1024 * 1024)
    LARGE_FILE_THRESHOLD_MB = 5
    is_large_file = file_size_mb > LARGE_FILE_THRESHOLD_MB

    Logger.log(f"File size: {file_size_mb:.2f} MB")
    if is_large_file:
        Logger.warning(
            "File size exceeds threshold - pagination or chunking will be requested.")

    try:
        Logger.log("Reading file...")
        file_content = read_file(args.file, args.chars, args.lines)
    except Exception as e:
        Logger.error(f"Error reading file: {e}")
        return

    try:
        file_content_str = "\n".join(file_content)
        cache_dir = get_cache_path(file_content_str)
        python_cache_path = f"{cache_dir}.py"
        html_cache_path = get_html_cache_path(file_content_str)

        os.makedirs(os.path.dirname(python_cache_path), exist_ok=True)

        retries = 3
        previous_code = None
        error_message = None
        success = False

        for attempt in range(retries):
            stop_event = threading.Event()
            animation_thread = threading.Thread(
                target=loading_animation, args=(
                    "Visualizing your file...", stop_event)
            )
            animation_thread.start()

            generated_response = generate_python_visualization_code(
                args.file,
                file_content_str,
                html_cache_path,
                large_file=is_large_file,
                previous_code=previous_code,
                error_message=error_message,
            )
            generated_code = extract_python_code(generated_response)
            save_code_to_file(generated_code, python_cache_path)

            success, error_message = run_generated_code(
                python_cache_path, html_cache_path
            )

            append_css_to_html(html_cache_path)

            stop_event.set()
            animation_thread.join()

            if success:
                Logger.success("Visualization successfully generated.")
                open_html_file(html_cache_path)
                break

            previous_code = generated_code

        if not success:
            Logger.error(
                "Failed to generate visualization after multiple attempts.")
        else:
            Logger.success("Process completed.")

    except Exception as e:
        Logger.error(f"Error generating or retrying code: {e}")


if __name__ == "__main__":
    main()
