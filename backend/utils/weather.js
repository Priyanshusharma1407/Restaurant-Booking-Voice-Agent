import axios from "axios";

export const getWeatherForDate = async (city) => {
  try {
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(
      city
    )}&appid=${process.env.OPENWEATHER_API_KEY}&units=metric`;

    const resp = await axios.get(url);

    return {
      description: resp.data.weather[0].description,
      temp: resp.data.main.temp,
    };
  } catch (err) {
    console.error("Weather API error:", err.response?.data || err.message);
    return null;
  }
};
