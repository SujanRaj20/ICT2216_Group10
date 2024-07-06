from modules.db_engine import get_engine


import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, text, DECIMAL, JSON, DATE
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime
import os


class Buyer_Cart:
    # @staticmethod
    # def add_to_cart(user_id, listing_id):
    #     engine = get_engine()
    #     try:
    #         # Get the user's cart
    #         user_cart = Buyer_Cart.get_user_cart(user_id)  # Corrected

    #         cart_id = user_cart['id']
            
    #         # Check if the item already exists in the cart
    #         check_query = f"""
    #             SELECT * FROM cart_items 
    #             WHERE cart_id = '{cart_id}' AND listing_id = '{listing_id}'
    #         """
    #         existing_item = engine.execute(check_query).fetchone()
            
    #         # Get the price of the item from the listing table
    #         price_query = f"SELECT price FROM listings WHERE id = '{listing_id}'"
    #         listing = engine.execute(price_query).fetchone()
    #         if not listing:
    #             return {'error': 'Listing not found.'}
            
    #         price = listing['price']
            
    #         if existing_item:
    #             # Update the quantity if the item already exists
    #             new_quantity = existing_item['quantity'] + 1
    #             update_query = f"""
    #                 UPDATE cart_items 
    #                 SET quantity = '{new_quantity}' 
    #                 WHERE cart_id = '{cart_id}' AND listing_id = '{listing_id}'
    #             """
    #             engine.execute(update_query)
    #         else:
    #             # Insert a new item if it doesn't exist
    #             insert_query = f"""
    #                 INSERT INTO cart_items (cart_id, listing_id, quantity) 
    #                 VALUES ('{cart_id}', '{listing_id}', 1)
    #             """
    #             engine.execute(insert_query)
                
    #         # Update the item_count and total_price in the carts table
    #         new_item_count = user_cart['item_count'] + 1
    #         new_total_price = user_cart['total_price'] + price
    #         update_cart_query = f"""
    #             UPDATE carts 
    #             SET item_count = '{new_item_count}', total_price = '{new_total_price}'
    #             WHERE id = '{cart_id}'
    #         """
    #         engine.execute(update_cart_query)
                
    #         return {'message': 'Item added to cart successfully.'}
        
    #     except SQLAlchemyError as e:
    #         print(f"Error: {e}")
    #         return {'error': str(e)}
    #     finally:
    #         engine.dispose()


    @staticmethod
    def add_to_cart(user_id, listing_id):
        engine = get_engine()
        try:
            # Get the user's cart
            user_cart = Buyer_Cart.get_user_cart(user_id)
            cart_id = user_cart['id']
            
            # Check if the item already exists in the cart
            check_query = f"""
                SELECT * FROM cart_items 
                WHERE cart_id = '{cart_id}' AND listing_id = '{listing_id}'
            """
            existing_item = engine.execute(check_query).fetchone()
            
            # Get the price and stock of the item from the listing table
            listing_query = f"SELECT price, stock FROM listings WHERE id = '{listing_id}'"
            listing = engine.execute(listing_query).fetchone()
            if not listing:
                return {'error': 'Listing not found.'}
            
            price = listing['price']
            stock = listing['stock']
            
            if existing_item:
                new_quantity = existing_item['quantity'] + 1
                if new_quantity > stock:
                    return {'error': 'Cannot add more than available stock.'}
                # Update the quantity if the item already exists
                update_query = f"""
                    UPDATE cart_items 
                    SET quantity = '{new_quantity}' 
                    WHERE cart_id = '{cart_id}' AND listing_id = '{listing_id}'
                """
                engine.execute(update_query)
            else:
                if stock < 1:
                    return {'error': 'Cannot add item to cart, no stock available.'}
                # Insert a new item if it doesn't exist
                insert_query = f"""
                    INSERT INTO cart_items (cart_id, listing_id, quantity) 
                    VALUES ('{cart_id}', '{listing_id}', 1)
                """
                engine.execute(insert_query)
                
            # Update the item_count and total_price in the carts table
            new_item_count = user_cart['item_count'] + 1
            new_total_price = user_cart['total_price'] + price
            update_cart_query = f"""
                UPDATE carts 
                SET item_count = '{new_item_count}', total_price = '{new_total_price}'
                WHERE id = '{cart_id}'
            """
            engine.execute(update_cart_query)
                
            return {'message': 'Item added to cart successfully.'}
        
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding to cart user_id {user_id} listing_id {listing_id}: {e}")
            return {'error': str(e)}
        finally:
            engine.dispose()

            


    @staticmethod
    def get_user_cart(user_id):  # Corrected to staticmethod
        engine = get_engine()
        try:
            query = f"SELECT * FROM carts WHERE user_id = '{user_id}'"
            result = engine.execute(query).fetchone()
            
            # If no cart exists, create a new cart
            if result is None:
                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_query = f"""
                        INSERT INTO carts (user_id, item_count, total_price, created_at) 
                        VALUES ('{user_id}', 0, 0.0, '{created_at}')
                    """
                engine.execute(insert_query)
                # Fetch the newly created cart
                result = engine.execute(query).fetchone()
                
            return result
        
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error getting user cart user_id {user_id}: {e}")
            return None
        finally:
            engine.dispose()
    
    @staticmethod            
    def get_cart_items(userid):
        engine = get_engine()
        try:
            # Get the user's cart
            user_cart = Buyer_Cart.get_user_cart(userid)  # Corrected

            cart_id = user_cart['id']
            
            query = f"""
                SELECT ci.listing_id, l.imagepath, l.title, l.price, ci.quantity, ci.id
                FROM cart_items ci
                JOIN listings l ON ci.listing_id = l.id
                WHERE ci.cart_id = '{cart_id}'
            """
            cart_items = engine.execute(query).fetchall()
            
            return cart_items
        
        except SQLAlchemyError as e:
            print(f"Error: {e}")
            return None
        finally:
            engine.dispose()
    
    @staticmethod        
    def update_cart_totals(cart_id):
        engine = get_engine()
        try:
            # Calculate the new total price and item count
            total_price_query = f"""
                SELECT SUM(ci.quantity * l.price) as total_price, SUM(ci.quantity) as item_count
                FROM cart_items ci
                JOIN listings l ON ci.listing_id = l.id
                WHERE ci.cart_id = '{cart_id}'
            """
            totals = engine.execute(total_price_query).fetchone()

            total_price = totals['total_price'] if totals['total_price'] else 0
            item_count = totals['item_count'] if totals['item_count'] else 0

            # Update the carts table with the new totals
            update_query = f"""
                UPDATE carts
                SET total_price = '{total_price}', item_count = '{item_count}'
                WHERE id = '{cart_id}'
            """
            engine.execute(update_query)

        except SQLAlchemyError as e:
            current_app.logger.error(f"Error updating cart totals: {e}")
        finally:
            engine.dispose()

    @staticmethod
    def get_user_cart_value(userid):
        user_cart = Buyer_Cart.get_user_cart(userid)  # Corrected
        cart_value = user_cart['total_price']
        
        return cart_value
    
    @staticmethod
    def get_user_cart_item_count(userid):
        try:
            cart = Buyer_Cart.get_user_cart(userid)  # Corrected
            cart_count = cart['item_count']
            return cart_count
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error: {e}")
            return None

    # @staticmethod
    # def increase_cart_item_quantity(cart_item_id, user_id):
    #     engine = get_engine()
    #     try:
    #         # Check if the cart item exists and belongs to the user
    #         query = f"""
    #             SELECT ci.*, c.id as cart_id, c.user_id FROM cart_items ci
    #             JOIN carts c ON ci.cart_id = c.id
    #             WHERE ci.id = '{cart_item_id}' AND c.user_id = '{user_id}'
    #         """
    #         cart_item = engine.execute(query).fetchone()
            
    #         if cart_item:
    #             # Increase the quantity
    #             new_quantity = cart_item['quantity'] + 1
    #             update_query = f"""
    #                 UPDATE cart_items
    #                 SET quantity = '{new_quantity}'
    #                 WHERE id = '{cart_item_id}'
    #             """
    #             engine.execute(update_query)

    #             # Update cart totals
    #             Buyer_Cart.update_cart_totals(cart_item['cart_id'])  # Corrected

    #             return {'success': True}
    #         else:
    #             return {'success': False, 'error': 'Cart item not found or does not belong to user'}
    #     except SQLAlchemyError as e:
    #         return {'success': False, 'error': str(e)}
    #     finally:
    #         engine.dispose()
            

    @staticmethod
    def increase_cart_item_quantity(cart_item_id, user_id):
        engine = get_engine()
        try:
            # Check if the cart item exists and belongs to the user
            query = f"""
                SELECT ci.*, c.id as cart_id, c.user_id, l.stock as max_stock FROM cart_items ci
                JOIN carts c ON ci.cart_id = c.id
                JOIN listings l ON ci.listing_id = l.id
                WHERE ci.id = '{cart_item_id}' AND c.user_id = '{user_id}'
            """
            cart_item = engine.execute(query).fetchone()
            
            if cart_item:
                # Check if the current quantity is less than the max stock
                if cart_item['quantity'] < cart_item['max_stock']:
                    # Increase the quantity
                    new_quantity = cart_item['quantity'] + 1
                    update_query = f"""
                        UPDATE cart_items
                        SET quantity = '{new_quantity}'
                        WHERE id = '{cart_item_id}'
                    """
                    engine.execute(update_query)

                    # Update cart totals
                    Buyer_Cart.update_cart_totals(cart_item['cart_id'])

                    return {'success': True}
                else:
                    return {'success': False, 'error': 'Maximum stock reached'}
            else:
                return {'success': False, 'error': 'Cart item not found or does not belong to user'}
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error increasing cart item quantity: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            engine.dispose()


    @staticmethod
    def decrease_cart_item_quantity(cart_item_id, user_id):
        engine = get_engine()
        try:
            # Check if the cart item exists and belongs to the user
            query = f"""
                SELECT ci.*, c.id as cart_id, c.user_id FROM cart_items ci
                JOIN carts c ON ci.cart_id = c.id
                WHERE ci.id = '{cart_item_id}' AND c.user_id = '{user_id}'
            """
            cart_item = engine.execute(query).fetchone()
            
            if cart_item:
                if cart_item['quantity'] > 1:
                    # Decrease the quantity
                    new_quantity = cart_item['quantity'] - 1
                    update_query = f"""
                        UPDATE cart_items
                        SET quantity = '{new_quantity}'
                        WHERE id = '{cart_item_id}'
                    """
                    engine.execute(update_query)
                else:
                    # If quantity is 1, delete the item
                    delete_query = f"""
                        DELETE FROM cart_items
                        WHERE id = '{cart_item_id}'
                    """
                    engine.execute(delete_query)

                # Update cart totals
                Buyer_Cart.update_cart_totals(cart_item['cart_id'])  # Corrected

                return {'success': True}
            else:
                return {'success': False, 'error': 'Cart item not found or does not belong to user'}
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error decrease cart item quantity: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            engine.dispose()

    @staticmethod
    def delete_cart_item(cart_item_id, user_id):
        engine = get_engine()
        
        try:
            # Check if the cart item exists and belongs to the user
            query = f"""
                SELECT ci.*, c.id as cart_id, c.user_id FROM cart_items ci
                JOIN carts c ON ci.cart_id = c.id
                WHERE ci.id = '{cart_item_id}' AND c.user_id = '{user_id}'
            """
            cart_item = engine.execute(query).fetchone()
            
            if cart_item:
                # Delete the cart item
                delete_query = f"""
                    DELETE FROM cart_items
                    WHERE id = '{cart_item_id}'
                """
                engine.execute(delete_query)

                # Update cart totals
                Buyer_Cart.update_cart_totals(cart_item['cart_id'])  # Corrected

                return {'success': True}
            else:
                return {'success': False, 'error': 'Cart item not found or does not belong to user'}
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error delete cart item quantity: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            engine.dispose()

 
class Buyer_Wishlist:
    # @staticmethod
    # def add_to_wishlist(user_id, listing_id):
    #     engine = get_engine()
    #     try:
        
    #         # Check if the item already exists in the cart
    #         check_query = f"""
    #             SELECT * FROM wishlist_items 
    #             WHERE user_id = '{user_id}' AND listing_id = '{listing_id}'
    #         """
    #         existing_item = engine.execute(check_query).fetchone()
            
    #         if not existing_item:
    #             # Insert a new item if it doesn't exist
    #             insert_query = f"""
    #                 INSERT INTO wishlist_items (listing_id, user_id) 
    #                 VALUES ('{listing_id}', '{user_id}')
    #             """
    #             engine.execute(insert_query)
                
    #         return {'message': 'Item added to wishlist.'}
        
    #     except SQLAlchemyError as e:
    #         print(f"Error: {e}")
    #         return {'error': str(e)}
    #     finally:
    #         engine.dispose()

    @staticmethod
    def add_to_wishlist(user_id, listing_id):
        engine = get_engine()
        try:
            # Check if the item already exists in the wishlist
            check_query = f"""
                SELECT * FROM wishlist_items 
                WHERE user_id = '{user_id}' AND listing_id = '{listing_id}'
            """
            existing_item = engine.execute(check_query).fetchone()
            
            if not existing_item:
                # Insert a new item if it doesn't exist
                insert_query = f"""
                    INSERT INTO wishlist_items (listing_id, user_id) 
                    VALUES ('{listing_id}', '{user_id}')
                """
                engine.execute(insert_query)
                
            return {'message': 'Item added to wishlist.'}
        
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error adding to wishlist: {e}")
            return {'error': str(e)}
        finally:
            engine.dispose()
    
    @staticmethod
    def get_wishlist_items(userid):
        engine = get_engine()
        try:
            # Get the user's wishlist items
            query = f"""
                SELECT wi.listing_id, l.imagepath, l.title, l.price, wi.id
                FROM wishlist_items wi
                JOIN listings l ON wi.listing_id = l.id
                WHERE wi.user_id = '{userid}'
            """
            wishlist_items = engine.execute(query).fetchall()
            
            return wishlist_items
        
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error get wishlist item: {e}")
            return None
        finally:
            engine.dispose()
     
    @staticmethod    
    def delete_wishlist_item(wishlist_item_id, user_id):
            engine = get_engine()
            
            try:
                # Delete the cart item
                delete_query = f"""
                    DELETE FROM wishlist_items
                    WHERE id = '{wishlist_item_id}'
                """
                engine.execute(delete_query)

                return {'success': True}

            except SQLAlchemyError as e:
                current_app.logger.error(f"Error deleting wishlist item quantity: {e}")
                return {'success': False, 'error': str(e)}
            finally:
                engine.dispose()

class Buyer_Shop:
    @staticmethod
    def fetch_all_listings_forbuyer(sort_option, category):
        engine = get_engine()
        query = f"SELECT * FROM listings"
        
        if category != 'all':
            query += f" WHERE type = '{category}'"
            
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
    def fetch_category_counts_for_shop_buyer():
        engine = get_engine()
        # Query to get the count of each category
        category_query = f"""
            SELECT type, COUNT(*) as count
            FROM listings
            GROUP BY type
        """
        category_result = engine.execute(category_query).fetchall()
        category_counts = {row['type']: row['count'] for row in category_result}
        
        # Query to get the total count of listings for the seller
        total_query = f"""
            SELECT COUNT(*) as total_count
            FROM listings
        """
        total_result = engine.execute(total_query).fetchone()
        category_counts['all'] = total_result['total_count']
        
        engine.dispose()
        return category_counts
    
    @staticmethod
    def fetch_category_counts(seller_id):
        engine = get_engine()
        
        # Query to get the count of each category
        category_query = f"""
            SELECT type, COUNT(*) as count
            FROM listings
            WHERE seller_id = {seller_id}
            GROUP BY type
        """
        category_result = engine.execute(category_query).fetchall()
        category_counts = {row['type']: row['count'] for row in category_result}
        
        # Query to get the total count of listings for the seller
        total_query = f"""
            SELECT COUNT(*) as total_count
            FROM listings
            WHERE seller_id = {seller_id}
        """
        total_result = engine.execute(total_query).fetchone()
        category_counts['all'] = total_result['total_count']
        
        return category_counts
    
def create_comment(title, body, rating, item_id, user_id):
        engine = get_engine()
        try:
            # Insert the new comment into the comments table
            insert_query = f"""
                    INSERT INTO comments (title, body, rating, listing_id, user_id) 
                    VALUES ('{title}', '{body}', '{rating}', '{item_id}', '{user_id}')
                """
                
                
            engine.execute(insert_query)
            
            return {'message': 'Comment created successfully.'}
        
        except SQLAlchemyError as e:
            current_app.logger.error(f"SQLAlchemy Error creating comment: {e}")
            return {'error': f"SQLAlchemy Error: {e}"}
        except Exception as e:
            current_app.logger.error(f"Error creating comment: {e}")
            return {'error': str(e)}
        finally:
            engine.dispose()

def create_comment_report(comment_id, reporter_id, title, body):
    engine = get_engine()
    
    try:
        insert_query = """
            INSERT INTO comment_reports (comment_id, reporter_id, title, body) 
            VALUES (%s, %s, %s, %s)
        """
            
        with engine.connect() as conn:
            conn.execute(insert_query, (comment_id, reporter_id, title, body))
        return {'message': 'Report created successfully.'}
    except SQLAlchemyError as e:
        current_app.logger.error(f"SQLAlchemy Error creating comment report: {e}")
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        current_app.logger.error(f"Error creating comment report: {e}")
        return {'error': str(e)}
    finally:
        engine.dispose()
        
def create_report(title, body, item_id, seller_id, buyer_id):
    engine = get_engine()
    # current_app.logger.debug(f"Received in user.py title: {title}, body: {body}, item_id: {item_id}, seller_id: {seller_id}, buyer_id: {buyer_id}")
    
    try:
        # Check if the item already exists in the reports table for this buyer
        check_query = f"""
            SELECT * FROM reports 
            WHERE buyer_id = {buyer_id} AND listing_id = {item_id}
        """
        existing_report = engine.execute(check_query).fetchone()
        
        if not existing_report:
            # Insert a new report if it doesn't exist
            insert_query = f"""
                INSERT INTO reports (title, body, listing_id, buyer_id, seller_id) 
                VALUES ('{title}', '{body}', '{item_id}', '{buyer_id}', '{seller_id}')
            """
            engine.execute(insert_query)
            return {'message': 'Report created successfully.'}
        else:
            return {'message': 'You have already reported this item.'}
    
    except SQLAlchemyError as e:
        error_message = f"SQLAlchemy Error: {e}"
        current_app.logger.error(f"SQLAlchemy Error creating report: {e}")
        return {'error': error_message}
    except Exception as e:
        error_message = f"Error: {e}"
        current_app.logger.error(f"Error creating report: {e}")
        return {'error': error_message}
    finally:
        engine.dispose()


def fetch_top_five_bestsellers():
    query = """
    SELECT id, title, imagepath, sales
    FROM listings
    ORDER BY sales DESC
    LIMIT 5
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(query))
            listings = [dict(row) for row in result]
        return listings
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching top five bestsellers: {e}")
        return []

def fetch_transactions(user_id):
    engine = get_engine()
    transactions = []
    try:
        transaction_query = f"""
            SELECT * FROM transactions
            WHERE user_id = '{user_id}'
        """
        transactions = engine.execute(transaction_query).fetchall()
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching transactions: {e}")
    finally:
        engine.dispose()
    return transactions


