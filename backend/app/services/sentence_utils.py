import re


# Negative lookbehinds prevent false splits after:
#   - single uppercase letters: A., I., U.  (catches A.I., U.S.A., etc.)
#   - single digits: 1., 2.                  (catches numbered list artifacts)
SENTENCE_SPLIT_PATTERN = re.compile(
    r'(?<![A-Z]\.)(?<![0-9]\.)(?<=[.!?])\s+'
)

# Parts with fewer words than this are merged forward rather than dispatched
# as standalone sentences, preventing abbreviation artifacts like "Mr." or "St."
MIN_SENTENCE_WORDS = 3


def extract_complete_sentences(buffer: str) -> tuple[list[str], str]:
    parts = SENTENCE_SPLIT_PATTERN.split(buffer)
    if len(parts) <= 1:
        return [], buffer

    complete: list[str] = []
    remainder = ""
    merge_buffer = ""

    for i, part in enumerate(parts):
        stripped = part.strip()
        if not stripped:
            continue

        # Carry any previously-too-short fragment forward into this candidate
        candidate = (merge_buffer + " " + stripped).strip() if merge_buffer else stripped

        is_last = (i == len(parts) - 1)
        ends_with_punct = candidate[-1] in ('.', '!', '?')

        if is_last and not ends_with_punct:
            # Trailing fragment without closing punctuation — always remainder
            remainder = candidate
            merge_buffer = ""
        elif len(candidate.split()) < MIN_SENTENCE_WORDS:
            # Too short to be a standalone sentence — accumulate and merge forward
            merge_buffer = candidate
        else:
            complete.append(candidate)
            merge_buffer = ""

    # Any unresolved merge_buffer at loop end becomes part of remainder
    if merge_buffer:
        remainder = (merge_buffer + " " + remainder).strip() if remainder else merge_buffer

    return complete, remainder

def sanitize_for_tts(text: str) -> str:
    """
    Cleans text from LLM outputs to prevent TTS engine (Kokoro/Phonemizer) crashes.
    Strips markdown and normalizes whitespace/newlines.
    """
    if not text:
        return ""
    
    # Replace single or double newlines/carriage returns with spaces
    clean = re.sub(r'[\r\n]+', ' ', text)
    
    # Strip basic markdown like bold/italic asterisks, underscores
    clean = re.sub(r'\*\*|\*|__|#', '', clean)
    
    # Collapse multiple spaces
    clean = re.sub(r'\s+', ' ', clean)
    
    return clean.strip()
