# DineSync - Real-Time Culinary Exploration in NYC

## Motivation and Purpose

Navigating New York City's vibrant culinary scene poses a challenge—long waiting lines and the potential to miss hidden gems. The motivation behind DineSync is to revolutionize the exploration of NYC's diverse culinary offerings by addressing the frustration of unpredictable wait times. Our data streaming application empowers users with real-time information to avoid queues and discover the best dining experiences nearby.

## Scope

DineSync leverages big data tools, including Spark, MongoDB, and Kafka, to create a seamless experience for users. Accessible through the DineSync website, users provide their current location, and the application uses geolocation services to plot nearby restaurants on an interactive map. The key characteristics for restaurant exploration include availability and cuisine type. Unlike static recommendations, DineSync offers real-time availability data for each restaurant once the user expresses interest. Live updates during the commute provide a seamless, integrated experience on the go. Continuous streaming functionality notifies users if a restaurant fills up before they complete their commute.

### Project Goals

- Utilize Spark, MongoDB, and Kafka for efficient data processing and real-time updates.
- Enable users to explore nearby restaurants based on availability and cuisine type.
- Offer real-time availability data for each restaurant upon user interest.
- Provide live updates during the user's commute for a seamless experience.
- Notify users in case a restaurant fills up before they reach their destination.

### Assumptions

- Restaurant occupancy sizes are assumed, with a static value of 100 seats available for each restaurant.
- Check-in traffic is generated internally for this short-term project.
- Restaurant owners are assumed to provide check-in real-time data for the application.

## Setup

### Prerequisites

- Python 3.x
- Django
- KAFKA
- KSQL
- Daphne
- Other dependencies (specified in requirements.txt)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/DineSync.git
   cd DineSync
2. Install dependencies:
    ```bash
   pip install -r requirements.txt
   
3. Apply migrations:
    ```bash
   python manage.py migrate

### Running the Application
    daphne -p 8000 DineSync.asgi:application
### Contributors
- Sitanshu Kushwaha
- Winnie Zheng

### License

Feel free to customize it further based on your preferences and project specifics.

   