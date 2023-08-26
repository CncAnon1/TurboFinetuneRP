import os
import json
import glob
from modules import config

def format():
    json_dir = config.chats_folder
    output_file = config.dataset_file
    json_files = glob.glob(os.path.join(json_dir, '*.json'))

    if len(json_files) < 10:
        print("You need at least 10 chats for a fine-tune!")

    with open(output_file, 'w') as outfile:
        for json_file in json_files:
            with open(json_file, 'r') as infile:
                json_data = {"messages": json.load(infile)}
                outfile.write(json.dumps(json_data) + '\n')