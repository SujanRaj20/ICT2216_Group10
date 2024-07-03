from dbmodules.db_engine import get_engine

class Listing_Modules:
    @staticmethod
    def get_listing_byid(listing_id):
        engine = get_engine()
        try:
            query = f"SELECT * FROM listings WHERE id = {listing_id}"
            result = engine.execute(query).fetchone()  # Fetch one instead of fetchall
        except SQLAlchemyError as e:
            logging.error(f"Error fetching listing {listing_id}: {e}")
            result = None
        finally:
            engine.dispose()
        return result

    @staticmethod
    def fetch_seller_listings(seller_id, sort_option, category):
        engine = get_engine()
        query = f"SELECT * FROM listings WHERE seller_id = {seller_id}"

        if category != 'all':
            query += f" AND type = '{category}'"

        if sort_option == "alpha":
            query += " ORDER BY title ASC"
        elif sort_option == "dateasc":
            query += " ORDER BY created_at ASC"
        elif sort_option == "datedesc":
            query += " ORDER BY created_at DESC"
        elif sort_option == "priceasc":
            query += " ORDER BY price ASC"
        elif sort_option == "pricedesc":
            query += " ORDER BY price DESC"
        elif sort_option == "stockasc":
            query += " ORDER BY stock ASC"
        elif sort_option == "stockdesc":
            query += " ORDER BY stock DESC"

        result = engine.execute(query).fetchall()
        engine.dispose()
        return result

    @staticmethod
    def delete_listing_fromdb(listing_id):
        engine = get_engine()
        try:
            query = f"DELETE FROM listings WHERE id = {listing_id}"
            engine.execute(query)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting listing {listing_id}: {e}")
            raise
        finally:
            engine.dispose()
        
def get_seller_info(seller_id):
    engine = get_engine()
    
    try:
        # Query to fetch seller information
        query = f"""
            SELECT username, fname, lname, email, phone_num
            FROM users
            WHERE id = {seller_id}
        """
        
        # Execute the query
        with engine.connect() as connection:
            result = connection.execute(text(query)).fetchone()
        
        if result:
            seller_info = {
                'username': result['username'],
                'fname': result['fname'],
                'lname': result['lname'],
                'email': result['email'],
                'phone_num': result['phone_num']
            }
            return seller_info
        else:
            return None  # Return None if seller_id does not exist
        
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        engine.dispose()
    