# from .constants import *
from rcosautomation.discord.constants import MATTERMOST_USERNAME, MATTERMOST_PASSWORD
from rcosautomation.discord.channels import add_channel_if_not_exists
import requests


from mattermostdriver import Driver

mattermost = Driver({
    'url': '54.197.25.170',
    'login_id': MATTERMOST_USERNAME,
    'password': MATTERMOST_PASSWORD
})

# mattermost.login()

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

    mattermost.channels.create_channel(options={
        'team_id': 'rcos',
        'name': 'pairing-test-project',
        'display_name': '(pairing) Test Project',
        'type': 0
    })

    # for project in projects:
    #     add_channel_if_not_exists(
    #         project, topic=f'Discuss **{project}** with its Project Lead!', parent_id=project_pairing_category_id)
