from ftplib import FTP
from pathlib import Path
import xml.etree.ElementTree as ET
from io import BytesIO

FTP_HOST = "ftp.bom.gov.au"
FTP_DIR = "/anon/gen/fwo"

FILES = [
    "IDS11068.xml",
    "IDS11068.amoc.xml",
    "IDS11068.pdf",
]


def get_issue_time(xml_bytes):
    """Extract issue-time-utc from XML"""
    root = ET.fromstring(xml_bytes)
    issue_time = root.find(".//issue-time-utc").text
    issue_time = issue_time.replace(":", "").replace("-", "")
    return issue_time


def download_file(ftp, filename):
    """Download file from FTP and return bytes"""
    buffer = BytesIO()
    ftp.retrbinary(f"RETR {filename}", buffer.write)
    return buffer.getvalue()


def main():

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    ftp = FTP(FTP_HOST)
    ftp.login("anonymous", "test@example.com")
    ftp.cwd(FTP_DIR)

    files = ftp.nlst()
    print("Files:", files)

    # ---- download main XML first (needed to get issue time)
    xml_filename = "IDS11068.xml"

    if xml_filename not in files:
        print("Main XML file not found!")
        return

    xml_data = download_file(ftp, xml_filename)

    issue_time = get_issue_time(xml_data)
    print("Issue time:", issue_time)

    # save main XML
    xml_save = out_dir / f"IDS11068_{issue_time}.xml"
    xml_save.write_bytes(xml_data)
    print("Saved:", xml_save)

    # ---- download remaining files
    for fname in FILES:

        if fname == xml_filename:
            continue

        if fname not in files:
            print(f"{fname} not found on FTP")
            continue

        data = download_file(ftp, fname)

        suffix = fname.replace("IDS11068", "")
        save_name = out_dir / f"IDS11068_{issue_time}{suffix}"

        save_name.write_bytes(data)

        print("Saved:", save_name)

    ftp.quit()

    print("Download complete")


if __name__ == "__main__":
    main()