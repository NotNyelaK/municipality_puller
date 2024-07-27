import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from googlesearch import search
import re

def fetcher():
    # Defines the url that it will search for
    print("In fetcher")
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
        
        l_data = row.find_all('a')
        if len(l_data) > 0:
            wiki_url = l_data[0].get('href')
        c_data = row.find_all('td')
        if len(c_data) > 0:
            pop = c_data[2].get_text(strip=True) if len(c_data) > 2 else 'N/A'
            land_area = c_data[-2].get_text(strip=True) if len(c_data) > 3 else 'N/A'

        print("defining dict")
        municipality_dictionary = {
            'Name': name,
            'Recent Population': pop,
            'Land Area in km²': land_area,
            'wikilink': f"https://en.wikipedia.org{wiki_url}"
        }

        # Find longitude and latitude data
        response2 = requests.get(municipality_dictionary['wikilink'])
        spicysoup = BeautifulSoup(response2.text, 'html.parser')
        
        latitude = spicysoup.find("span", {"class": "latitude"})
        longitude = spicysoup.find("span", {"class": "longitude"})
        
        # Set latitude and longitude only if found
        mun_lat = latitude.get_text(strip=True) if latitude else 'N/A'
        mun_lon = longitude.get_text(strip=True) if longitude else 'N/A'
        
        # Add latitude and longitude to the dictionary
        municipality_dictionary['latitude'] = mun_lat
        municipality_dictionary['longitude'] = mun_lon
        
        
        # Append the complete dictionary to the municipalities list

        municipality_dictionary['official website'] = web_finder(name)
        
        print(municipality_dictionary)
        municipalities.append(municipality_dictionary)

    time.sleep(4)
    return municipalities

def web_finder(municipality_name):
    print("in web_finder")
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
    csv_export(municipalities)

if __name__ == "__main__":
    main()