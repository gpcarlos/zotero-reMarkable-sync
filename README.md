# zotero-reMarkable-sync

# TODO: Update readme

This repository allows you to synchronize all the .pdf files from your [Zotero](https://www.zotero.org) library to your [reMarkable](https://remarkable.com) device.

How does it work?
1. Download all the .pdf files from the Zotero library to a local folder `<dir-name>`
2. Synchronize the `<dir-name>` to your reMarkable `/<dir-name>` folder.


## Requirements
Tested on Python 3.6

``` bash
pip install -r requirements.txt
```
## Authorization
### reMarkable

Get a **Security Code** from https://my.remarkable.com/connect/remarkable and run ***authorize_rmapy.py***

``` bash
python authorize_rmapy.py --security-code <security-code>
```

### zotero

Get your **Zotero Library ID** and **Zotero API Key** from https://www.zotero.org/settings/keys


## Use

``` bash
python sync.py --zot-library-id <zot-library-id> --zot-api-key <zot-api-key> --directory <dir-name> [--verbose]
```

## Features
- [x] Download .pdf files from Zotero Library
- [x] Upload .pdf files to reMarkable
- [x] Keep the directory structure
- [x] Prevent duplicate uploads and downloads
- [ ] Support more file extensions like .epub
- [ ] Delete files from reMarkable if they are deleted in the Zotero library
- [ ] Update files in the Zotero Library with the reMarkable annotations


##### Thanks to @urschrei and @subutux for the fantastic APIs  
- https://github.com/urschrei/pyzotero
- https://github.com/subutux/rmapy
