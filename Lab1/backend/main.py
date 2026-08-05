from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pymysql
from pymysql.cursors import DictCursor
from datetime import date, datetime, time, timedelta

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zxcvbnm",
    "database": "dbms",
    "cursorclass": DictCursor 
}

class CrimeRecordResponse(BaseModel):
    crime_id: int = Field(None, alias="Crime Id")
    original_crime_type_name: str = Field(..., alias="Original Crime Type Name")
    report_date: date = Field(..., alias="Report Date")
    call_date: date = Field(..., alias="Call Date")
    offense_date: date = Field(..., alias="Offense Date")
    call_time: time = Field(..., alias="Call Time")
    call_date_time: Optional[datetime] = Field(..., alias="Call Date Time")
    disposition: str = Field(..., alias="Disposition")
    address: str = Field(..., alias="Address")
    city: str = Field(..., alias="City")
    state: str = Field(..., alias="State")
    address_type: str = Field(..., alias="Address Type")
    case_status: Optional[str] = Field(None, alias="Case Status")

class CrimeRecordUpdate(BaseModel):
    original_crime_type_name: Optional[str] = Field(None, alias="Original Crime Type Name")
    report_date: Optional[date] = Field(None, alias="Report Date")
    call_date: Optional[date] = Field(None, alias="Call Date")
    offense_date: Optional[date] = Field(None, alias="Offense Date")
    call_time: Optional[time] = Field(None, alias="Call Time")
    call_date_time: Optional[datetime] = Field(None, alias="Call Date Time")
    disposition: Optional[str] = Field(None, alias="Disposition")
    address: Optional[str] = Field(None, alias="Address")
    city: Optional[str] = Field(None, alias="City")
    state: Optional[str] = Field(None, alias="State")
    address_type: Optional[str] = Field(None, alias="Address Type")
    case_status: Optional[str] = Field(None, alias="Case Status")

class CrimeRecordCreate(BaseModel):
    crime_id: int = Field(..., alias="Crime Id")
    original_crime_type_name: str = Field(..., alias="Original Crime Type Name")
    report_date: date = Field(..., alias="Report Date")
    call_date: date = Field(..., alias="Call Date")
    offense_date: date = Field(..., alias="Offense Date")
    call_time: time = Field(..., alias="Call Time")
    # call_date_time: datetime = Field(..., alias="Call Date Time")
    disposition: str = Field(..., alias="Disposition")
    address: str = Field(..., alias="Address")
    city: str = Field(..., alias="City")
    state: str = Field(..., alias="State")
    address_type: str = Field(..., alias="Address Type")
    case_status: Optional[str] = Field(None, alias="Case Status")
# ==========================================
# 3. FastAPI Application Setup
# ==========================================
app = FastAPI(title="Crime Records API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()

# ==========================================
# 4. API Endpoint with Comprehensive Filters
# ==========================================
@app.get("/crimes", response_model=List[CrimeRecordResponse])
def get_crimes(
    # Pagination
    limit: int = Query(1500, ge=1, description="Max rows to return"),
    skip: int = Query(0, ge=0, description="Rows to skip"),
    
    # Date Range Filters
    report_start_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    report_end_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    call_start_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    call_end_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    offense_start_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    offense_end_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    
    # Other Column Filters
    crime_id: Optional[int] = None,
    crime_type: Optional[str] = Query(None, description="Original Crime Type Name"),
    disposition: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    address_type: Optional[str] = None,
    status: Optional[str] = None,
    
    # DB Connection Dependency
    conn = Depends(get_db_connection)
):
    with conn.cursor() as cursor:
        # 1. Base Query
        sql = """
            SELECT  `Crime Id`, `Original Crime Type Name`, `Report Date`, 
                   `Call Date`, `Offense Date`, `Call Time`, `Call Date Time`, 
                   `Disposition`, `Address`, `City`, `State`, 
                   `Address Type`, `Case Status` 
            FROM crime_data
        """
        
        conditions = []
        values = []

        # 2. Safely apply Date Range Filters
        if report_start_date:
            conditions.append("`Report Date` >= %s")
            values.append(report_start_date)
        if report_end_date:
            conditions.append("`Report Date` <= %s")
            values.append(report_end_date)
            
        if call_start_date:
            conditions.append("`Call Date` >= %s")
            values.append(call_start_date)
        if call_end_date:
            conditions.append("`Call Date` <= %s")
            values.append(call_end_date)
            
        if offense_start_date:
            conditions.append("`Offense Date` >= %s")
            values.append(offense_start_date)
        if offense_end_date:
            conditions.append("`Offense Date` <= %s")
            values.append(offense_end_date)

        # 3. Safely apply Standard Filters
        if crime_id is not None:
            conditions.append("`Crime Id` = %s")
            values.append(crime_id)
        if crime_type:
            conditions.append("`Original Crime Type Name` = %s")
            values.append(crime_type)
        if disposition:
            conditions.append("`Disposition` = %s")
            values.append(disposition)
        if address:
            conditions.append("`Address` = %s")
            values.append(address)
        if city:
            conditions.append("`City` = %s")
            values.append(city)
        if state:
            conditions.append("`State` = %s")
            values.append(state)
        
        if address_type:
            conditions.append("`Address Type` = %s")
            values.append(address_type)
        if status:
            conditions.append("`Case Status` = %s")
            values.append(status)

        # 4. Assemble WHERE clause if conditions exist
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        # 5. Add Pagination
        sql += " LIMIT %s OFFSET %s"
        values.extend([limit, skip])
        
        # 6. Execute safely
        cursor.execute(sql, tuple(values))
        records = cursor.fetchall()

        # 7. Format MySQL TimeDelta to Python Time Objects for Pydantic
        for row in records:
            call_duration = row.get("Call Time")
            if isinstance(call_duration, timedelta):
                total_seconds = int(call_duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                row["Call Time"] = time(hour=hours, minute=minutes, second=seconds)
                    
        return records


@app.post("/crimes", status_code=201)
def create_crime(
    crime_data: CrimeRecordCreate, 
    conn = Depends(get_db_connection)
):
    """
    Insert a new crime record into the database.
    """
    # 1. Convert the Pydantic model to a dictionary mapping to DB column names
    insert_data = crime_data.model_dump(by_alias=True)
    
    # 2. Dynamically build the columns and placeholders for the SQL query
    columns = [f"`{col}`" for col in insert_data.keys()]
    placeholders = ["%s"] * len(insert_data)
    values = tuple(insert_data.values())
    
    sql = f"""
        INSERT INTO crime_data ({', '.join(columns)}) 
        VALUES ({', '.join(placeholders)})
    """

    try:
        with conn.cursor() as cursor:
            # 3. Execute the insert safely
            cursor.execute(sql, values)
            
            # 4. Commit the transaction to save the changes
            conn.commit()
            
            # Retrieve the auto-generated S.No. (if applicable)
            inserted_id = cursor.lastrowid
            
        return {
            "message": "Record inserted successfully",
            "crime_id": crime_data.crime_id
        }
        
    except pymysql.err.IntegrityError as e:
        # Handle cases where the user tries to insert a duplicate Crime Id (if it's constrained)
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database Integrity Error: {str(e)}")
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.patch("/crimes/{crime_id}")
def update_crime(
    crime_id: int, 
    crime_data: CrimeRecordUpdate, 
    conn = Depends(get_db_connection)
):
    """
    Update specific fields of an existing crime record by its Crime Id.
    """
    # 1. Extract only the fields the user actually sent in the request body
    # exclude_unset=True ensures we don't update missing fields to null
    # by_alias=True converts the python variable names to your DB column names
    update_data = crime_data.model_dump(exclude_unset=True, by_alias=True)
    
    # 2. Prevent empty updates
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update.")

    # 3. Dynamically build the SET clause for the SQL query
    set_clauses = []
    values = []
    
    for column, value in update_data.items():
        set_clauses.append(f"`{column}` = %s")
        values.append(value)
        
    # Combine the SET clauses into the final SQL string
    sql = f"UPDATE crime_data SET {', '.join(set_clauses)} WHERE `Crime Id` = %s"
    
    # Add the crime_id to the end of the values list for the WHERE clause
    values.append(crime_id)

    with conn.cursor() as cursor:
        # 4. Execute the update safely
        cursor.execute(sql, tuple(values))
        
        # 5. Commit the transaction (Crucial for UPDATE/INSERT/DELETE)
        conn.commit()
        
        # 6. Check if the record existed
        if cursor.rowcount == 0:
            # Note: rowcount is also 0 if the new values are identical to the old values in MySQL
            raise HTTPException(
                status_code=404, 
                detail="Crime record not found, or no new changes were made."
            )
            
    return {
        "message": "Record updated successfully", 
        "updated_fields": list(update_data.keys())
    }