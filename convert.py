#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
import re

def sanitize_filename(text):
    """Remove or replace characters that are invalid in filenames"""
    if not text:
        return "untitled"
    # Replace invalid characters with underscores
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    # Remove any non-printable characters
    text = ''.join(char for char in text if char.isprintable())
    # Limit length to avoid filesystem issues
    return text[:100].strip()

def convert_timestamp_to_filename(timestamp_str):
    """Convert ISO timestamp to yyyy-mm-dd format"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return "unknown-date"

def convert_artifact_to_markdown(text):
    """Convert antArtifact tags to markdown code blocks and handle all types"""
    import re
    
    # First, let's find all artifact tags to analyze them
    all_artifacts_pattern = r'<antArtifact\s+([^>]*?)>(.*?)</antArtifact>'
    
    def analyze_artifact(match):
        attributes = match.group(1)
        content = match.group(2)
        
        # Extract type attribute if present
        type_match = re.search(r'type="([^"]+)"', attributes)
        artifact_type = type_match.group(1) if type_match else None
        
        # Extract language attribute if present
        lang_match = re.search(r'language="([^"]+)"', attributes)
        language = lang_match.group(1) if lang_match else None
        
        # Extract title if present
        title_match = re.search(r'title="([^"]+)"', attributes)
        title = title_match.group(1) if title_match else None
        
        # Add title as a comment if present
        title_line = f"# {title}\n\n" if title else ""
        
        # Handle all known types
        if artifact_type == "application/vnd.ant.code" and language:
            return f"\n```{language}\n{content}\n```\n"
        elif artifact_type == "application/vnd.ant.mermaid":
            return f"\n```mermaid\n{content}\n```\n"
        elif artifact_type == "application/vnd.ant.react":
            # React components - use jsx
            return f"\n```jsx\n{content}\n```\n"
        elif artifact_type == "application/vnd.ant.html":
            # HTML artifacts
            return f"\n```html\n{content}\n```\n"
        elif artifact_type == "text/html":
            # Plain HTML
            return f"\n```html\n{content}\n```\n"
        elif artifact_type == "text/markdown":
            # Markdown content - just include as-is with a separator
            return f"\n---\n\n{title_line}{content}\n\n---\n"
        elif artifact_type == "image/svg+xml":
            # SVG images
            return f"\n```svg\n{content}\n```\n"
        elif language:
            # Has language but different/no type
            return f"\n```{language}\n{content}\n```\n"
        else:
            # Default to plain code block
            return f"\n```\n{content}\n```\n"
    
    # Replace all artifacts
    text = re.sub(all_artifacts_pattern, analyze_artifact, text, flags=re.DOTALL)
    
    # Remove antThinking tags (these are internal thinking, not meant for output)
    text = re.sub(r'<antThinking>.*?</antThinking>', '', text, flags=re.DOTALL)
    
    return text

def extract_message_text(message):
    """Extract text from message, handling both direct text and content array"""
    if 'text' in message and message['text']:
        text = message['text']
    elif 'content' in message and message['content']:
        # Concatenate text from all content items
        texts = []
        for item in message['content']:
            if isinstance(item, dict) and 'text' in item:
                texts.append(item['text'])
        text = '\n'.join(texts)
    else:
        return ""
    
    # Convert artifacts to markdown code blocks
    return convert_artifact_to_markdown(text)

def convert_conversation_to_markdown(conversation):
    """Convert a single conversation to markdown format"""
    markdown_lines = []
    
    # Add YAML frontmatter
    markdown_lines.append("---")
    markdown_lines.append(f"uuid: {conversation.get('uuid', 'unknown')}")
    markdown_lines.append(f"name: {conversation.get('name', 'untitled')}")
    markdown_lines.append(f"summary: {conversation.get('summary', 'No summary available')}")
    markdown_lines.append(f"created_at: {conversation.get('created_at', 'unknown')}")
    markdown_lines.append(f"updated_at: {conversation.get('updated_at', 'unknown')}")
    markdown_lines.append("---")
    markdown_lines.append("")  # Blank line after frontmatter
    
    # Add title if available
    if conversation.get('name'):
        markdown_lines.append(f"# {conversation['name']}\n")
    
    # Process messages
    for message in conversation.get('chat_messages', []):
        sender = message.get('sender', 'unknown')
        text = extract_message_text(message)
        
        if not text:
            continue
            
        # Determine header based on sender
        if sender.lower() == 'human':
            markdown_lines.append("## User")
        elif sender.lower() in ['assistant', 'claude']:
            markdown_lines.append("## Assistant")
        else:
            markdown_lines.append(f"## {sender}")
        
        markdown_lines.append(text)
        markdown_lines.append("")  # Add blank line between messages
    
    return '\n'.join(markdown_lines)

def slugify(text):
    """Convert text to a URL-friendly slug"""
    if not text:
        return "untitled"
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove non-alphanumeric characters (except hyphens)
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Strip leading/trailing hyphens
    text = text.strip('-')
    # Limit length
    return text[:100] if text else "untitled"

def print_usage():
    """Print usage information"""
    print("Usage: python3 convert_conversations.py [INPUT_FILE] [OUTPUT_DIR] [LIMIT]")
    print()
    print("Convert Claude.ai conversation exports to Markdown files")
    print()
    print("Arguments:")
    print("  INPUT_FILE   Path to conversations.json file (default: conversations.json)")
    print("  OUTPUT_DIR   Output directory for markdown files (default: output)")
    print("  LIMIT        Maximum number of conversations to convert (default: all)")
    print()
    print("Examples:")
    print("  python3 convert_conversations.py")
    print("  python3 convert_conversations.py conversations.json output")
    print("  python3 convert_conversations.py conversations.json my_notes 100")
    print("  python3 convert_conversations.py ~/Downloads/conversations.json ~/Documents/claude-notes")

def main():
    # Parse command-line arguments
    args = sys.argv[1:]
    
    # Show help if requested
    if args and args[0] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    # Set defaults and parse positional arguments
    input_file = 'conversations.json'
    output_dir = 'output'
    limit = None
    
    if len(args) >= 1:
        input_file = args[0]
    if len(args) >= 2:
        output_dir = args[1]
    if len(args) >= 3:
        try:
            limit = int(args[2])
            if limit <= 0:
                print(f"Error: LIMIT must be a positive number, got {limit}")
                sys.exit(1)
        except ValueError:
            print(f"Error: LIMIT must be a number, got '{args[2]}'")
            sys.exit(1)
    
    if len(args) > 3:
        print("Warning: Extra arguments ignored")
        print()
    
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        print()
        print_usage()
        sys.exit(1)
    
    # Load the conversations
    print(f"Loading conversations from: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Validate it's a list
    if not isinstance(conversations, list):
        print("Error: JSON file should contain a list of conversations")
        sys.exit(1)
    
    total_conversations = len(conversations)
    print(f"Found {total_conversations} conversations")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Apply limit if specified
    if limit:
        conversations_to_process = conversations[:limit]
        print(f"Processing first {len(conversations_to_process)} conversations (limit: {limit})")
    else:
        conversations_to_process = conversations
        print(f"Processing all {len(conversations_to_process)} conversations")
    
    print("-" * 60)
    
    # Process conversations
    successful = 0
    failed = 0
    
    for i, conversation in enumerate(conversations_to_process):
        try:
            print(f"Processing conversation {i+1}/{len(conversations_to_process)}...", end='')
            
            # Generate filename
            timestamp = conversation.get('created_at', '')
            date_time_str = convert_timestamp_to_filename(timestamp)
            
            # Use the conversation name (which becomes H1 header) for the filename
            title = conversation.get('name', 'untitled')
            slugified_title = slugify(title)
            
            filename = f"{date_time_str}-{slugified_title}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Convert to markdown
            markdown_content = convert_conversation_to_markdown(conversation)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f" ✓ {filename}")
            successful += 1
            
        except Exception as e:
            print(f" ✗ Failed: {e}")
            failed += 1
    
    # Print summary
    print("-" * 60)
    print(f"Conversion complete!")
    print(f"  Successfully converted: {successful}")
    if failed > 0:
        print(f"  Failed: {failed}")
    print(f"  Output directory: {output_dir}/")
    
    if limit and limit < total_conversations:
        remaining = total_conversations - limit
        print(f"  Remaining conversations: {remaining} (use higher limit to convert more)")

if __name__ == "__main__":
    main()