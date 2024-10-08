document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.edit-link').forEach((btn) => {
    btn.addEventListener('click', function () {
      const postId = this.getAttribute('data-post-id');
      editPost(postId);
    });
  });

  document.querySelectorAll('.delete-link').forEach((btn) => {
    btn.addEventListener('click', function () {
      const postId = this.getAttribute('data-post-id');
      const post = document.querySelector(`#post-${postId}`);
      post.style.animationPlayState = 'running';
      deletePost(postId);
    });
  });

  document.querySelectorAll('.button-like').forEach((btn) => {
    btn.addEventListener('click', function () {
      const postId = this.getAttribute('data-post-id');
      likePost(postId);
    });
  });
});

function likePost(postId) {
  const likebtn = document.querySelector(`#like-btn-${postId}`);
  const url = likebtn.getAttribute('data-url');
  fetch(url, {
    method: 'PUT',
  })
    .then((response) => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        return response.json();
      }
    })
    .then((data) => {
      if (data) {
        likebtn.classList.toggle('liked');
        const likeCount = document.querySelector(`#like-count-${postId}`);
        likeCount.innerHTML = data.likes;
      }
    })
    .catch((error) => console.error('Error', error));
}

function deletePost(postId) {
  fetch(`/delete_post/${postId}`, {
    method: 'DELETE',
  }).then((response) => {
    if (response.ok) {
      console.log('Post deleted');
    }
  });
}

function editPost(postId) {
  const contentElem = document.querySelector(`#post-content-${postId}`);

  const newText = document.createElement('textarea');
  newText.className = 'form-control';
  newText.innerHTML = contentElem.innerHTML;
  contentElem.replaceWith(newText);

  const saveButton = document.querySelector(`#save-btn-${postId}`);
  saveButton.style.display = 'block';

  saveButton.onclick = function () {
    const url = saveButton.getAttribute('data-url');
    fetch(url, {
      method: 'PUT',
      body: JSON.stringify({
        newcontent: newText.value,
      }),
    })
      .then((response) => {
        const newTextContentElement = document.createElement('p');
        newTextContentElement.id = `post-content-${postId}`;
        newTextContentElement.className = 'mt-3';
        if (!response.ok) {
          if (response.status == 403) {
            newTextContentElement.innerHTML = contentElem.innerHTML;
            newText.replaceWith(newTextContentElement);
            alert('You must be owner of the post to edit');
          } else {
            alert('An error occured while trying to save the post');
          }
        } else {
          newTextContentElement.innerHTML = newText.value;
          newText.replaceWith(newTextContentElement);
          saveButton.style.display = 'none';
        }
      })
      .catch((error) => console.error('Error', error));
  };
}
