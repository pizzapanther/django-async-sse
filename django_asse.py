import json
from dataclasses import dataclass
from typing import Any

from django.http import StreamingHttpResponse
from django.views import View

__version__ = "1.0.0"


@dataclass
class Event:
  data: str
  event: str = None

  def data_to_string(self):
    return self.data

  def to_content(self):
    ret = ""
    if self.event:
      ret += f"event: {self.event}\n"

    ret += f"data: {self.data_to_string()}\n\n"
    return ret

  def __str__(self):
    ret = self.to_content()
    if len(ret) >= 255:
      return ret[:253] + ' ...'

    return ret[:-2]


@dataclass
class JsonEvent(Event):
  data: Any

  def data_to_string(self):
    return json.dumps(self.data)


class SseStreamView(View):
  SSE_CONTENT_TYPE = 'text/event-stream'
  SSE_HEADERS = {
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  }

  async def get(self, request, *args, **kwargs):
    return StreamingHttpResponse(
      (self._stream(request, *args, **kwargs)),
      content_type=self.SSE_CONTENT_TYPE,
      headers=self.SSE_HEADERS
    )

  async def _stream(self, request, *args, **kwargs):
    async for event in self.stream(request, *args, **kwargs):
      yield event.to_content()
