# autoschedule

Generate schedule, talks, speakers page automatically like official Pycon thailand 2019 website: https://th.pycon.org

* Schedule Page: https://th.pycon.org/schedule
* Talks Page: https://th.pycon.org/talks
* Speakers Page: https://th.pycon.org/speakers

These three pages generated from one yaml file: [CLICK HERE FOR YAML FILE EXAMPLE (talks2019.yaml)](https://github.com/Chomtana/autoschedule/blob/master/talks2019.yaml "talks2019.yaml")

And these three pages are linked together

Good for people who organizing conference event and don't want to code your website schedule, talks, speakers page

# How to use

## For local file generation use

### Basic example
```python
from autoschedule import generate

generate("talks2019.yaml")
```

*Note: you need to change **talks2019.yaml** to your correct yaml file path*

### Custom file name
```python
from autoschedule import generate

generate("talks2019.yaml", schedule_page="./timetable.html", talks_page="./courses.html", speakers_page="./tutors.html")
```

*Note: you need to change **talks2019.yaml** to your correct yaml file path*

## For using in nikola

### Step 1: Install ScheduleShortcode plugins

Copy [ScheduleShortcode.py](https://github.com/Chomtana/autoschedule/blob/master/ScheduleShortcode.py) and [ScheduleShortcode.plugin](https://github.com/Chomtana/autoschedule/blob/master/ScheduleShortcode.plugin) from this repository to plugins/schedule folder in your nikola setup

*Note: if folder doesn't exists, create new one*

### Step 2: Use shortcode in your page

Paste:
* `{{% schedule mode="schedule" file="../talks2019.yaml" talks_page="/talks" speakers_page="/speakers" schedule_page="/schedule %}}` To your schedule page
* `{{% schedule mode="talks" file="../talks2019.yaml" talks_page="/talks" speakers_page="/speakers" schedule_page="/schedule %}}` To your talks page
* `{{% schedule mode="speakers" file="../talks2019.yaml" talks_page="/talks" speakers_page="/speakers" schedule_page="/schedule %}}` To your speakers page

*Note: you need to change **../talks2019.yaml** to your correct yaml file path*

Example of these step can be found in [here](https://github.com/Chomtana/autoschedule/tree/master/nikolaexample)
