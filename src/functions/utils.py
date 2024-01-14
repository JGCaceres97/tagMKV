from os import path


def normalize_path(pathStr: str) -> str:
    quotedPath = f'"{pathStr}"'

    return path.normpath(quotedPath)


def get_title_from_filename(file_name: str) -> str:
    return file_name.split(" - ")[1].split(".mkv")[0].strip()
