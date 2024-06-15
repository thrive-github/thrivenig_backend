# Make sure you have a serializer for Flight
from amadeus import Client, ResponseError
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
import json
from amadeus import Client, ResponseError, Location
from django.shortcuts import render
from django.contrib import messages
from .flight import Flight
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
import ast
from .booking import Booking
from django.conf import settings


amadeus = Client(
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET
)


def demo(request):
    origin = request.POST.get('Origin')
    destination = request.POST.get('Destination')
    departureDate = request.POST.get('Departuredate')
    returnDate = request.POST.get('Returndate')
    adults = request.POST.get('Adults')

    if not adults:
        adults = 1

    kwargs = {'originLocationCode': origin,
              'destinationLocationCode': destination,
              'departureDate': departureDate,
              'adults': adults
              }

    tripPurpose = ''
    if returnDate:
        kwargs['returnDate'] = returnDate
        try:
            trip_purpose_response = amadeus.travel.predictions.trip_purpose.get(
                **kwargs).data
            tripPurpose = trip_purpose_response['result']
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error)
            return render(request, 'demo_form.html', {})

    if origin and destination and departureDate:
        try:
            flight_offers = amadeus.shopping.flight_offers_search.get(**kwargs)
            prediction_flights = amadeus.shopping.flight_offers.prediction.post(
                flight_offers.result)
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error)
            return render(request, 'demo_form.html', {})
        flights_offers_returned = []
        for flight in flight_offers.data:
            offer = Flight(flight).construct_flights()
            flights_offers_returned.append(offer)

        prediction_flights_returned = []
        for flight in prediction_flights.data:
            offer = Flight(flight).construct_flights()
            prediction_flights_returned.append(offer)

        return render(request, 'results.html', {'response': flights_offers_returned,
                                                'prediction': prediction_flights_returned,
                                                'origin': origin,
                                                'destination': destination,
                                                'departureDate': departureDate,
                                                'returnDate': returnDate,
                                                'tripPurpose': tripPurpose,
                                                })
    return render(request, 'demo_form.html', {})

# using response react view


@api_view(['GET', 'POST'])
def flight(request):
    if request.method == 'GET':
        response_data = {
            'message': 'Use POST method to search for flights. Provide the following fields: departureCity, arrivalCity, departureDate, returnDate (optional), adults (optional), children (optional), infants (optional).'
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        origin = request.data.get('departureCity')
        destination = request.data.get('arrivalCity')
        departureDate = request.data.get('departureDate')
        returnDate = request.data.get('returnDate')
        adults = request.data.get('adults', 1)
        children = request.data.get('children', 0)
        infants = request.data.get('infants', 0)

        if not origin or not destination or not departureDate:
            return JsonResponse({'error': 'Missing required fields: departureCity, arrivalCity, departureDate'}, status=status.HTTP_400_BAD_REQUEST)

        kwargs = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departureDate,
            'adults': adults,
            'children': children,
            'infants': infants,
        }

        if returnDate:
            kwargs['returnDate'] = returnDate

        tripPurpose = ''
        if returnDate:
            try:
                trip_purpose_response = amadeus.travel.predictions.trip_purpose.get(
                    **kwargs).data
                tripPurpose = trip_purpose_response['result']
            except ResponseError as error:
                return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flight_offers = amadeus.shopping.flight_offers_search.get(**kwargs)
            prediction_flights = amadeus.shopping.flight_offers.prediction.post(
                flight_offers.result)
        except ResponseError as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        flights_offers_returned = []
        for flight in flight_offers.data:
            offer = Flight(flight).construct_flights()
            flights_offers_returned.append(offer)

        prediction_flights_returned = []
        for flight in prediction_flights.data:
            offer = Flight(flight).construct_flights()
            prediction_flights_returned.append(offer)

        response_data = {
            'response': flights_offers_returned,
            'prediction': prediction_flights_returned,
            'origin': origin,
            'destination': destination,
            'departureDate': departureDate,
            'returnDate': returnDate,
            'tripPurpose': tripPurpose,
        }

        return JsonResponse(response_data)

# end


def book_flight(request, flight):
    # Create a fake traveler profile for booking
    traveler = {
        "id": "1",
        "dateOfBirth": "1982-01-16",
        "name": {"firstName": "JORGE", "lastName": "GONZALES"},
        "gender": "MALE",
        "contact": {
            "emailAddress": "jorge.gonzales833@telefonica.es",
            "phones": [
                {
                    "deviceType": "MOBILE",
                    "countryCallingCode": "34",
                    "number": "480080076",
                }
            ],
        },
        "documents": [
            {
                "documentType": "PASSPORT",
                "birthPlace": "Madrid",
                "issuanceLocation": "Madrid",
                "issuanceDate": "2015-04-14",
                "number": "00000000",
                "expiryDate": "2025-04-14",
                "issuanceCountry": "ES",
                "validityCountry": "ES",
                "nationality": "ES",
                "holder": True,
            }
        ],
    }
    # Use Flight Offers Price to confirm price and availability
    try:
        flight_price_confirmed = amadeus.shopping.flight_offers.pricing.post(
            ast.literal_eval(flight)
        ).data["flightOffers"]
    except (ResponseError, KeyError, AttributeError) as error:
        messages.add_message(request, messages.ERROR, error.response.body)
        return render(request, "demo/book_flight.html", {})

    # Use Flight Create Orders to perform the booking
    try:
        order = amadeus.booking.flight_orders.post(
            flight_price_confirmed, traveler
        ).data
    except (ResponseError, KeyError, AttributeError) as error:
        messages.add_message(
            request, messages.ERROR, error.response.result["errors"][0]["detail"]
        )
        return render(request, "demo/book_flight.html", {})

    passenger_name_record = []
    booking = Booking(order).construct_booking()
    passenger_name_record.append(booking)

    return render(request, "demo/book_flight.html", {"response": passenger_name_record})


def origin_airport_search(request):
    if request.is_ajax():
        try:
            data = amadeus.reference_data.locations.get(
                keyword=request.GET.get("term", None), subType=Location.ANY
            ).data
        except (ResponseError, KeyError, AttributeError) as error:
            messages.add_message(
                request, messages.ERROR, error.response.result["errors"][0]["detail"]
            )
    return HttpResponse(get_city_airport_list(data), "application/json")


def destination_airport_search(request):
    if request.is_ajax():
        try:
            data = amadeus.reference_data.locations.get(
                keyword=request.GET.get("term", None), subType=Location.ANY
            ).data
        except (ResponseError, KeyError, AttributeError) as error:
            messages.add_message(
                request, messages.ERROR, error.response.result["errors"][0]["detail"]
            )
    return HttpResponse(get_city_airport_list(data), "application/json")


def get_city_airport_list(data):
    result = []
    for i, val in enumerate(data):
        result.append(data[i]["iataCode"] + ", " + data[i]["name"])
    result = list(dict.fromkeys(result))
    return json.dumps(result)
