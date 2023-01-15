#!/usr/bin/python3

from pathlib import Path
from argparse import ArgumentParser
from os import path, scandir
from json import loads
from subprocess import getstatusoutput

languages = {"eng": "Inglés", "spa": '"Español Latino"', "jpn": "Japonés"}
subtitles = {
    "eng": '"Subtítulos Inglés"',
    "spa": '"Subtítulos Español"',
    "und": '"Subtítulos Forzados"',
}
validLanguages = ["eng", "spa", "jpn"]


def main():
    parser = ArgumentParser(description="Tag MKV files.")
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help="directory containing files from which update tags",
    )
    parser.add_argument("-l", "--language", required=True, help="original language from the media")

    args = parser.parse_args()

    dir = Path(args.directory)
    if not dir.exists():
        print("The target directory does not exists")
        exit(1)

    language = args.language
    if not validLanguages.__contains__(language):
        print("Not a valid language provided")
        exit(1)

    with scandir(dir) as files:
        for file in files:
            if file.is_dir():
                continue

            if not file.name.endswith(".mkv"):
                continue

            print(file.name + "...", end=" ")
            tracks = get_tracks(file.path)
            if tracks[0]:
                print("ERROR")

                for error in tracks[1]:
                    print(error)

                continue

            audios = []
            subtitles = []

            for track in tracks[1]:
                if track["type"] == "audio":
                    audios.append(track)
                    continue

                if track["type"] == "subtitles":
                    subtitles.append(track)
                    continue

            success_title = update_title(file.path, file.name)

            if not success_title:
                print("ERROR WITH TITLE")
                continue

            sucess_audios = update_audios(file.path, audios, language)

            if not sucess_audios:
                print("ERROR WITH AUDIOS")
                continue

            sucess_subs = update_subs(file.path, subtitles, language)

            if not sucess_subs:
                print("ERROR WITH SUBS")
                continue

            print("OK")


def normalize_path(pathStr: str) -> str:
    return path.normpath('"' + pathStr + '"')


def get_title_from_filename(file_name: str) -> str:
    return file_name.split(" - ")[1].split(".mkv")[0].strip()


def get_tracks(pathStr: str) -> tuple:
    mkv_command = "mkvmerge -J " + normalize_path(pathStr)

    file_info = getstatusoutput(mkv_command.strip())
    json_result: dict = loads(file_info[1])

    if file_info[0] != 0:
        return (True, json_result["errors"])

    return (False, json_result["tracks"])


def update_title(pathStr: str, file_name: str) -> bool:
    title = get_title_from_filename(file_name)
    mkv_command = "mkvpropedit " + normalize_path(pathStr) + ' -e info -s title="' + title + '"'

    result = getstatusoutput(mkv_command.strip())
    return result[0] == 0


def update_audios(pathStr: str, audios: list, language: str) -> bool:
    mkv_command = "mkvpropedit " + normalize_path(pathStr)

    for audio in audios:
        lang: str = audio["properties"]["language"]
        default: str = str(int(lang == language))

        mkv_command += " -e track:@" + str(audio["properties"]["number"]) + " "
        mkv_command += (
            "-s flag-default="
            + default
            + " -s flag-enabled=1 -s flag-forced=0 -s name="
            + languages[lang]
        )

    result = getstatusoutput(mkv_command.strip())
    return result[0] == 0


def update_subs(pathStr: str, subs: list, language: str) -> bool:
    mkv_command = "mkvpropedit " + normalize_path(pathStr)

    for sub in subs:
        lang: str = sub["properties"]["language"]
        default: str = str(int(lang == "spa" and language != "spa"))
        forced: str = str(int(lang == "und"))

        mkv_command += " -e track:@" + str(sub["properties"]["number"]) + " "
        mkv_command += (
            "-s flag-default="
            + default
            + " -s flag-forced="
            + forced
            + " -s flag-enabled=1 -s name="
            + subtitles[lang]
        )

    result = getstatusoutput(mkv_command.strip())
    return result[0] == 0


main()
