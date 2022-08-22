from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
from time import sleep
import requests
from numpy import random

# Main Function
if __name__ == "__main__":

    # Enable Performance Logging of Chrome.
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    # Create the webdriver object and pass the arguments
    options = webdriver.ChromeOptions()

    # Chrome will start in Headless mode
    options.add_argument('headless')

    # Ignores any certificate errors if there is any
    options.add_argument("--ignore-certificate-errors")

    # Startup the chrome webdriver with executable path and
    # pass the chrome options and desired capabilities as
    # parameters.
    driver = webdriver.Chrome(executable_path="{INSERT_PATH_TO_DRIVER}",
                              chrome_options=options, desired_capabilities=desired_capabilities)

    # Send a request to the website and let it load
    driver.get(
        '{INSERT_URL_TO_SCRAPE}')

    # Sleeps for 10 seconds
    time.sleep(10)

    # Gets all the logs from performance in Chrome
    logs = driver.get_log("performance")

    # Opens a writable JSON file and writes the logs in it
    with open("network_log.json", "w", encoding="utf-8") as f:
        f.write("[")

        # Iterates every logs and parses it using JSON
        for log in logs:
            network_log = json.loads(log["message"])["message"]

            # Checks if the current 'method' key has any
            # Network related value.
            if ("Network.response" in network_log["method"]
                    or "Network.request" in network_log["method"]
                    or "Network.webSocket" in network_log["method"]):
                # Writes the network log to a JSON file by
                # converting the dictionary to a JSON string
                # using json.dumps().
                f.write(json.dumps(network_log) + ",")
        f.write("{}]")

    print("Quitting Selenium WebDriver")
    driver.quit()

    # Read the JSON File and parse it using
    # json.loads() to find the urls containing images.
    json_file_path = "network_log.json"
    with open(json_file_path, "r", encoding="utf-8") as f:
        logs = json.loads(f.read())

    url_list = []
    # Iterate the logs
    for log in logs:

        # Except block will be accessed if any of the
        # following keys are missing.
        try:
            # URL is present inside the following keys
            geojson = log["params"]["request"]["url"]

            # Checks if the extension is .png or .jpg
            if geojson[len(geojson) - 8:] == ".geojson":
                url_list.append(geojson)
        except Exception as e:
            pass

    print(url_list)

    # Define an empty dictionary
    all_dict = {"type": "FeatureCollection", "features": []}

    # Loop through list of urls
    for url in url_list:
        data = json.loads(requests.get(url).text)
        sleeptime = random.uniform(2, 6)
        print("sleeping for:", sleeptime, "seconds")
        sleep(sleeptime)
        print("sleeping is over")

        for feature in data["features"]:
            key_list = ["type", "properties", "geometry"]
            item = dict(zip(key_list, [None] * len(key_list)))

            typee = feature.get("type")
            item['type'] = typee

            properties = feature.get('properties')
            item['properties'] = properties

            geometry = feature.get('geometry')
            item['geometry'] = geometry

            all_dict["features"].append(item)

    with open('combined_files.geojson', 'w') as stream:
        json.dump(all_dict, stream)
