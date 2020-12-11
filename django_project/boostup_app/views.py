from django.shortcuts import redirect
from django.conf import settings

from datetime import datetime

import requests
import urllib
import json

from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view

from boostup_app.models import HubSpotUser, HubSpotDeal


@api_view(['GET'])
def oauth_authorize(request):
    # redirect to hubspot for oauth flow...
    auth_url = settings.HUBSPOT.get('AUTH_URL')
    client_id = settings.HUBSPOT.get('CLIENT_ID')
    scope = settings.HUBSPOT.get('SCOPE')
    redirect_url = settings.HUBSPOT.get('REDIRECT_URI')
    url = f'{auth_url}?client_id={client_id}&scope={scope}&redirect_uri={redirect_url}'
    return redirect(url)


@api_view(['GET'])
def oauth_redirect(request):
    # Get token...
    code = request.GET.get('code', None)
    form_data = {
        'grant_type': 'authorization_code',
        'client_id': settings.HUBSPOT.get('CLIENT_ID'),
        'client_secret': settings.HUBSPOT.get('CLIENT_SECRET'),
        'redirect_uri': settings.HUBSPOT.get('REDIRECT_URI'),
        'code': code
    }
    token_url = settings.HUBSPOT.get('TOKEN_URL')
    response = requests.post(token_url, data=form_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
    else:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    # Get token info ...
    token_info_url = f"{settings.HUBSPOT.get('TOKEN_INFO_URL')}/{access_token}"
    response = requests.get(token_info_url)
    if response.status_code == 200:
        token_info_data = response.json()
        user = token_info_data["user"]
    else:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    # check if user already exist in db
    try:
        db_user = HubSpotUser.objects.get(userid=user)
        db_user.refresh_token = refresh_token
        db_user.access_token = access_token
    except HubSpotUser.DoesNotExist as exc:
        db_user = HubSpotUser(
            userid=user,
            access_token=access_token,
            refresh_token=refresh_token
        )
    db_user.save()

    # get all deals...
    max_results = 500
    limit = 5
    hapikey = 'demo'
    deal_list = []
    get_all_deals_url = "https://api.hubapi.com/deals/v1/deal/paged?"
    parameter_dict = {'hapikey': hapikey, 'limit': limit}
    headers = {}  # {'Authorization': f'Bearer {access_token}'}

    # Paginate request using offset
    has_more = True
    while has_more:
        parameters = urllib.parse.urlencode(parameter_dict)
        get_url = get_all_deals_url + parameters
        r = requests.get(url=get_url, headers=headers)
        response_dict = json.loads(r.text)
        has_more = response_dict['hasMore']
        deal_list.extend(response_dict['deals'])
        for deal in deal_list:
            # get deal data...
            deal_id = deal["dealId"]
            deal_url = f'https://api.hubapi.com/deals/v1/deal/{deal_id}?hapikey=demo&includePropertyVersions=true'
            deal_resp = requests.get(url=deal_url, headers=headers)
            deal_resp_dict = json.loads(deal_resp.text)

            # get deal properties...
            deal_name = deal_stage = deal_close_date = deal_amount = deal_type = None
            deal_prop = deal_resp_dict["properties"]
            if deal_prop.get("dealname", None):
                deal_name = deal_prop.get("dealname", None)["value"]
            if deal_prop.get("dealstage", None):
                deal_stage = deal_prop.get("dealstage", None)["value"]
            if deal_prop.get("closedate", None):
                deal_close_date = deal_prop.get("closedate", None)["value"]
                deal_close_date = datetime.fromtimestamp(int(deal_close_date)/1000)  # rarísimo pero anda...
            if deal_prop.get("amount", None):
                deal_amount = deal_prop.get("amount", None)["value"]
            if deal_prop.get("type", None):
                deal_type = deal_prop.get("type", None)["value"]
            # create/update deal in database...
            try:
                db_deal = HubSpotDeal.objects.get(deal_id=deal_id)
                db_deal.name = deal_name
                db_deal.stage = deal_stage
                db_deal.close_date = deal_close_date
                db_deal.amount = deal_amount
                db_deal.type = deal_type
            except HubSpotDeal.DoesNotExist as exc:
                db_deal = HubSpotDeal(
                    deal_id=deal_id,
                    name=deal_name,
                    stage=deal_stage,
                    close_date=deal_close_date,
                    amount=deal_amount,
                    type=deal_type
                )
            db_deal.save()

        parameter_dict['offset'] = response_dict['offset']
        if len(deal_list) >= max_results:
            # Exit pagination
            break

    # return all deals from mongodb...
    return_data = list(HubSpotDeal.objects.values())
    return JsonResponse(return_data, safe=False)
