#!/usr/bin/python

import sys
import requests
import threading
from plyer import notification
from prettytable import PrettyTable


def filterCity(response, date):
    # Cities used to filter result
    cities = ['Essunga', 'Falköping', 'Grästorp', 'Gullspång', 'Götene', 'Hjo', 'Karlsborg',
              'Lidköping', 'Mariestad', 'Skara', 'Skövde', 'Tibro', 'Tidaholm', 'Töreboda', 'Vara']
    result = []
    # Append clinique to result list if all requirements are valid
    for clinique in response:
        if clinique['hasWebTimebook'] == True and clinique['city'] in cities and filterApointmentType(clinique, date):
            result.append(clinique)

    return result


def filterApointmentType(clinique, date):
    # Covid catagory ids 
    cat_ids = ['2596', '6898', '1348', '6680']  # TODO: Check if there is an enpoint for retriving all categories with ids
    
    # Appointment types endpoint
    appointmentTypes = requests.get(
        f'https://booking-api.mittvaccin.se/clinique/{clinique["id"]}/appointmentTypes').json()

    for type in appointmentTypes:
        if type['categoryId'] in cat_ids and checkSlots(clinique, type, date):
            return True

    return False


def checkSlots(clinique, type, date):
    
    # Appointment endpoint
    appointments = requests.get(
        f'https://booking-api.mittvaccin.se/clinique/{clinique["id"]}/appointments/{type["id"]}/slots/{date}').json()

    # Checks if there are any appointmens available
    for appointment in appointments:
        if len(appointment['slots']) > 0:
            for slot in appointment['slots']:
                if slot['available'] == True:
                    return True
    return False


def main(minutes, date):

    threading.Timer(60 * int(minutes), main).start()

    try:
        # Create console table for output
        table = PrettyTable()
        table.field_names = ["ID", "City", "Name"]

        # Clinique endpoint
        response = requests.get(
            'https://booking-api.mittvaccin.se/clinique/').json()

        cliniques = filterCity(response, date)

        # If there are any cliniques add and display them in the console table
        if len(cliniques) != 0:
            for clinique in cliniques:
                table.add_row(
                    [clinique['id'], clinique['city'], clinique['name']])

            # Creates a notofication when an appointment is found
            title = 'Appointment found!'
            message = f"An appointment for Covid-19 was found check the console"
            notification.notify(title=title,
                                message=message,
                                timeout=10,
                                toast=False)

            # Print result in the console
            print(f"{title}\r\n{table}")
        else:
            print(f"No available appointments. (Retrying in {str(minutes)} minutes)")

    except Exception as ex:
        print(f"Exception raised: {ex}")

def test_main():
    response = requests.get(
            'https://booking-api.mittvaccin.se/clinique/').json()

    cliniques = filterCity(response, '10719-210725')
    assert cliniques is not None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Error: no arguments passed")
