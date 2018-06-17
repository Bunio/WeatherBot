import time
import re
from slackclient import SlackClient


RTM_READ_DELAY = 1
COMMAND_WEATHER = "weather"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

slack_client = SlackClient("xoxb-382425581521-382273516256-tUzVE0NsPOtQNxHkcHBfOlRQ")
starterbot_id = None


def handleCommand(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parseDirectMention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parseDirectMention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def processCommand(command, channel):

    default_response = "Not sure what you mean. Try *{}*.".format(COMMAND_WEATHER)
    response = None

    if command.startswith(COMMAND_WEATHER):
        response = getWeather();

    sendMessage(channel, response or default_response)

def getWeather():
    print("Getting weather...")
    return "Some weather"


def sendMessage(channel, message):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("jWeather is up and running !")
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = handleCommand(slack_client.rtm_read())
            if command:
                processCommand(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed!")