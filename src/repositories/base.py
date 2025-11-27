from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel

from src.schemas.hotels import Hotel


class BaseRepository:
    """
    Abstract base repository class that provides common database operations.

    This class implements the Repository pattern and provides generic
    methods for CRUD operations (Create, Read, Update, Delete) on any
    SQLAlchemy model. It is designed to be inherited by specific repository
    classes that define the actual model and schema to work with.

    Attributes:
        model (type): The SQLAlchemy ORM model class that this repository manages.
                     Should be set in subclasses.
        schema (type[BaseModel]): The Pydantic schema class used for data validation
                                 and serialization. Should be set in subclasses.
    """
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        """
        Initialize the repository with a database session.

        Args:
            session: An active SQLAlchemy async session used for database operations.
                    This session will be used for all database interactions
                    performed by this repository instance.
        """
        self.session = session

    async def get_all(self, *args, **kwargs):
        """
        Retrieve all records of the model from the database.

        Executes a SELECT query to fetch all instances of the model and
        converts them to Pydantic schema objects.

        Args:
            *args: Variable length argument list (not used in this method).
            **kwargs: Arbitrary keyword arguments (not used in this method).

        Returns:
            list: A list of schema objects representing all records in the table.
                 Returns an empty list if no records exist.
                 Each ORM model instance is converted to the specified schema
                 using model_validate with from_attributes=True.
        """
        query = select(self.model)
        result = await self.session.execute(query)

        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_one_or_none(self, **filter_by):
        """
        Retrieve a single record that matches the filter criteria.

        Executes a SELECT query with filter conditions and returns one
        matching record or None if no record matches.

        Args:
            **filter_by: Keyword arguments representing filter conditions.
                        These are passed directly to SQLAlchemy's filter_by()
                        method. For example, id=1, name="Hotel" would filter
                        by id equals 1 and name equals "Hotel".

        Returns:
            Optional: A schema object representing the matching record,
                     or None if no record matches the criteria.
                     The ORM model is converted to the specified schema
                     using model_validate with from_attributes=True.

        Note:
            The compiled SQL query is printed with literal values for
            debugging purposes. This should be removed or disabled in
            production environments.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: BaseModel):
        """
        Add a new record to the database.

        Inserts a new record using the provided data and returns the
        created record as a schema object.

        Args:
            data (BaseModel): A Pydantic model instance containing the data
                             to be inserted. The data is converted to a dictionary
                             using model_dump() and used as values for the INSERT.

        Returns:
            The created record as a schema object. The returned object includes
            any database-generated fields (like auto-incremented ID) since
            the method uses RETURNING to get the full inserted row.

        Note:
            The method uses RETURNING clause to immediately get the inserted
            row, including any database-generated values.
        """
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        model = result.scalars().one()
        return self.schema.model_validate(model, from_attributes=True)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        """
        Update existing record(s) in the database.

        Modifies existing record(s) that match the filter criteria with
        the provided data.

        Args:
            data (BaseModel): A Pydantic model instance containing the new values.
                            If exclude_unset is True, only fields that were
                            explicitly set when creating the model instance
                            will be updated.
            exclude_unset (bool): If True, only update fields that were explicitly
                                set in the data model. If False, update all fields,
                                setting unspecified ones to None/default values.
            **filter_by: Keyword arguments representing filter conditions to
                        identify which record(s) to update. Passed to filter_by().

        Returns:
            None: This method does not return any value.

        Note:
            The update is performed asynchronously and the changes are not
            committed to the database - the caller is responsible for committing
            the transaction.
        """
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        """
        Delete record(s) from the database.

        Removes record(s) that match the specified filter criteria.

        Args:
            **filter_by: Keyword arguments representing filter conditions to
                        identify which record(s) to delete. Passed to filter_by().

        Returns:
            None: This method does not return any value.

        Note:
            The deletion is performed asynchronously and the changes are not
            committed to the database - the caller is responsible for committing
            the transaction.
        """
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
