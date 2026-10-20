#!/usr/bin/env python3
"""Copy the Windows install screenshots used by part1/installing.md into documentation/docs/img/windows/.

    .venv/bin/python tools/figures/installing_windows_shots.py

Sources are the redacted captures in screenshots-raw/windows/ (taken in the Windows 11 VM by the
rusefi-docs-windows skill). The EFI Analytics download page is cropped to the page content so the
browser toolbar and the "Activate Windows" watermark are left out. Re-run after re-shooting.
"""
import pathlib
import shutil

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "screenshots-raw" / "windows"
OUT = ROOT / "documentation" / "docs" / "img" / "windows"

COPY = {
    "win-ts-01-uac.png": "installing-ts-uac.png",
    "win-ts-02-license.png": "installing-ts-license.png",
    "win-ts-03-destination.png": "installing-ts-destination.png",
    "win-ts-05-tasks.png": "installing-ts-tasks.png",
    "win-ts-08-finish.png": "installing-ts-finish.png",
    "win-ts-09-first-start-lite.png": "installing-ts-lite.png",
    "win-ts-10-registration-empty.png": "installing-ts-registration.png",
    "win-ts-11-registration-restart.png": "installing-ts-restart.png",
    "win-ts-12-registered.png": "installing-ts-registered.png",
    "win-mlv-03-information.png": "installing-mlv-information.png",
    "win-mlv-07-ready.png": "installing-mlv-ready.png",
    "win-mlv-09-update-offer.png": "installing-mlv-update.png",
    "win-mlv-10-first-start-lite.png": "installing-mlv-lite.png",
    "win-mlv-11-registration-otc.png": "installing-mlv-registration-otc.png",
    "win-mlv-12-registration-manual-empty.png": "installing-mlv-registration-manual.png",
    "win-mlv-14-look-and-feel.png": "installing-mlv-look.png",
    "win-mlv-15-registered.png": "installing-mlv-registered.png",
}
# (left, top, right, bottom) in pixels of the 1580x890 browser capture
DOWNLOAD_PAGE_CROP = (140, 145, 1278, 890)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for src, dst in COPY.items():
        shutil.copyfile(RAW / src, OUT / dst)
    Image.open(RAW / "win-ts-download-page.png").crop(DOWNLOAD_PAGE_CROP).save(OUT / "installing-efia-downloads.png")
    print(f"{len(COPY) + 1} images written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
