document.addEventListener('DOMContentLoaded', function () {
  const profileDetails = document.querySelector('.profile-details');
  const editButton = document.querySelector('.edit-button');
  let isEditing = false;
  const originalDetails = {};

  // Function to create an input element
  function createInput(value, type = 'text') {
    const input = document.createElement('input');
    input.type = type;
    input.value = value;
    input.classList.add('editable-field');
    return input;
  }

  // Function to transform text to input
  function transformToEditable() {
    const detailSections = document.querySelectorAll('.detail-section');
    detailSections.forEach(section => {
      const paragraphs = section.querySelectorAll('p');
      paragraphs.forEach(p => {
        const label = p.querySelector('strong').textContent;
        const value = p.textContent.replace(label, '').trim();
        originalDetails[label] = value;

        const input = createInput(value);
        input.dataset.label = label;

        p.innerHTML = '';
        p.appendChild(document.createTextNode(label));
        p.appendChild(input);
      });
    });
  }

  // Function to save the edited details
  function saveEditedDetails() {
    const updatedData = {};
    const detailSections = document.querySelectorAll('.detail-section');
    
    detailSections.forEach(section => {
      const paragraphs = section.querySelectorAll('p');
      paragraphs.forEach(p => {
        const input = p.querySelector('input.editable-field');
        if (input) {
          const label = input.dataset.label;
          const newValue = input.value;
          updatedData[label.toLowerCase().replace(':', '')] = newValue;

          p.innerHTML = `<strong>${label}</strong> ${newValue}`;
        }
      });
    });

    // Send updated data to server
    fetch('/update_profile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showNotification('Profile updated successfully!', 'success');
      } else {
        showNotification('Failed to update profile', 'error');
        revertChanges();
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showNotification('An error occurred', 'error');
      revertChanges();
    });
  }

  // Function to revert changes if update fails
  function revertChanges() {
    const detailSections = document.querySelectorAll('.detail-section');
    detailSections.forEach(section => {
      const paragraphs = section.querySelectorAll('p');
      paragraphs.forEach(p => {
        const input = p.querySelector('input.editable-field');
        if (input) {
          const label = input.dataset.label;
          p.innerHTML = `<strong>${label}</strong> ${originalDetails[label]}`;
        }
      });
    });
  }

  // Function to show notification
  function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);

    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }

  // Event listener for the edit button
  editButton.addEventListener('click', function () {
    isEditing = !isEditing;
    if (isEditing) {
      transformToEditable();
      editButton.innerHTML = '<span class="material-symbols-outlined">save</span>Save Profile';
      editButton.style.backgroundColor = "#4CAF50";
    } else {
      saveEditedDetails();
      editButton.innerHTML = '<span class="material-symbols-outlined">edit</span>Edit Profile';
      editButton.style.backgroundColor = "#46f27a";
    }
  });

  // Handle cancel editing with Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && isEditing) {
      isEditing = false;
      revertChanges();
      editButton.innerHTML = '<span class="material-symbols-outlined">edit</span>Edit Profile';
      editButton.style.backgroundColor = "#46f27a";
    }
  });
});