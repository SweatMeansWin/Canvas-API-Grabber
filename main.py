"""
SweatMeansWin
Get data from Canvas and save to Google SpreadSheets
"""
import datetime
from canvas_utils import CanvasInfoLoader


if __name__ == "__main__":
    print("Updating info {!s}".format(datetime.datetime.now()))
    CanvasInfoLoader().update_info()
