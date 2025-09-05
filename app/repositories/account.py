from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from models.account import Account


class AccountRepo:
    """
    Repository for managing Account entities in the database.

    This class provides methods for CRUD operations and balance updates,
    encapsulating direct database access using SQLAlchemy AsyncSession.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an async database session.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
        """
        self.session = session

    async def get(self, account_id: int) -> Account | None:
        """
        Retrieves a single account by its ID.

        Args:
            account_id (int): The ID of the account to retrieve.

        Returns:
            Account | None: The Account instance if found, else None.
        """
        return await self.session.get(Account, account_id)

    async def list_by_user(self, user_id: int) -> list[Account]:
        """
        Retrieves all accounts associated with a specific user.

        Args:
            user_id (int): The ID of the user whose accounts to retrieve.

        Returns:
            list[Account]: List of Account instances belonging to the user.
        """
        q = await self.session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return q.scalars().all()

    async def create(self, user_id: int, account_id: int | None = None) -> Account:
        """
        Creates a new account for a user. Optionally, a specific account ID can be assigned.

        Args:
            user_id (int): The ID of the user to associate the account with.
            account_id (int | None): Optional ID for the account. Defaults to None.

        Returns:
            Account: The newly created Account instance.
        """
        acc = Account()
        if account_id is not None:
            acc.id = account_id
        acc.user_id = user_id
        self.session.add(acc)
        await self.session.flush()
        return acc

    async def create_if_not_exists(self, user_id: int, account_id: int | None = None) -> Account:
        stmt = insert(Account).values(
            id=account_id,
            user_id=user_id
        ).on_conflict_do_nothing(
            index_elements=['id']
        )

        await self.session.execute(stmt)
        account = await self.get_account_for_update(account_id)
        return account


    async def update_balance(self, account: Account, new_balance) -> None:
        """
        Updates the balance of an existing account.

        Args:
            account (Account): The Account instance to update.
            new_balance (decimal.Decimal | float): The new balance to set.
        """
        account.balance = new_balance

    async def get_account_for_update(self, account_id: int):
        """
        Retrieves an account by ID and locks it for update using 'SELECT ... FOR UPDATE'.

        This is useful to prevent race conditions when modifying the balance
        in concurrent transactions.

        Args:
            account_id (int): The ID of the account to lock and retrieve.

        Returns:
            Account | None: The Account instance if found, else None.
        """
        result = await self.session.execute(
            select(Account).where(Account.id == account_id).with_for_update()
        )
        return result.scalar_one_or_none()
