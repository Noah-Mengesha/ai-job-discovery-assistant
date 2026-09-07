import time, logging
from discovery import run_once, config
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(message)s")
if __name__=="__main__":
    while True:
        try: logging.info("Discovery: %s",run_once())
        except Exception: logging.exception("Discovery failed")
        time.sleep(max(1,int(config().get("interval_hours",3)))*3600)
