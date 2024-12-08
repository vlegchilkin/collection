import dataclasses as dc


@dc.dataclass
class OuterRelease:
    folder: str
    year: str
    month: str
    product_no: str | None
    total: int
    caption: str | None
    collection: dict
