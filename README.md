# vcat

### Overview
**vcat** is a command-line (CLI) tool that generates human-friendly visualizations from any file’s contents.


https://github.com/user-attachments/assets/f1836b5b-3664-4ef5-9d90-3d0e138e234b


### Key Features
- **Automatic Visualization**: Provide a file, and **vcat** writes a custom Python script on the fly to produce an HTML-based visualization.
- **Supports Any File Size**: `vcat` works for visualziing files of any size. 
- **Large File Handling**: For files exceeding a configurable threshold, **vcat** can break down the content into chunks so the final visualization is still efficient and doesn't kill your browser.
- **Simple CLI**: An intuitive command-line interface (`vcat path/to/file.txt`) that does all the heavy lifting for you.
- **Custom Styling**: Cool custom styles 😎 (maybe).

### Installation
1. **Prerequisites**:  
   - Python 3.7+  
   - An OpenAI API key (`OPENAI_API_KEY` must be set as an environment variable)  
2. **Install with pip**:  
   ```bash
   pip install vcat
   ```

### Usage
```bash
# Create the environment variable
export OPENAI_API_KEY=sk-****************

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

