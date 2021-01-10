# Pet Adoption

> Web application built for [Google Software Product Sprint (SPS)](https://buildyourfuture.withgoogle.com/programs/softwareproductsprint/), Summer 2020  <br>
> We built this website to provide a centralised platform for users to adopt pets, and show the pets that are up for adoption.

###### [Click here for the Website](https://petadoption-sps.herokuapp.com/)

###### [Click here for our Presentation](https://docs.google.com/presentation/d/1ypY5AXfkRWxMDJs04YtG8owsqjFshq4BGDfUrbMD1Ls/edit?usp=sharing)

### Tl;dr
1. One-stop adoption platform to connect the want-to-be owners and current caregivers together
2. Easy-to-use interface and quick adoption flow
3. Simple signing up process and authentication for users to edit the information of their pets
4. Built using [Flask](https://flask.palletsprojects.com/en/1.1.x/) as backend, [Firebase](https://firebase.google.com/) as database, HTML/CSS/JS as frontend

<br>
<br>

------------------------------------------------------------------------------

<br>
<br>

### Setup
1. Navigate to your project directory and install dependencies:
    * `cd pet-adoption`
    * `pip install  -r requirements.txt`
    * Generate a private key file for your service account. In the Firebase console, open Settings > [Service Accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).
    * Click Generate New Private Key, then confirm by clicking Generate Key.
    * Move the private key file to this project directory: `mv path/to/downloaded_key.json path/to/pet-adoption/servicekey.json`

2. Run the application
    * `python main.py`

3. In your web browser, enter the following address
    * `localhost:8080`

