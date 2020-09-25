from time import sleep
from rcosautomation.discord.users import add_role_to_member
from rcosautomation.discord.constants import RCOS_SERVER_ID, VIEW_CHANNELS, CATEGORY, VOICE_CHANNEL, DISCORD_PM_ROLE_ID, MANAGE_MESSAGES, TEXT_CHANNEL
from rcosautomation.discord.channels import add_channel_if_not_exists, edit_channel, find_channel
from rcosautomation.discord.roles import add_role_if_not_exists, find_role
from typing import List, Dict, Optional
from csv import DictReader
import requests
import re
import os
from pymongo import MongoClient


def run():
    client = MongoClient(os.environ.get('MONGO_URI'))
    db = client['rcos-discord']
    projects = []
    small_groups = dict()

    project_leads_to_project_name = dict()

    with open('projects.csv', 'r') as file:
        csv_reader = DictReader(file)
        for project in csv_reader:
            project_leads_to_project_name[project['Project Lead (RCS ID)']
                                          ] = project['Project Name']
            small_groups[project['Project Name']] = project['Small Group #']
    print(small_groups)

    # First Name,Last Name,User ID,Team ID,Project,Project Lead,Team Registration Section,Team Rotating Section,Mentor
    with open('teams.csv', 'r') as file:
        csv_reader = DictReader(file)
        for team_member in csv_reader:
            rcs_id = team_member['User ID']
            if not team_member['Project Lead'] in project_leads_to_project_name:
                print('Can\'t find project lead',
                      team_member['Project Lead'], 'for', rcs_id)
                continue
            project = project_leads_to_project_name[team_member['Project Lead']]

            project_role = find_role(project)
            if project_role == None:
                print('Can\'t find role for project', project)
                continue

            # Get Discord user id
            user = db.users.find_one({'rcs_id': rcs_id})
            if user == None:
                print(f'Can\'t find user {rcs_id}')
                continue

            if 'discord' not in user or 'user_id' not in user['discord']:
                print(f'{rcs_id} did not connect Discord')
                continue

            small_group_role = find_role(
                'Small Group ' + str(small_groups[project]))
            if small_group_role == None:
                print(
                    f'Can\'t find small group role for Small Group {small_groups[project]}')
            else:
                add_role_to_member(
                    user['discord']['user_id'], small_group_role['id'])
                print(f'Added small group role to {rcs_id}')

            # try:
            #     print(user['discord']['user_id'])
            #     add_role_to_member(
            #         user['discord']['user_id'], project_role['id'])
            #     print(f'Added project {project} role to {rcs_id} on Discord')
            # except Exception as e:
            #     print(
            #         f'Failed to give project role {project} to {rcs_id}: {e}')

            sleep(2)
# Associate project names with their leaders
# Loop through every team record and find team name from team lead
# Add role to member
