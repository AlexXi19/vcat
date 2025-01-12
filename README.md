## vcat

### Overview
**vcat** is a command-line (CLI) tool that generates human-friendly visualizations from any file’s contents. By leveraging OpenAI’s API to dynamically generate a specialized Python script, **vcat** transforms raw data into an HTML file. This makes it easy to explore and analyze your data right in your browser. Large files are automatically handled via pagination or chunking so that your system remains responsive.

### Key Features
- **Automatic Visualization**: Provide a file, and **vcat** writes a custom Python script on the fly to produce an HTML-based visualization.
- **Large File Handling**: For files exceeding a configurable threshold, **vcat** can break down the content into chunks so the final visualization is still efficient.
- **Simple CLI**: An intuitive command-line interface (`vcat path/to/file.txt`) that does all the heavy lifting for you.
- **Custom Styling**: Automatically injects Tailwind CSS into the generated HTML for a modern look and feel.
- **OpenAI Integration**: Uses OpenAI’s generative capabilities to produce and refine the visualization code.  
- **Cross-Platform**: Works on macOS, Linux, and Windows (Python 3.7+).

### How It Works
1. **File Reading**: **vcat** reads the first *N* characters or *M* lines (configurable) of the file.  
2. **Code Generation**: It sends the file snippet to the OpenAI API with instructions on how to create an HTML visualization.  
3. **Local Python Script**: The generated code is saved locally, then executed to produce an HTML file.  
4. **Styling**: Tailwind CSS is appended to give a cleaner layout.  
5. **View Results**: **vcat** attempts to automatically open the newly created HTML file in your default browser.

### Installation
1. **Prerequisites**:  
   - Python 3.7+  
   - An OpenAI API key (`OPENAI_API_KEY` must be set as an environment variable)  
2. **Install with pip** (once you’ve published to PyPI):  
   ```bash
   pip install vcat
   ```

### Usage
```bash
# Basic usage
vcat path/to/data.csv

# Reading only 100 lines
vcat path/to/data.csv --lines 100

# Reading only 5000 characters
vcat path/to/data.csv --chars 5000
```

- After running, **vcat** will create and open an HTML file that visualizes your data.

### Environment Variables
- **OPENAI_API_KEY**: Must be set to a valid OpenAI API key.  
- **VERBOSE** (optional): Set to any value to see more detailed logs.

### Example
```bash
# Example usage
export OPENAI_API_KEY=sk-****************
vcat my_data.json
```
You’ll see a loading spinner in the terminal. Once complete, your default browser opens an interactive HTML visualization of `my_data.json`.

### License
MIT License. See the [LICENSE](LICENSE) file for details.

