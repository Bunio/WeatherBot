import time
import re
import requests
from slackclient import SlackClient

#CONSTANTS
RTM_READ_DELAY = 1
COMMAND_WEATHER = "weather"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

#API KEYS
SLACK_API_KEY = "xoxb-382425581521-382273516256-tUzVE0NsPOtQNxHkcHBfOlRQ"
OPENWEATHERMAP_API_KEY = "f1ac76f721d84084b47c479ce1871604"


slackClient = SlackClient(SLACK_API_KEY)
botId = None


def handleCommand(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            userId, message = parseDirectMention(event["text"])
            if userId == botId:
                return message, event["channel"]
    return None, None

def parseDirectMention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def processCommand(command, channel):

    default_response = "Not sure what you mean. Try *{}*.".format(COMMAND_WEATHER)
    response = None

    #if command.startswith(COMMAND_WEATHER):

    print("Processing command...")
    response = getWeather();
    sendMessage(channel, response or default_response)

def getWeather():
    print("Getting weather...")

    city = "Cracow"
    payload = {'appid' : OPENWEATHERMAP_API_KEY,  'q': city}
    response = requests.get("http://api.openweathermap.org/data/2.5/weather", params = payload)
    debugResponse(response);
    return "Some weather"


def debugResponse(response):
    print("STATUS:")
    print(response.status_code)
    print("HEADERS::")
    print(response.headers)
    print("CONTENT:")
    print(response.content)

def sendMessage(channel, message):
    slackClient.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

if __name__ == "__main__":
    if slackClient.rtm_connect(with_team_state=False):
        print("jWeather is up and running !")
        botId = slackClient.api_call("auth.test")["user_id"]
        while True:
            command, channel = handleCommand(slackClient.rtm_read())
            if command:
                processCommand(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed!")