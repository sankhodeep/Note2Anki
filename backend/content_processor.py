import tiktoken
from typing import List, Dict, Any

# Corrected: Use a relative import for a module within the same package
from .markdown_parser import parse_markdown

def reconstruct_markdown(all_sections: List[Dict[str, Any]], selected_titles: List[str]) -> str:
    """
    Reconstructs a markdown document containing only the selected sections
    and their subsections.
    """
    content_parts = []
    selected_set = set(selected_titles)

    i = 0
    while i < len(all_sections):
        section = all_sections[i]
        section_title_full = f"{'#' * section['level']} {section['title']}"

        if section_title_full in selected_set:
            content_parts.append(f"\n{section_title_full}\n{section['content']}".strip())

            current_level = section['level']
            j = i + 1
            while j < len(all_sections) and all_sections[j]['level'] > current_level:
                next_section = all_sections[j]
                next_section_title = f"{'#' * next_section['level']} {next_section['title']}"
                content_parts.append(f"\n{next_section_title}\n{next_section['content']}".strip())
                j += 1
            i = j
        else:
            i += 1

    return "\n\n".join(content_parts)


def chunk_content(markdown_text: str, token_limit: int = 5000) -> List[Dict[str, Any]]:
    """
    Chunks markdown content by grouping sections under top-level headings (H1)
    and then packing these groups into chunks based on a token limit.
    """
    # Moved from module level to here to prevent import-time errors.
    encoding = tiktoken.get_encoding("cl100k_base")
    all_sections = parse_markdown(markdown_text)
    if not all_sections:
        return []

    topic_blocks = []
    current_block = []
    if all_sections:
        for section in all_sections:
            if section['level'] == 1 and current_block:
                topic_blocks.append(current_block)
                current_block = []
            current_block.append(section)
        topic_blocks.append(current_block)

    chunks = []
    current_chunk_content_parts = []
    current_chunk_tokens = 0

    for block in topic_blocks:
        if not block: continue

        block_title = block[0]['title']
        block_text = "\n\n".join([f"{'#' * s['level']} {s['title']}\n{s['content']}".strip() for s in block])
        block_tokens = len(encoding.encode(block_text))

        if block_tokens > token_limit:
            if current_chunk_content_parts:
                chunks.append({"content": "\n\n".join(current_chunk_content_parts), "warning": None})
                current_chunk_content_parts, current_chunk_tokens = [], 0

            chunks.append({
                "content": block_text,
                "warning": f"Topic '{block_title}' alone ({block_tokens} tokens) exceeds the limit of {token_limit}."
            })
            continue

        if current_chunk_tokens + block_tokens > token_limit and current_chunk_content_parts:
            chunks.append({"content": "\n\n".join(current_chunk_content_parts), "warning": None})
            current_chunk_content_parts = [block_text]
            current_chunk_tokens = block_tokens
        else:
            current_chunk_content_parts.append(block_text)
            current_chunk_tokens += block_tokens

    if current_chunk_content_parts:
        chunks.append({"content": "\n\n".join(current_chunk_content_parts), "warning": None})

    return chunks


# if __name__ == '__main__':
#     print("Running Content Processor test...")

#     # --- Test 1: Markdown Reconstruction (No changes needed here) ---
#     print("\n--- Testing Markdown Reconstruction ---")
#     recon_md_input = """
# # Chapter 1: The Basics
# ## Section 1.1: Details
# Content for 1.1
# # Chapter 2: Other
# Content for 2
#     """
#     recon_sections = parse_markdown(recon_md_input)
#     ai_selected = ["# Chapter 1: The Basics"]
#     reconstructed = reconstruct_markdown(recon_sections, ai_selected)
#     assert "Chapter 1" in reconstructed
#     assert "Section 1.1" in reconstructed
#     assert "Chapter 2" not in reconstructed
#     print("Reconstruction test PASSED.")

#     # --- Test 2: Smart Chunking (with corrected data and logging) ---
#     print("\n--- Testing Smart Chunking ---")

#     # This text is now genuinely oversized for the token limit.
#     long_text = "This is a very long sentence repeated over and over again to ensure it exceeds the token limit. " * 10

#     chunking_md = f"""
# # Chapter 1
# Small topic.

# # Chapter 2
# Another small topic.

# # Chapter 3
# {long_text}

# # Chapter 4
# Final small topic.
#     """
#     token_limit = 50
#     chunks = chunk_content(chunking_md, token_limit)

#     print(f"\nContent chunked with a {token_limit} token limit:")
#     for i, chunk in enumerate(chunks):
#         chunk_token_count = len(ENCODER.encode(chunk['content']))
#         print(f"  Chunk {i+1} (Tokens: {chunk_token_count}) (Warning: {chunk['warning']})")

#     assert len(chunks) == 3, f"Expected 3 chunks, but got {len(chunks)}"

#     assert "Chapter 1" in chunks[0]['content']
#     assert "Chapter 2" in chunks[0]['content']
#     assert chunks[0]['warning'] is None

#     assert "Chapter 3" in chunks[1]['content']
#     assert chunks[1]['warning'] is not None

#     assert "Chapter 4" in chunks[2]['content']
#     assert chunks[2]['warning'] is None
#     print("Chunking test PASSED.")

#     print("\nContent Processor test finished successfully!")