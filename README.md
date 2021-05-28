# Air Quality Alert

This script sends an SMS alert when air quality is poor.  

I created the script after waking up one morning to very poor air quality due to a lot of smoke from the [2019-2020 Australian busfire season](https://en.wikipedia.org/wiki/2019-20_Australian_bushfire_season).

## APIs
Two APIs are used:  
1. EPA AirWatch API  
2. Telstra Messaging API  

### EPA AirWatch API
You can get access to the EPA AirWatch API and documentation here:  
https://portal.api.epa.vic.gov.au/  

### Telstra Messaging API
You can get access to the Telstra Messaging API and documentation here:  
https://dev.telstra.com/  

## Setup
To run this script you'll need a machine with Python3 and Internet access. Ideally with Linux but you can try to run this from other operating systems.   

### Clone the repository
```
cd ~
git clone https://github.com/TimMcMahon/air_quality_alert.git
```

### Configure permissions to execute the script
```
cd ~/air_quality_alert
chmod +x check_air_quality.py
```

### Install requests etc
```
cd ~/air_quality_alert
pip install -r requirements.txt
```

### Configuration
Copy the check_air_quality.config.json.example to check_air_quality.config.json  
check_air_quality.config.json is required for the script to work.  
```
cd ~/air_quality_alert
cp check_air_quality.config.json.example check_air_quality.config.json
```

#### Add your EPA AirWatch API key to the config file
```
{
    "epa": {
        "api_key": "",
```

#### Add your Telstra Messaging API key and secret to the config file
```
    "telstra": {
        "client_key": "",
        "client_secret": "",
```

#### Add the mobile phone numbers that you'd like to send the alert to to the config file
```
        "recipients": [
            "+61491570006"
        ]
```

### Configure the site to get air quality measurements for
Refer to EPA AirWatch API documentation to get a list of sites. The example script has three sites and Box Hill has been selected.  

### Configure the threshold
I set the threshold for PM2.5 to 100. You can choose something more appropriate for your needs.  
```
        "threshold": 100
```

### Schedule the script to run
Replace user with your username (e.g. pi if on a Raspberry Pi) in the line below.  
More info about crontab: [https://crontab.guru/#20\_\*\_\*\_\*\_\*](https://crontab.guru/#20_*_*_*_*)  
```
crontab -e
20 * * * * /home/user/air_quality_alert/check_air_quality.py >> /home/user/air_quality_alert/check_air_quality.log 2>&1
```


## Usage
```
cd ~/air_quality_alert
./check_air_quality.py
```

Example output log:

```
2021-05-28 11:14:04,027	check_air_quality	INFO	EPA AirWatch API site name: box_hill
2021-05-28 11:14:05,077	check_air_quality	INFO	EPA AirWatch API site status: HTTP 200
2021-05-28 11:14:05,078	check_air_quality	INFO	EPA AirWatch API site info: Box Hill Good 3.81 µg/m³ PM2.5
2021-05-28 11:14:05,320	check_air_quality	INFO	Telstra Messaging API access_token: HTTP 200
2021-05-28 11:14:05,612	check_air_quality	INFO	Telstra Messaging API from status: HTTP 201
2021-05-28 11:14:06,355	check_air_quality	INFO	Telstra Messaging API sms status: HTTP 201
2021-05-28 11:14:06,356	check_air_quality	INFO	Telstra Messaging API sms: {'messages': [{'to': '+61491570006', 'deliveryStatus': 'MessageWaiting', 'messageId': '88B71CFF51BFEB61813800000500A31D', 'messageStatusURL': 'https://tapi.telstra.com/v2/messages/sms/88B71CFF51BFEB61813800000500A31D/status'}], 'Country': [{'AUS': 1}], 'messageType': 'SMS', 'numberSegments': 1}
```
