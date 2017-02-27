#!/usr/bin/env python3

import sys
import collections
import itertools
import re
import tbapy
import discord
import asyncio

client = discord.Client()
tba = tbapy.TBA('Rishov Sarkar <rishov.sarkar@gmail.com>:FRC Meetup Bot:v0.0.0')

server_id = '176186766946992128'

message_server_id = server_id
message_channel_id = '285628715017437184'

year = 2017
week = 1
max_events = 25

separator = '~~{0}~~'.format(' ' * 100)

not_digit = r'(?:[^\d]|$|^)'
team_number_regexes = [
        re.compile(r'\b(?:FRC|Team)(\d{1,4})\b', re.IGNORECASE),
        re.compile(r'(?:FRC|Team)(\d{1,4})' + not_digit, re.IGNORECASE),
        re.compile(r'\b(\d{1,4})\b'),
        re.compile(r'\b(\d{4})' + not_digit),
        re.compile(not_digit + r'(\d{4})\b'),
        re.compile(not_digit + r'(\d{4})' + not_digit),
        re.compile(r'\b(\d{3})' + not_digit),
        re.compile(not_digit + r'(\d{3})\b'),
        re.compile(not_digit + r'(\d{3})' + not_digit),
        re.compile(r'\b(\d{2})' + not_digit),
        re.compile(not_digit + r'(\d{2})\b'),
        re.compile(not_digit + r'(\d{2})' + not_digit),
        re.compile(r'\b(\d)' + not_digit),
        re.compile(not_digit + r'(\d)\b'),
        re.compile(not_digit + r'(\d)' + not_digit),
]

valid_team_numbers = set()
tba_pages_queried = set()

def is_team_number_valid(team):
    if team in valid_team_numbers: return True
    page = team // 500
    if page in tba_pages_queried: return False
    teams_from_page = tba.teams(page)
    def get_team_from_tba_object(tba_object): return tba_object['team_number']
    valid_team_numbers.update(map(get_team_from_tba_object, teams_from_page))
    tba_pages_queried.add(page)
    return team in valid_team_numbers

def get_team(member):
    nick = member.nick or member.name
    for regex in team_number_regexes:
        for match in regex.finditer(nick):
            team = int(match.group(1))
            if team and is_team_number_valid(team): return team

async def run_bot():
    def is_not_bot(member): return not member.bot

    server = client.get_server(server_id)

    message_server = client.get_server(message_server_id)
    message_channel = None

    if message_server is not None:
        message_channel = message_server.get_channel(message_channel_id)
        await client.send_message(message_channel, '*Hello, I am the FRC '
                'Meetup Bot! Please give me a moment to fetch data for all the '
                'members on this server and compute possible meetups.*')

    if server is None:
        if message_server is None:
            print('Error: no access to server!', file=sys.stderr)
        else:
            await client.send_message(message_channel,
                    '***Error:** no access to server!*')
        return

    members_by_team = collections.defaultdict(list)
    for member in filter(is_not_bot, server.members):
        members_by_team[get_team(member)].append(member)
    members_with_no_team = members_by_team.pop(None, ())

    def in_week(event): return event['week'] == week - 1

    event_names = {}
    teams_by_event = collections.defaultdict(set)

    loop = asyncio.get_event_loop()

    for index, team in enumerate(members_by_team.keys()):
        print('Fetching data for team {0} ({1} of {2})...'.format(team,
            index + 1, len(members_by_team.keys())))
        team_events = filter(in_week, await loop.run_in_executor(None,
            tba.team_events, team, year))
        for event in team_events:
            event_key = event['key']
            event_names[event_key] = event['name']
            teams_by_event[event_key].add(team)

    def number_of_teams_attending(event_key):
        return len(teams_by_event[event_key])
    def multiple_teams_attending(event_key):
        return number_of_teams_attending(event_key) > 1
    def pluralize(number, unit):
        return '{number} {unit}{s}'.format(number=number, unit=unit,
                s='s' if number != 1 else '')
    def get_mention(member): return member.mention

    events = tuple(sorted(filter(multiple_teams_attending,
            teams_by_event.keys()),
            key=number_of_teams_attending, reverse=True))
    for event_key in events[:max_events]:
        event_name = event_names[event_key]
        x_teams = pluralize(number_of_teams_attending(event_key), 'team')
        members = tuple(itertools.chain.from_iterable(map(members_by_team.get,
            teams_by_event[event_key])))
        x_members = pluralize(len(members), 'member')
        member_mentions = '\n'.join(map(get_mention, members))
        await client.send_message(message_channel, '{separator}\n**Attending '
                '{event_name}:**\n*{x_teams}, {x_members}*\n{member_mentions}'
                .format(separator=separator, event_name=event_name,
                    x_teams=x_teams, x_members=x_members,
                    member_mentions=member_mentions))
    if not len(events):
        await client.send_message(message_channel, '*I couldn\'t find any '
                'potential meetups. :frowning: Try again next week, or make '
                'sure that your team number is set correctly.*')
    if len(events) > max_events:
        await client.send_message(message_channel, '{separator}\n*{0} not '
                'shown.*'
                .format(pluralize(len(events) - max_events, 'event'),
                    separator=separator))
    if len(members_with_no_team):
        member_mentions = '\n'.join(map(get_mention, members_with_no_team))
        await client.send_message(message_channel, '{separator}\n'
                '*Could not identify team '
                'number for the following members:*\n{member_mentions}'
                .format(member_mentions=member_mentions, separator=separator))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await run_bot()

if __name__ == '__main__':
    with open('token.txt', 'r') as oauth_token_file:
        oauth_token = oauth_token_file.readline().strip()
    client.run(oauth_token)
