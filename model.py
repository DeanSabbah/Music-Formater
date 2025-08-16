from os import scandir, replace
from pathlib import Path
from tinytag import TinyTag
import defs, json, random, string, logging

logger = logging.getLogger(__name__)

music = dict()

def index_files():
    with scandir(defs.basepath) as entries:
        for entry in entries:
            if TinyTag.SUPPORTED_FILE_EXTENSIONS.__contains__(Path(entry).suffix):
                track:TinyTag = TinyTag.get(entry)
                main_artist = track.artist.split(";")[0] # type: ignore
                if not music.__contains__(main_artist):
                    music[main_artist] = dict()
                    print(main_artist)
                if not music[main_artist].__contains__(track.album):
                    music[main_artist][track.album] = []
                music[main_artist][track.album].append({
                    "name": track.title,
                    "path": entry
                })

def move_files():
    for artist in music:
        for album in music[artist]:
            for track in music[artist][album]:
                # Create dir if absent
                Path(f"{defs.basepath}\\{artist}\\{album}").mkdir(parents=True, exist_ok=True)
                # Move file
                replace(track["path"], f"{defs.basepath}\\{artist}\\{album}\\{Path(track["path"]).stem}{"".join(Path(track["path"]).suffixes)}")
                
def main():
    if defs.log_out != "":
        logging.basicConfig(filename=defs.log_out, level=logging.INFO)
    music.clear()
    # Check for priviliges
    try:
        random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        Path(defs.basepath + f"\\{random_str}").mkdir()
        Path(defs.basepath + f"\\{random_str}").rmdir()
    except PermissionError:
        #print("Error: Admin proviliges required")
        logger.error("Admin proviliges required")
        raise PermissionError
    except Exception as e:
        logger.fatal("Unkown Error")
        logger.fatal(e)
        raise e
    index_files()
    if defs.json:
        serializable_music = {
            artist: {
                album: [track["name"] for track in tracks]
                for album, tracks in albums.items()
            }
            for artist, albums in music.items()
        }
        with open(f'{defs.basepath}\\music_index.json', "wt") as f:
            json.dump(serializable_music, f, indent=2)
    move_files()