#!/home/qq/Applications/miniconda3/bin/python

from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.widgets import RadioList, Label, SearchToolbar
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.shortcuts import print_formatted_text, prompt, clear
from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition

import subprocess
import argparse
import json
import re
import time
import requests

sub_el = re.compile(r'\|')


def check_network():
    try:
        # send a request to google.com
        requests.get('https://www.google.com')
        return True
    except:
        return False


def run_video(video_player: str, result) -> None:
    video_player = video_player.split(' ')
    video_player.append(result)
    subprocess.run(video_player)


def row_formater(row,separator):
    return (row[-2], separator.join([row[0],row[1],row[2]]))


def radiolist_dialog(title='', values=None, style=None, async_=False):
    # Add exit key binding.
    bindings = KeyBindings()
    @bindings.add('c-d')
    def exit_(event):
        """
        Pressing Ctrl-d will exit the user interface.
        """
        event.app.exit()    
    @bindings.add('c-a')
    def exit_with_value(event):
        """
        Pressing Ctrl-a will exit the user interface returning the selected value.
        """
        event.app.exit(result=radio_list.current_value)   

    radio_list = RadioList(values)
    application = Application(
        layout=Layout(HSplit([ Label(title), radio_list])),
        key_bindings=merge_key_bindings(
            [load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,        
        full_screen=False)

    if async_:
        return application.run_async()
    else:
        return application.run()
    

def json_parse(item, domain="https://watch.whatever.social"):
    if item.get('type') == "channel":
        creator_name = item.get('name')
        description = item.get('description')
        creator_url = item.get('url')
        return (creator_name,description,'',domain+creator_url,'')
    creator_name = item.get('uploaderName')
    title = sub_el.sub('', item.get('title')).lower()
    duration_time = str(round(item.get('duration') / 60,1))+'min'
    publish_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(item.get('uploaded') // 1000))
    video_url = item.get('url')
    creator_url = item.get('uploaderUrl')
    return (creator_name,title,duration_time,publish_time,domain+video_url,domain+creator_url)


def parse_piped_feed(domain,separator, video_player):
    token = prompt('your token > ', default='7c7b9f5a-6018-4a59-9361-d28beb5754a1')
    data = requests.get(f'https://{domain}/feed?authToken='+token)
    videos = []
    for item in json.loads(data.content):
        row = json_parse(item)
        videos.append(row_formater(row,separator))
    
    while True:
        result = radiolist_dialog(
            title='Choose a video:',
            values=videos
        )

        if result is None:
            return print("End program")
        
        run_video(video_player, result)
        clear()

    return


def parse_piped_search(domain, separator, video_player):
    search_query = prompt('what we would search? > ')
    data = requests.get(f'https://{domain}/search?q={search_query}&filter=all')
    json_data = json.loads(data.content)
    next_page_data = json_data.get('nextpage')
    videos = []
    videos.append(('next-page', 'next page'))
    for item in json_data.get('items'):
        row = json_parse(item)
        videos.append(row_formater(row,separator))
    
    while True:
        result = radiolist_dialog(
            title='Choose a video:',
            values=videos
        )
        
        if result == 'next-page':
            escaped_string = requests.utils.quote(str(next_page_data))
            data = requests.get(f'https://{domain}/nextpage/search?nextpage={escaped_string}&q={search_query}&filter=all')
            json_data = json.loads(data.content)
            next_page_data = json_data.get('nextpage')
            for item in json_data.get('items'):
                row = json_parse(item)
                videos.append(row_formater(row,separator))
            continue
           

        if result is None:
            return print("End program")
        
        run_video(video_player, result)
        clear()
    
    return videos


def parse_piped_channel(domain, separator, video_player):
    
    with open('/home/qq/Documents/Programming/Scripts/text-piped-cli/channels-json') as f:
        channel_json = json.load(f)

    channel_list = []
    for item in channel_json.get('subscriptions'):
        id = re.sub(r'https:\/\/www\.youtube\.com\/channel\/', '', item.get('url'))
        channel_list.append((id,item.get('name')))

    channel_id = radiolist_dialog(
        title='Choose channel:',
        values=channel_list)
    
    data = requests.get(f'https://{domain}/channel/{channel_id}')
    json_data = json.loads(data.content)
    next_page_data = json_data.get('nextpage')
    videos = []
    videos.append(('choose-channel', 'choose channel'))
    videos.append(('next-page', 'next page'))
    for item in json_data.get('relatedStreams'):
        row = json_parse(item)
        videos.append(row_formater(row,separator))

    while True:
        result = radiolist_dialog(
            title='Choose a video:',
            values=videos
        )

        if result == 'choose-channel':
            channel_id = radiolist_dialog(
                title='Choose channel:',
                values=channel_list
            )
            data = requests.get(f'https://{domain}/channel/{channel_id}')
            json_data = json.loads(data.content)
            videos = []
            videos.append(('choose-channel', 'choose channel'))
            videos.append(('next-page', 'next page'))
            for item in json_data.get('relatedStreams'):
                row = json_parse(item)
                videos.append(row_formater(row,separator))
            continue

        if result == 'next-page':
            escaped_string = requests.utils.quote(str(next_page_data))
            data = requests.get(f'https://{domain}/nextpage/channel/{channel_id}?nextpage={escaped_string}')
            json_data = json.loads(data.content)
            next_page_data = json_data.get('nextpage')
            for item in json_data.get('relatedStreams'):
                row = json_parse(item)
                videos.append(row_formater(row,separator))
            continue
           

        if result is None:
            return print("End program")
        
        run_video(video_player, result)
        clear()
    
    return videos


func_dict = {
    "feed": parse_piped_feed,
    "search": parse_piped_search,
    "channel": parse_piped_channel,
}

def main():
    if not check_network():
        return print("Don't have ethernet")
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--domain",
        choices=['watchapi.whatever.social', 'piped.kavin.rocks'],
        help="domain of piped to use", 
        required=False
    )
    parser.add_argument(
        "-m", "--mode",
        default='none',
        choices=['feed', 'search', 'channel'],
        help="in which mode to run the parser. You can use: ['feed', 'search', 'channel']",
        required=False
    )
    parser.add_argument(
        "-v", "--video-player",
        help="player with/withour parameters",
        default='mpv',
        required=False
    )
    parser.add_argument(
        "-s", "--separator",
        default=' | ',
        help="which separator to use"
    )
    args = parser.parse_args()
    

    # if not args.domain:
    #     args.domain = radiolist_dialog(
    #         title='Choose domain:',
    #         values=[
    #             ('watchapi.whatever.social','watchapi.whatever.social'),
    #             ('piped.kavin.rocks','piped.kavin.rocks'),
    #         ])
    
    # if not args.mode:
    #     args.mode = radiolist_dialog(
    #         title='Choose mode:',
    #         values=[
    #             ('feed','feed'),
    #             ('search','search'),
    #             ('channel','channel'),
    #         ])

    choosed_func = func_dict.get(args.mode)
    choosed_func(domain=args.domain, separator=args.separator, video_player=args.video_player)

    # while True:
    #     result = radiolist_dialog(
    #         title='Choose a video:',
    #         values=choosed_func(domain=args.domain, separator=args.separator))

    #     if result is None:

    #     subprocess.run(['mpv', result])

if __name__ == '__main__':
    main()