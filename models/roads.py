from tortoise import fields, models


class RoadModel(models.Model):
    id = fields.IntField(pk=True)

    class Meta:
        table = "roads"
        table_description = "Roads information"
