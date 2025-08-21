from os import scandir, replace, remove
from pathlib import Path
from tinytag import TinyTag
import defs, json, random, string, re, time

music = dict()

# Try to create a new file with random name, then delete it
def check_permision():
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
    open(defs.basepath + f"\\{random_str}", "x")
    remove(defs.basepath + f"\\{random_str}")
    
def wait_for_choice():
    while defs.confiriming_quit:
        defs.logger.debug("Awaiting responce for quit confirmation")
        time.sleep(0.5)
        
def check_canceled(pos:str):
    if defs.cancel_request:
        defs.logger.info(f"Cancellation requested {pos}.")
        raise SystemExit

def index_files():
    with scandir(defs.basepath) as entries:
        entries = list(entries)
        num_files = len(entries)
        current_file = 0
        defs.logger.info("Indexing files")
        for entry in entries:
            current_file += 1
            defs.percent_complete = (current_file/num_files) * 0.33
            wait_for_choice()
            check_canceled("during file indexing")
            if TinyTag.SUPPORTED_FILE_EXTENSIONS.__contains__(Path(entry).suffix):
                track:TinyTag = TinyTag.get(entry)
                main_artist = re.split("; |, |&", track.artist)[0].strip() #type: ignore
                if not music.__contains__(main_artist):
                    defs.logger.info(f"Adding {main_artist} to index")
                    music[main_artist] = dict()
                if not music[main_artist].__contains__(track.album):
                    defs.logger.info(f"Adding {track.album} to index")
                    music[main_artist][track.album] = []
                defs.logger.info(f"Adding {track.title} to index")
                music[main_artist][track.album].append({
                    "name": track.title,
                    "path": entry
                })
        defs.percent_complete = 0.33

def move_files():
    num_files = len(music)
    current_file = 0
    defs.logger.info("during moving files")
    for artist in music:
        wait_for_choice()
        check_canceled("during moving files")
        for album in music[artist]:
            wait_for_choice()
            check_canceled("during moving files")
            for track in music[artist][album]:
                current_file += 1
                defs.percent_complete += (current_file/num_files) * 0.67
                wait_for_choice()
                check_canceled("during moving files")
                defs.logger.debug(f"Moving >>{track["path"].path}<< to >>{defs.basepath}\\{artist}\\{album}\\{Path(track["path"]).stem}{"".join(Path(track["path"]).suffixes)}<<")
                Path(f"{defs.basepath}\\{artist}\\{album}").mkdir(parents=True, exist_ok=True)
                replace(track["path"], f"{defs.basepath}\\{artist}\\{album}\\{Path(track["path"]).stem}{"".join(Path(track["path"]).suffixes)}")
    defs.percent_complete = 1.0

def main():
    wait_for_choice()
    if defs.cancel_request:
        defs.logger.info("Cancellation requested before starting main.")
        raise SystemExit
    # test timer
    # start_time = time.time()
    # while(time.time() - start_time < 5):
    #     wait_for_choice()
    #     check_canceled("test timer")
    music.clear()
    # Check for priviliges
    try:
        check_permision()
    except PermissionError:
        defs.logger.error("Admin proviliges required")
        raise PermissionError
    except FileExistsError:
        # try again
        defs.logger.warning("File exists, trying again with new string")
        check_permision()
    except Exception as e:
        defs.logger.fatal("Unkown Error")
        defs.logger.fatal(e)
        raise e
    wait_for_choice()
    check_canceled("before indexing files")
    index_files()
    if defs.json:
        wait_for_choice()
        check_canceled("before writing JSON")
        serializable_music = {
            artist: {
                album: [track["name"] for track in tracks]
                for album, tracks in albums.items()
            }
            for artist, albums in music.items()
        }
        with open(f'{defs.basepath}\\music_index.json', "wt") as f:
            json.dump(serializable_music, f, indent=2)
    wait_for_choice()
    check_canceled("before moving files")
    move_files()