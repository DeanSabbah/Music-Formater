from os import scandir, replace, remove
from pathlib import Path
from tinytag import TinyTag
import defs, json, random, string, re, time, traceback

logger = defs.log()

music = dict()

# For testing
def wait(sec):
    start_time = time.time()
    while(time.time() - start_time < sec):
        check_canceled("during test timer")

# Try to create a new file with random name, then delete it
def check_permision():
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
    try:
        open(defs.basepath + f"/{random_str}", "x")
        remove(defs.basepath + f"/{random_str}")
    except FileExistsError:
        if check_permision.number_of_tries >= 2:   # type: ignore
            logger.warning("File exists, too many tries")
            raise FileExistsError
        # try again
        check_permision.number_of_tries += 1   # type: ignore
        logger.warning("File exists, trying again with new string")
        check_permision()
    
def wait_for_choice():
    while defs.confiriming_quit:
        defs.logger.debug("Awaiting responce for quit confirmation")
        time.sleep(0.25)
        
def check_canceled(pos:str):
    wait_for_choice()
    if defs.cancel_request:
        logger.info(f"Cancellation requested {pos}.")
        raise SystemExit

def index_files() -> int:
    with scandir(defs.basepath) as entries:
        entries = list(entries)
        num_files:int = len(entries)
        current_file:int = 0
        indexed_files:int = 0
        logger.info("Indexing files")
        for entry in entries:
            check_canceled("during file indexing")
            current_file += 1
            if TinyTag.SUPPORTED_FILE_EXTENSIONS.__contains__(Path(entry).suffix):
                indexed_files += 1
                track:TinyTag = TinyTag.get(entry)
                # Split using common seperators for tracks with multiple artists
                main_artist = re.split("; |, |&", track.artist)[0].strip() #type: ignore
                if not music.__contains__(main_artist):
                    logger.debug(f"Adding {main_artist} to index")
                    music[main_artist] = dict()
                if not music[main_artist].__contains__(track.album):
                    logger.debug(f"Adding {track.album} to index")
                    music[main_artist][track.album] = []
                logger.debug(f"Adding {track.title} to index")
                music[main_artist][track.album].append({
                    "name": track.title,
                    "path": entry
                })
            defs.percent_complete = (current_file/num_files) * 0.33
        defs.percent_complete = 0.333
        return indexed_files

def move_files(num_files:int):
    current_file = 0
    logger.info("Moving files")
    for artist in music:
        for album in music[artist]:
            for track in music[artist][album]:
                check_canceled("during moving files")
                current_file += 1
                logger.debug(f"Moving >>{track["path"].path}<< to >>{defs.basepath}/{artist}/{album}/{Path(track["path"]).stem}{"".join(Path(track["path"]).suffixes)}<<")
                Path(f"{defs.basepath}/{artist}/{album}").mkdir(parents=True, exist_ok=True) # type: ignore
                replace(track["path"], f"{defs.basepath}/{artist}/{album}/{Path(track["path"]).stem}{"".join(Path(track["path"]).suffixes)}")
                defs.percent_complete = 0.33 + (current_file/num_files) * 0.67
    defs.percent_complete = 0.999
    
def output_json():
    check_canceled("before writing JSON")
    logger.info("Serializing music data")
    serializable_music = {
        artist: {
            album: [track["name"] for track in tracks]
            for album, tracks in albums.items()
        }
        for artist, albums in music.items()
    }
    logger.info("Writing JSON")
    with open(f'{defs.basepath}/music_index.json', "wt") as f:
        json.dump(serializable_music, f, indent=2)

def main():
    check_canceled("before starting main")
    music.clear()
    defs.percent_complete = 0
    # Check for priviliges
    try:
        check_permision.number_of_tries = 0  # type: ignore
        check_permision()
    except PermissionError:
        logger.error("Admin proviliges required")
        raise PermissionError
    except Exception as e:
        logger.fatal("Unknown error\n" + traceback.format_exc())
        raise e
    check_canceled("before indexing files")
    num_files = index_files()
    if defs.json_out:
        output_json()
    check_canceled("before moving files")
    move_files(num_files)