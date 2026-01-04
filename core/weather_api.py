from datetime import datetime, timedelta
import requests
import pandas as pd
import math

class WeatherAPI:
    """
    Fetch real weather data for ET0 calculation and rainfall using Open-Meteo API.
    No API key required, works worldwide.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, latitude: float, longitude: float, days: int = 10):
        self.latitude = latitude
        self.longitude = longitude
        self.days = days
        self.daily_data = None
        self.current_weather_data = None

    def fetch(self):
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=self.days - 1)).strftime("%Y-%m-%d")

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "current_weather": True  # اضافه کردن وضعیت فعلی
        }

        response = requests.get(self.BASE_URL, params=params)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch weather data: {response.status_code}, {response.text}")

        json_data = response.json()
        daily = json_data.get("daily", {})
        self.daily_data = daily
        self.current_weather_data = json_data.get("current_weather", {})

        dates = daily.get("time", [])
        tmax_list = daily.get("temperature_2m_max", [])
        tmin_list = daily.get("temperature_2m_min", [])
        prcp_list = daily.get("precipitation_sum", [])

        if not dates:
            raise ValueError("No weather data returned from API")

        et0_list = []
        rainfall_list = []

        for tmax, tmin, prcp in zip(tmax_list, tmin_list, prcp_list):
            if tmax is None or tmin is None:
                tmax = 25.0
                tmin = 15.0
            tmean = (tmax + tmin) / 2

            # Hargreaves ET0 (FAO-56 simplified)
            et0 = 0.0023 * (tmean + 17.8) * math.sqrt(max(tmax - tmin, 0)) * 0.408 * 136
            et0_list.append(round(et0, 2))
            rainfall_list.append(round(prcp if prcp is not None else 0.0, 1))

        return et0_list, rainfall_list

    def current_temperature(self):
        """
        Return current temperature in Celsius from Open-Meteo
        """
        if self.current_weather_data:
            return round(self.current_weather_data.get("temperature", 0.0), 1)
        return 0.0

    def current_conditions(self):
        """
        Return a simple text description of current weather
        """
        if self.current_weather_data:
            weather_code = self.current_weather_data.get("weathercode", 0)
            # کدهای آب و هوای Open-Meteo (کدهای FAO مشابه)
            code_map = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Drizzle: light",
                53: "Drizzle: moderate",
                55: "Drizzle: dense",
                61: "Rain: slight",
                63: "Rain: moderate",
                65: "Rain: heavy",
                71: "Snow: slight",
                73: "Snow: moderate",
                75: "Snow: heavy",
                80: "Rain showers: slight",
                81: "Rain showers: moderate",
                82: "Rain showers: violent",
            }
            return code_map.get(weather_code, "Unknown")
        return "Unknown"
