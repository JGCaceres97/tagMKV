#!/usr/bin/python3

from pathlib import Path
from argparse import ArgumentParser
from os import scandir
from functions.tracks import (
    get_tracks,
    update_audios,
    update_subs,
    update_title,
    update_videos,
)
from const.languages import validLanguages


def main():
    parser = ArgumentParser(description="Tag MKV files.")
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help="directory containing files from which update tags",
    )
    parser.add_argument("-l", "--language", help="original language from the media")

    args = parser.parse_args()
    argLang: str = args.language

    dir = Path(args.directory)
    if not dir.exists():
        print("The target directory does not exists.")
        exit(1)

    while argLang is None or not validLanguages.__contains__(argLang):
        argLang = input("Enter the default audio language to be set: ")

        if not validLanguages.__contains__(argLang):
            langOptions = str(validLanguages).replace("'", "")

            print(f"Not a valid language provided. {langOptions}\n")

    language: str = argLang

    with scandir(dir) as files:
        for file in files:
            if file.is_dir():
                continue

            if not file.name.endswith(".mkv"):
                continue

            print(f"{file.name}...", end=" ")
            tracks = get_tracks(file.path)
            if tracks[0]:
                print("ERROR")

                for error in tracks[1]:
                    print(error)

                continue

            videos = []
            audios = []
            subtitles = []

            for track in tracks[1]:
                if track["type"] == "video":
                    videos.append(track)
                    continue

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

            clean_videos = update_videos(file.path, videos)
            if not clean_videos:
                print("ERROR WITH VIDEOS")
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


main()
