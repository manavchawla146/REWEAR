from flask_admin import Admin, BaseView, expose
from flask_admin.base import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required
from flask import url_for, request, flash, current_app, jsonify, redirect
from werkzeug.utils import redirect
from flask_mail import Message, Mail
from flask_admin.actions import action
from wtforms import validators, SelectField
from datetime import datetime
from flask_admin.model.template import macro

# Base admin view classes with security
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.signin'))

class SecureBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.signin'))

class HomeAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.is_admin):
            return redirect(url_for('main.signin'))
        return redirect(url_for('admin_analytics.analytics_dashboard'))

# Custom formatter functions
def formatter_price(view, context, model, name):
    price_value = getattr(model, name)
    if price_value is not None:
        return f"<img src='/static/images/coin.png' class='coin-icon'>{price_value:.2f}"
    return ""

# Admin views
class EmailView(SecureBaseView):
    @expose('/', methods=['GET', 'POST'])
    def send_email(self):
        from ..models import User
        mail = Mail(current_app)
        users = User.query.all()
        
        if request.method == 'POST':
            recipients = request.form.getlist('recipients')
            subject = request.form.get('subject')
            message_body = request.form.get('message')
            
            if not recipients:
                flash('You must select at least one recipient', 'error')
                return self.render('admin/email.html', users=users)
            
            recipient_users = User.query.filter(User.id.in_(recipients)).all()
            recipient_emails = [user.email for user in recipient_users]
            
            try:
                msg = Message(subject=subject, recipients=recipient_emails, body=message_body)
                mail.send(msg)
                flash(f'Email successfully sent to {len(recipient_emails)} users!', 'success')
            except Exception as e:
                flash(f'Error sending email: {str(e)}', 'error')
        
        return self.render('admin/email.html', users=users)

class CategoryView(SecureModelView):
    column_list = ['id', 'name', 'slug', 'image_url', 'description']
    form_columns = ['name', 'slug', 'image_url', 'description']

class AddressView(SecureModelView):
    column_list = ['user.username', 'address_type', 'city', 'state', 'is_default']
    column_searchable_list = ['city', 'state', 'pin_code']
    column_filters = ['address_type', 'city', 'state', 'is_default']
    form_columns = [
        'user', 'address_type', 'company_name', 'street_address',
        'apartment', 'city', 'state', 'country', 'pin_code', 'is_default'
    ]

class OrderView(SecureModelView):
    column_list = ['id', 'user.username', 'user.email', 'timestamp', 'total_price', 'payment_status', 'payment_id', 'order_id']
    column_searchable_list = ['payment_id', 'order_id', 'payment_status', 'user.username', 'user.email']
    column_filters = ['timestamp', 'payment_status', 'user.username']
    column_default_sort = ('timestamp', True)
    can_create = False
    column_formatters = {
        'total_price': formatter_price
    }
    column_labels = {
        'user.username': 'Customer Name',
        'user.email': 'Customer Email'
    }

class OrderItemView(SecureModelView):
    column_list = ['order.id', 'order.user.username', 'product.name', 'quantity', 'price_at_purchase']
    column_filters = ['order.id', 'product.name']
    column_searchable_list = ['product.name']
    can_create = False
    column_labels = {
        'order.user.username': 'Customer Name',
        'order.id': 'Order ID',
        'product.name': 'Product',
        'quantity': 'Quantity',
        'price_at_purchase': 'Price'
    }
    column_formatters = {
        'price_at_purchase': formatter_price
    }

    def __init__(self, model, session, **kwargs):
        super(OrderItemView, self).__init__(model, session, **kwargs)

class PromoCodeView(SecureModelView):
    column_list = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'uses', 'max_uses', 'min_order_value', 'active']
    column_searchable_list = ['code']
    column_filters = ['discount_type', 'active']
    column_sortable_list = ['code', 'discount_value', 'valid_from', 'valid_until', 'uses', 'active']
    form_columns = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'max_uses', 'min_order_value', 'active']
    
    form_args = {
        'code': {
            'validators': [validators.DataRequired(), validators.Length(min=3, max=20)],
            'description': 'Unique code (3-20 characters)'
        },
        'discount_type': {
            'validators': [validators.DataRequired()],
            'choices': [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')]
        },
        'discount_value': {
            'validators': [validators.DataRequired(), validators.NumberRange(min=0)],
            'description': 'Enter percentage (0-100) or fixed amount in <img src="/static/images/coin.png" class="coin-icon">'
        },
        'valid_from': {
            'validators': [validators.DataRequired()]
        },
        'valid_until': {
            'validators': [validators.DataRequired()]
        },
        'max_uses': {
            'validators': [validators.Optional(), validators.NumberRange(min=1)],
            'description': 'Leave blank for unlimited uses'
        },
        'min_order_value': {
            'validators': [validators.Optional(), validators.NumberRange(min=0)],
            'description': 'Minimum order value in <img src="/static/images/coin.png" class="coin-icon"> (optional)'
        },
        'active': {
            'default': True
        }
    }
    
    column_formatters = {
        'discount_value': lambda v, c, m, n: f"{m.discount_value}%" if m.discount_type == 'percentage' else f"<img src='/static/images/coin.png' class='coin-icon'>{m.discount_value:.2f}",
        'min_order_value': lambda v, c, m, n: f"<img src='/static/images/coin.png' class='coin-icon'>{m.min_order_value:.2f}" if m.min_order_value else "None",
        'active': lambda v, c, m, n: '<span class="badge badge-success">Active</span>' if m.active else '<span class="badge badge-danger">Inactive</span>'
    }
    
    column_labels = {
        'code': 'Promo Code',
        'discount_type': 'Type',
        'discount_value': 'Discount',
        'valid_from': 'Start Date',
        'valid_until': 'End Date',
        'max_uses': 'Max Uses',
        'uses': 'Uses',
        'min_order_value': 'Min Order',
        'active': 'Status'
    }
    
    extra_css = ['https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/css/bootstrap-datetimepicker.min.css']
    extra_js = [
        'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/js/bootstrap-datetimepicker.min.js',
        """
        $(document).ready(function() {
            $('.form_datetime').datetimepicker({
                format: 'YYYY-MM-DD HH:mm:ss',
                sideBySide: true,
                widgetPositioning: {
                    horizontal: 'auto',
                    vertical: 'bottom'
                }
            });
            $('select[name="discount_type"]').css({
                'border-color': '#a61f4c',
                'color': '#08284a'
            });
        });
        """
    ]
    
    def scaffold_form(self):
        form_class = super(PromoCodeView, self).scaffold_form()
        form_class.discount_type = SelectField('Discount Type', choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], validators=[validators.DataRequired()])
        return form_class
    
    @action('toggle_active', 'Toggle Active Status', 'Are you sure you want to toggle the active status?')
    def action_toggle_active(self, ids):
        try:
            from ..models import PromoCode
            count = 0
            for promo_id in ids:
                promo = PromoCode.query.get(promo_id)
                if promo:
                    promo.active = not promo.active
                    count += 1
            db.session.commit()
            flash(f'Toggled active status for {count} promo codes.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error toggling status: {str(e)}', 'error')
        return redirect(url_for('promocode.index_view'))


# Product Approval Management View
class ProductApprovalInterfaceView(SecureBaseView):
    """Custom interface for product approval with better UX"""
    
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from ..models import Product
        
        if request.method == 'POST':
            product_id = request.form.get('product_id')
            action = request.form.get('action')
            
            if product_id and action:
                product = Product.query.get(product_id)
                if product:
                    if action == 'approve':
                        product.approval_status = 'approved'
                        product.is_approved = True
                        product.approved_by = current_user.id
                        product.approved_at = datetime.utcnow()
                        flash(f'Product "{product.name}" has been approved!', 'success')
                    elif action == 'reject':
                        product.approval_status = 'rejected'
                        product.is_approved = False
                        product.approved_by = current_user.id
                        product.approved_at = datetime.utcnow()
                        product.rejection_reason = 'Rejected by admin'
                        flash(f'Product "{product.name}" has been rejected.', 'warning')
                    
                    try:
                        from .. import db
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Error updating product: {str(e)}', 'error')
        
        # Get products with statistics
        pending_products = Product.query.filter_by(approval_status='pending').order_by(Product.created_at.desc()).all()
        pending_count = len(pending_products)
        approved_count = Product.query.filter_by(approval_status='approved').count()
        rejected_count = Product.query.filter_by(approval_status='rejected').count()
        
        return self.render('admin/product_approval.html', 
                         products=pending_products,
                         pending_count=pending_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count)


class AllProductsApprovalView(SecureModelView):
    """View to see all products with their approval status"""
    column_list = ['id', 'name', 'uploader.username', 'approval_status', 'is_approved', 'created_at', 'approved_at']
    column_searchable_list = ['name', 'uploader.username']
    column_filters = ['approval_status', 'is_approved', 'created_at', 'approved_at', 'uploader.username']
    column_default_sort = ('created_at', True)
    can_create = False
    can_delete = False
    can_edit = True
    
    column_labels = {
        'uploader.username': 'Uploaded By',
        'approval_status': 'Status',
        'is_approved': 'Approved',
        'approved_at': 'Approval Date'
    }
    
    column_formatters = {
        'approval_status': lambda v, c, m, n: f'<span class="badge badge-{"success" if m.approval_status == "approved" else "warning" if m.approval_status == "pending" else "danger"}">{m.approval_status.title()}</span>',
        'is_approved': lambda v, c, m, n: f'<span class="badge badge-{"success" if m.is_approved else "danger"}">{"Yes" if m.is_approved else "No"}</span>'
    }
    
    form_columns = ['approval_status', 'rejection_reason']
    
    # Custom form choices for approval status
    form_choices = {
        'approval_status': [
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ]
    }
    
    @action('approve_products', 'Approve Selected', 'Are you sure you want to approve selected products?')
    def action_approve_products(self, ids):
        from ..models import Product
        try:
            count = 0
            for product_id in ids:
                product = Product.query.get(product_id)
                if product and product.approval_status != 'approved':
                    product.approval_status = 'approved'
                    product.is_approved = True
                    product.approved_by = current_user.id
                    product.approved_at = datetime.utcnow()
                    count += 1
            self.session.commit()
            flash(f'Successfully approved {count} products.', 'success')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            self.session.rollback()
            flash('Failed to approve products.', 'error')
    
    @action('reject_products', 'Reject Selected', 'Are you sure you want to reject selected products?')
    def action_reject_products(self, ids):
        from ..models import Product
        try:
            count = 0
            for product_id in ids:
                product = Product.query.get(product_id)
                if product and product.approval_status != 'rejected':
                    product.approval_status = 'rejected'
                    product.is_approved = False
                    product.approved_by = current_user.id
                    product.approved_at = datetime.utcnow()
                    product.rejection_reason = 'Rejected by admin'
                    count += 1
            self.session.commit()
            flash(f'Successfully rejected {count} products.', 'warning')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            self.session.rollback()
            flash('Failed to reject products.', 'error')
    
    def on_model_change(self, form, model, is_created):
        if not is_created:  # Only for edits, not new records
            if model.approval_status == 'approved':
                model.is_approved = True
                model.approved_by = current_user.id
                model.approved_at = datetime.utcnow()
            elif model.approval_status == 'rejected':
                model.is_approved = False
                model.approved_by = current_user.id
                model.approved_at = datetime.utcnow()
        
        super().on_model_change(form, model, is_created)


class ProductApprovalView(SecureModelView):
    column_list = ['id', 'name', 'uploader.username', 'created_at', 'approval_status', 'approved_by', 'approved_at']
    column_searchable_list = ['name', 'uploader.username']
    column_filters = ['approval_status', 'created_at', 'approved_at', 'uploader.username']
    column_default_sort = ('created_at', True)
    can_create = False
    can_delete = False
    can_edit = True
    
    # Show only pending products by default
    def get_query(self):
        return self.session.query(self.model).filter(self.model.approval_status == 'pending')
    
    def get_count_query(self):
        return self.session.query(self.model).filter(self.model.approval_status == 'pending')
    
    column_labels = {
        'uploader.username': 'Uploaded By',
        'approval_status': 'Status',
        'approved_by': 'Approved By',
        'approved_at': 'Approval Date'
    }
    
    column_formatters = {
        'approval_status': lambda v, c, m, n: f'<span class="badge badge-{"success" if m.approval_status == "approved" else "warning" if m.approval_status == "pending" else "danger"}">{m.approval_status.title()}</span>'
    }
    
    form_columns = ['approval_status', 'rejection_reason']
    
    # Custom form choices for approval status
    form_choices = {
        'approval_status': [
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ]
    }
    
    @action('approve_products', 'Approve Selected', 'Are you sure you want to approve selected products?')
    def action_approve_products(self, ids):
        from ..models import Product
        from flask_login import current_user
        from datetime import datetime
        try:
            count = 0
            for product_id in ids:
                product = Product.query.get(product_id)
                if product and product.approval_status == 'pending':
                    product.approval_status = 'approved'
                    product.is_approved = True
                    product.approved_by = current_user.id
                    product.approved_at = datetime.utcnow()
                    count += 1
            self.session.commit()
            flash(f'Successfully approved {count} products.', 'success')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            self.session.rollback()
            flash('Failed to approve products.', 'error')
    
    @action('reject_products', 'Reject Selected', 'Are you sure you want to reject selected products?')
    def action_reject_products(self, ids):
        from ..models import Product
        from flask_login import current_user
        from datetime import datetime
        try:
            count = 0
            for product_id in ids:
                product = Product.query.get(product_id)
                if product and product.approval_status == 'pending':
                    product.approval_status = 'rejected'
                    product.is_approved = False
                    product.approved_by = current_user.id
                    product.approved_at = datetime.utcnow()
                    product.rejection_reason = 'Rejected by admin'
                    count += 1
            self.session.commit()
            flash(f'Successfully rejected {count} products.', 'warning')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            self.session.rollback()
            flash('Failed to reject products.', 'error')
    
    # Override the edit form to update approval fields automatically
    def on_model_change(self, form, model, is_created):
        from flask_login import current_user
        from datetime import datetime
        
        if not is_created:  # Only for edits, not new records
            if model.approval_status == 'approved':
                model.is_approved = True
                model.approved_by = current_user.id
                model.approved_at = datetime.utcnow()
            elif model.approval_status == 'rejected':
                model.is_approved = False
                model.approved_by = current_user.id
                model.approved_at = datetime.utcnow()
        
        super().on_model_change(form, model, is_created)


# Swap Request Management View
class SwapRequestView(SecureModelView):
    column_list = ['id', 'requester.username', 'requested_item.name', 'offered_item.name', 'status', 'created_at']
    column_searchable_list = ['requester.username', 'requested_item.name', 'offered_item.name']
    column_filters = ['status', 'created_at']
    column_default_sort = ('created_at', True)
    can_create = False
    can_delete = True
    
    column_labels = {
        'requester.username': 'Requester',
        'requested_item.name': 'Wants Item',
        'offered_item.name': 'Offers Item',
        'created_at': 'Requested On'
    }
    
    column_formatters = {
        'status': lambda v, c, m, n: f'<span class="badge badge-{"success" if m.status == "completed" else "info" if m.status == "approved" else "warning" if m.status == "pending" else "danger"}">{m.status.title()}</span>'
    }
    
    form_columns = ['status', 'rejection_reason']

        
class ProductView(SecureModelView):
    column_list = ['name', 'price', 'stock', 'category.name', 'pet_type.name', 'weight', 'parent.name']
    column_searchable_list = ['name', 'description']
    column_filters = ['price', 'stock', 'category.name', 'pet_type.name', 'weight']
    form_columns = ['name', 'description', 'price', 'stock', 'image_url', 'category', 'pet_type', 'weight', 'parent']
    column_formatters = {
        'price': formatter_price
    }
    
    def __init__(self, model, session, **kwargs):
        super(ProductView, self).__init__(model, session, **kwargs)
    
    def _refresh_forms_args(self):
        from ..models import Category, PetType, Product
        
        self.form_args = {
            'category': {'query_factory': lambda: Category.query.order_by(Category.name)},
            'pet_type': {'query_factory': lambda: PetType.query.order_by(PetType.name)},
            'parent': {
                'query_factory': lambda: Product.query.filter_by(parent_id=None).order_by(Product.name)
            }
        }
    
    def create_form(self, obj=None):
        self._refresh_forms_args()
        form = super(ProductView, self).create_form(obj)
        self._add_conditional_field_script(form)
        return form
    
    def edit_form(self, obj=None):
        self._refresh_forms_args()
        form = super(ProductView, self).edit_form(obj)
        self._add_conditional_field_script(form)
        return form
    
    def _add_conditional_field_script(self, form):
        from ..models import Category
        food_category = Category.query.filter(Category.name.ilike('%food%')).first()
        food_category_id = food_category.id if food_category else -1
        
        self.extra_js = [
            f"""
            $(document).ready(function() {{
                var foodCategoryId = {food_category_id};
                
                function toggleFoodFields() {{
                    var selectedCategory = $('select[name="category"]').val();
                    var weightField = $('.field-weight').closest('.form-group');
                    var parentField = $('.field-parent').closest('.form-group');
                    
                    if (selectedCategory == foodCategoryId) {{
                        weightField.show();
                        parentField.show();
                    }} else {{
                        weightField.hide();
                        parentField.hide();
                    }}
                }}
                
                toggleFoodFields();
                
                $('select[name="category"]').change(function() {{
                    toggleFoodFields();
                }});
                
                $('select[name="category"], select[name="pet_type"]').change(function() {{
                    var categoryId = $('select[name="category"]').val();
                    var petTypeId = $('select[name="pet_type"]').val();
                    
                    if (categoryId && petTypeId) {{
                        $.ajax({{
                            url: '/admin/admin_api/filter_parents',
                            data: {{
                                category_id: categoryId,
                                pet_type_id: petTypeId
                            }},
                            success: function(data) {{
                                var parentSelect = $('select[name="parent"]');
                                parentSelect.empty();
                                
                                parentSelect.append($('<option>', {{
                                    value: '',
                                    text: 'None (Master)'
                                }}));
                                
                                $.each(data.products, function(i, product) {{
                                    parentSelect.append($('<option>', {{
                                        value: product.id,
                                        text: product.name
                                    }}));
                                }});
                            }}
                        }});
                    }}
                }});
            }});
            """
        ]

class ReviewView(SecureModelView):
    column_list = ['product.name', 'reviewer.username', 'rating', 'content', 'created_at']
    column_searchable_list = ['content']
    column_filters = ['rating', 'product.name']
    form_columns = ['product', 'reviewer', 'rating', 'content']
    
    def __init__(self, model, session, **kwargs):
        super(ReviewView, self).__init__(model, session, **kwargs)
    
    def _refresh_forms_args(self):
        from ..models import Product, User
        
        self.form_args = {
            'product': {'query_factory': lambda: Product.query.order_by(Product.name)},
            'reviewer': {'query_factory': lambda: User.query.order_by(User.username)}
        }
    
    def create_form(self, obj=None):
        self._refresh_forms_args()
        return super(ReviewView, self).create_form(obj)
    
    def edit_form(self, obj=None):
        self._refresh_forms_args()
        return super(ReviewView, self).edit_form(obj)

class ProductImageView(SecureModelView):
    column_list = ['product.name', 'image_url', 'is_primary', 'display_order']
    column_filters = ['product.name', 'is_primary']
    form_columns = ['product', 'image_url', 'is_primary', 'display_order']
    
    def __init__(self, model, session, **kwargs):
        super(ProductImageView, self).__init__(model, session, **kwargs)
    
    def _refresh_forms_args(self):
        from ..models import Product
        
        self.form_args = {
            'product': {'query_factory': lambda: Product.query.order_by(Product.name)}
        }
    
    def create_form(self, obj=None):
        self._refresh_forms_args()
        return super(ProductImageView, self).create_form(obj)
    
    def edit_form(self, obj=None):
        self._refresh_forms_args()
        return super(ProductImageView, self).edit_form(obj)

class ProductAttributeView(SecureModelView):
    column_list = ['product.name', 'key', 'value', 'display_order']
    column_searchable_list = ['key', 'value']
    column_filters = ['product.name']
    form_columns = ['product', 'key', 'value', 'display_order']
    
    def __init__(self, model, session, **kwargs):
        super(ProductAttributeView, self).__init__(model, session, **kwargs)
    
    def _refresh_forms_args(self):
        from ..models import Product
        
        self.form_args = {
            'product': {'query_factory': lambda: Product.query.order_by(Product.name)}
        }
    
    def create_form(self, obj=None):
        self._refresh_forms_args()
        return super(ProductAttributeView, self).create_form(obj)
    
    def edit_form(self, obj=None):
        self._refresh_forms_args()
        return super(ProductAttributeView, self).edit_form(obj)

class UserView(SecureModelView):
    column_list = ['id', 'username', 'email', 'phone', 'is_admin', 'created_at']
    column_searchable_list = ['username', 'email', 'phone']
    column_filters = ['is_admin', 'created_at']

class AdminAPI(SecureBaseView):
    @expose('/')
    def index(self):
        return self.render('admin/api_index.html')

    @expose('/filter_parents')
    def filter_parents(self):
        from ..models import Product
        
        category_id = request.args.get('category_id', type=int)
        pet_type_id = request.args.get('pet_type_id', type=int)
        
        if not category_id or not pet_type_id:
            return jsonify({'products': []})
        
        try:
            products = Product.query.filter_by(
                category_id=category_id,
                pet_type_id=pet_type_id,
                parent_id=None
            ).all()
            
            return jsonify({
                'products': [{'id': p.id, 'name': p.name} for p in products]
            })
        except Exception as e:
            current_app.logger.error(f"Error in filter_parents: {str(e)}")
            return jsonify({'error': 'Failed to fetch products', 'products': []})

class AnalyticsDashboardView(SecureBaseView):
    @expose('/')
    def analytics_dashboard(self):
        from ..models import Order, Product, User
        
        total_orders = Order.query.count()
        total_products = Product.query.count()
        total_users = User.query.count()
        
        recent_orders = Order.query.order_by(Order.timestamp.desc()).limit(10).all()
        
        return self.render(
            'admin/analytics_dashboard.html',
            total_orders=total_orders,
            total_products=total_products,
            total_users=total_users,
            recent_orders=recent_orders
        )

def init_admin(app, db):
    from ..models import (
        User, Product, Review, ProductImage, Category, 
        PetType, Order, OrderItem, Address, ProductAttribute, PromoCode, SwapRequest
    )
    
    admin = Admin(
        app, 
        name='PetPocket Admin', 
        template_mode='bootstrap4', 
        index_view=HomeAdminView(name='Home')
    )
    
    admin.add_view(UserView(User, db.session, name='Users'))
    admin.add_view(ProductView(Product, db.session, name='Products'))
    admin.add_view(ProductApprovalInterfaceView(name='📋 Product Approvals', endpoint='product_approval_interface'))
    admin.add_view(ProductApprovalView(Product, db.session, name='Pending Approvals', endpoint='product_approvals'))
    admin.add_view(AllProductsApprovalView(Product, db.session, name='All Products Status', endpoint='all_products_approval'))
    admin.add_view(SwapRequestView(SwapRequest, db.session, name='Swap Requests'))
    admin.add_view(CategoryView(Category, db.session, name='Categories'))
    admin.add_view(SecureModelView(PetType, db.session, name='Pet Types'))
    admin.add_view(OrderView(Order, db.session, name='Orders'))
    admin.add_view(OrderItemView(OrderItem, db.session, name='Order Items'))
    admin.add_view(AddressView(Address, db.session, name='Addresses'))
    admin.add_view(ReviewView(Review, db.session, name='Reviews'))
    admin.add_view(ProductImageView(ProductImage, db.session, name='Product Images'))
    admin.add_view(ProductAttributeView(ProductAttribute, db.session, name='Product Attributes'))
    admin.add_view(PromoCodeView(PromoCode, db.session, name='Promo Codes'))
    
    admin.add_view(EmailView(name='Send Email', endpoint='admin_email'))
    admin.add_view(AdminAPI(name='API', endpoint='admin_api'))
    admin.add_view(AnalyticsDashboardView(name='Analytics', endpoint='analytics_dashboard'))
    
    return admin