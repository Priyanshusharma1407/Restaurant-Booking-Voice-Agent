const axios = require("axios");

async function getWeatherForDate(city) {
  try {
    const resp = await axios.get(
      `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${process.env.OPENWEATHER_API_KEY}&units=metric`
    );

    return {
      temp: resp.data.main.temp,
      description: resp.data.weather[0].description,
    };
  } catch (error) {
    console.error("Weather fetch error:", error.message);
    return null;
  }
}

module.exports = { getWeatherForDate };
