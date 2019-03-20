import peewee as pw
from models.base_model import BaseModel
# from models.user import User

class Following(BaseModel):
    fan_id = pw.IntegerField(null=False, index=True) #IntegerField was used instead of ForeignKeyField to prevent circular import errors
    idol_id = pw.IntegerField(null=False, index=True) #IntegerField was used instead of ForeignKeyField to prevent circular import errors
    is_approved = pw.BooleanField(default=False)

    class Meta:
        # `indexes` is a tuple of 2-tuples, where the 2-tuples are
        # a tuple of column names to index and a boolean indicating
        # whether the index is unique or not.
        indexes = (
            # Specify a unique multi-column index on fan_id/idol_id.
            (('fan_id', 'idol_id'), True),
        )