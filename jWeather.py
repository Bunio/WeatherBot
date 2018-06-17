import time
import re
import requests
import json
from slackclient import SlackClient

#CONSTANTS
COMMAND_WEATHER = "weather"

# For temperature in Celsius
UNITS_METRIC = "metric"
# For temperature in Fahrenheit
UNITS_IMPERIAL = "imperial"

PARAM_APPID = "appid"
PARAM_CITY = "q"
PARAM_UNITS = "units"


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
    city = command.split()[0]
    response = getWeather(city);
    sendMessage(channel, response)

def getWeather(city):
    print("Getting weather for " + city)

    payload = {
        PARAM_APPID : OPENWEATHERMAP_API_KEY,
        PARAM_UNITS : UNITS_METRIC,
        PARAM_CITY: city
    }

    response = requests.get("http://api.openweathermap.org/data/2.5/weather", params = payload)
    debugResponse(response);

    if response.status_code == 200:
        return (parseWeatherJson(response.json(), city))

    return "I could not get weather data for \"" + city + "\" city. Are you sure it exists?"


def parseWeatherJson(jsonResponse, city):
    response = "Weather in " + city + ": " + getMainWeather(jsonResponse)
    response += ", Temperature: " + getTemperature(jsonResponse);
    return response

def getMainWeather(jsonResponse):
    return jsonResponse["weather"][0]["main"]

def getTemperature(jsonResponse):
    temp_min = jsonResponse["main"]["temp_min"]
    temp_max = jsonResponse["main"]["temp_max"]
    if temp_min != temp_max :
        temperatureString = "between " + str(temp_min) + "°C and " + str(temp_max) + "°C"
    else:
        temperatureString = str(temp_max) + "°C"

    return temperatureString


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
            time.sleep(1)
    else:
        print("Connection failed!")