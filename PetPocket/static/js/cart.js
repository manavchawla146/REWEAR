function updateQuantity(productId, delta) {
  const quantitySpan = document.querySelector(`.cart-item[data-product-id="${productId}"] .quantity-number`);
  let quantity = parseInt(quantitySpan.textContent) + delta;
  
  if (quantity < 1) return;
  
  // Get CSRF token from meta tag
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  
  fetch('/update_cart_item', {
      method: 'PUT',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({product_id: productId, quantity: quantity})
  }).then(response => response.json())
  .then(data => {
      if (data.success) {
          // Update the quantity display
          quantitySpan.textContent = quantity;
          
          // Update subtotal, tax, shipping, and total
          if (data.cart_total) {
              document.querySelector('.subtotal').innerHTML = `₹${data.cart_total.subtotal.toFixed(2)}`;
              document.querySelector('.tax').innerHTML = `₹${data.cart_total.tax.toFixed(2)}`;
              document.querySelector('.shipping').innerHTML = `₹${data.cart_total.shipping.toFixed(2)}`;
              document.querySelector('.total-value').innerHTML = `₹${data.cart_total.total.toFixed(2)}`;
          } else {
              location.reload();
          }
          
          // Update cart count in navbar with the total from server
          if (data.cart_count !== undefined) {
              updateNavbarCartCountAbsolute(data.cart_count);
          }
      }
  });
}

// Function to set the absolute cart count
function updateNavbarCartCountAbsolute(totalCount) {
    const cartBadge = document.querySelector('.cart-badge');
    const cartIcon = document.querySelector('.cart-icon');
    
    if (!cartIcon) return;
    
    if (cartBadge) {
        // Update existing badge
        cartBadge.textContent = totalCount;
        
        if (totalCount > 0) {
            cartIcon.classList.add('cart-has-items');
        } else {
            cartIcon.classList.remove('cart-has-items');
        }
    } else if (totalCount > 0) {
        // Create new badge
        const badge = document.createElement('span');
        badge.className = 'cart-badge';
        badge.textContent = totalCount;
        cartIcon.appendChild(badge);
        cartIcon.classList.add('cart-has-items');
    }
}

function removeItem(productId) {
  // Get CSRF token from meta tag
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

  fetch('/remove_from_cart', {
      method: 'DELETE',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({product_id: productId})
  }).then(response => response.json())
  .then(data => {
      if (data.success) {
          // Remove the item from the display
          const item = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
          if (item) {
              item.remove();
              
          }
          
          // Update cart totals
          if (data.cart_total) {
              document.querySelector('.subtotal').innerHTML = `₹${data.cart_total.subtotal.toFixed(2)}`;
              document.querySelector('.tax').innerHTML = `₹${data.cart_total.tax.toFixed(2)}`;
              document.querySelector('.shipping').innerHTML = `₹${data.cart_total.shipping.toFixed(2)}`;
              // Update the selector here too
              document.querySelector('.total-value').innerHTML = `₹${data.cart_total.total.toFixed(2)}`;
              
              // Update cart count in navbar
              const cartBadge = document.querySelector('.cart-badge');
              if (cartBadge) {
                  const currentItems = parseInt(cartBadge.textContent) || 0;
                  if (currentItems > 0) {
                      const newCount = currentItems - 1;
                      cartBadge.textContent = newCount;
                      
                      if (newCount === 0) {
                          document.querySelector('.cart-icon').classList.remove('cart-has-items');
                          cartBadge.remove();
                      }
                  }
              }
              
              // Check if cart is now empty
              const cartItems = document.querySelectorAll('.cart-item');
              if (cartItems.length === 0) {
                  // Hide cart summary
                  const cartSummary = document.querySelector('.cart-summary');
                  if (cartSummary) cartSummary.style.display = 'none';
                  // Show empty cart message
                  let emptyMsg = document.getElementById('empty-cart-message');
                  if (emptyMsg) {
                      emptyMsg.style.display = 'flex';
                  } else {
                      // fallback: reload if not found
                      location.reload();
                  }
                  // Update cart header count to 0
                  document.querySelector('.cart-header h1').textContent = 'Shopping Cart (0 items)';
                  // Update navbar cart badge to 0 or hide
                  const cartBadge = document.querySelector('.cart-badge');
                  const cartIcon = document.querySelector('.cart-icon');
                  if (cartBadge) {
                      cartBadge.textContent = 0;
                      cartBadge.style.display = 'none';
                  }
                  if (cartIcon) {
                      cartIcon.classList.remove('cart-has-items');
                  }
                  // Always update the navbar cart count after cart is empty
                  if (typeof fetchAndUpdateCartCount === 'function') {
                      fetchAndUpdateCartCount();
                  }
              }
          } else {
              // If no cart total data is returned, simply reload the page
              location.reload();
          }
      }
  });
}

// Update cart header count on load
document.addEventListener('DOMContentLoaded', () => {
  const cartItems = document.querySelectorAll('.cart-item');
  const itemCount = cartItems.length;
  document.querySelector('.cart-header h1').textContent = 
      `Shopping Cart (${itemCount} ${itemCount === 1 ? 'item' : 'items'})`;
});

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

// Update cart count on pageshow (for browser back/forward)
window.addEventListener('pageshow', fetchAndUpdateCartCount);