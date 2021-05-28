#!/usr/bin/env python3
#
#   Air Quality Alert
#
#   Copyright (C) 2021 Tim McMahon <tim@timmcmahon.com.au>
#   Released under GNU GPL v3 or later
#
#   Refer to GitHub page for instructions on setup and usage.
#   https://github.com/TimMcMahon/air_quality_alert/
#
import os.path
import requests
import json
import html
import logging


logging.basicConfig(format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s')
logger = logging.getLogger('check_air_quality')
logger.setLevel(logging.INFO)


def get_epa_site(epa_api_key, epa_api_url, epa_site_id):
    epa_request = requests.get(epa_api_url + epa_site_id,
        headers={
            "Accept":"application/json",
            "User-Agent": "curl/7.58.0",
            "X-API-Key":epa_api_key
        }
    )
    
    logger.info("EPA AirWatch API site status: HTTP %s" % epa_request.status_code)
    site = epa_request.json()

    return site


def get_telstra_access_token(telstra_client_key, telstra_client_secret):
    telstra_token_request = requests.post("https://tapi.telstra.com/v2/oauth/token",
        headers = {
            "Accept":"application/json",
            "User-Agent": "curl/7.58.0"
        },
        data = {
            "grant_type": "client_credentials",
            "client_id": telstra_client_key,
            "client_secret": telstra_client_secret,
            "scope": "NSMS"
        }
    )
    
    logger.info("Telstra Messaging API access_token: HTTP %s" % telstra_token_request.status_code)
    telstra_access_token = telstra_token_request.json()["access_token"]

    return telstra_access_token


def register_bnum(telstra_access_token, recipients):
    telstra_bnum_request = requests.post("https://tapi.telstra.com/v2/messages/freetrial/bnum",
        headers={
            "Accept":"application/json",
            "User-Agent": "curl/7.58.0",
            "Authorization": "Bearer %s" % (telstra_access_token),
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        },
        data = json.dumps({
            "bnum": recipients 
        })
    )
    
    logger.info("Telstra Messaging API bnum status: HTTP %s" % telstra_bnum_request.status_code)
    telstra_bnum_response = telstra_bnum_request.json()

    return telstra_bnum_response


def get_telstra_from_number(telstra_access_token):
    telstra_from_request = requests.post("https://tapi.telstra.com/v2/messages/provisioning/subscriptions",
        headers={
            "Accept":"application/json",
            "User-Agent": "curl/7.58.0",
            "Authorization": "Bearer %s" % (telstra_access_token),
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        },
        data = json.dumps({
            "activeDays": 30
        })
    )
    
    logger.info("Telstra Messaging API from status: HTTP %s" % telstra_from_request.status_code)
    telstra_from_number = telstra_from_request.json()["destinationAddress"]

    return telstra_from_number


def send_sms(telstra_access_token, telstra_from_number, recipients, message):
    telstra_sms_request = requests.post("https://tapi.telstra.com/v2/messages/sms",
        headers={
            "Accept":"application/json",
            "User-Agent": "curl/7.58.0",
            "Authorization": "Bearer %s" % (telstra_access_token),
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        },
        data = json.dumps({
            "to": recipients,
            "from": telstra_from_number,
            "body": message,
            "validity": 5,
            "scheduledDelivery": 1,
            "replyRequest": False,
            "priority": True
        }).replace('\/', '/')
    )
    
    logger.info("Telstra Messaging API sms status: HTTP %s" % telstra_sms_request.status_code)
    telstra_sms = telstra_sms_request.json()

    return telstra_sms


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'check_air_quality.config.json')) as json_config:
        conf = json.load(json_config)

    # EPA VIC Environment Monitoring API
    epa_api_key = conf["epa"]["api_key"]
    epa_api_url = conf["epa"]["api_url"]
    epa_site = conf["epa"]["site"]
    epa_site_id = conf["epa"]["sites"][epa_site]
    threshold = conf["epa"]["threshold"]
    
    # Telstra Messaging API
    telstra_client_key = conf["telstra"]["client_key"]
    telstra_client_secret = conf["telstra"]["client_secret"]
    recipients = conf["telstra"]["recipients"]
    
    logger.info("EPA AirWatch API site name: %s" % epa_site)
    site = get_epa_site(epa_api_key, epa_api_url, epa_site_id)
    
    for advice in site['siteHealthAdvices']:
        epa_message = "%s %s %s %s %s" % (
            site["siteName"].strip(),
            advice["healthAdvice"].strip(),
            advice["averageValue"],
            html.unescape(advice["unit"].strip()),
            advice["healthParameter"].strip()
        )
        logger.info("EPA AirWatch API site info: %s" % epa_message)
    
        # Send SMS if the air quality is above threshold 
        if advice["averageValue"] > threshold and advice["healthParameter"] == "PM2.5":
            message = epa_message
            telstra_access_token = get_telstra_access_token(telstra_client_key, telstra_client_secret)
            # Call the following line once to register up to 5 recipients for the free trial
            #print(register_bnum(telstra_access_token, recipients))
            telstra_from_number = get_telstra_from_number(telstra_access_token)
            sms = send_sms(telstra_access_token, telstra_from_number, recipients, message)
            logger.info("Telstra Messaging API sms: %s" % sms)
