import pandas as pd
import requests
from bs4 import BeautifulSoup


def scraping_political_opinion_data():
    urls = ["http://entnemdept.ufl.edu/frank/kiss/kiss17.htm", "https://ballotpedia.org/Partisan_composition_of_state_legislatures"]
    page = requests.get(urls[0])
    soup = BeautifulSoup(page.content, 'html.parser')
    table_body = soup.find('tbody')
    rows = table_body.find_all('tr')
    state_names = []
    for row in rows:
        cols = row.find_all('td')
        cols = [x.text.strip() for x in cols]
        cols = [cols[x:x+3] for x in range(0, len(cols), 3)]
        for i in range(2):
            cols[i][0] = cols[i][0].replace("\r\n     ", "")
        state_names += cols
    states_fullname_to_shortname_mapping = {}
    for List in state_names:
        states_fullname_to_shortname_mapping[List[0]] = List[2]

    page = requests.get(urls[1])
    soup = BeautifulSoup(page.content, 'html.parser')
    table_body = soup.find('table', attrs={"class": "bptable sortable collapsible"})
    rows = table_body.find_all('tr')
    political_opinion_per_state = []
    for row in rows:
        cols = row.find_all('td')
        cols = [x.text.strip() for x in cols]
        cols = [cols[x:x + 3] for x in range(0, len(cols), 3)]
        political_opinion_per_state += cols
    political_opinion_serious_map_by_state = {}
    for List in political_opinion_per_state:
        if "Republican" in List[1]:
            political_opinion_serious_map_by_state[states_fullname_to_shortname_mapping[List[0]]] = "Republican"
        elif "Democratic" in List[1]:
            political_opinion_serious_map_by_state[states_fullname_to_shortname_mapping[List[0]]] = "Democratic"
        else:
            political_opinion_serious_map_by_state[states_fullname_to_shortname_mapping[List[0]]] = "Divided Government"
    return political_opinion_serious_map_by_state


def load_dataset(file_name):
    df = pd.read_csv(file_name)
    return df


def add_data_to_df(political_opinion_serious_map_by_state):
    df = load_dataset("/Users/or.gelkop/Downloads/lending_club_loan_two.csv")
    political_opinion = []
    state_serious = []
    for address in df.loc[:, "address"]:
        state = ""
        try:
            state = address.split("\n")[1].split(",")[1].split(" ")[1]
            # print(address.split("\n")[1].split(",")[1].split(" ")[1])
        except IndexError:
            state = address.split("\n")[1].split(" ")[1]
            # print(address.split("\n")[1].split(" ")[1])
        finally:
            if state == "AE" or state == "AA" or state == "AP" or state == "DC":
                political_opinion.append("NaN")
                state_serious.append("NaN")
            else:
                political_opinion.append(political_opinion_serious_map_by_state[state])
                state_serious.append(state)
    df["political_opinion"] = political_opinion
    df["state"] = state_serious
    df.to_csv("/Users/or.gelkop/Downloads/lending_club_loan_dataset_with_political_opinion.csv", index=False)
    #return df


if __name__ == '__main__':
    political_opinion_serious = scraping_political_opinion_data()
    add_data_to_df(political_opinion_serious)
