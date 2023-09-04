// network.js

// Function to handle the follow toggle
function handleFollowToggle(userId) {
  // Send an AJAX request to the follow_toggle URL
  fetch(`/profile/${userId}/`)
    .then((response) => response.json())
    .then((data) => {
      // Update the follow button based on the response
      const followButton = document.getElementById(`follow-button-${userId}`);
      if (data.is_following) {
        followButton.classList.add("btn-danger");
        followButton.classList.remove("btn-outline-danger");
        followButton.textContent = "Unfollow";
      } else {
        followButton.classList.remove("btn-danger");
        followButton.classList.add("btn-outline-danger");
        followButton.textContent = "Follow";
      }
    })
    .catch((error) => console.log(error));
}
