# from .constants import *
from .create_channels import add_channel_if_not_exists
import requests

# The ID of the Project Pairing category
project_pairing_category_id = '748650123092820140'

# You can copy-paste project names here on each line and it will split and trim them
project_text = '''The Hotbox
Padlock News
Tempoture
Sage
Submitty
Insomnia Dialogue System
Exalendar
DormDesign
RPI Housing Finder
Spiral Football Stats
Lavender Programming Language
useCloudFS
Used Car Data Playground
OpenCircuits
TutorBase
Smartrider
ShuttleTracker
Poll Buddy
Telescope
AIPS 
Pipeline
YACS
Venue
Taper'''
projects = list(map(str.strip, project_text.splitlines()))


def run():
    print(
        f'Creating project pairing text-channels for {len(projects)} projects')

    for project in projects:
        add_channel_if_not_exists(
            project, topic=f'Discuss **{project}** with its Project Lead!', parent_id=project_pairing_category_id)
