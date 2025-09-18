# Claude to Markdown

Convert your Claude.ai conversation exports into beautifully formatted Markdown files for use in Obsidian, Logseq, or any markdown-based note-taking system.

## Features

✨ **Complete Conversion**
- Converts Claude JSON exports to individual Markdown files
- Preserves full conversation history with User/Assistant structure
- Maintains conversation metadata in YAML frontmatter

📝 **Smart Formatting**
- Handles all Claude artifact types (code, React, HTML, Mermaid diagrams, SVG)
- Converts artifacts to properly syntax-highlighted code blocks
- Removes internal thinking blocks for cleaner output
- Preserves formatting and structure of conversations

🗂️ **Organized Output**
- Creates descriptive filenames: `yyyy-mm-dd-slugified-title.md`
- Includes metadata (UUID, name, summary, timestamps) in frontmatter
- Perfect for searching, filtering, and linking in your knowledge base

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yuvadm/claude-to-markdown
cd claude-to-markdown
```

2. Ensure you have Python 3.6+ installed:
```bash
python --version
```

## Usage

### Basic Usage

1. Export your Claude conversations:
   - Go to [Claude.ai](https://claude.ai)
   - Navigate to Settings → Account
   - Click "Export data"
   - Download and extract the ZIP file
   - Locate `conversations.json` in the extracted files

2. Run the converter:
```bash
# Convert all conversations using defaults
python convert_conversations.py

# Specify input file and output directory
python convert_conversations.py conversations.json my_claude_notes

# Convert only first 100 conversations
python convert_conversations.py conversations.json output 100

# Show help
python convert_conversations.py --help
```

### Command Line Arguments

```
python convert_conversations.py [INPUT_FILE] [OUTPUT_DIR] [LIMIT]
```

| Argument | Description | Default |
|----------|-------------|---------|
| `INPUT_FILE` | Path to conversations.json | `conversations.json` |
| `OUTPUT_DIR` | Output directory for markdown files | `output` |
| `LIMIT` | Max number of conversations to convert | All |

### Examples

```bash
# Use all defaults (input: conversations.json, output: output/)
python convert_conversations.py

# Custom input and output paths
python convert_conversations.py ~/Downloads/conversations.json ~/Documents/claude-notes

# Process only first 50 conversations for testing
python convert_conversations.py conversations.json test_output 50

# Convert from a different location
python convert_conversations.py /path/to/claude_export.json /path/to/notes
```

3. Import to your note-taking app:
   - **Obsidian**: Copy the contents of `output/` to your vault
   - **Logseq**: Import the markdown files to your graph
   - **Notion**: Import as markdown (may need formatting adjustments)
   - **VS Code**: Open the folder directly to browse with markdown preview
   - Or use any markdown-compatible application

## Output Format

Each conversation is converted to a Markdown file with:

### Filename
```
2024-03-15-understanding-quantum-computing.md
```

### Content Structure
```markdown
---
uuid: 4dc7f4d6-7290-4b41-8bea-453c7dfeaa9f
name: Understanding Quantum Computing
summary: Discussion about quantum computing principles
created_at: 2024-03-15T10:30:00.000Z
updated_at: 2024-03-15T11:45:00.000Z
---

# Understanding Quantum Computing

## User
Can you explain quantum computing?

## Assistant
Quantum computing is a revolutionary approach to computation...
```

## Artifact Handling

The converter intelligently handles various Claude artifact types:

| Artifact Type | Converted To |
|--------------|--------------|
| `application/vnd.ant.code` | Code block with language syntax |
| `application/vnd.ant.react` | JSX code block |
| `application/vnd.ant.html` | HTML code block |
| `application/vnd.ant.mermaid` | Mermaid diagram block |
| `text/markdown` | Inline markdown |
| `image/svg+xml` | SVG code block |

## Tips for Different Platforms

### Obsidian
- Install the Mermaid plugin for diagram support
- Use Graph View to visualize conversation relationships
- Search by frontmatter fields using Dataview plugin

### Logseq
- Import files to see them in the journal view by date
- Use page properties (frontmatter) for queries
- Tag conversations for easy filtering

### VS Code
- Install a markdown preview extension
- Use the file explorer to browse by date
- Search across all files with Ctrl/Cmd+Shift+F

## Privacy & Security

- All processing happens locally on your machine
- No data is sent to external servers
- Your conversations remain private
- Consider the sensitivity of your data before sharing converted files

## Troubleshooting

**Issue**: Script says `conversations.json not found`
- **Solution**: Specify the correct path to your JSON file as the first argument

**Issue**: Some conversations are missing
- **Solution**: Conversations without content are skipped. Check the console output for the total processed

**Issue**: Special characters in filenames
- **Solution**: The script automatically sanitizes filenames for all operating systems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Some areas for improvement:

- [ ] Add support for custom output directories
- [ ] Include conversation statistics in a summary file
- [ ] Add options for different filename formats
- [ ] Support for incremental updates
- [ ] Export to other formats (Notion, Roam, etc.)

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built for the Claude.ai community
- Inspired by the need to preserve AI conversations for future reference
- Designed to work with any markdown-based workflow

## Contact

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ for knowledge preservation