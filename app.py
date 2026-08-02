from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# OpenRouter / AI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)


# ---------------- HOME ----------------

@app.route('/')
def index():
    return render_template('index.html')


# ---------------- ABOUT ----------------

@app.route('/about')
def about():
    return render_template('about.html')


# ---------------- WEATHER ----------------

@app.route('/weather-by-coords', methods=['POST'])
def weather_by_coords():
    try:
        data = request.json or {}

        lat = data.get('lat')
        lon = data.get('lon')

        if not lat or not lon:
            return jsonify({
                "response": "Location coordinates are missing, sir."
            }), 400

        weather_api_key = os.environ.get("OPENWEATHER_API_KEY")

        if not weather_api_key:
            return jsonify({
                "response": "OpenWeather API key is missing, sir."
            }), 500

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "lat": lat,
            "lon": lon,
            "appid": weather_api_key,
            "units": "metric"
        }

        res = requests.get(url, params=params, timeout=10)
        weather_data = res.json()

        if weather_data.get("cod") != 200:
            return jsonify({
                "response": "Sorry sir, I couldn't get the weather for your location."
            }), 400

        city = weather_data["name"]
        temp = weather_data["main"]["temp"]
        feels = weather_data["main"]["feels_like"]
        desc = weather_data["weather"][0]["description"]
        humidity = weather_data["main"]["humidity"]

        response = (
            f"It is {desc} in {city}, {temp}°C, "
            f"feels like {feels}°C, humidity {humidity}% sir."
        )

        return jsonify({
            "response": response,
            "city": city,
            "temperature": temp,
            "feels_like": feels,
            "description": desc,
            "humidity": humidity
        })

    except Exception as e:
        return jsonify({
            "response": f"Weather error: {str(e)}"
        }), 500


# ---------------- COMMAND ----------------

@app.route('/command', methods=['POST'])
def handle_command():
    try:
        data = request.json or {}
        command = data.get('command', '').lower().strip()

        if not command:
            return jsonify({
                "response": "I didn't receive any command sir."
            })

        # Open Google
        if "open google" in command:
            return jsonify({
                "response": "Opening Google sir.",
                "url": "https://www.google.com"
            })

        # Open YouTube
        elif "open youtube" in command:
            return jsonify({
                "response": "Opening YouTube sir.",
                "url": "https://www.youtube.com"
            })

        # Open Facebook
        elif "open facebook" in command:
            return jsonify({
                "response": "Opening Facebook sir.",
                "url": "https://www.facebook.com"
            })

        # Open Instagram
        elif "open instagram" in command:
            return jsonify({
                "response": "Opening Instagram sir.",
                "url": "https://www.instagram.com"
            })

        # Current time
        elif "what time" in command or "current time" in command:
            now = datetime.datetime.now().strftime("%I:%M:%S %p")

            return jsonify({
                "response": f"The current time is {now} sir."
            })

        # Current date
        elif (
            "what date" in command
            or "today date" in command
            or "current date" in command
        ):
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")

            return jsonify({
                "response": f"Today is {today} sir."
            })

        # Weather
        elif "weather" in command:
            return jsonify({
                "response": "Please allow location access so I can check the weather, sir.",
                "weather": True
            })

        # AI / OpenRouter
        else:
            if not os.environ.get("OPENROUTER_API_KEY"):
                return jsonify({
                    "response": "OpenRouter API key is missing, sir."
                }), 500

            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://jarvis-python-project.onrender.com/",
                    "X-Title": "Ved Rathod - Jarvis AI Voice Assistant"
                },
                model="openai/gpt-oss-20b:free",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Jarvis, a professional AI voice assistant. "
                            "Reply in one short sentence like a helpful butler."
                        )
                    },
                    {
                        "role": "user",
                        "content": command
                    }
                ]
            )

            response = completion.choices[0].message.content

            return jsonify({
                "response": response
            })

    except Exception as e:
        return jsonify({
            "response": f"Sorry sir, error: {str(e)}"
        }), 500


# ---------------- RUN SERVER ----------------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
