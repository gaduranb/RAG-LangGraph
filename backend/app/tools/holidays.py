import httpx
from datetime import datetime
from typing import List, Dict, Optional

async def get_federal_holidays(year: Optional[int] = None) -> List[Dict]:
    """
    Get US federal holidays from Nager.Date API.

    Args:
        year: Year to get holidays for. Defaults to current year.

    Returns:
        List of holidays with date, name, and type.
    """
    if year is None:
        year = datetime.now().year

    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/US"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            holidays = response.json()

            return [
                {
                    "date": h["date"],
                    "name": h["localName"],
                    "type": h.get("type", "Public")
                }
                for h in holidays
            ]
    except Exception as e:
        print(f"Error fetching holidays: {e}")
        return []

async def is_federal_holiday(date_str: Optional[str] = None) -> Dict:
    """
    Check if a given date (or today) is a US federal holiday.

    Args:
        date_str: Date in YYYY-MM-DD format. Defaults to today.

    Returns:
        Dict with is_holiday flag and holiday info if applicable.
    """
    if date_str is None:
        check_date = datetime.now().date()
    else:
        check_date = datetime.fromisoformat(date_str).date()

    holidays = await get_federal_holidays(check_date.year)

    for holiday in holidays:
        holiday_date = datetime.fromisoformat(holiday["date"]).date()
        if holiday_date == check_date:
            return {
                "is_holiday": True,
                "date": date_str or str(check_date),
                "name": holiday["name"],
                "message": f"{holiday['name']} is a federal holiday. Banking services may be limited or delayed until the next business day."
            }

    return {
        "is_holiday": False,
        "date": date_str or str(check_date),
        "message": "This is a regular business day."
    }
