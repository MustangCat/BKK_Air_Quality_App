import requests
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from datetime import datetime
import numpy as np
from scipy.stats import gaussian_kde
from config import API_TOKEN

st.set_page_config(
    page_title="Real-time Air Quality",
    page_icon="😷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .centered {
            text-align: center;
            color: #2C3E50;
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.5em;
            margin: 0;
        }
        p {
            font-size: 1.1em;
            margin: 0;
            color: #7F8C8D;
        }
    </style>
    <div class="centered">
        <h1 style="color:#ed66c0;">วันนี้มีฝุ่นเยอะไหม?</h1>
        <p style="color: #7F8C8D; font-size: 1.2em;">
            สำรวจดัชนีวัดคุณภาพอากาศ (Air Quality Index) แบบเรียลไทม์ กรุงเทพและเมืองอื่น ๆ
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="margin-top: 50px;"></div>
    """,
    unsafe_allow_html=True
)

# Function to fetch AQI data for a city
def fetch_aqi_data(city):
    url = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok":
            return data
    except requests.RequestException as e:
        st.error(f"Error fetching data for {city}: {e}")
    return None

# Function to validate and convert AQI
def validate_and_convert_aqi(aqi):
    try:
        return int(aqi)
    except (ValueError, TypeError):
        return None

# Function to display AQI card with embedded forecast chart
def display_aqi_card_with_chart(column, city_name, aqi, time_struct, forecast):
    aqi_color = get_aqi_color(aqi)

    # Format time from API structure
    formatted_time = time_struct.get("s", "Unknown")

    # Generate forecast chart if forecast data is available
    forecast_chart_html = ""
    if forecast:
        days = [f["day"] for f in forecast]
        values = [f["avg"] for f in forecast]
        today = datetime.now().strftime("%Y-%m-%d")
        fig, ax = plt.subplots(figsize=(4, 2), dpi=150)
        ax.plot(days, values, marker="o", linestyle="-", color="#ed66c0")

        if today in days:
            today_index = days.index(today)
            ax.scatter(days[today_index], values[today_index], color="#7F8C8D", s=100, label="Today")

        ax.set_title("Forecast AQI", fontsize=10, color="#7F8C8D")
        ax.set_xlabel("Date", fontsize=8, color="#7F8C8D")
        ax.set_ylabel("AQI", fontsize=8, color="#7F8C8D")
        ax.tick_params(axis="x", labelsize=7, rotation=45, colors="#7F8C8D")
        ax.tick_params(axis="y", labelsize=7, colors="#7F8C8D")
        ax.legend(fontsize=7)
        sns.despine()

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        forecast_chart_html = f"<img src='data:image/png;base64,{base64.b64encode(buf.read()).decode()}' style='width:100%; border-radius:5px; margin-top:5px;'>"
        buf.close()
        plt.close(fig)

    # Render the AQI card with embedded forecast chart
    column.markdown(
        f"""
        <div style="text-align: center; background: #F9F9F9; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); padding: 20px; border-radius: 10px;">
            <h2 style="color: {aqi_color}; margin: 0;">{aqi}</h2>
            <p style="margin: 5px 0; font-weight: bold; color: #34495E;">{city_name}</p>
            <p style="font-size: 0.9em; color: #7F8C8D;">อัพเดตล่าสุดเมื่อ: {formatted_time}</p>
            {forecast_chart_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# Function to get AQI color
def get_aqi_color(aqi):
    try:
        aqi = int(aqi)
    except ValueError:
        return "#000000"
    if aqi <= 25:
        return "#1E8449"
    elif aqi <= 50:
        return "#27AE60"
    elif aqi <= 75:
        return "#F1C40F"
    elif aqi <= 100:
        return "#F39C12"
    elif aqi <= 125:
        return "#E67E22"
    elif aqi <= 150:
        return "#D35400"
    elif aqi <= 175:
        return "#C0392B"
    elif aqi <= 200:
        return "#A93226"
    elif aqi <= 300:
        return "#7D3C98"
    else:
        return "#5B2C6F"

# Fetch AQI data for multiple cities
def fetch_cities_aqi():
    cities = ["Bangkok", "Tokyo", "Delhi", "New York", "London", "Paris", "Beijing", "Moscow", "Dubai", "Singapore",
        "Los Angeles", "Chicago", "Sydney", "Istanbul", "Seoul", "Mumbai", "Karachi", "Shanghai", "Mexico City",
        "São Paulo", "Jakarta", "Lagos", "Cairo", "Buenos Aires", "Kolkata", "Lima", "Tehran", "Kinshasa",
        "Rio de Janeiro", "Baghdad", "Santiago", "Madrid", "Bangladesh", "Berlin", "Riyadh", "Houston",
        "Toronto", "Philadelphia", "Dallas", "San Francisco", "Boston", "Atlanta", "Miami", "Barcelona",
        "Johannesburg", "Nairobi", "Melbourne", "Montreal", "Rome", "Cape Town"]  
    city_data = []
    bangkok_data = fetch_aqi_data("Bangkok")
    bangkok_aqi = validate_and_convert_aqi(bangkok_data["data"].get("aqi")) if bangkok_data else None

    for city in cities:
        if city == "Bangkok":
            continue
        data = fetch_aqi_data(city)
        if data:
            aqi = validate_and_convert_aqi(data["data"].get("aqi"))
            if aqi is not None:
                city_data.append({
                    "city": data["data"].get("city", {}).get("name", "Unknown"),
                    "aqi": aqi,
                    "time": data["data"].get("time", {})
                })
    return bangkok_aqi, city_data, bangkok_data

# Display Bangkok's AQI and forecast
bangkok_aqi, other_cities, bangkok_data = fetch_cities_aqi()
if bangkok_aqi and bangkok_data:
    left, right = st.columns([2, 1], gap="large")
    forecast = bangkok_data["data"].get("forecast", {}).get("daily", {}).get("pm25", [])
    time_struct = bangkok_data["data"].get("time", {})
    display_aqi_card_with_chart(right, "Bangkok", bangkok_aqi, time_struct, forecast)

# KDE Plot for Bangkok AQI Percentile
if bangkok_aqi:
    cities_aqi = [city["aqi"] for city in other_cities]
    cities_aqi.append(bangkok_aqi)
    kde = gaussian_kde(cities_aqi)
    x_vals = np.linspace(min(cities_aqi), max(cities_aqi), 200)
    density = kde(x_vals)

    fig, ax = plt.subplots()
    sns.lineplot(x=x_vals, y=density, color="#7F8C8D", ax=ax)
    ax.axvline(bangkok_aqi, color="#ed66c0", linestyle="--", label="Bangkok AQI")
    ax.set_title("Bangkok AQI Percentile", fontsize=8, color="#7F8C8D")

    # Calculate and display percentile rank for Bangkok
    all_aqi = [city["aqi"] for city in other_cities] + [bangkok_aqi]
    all_aqi_sorted = sorted(all_aqi)
    bangkok_percentile = (all_aqi_sorted.index(bangkok_aqi) / len(all_aqi_sorted)) * 100

    ax.text(bangkok_aqi, max(density) * 0.8, f"{bangkok_percentile:.2f}%", color="#ed66c0", fontsize=8, ha="center")

    ax.set_xlabel("AQI", fontsize=8, color="#7F8C8D")
    ax.set_ylabel("Density", fontsize=8, color="#7F8C8D")
    ax.legend()
    sns.despine()
    left.pyplot(fig)

    st.markdown(
    f"""
    <div style="background-color: #F9F9F9; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); margin: 20px auto; width: 80%;">
        <h3 style="font-size: 1.5em; color: #34495E; margin: 0;">Bangkok AQI Percentile: <span style="color: #E74C3C;">{bangkok_percentile:.2f}%</span></h3>
        <p style="font-size: 1.1em; color: #7F8C8D; margin-top: 10px;">
            AQI ในกรุงเทพ เมื่อเทียบกับเมืองอื่น ๆ ให้คะแนนอากาศแย่ที่สุด 100 คะแนน ปัจจุบันกรุงเทพได้คะแนน <strong>{bangkok_percentile:.2f}</strong><br>
            ซึ่งหมายถึงคุณภาพอากาศในกรุงเทพแย่กว่าเมืองส่วนใหญ่ในรายการนี้
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="margin-top: 100px;"></div>
    """,
    unsafe_allow_html=True
)

# Display top 5 better and worse cities
if other_cities:
    st.markdown(
        """
        <div style="text-align: center; color: #ed66c0;">
            <h2>5 เมืองที่อากาศดีที่สุด</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    better_cities = sorted(other_cities, key=lambda x: x["aqi"])[:5]
    better_cols = st.columns(len(better_cities))
    for col, city in zip(better_cols, better_cities):
        display_aqi_card_with_chart(col, city["city"], city["aqi"], city["time"], None)

    st.markdown(
    """
    <div style="margin-top: 50px;"></div>
    """,
    unsafe_allow_html=True
)
    
    st.markdown(
        """
        <div style="text-align: center; color: #ed66c0;">
            <h2>5 เมืองที่อากาศแย่ที่สุด</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    worse_cities = sorted(other_cities, key=lambda x: x["aqi"], reverse=True)[:5]
    worse_cols = st.columns(len(worse_cities))
    for col, city in zip(worse_cols, worse_cities):
        display_aqi_card_with_chart(col, city["city"], city["aqi"], city["time"], None)

st.markdown(
    """
    <div style="margin-top: 100px;"></div>
    """,
    unsafe_allow_html=True
)

# Add a footnote listing all cities
st.markdown(
    """
    <div style="margin-top: 40px; text-align: center; color: #7F8C8D; font-size: 0.9em;">
        <p><strong>Cities with collected data:</strong></p>
        <p>Bangkok, Tokyo, Delhi, New York, London, Paris, Beijing, Moscow, Dubai, Singapore,<br>
        Los Angeles, Chicago, Sydney, Istanbul, Seoul, Mumbai, Karachi, Shanghai, Mexico City,<br>
        São Paulo, Jakarta, Lagos, Cairo, Buenos Aires, Kolkata, Lima, Tehran, Kinshasa,<br>
        Rio de Janeiro, Baghdad, Santiago, Madrid, Bangladesh, Berlin, Riyadh, Houston,<br>
        Toronto, Philadelphia, Dallas, San Francisco, Boston, Atlanta, Miami, Barcelona,<br>
        Johannesburg, Nairobi, Melbourne, Montreal, Rome, Cape Town</p>
    </div>
    """,
    unsafe_allow_html=True
)






