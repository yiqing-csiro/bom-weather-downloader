from ftplib import FTP
from pathlib import Path
import xml.etree.ElementTree as ET
from io import BytesIO
import re

FTP_HOST = "ftp.bom.gov.au"
FTP_DIR = "/anon/gen/fwo"


def extract_issue_time(xml_bytes):
    """Extract issue-time-utc from XML"""
    root = ET.fromstring(xml_bytes)
    issue_time = root.find(".//issue-time-utc").text
    return issue_time.replace(":", "").replace("-", "")


def download_bytes(ftp, filename):
    """Download file from FTP and return bytes"""
    buffer = BytesIO()
    ftp.retrbinary(f"RETR {filename}", buffer.write)
    return buffer.getvalue()


def main():

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    ftp = FTP(FTP_HOST)
    ftp.login("anonymous", "test@example.com")
    ftp.cwd(FTP_DIR)

    ftp_files = ftp.nlst()
    print(f"Total files on FTP: {len(ftp_files)}")

    # Match IDS files
    pattern = re.compile(r"^(IDS\d+).*\.(xml|pdf)$")

    grouped_files = {}

    for f in ftp_files:
        m = pattern.match(f)
        if m:
            product_id = m.group(1)
            grouped_files.setdefault(product_id, []).append(f)

    print(f"Found {len(grouped_files)} IDS products")

    for product_id, files in grouped_files.items():

        print(f"\nProcessing {product_id}")

        main_xml = f"{product_id}.xml"

        if main_xml not in files:
            print(f"No main XML for {product_id}")
            continue

        product_dir = output_dir / product_id
        product_dir.mkdir(exist_ok=True)

        # download main XML
        xml_data = download_bytes(ftp, main_xml)

        try:
            issue_time = extract_issue_time(xml_data)
        except Exception:
            print("Failed to extract issue time")
            continue

        print("Issue time:", issue_time)

        # save main XML
        xml_save = product_dir / f"{product_id}_{issue_time}.xml"
        xml_save.write_bytes(xml_data)
        print("Saved:", xml_save)

        # download remaining files
        for filename in files:

            if filename == main_xml:
                continue

            try:
                data = download_bytes(ftp, filename)
            except Exception as e:
                print("Download failed:", filename, e)
                continue

            suffix = filename.replace(product_id, "")
            save_path = product_dir / f"{product_id}_{issue_time}{suffix}"

            save_path.write_bytes(data)
            print("Saved:", save_path)

    ftp.quit()

    print("\nDownload complete")


if __name__ == "__main__":
    main()