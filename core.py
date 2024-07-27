import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from googlesearch import search

def fetcher():
    # Defines the url that it will search for

    url = "https://en.wikipedia.org/wiki/List_of_municipalities_in_Alberta"

    # actually pulls the url
    response = requests.get(url)

    # sets up beautiful soup to look through html
    soup = BeautifulSoup(response.text, 'html.parser')

    municipalities = []
    wikitable = soup.find('table', {'class': 'wikitable'})

    # collecting the rows in the table skipping the first row
    for row in wikitable.find_all('tr')[2:]: 
        cells = row.find_all('th')
        if len(cells) > 0: #apparently needed for index error fix
            name = cells[0].get_text(strip=True)
        c_data = row.find_all('td')
        if len(c_data) > 0:
            pop = c_data[2].get_text(strip=True) if len(c_data) > 2 else 'N/A'
            land_area = c_data[-2].get_text(strip=True) if len(c_data) > 3 else 'N/A'
            municipalities.append({'Name': name, 'Recent Population': pop, 'Land Area in km2': land_area})

    return municipalities

def web_finder(municipality_name):
    #f"<String>" allows for a variable name to be used in the string
    query = f"{municipality_name} municipality official website"
    try:
        search_town = list(search(query, num_results=1, lang='en'))
        if search_town:
            return search_town[0]
        else:
            return "Not Found"
    except Exception as e:
        print(f"Error searching for {municipality_name}: {e}")
        return "Error finding Municipality. Try broader search params."
    
def csv_export(data, filename="municipalities_alberta.csv"): #eventually needs to be modified to enable scalability
    #pandas data frame typically is called df. 
    df = pd.DataFrame(data) #also want metric data for pushing (bigger population = more focused)
    df.to_csv(filename, index=False)
    print(f"Saved csv to {filename}")

def main():
    municipalities = fetcher()

    columns = ['Name', 'Recent Population', 'Area', 'Website']
    df = pd.DataFrame(columns=columns)

    for municipality in municipalities:
        name = municipality['Name']
        print(f"Storing the municipality of {name}")
        website = web_finder(name)
        df = pd.concat([df, pd.DataFrame([{
            'Name': name,
            'Recent Population': municipality['Recent Population'],
            'Land Area in km2': municipality['Land Area in km2'],
            'Website': website
        }])], ignore_index=True)

        time.sleep(4)

        csv_export(df)

if __name__ == "__main__":
    main()