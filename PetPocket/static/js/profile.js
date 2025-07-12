document.addEventListener('DOMContentLoaded', function () {
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabPanes = document.querySelectorAll('.tab-pane');

  // Tab switching logic
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabId = button.getAttribute('data-tab');
      
      // Remove active class from all buttons and panes
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));
      
      // Add active class to clicked button
      button.classList.add('active');
      
      // Show the corresponding tab pane
      const targetPane = document.getElementById(tabId);
      if (targetPane) {
        targetPane.classList.add('active');
      }
    });
  });

  // Profile editing functionality
  const editButton = document.getElementById('edit-profile-btn');
  const displayDiv = document.getElementById('personal-info-display');
  const editForm = document.getElementById('personal-info-form');
  const cancelButton = document.getElementById('cancel-edit-btn');
  
  // Edit profile button handling
  if (editButton && displayDiv && editForm) {
    editButton.addEventListener('click', function() {
      // Populate form fields with current user data
      const infoValues = document.querySelectorAll('.info-value');
      
      if (infoValues.length >= 3) {
        const usernameValue = infoValues[0].textContent.trim();
        const emailValue = infoValues[1].textContent.trim();
        const phoneValue = infoValues[2].textContent.trim();
        
        // Safely populate form fields
        const usernameInput = document.querySelector('#personal-info-form input[name="username"]');
        const emailInput = document.querySelector('#personal-info-form input[name="email"]');
        const phoneInput = document.querySelector('#personal-info-form input[name="phone"]');
        
        if (usernameInput) usernameInput.value = usernameValue;
        if (emailInput) emailInput.value = emailValue;
        if (phoneInput) phoneInput.value = phoneValue !== 'Not set' ? phoneValue : '';
      }
      
      // Toggle visibility
      toggleEditForm();
    });
  }

  // Cancel button handling
  if (cancelButton) {
    cancelButton.addEventListener('click', function() {
      toggleEditForm();
      // Clear any error messages
      clearFlashMessages();
    });
  }

  // Form submission handling
  if (editForm) {
    editForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Clear previous messages
      clearFlashMessages();
      
      const submitButton = editForm.querySelector('button[type="submit"]');
      if (!submitButton) {
        console.error('Submit button not found');
        return;
      }
      
      // Disable submit button and show loading state
      const originalText = submitButton.textContent;
      submitButton.disabled = true;
      submitButton.textContent = 'Saving...';

      const formData = new FormData(editForm);
      const data = {
        username: formData.get('username')?.trim(),
        email: formData.get('email')?.trim(),
        phone: formData.get('phone')?.trim() || null
      };

      // Basic client-side validation
      if (!data.username || !data.email) {
        showFlashMessage('Username and email are required.', 'danger');
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data.email)) {
        showFlashMessage('Please enter a valid email address.', 'danger');
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        return;
      }

      // Phone validation (if provided)
      if (data.phone && data.phone.length > 0) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(data.phone.replace(/[\s\-\(\)]/g, ''))) {
          showFlashMessage('Please enter a valid phone number.', 'danger');
          submitButton.disabled = false;
          submitButton.textContent = originalText;
          return;
        }
      }

      fetch('/edit-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
      })
        .then(response => {
          if (response.status === 403) {
            handleCsrfError();
            throw new Error('CSRF token validation failed');
          }
          if (!response.ok) {
            return response.json().then(err => {
              throw new Error(err.message || `HTTP error! status: ${response.status}`);
            });
          }
          return response.json();
        })
        .then(result => {
          if (result.success) {
            // Update the display values
            updateDisplayValues(result.user);
            
            // Update the welcome message
            updateWelcomeMessage(result.user.username);
            
            // Show success message
            showFlashMessage(result.message || 'Profile updated successfully!', 'success');
            
            // Hide form and show display after a short delay
            setTimeout(() => {
              toggleEditForm();
            }, 1000);
          } else {
            // Handle server-side validation errors
            showFlashMessage(result.message || 'An error occurred while updating your profile.', 'danger');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          let errorMessage = 'An unexpected error occurred. Please try again.';
          
          if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Network error. Please check your connection and try again.';
          } else if (error.message.includes('403')) {
            errorMessage = 'Access denied. Please refresh the page and try again.';
          } else if (error.message.includes('CSRF')) {
            errorMessage = 'Session expired. Please refresh the page and try again.';
          } else {
            // Use the server's error message if available
            errorMessage = error.message;
          }
          
          showFlashMessage(errorMessage, 'danger');
        })
        .finally(() => {
          submitButton.disabled = false;
          submitButton.textContent = originalText;
        });
    });
  }

  // Helper Functions
  function toggleEditForm() {
    if (displayDiv && editForm) {
      const isFormVisible = editForm.style.display === 'block';
      
      if (isFormVisible) {
        // Hide form, show display
        editForm.style.display = 'none';
        displayDiv.style.display = 'block';
      } else {
        // Show form, hide display
        displayDiv.style.display = 'none';
        editForm.style.display = 'block';
      }
    }
  }

  function updateDisplayValues(user) {
    const infoValues = document.querySelectorAll('.info-value');
    if (infoValues.length >= 3) {
      infoValues[0].textContent = user.username;
      infoValues[1].textContent = user.email;
      infoValues[2].textContent = user.phone || 'Not set';
    }
  }

  function updateWelcomeMessage(username) {
    const welcomeHeader = document.querySelector('.profile-hero h2');
    if (welcomeHeader) {
      welcomeHeader.textContent = `Welcome, ${username}`;
    }
  }

  function showFlashMessage(message, type) {
    const flashMessages = document.getElementById('flash-messages');
    if (!flashMessages) {
      console.warn('Flash messages container not found');
      return;
    }
    
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash-message flash-${type}`;
    flashDiv.textContent = message;
    
    // Add some basic styling if not already styled
    flashDiv.style.padding = '10px';
    flashDiv.style.margin = '10px 0';
    flashDiv.style.borderRadius = '4px';
    flashDiv.style.fontSize = '14px';
    
    if (type === 'success') {
      flashDiv.style.backgroundColor = '#d4edda';
      flashDiv.style.color = '#155724';
      flashDiv.style.border = '1px solid #c3e6cb';
    } else if (type === 'danger') {
      flashDiv.style.backgroundColor = '#f8d7da';
      flashDiv.style.color = '#721c24';
      flashDiv.style.border = '1px solid #f5c6cb';
    }
    
    flashMessages.appendChild(flashDiv);
    
    // Auto-hide after 5 seconds for errors, 3 for success
    const hideTimeout = type === 'danger' ? 5000 : 3000;
    setTimeout(() => {
      if (flashDiv.parentNode) {
        flashDiv.remove();
      }
    }, hideTimeout);
  }

  function clearFlashMessages() {
    const flashMessages = document.getElementById('flash-messages');
    if (flashMessages) {
      flashMessages.innerHTML = '';
    }
  }

  function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (!metaTag) {
      console.error('CSRF token meta tag not found');
      return '';
    }
    return metaTag.getAttribute('content');
  }

  // Add this function to handle CSRF errors
  function handleCsrfError() {
    showFlashMessage('Session expired. Please refresh the page and try again.', 'danger');
    setTimeout(() => {
      window.location.reload();
    }, 2000);
  }

  // Make functions globally available if needed
  window.toggleEditForm = toggleEditForm;
  window.showFlashMessage = showFlashMessage;

  // Add Item Form Handling
  const addItemForm = document.getElementById('add-item-form');
  if (addItemForm) {
    addItemForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const submitButton = addItemForm.querySelector('button[type="submit"]');
      if (!submitButton) {
        console.error('Submit button not found');
        return;
      }
      
      // Disable submit button and show loading state
      const originalText = submitButton.textContent;
      submitButton.disabled = true;
      submitButton.textContent = 'Adding Item...';

      const formData = new FormData(addItemForm);
      
      // Get CSRF token
      const csrfToken = document.querySelector('meta[name="csrf-token"]');
      if (csrfToken) {
        formData.append('csrf_token', csrfToken.getAttribute('content'));
      }

      // Submit to new endpoint
      fetch('/add-product', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showFlashMessage(data.message, 'success');
          addItemForm.reset();
          
          // Reload page to show the new item
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        } else {
          showFlashMessage(data.message, 'danger');
        }
      })
      .catch(error => {
        console.error('Error adding item:', error);
        showFlashMessage('An error occurred while adding the item. Please try again.', 'danger');
      })
      .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      });
    });
  }

  // Helper function to show messages
  function showMessage(message, type) {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageEl.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 1000;
      max-width: 300px;
      padding: 15px;
      border-radius: 5px;
      background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
      color: ${type === 'success' ? '#155724' : '#721c24'};
      border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};
    `;
    messageEl.textContent = message;
    
    // Add to page
    document.body.appendChild(messageEl);
    
    // Remove after 3 seconds
    setTimeout(() => {
      if (messageEl.parentNode) {
        messageEl.parentNode.removeChild(messageEl);
      }
    }, 3000);
  }
});