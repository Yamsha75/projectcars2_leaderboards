from typing import List

from sqlalchemy.orm.exc import DetachedInstanceError


class BaseMixin(object):
    _repr_fields: List[str]

    def __repr__(self):
        fields_output = []
        for field in self._repr_fields:
            try:
                fields_output.append(f"{field}={repr(getattr(self, field))}")
            except DetachedInstanceError:
                fields_output.append(f"{field}=DetachedInstanceError")
        text = ",".join(fields_output)
        return f"{self.__class__.__name__}({text})"
