import json

from django.http import QueryDict
from rest_framework import parsers


class MultipartJsonParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context
        )

        # find the data field and parse it
        qdict = QueryDict('', mutable=True)
        if 'data' in result.data:
            try:
                data = json.loads(result.data['data'])
            except json.decoder.JSONDecodeError:
                pass
            else:
                qdict.update(data)
        return parsers.DataAndFiles(qdict, result.files)
