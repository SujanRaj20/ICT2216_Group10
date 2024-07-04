from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import logging
from modules.db_engine import get_engine

logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG


def get_buyers_foradmin():
    engine = get_engine()
    try:
        buyers_query = " SELECT * FROM users WHERE role = 'buyer' "
        
        buyers = engine.execute(buyers_query).fetchall()
        
        return buyers
    except SQLAlchemyError as e:
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        return {'error': str(e)}
    finally:
        engine.dispose()

def get_sellers_foradmin():
    engine = get_engine()
    try:
        sellers_query = " SELECT * FROM users WHERE role = 'seller' "
        
        sellers = engine.execute(sellers_query).fetchall()
        
        return sellers
    except SQLAlchemyError as e:
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        return {'error': str(e)}
    finally:
        engine.dispose()

def get_listings_foradmin():
    engine = get_engine()
    try:
        listing_query = " SELECT * FROM listings"
        
        listings = engine.execute(listing_query).fetchall()
        
        return listings
    except SQLAlchemyError as e:
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        return {'error': str(e)}
    finally:
        engine.dispose()

def get_comments_foradmin():
    engine = get_engine()
    try:
        comments_query = """
            SELECT 
                c.id AS comment_id, 
                c.title AS comment_title, 
                c.body AS comment_body, 
                c.rating AS comment_rating, 
                c.listing_id AS comment_listing_id, 
                c.user_id AS comment_user_id, 
                c.created_at AS comment_created_at,
                u.id AS user_id, 
                u.username AS user_username, 
                u.fname AS user_fname, 
                u.lname AS user_lname, 
                u.email AS user_email, 
                u.phone_num AS user_phone_num, 
                u.role AS user_role, 
                l.id AS listing_id, 
                l.title AS listing_title, 
                l.description AS listing_description, 
                l.keywords AS listing_keywords, 
                l.release_date AS listing_release_date, 
                l.author AS listing_author, 
                l.publisher AS listing_publisher, 
                l.price AS listing_price, 
                l.stock AS listing_stock, 
                l.type AS listing_type, 
                l.seller_id AS listing_seller_id, 
                l.imagepath AS listing_imagepath
            FROM 
                comments c
            JOIN 
                users u ON c.user_id = u.id
            JOIN 
                listings l ON c.listing_id = l.id
        """
        
        comments = engine.execute(comments_query).fetchall()
        
        return comments
    except SQLAlchemyError as e:
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        return {'error': str(e)}
    finally:
        engine.dispose()

def get_commentreports_foradmin():
    engine = get_engine()
    try:
        commentreports_query = """
            SELECT 
                cr.id AS commentreport_id,
                cr.comment_id AS commentreport_comment_id,
                cr.reporter_id AS commentreport_reporter_id,
                cr.title AS commentreport_title,
                cr.body AS commentreport_body,
                c.id AS commentreport_comment_id,
                c.title AS commentreport_comment_title,
                c.body AS commentreport_comment_body,
                c.rating AS commentreport_comment_rating,
                c.listing_id AS commentreport_comment_listing_id,
                c.user_id AS commentreport_comment_user_id,
                c.created_at AS commentreport_comment_created_at
            FROM 
                comment_reports cr
            JOIN 
                comments c ON c.id = cr.comment_id
        """
        
        commentreports = engine.execute(commentreports_query).fetchall()
        
        return commentreports
    except SQLAlchemyError as e:
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        return {'error': str(e)}
    finally:
        engine.dispose()

def get_listingreports_foradmin():
    engine = get_engine()
    try:
        listingreports_query = """
            SELECT 
                lr.id AS listingreport_id,
                lr.listing_id AS listingreport_listing_id,
                lr.buyer_id AS listingreport_reporter_id,
                lr.seller_id AS listingreport_seller_id,
                lr.title AS listingreport_title,
                lr.body AS listingreport_body,
                lr.created_at AS listingreport_created_at,
                l.id AS listing_id, 
                l.title AS listing_title, 
                l.description AS listing_description, 
                l.keywords AS listing_keywords, 
                l.release_date AS listing_release_date, 
                l.author AS listing_author, 
                l.publisher AS listing_publisher, 
                l.price AS listing_price, 
                l.stock AS listing_stock, 
                l.type AS listing_type, 
                l.seller_id AS listing_seller_id, 
                l.imagepath AS listing_imagepath
            FROM 
                reports lr
            JOIN 
                listings l ON lr.listing_id = l.id
        """
        
        listingreports = engine.execute(listingreports_query).fetchall()
        
        return listingreports
    except SQLAlchemyError as e:
        return {'error': f"SQLAlchemy Error: {e}"}
    except Exception as e:
        return {'error': str(e)}
    finally:
        engine.dispose()

def admin_buyerdelete(user_id):
    engine = get_engine()
    try:
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT * FROM users WHERE id = '{user_id}' AND role = 'buyer'
        """
        buyer = engine.execute(query).fetchone()
        
        if buyer:
            # Delete the cart item
            delete_query = f"""
                DELETE FROM users
                WHERE id = '{user_id}'
            """
            engine.execute(delete_query)

            return {'success': True}
        else:
            return {'success': False, 'error': 'Buyer account not found'}
    except SQLAlchemyError as e:
        current_app.logger.debug(e)
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()

def admin_sellerdelete(user_id):
    engine = get_engine()
    
    try:
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT * FROM users WHERE id = '{user_id}' AND role = 'seller'
        """
        buyer = engine.execute(query).fetchone()
        
        if buyer:
            # Delete the cart item
            delete_query = f"""
                DELETE FROM users
                WHERE id = '{user_id}'
            """
            engine.execute(delete_query)

            return {'success': True}
        else:
            return {'success': False, 'error': 'Seller account not found'}
    except SQLAlchemyError as e:
        current_app.logger.debug(e)
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()

def admin_listingdelete(listing_id):
    engine = get_engine()
    
    try:
        
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT * FROM listings WHERE id = '{listing_id}'
        """
        listing = engine.execute(query).fetchone()
        
        if listing:
            delete_query1 = f"""
                DELETE FROM reports
                WHERE listing_id = '{listing_id}'
            """
            # Delete the cart item
            delete_query2 = f"""
                DELETE FROM listings
                WHERE id = '{listing_id}'
            """
            engine.execute(delete_query1)
            engine.execute(delete_query2)

            return {'success': True}
        else:
            return {'success': False, 'error': 'Listing not found'}
    except SQLAlchemyError as e:
        current_app.logger.debug(e)
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()

def admin_commentdelete(comment_id):
    engine = get_engine()
    
    try:
        
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT * FROM comments WHERE id = '{comment_id}'
        """
        comment = engine.execute(query).fetchone()
        
        if comment:
            
            delete_query1 = f"""
                DELETE FROM comment_reports
                WHERE comment_id = '{comment_id}'
            """
            # Delete the cart item
            delete_query2 = f"""
                DELETE FROM comments
                WHERE id = '{comment_id}'
            """
            engine.execute(delete_query1)
            engine.execute(delete_query2)

            return {'success': True}
        else:
            return {'success': False, 'error': 'Comment not found'}
    except SQLAlchemyError as e:
        current_app.logger.debug(e)
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()

def admin_commentreportdelete(report_id):
    engine = get_engine()
    
    try:
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT * FROM comment_reports WHERE id = '{report_id}'
        """
        comment_report = engine.execute(query).fetchone()
        
        if comment_report:
            # Delete the cart item
            delete_query = f"""
                DELETE FROM comment_reports
                WHERE id = '{report_id}'
            """
            engine.execute(delete_query)

            return {'success': True}
        else:
            return {'success': False, 'error': 'Comment Report not found'}
    except SQLAlchemyError as e:
        current_app.logger.debug(e)
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()

def admin_listingreportdelete(report_id):
    engine = get_engine()
    
    try:
        # Check if the cart item exists and belongs to the user
        query = f"""
            SELECT * FROM reports WHERE id = '{report_id}'
        """
        listing_report = engine.execute(query).fetchone()
        
        if listing_report:
            # Delete the cart item
            delete_query = f"""
                DELETE FROM reports
                WHERE id = '{report_id}'
            """
            engine.execute(delete_query)

            return {'success': True}
        else:
            return {'success': False, 'error': 'Listing Report not found'}
    except SQLAlchemyError as e:
        current_app.logger.debug(e)
        return {'success': False, 'error': str(e)}
    finally:
        engine.dispose()