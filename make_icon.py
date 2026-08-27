import struct
from pathlib import Path

BACKGROUND = (47, 102, 144, 255)
PAPER = (255, 255, 255, 255)
LINE = (47, 102, 144, 255)


def pixel(x, y, size):
    if size * 3 // 16 <= x < size * 13 // 16 and size * 2 // 16 <= y < size * 14 // 16:
        line_start = size * 5 // 16
        line_end = size * 11 // 16
        line_height = max(1, size // 16)
        if line_start <= x < line_end and (
            size * 7 // 16 <= y < size * 7 // 16 + line_height
            or size * 10 // 16 <= y < size * 10 // 16 + line_height
        ):
            return LINE
        return PAPER
    return BACKGROUND


def create_icon(path):
    sizes = (16, 24, 32, 48, 64, 256)
    images = []
    for size in sizes:
        pixels = bytearray()
        for y in range(size - 1, -1, -1):
            for x in range(size):
                red, green, blue, alpha = pixel(x, y, size)
                pixels.extend((blue, green, red, alpha))
        mask_row_size = ((size + 31) // 32) * 4
        mask = bytes(mask_row_size * size)
        header = struct.pack(
            "<IiiHHIIiiII",
            40, size, size * 2, 1, 32, 0, len(pixels), 0, 0, 0, 0
        )
        images.append(header + pixels + mask)

    directory = struct.pack("<HHH", 0, 1, len(sizes))
    entries = bytearray()
    offset = 6 + 16 * len(sizes)
    for size, image in zip(sizes, images):
        entries.extend(struct.pack("<BBBBHHII", size if size < 256 else 0, size if size < 256 else 0, 0, 0, 1, 32, len(image), offset))
        offset += len(image)
    Path(path).write_bytes(directory + entries + b"".join(images))


if __name__ == "__main__":
    create_icon(Path(__file__).with_name("classic_notepad.ico"))
