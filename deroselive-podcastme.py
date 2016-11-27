"""
Programa para gerar podcast
Autor: Daniel Cambria
Criado: 2016-09-02


Atualizado: 2016-11-26
- Funciona com gravação dentro do Google Drive
- Organizado diretório de vinhetas

"""
from __future__ import unicode_literals
from ffmpy import FFmpeg
import youtube_dl
import datetime
import os
import re
import os

class MyLogger(object):
    def debug(self, msg):
        pass
        
    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('\nDone downloading, now converting...\n')

# set default writing path in $HOME
rootpath = os.path.expanduser('~/Google Drive/Podcasts/') # can't start with '/'!

# set new directory
print('Welcome, Dan!\nThese were the last directories: \n')
os.system('cd "'+ rootpath +'" && ls -FdC *-*-*')

while True:
    today = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month,datetime.datetime.now().day).isoformat()
    set_newdir = input('\nPreparing to create directory. Hit ENTER for Today (%s)\nOr enter custom date (aaaa-mm-dd): ' % today)
    
    if re.match("(^20(1[6-9])|(2[0-9])-([0][1-9]|[1][0-2])-[0-3][0-9]$)", set_newdir):
        new_dir = set_newdir        
        break
    elif set_newdir == '':
        new_dir = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month,datetime.datetime.now().day).isoformat()
        break
    else:
        print ('\n'+10*'*'+' Try again\n')   
print('\n...Directory name set "%s"\n' % new_dir)


# set default audio files for podcast concatenations
savepath  = rootpath + new_dir + '/'
cta_intro = rootpath + 'vinhetas/CTA_intro.mp3'
cta_start = cta_intro
cta_fb1   = rootpath + 'vinhetas/CTA_CompartilhePodcast+FanpageFacebook_op1.mp3' #1
cta_fb2   = rootpath + 'vinhetas/CTA_CompartilhePodcast+FanpageFacebook_op2.mp3' #2
cta_blog  = rootpath + 'vinhetas/CTA_Blog.mp3'                                   #3
cta_yt1   = rootpath + 'vinhetas/CTA_Compartilhe+Youtube_op2.mp3'                #4
cta_yt2   = rootpath + 'vinhetas/CTA_CompartilhePodcast+Youtube_op1.mp3'         #5
cta_end   = cta_fb1
 
'''
ydl_opts_reserva = { # baixa mp4, mp3 e jpg                      
    'keepvideo': True, 
    'writethumbnail': True,
    'format': 'mp4',
    'postprocessors':[
#        {'key': 'EmbedThumbnail'},   
        {        
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        },    
    ],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'outtmpl': savepath+'%(title)s-%(id)s.%(ext)s',  
}
'''
def go_yt():
    global video_title 
    global video_id  
    global video_ext
    print('\n...Creating new directory as "%s"' % savepath)
    os.makedirs(savepath, exist_ok=True) # cria pasta para salvar novos arquivos
    os.system('open "'+savepath+'"')
    print('\n...Downloading content...')    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        video_title = info.get('title', None)
        video_id = info.get('id', None)
        video_ext = info.get('ext', None)
        
        print("TÍTULO = ", video_title) 
        print('MESSAGE: ☞ Inscreva-se no nosso canal www.youtube.com/metododerose')
        print("ARQUIVO = %s-%s.%s (audio files are converted to .mp3)" % (video_title,video_id,video_ext))
        print('Done!')
        

def build_podcast():
    # cta select
    while True:
        cta_start = cta_intro
        print('''
Choose final CTA message to merge:
        (1) - FB1
        (2) - FB2
        (3) - Blog
        (4) - YT1
        (5) - YT2''')    
        cta_end = str(input('->'+'CTA (1-5) '))
        if cta_end == '1':
            cta_end = cta_fb1
            break
        elif cta_end == '2':
            cta_end = cta_fb2
            break
        elif cta_end == '3':
            cta_end = cta_blog
            break
        elif cta_end == '4':
            cta_end = cta_yt1
            break
        elif cta_end == '5':
            cta_end = cta_yt2
            break
        else:
            print('Try again')
    # build raw .mp3 and .jpg filename (downloaded from youtube)
    mp3_raw = savepath + video_title + "-" + video_id + ".mp3"
    jpg_raw = savepath + video_title + "-" + video_id + ".jpg"

    # create output .mp3 filename
    mp3_raw_normalized = savepath + video_title + "-" + video_id + '-normalized' + '.mp3'
    mp3_output = savepath + '#' + podcast_number + ' - ' + video_title + "-" + video_id + '-podcast' + '.mp3'

# build ffmpeg command
    # (detectar o volume máximo e aumentar o ganho em dB)

    # volume detect. As: ffmpeg -i normal.mp3 -af "volumedetect" -f null /dev/null 
    FFmpeg(
        inputs={mp3_raw:[]},
        outputs={None: '-af "volumedetect" -f null /dev/null'}
    ).run()
    
    # increase volume manually. As: ffmpeg -i normal.mp3 -af "volume=8.4dB" output.mp3
    db = input('Look at the max_volume. Set the difference in dB to normalize to 0dB: ')
    FFmpeg(
        inputs={mp3_raw:[]},
        outputs={mp3_raw_normalized: '-af "volume='+str(db)+'dB"'}
    ).run()

    # concatenate to podcast file
    FFmpeg(
        inputs={'concat:'+ cta_start +'|'+ mp3_raw_normalized +'|'+ cta_end:[],
                jpg_raw:[]                
                },
        outputs={mp3_output: '-map 0 -map 1 -acodec copy'}
    ).run()
    
    print('\nRemoving old raws .mp3 to avoid duplicates...\n')
    os.remove(mp3_raw)
    os.remove(mp3_raw_normalized)
    print('\nConcatenation done! New Podcast created in \n%s\n' % mp3_output)
    print('\nJob finished. Thank you!')    

while True:
    link =  input('Link YouTube: ') # 'https://youtu.be/zRTkjbF-Bc4' #
    if re.match("(.*youtu.*)", link):
        break
    print('\n...insert a valid YouTube link:\n')

def select_1():
    global ydl_opts
    ydl_opts = { # youtube-dl variables - short video for fanpage - downloads mp4 e jpg)
        'keepvideo': True,
        'writethumbnail': True,
        'format': 'mp4',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'outtmpl': savepath + '%(title)s-%(id)s.%(ext)s',  
    }
def select_2():
    global ydl_opts
    global podcast_number 
    podcast_number = input('Podcast number for title (#): ')
    ydl_opts = { # youtube-dl variables - long video to podcast - downloads .mp3 and .jpg                    
        'writethumbnail': True,
        'format': 'bestaudio',
        'postprocessors':[   
            {        
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            },   
        ],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'outtmpl': savepath + ('%(title)s-%(id)s.%(ext)s'),  
    }

os.system('open "'+ savepath +'"')
while True:
    select = input('(1) for Fanpage files, (2) for Podcast files, (3) All: ')
    if select == '1':
        select_1()
        go_yt()
        break
    elif select == '2':
        select_2()
        go_yt()
        build_podcast()        
        break
    elif select == '3':
        select_1()
        go_yt()
        select_2()
        go_yt()
        build_podcast()        
        break        
    else:
        print('\n...try again:\n')    
    
print('\n...bye!')

print(60*'—'+'''
                         ———————————
                         CTA YOUTUBE
                         ———————————
Acompanhe meus posts diários no Facebook
➲ fb.com/derosefanpage
#derosemethod #deroselive

============================

Leia mais sobre o assunto no BLOG DO DeROSE
➲ https://wp.me/p2gk9N-3y2

Acompanhe nosso PODCAST
➲ iTunes: DeRoseCast
➲ SoundCloud: soundcloud.com/derosecast
#derosemethod #deroselive

Assista o vídeo sem cortes neste link:
                         ———————————
                         CTA PODCAST
                         ———————————
Confira nosso canal no YOUTUBE
➡ youtube.com/MetodoDeRose
#derosemethod #deroselive

Inscreva-se na nossa fanpage do FACEBOOK
➲ fb.com/derosefanpage
E tenha acesso a diversos temas relacionados ao COMPORTAMENTO e BOM RELACIONAMENTO HUMANO
#derosemethod #deroselive

v


                         ———————————
                         CTA FANPAGE
                         ———————————
➡ Inscreva-se no nosso canal www.youtube.com/metododerose
Confira nosso canal no YOUTUBE.com/metododerose e assista também esta aula completa no link
➲ xxxxxxxx
#derosemethod #deroselive

'''+60*'—')

print('''\n
REMINDERS:            On Spreadsheet: http://bit.ly/2cIz7Qh
—————————             - PASTE link podcast
                      - PASTE link blog
                      
                      On Yutube:
                      - Publish long video
                      - Publish short video  / insert link to long video

''')

'''
Next implementations:

Podcast:
- Pick last podcast # number and auto increment
- Upload new podcast

YouTube:
- Turn video published


# Shell functions

# download (show title first, then video and thumbnail)
youtube-dl youtube_filename --get-filename                          # ok
youtube-dl youtube_filename --write-thumbnail --embed-thumbnail -x  # ok

#remove silence
ffmpeg -ss 2 -i input.flv -vcodec copy -acodec copy output.flv

# converte vídeo em áudio
ffmpeg -i youtube_filename.mp4 -acodec mp3 youtube_filename.mp3

# create podcast
ffmpeg -i "concat:Intro.mp3|youtube_filename.mp3|CTA_number.mp3" -c copy 'youtube_filename-podcast.mp3'

# embed cover art
ffmpeg -i youtube_filename_podcast.mp3 -i youtube_filename.jpg -map 0 -map 1 -acodec copy youtube_filename_podcast_final.mp3


API SOUNDCLOUD

Site do seu aplicativo	
metododerose.org/secretariavirtual/podcast

URI de redirecionamento	
metododerose.org/blogdoderose/podcast

ID do cliente	ZToXVXJAEEJONfarvhG3TRrD19HpKwsN
Cliente secreto	UXk95UQ4wd29TPurOzhGnWAjNKkijgVh

'''