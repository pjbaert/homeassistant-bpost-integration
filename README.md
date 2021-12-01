# My bpost integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sdebruyn/homeassistant-bpost-integration/main.svg)](https://results.pre-commit.ci/latest/github/sdebruyn/homeassistant-bpost-integration/main)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/sdebruyn/homeassistant-bpost-integration/Validate/main)
![GitHub](https://img.shields.io/github/license/sdebruyn/my-bpost-api)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

This is a custom component for [Home Assistant](https://home-assistant.io/)
that allows you to see the mail you are going to receive.

This integration requires you to create and configure an account in the [my bpost app](https://www.bpost.be/en/my-bpost-app).
You need to have _My Mail_ correctly setup within the app to use this integration.

## Features

Only features with a ☑️ are available at the moment. Other features are planned for the future.

### Entities

#### Sensor

* [x] The amount of mail you will receive today: `bpost_sensor_mail_today` (extra attribute containing unique IDs of the mail)
* [ ] Information about parcels you're tracking

#### Binary sensor

* [x] If mail has been processed today: `bpost_binary_sensor_mail_processed_today`
* [x] If you've configured the mail service correctly: `bpost_binary_sensor_mail_service_available`
* [ ] If you're expecting a parcel

#### Camera

* [x] Pictures of the mail you will receive. The image will be available with a unique ID in the form `bpost_camera_id`.
    The list of IDs can be found in the `bpost_sensor_mail_today` extra attribute.
    This entity has an extra attribute `expected_delivery_date` with a timestamp indicating when the mail should arrive.

### Services

* [ ] Start tracking a new parcel

## Installation

### Installing the integration as a custom component

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. Open HACS > Integrations and press the top right button to add a custom repository.
3. Enter `https://github.com/sdebruyn/homeassistant-bpost-integration` as repository and `Integration` as category.
4. Download the integration in HACS (should have appeared in your HACS integrations).
5. Restart Home Assistant if this is your first custom component.

### Configure the integration in Home Assistant

1. Go to your Home Assistant settings > Integrations and add a new integration.
2. Search for `bpost` and select it.
3. Enter the email address you've used in the mobile app.
4. You will receive a verification code through email.
5. Enter the verification code you received.
6. All entities and services mentioned above are now available.

## License

MIT license

## Contributing

1. Install [poetry](https://python-poetry.org/)
2. Clone the repository
3. Install dependencies `poetry install`
4. Activate venv: `poetry shell`
5. Configure pre-commit: `pre-commit install`
6. Configure your IDE to use the poetry venv (`poetry env info`)
