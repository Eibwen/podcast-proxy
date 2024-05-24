import requests
import xml.etree.ElementTree as ET
from pathlib import Path

import os
import zstandard as zstd

ITEMS_TO_KEEP = 14

feedsToProxy = [
    "https://feeds.simplecast.com/bOogzwqU"
]


def ProcessUrl(url):
	# TODO make sure this has any gzip headers enabled?
	f = DownloadFile(url)

	print("Original File: ", get_file_sizes(f))

	tree = ET.parse(f)
	root = tree.getroot()

	channelRoot = root.find('channel')
	items = channelRoot.findall('item')

	itemsToRemove = items[ITEMS_TO_KEEP:]

	for item in itemsToRemove:
		# print(item.find('title').text)
		channelRoot.remove(item)

	outputItems = channelRoot.findall('item')
	print('Output items len: ', len(outputItems))

	outFile = Path(f).with_suffix('.proxy.xml')
	tree.write(outFile)

	print("Proxy file: ", get_file_sizes(outFile))

	print('DONE')


def DownloadFile(url):
    local_filename = url.split('/')[-1] + '.xml'
    r = requests.get(url)
    # print(r.headers)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename


def get_file_sizes(file_path):
    # Get the uncompressed size using os.path.getsize()
    uncompressed_size = os.path.getsize(file_path)
 
    # Get the compressed size using zstandard
    with open(file_path, 'rb') as file:
        compressed_data = zstd.compress(file.read())
        compressed_size = len(compressed_data)
 
    return {
        "Uncompressed": uncompressed_size,
        "Compressed": compressed_size,
        "Percentage": compressed_size*100/uncompressed_size
    }


for url in feedsToProxy:
    ProcessUrl(url)
