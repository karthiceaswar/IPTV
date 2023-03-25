import argparse
import requests
from tqdm import tqdm
import os
import ntpath

def read_m3u(file_name):
    """
    Reads an m3u file and returns a list of tuples containing the channel name and URL
    """
    channels = []
    with open(file_name, 'r') as f:
        for line in f:
            if line.startswith('#EXTINF:'):
                name = line.split(',')[-1].strip()
            elif not line.startswith('#'):
                url = line.strip()
                channels.append((name, url))
    return channels

def check_channel(url):
    """
    Checks if a given URL is a working stream by making a HEAD request and checking the response code
    """
    try:
        response = requests.head(url, timeout=5)
        if response.status_code < 400:
            return True
        else:
            return False
    except:
        return False

parser = argparse.ArgumentParser(description='Check working channels in an IPTV playlist.')
parser.add_argument('file_1_url', metavar='file_1_url', type=str, help='URL to download the first m3u file')

args = parser.parse_args()

file_name_1 = os.path.splitext(ntpath.basename(args.file_1_url))[0]
file_name_2 = 'eng.m3u'

# download file_1
response = requests.get(args.file_1_url)
with open(file_name_1 + '.m3u', 'wb') as f:
    f.write(response.content)

# read channels from both files
channels_1 = read_m3u(file_name_1 + '.m3u')
channels_2 = read_m3u(file_name_2)

# get common channels
common_channels = []
for channel_1 in channels_1:
    for channel_2 in channels_2:
        if channel_1[1] == channel_2[1]:
            common_channels.append(channel_1)

# check working channels
working_channels = []
for channel in tqdm(common_channels, desc="Checking channels"):
    if check_channel(channel[1]):
        working_channels.append(channel)

# write working channels to file
output_file_name = f"working_channels_english_{file_name_1}.m3u"
with open(output_file_name, 'w') as f:
    f.write('#EXTM3U\n')
    for channel in working_channels:
        f.write('#EXTINF:-1,' + channel[0] + '\n')
        f.write(channel[1] + '\n')

# delete temp files
os.remove(file_name_1 + '.m3u')

print('Total channels in', file_name_1 + '.m3u:', len(channels_1))
print('Total channels in', file_name_2 + ':', len(channels_2))
print('Common channels:', len(common_channels))
print('Working channels:', len(working_channels))
print('Output file:', output_file_name)
