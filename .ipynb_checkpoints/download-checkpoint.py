from ftplib import FTP
from pathlib import Path

# ftp = FTP("ftp.bom.gov.au")
# ftp.login("anonymous", "test@example.com")

# ftp.cwd("/anon/gen/fwo")

# print(ftp.nlst())   # 列出目录文件

FTP_HOST = "ftp.bom.gov.au"
FTP_DIR = "/anon/gen/fwo"
FILENAME = "IDD10112.amoc.xml"

def main():
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    out_file = out_dir / FILENAME

    ftp = FTP(FTP_HOST, timeout=60)
    ftp.login("anonymous", "your_email@example.com")
    ftp.cwd(FTP_DIR)

    with open(out_file, "wb") as f:
        ftp.retrbinary(f"RETR {FILENAME}", f.write)

    ftp.quit()
    print(f"Downloaded to {out_file}")

if __name__ == "__main__":
    main()