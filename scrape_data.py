import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
from parse import parse
import pickle

def load_page(datetime):
    formatted_datetime = datetime.strftime("%Y%m%d%H%M%S")
    original_url = "https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html"
    url = f"https://web.archive.org/web/{formatted_datetime}/{original_url}"
    page = requests.get(url)
    print(f"Requested page from {datetime}. Status code: {page.status_code}")
    return page


def parse_page(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} table(s)")
    df = pd.read_html(str(tables[0]))[0]
    par = ""
    for p in soup.find_all('p'):
        if ("Stand:" in p.get_text() or "Datenstand:" in p.get_text()) and "Uhr" in p.get_text():
            par = p.get_text()
            break
    if par.startswith("(") and par.endswith(")"):
        par = par[1:-1]
    timeinfo = parse("Stand: {}, {} Uhr", par)
    print(par)
    if timeinfo is None:
        timeinfo = parse("Datenstand: {}, {} Uhr", par)
    date, time = timeinfo[0], timeinfo[1]
    day, month, year = [int(s) for s in date.split(".")]
    hour, minutes = [int(s) for s in time.split(":")]
    dt = datetime(year, month, day, hour, minutes)
    return df, dt

def query(initial_dt, delta_dt):
    query_dt = initial_dt

    try:
        with open("data.pkl", "rb") as file:
            df_list, dt_list = pickle.load(file)
    except:
        df_list = []
        dt_list = []

    while query_dt < datetime.now():
        page = load_page(query_dt)
        df, dt = parse_page(page)
        if dt not in dt_list:
            df_list.append(df)
            dt_list.append(dt)
        query_dt += delta_dt
        time.sleep(1)

    with open("data.pkl", "wb") as file:
        pickle.dump([df_list, dt_list], file)


if __name__ == "__main__":
    initial_dt = datetime(2020, 2, 29, 0, 0, 0)
    delta_dt = timedelta(hours=6)
    query(initial_dt, delta_dt)



