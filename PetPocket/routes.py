from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from .models import PetType, Product, Category, WishlistItem, CartItem, Order, User
from .models import OrderItem, ProductAnalytics, Address, ProductImage, ProductView, Review, ProductAttribute, PromoCode
from .models import SwapHistory, PointRedemption, ItemReport, SwapRequest
from . import db
from flask import current_app
from . import razorpay_client
from datetime import datetime
from sqlalchemy import func, desc
from flask_wtf.csrf import validate_csrf, CSRFError  # Added for explicit CSRF validation
from werkzeug.exceptions import BadRequest, NotFound, HTTPException # Added NotFound for explicit handling

main = Blueprint('main', __name__)

# General handler for all HTTP exceptions to ensure JSON response for AJAX requests
@main.app_errorhandler(HTTPException)
def handle_http_exception(e):
    if request.is_json:
        # For AJAX requests, return JSON error
        return jsonify({'success': False, 'message': e.description or str(e)}), e.code
    # For regular browser requests, render an HTML error page
    return render_template('error.html', error=e.description, code=e.code), e.code

# Specific handler for CSRF errors (can be kept if you want custom messaging for CSRF)
@main.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    if request.is_json:
        return jsonify({'success': False, 'message': 'CSRF token missing or incorrect.'}), 400
    return render_template('csrf_error.html', reason=e.description), 400

@main.route("/", methods=["GET", "POST"])
def home():
    pet_types = PetType.query.all()
    # Only show approved products
    products = Product.query.filter_by(is_approved=True).limit(8).all()
    return render_template("home.html", pet_types=pet_types, products=products)

@main.route("/signin", methods=["GET", "POST"])
def signin():
    return render_template("signin.html")

@main.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    # Join with Category and PetType to allow searching by those names
    # Only show approved products
    products = Product.query \
        .join(Category, isouter=True) \
        .join(PetType, isouter=True) \
        .filter(Product.is_approved == True) \
        .filter(
            (Product.name.ilike(f'%{query}%')) |
            (Product.description.ilike(f'%{query}%')) |
            (Category.name.ilike(f'%{query}%')) |
            (PetType.name.ilike(f'%{query}%'))
        ).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': float(p.price),
        'stock': p.stock,
        'image_url': p.image_url
    } for p in products])

@main.route('/search')
def search():
    return render_template('search.html')

@main.route('/profile')
@login_required
def profile():
    # Refresh current user data from database to get latest points balance
    db.session.refresh(current_user)
    
    # Remove orders since we're removing purchase functionality
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.all()
    
    # Get swap history for the current user
    user_swaps = SwapHistory.query.filter(
        (SwapHistory.user1_id == current_user.id) | 
        (SwapHistory.user2_id == current_user.id)
    ).order_by(SwapHistory.completed_at.desc()).all()
    
    # Get point redemptions for the current user
    point_redemptions = PointRedemption.query.filter_by(user_id=current_user.id).order_by(PointRedemption.redeemed_at.desc()).all()
    
    # Get user's uploaded products
    uploaded_products = Product.query.filter_by(uploader_id=current_user.id).all()
    
    # Create recent activity data
    recent_activity = []
    
    # Add recent swaps
    for swap in user_swaps[:3]:
        if swap.user1_id == current_user.id:
            other_user = User.query.get(swap.user2_id)
            recent_activity.append({
                'icon': 'swap_horiz',
                'text': f'Completed swap with {other_user.username}',
                'time': swap.completed_at.strftime('%B %d, %Y'),
                'timestamp': swap.completed_at
            })
        else:
            other_user = User.query.get(swap.user1_id)
            recent_activity.append({
                'icon': 'swap_horiz',
                'text': f'Completed swap with {other_user.username}',
                'time': swap.completed_at.strftime('%B %d, %Y'),
                'timestamp': swap.completed_at
            })
    
    # Add recent point redemptions
    for redemption in point_redemptions[:3]:
        recent_activity.append({
            'icon': 'stars',
            'text': f'Redeemed {redemption.points_spent} points for {redemption.product.name}',
            'time': redemption.redeemed_at.strftime('%B %d, %Y'),
            'timestamp': redemption.redeemed_at
        })
    
    # Add recent item listings
    for product in uploaded_products[:2]:
        recent_activity.append({
            'icon': 'add_circle',
            'text': f'Listed {product.name} for exchange',
            'time': product.created_at.strftime('%B %d, %Y'),
            'timestamp': product.created_at
        })
    
    # Sort by timestamp (most recent first)
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activity = recent_activity[:5]  # Limit to 5 most recent activities
    
    return render_template('profile.html', 
                          wishlist_items=wishlist_items,
                          addresses=addresses,
                          categories=categories,
                          recent_activity=recent_activity,
                          user_swaps=user_swaps,
                          point_redemptions=point_redemptions,
                          uploaded_products=uploaded_products)

@main.route('/create-swap-request', methods=['POST'])
@login_required
def create_swap_request():
    """Create a swap request"""
    try:
        data = request.get_json()
        requested_item_id = data.get('requested_item_id')
        offered_item_id = data.get('offered_item_id')
        
        # Validate the request
        requested_item = Product.query.get_or_404(requested_item_id)
        offered_item = Product.query.get_or_404(offered_item_id)
        
        # Check if user owns the offered item
        if offered_item.uploader_id != current_user.id:
            return jsonify({'success': False, 'message': 'You can only offer items you own'}), 400
        
        # Check if user is not requesting their own item
        if requested_item.uploader_id == current_user.id:
            return jsonify({'success': False, 'message': 'You cannot request your own item'}), 400
        
        # Prevent user from swapping the same product (offered and requested are the same)
        if requested_item_id == offered_item_id:
            return jsonify({'success': False, 'message': 'You cannot swap the same product with itself'}), 400
        
        # Check if a similar swap request already exists
        existing_request = SwapRequest.query.filter_by(
            requester_id=current_user.id,
            requested_item_id=requested_item_id,
            offered_item_id=offered_item_id,
            status='pending'
        ).first()
        
        if existing_request:
            return jsonify({'success': False, 'message': 'Swap request already exists'}), 400
        
        # Create the swap request
        swap_request = SwapRequest(
            requester_id=current_user.id,
            requested_item_id=requested_item_id,
            offered_item_id=offered_item_id
        )
        
        db.session.add(swap_request)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Swap request sent to {requested_item.uploader.username}!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/respond-swap-request', methods=['POST'])
@login_required
def respond_swap_request():
    """Respond to a swap request (approve/reject)"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        action = data.get('action')  # 'approve' or 'reject'
        
        swap_request = SwapRequest.query.get_or_404(request_id)
        
        # Check if user owns the requested item
        if swap_request.requested_item.uploader_id != current_user.id:
            return jsonify({'success': False, 'message': 'You can only respond to requests for your items'}), 403
        
        if action == 'approve':
            swap_request.status = 'approved'
            swap_request.owner_approved = True
            swap_request.responded_at = datetime.utcnow()
            
            # If both parties have approved, complete the swap
            if swap_request.requester_approved and swap_request.owner_approved:
                # Create swap history record
                swap_history = SwapHistory(
                    item1_id=swap_request.offered_item_id,
                    item2_id=swap_request.requested_item_id,
                    user1_id=swap_request.requester_id,
                    user2_id=current_user.id
                )
                
                db.session.add(swap_history)
                swap_request.status = 'completed'
                swap_request.completed_at = datetime.utcnow()
                
                # Award points to both users
                requester = User.query.get(swap_request.requester_id)
                owner = current_user
                
                if requester:
                    requester.points_balance += 10  # Points for successful swap
                if owner:
                    owner.points_balance += 10
                
                message = 'Swap completed successfully! Both users have been awarded 10 points.'
            else:
                message = 'Swap request approved! Waiting for final confirmation.'
            
        elif action == 'reject':
            swap_request.status = 'rejected'
            swap_request.responded_at = datetime.utcnow()
            swap_request.rejection_reason = data.get('reason', 'Request rejected by owner')
            message = 'Swap request rejected.'
        
        else:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        db.session.commit()
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/my-swap-requests')
@login_required
def my_swap_requests():
    """Get user's swap requests (both made and received)"""
    swap_requests_made = SwapRequest.query.filter_by(requester_id=current_user.id)\
        .order_by(SwapRequest.created_at.desc()).all()
    
    swap_requests_received = SwapRequest.query.join(Product, SwapRequest.requested_item_id == Product.id)\
        .filter(Product.uploader_id == current_user.id)\
        .order_by(SwapRequest.created_at.desc()).all()
    
    return jsonify({
        'requests_made': [{
            'id': req.id,
            'requested_item': req.requested_item.name,
            'offered_item': req.offered_item.name,
            'status': req.status,
            'created_at': req.created_at.strftime('%B %d, %Y'),
            'owner': req.requested_item.uploader.username
        } for req in swap_requests_made],
        'requests_received': [{
            'id': req.id,
            'requested_item': req.requested_item.name,
            'offered_item': req.offered_item.name,
            'status': req.status,
            'created_at': req.created_at.strftime('%B %d, %Y'),
            'requester': req.requester.username
        } for req in swap_requests_received]
    })

@main.route('/products/<int:pet_type_id>')
def products(pet_type_id):
    pet_type = PetType.query.get_or_404(pet_type_id)
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    
    # Build the query with optional category filtering
    # Only show approved products
    query = Product.query.filter_by(pet_type_id=pet_type_id, is_approved=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.paginate(page=page, per_page=15, error_out=False)
    categories = Category.query.all()
    
    return render_template('product-listing.html',
                          products=products,
                          pet_type=pet_type,
                          categories=categories,
                          selected_category_id=category_id)

@main.route('/get_product_details/<int:product_id>')
def get_product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url,
        'category': product.category.name if product.category else None,
        'pet_type': product.pet_type.name if product.pet_type else None
    })

def get_advanced_recommendations(user_id=None, limit=10):  # Changed limit from 5 to 10
    recommendations = []
    scored_products = {}
    product_ids_added = set()
    weights = {
        'collaborative': 0.4,
        'content': 0.3,
        'popularity': 0.3
    }
    if user_id:
        user_views = ProductView.query.filter_by(user_id=user_id).subquery()
        similar_users = db.session.query(ProductView.user_id).filter(
            ProductView.product_id.in_(db.session.query(user_views.c.product_id).subquery().select()),
            ProductView.user_id != user_id
        ).subquery()
        collaborative_products = db.session.query(
            ProductView.product_id, func.count(ProductView.id).label('view_count')
        ).filter(
            ProductView.user_id.in_(similar_users),
            ProductView.product_id.notin_(db.session.query(user_views.c.product_id))
        ).group_by(ProductView.product_id).order_by(desc('view_count')).limit(limit * 2).all()
        for product_id, score in collaborative_products:
            product = Product.query.get(product_id)
            if product and product.stock > 0 and product.id not in product_ids_added:
                scored_products[product.id] = scored_products.get(product.id, 0) + (score * weights['collaborative'])
        co_purchased_product_ids = db.session.query(
            OrderItem.product_id, func.count(OrderItem.id).label('purchase_count')
        ).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.id.in_(
                db.session.query(OrderItem.order_id).filter(
                    OrderItem.product_id.in_(db.session.query(user_views.c.product_id))
                )
            ),
            OrderItem.product_id.notin_(db.session.query(user_views.c.product_id))
        ).group_by(OrderItem.product_id).order_by(desc('purchase_count')).limit(limit * 2).all()
        for product_id, score in co_purchased_product_ids:
            product = Product.query.get(product_id)
            if product and product.stock > 0 and product.id not in product_ids_added:
                scored_products[product.id] = scored_products.get(product.id, 0) + (score * weights['collaborative'])
    if user_id:
        user_products = db.session.query(Product).join(
            ProductView, Product.id == ProductView.product_id
        ).filter(ProductView.user_id == user_id).all()
        preferred_categories = set(p.category_id for p in user_products)
        preferred_pet_types = set(p.pet_type_id for p in user_products)
        content_products = Product.query.filter(
            Product.category_id.in_(preferred_categories) | Product.pet_type_id.in_(preferred_pet_types),
            Product.stock > 0
        ).order_by(func.random()).limit(limit * 2).all()
        for product in content_products:
            if product.id not in product_ids_added:
                score = 0
                if product.category_id in preferred_categories:
                    score += 0.6
                if product.pet_type_id in preferred_pet_types:
                    score += 0.4
                scored_products[product.id] = scored_products.get(product.id, 0) + (score * weights['content'])
    popular_products = db.session.query(
        Product.id, func.sum(ProductAnalytics.view_count + ProductAnalytics.purchase_count).label('popularity')
    ).join(
        ProductAnalytics, Product.id == ProductAnalytics.product_id
    ).filter(
        Product.stock > 0
    ).group_by(Product.id).order_by(desc('popularity')).limit(limit * 2).all()
    for product_id, score in popular_products:
        if product_id not in product_ids_added:
            scored_products[product_id] = scored_products.get(product_id, 0) + (score * weights['popularity'])
    for product_id, score in sorted(scored_products.items(), key=lambda x: x[1], reverse=True):
        product = Product.query.get(product_id)
        if product and product.id not in product_ids_added:
            recommendations.append(product)
            product_ids_added.add(product.id)
            if len(recommendations) >= limit:
                break
    if len(recommendations) < limit:
        fallback_products = Product.query.filter(
            Product.stock > 0,
            Product.id.notin_(product_ids_added)
        ).order_by(func.random()).limit(limit - len(recommendations)).all()
        recommendations.extend(fallback_products)
    return recommendations[:limit]

@main.route('/api/home_recommendations')
def home_recommendations():
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        # Get products that are not in best sellers or pet parent loves
        best_seller_ids = db.session.query(Product.id).join(
            ProductAnalytics, Product.id == ProductAnalytics.product_id
        ).group_by(Product.id).having(
            func.sum(ProductAnalytics.purchase_count) > 0
        ).order_by(func.sum(ProductAnalytics.purchase_count).desc()).limit(10).subquery()

        loved_product_ids = db.session.query(Product.id).join(
            Review, Product.id == Review.product_id
        ).group_by(Product.id).having(
            func.count(Review.id) >= 3
        ).order_by(func.avg(Review.rating).desc()).limit(10).subquery()

        recommendations = Product.query.filter(
            ~Product.id.in_(best_seller_ids),
            ~Product.id.in_(loved_product_ids)
        ).order_by(func.random()).limit(10).all()

        return jsonify([{
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'image_url': p.image_url,
            'category': p.category.name,
            'pet_type': p.pet_type.name,
            'rating': round(sum(r.rating for r in p.reviews) / len(p.reviews), 1) if p.reviews else 0,
            'review_count': len(p.reviews)
        } for p in recommendations])
    except Exception as e:
        current_app.logger.error(f"Home recommendation error: {str(e)}")
        return jsonify([])

def get_recommended_products(product_id, limit=10):  # Changed default limit from 4 to 10
    current_product = Product.query.get(product_id)
    if not current_product:
        return []
    user_id = current_user.id if current_user.is_authenticated else None
    recommendations = get_advanced_recommendations(user_id=user_id, limit=limit * 2)
    filtered_recommendations = [
        p for p in recommendations
        if p.id != product_id and (
            p.category_id == current_product.category_id or
            p.pet_type_id == current_product.pet_type_id
        )
    ]
    if len(filtered_recommendations) < limit:
        filtered_recommendations.extend([
            p for p in recommendations
            if p.id != product_id and p not in filtered_recommendations
        ])
    return filtered_recommendations[:limit]

@main.route('/api/recommendations/<int:product_id>')
def get_recommendations(product_id):
    try:
        recommendations = get_recommended_products(product_id, limit=10)
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'image_url': p.image_url,
            'category': p.category.name,
            'pet_type': p.pet_type.name
        } for p in recommendations])
    except Exception as e:
        current_app.logger.error(f"Recommendation error: {str(e)}")
        return jsonify([])

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    additional_images = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.display_order).all()
    attributes = ProductAttribute.query.filter_by(product_id=product_id).order_by(ProductAttribute.display_order).all()
    recommended_products = Product.query.filter(
        Product.id != product_id,
        (Product.category_id == product.category_id) | (Product.pet_type_id == product.pet_type_id)
    ).limit(10).all()
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    total_reviews = len(reviews)
    avg_rating = 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    if total_reviews > 0:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / total_reviews, 1)
        for review in reviews:
            rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
    if product.parent:
        master_product = product.parent
        selected_variant = product
    else:
        master_product = product
        selected_variant = product
    variants = [master_product] + list(master_product.variants)
    variants = sorted(variants, key=lambda x: x.weight or 0)
    user_uploaded_products = []
    if current_user.is_authenticated:
        user_uploaded_products = Product.query.filter_by(uploader_id=current_user.id).all()
    return render_template('product-detail.html', 
                         product=product, 
                         variants=variants,
                         selected_variant=selected_variant,
                         additional_images=additional_images,
                         attributes=attributes,
                         reviews=reviews,
                         total_reviews=total_reviews,
                         avg_rating=avg_rating,
                         rating_counts=rating_counts,
                         recommended_products=recommended_products,
                         user_uploaded_products=user_uploaded_products
                         )

@main.route('/api/reviews/add', methods=['POST'])
@login_required
def add_review():
    data = request.json
    product_id = data.get('product_id')
    rating = data.get('rating')
    content = data.get('content')
    if not all([product_id, rating, content]):
        return jsonify({'error': 'Missing required fields'}), 400
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    if existing_review:
        existing_review.rating = rating
        existing_review.content = content
        existing_review.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'id': existing_review.id,
            'rating': existing_review.rating,
            'content': existing_review.content,
            'created_at': existing_review.updated_at.strftime('%B %d, %Y'),
            'user': current_user.username,
            'message': 'Review updated successfully'
        })
    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=rating,
        content=content
    )
    db.session.add(review)
    db.session.commit()
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    total_reviews = len(reviews)
    avg_rating = round(sum(r.rating for r in reviews) / total_reviews, 1) if total_reviews > 0 else 0
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in reviews:
        rating_counts[r.rating] += 1
    return jsonify({
        'id': review.id,
        'rating': review.rating,
        'content': review.content,
        'created_at': review.created_at.strftime('%B %d, %Y'),
        'user': current_user.username,
        'average_rating': avg_rating,
        'total_reviews': total_reviews,
        'rating_counts': rating_counts,
        'message': 'Review added successfully'
    })

@main.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    products = [item.product for item in wishlist_items]
    return render_template('wishlist.html', products=products)

@main.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    try:
        # Debug log
        print("Received add_to_wishlist request")
        print("Request headers:", dict(request.headers))
        print("Request data:", request.get_json())

        if not request.is_json:
            print("Request is not JSON")
            return jsonify({'success': False, 'message': 'Request must be JSON'}), 400

        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({'success': False, 'message': 'No data received'}), 400

        product_id = data.get('product_id')
        if not product_id:
            print("No product_id in request")
            return jsonify({'success': False, 'message': 'Product ID is required'}), 400
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            print(f"Invalid product_id: {product_id}")
            return jsonify({'success': False, 'message': 'Invalid product ID'}), 400

        # Debug log
        print(f"Processing wishlist update - Product ID: {product_id}")

        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            print(f"Product not found - ID: {product_id}")
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        # Check if product is already in wishlist
        wishlist_item = WishlistItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if wishlist_item:
            # Remove from wishlist
            db.session.delete(wishlist_item)
            message = 'Product removed from wishlist'
            print(f"Removed product from wishlist - ID: {product_id}")
        else:
            # Add to wishlist
            wishlist_item = WishlistItem(
                user_id=current_user.id,
                product_id=product_id
            )
            db.session.add(wishlist_item)
            message = 'Product added to wishlist'
            print(f"Added product to wishlist - ID: {product_id}")

        db.session.commit()
        return jsonify({'success': True, 'message': message})

    except Exception as e:
        print(f"Error in add_to_wishlist: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/check_wishlist_status')
@login_required
def check_wishlist_status():
    if not current_user.is_authenticated:
        return jsonify({'items': []})
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    wishlist_product_ids = [item.product_id for item in wishlist_items]
    return jsonify({'items': wishlist_product_ids})

@main.route('/remove_from_wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    data = request.get_json()
    print(f"Remove from wishlist request: product_id={data.get('product_id')}")  # Debug log
    try:
        product_id = data.get('product_id')
        if not product_id:
            print("Remove from wishlist error: Missing product_id")
            return jsonify({'success': False, 'message': 'Missing product_id'}), 400
        wishlist_item = WishlistItem.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        if wishlist_item:
            db.session.delete(wishlist_item)
            db.session.commit()
            print(f"Removed product {product_id} from wishlist for user {current_user.id}")
            return jsonify({'success': True, 'message': 'Removed from wishlist'})
        print(f"Product {product_id} not found in wishlist for user {current_user.id}")
        return jsonify({'success': False, 'message': 'Item not found in wishlist'})
    except Exception as e:
        db.session.rollback()
        print(f"Remove from wishlist error: {str(e)}")  # Debug log
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/api/wishlist_products')
@login_required
def get_wishlist_products():
    try:
        wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
        products_data = []
        for item in wishlist_items:
            product = item.product
            # Fetch reviews for the product to calculate rating
            reviews = Review.query.filter_by(product_id=product.id).all()
            avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0
            review_count = len(reviews)
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'image_url': product.image_url,
                'avg_rating': avg_rating,
                'review_count': review_count
            })
        return jsonify({'success': True, 'products': products_data})
    except Exception as e:
        current_app.logger.error(f"Error fetching wishlist products: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/cart')
def cart():
    cart_items = []
    subtotal = 0
    tax = 0
    shipping = 0
    total = 0
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        tax = subtotal * 0.10
        shipping = 5.00 if cart_items else 0
        total = subtotal + tax + shipping
    return render_template('cart.html',
                         cart_items=cart_items,
                         subtotal=subtotal,
                         tax=tax,
                         shipping=shipping,
                         total=total)

@main.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        # Debug log
        print("Received add_to_cart request")
        print("Request headers:", dict(request.headers))
        print("Request data:", request.get_json())

        if not request.is_json:
            print("Request is not JSON")
            return jsonify({'success': False, 'message': 'Request must be JSON'}), 400

        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({'success': False, 'message': 'No data received'}), 400

        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            print("No product_id in request")
            return jsonify({'success': False, 'message': 'Product ID is required'}), 400

        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (ValueError, TypeError):
            print(f"Invalid product_id or quantity: {product_id}, {quantity}")
            return jsonify({'success': False, 'message': 'Invalid product ID or quantity'}), 400

        # Debug log
        print(f"Processing cart addition - Product ID: {product_id}, Quantity: {quantity}")

        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            print(f"Product not found - ID: {product_id}")
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        # Check if product is already in cart
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if cart_item:
            # Update quantity if product already in cart
            cart_item.quantity += quantity
            print(f"Updated existing cart item - New quantity: {cart_item.quantity}")
        else:
            # Add new item to cart
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
            print(f"Added new cart item - Quantity: {quantity}")

        db.session.commit()

        # Get updated cart count
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        print(f"Updated cart count: {cart_count}")

        return jsonify({
            'success': True,
            'message': 'Product added to cart successfully!',
            'cart_count': cart_count
        })

    except Exception as e:
        print(f"Error in add_to_cart: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/update_cart_item', methods=['PUT'])
@login_required
def update_cart_item():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
    cart_item.quantity = quantity
    db.session.commit()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    tax = subtotal * 0.05
    shipping = 40 if subtotal < 500 else 0
    total = subtotal + tax + shipping
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({
        'success': True,
        'cart_total': {
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'total': total
        },
        'cart_count': cart_count
    })

@main.route('/remove_from_cart', methods=['DELETE'])
@login_required
def remove_from_cart():
    product_id = request.json.get('product_id')
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        tax = subtotal * 0.10
        shipping = 5.00 if cart_items else 0
        total = subtotal + tax + shipping
        return jsonify({
            'success': True,
            'cart_total': {
                'subtotal': subtotal,
                'tax': tax,
                'shipping': shipping,
                'total': total
            }
        })
    return jsonify({'success': False}), 404

@main.route('/apply_promo_code', methods=['POST'])
@login_required
def apply_promo_code():
    try:
        data = request.get_json()
        promo_code = data.get('promo_code')
        if not promo_code:
            return jsonify({'success': False, 'message': 'Promo code is required'}), 400
        
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        
        promo = PromoCode.query.filter_by(code=promo_code, active=True).first()
        if not promo:
            return jsonify({'success': False, 'message': 'Invalid promo code'}), 404
        
        is_valid, message = promo.is_valid(subtotal)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        discount = promo.apply_discount(subtotal)
        tax = (subtotal - discount) * 0.10
        shipping = 5.00 if cart_items else 0
        total = subtotal - discount + tax + shipping
        
        # Store promo code in session for checkout
        session['promo_code'] = promo_code
        session['discount'] = discount
        
        return jsonify({
            'success': True,
            'message': 'Promo code applied successfully',
            'cart_total': {
                'subtotal': subtotal,
                'discount': discount,
                'tax': tax,
                'shipping': shipping,
                'total': total
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/redeem-points', methods=['POST'])
@login_required
def redeem_points():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        points_required = data.get('points_required')
        
        if not product_id or not points_required:
            return jsonify({'success': False, 'message': 'Product ID and points required'}), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        # Prevent user from redeeming their own product
        if product.uploader_id == current_user.id:
            return jsonify({'success': False, 'message': 'You cannot redeem your own product'}), 400
        
        if product.stock <= 0:
            return jsonify({'success': False, 'message': 'Product is out of stock'}), 400
        
        if current_user.points_balance < points_required:
            return jsonify({'success': False, 'message': 'Insufficient points'}), 400
        
        # Create point redemption record
        redemption = PointRedemption(
            user_id=current_user.id,
            product_id=product_id,
            points_spent=points_required
        )
        
        # Deduct points from user
        current_user.points_balance -= points_required
        
        # Reduce product stock
        product.stock -= 1
        
        db.session.add(redemption)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Product redeemed successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/request-swap', methods=['POST'])
@login_required
def request_swap():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'}), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        if product.stock <= 0:
            return jsonify({'success': False, 'message': 'Product is out of stock'}), 400
        
        if product.uploader_id == current_user.id:
            return jsonify({'success': False, 'message': 'You cannot swap your own product'}), 400
        
        # Check if swap request already exists
        existing_swap = SwapHistory.query.filter_by(
            user1_id=current_user.id,
            item1_id=product_id
        ).first()
        
        if existing_swap:
            return jsonify({'success': False, 'message': 'Swap request already exists for this product'}), 400
        
        # For simplification, let's award points to the user instead of creating incomplete swap
        # In a real app, you'd show a form to select which of user's products to offer
        points_awarded = min(10, int(product.price * 0.1))  # Award 10% of product price as points, max 10
        current_user.points_balance += points_awarded
        
        # Create a swap history record showing interest (using current user's latest product as placeholder)
        user_latest_product = Product.query.filter_by(uploader_id=current_user.id).order_by(Product.created_at.desc()).first()
        
        if user_latest_product:
            swap_request = SwapHistory(
                user1_id=current_user.id,
                user2_id=product.uploader_id,
                item1_id=user_latest_product.id,
                item2_id=product_id
            )
            db.session.add(swap_request)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Swap interest recorded! Earned {points_awarded} points.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/refresh-points', methods=['GET'])
@login_required
def refresh_points():
    """Refresh current user's points balance from database"""
    try:
        # Refresh user data from database
        db.session.refresh(current_user)
        return jsonify({
            'success': True, 
            'points_balance': current_user.points_balance,
            'message': 'Points balance refreshed'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Now handles exchange confirmations instead of payments
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your exchange list is empty.', 'warning')
        return redirect(url_for('main.cart'))
    
    total_points_required = 0
    swap_items = []
    point_items = []
    
    for item in cart_items:
        if item.product.points_required:
            point_items.append(item)
            total_points_required += item.product.points_required * item.quantity
        else:
            swap_items.append(item)
    
    if request.method == 'POST':
        try:
            # Process point redemptions
            if point_items and current_user.points >= total_points_required:
                for item in point_items:
                    points_cost = item.product.points_required * item.quantity
                    redemption = PointRedemption(
                        user_id=current_user.id,
                        product_id=item.product.id,
                        points_used=points_cost,
                        quantity=item.quantity
                    )
                    db.session.add(redemption)
                
                current_user.points -= total_points_required
                
            elif point_items:
                flash('Insufficient points for redemption.', 'warning')
                return redirect(url_for('main.checkout'))
            
            # For swap items, we'll add them to user's wishlist for now
            # Later we can implement a proper swap request system
            for item in swap_items:
                # Check if already in wishlist
                existing_wishlist = WishlistItem.query.filter_by(
                    user_id=current_user.id, 
                    product_id=item.product.id
                ).first()
                
                if not existing_wishlist:
                    wishlist_item = WishlistItem(
                        user_id=current_user.id,
                        product_id=item.product.id
                    )
                    db.session.add(wishlist_item)
            
            # Clear cart
            CartItem.query.filter_by(user_id=current_user.id).delete()
            
            db.session.commit()
            flash('Exchange requests submitted successfully!', 'success')
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing exchange: {str(e)}', 'danger')
    
    return render_template('checkout.html',
                         cart_items=cart_items,
                         point_items=point_items,
                         swap_items=swap_items,
                         total_points_required=total_points_required,
                         user_points=current_user.points,
                         user=current_user)

@main.route('/get_address/<int:address_id>')
@login_required
def get_address(address_id):
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    if not address:
        return jsonify({'success': False, 'message': 'Address not found'}), 404
    return jsonify({
        'success': True,
        'address': {
            'id': address.id,
            'first_name': current_user.username.split()[0] if current_user.username else '',
            'last_name': current_user.username.split()[1] if current_user.username and ' ' in current_user.username else '',
            'address_type': address.address_type,
            'company_name': address.company_name,
            'street_address': address.street_address,
            'apartment': address.apartment,
            'city': address.city,
            'state': address.state,
            'country': address.country,
            'pin_code': address.pin_code,
            'phone': current_user.phone,
            'email': current_user.email,
            'is_default': address.is_default
        }
    })

@main.route('/check_cart_status')
def check_cart_status():
    if not current_user.is_authenticated:
        return jsonify({'items': []})
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_product_ids = [item.product_id for item in cart_items]
    return jsonify({'items': cart_product_ids})

@main.route('/create_order', methods=['POST'])
@login_required
def create_order():
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        discount = session.get('discount', 0)
        tax = (subtotal - discount) * 0.10
        shipping = 5.00 if cart_items else 0
        total = subtotal - discount + tax + shipping
        data = {
            'amount': int(total * 100),
            'currency': 'INR',
            'receipt': f'order_rcptid_{current_user.id}_{datetime.now().timestamp()}',
            'payment_capture': '1'
        }
        order = razorpay_client.order.create(data=data)
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'amount': data['amount'],
            'currency': data['currency'],
            'key': current_app.config['RAZORPAY_KEY_ID']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/payment_callback', methods=['POST'])
@login_required
def payment_callback():
    try:
        payment_id = request.form.get('razorpay_payment_id')
        order_id = request.form.get('razorpay_order_id')
        signature = request.form.get('razorpay_signature')
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        discount = session.get('discount', 0)
        tax = (subtotal - discount) * 0.10
        shipping = 5.00 if cart_items else 0
        total = subtotal - discount + tax + shipping
        order = Order(
            user_id=current_user.id,
            total_price=total,
            payment_id=payment_id,
            order_id=order_id,
            payment_status='completed'
        )
        db.session.add(order)
        db.session.commit()
        
        # Update promo code usage
        promo_code = session.get('promo_code')
        if promo_code:
            promo = PromoCode.query.filter_by(code=promo_code, active=True).first()
            if promo:
                promo.uses += 1
                db.session.commit()
            # Clear promo code from session
            session.pop('promo_code', None)
            session.pop('discount', None)
        
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price
            )
            db.session.add(order_item)
            ProductAnalytics.increment_purchase(cart_item.product_id, cart_item.quantity)
            product = cart_item.product
            product.stock -= cart_item.quantity
            db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Payment successful', 'order_id': order.id})
    except Exception as e:
        db.session.rollback()
        print(f"Payment verification error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/track/product-view/<int:product_id>')
def track_product_view(product_id):
    if current_user.is_authenticated:
        ProductAnalytics.increment_view(product_id)
    return jsonify({'status': 'success'})

@main.route('/track/cart-add/<int:product_id>')
@login_required
def track_cart_add(product_id):
    ProductAnalytics.increment_cart_add(product_id)
    return jsonify({'status': 'success'})

@main.route('/api/pet_parent_loves')
def pet_parent_loves():
    try:
        # Get products with high ratings and reviews
        loved_products = db.session.query(
            Product,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).join(
            Review, Product.id == Review.product_id
        ).group_by(
            Product.id
        ).having(
            func.count(Review.id) >= 3,
            func.avg(Review.rating) >= 4.0  # Only highly rated products
        ).order_by(
            func.avg(Review.rating).desc()
        ).limit(10).all()

        return jsonify([{
            'id': p.Product.id,
            'name': p.Product.name,
            'price': float(p.Product.price),
            'image_url': p.Product.image_url if p.Product.image_url else 'https://placehold.co/200x200/46f27a/ffffff?text=Product',
            'category': p.Product.category.name if p.Product.category else None,
            'pet_type': p.Product.pet_type.name if p.Product.pet_type else None,
            'rating': round(p.avg_rating, 1) if p.avg_rating else 0,
            'review_count': p.review_count
        } for p in loved_products])
    except Exception as e:
        current_app.logger.error(f"Pet parent loves error: {str(e)}")
        return jsonify([])

@main.route('/api/best_sellers')
def best_sellers():
    try:
        # Get products with highest purchase count
        best_sellers = db.session.query(
            Product,
            func.coalesce(func.sum(ProductAnalytics.purchase_count), 0).label('total_purchases'),
            func.avg(Review.rating).label('avg_rating'),
            func.coalesce(func.count(func.distinct(Review.id)), 0).label('review_count')
        ).outerjoin(
            ProductAnalytics, Product.id == ProductAnalytics.product_id
        ).outerjoin(
            Review, Product.id == Review.product_id
        ).group_by(
            Product.id
        ).having(
            func.sum(ProductAnalytics.purchase_count) > 0
        ).order_by(
            func.sum(ProductAnalytics.purchase_count).desc()
        ).limit(10).all()

        return jsonify([{
            'id': p.Product.id,
            'name': p.Product.name,
            'price': float(p.Product.price),
            'image_url': p.Product.image_url if p.Product.image_url else 'https://placehold.co/200x200/46f27a/ffffff?text=Product',
            'category': p.Product.category.name if p.Product.category else None,
            'pet_type': p.Product.pet_type.name if p.Product.pet_type else None,
            'rating': round(p.avg_rating, 1) if p.avg_rating else 0,
            'review_count': p.review_count
        } for p in best_sellers])
    except Exception as e:
        current_app.logger.error(f"Best sellers error: {str(e)}")
        return jsonify({'error': 'Failed to fetch best sellers'}), 500

# Updated edit_profile route with case-insensitive checks and CSRF validation
@main.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():
    try:
        # Validate CSRF token
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            return jsonify({
                'success': False,
                'message': 'CSRF token missing'
            }), 403
        
        validate_csrf(csrf_token)

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip() if data.get('phone') else None

        if not username or not email:
            return jsonify({
                'success': False,
                'message': 'Username and email are required.'
            }), 400

        # Case-insensitive check for username
        existing_user = User.query.filter(
            func.lower(User.username) == func.lower(username), 
            User.id != current_user.id
        ).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Username already exists. Please choose a different one.'
            }), 400

        # Case-insensitive check for email
        existing_email = User.query.filter(
            func.lower(User.email) == func.lower(email), 
            User.id != current_user.id
        ).first()
        if existing_email:
            return jsonify({
                'success': False,
                'message': 'Email already exists. Please use a different email address.'
            }), 400

        current_user.username = username
        current_user.email = email
        current_user.phone = phone
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully!',
            'user': {
                'username': current_user.username,
                'email': current_user.email,
                'phone': current_user.phone
            }
        })

    except CSRFError:
        return jsonify({
            'success': False,
            'message': 'Invalid CSRF token. Please refresh the page and try again.'
        }), 403
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating profile for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An error occurred while updating your profile: {str(e)}'
        }), 500

@main.route('/api/product_review_stats/<int:product_id>')
def product_review_stats(product_id):
    from .models import Product, Review
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    total_reviews = len(reviews)
    avg_rating = round(sum(r.rating for r in reviews) / total_reviews, 1) if total_reviews > 0 else 0
    return jsonify({
        'avg_rating': avg_rating,
        'total_reviews': total_reviews
    })

@main.route('/api/home_products')
def home_products():
    try:
        # Get all product IDs to avoid repeats
        used_ids = set()
        # Best Sellers
        best_sellers_query = db.session.query(
            Product,
            func.coalesce(func.sum(ProductAnalytics.purchase_count), 0).label('total_purchases'),
            func.avg(Review.rating).label('avg_rating'),
            func.coalesce(func.count(func.distinct(Review.id)), 0).label('review_count')
        ).outerjoin(
            ProductAnalytics, Product.id == ProductAnalytics.product_id
        ).outerjoin(
            Review, Product.id == Review.product_id
        ).group_by(
            Product.id
        ).having(
            func.sum(ProductAnalytics.purchase_count) > 0
        ).order_by(
            func.sum(ProductAnalytics.purchase_count).desc()
        ).limit(20).all()
        best_sellers = []
        for p in best_sellers_query:
            if len(best_sellers) >= 8:
                break
            best_sellers.append({
                'id': p.Product.id,
                'name': p.Product.name,
                'price': float(p.Product.price),
                'image_url': p.Product.image_url if p.Product.image_url else 'https://placehold.co/200x200/46f27a/ffffff?text=Product',
                'category': p.Product.category.name if p.Product.category else None,
                'pet_type': p.Product.pet_type.name if p.Product.pet_type else None,
                'rating': round(p.avg_rating, 1) if p.avg_rating else 0,
                'review_count': p.review_count
            })
            used_ids.add(p.Product.id)
        # Pet Parent Loves
        pet_parent_loves_query = db.session.query(
            Product,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).join(
            Review, Product.id == Review.product_id
        ).group_by(
            Product.id
        ).having(
            func.count(Review.id) >= 3,
            func.avg(Review.rating) >= 4.0
        ).order_by(
            func.avg(Review.rating).desc()
        ).limit(20).all()
        pet_parent_loves = []
        for p in pet_parent_loves_query:
            if len(pet_parent_loves) >= 8:
                break
            if p.Product.id in used_ids:
                continue
            pet_parent_loves.append({
                'id': p.Product.id,
                'name': p.Product.name,
                'price': float(p.Product.price),
                'image_url': p.Product.image_url if p.Product.image_url else 'https://placehold.co/200x200/46f27a/ffffff?text=Product',
                'category': p.Product.category.name if p.Product.category else None,
                'pet_type': p.Product.pet_type.name if p.Product.pet_type else None,
                'rating': round(p.avg_rating, 1) if p.avg_rating else 0,
                'review_count': p.review_count
            })
            used_ids.add(p.Product.id)
        # If no products meet the criteria, fill with any products not already used
        if len(pet_parent_loves) == 0:
            all_products = Product.query.all()
            for p in all_products:
                if p.id not in used_ids:
                    pet_parent_loves.append({
                        'id': p.id,
                        'name': p.name,
                        'price': float(p.price),
                        'image_url': p.image_url if p.image_url else 'https://placehold.co/200x200/46f27a/ffffff?text=Product',
                        'category': p.category.name if p.category else None,
                        'pet_type': p.pet_type.name if p.pet_type else None,
                        'rating': round(sum(r.rating for r in p.reviews) / len(p.reviews), 1) if p.reviews else 0,
                        'review_count': len(p.reviews)
                    })
                    used_ids.add(p.id)
                    if len(pet_parent_loves) >= 8:
                        break
        # Recommendations (random, not in above)
        recommendations_query = Product.query.filter(~Product.id.in_(used_ids)).order_by(func.random()).limit(20).all()
        recommendations = []
        for p in recommendations_query:
            if len(recommendations) >= 8:
                break
            recommendations.append({
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'image_url': p.image_url if p.image_url else 'https://placehold.co/200x200/46f27a/ffffff?text=Product',
                'category': p.category.name if p.category else None,
                'pet_type': p.pet_type.name if p.pet_type else None,
                'rating': round(sum(r.rating for r in p.reviews) / len(p.reviews), 1) if p.reviews else 0,
                'review_count': len(p.reviews)
            })
            used_ids.add(p.id)
        # Fill any section with random products if < 8
        all_products = Product.query.all()
        def fill_section(section):
            while len(section) < 8:
                for p in all_products:
                    if p.id not in used_ids:
                        section.append({
                            'id': p.id,
                            'name': p.name,
                            'price': float(p.price),
                            'image_url': p.image_url if p.image_url else 'https://placehold.co/200x200/46f27a/ffffff?text=Product',
                            'category': p.category.name if p.category else None,
                            'pet_type': p.pet_type.name if p.pet_type else None,
                            'rating': round(sum(r.rating for r in p.reviews) / len(p.reviews), 1) if p.reviews else 0,
                            'review_count': len(p.reviews)
                        })
                        used_ids.add(p.id)
                        if len(section) >= 8:
                            break
                else:
                    break  # Prevent infinite loop if not enough products
        fill_section(best_sellers)
        fill_section(pet_parent_loves)
        fill_section(recommendations)
        return jsonify({
            'best_sellers': best_sellers,
            'pet_parent_loves': pet_parent_loves,
            'recommendations': recommendations
        })
    except Exception as e:
        current_app.logger.error(f"Home products error: {str(e)}")
        return jsonify({'best_sellers': [], 'pet_parent_loves': [], 'recommendations': []})


@main.route('/add-product', methods=['POST'])
@login_required
def add_product():
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        points_required = request.form.get('points', type=int)
        category_id = request.form.get('category_id', type=int)
        image_url = request.form.get('image_url', '').strip()
        
        # Validation
        if not all([name, description, points_required, category_id]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all required fields.'
            }), 400
        
        if points_required <= 0:
            return jsonify({
                'success': False,
                'message': 'Points required must be greater than 0.'
            }), 400
        
        # Verify category exists
        category = Category.query.get(category_id)
        if not category:
            return jsonify({
                'success': False,
                'message': 'Invalid category selected.'
            }), 400
        
        # For ReWear platform, we need a default pet_type (you might want to create a "Clothing" pet type)
        # For now, let's use the first available pet type or create a default one
        pet_type = PetType.query.first()
        if not pet_type:
            # Create a default "General" pet type if none exists
            pet_type = PetType(name="General", image_url="")
            db.session.add(pet_type)
            db.session.flush()  # Get the ID without committing
        
        # Create the product (pending admin approval)
        product = Product(
            name=name,
            description=description,
            price=0.0,  # Set price to 0 for point-based items
            stock=1,  # Default stock
            image_url=image_url if image_url else None,
            points_required=points_required,
            pet_type_id=pet_type.id,
            category_id=category_id,
            uploader_id=current_user.id,
            # Approval system - new products need admin approval
            is_approved=False,
            approval_status='pending'
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully submitted "{name}" for approval! It will be visible once approved by admin.',
            'product_id': product.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Add product error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while adding the product. Please try again.'
        }), 500