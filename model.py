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

def index_files():
    with scandir(defs.basepath) as entries:
        entries = list(entries)
        num_files = len(entries)
        current_file = 0
        defs.logger.info("Indexing files")
        for entry in entries:
            current_file += 1
            defs.percent_complete = (current_file/num_files) * 0.33
            while defs.confiriming_quit:
                defs.logger.debug("Awaiting responce for quit confirmation")
                time.sleep(1)
            if defs.cancel_request:
                defs.logger.debug("Cancellation requested during indexing.")
                raise SystemExit
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
    defs.logger.info("Moving files")
    for artist in music:
        while defs.confiriming_quit:
            defs.logger.debug("Awaiting responce for quit confirmation")
            time.sleep(1)
        if defs.cancel_request:
            defs.logger.info("Cancellation requested during moving files.")
            raise SystemExit
        for album in music[artist]:
            while defs.confiriming_quit:
                defs.logger.debug("Awaiting responce for quit confirmation")
                time.sleep(1)
            if defs.cancel_request:
                defs.logger.info("Cancellation requested during moving files.")
                raise SystemExit
            for track in music[artist][album]:
                current_file += 1
                defs.percent_complete += (current_file/num_files) * 0.67
                while defs.confiriming_quit:
                    defs.logger.debug("Awaiting responce for quit confirmation")
                    time.sleep(1)
                if defs.cancel_request:
                    defs.logger.info("Cancellation requested during moving files.")
                    raise SystemExit
                defs.logger.debug(f"Moving >>{track["path"].path}<< to >>{defs.basepath}\\{artist}\\{album}\\{Path(track["path"]).stem}{"".join(Path(track["path"]).suffixes)}<<")
                Path(f"{defs.basepath}\\{artist}\\{album}").mkdir(parents=True, exist_ok=True)
                replace(track["path"], f"{defs.basepath}\\{artist}\\{album}\\{Path(track["path"]).stem}{"".join(Path(track["path"]).suffixes)}")
    defs.percent_complete = 1.0

def main():
    while defs.confiriming_quit:
        defs.logger.debug("Awaiting responce for quit confirmation")
        time.sleep(1)
    if defs.cancel_request:
        defs.logger.info("Cancellation requested before starting main.")
        raise SystemExit
    start_time = time.time()
    # test timer
    # while(time.time() - start_time < 5):
    #     defs.percent_complete = random.uniform(0.0, 1.0) * 100
    #     while defs.confiriming_quit:
    #         defs.logger.debug("Awaiting responce for quit confirmation")
    #         time.sleep(1)
    #     if defs.cancel_request:
    #         defs.logger.info("Cancellation requested during test timer.")
    #         raise SystemExit
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
    while defs.confiriming_quit:
        defs.logger.debug("Awaiting responce for quit confirmation")
        time.sleep(1)
    if defs.cancel_request:
        defs.logger.info("Cancellation requested before indexing files.")
        return
    index_files()
    if defs.json:
        while defs.confiriming_quit:
            defs.logger.debug("Awaiting responce for quit confirmation")
            time.sleep(1)
        if defs.cancel_request:
            defs.logger.info("Cancellation requested before writing JSON.")
            return
        serializable_music = {
            artist: {
                album: [track["name"] for track in tracks]
                for album, tracks in albums.items()
            }
            for artist, albums in music.items()
        }
        with open(f'{defs.basepath}\\music_index.json', "wt") as f:
            json.dump(serializable_music, f, indent=2)
    while defs.confiriming_quit:
        defs.logger.debug("Awaiting responce for quit confirmation")
        time.sleep(1)
    if defs.cancel_request:
        defs.logger.info("Cancellation requested before moving files.")
        raise SystemExit
    move_files()