import time
import re
import requests

from datetime import datetime
from datetime import timedelta
from time import strftime
from slackclient import SlackClient


#CONSTANTS
COMMAND_WEATHER = "weather"
UNITS_METRIC = "metric" # For temperature in Celsius
UNITS_IMPERIAL = "imperial" # For temperature in Fahrenheit

PARAM_APPID = "appid"
PARAM_CITY = "q"
PARAM_UNITS = "units"

WHEN_NOW = "now"
WHEN_TODAY = "today"
WHEN_TOMORROW = "tomorrow"
WHEN_FORECAST = "forecast"

URL_NOW = "http://api.openweathermap.org/data/2.5/weather"
URL_FORECAST = "http://api.openweathermap.org/data/2.5/forecast"

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

    commandArray = command.split();

    city = command.split()[0]
    when = WHEN_NOW

    if len(commandArray) > 1:
     when = commandArray[1]

    if(city.lower() == "help"):
        response = getHelp()
    else:
        response = getWeather(city, when)

    sendMessage(channel, response)

def getWeather(city, when):
    print("Getting weather for " + city + " when ? " + when)

    payload = {
        PARAM_APPID : OPENWEATHERMAP_API_KEY,
        PARAM_UNITS : UNITS_METRIC,
        PARAM_CITY: city
    }

    when = when.lower();

    URL = URL_NOW if when == WHEN_NOW else URL_FORECAST
    response = requests.get(URL, params = payload)
    #debugResponse(response);

    weatherText = "I could not get weather data for \"" + city + "\" city. Say \"Help\" to get more info";

    if response.status_code == 200:
        if when == WHEN_NOW:
            weatherText = parseWeatherJson(response.json(), city, when)
        elif when == WHEN_TODAY:
            date = datetime.now()
            weatherText = parseWeatherJsonWithDate(response.json(), city, when, date.strftime("%Y-%m-%d"))
        elif when == WHEN_TOMORROW:
            date = datetime.now() + timedelta(days=1)
            weatherText = parseWeatherJsonWithDate(response.json(), city, when, date.strftime("%Y-%m-%d"))
        elif when == WHEN_FORECAST:
            weatherText = ""
            for listItem in response.json()["list"]:
                weatherText += parseWeatherJson(listItem, city, when) + "\n"

    return weatherText;


def parseWeatherJsonWithDate(jsonResponse, city, when, date):
    weatherText = ""
    for listItem in jsonResponse["list"]:
        if listItem["dt_txt"].split()[0] == date:
            weatherText += parseWeatherJson(listItem, city, when) + "\n"

    return weatherText;

def parseWeatherJson(jsonResponse, city, when):
    date = "now" if when == WHEN_NOW else getDate(jsonResponse)
    response = "Weather in " + city + " (" + date + "): " + getMainWeather(jsonResponse)
    response += ", Temperature: " + getTemperature(jsonResponse);
    return response

def getDate(jsonResponse):
    return jsonResponse["dt_txt"]

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

def getHelp():
    help = ""
    help += "Hi, my name is jWeather ! Please ask me about weather in following format: \n"
    help += "[CITY] + (optional) [NOW/TODAY/TOMORROW/FORECAST] eg: \"Cracow tomorrow\" \n"
    help += " > [CITY] - Name of your city eg. Cracow \n"
    help += " > [NOW] - Weather at the moment (default) \n"
    help += " > [TODAY] - Weather for the rest of the day, measured every 3 hours \n"
    help += " > [TOMORROW] - Weather for tomorrow, measured every 3 hours \n"
    help += " > [FORECAST] - Weather for the next 5 days, measured every 3 hours \n"
    return help


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