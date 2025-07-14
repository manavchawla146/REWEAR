document.addEventListener('DOMContentLoaded', function () {
    const wishlistGrid = document.querySelector('.wishlist-grid');
    const productGridContainer = document.querySelector('.product-grid'); // This will hold the dynamically created product cards
    let cartItems = [];

    // Helper function to get CSRF token
    function getCsrfToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.content : '';
    }

    // Function to create a product card HTML string
    function createProductCard(product) {
        return `
            <div class="product-card" data-product-id="${product.id}">
              <img class="product-image" src="${product.image_url}" alt="${product.name}">
              <h3 class="product-name">${product.name}</h3>
              <div class="product-price-rating">
                <span class="product-price">₹${product.price.toFixed(2)}</span>
                <button class="remove-from-wishlist" data-product-id="${product.id}">
                  <span class="material-symbols-outlined">delete</span>
                  <span class="del-txt">Remove</span>
                </button>
              </div>
            </div>
        `;
    }

    // Function to fetch and render the wishlist grid
    async function fetchAndRenderWishlistGrid() {
        console.log('Fetching and rendering wishlist...');
        try {
            const response = await fetch('/api/wishlist_products');
            if (response.redirected) {
                window.location.href = response.url; // Redirect to login if not authenticated
                return Promise.reject('Redirect needed');
            }
            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Server returned ${response.status}: ${text}`);
            }
            const data = await response.json();
            console.log('Wishlist products response:', data);

            const currentProducts = data.products || [];
            
            // Clear the entire wishlist grid first
            wishlistGrid.innerHTML = '';
            
            if (currentProducts.length > 0) {
                // Create a new product grid container
                const newProductGrid = document.createElement('div');
                newProductGrid.className = 'product-grid';
                
                // Add all products to the new grid
                currentProducts.forEach(product => {
                    newProductGrid.insertAdjacentHTML('beforeend', createProductCard(product));
                });
                
                // Replace the old grid with the new one
                wishlistGrid.appendChild(newProductGrid);
                
                // Re-attach event listeners
                attachEventListenersToWishlistItems();
            } else {
                wishlistGrid.innerHTML = `
                    <div class="empty-wishlist">
                        <p>Your wishlist is empty</p>
                        <a href="/" class="shop-now-btn">Shop Now</a>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error fetching and rendering wishlist:', error);
            showNotification('Failed to load wishlist', 'error');
        }
    }

    // Function to attach event listeners to wishlist items (called after rendering)
    function attachEventListenersToWishlistItems() {
        // Re-attach remove from wishlist listeners
        document.querySelectorAll('.remove-from-wishlist').forEach(button => {
            button.removeEventListener('click', handleRemoveFromWishlist); // Prevent duplicate listeners
            button.addEventListener('click', handleRemoveFromWishlist);
        });

        // Re-attach add to cart listeners
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.removeEventListener('click', addToCartHandler); // Prevent duplicate listeners
            button.removeEventListener('click', goToCartHandler); // Prevent duplicate listeners
            if (button.classList.contains('added-to-cart')) {
                button.addEventListener('click', goToCartHandler);
            } else {
                button.addEventListener('click', addToCartHandler);
            }
        });

        // Re-attach product card click to detail page
        document.querySelectorAll('.product-card').forEach(card => {
            card.removeEventListener('click', handleProductCardClick); // Prevent duplicate listeners
            card.addEventListener('click', handleProductCardClick);
        });
    }

    // Handle remove from wishlist
    async function handleRemoveFromWishlist(e) {
        e.preventDefault();
        e.stopPropagation();
        const productId = this.dataset.productId;
        console.log('Removing product:', productId);
        try {
            const response = await fetch('/remove_from_wishlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ product_id: productId })
            });
            if (response.redirected) {
                window.location.href = response.url; // Redirect to login if not authenticated
                return Promise.reject('Redirect needed');
            }
            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Server returned ${response.status}: ${text}`);
            }
            const data = await response.json();
            console.log('Remove response:', data);
            if (data.success) {
                showNotification('Removed from wishlist!', 'success');
                // Re-fetch and render the entire wishlist to ensure consistency
                await fetchAndRenderWishlistGrid();
            }
        } catch (error) {
            console.error('Error removing from wishlist:', error);
            showNotification('Failed to remove from wishlist', 'error');
        }
    }

    // Handle product card click to detail page
    function handleProductCardClick(e) {
        if (!e.target.closest('.add-to-cart') && !e.target.closest('.remove-from-wishlist')) {
            const productId = this.dataset.productId;
            console.log('Navigating to product:', productId);
            window.location.href = `/rewear/product/${productId}`;
        }
    }

    // Initial setup and event listeners
    // Sync cart state on page load and on pageshow
    window.addEventListener('pageshow', (event) => {
        if (event.persisted || performance.navigation.type === 2) {
            console.log('Page loaded from cache (bfcache) or via history navigation. Re-fetching cart and wishlist.');
            fetchAndUpdateCartCount();
            fetchAndRenderWishlistGrid();
        }
    });
    
    // Initial fetch and render on DOMContentLoaded
    fetchAndUpdateCartCount();
    fetchAndRenderWishlistGrid(); // Call to populate wishlist on initial load

    // Function to fetch and update cart count in navbar
    function fetchAndUpdateCartCount() {
        fetch('/check_cart_status')
            .then(response => response.json())
            .then(data => {
                const cartBadge = document.querySelector('.cart-badge');
                const cartIcon = document.querySelector('.cart-icon');
                if (cartIcon) {
                    if (cartBadge) {
                        cartBadge.textContent = data.items.length;
                        if (data.items.length > 0) {
                            cartBadge.style.display = 'block';
                            cartIcon.classList.add('cart-has-items');
                        } else {
                            cartBadge.style.display = 'none';
                            cartIcon.classList.remove('cart-has-items');
                        }
                    } else if (data.items.length > 0) {
                        const badge = document.createElement('span');
                        badge.className = 'cart-badge';
                        badge.textContent = data.items.length;
                        cartIcon.appendChild(badge);
                        cartIcon.classList.add('cart-has-items');
                    }
                }
            });
    }

    // Add to cart handler
    function addToCartHandler(e) {
        e.preventDefault();
        e.stopPropagation();
        const button = this;
        if (button.classList.contains('added-to-cart') || button.disabled) return;
        const productId = button.closest('.product-card').dataset.productId;
        console.log('Adding to cart:', productId);
        addToCart(productId, 1, button);
    }

    // Go to cart handler
    function goToCartHandler(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Navigating to cart...');
        window.location.href = '/cart';
    }

    // Add to cart helper
    function addToCart(productId, quantity, btn) {
        console.log('Sending cart data:', { product_id: productId, quantity: quantity });
        fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url; // Redirect to login if not authenticated
                return Promise.reject('Redirect needed');
            }
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`Server returned ${response.status}: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Add to cart response:', data);
            if (data.success) {
                btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> <span class="cart-txt">Go to Cart</span>';
                btn.classList.add('added-to-cart');
                btn.disabled = false;
                btn.removeEventListener('click', addToCartHandler);
                btn.addEventListener('click', goToCartHandler);
                updateCartCount(true);
            } else if (data.redirect) {
                console.log('Redirecting to:', data.redirect);
                window.location.href = data.redirect;
            } else {
                showNotification('Failed to add to cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            showNotification('Failed to add to cart', 'error');
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ product_id: productId, quantity: quantity })
            })
            .then(response => response.text())
            .then(text => console.error('Add to cart response body:', text))
            .catch(err => console.error('Debug fetch failed:', err));
        });
    }

    // Notification function
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => { notification.classList.add('show'); }, 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => { notification.remove(); }, 300);
        }, 3000);
    }

    // Update cart count in navbar
    function updateCartCount(increment = true) {
        const cartIcon = document.querySelector('.cart-icon');
        let cartBadge = document.querySelector('.cart-badge');
        if (!cartIcon) return;
        if (!cartBadge) {
            cartBadge = document.createElement('span');
            cartBadge.className = 'cart-badge';
            cartBadge.textContent = '1';
            cartIcon.appendChild(cartBadge);
            cartIcon.classList.add('cart-has-items');
            return;
        }
        let currentCount = parseInt(cartBadge.textContent) || 0;
        if (increment) currentCount += 1;
        else currentCount = Math.max(0, currentCount - 1);
        cartBadge.textContent = currentCount;
        if (currentCount > 0) {
            cartBadge.style.display = 'block';
            cartIcon.classList.add('cart-has-items');
        } else {
            cartBadge.style.display = 'none';
            cartIcon.classList.remove('cart-has-items');
        }
    }
});