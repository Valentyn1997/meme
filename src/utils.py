def dropbox_download(url, dest_path):
    import urllib.request
    u = urllib.request.urlopen(url)
    data = u.read()
    u.close()

    with open([filename], "wb") as f:
        f.write(data)

    # url = "https://www.dropbox.com/[something]/[filename]?dl=1"  # dl=1 is important


