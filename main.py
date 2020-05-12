import requests
import json
import speech_recognition as sr
# import pyttsx3
from gtts import gTTS
import re
import playsound
import threading
import time


class Data:
    def __init__(self, api_key, project_key):
        self.api_key = api_key
        self.project_key = project_key
        self.params = {
            "api_key": api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_key}/last_ready_run/data',
                                params={"api_key": self.api_key})
        data = json.loads(response.text)
        return data


    def get_total_cases(self):
        data = self.data['total']

        for content in data:
            if content['name'] == "Coronavirus Cases:":
                print("Total cases Wordlwide:", content['values'])
                return content['values']

    def get_total_deaths(self):
        data = self.data['total']

        for death in data:
            if death['name'] == "Deaths:":
                print("Total Deaths:", death['values'])
                return death['values']

    def get_total_recovered(self):
        data = self.data['total']

        for content in data:
            if content['name'] == 'Recovered:':
                print("Total Recovered:", content['values'])
                return content['values']

    def get_country_data(self, country):
        data = self.data['selection1']

        for content in data:
            if content['name'].lower() == country.lower():
                print("COVID-19 Statistics for", str(country))
                print("Total Cases:", str(content['total_cases']))
                print("Total Deaths:", str(content['total_deaths']))
                print("Total Recovered:", str(content['total_recvr']))
                print("Total Active Cases:", str(content['active_cases']))
                return content

        return "0"

    def get_country_list(self):
        countries = []
        for country in self.data['selection1']:
            countries.append(country['name'].lower())

        return countries

    def update(self):
        requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_key}/run',
                      params={"api_key": self.api_key})


        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data Updated")
                    break
                time.sleep(5)


        t = threading.Thread(target=poll())
        t.start()


# print(data.get_country_data("India")["total_cases"])

def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = 'voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        ip_text = ""
        try:
            ip_text = r.recognize_google(audio)
        except Exception as e:
            print("Exception", str(e))

    return ip_text.lower()


def main():
    api_key1 = "tHFp87yrN8JV"
    project_token = "tduQt5gxrndZ"
    # run_token = "tWkq9L9Q_nJQ"
    print("Started.")
    stop = "stop"
    data = Data(api_key1, project_token)

    country_list = data.get_country_list()
    update_cmd = "update"
    patterns = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ death"): data.get_total_deaths,
        re.compile("[\w\s]+ total death"): data.get_total_deaths,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total recovered"): data.get_total_recovered,
        re.compile("[\w\s]+ total recover"): data.get_total_recovered,
    }

    country_data = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)["total_cases"],
        re.compile("[\w\s]+ death [\w\s]+"): lambda country: data.get_country_data(country)["total_deaths"],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)["total_deaths"],
        re.compile("[\w\s]+ recover [\w\s]+"): lambda country: data.get_country_data(country)["total_recvr"],
        re.compile("[\w\s]+ recovered [\w\s]+"): lambda country: data.get_country_data(country)["total_recvr"],
        re.compile("[\w\s]+ recovery [\w\s]+"): lambda country: data.get_country_data(country)["total_recvr"],
        re.compile("[\w\s]+ active [\w\s]+"): lambda country: data.get_country_data(country)["active_cases"],
    }

    while True:
        print("Listening...")

        text = get_audio()
        print(text)
        result = None
        for pattern, func in country_data.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in patterns.items():
            if pattern.match(text):
                result = func()
                break

        if text == update_cmd:
            result = "Data is being updated!"
            data.update()

        if result:
            speak(result)

        if text.find(stop):  # If stop in audio quit
            break


main()
