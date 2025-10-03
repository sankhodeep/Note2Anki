import re
from typing import List, Dict, Any

def parse_markdown(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Parses a markdown string to extract headings and their content.

    Each heading and its content are treated as a 'section'. The content
    of a heading runs from after the heading line to the line just before
    the next heading.

    Args:
        markdown_text: The string content of the markdown file.

    Returns:
        A list of dictionaries, where each dictionary represents a
        heading section.
        e.g., [{'level': 1, 'title': 'Title', 'content': '...'}, ...]
    """
    lines = markdown_text.split('\n')
    sections = []
    current_section_content = []
    current_section_heading = None

    for line in lines:
        heading_match = re.match(r'^(#+)\s+(.*)', line)
        if heading_match:
            # If we find a new heading, save the previous section first
            if current_section_heading:
                sections.append({
                    'level': len(current_section_heading[0]),
                    'title': current_section_heading[1].strip(),
                    'content': '\n'.join(current_section_content).strip()
                })
                current_section_content = []

            current_section_heading = (heading_match.group(1), heading_match.group(2))
        elif current_section_heading:
            current_section_content.append(line)

    # Add the last section after the loop finishes
    if current_section_heading:
        sections.append({
            'level': len(current_section_heading[0]),
            'title': current_section_heading[1].strip(),
            'content': '\n'.join(current_section_content).strip()
        })

    return sections

# if __name__ == '__main__':
#     test_md = """
# # Main Title

# Some intro text.

# ## Subheading 1

# Content for subheading 1.
# More content.

# ## Subheading 2

# Content for subheading 2.

# ### Sub-subheading 2.1

# Content for 2.1

# # Another Main Title

# Content for the second main title.
# """
#     parsed = parse_markdown(test_md.strip())

#     # Basic structural and content assertions
#     assert len(parsed) == 5
#     assert parsed[0]['title'] == 'Main Title'
#     assert parsed[0]['level'] == 1
#     assert parsed[0]['content'] == 'Some intro text.'

#     assert parsed[1]['title'] == 'Subheading 1'
#     assert parsed[1]['level'] == 2
#     assert parsed[1]['content'] == 'Content for subheading 1.\nMore content.'

#     assert parsed[2]['title'] == 'Subheading 2'
#     assert parsed[2]['level'] == 2
#     assert parsed[2]['content'] == 'Content for subheading 2.'

#     assert parsed[3]['title'] == 'Sub-subheading 2.1'
#     assert parsed[3]['level'] == 3
#     assert parsed[3]['content'] == 'Content for 2.1'

#     assert parsed[4]['title'] == 'Another Main Title'
#     assert parsed[4]['level'] == 1
#     assert parsed[4]['content'] == 'Content for the second main title.'

#     print("Markdown parser test passed!")