import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from pipeline import process_catalog_image
from exporter import export_to_excel

WATCH_FOLDER = "input"
VALID_EXTENSIONS = (".png", ".jpg", ".jpeg")


class CatalogHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        if not filepath.lower().endswith(VALID_EXTENSIONS):
            return

        print(f"\nNew file detected: {filepath}")
        time.sleep(1)

        try:
            results = process_catalog_image(filepath)
            filename = os.path.splitext(os.path.basename(filepath))[0]
            output_path = f"output/{filename}_output.xlsx"
            export_to_excel(results, output_path)
        except Exception as e:
            print(f"Could not process '{filepath}': {e}")
            print("Skipping this file and continuing to watch for new ones.")


if __name__ == "__main__":
    os.makedirs(WATCH_FOLDER, exist_ok=True)

    event_handler = CatalogHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    print(f"Watching '{WATCH_FOLDER}/' for new catalog images... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()