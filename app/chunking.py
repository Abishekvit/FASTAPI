def split_text(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    seps = ["\n\n", "\n", ". ", " "]
    #here the chunking method used is split into paragraphs, then sentences, then words, and finally by character count if necessary. The function recursively splits the text based on the specified separators until the chunks are of the desired size or smaller.
    #size is 800 characters, overlap is 120 characters, meaning that the last 120 characters of one chunk will be included at the beginning of the next chunk to maintain context.
    def rec(t, seps):
        if len(t) <= size:
            return [t]
        if not seps:
            return [t[i:i + size] for i in range(0, len(t), size)]
        out, cur = [], ""
        for p in t.split(seps[0]):
            piece = f"{cur}{seps[0]}{p}" if cur else p
            if len(piece) <= size:
                cur = piece
                continue
            if cur:
                out.append(cur)
            if len(p) > size:
                out.extend(rec(p, seps[1:]))
                cur = ""
            else:
                cur = p
        if cur:
            out.append(cur)
        return out

    chunks = [c.strip() for c in rec(text, seps) if c.strip()]
    return [(chunks[i - 1][-overlap:] + " " + c) if i and overlap else c
            for i, c in enumerate(chunks)]