from flask import Flask, render_template, send_file, request
from ftplib import FTP, error_perm
from io import BytesIO

app = Flask(__name__)

FTP_HOST = "117.240.136.5"
FTP_USER = "anonymous"
FTP_PASS = ""

def list_ftp_dir(path):
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(path)

    entries = []

    filenames = ftp.nlst()
    for name in filenames:
        full_path = f"{path}/{name}".replace("//", "/")
        try:
            ftp.cwd(full_path)  # Try to enter it
            is_dir = True
            ftp.cwd(path)  # Go back to original dir
        except error_perm:
            is_dir = False
        entries.append({"name": name, "is_dir": is_dir})
    ftp.quit()
    return entries

def download_ftp_file(file_path):
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)

    memory_file = BytesIO()
    ftp.retrbinary(f"RETR {file_path}", memory_file.write)
    ftp.quit()
    memory_file.seek(0)
    return memory_file

@app.route("/")
@app.route("/browse")
@app.route("/browse/<path:subpath>")
def browse(subpath=""):
    current_path = f"/{subpath}" if subpath else "/"
    items = list_ftp_dir(current_path)

    parent_path = None
    if subpath:
        parent_path = '/'.join(subpath.strip('/').split('/')[:-1])

    return render_template(
        "index.html",
        items=items,
        current_path=subpath,
        parent_path=parent_path
    )

@app.route("/download/<path:file_path>")
def download(file_path):
    try:
        file_data = download_ftp_file(f"/{file_path}")
        filename = file_path.split("/")[-1]
        return send_file(file_data, download_name=filename, as_attachment=True)
    except error_perm as e:
        return f"Error: {e}", 404

if __name__ == "__main__":
    app.run(debug=True)