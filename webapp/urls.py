# yourappname/urls.py
from django.urls import path
from .views import (home,
your_location_view,
                    # recommend_on_location,
                    process_selected_restaurant
                    )

urlpatterns = [
    path('', home, name='home'),
    path('your-location-url/', your_location_view, name='your_location_view_name'),

    # path('recommend_on_location/', recommend_on_location, name='recommend_on_location'),
    path('process_selected_restaurant/', process_selected_restaurant, name='process_selected_restaurant'),
]