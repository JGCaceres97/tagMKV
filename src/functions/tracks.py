from const.languages import languages, subtitles, validLanguages
from json import loads
from subprocess import getstatusoutput
from functions.utils import get_title_from_filename, normalize_path


def get_tracks(pathStr: str) -> tuple:
    mkv_command = f"mkvmerge -J {normalize_path(pathStr)}"

    file_info = getstatusoutput(mkv_command.strip())
    json_result: dict = loads(file_info[1])

    if file_info[0] != 0:
        return (True, json_result["errors"])

    return (False, json_result["tracks"])


def update_title(pathStr: str, file_name: str) -> bool:
    title = get_title_from_filename(file_name)
    mkv_command = f"mkvpropedit {normalize_path(pathStr)}"

    mkv_command = f'{mkv_command} -e info -s title="{title}"'

    result = getstatusoutput(mkv_command.strip())
    return result[0] == 0


def update_videos(pathStr: str, videos: list) -> bool:
    mkv_command = f"mkvpropedit {normalize_path(pathStr)}"

    for video in videos:
        props: dict = video["properties"]

        mkv_command = f'{mkv_command} -e track:@{str(props["number"])}'
        mkv_command = f"{mkv_command} -s flag-default=1 -s flag-enabled=1 -s flag-forced=0 -s language=und -d name"

    result = getstatusoutput(mkv_command.strip())
    return result[0] == 0


def update_audios(pathStr: str, audios: list, language: str) -> bool:
    mkv_command = f"mkvpropedit {normalize_path(pathStr)}"

    for audio in audios:
        props: dict = audio["properties"]

        lang: str = props["language"]
        default: str = str(int(lang == language))

        tagFound: bool = lang in languages

        if not tagFound:
            print("AUDIO TAG NOT FOUND")

        while not lang in languages:
            langOptions = str(validLanguages).replace("'", "")

            lang = input(
                f'"{lang}" not found in defined dict, enter an alternative {langOptions}: '
            )

        mkv_command = f'{mkv_command} -e track:@{str(props["number"])}'
        mkv_command = f"{mkv_command} -s flag-default={default} -s flag-enabled=1 -s flag-forced=0 -s name={languages[lang]}"

        if not tagFound:
            mkv_command = f"{mkv_command} -s language={lang}"

    result = getstatusoutput(mkv_command.strip())
    return result[0] == 0


def update_subs(pathStr: str, subs: list, language: str) -> bool:
    mkv_command = f"mkvpropedit {normalize_path(pathStr)}"

    for sub in subs:
        props: dict = sub["properties"]

        lang: str = props["language"]
        name: str = ""

        if "track_name" in props:
            name = props["track_name"]

        if name.upper().__contains__("FORZADO"):
            lang = "und"

        forced: str = str(int(lang == "und"))
        default: str = str(int(lang == "spa" and language != "spa"))

        mkv_command = f'{mkv_command} -e track:@{str(props["number"])}'
        mkv_command = f"{mkv_command} -s flag-default={default} -s flag-enabled=1 -s flag-forced={forced} -s name={subtitles[lang]} -s language={lang}"

    result = getstatusoutput(mkv_command.strip())
    return result[0] == 0
