from docutils.core import publish_parts

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def generate(file, schedule_page="./schedule.html", talks_page="./talks.html", speakers_page="./speakers.html"):
  """"
  Read yaml data and generate all these three pages:
  - schedule_page
  - talks_page
  - speakers_page

  To three local file in the location of schedule_page, talks_page, speakers_page parameter

  Example:
  generate("talks2019.yaml")
  """

  with open(schedule_page, "w", encoding="utf8") as f:
    f.write(genone(file, schedule_page, talks_page, speakers_page, "schedule"))
  with open(talks_page, "w", encoding="utf8") as f:
    f.write(genone(file, schedule_page, talks_page, speakers_page, "talks"))
  with open(speakers_page, "w", encoding="utf8") as f:
    f.write(genone(file, schedule_page, talks_page, speakers_page, "speakers"))

def genone(file, schedule_page, talks_page, speakers_page, mode):
    """"
    Read yaml data and generate one of these page according to mode:
    - schedule_page
    - talks_page
    - speakers_page

    Return html string for that page

    Example:

    # Generate schedule page html string for local file
    genone("talks2019.yaml","./schedule.html","./talks.html","./speakers.html","schedule")

    # Generate talks page html string for nikola or site that support clean URLs
    genone("talks2019.yaml","/schedule","/talks","/speakers","talks")

    # Generate speakers page html string for nikola or site that support clean URLs
    genone("talks2019.yaml","/schedule","/talks","/speakers","speakers")

    # Generate speakers page html string for local file
    genone("talks2019.yaml","./schedule.html","./talks.html","./speakers.html","speakers")
    """

    def timeadd(a,b):
        a = list(map(int,a.split(":")))
        b = list(map(int,b.split(":")))
        c = [a[0]+b[0],a[1]+b[1]]
        if c[1]>=60:
            c[0] += c[1]//60
            c[1] %= 60
        c[0] = "%02d"%c[0]
        c[1] = "%02d"%c[1]
        return ":".join(map(str,c))



    with open(file, encoding="utf8") as f:
        data = yaml.load(f, Loader=Loader)

    talks = sorted([t for t in data['talks'] if 'day' in t],
                   key=lambda t: (t['day'], t['time'], t['dur'], t['track']))
    tracks_ = data['tracks']
    daylabel_ = data['days']

    specialid = 1
    for talk in talks:
        talk['specialid'] = specialid
        specialid += 1

    tracks = {}
    daylabel = {}

    for x in daylabel_: daylabel[list(x.keys())[0]] = list(x.values())[0]
    for x in tracks_: tracks[list(x.keys())[0]] = list(x.values())[0]
    tracks[5] = ""

    # print(daylabel)

    for talk in talks:
      talk['day'] = daylabel[talk['day']]

    # print(tracks)

    sched = []

    cur = None
    for talk in talks:
        if talk['time'] != cur:
            cur = talk['time']
            dur = talk['dur']
            day = talk['day']
            slot = dict(time=cur, dur=dur, day=day, talks=[])
            sched.append(slot)
        # now try to fit in the track
        slot['talks'].append(talk)

    # print(talks)
    # sched

    schedule = {}
    currrow = 1

    foundtrackfour = 0
    for s in sched:
      time = s['time']
      day = s['day']
      key = day+" "+time
      if not key in schedule: schedule[key] = []

      for talk in s['talks']:
        talk['row'] = currrow
        talk['col'] = 1 if talk['track'] != 4 else 2
        if 'track' in talk:
          talk['subcol'] = 5 if type(talk['track']) == list else talk['track']
          talk['colspan'] = 2 if talk['track'] == [1, 2, 3, 4] else 1
          if talk['subcol'] is None: talk['subcol'] = 5
          if talk['track'] == 4: foundtrackfour = 3
          if talk['subcol'] < 5:
            if talk['subcol'] < 4:
              talk['format'] = 'Talk'
            else:
              talk['format'] = 'Workshop'
        else:
          talk['subcol'] = 1
          talk['colspan'] = 2
        talk['time'] = time
        if talk['subcol'] is None:
          talk['subcol'] = 5
          talk['colspan'] = 2
        if not 'dur' in talk: talk['dur'] = "00:00"
        talk['timeend'] = timeadd(talk['time'], talk['dur'])
        if not 'speaker' in talk or talk['speaker'] is None: talk['speaker'] = ""
        if not 'description' in talk or talk['description'] is None: talk['description'] = ""
        if not 'bio' in talk or talk['bio'] is None: talk['bio'] = ""
        if 'twitter' not in talk: talk['twitter'] = ""
        if 'speakerimg' not in talk or str(
            talk['speakerimg']) == "None": talk['speakerimg'] = "https://secure.gravatar.com/avatar/7ebded1e9171acbf1b8cbf3532e25172?s=500"
        if not '<p>' in talk['bio']: talk['bio'] = publish_parts(
            talk['bio'].strip(), writer_name="html")['html_body']
        if not '<p>' in talk['description']: talk['description'] = publish_parts(
            talk['description'].strip(), writer_name="html")['html_body']
        if 'format' in talk:
            talk['timeplace'] = day+" "+time+" @ "+tracks[talk['track']]
        else:
            talk['timeplace'] = day+" "+time

        schedule[key].append(talk)

      for talk in s['talks']:
        if foundtrackfour <= 0:
            talk['colspan'] = 2

      foundtrackfour -= 1

      currrow += 1

    if mode == "schedule":

        html = '<h2>Tracks</h2> <div style="display:flex;">'

        for track in tracks:
          if tracks[track] != "": html += '<div class="schedule-item schedule-item-{}">{}</div>'.format(
              track, tracks[track])

        html += "</div>"

        currday = ""
        rowoffset = 0

        for t in schedule:
          s = schedule[t]
          if len(s) == 0: continue
          talk = s[0]
          if talk['day'] != currday:
            if currday != "": html += "</div>"
            html += '<h2>' + talk['day'] + '</h2> <div class="grid-container">'
            currday = talk['day']
            rowoffset = talk['row']-1
          subhtml = '<div class="timeflex" style="grid-row-start: {}; grid-row-end: {}; grid-column-start: {}; grid-column-end: {};"> <div class="timetext"><div><b>{}</b></div><div class="timetext-divider">&nbsp;-&nbsp;</div><div><b>{}</b></div></div> <div class="schedule-item-container" style="flex-grow:1;">'.format(
              talk['row']-rowoffset, talk['row']-rowoffset, talk['col'], talk['col']+talk['colspan'], talk['time'], talk['timeend'])
          for talk in s:
            if talk['col'] == 1:
              subhtml += '''        <div class="schedule-item schedule-item-{}" style="order: {};" id="schedule-field-{}" onclick="var hid=$(this).attr('id').replace('schedule-field','hidden-field'); if (!$('#'+hid).hasClass('active')) $('#'+hid).fadeIn(250),$('#'+hid).addClass('active'); else $('#'+hid).fadeOut(250),$('#'+hid).removeClass('active');">
              <div><b>{}</b></div>
              <div>{}</div>
              <div class="hidden-field" id="hidden-field-{}">
                <br>
                <div>{}</div>
                <br>
                <div><b>Description:</b></div>
                <div>{}</div>
                <br>
                <div><b>Bio:</b></div>
                <div>{}</div>
                <br>
                <div><b>{}</b></div>
                <br>
                <a href="{talks_page}#row-{}">View more talks information</a> <br>
                <a href="{speakers_page}#row-{}">View more speaker information</a>
              </div>
            </div>'''.format(talk['subcol'], talk['subcol']-1, talk['specialid'], talk['title'], talk['speaker'], talk['specialid'], talk['timeplace'], talk['description'], talk['bio'], tracks[talk['subcol']], talk['specialid'], talk['specialid'], talks_page=talks_page, speakers_page=speakers_page, schedule_page=schedule_page)
          subhtml += '</div> </div>'
          for talk in s:
            if talk['col'] == 2:
              subhtml += '''    <div class="workshop-item" style="grid-row-start:{}; grid-row-end:{}; grid-column-start: {}; grid-column-end: {};" id="schedule-field-{}" onclick="var hid=$(this).attr('id').replace('schedule-field','hidden-field'); if (!$('#'+hid).hasClass('active')) $('#'+hid).fadeIn(250),$('#'+hid).addClass('active'); else $('#'+hid).fadeOut(250),$('#'+hid).removeClass('active');">
            <div class="workshop-text">
              <b>{}</b><br>
              {}
              <div class="hidden-field" id="hidden-field-{}">
                <br>
                <div>{}</div>
                <br>
                <div><b>Description:</b></div>
                <div>{}</div>
                <br>
                <div><b>Bio:</b></div>
                <div>{}</div>
                <br>
                <div><b>{}</b></div>
                <br>
                <a href="{talks_page}#row-{}">View more talks information</a> <br>
                <a href="{speakers_page}#row-{}">View more speaker information</a>
              </div>
            </div>
          </div>'''.format(talk['row']-rowoffset, talk['row']-rowoffset+3, talk['col'], talk['col'], talk['specialid'], talk['title'], talk['speaker'], talk['specialid'], talk['timeplace'], talk['description'], talk['bio'], tracks[talk['subcol']], talk['specialid'], talk['specialid'], talks_page=talks_page, speakers_page=speakers_page, schedule_page=schedule_page)

          html += subhtml

        # print(html)

        # Generate html file
        htmlhead = '''
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="date" content="2019-06-10 22:28" />
        <meta name="summary" content="Conference Schedule" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.js"></script>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
        <style>
        .root-container a {
            color: white !important;
        }
        .grid-container {
            width: 100%;
            display: grid;
            grid-template-columns: 60% auto;
            grid-row-gap: 10px;
            grid-column-gap: 5px;
        }
        .timeflex {
            display: flex;
            flex-direction: row;
        }
        .schedule-item-container {
            display:flex;
            flex-direction: column;
        }
        .schedule-item {
            padding: 5px;
            padding-left: 10px;
            color: white;
            width: 100%;
            margin-bottom: 5px;
        }
        .schedule-item:hover, .workshop-item:hover {
          opacity: 0.8;
          cursor: pointer;
        }
        .schedule-item-1 {
            background-color: darkblue;
        }
        .schedule-item-2 {
            background-color: darkgreen;
        }
        .schedule-item-3 {
            background-color: darkred;
        }
        .schedule-item-5 {
            background-color: gray;
        }
        .p-5 {
            padding: 5px;
        }
        .workshop-item, .schedule-item-4 {
            grid-column-start:3;
            background-color: purple;
            color: white;
            margin-bottom: 5px;
            padding: 5px;
            padding-left: 10px;
        }
        .workshop-item .workshop-text {
        }
        .timetext {
            padding-right: 5px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .timetext .timetext-divider {
            display: none;
        }
        .hidden-field {
          display: none;
        }

        @media screen and (max-width: 576px) /* Mobile */ {
            .timeflex {
                flex-direction: column;
            }

            .timetext {
                flex-direction: row;
                justify-content: flex-start;
            }

            .timetext .timetext-divider {
                display: block;
            }
        }
        </style>
        '''

        return ''+htmlhead+'<div class="root-container">'+html+'</div>'

    elif mode == "talks":
        html = '<div>'

        talks = sorted(talks, key=lambda t: t['title'])

        htmlhead = '''
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
        '''

        htmlblock = '''
        <div class="clearfix section" id="row-{}">
            <h1>{}</h1>
            <p>by <a href="{speakers_page}#row-{}">{}</a></p>
            <p>Format: {} (Duration: {})</p>
            <p><a href="{schedule_page}#schedule-field-{}">{}</a></p>
            <div class="section" id="abstract">
                <h2>Abstract</h2>
                <p>{}</p>
            </div>
        </div>
        '''

        for talk in talks:
            if not 'format' in talk: continue
            html += htmlblock.format(talk['specialid'], talk['title'], talk['specialid'], talk['speaker'],
                                     talk['format'], talk['dur'], talk['specialid'], talk['timeplace'], talk['description'], talks_page=talks_page, speakers_page=speakers_page, schedule_page=schedule_page)

        html += '</div>'

        return htmlhead+html

    elif mode == "speakers":
        html = '<div>'

        talks = sorted(talks, key=lambda t: t['speaker'])

        htmlhead = '''
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

        <style>
            .profile-img { height: 200px; float:right; border-radius:50%; }
            @media screen and (max-width: 576px) /* Mobile */ {
                .profile-img { float: none; }
            }
        </style>
        '''

        htmlblock = '''
        <div class="clearfix section" id="row-{}">
            <h1>{}</h1>
            <img alt="{}" class="img-circle img-responsive align-right profile-img" src="{}">
            {}
            <p>Talk: <a href="{talks_page}#row-{}">{}</a></p>
            <p><a href="{schedule_page}#schedule-field-{}">{}</a></p>
            <div class="section" id="biography">
              <h2>Biography</h2>
              <p>{}</p>
            </div>
        </div>
        '''

        for talk in talks:
            if not 'format' in talk: continue
            html += htmlblock.format(talk['specialid'], talk['speaker'], talk['speaker'], talk['speakerimg'],
                                     '<p class="fa fa-twitter fa-fw"><a class="reference external" href="https://twitter.com/{}">{}</a></p>'.format(talk['twitter'], talk['twitter']) if len(talk['twitter'].strip()) > 0 else "", talk['specialid'], talk['title'], talk['specialid'], talk['timeplace'], talk['bio'], talks_page=talks_page, speakers_page=speakers_page, schedule_page=schedule_page)

        html += '</div>'

        return htmlhead+html


if __name__ == "__main__":
  generate("talks2019.yaml")
  #print(genone("talks2019.yaml","./schedule.html","./talks.html","./speakers.html","schedule"))
