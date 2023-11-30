# Django Async Server Sent Events Helpers

Helpers to make Server Sent Events in Django easier and async.

## SSE Reference

See: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

## Install

`pip install django-async-sse`

## Setup

### Write an Event Stream

`SseStreamView` is a class-based view. Add an async `stream` method that uses `yield` to send events. Otherwise known as an async iterator.

**Example SSE View:**
```python
import asyncio
from django_asse import SseStreamView, JsonEvent

class WeatherStream(SseStreamView):
  async def stream(self, request, lat, lng):
    last_update = None

    while 1:
      wp = await WeatherPoint.objects.filter(point=f"{lat},{lng}").afirst()

      if wp and wp.created != last_update:
        event = JsonEvent(event='weather', data=wp.weather_data['current'])
        last_update = wp.created
        # yield an event to send it
        yield event

      # always send a ping to keep connection from timing out
      # Note: needed for some deployments like Heroku
      yield JsonEvent(event='ping', data=None)
      await asyncio.sleep(30)
```

### Connect View to a URL

```python
urlpatterns = [
    ...
    re_path(r"weather/(-?\d{1,3}.\d{2}),(-?\d{1,3}.\d{2})/", WeatherStream.as_view()),
]
```

### Run an ASGI server

```
pip install uvicorn[standard]
uvicorn myproject.asgi:application --loop uvloop
```

## Included Helpers

- `Event`: Event where data are strings.
- `JsonEvent`: Event where data is encoded as JSON.
- `SseStreamView`: Class-based view to generate an async streaming response. Inherit from this class and add an async `stream` method that is an async iterator.
