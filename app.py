from flask import Flask, render_template, request, jsonify, session, Response
import csv
import random
from datetime import datetime
from user_agents import parse
import threading
app = Flask(__name__)

def shot_on_string(video_title):
    to_return = 'SHOT ON '
    if 'IMG_' in video_title:
        to_return += 'iPHONE'
    elif '100-' in video_title:
        to_return += 'CANON'
    elif '101-' in video_title:
        to_return += 'CANON'
    elif 'MVI' in video_title:
        to_return += 'CANON'
    elif 'DSCN' in video_title:
        to_return += 'NIKON'
    elif 'CIMG' in video_title:
        to_return += 'CASIO'
    elif 'DSCF' in video_title:
        to_return += 'FUJI'
    elif 'GX01' in video_title:
        to_return += 'GOPRO'
    elif 'GH01' in video_title:
        to_return += 'GOPRO'
    elif 'HPIM' in video_title:
        to_return += 'HP'
    elif 'DCP_' in video_title:
        to_return += 'KODAK'
    elif '102_' in video_title:
        to_return += 'KODAK'
    elif 'DCM' in video_title:
        to_return += 'NOKIA'
    elif 'Pmdd' in video_title:
        to_return += 'PANASONIC'
    elif 'SANY' in video_title:
        to_return += 'SANYO'
    else:
        to_return = ""
    return to_return

def update_viewcounts(youtube_video_url,youtube_videos_to_choose_from):
    read_file_successfully = False
    try:
        with open('numvidsstreamed','r',encoding='utf-8') as infile:
            numvidsstreamed = str(int(infile.read())+1)
            read_file_successfully = True
    except:
        pass
    if read_file_successfully:
        with open('numvidsstreamed','w',encoding='utf-8') as outfile:
            outfile.write(numvidsstreamed)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

def user_video_uri_history(youtube_video_url_local):
    uri = youtube_video_url_local.split('?')[0].split('/')[-1]
    if 'history' not in session:
        session['history'] = []
    session['history'] = session['history'][max(-9,-1*len(session['history'])):]
    session['history'].append(uri)

@app.route('/index',methods=['GET','POST'])
def index():
    try:
        youtube_video_url = random.choice(list(youtube_videos_to_choose_from.keys()))
    except:
        globals()['youtube_videos_to_choose_from'] = load_videos()
        youtube_video_url = random.choice(list(youtube_videos_to_choose_from.keys()))
    threading.Thread(target=update_viewcounts,args=(youtube_video_url,youtube_videos_to_choose_from),daemon=True).start()
    yvu = youtube_video_url
    user_video_uri_history(yvu)
    if parse(request.user_agent.string).is_mobile:
        yvu = youtube_video_url.replace('mute=0','mute=1')
    return render_template('index.html',
    youtube_video_url=yvu,
    page_title=youtube_videos_to_choose_from[youtube_video_url]['title'],
    video_duration=int(youtube_videos_to_choose_from[youtube_video_url]['duration']),
    view_count=youtube_videos_to_choose_from[youtube_video_url]['view_count'],
    upload_date=youtube_videos_to_choose_from[youtube_video_url]['upload_date'],
    shot_on=shot_on_string(youtube_videos_to_choose_from[youtube_video_url]['title']),
    video_history=reversed(session.get('history',[])))

@app.route('/old',methods=['GET','POST'])
def old():
    try:
        youtube_video_url = random.choice(list(youtube_videos_to_choose_from.keys()))
        if int(youtube_videos_to_choose_from[youtube_video_url]['upload_date'][-4:])>2010:
            raise
    except:
        globals()['youtube_videos_to_choose_from'] = load_videos(year_max=2010)
        youtube_video_url = random.choice(list(youtube_videos_to_choose_from.keys()))
    threading.Thread(target=update_viewcounts,args=(youtube_video_url,youtube_videos_to_choose_from),daemon=True).start()
    yvu = youtube_video_url
    user_video_uri_history(yvu)
    if parse(request.user_agent.string).is_mobile:
        yvu = youtube_video_url.replace('mute=0','mute=1')
    return render_template('index.html',
    youtube_video_url=yvu,
    page_title=youtube_videos_to_choose_from[youtube_video_url]['title'],
    video_duration=int(youtube_videos_to_choose_from[youtube_video_url]['duration']),
    view_count=youtube_videos_to_choose_from[youtube_video_url]['view_count'],
    upload_date=youtube_videos_to_choose_from[youtube_video_url]['upload_date'],
    shot_on=shot_on_string(youtube_videos_to_choose_from[youtube_video_url]['title']),
    video_history=reversed(session.get('history',[])))

@app.route('/robots.txt')
def robots_txt():    
    return """User-agent: *
    Disallow: /admin
    Allow: /"""

@app.route('/')
def home():
    globals()['youtube_videos_to_choose_from'] = load_videos()
    media_urls = sorted([
    'https://wired.com/story/the-website-of-old-youtube-clips-that-feels-like-a-gut-punch',
    'https://theverge.com/2024/11/19/24300866/img-0001-old-youtube-video-randomizer',
    'https://gigazine.net/gsc_news/en/20241205-youtube-iphone-img-0001',
    'https://washingtonpost.com/technology/2024/11/29/youtube-nostalgia-home-videos',
    'https://mashable.com/article/candid-youtube-video-random-generator',
    'https://yahoo.com/lifestyle/love-nostalgic-vibes-youtube-time-070000016.html',
    'https://mentalfloss.com/iphone-video-time-capsule',
    'https://newyorker.com/culture/infinite-scroll/the-artist-exposing-the-data-we-leave-online',
    'https://finestresullarte.info/en/contemporary-art/does-art-anticipate-science-luca-rossi-s-artistic-intuition-becomes-software',
    ])
    return render_template('home.html',num_videos_indexed = len(youtube_videos_to_choose_from.keys()),media_urls=media_urls,numvidsstreamed=int(open('numvidsstreamed','r',encoding='utf-8').read()))

def yt_embed_url(original_url): 
    return original_url.replace('/watch?v=','/embed/').replace('/shorts/','/embed/')+'?autoplay=1&mute=0&enablejsapi=1&iv_load_policy=3&controls=0&showinfo=0&modestbranding=1&rel=0&autohide=1&fs=1&playsinline=1&color=blue&origin=https://www.0001.site'

def load_videos(year_min=2000,year_max=3000):
    to_return = dict()
    with open('yturls.csv','r',encoding='utf-8') as infile:
        reader = csv.reader(infile,delimiter=',')
        for line in reader:
            if len(line[2])>3 or int(line[4])>=15 or int(line[3][:4])<year_min or int(line[3][:4])>year_max:
                continue
            to_return[yt_embed_url(line[0])] = {'url':line[0],'title':line[1],'view_count':line[2],'upload_date':datetime.strptime(line[3],"%Y%m%d").strftime('%B %d, %Y') if len(line[3])>0 else 'UNKNOWN DATE','duration':line[4]}
    return to_return

if __name__ == '__main__':
    global youtube_videos_to_choose_from
    app.run(debug=False)