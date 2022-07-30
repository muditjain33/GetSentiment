from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

from GetSentiment.settings import SECRET_KEY
from .models import emailmodel
from numpy.core.fromnumeric import size
from django.core.mail import send_mail
from . import preprocessing
api_key = ''
# Create your views here.


def get_yt_video_id(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """

    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    else:
        raise ValueError


def coments(video_id):

    # creating youtube resource object
    youtube = build('youtube', 'v3',
                    developerKey=api_key)

    # retrieve youtube video results
    video_response = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id
    ).execute()
    # print(video_response)
    yt_corpus1 = []
    yt_corpus1weights = []
    while True:
        for i in video_response['items']:
            yt_corpus1.append(i['snippet']["topLevelComment"]
                              ["snippet"]["textOriginal"])
            yt_corpus1weights.append(
                i['snippet']["topLevelComment"]["snippet"]["likeCount"])

        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id
            ).execute()
        else:
            break

        if(len(yt_corpus1) > 500):
            break
    return yt_corpus1, yt_corpus1weights


def index(request):
    if(request.method == "POST" and 'urle' in request.POST):
        url = request.POST.get('url', default="Nhi_Milla")
        if(url != "Nhi_Milla"):
            url = get_yt_video_id(url)
            yt1, yt1_likes = coments(url)
            yt1 = preprocessing.preprocessing(yt1)
            yt1 = preprocessing.preprocessing2(yt1)
            yt1 = preprocessing.preprocessing3(yt1)
            yt1 = preprocessing.predictionfrommodel(yt1)
            sizze = len(yt1)
            pos = 0
            neg = 0
            for i in range(0, sizze):
                if(yt1[i] == 0):
                    pos += (1+yt1_likes[i]/4)
                elif(yt1[i] == 1):
                    neg += (1+yt1_likes[i]/4)
            temp = pos
            pos = pos/(pos+neg)*100
            neg = neg/(neg+temp)*100
            pos = round(pos, 2)
            neg = round(neg, 2)
        return render(request, "sentiment/index.html", {"pos": pos, "neg": neg, "a": '0', "b": '1'})
    elif(request.method == 'POST' and 'emaile' in request.POST):
        cemail = request.POST['emaili']
        send_mail(
            "Welcome to there family",
            "GetSentiment is a sentiment analysis web app based on machine learning algorithm which helps users to get the ability to decide whether to watch a YouTube video or not. It reads topmost comments from a video and apply the algorithm which is trained on multiple datasets like IMDB , Twitter Tweets Sentiment and various independent datasets. Concluding , it helps user get back their dislike counter through comments.",
            "getsentiments.email@gmail.com",
            [cemail],
        )
        emailmodel(email=cemail).save()
        return render(request, "sentiment/index.html", {"pos": 0, "neg": 0, "a": '1', "b": '0'})
    else:
        return render(request, "sentiment/index.html", {"pos": 0, "neg": 0, "a": '1', "b": '1'})


def emailing(request):
    if(request.method == 'POST'):
        secret = request.POST['secretkey']
        subject = request.POST['subject']
        message = request.POST['message']
        if(secret == "KOIVEna123@"):
            obs = emailmodel.objects.all()
            l = []
            for i in obs:
                l.append(i.email)
            send_mail(
                subject,
                message,
                "getsentiments.email@gmail.com",
                l,
            )
        return render(request, "sentiment/emailing.html", {"pos": 0, "neg": 0, "a": '1', "b": '0'})
    else:
        return render(request, "sentiment/emailing.html", {"pos": 0, "neg": 0, "a": '1', "b": '1'})
