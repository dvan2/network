document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.edit-link').forEach((btn) => {
    btn.addEventListener('click', function () {
      const postId = this.getAttribute('data-post-id');
      editPost(postId);
    });
  });
});

function editPost(postId) {
  console.log('Edit', postId);
  const contentElem = document.querySelector(`#post-content-${postId}`);

  const newText = document.createElement('textarea');
  newText.className = 'form-control';
  newText.innerHTML = contentElem.innerHTML;
  contentElem.replaceWith(newText);

  const saveButton = document.createElement('button');
  saveButton.className = 'btn btn-success mt-2';
  saveButton.innerHTML = 'Save';
  const editBtnElem = document.querySelector(`#edit-btn-${postId}`);
  editBtnElem.replaceWith(saveButton);

  saveButton.onclick = function () {
    saveButton.replaceWith(editBtnElem);
    fetch(`edit/${postId}`, {
      method: 'PUT',
      body: JSON.stringify({
        newcontent: newText.value,
      }),
    })
      .then((response) => {
        const newTextContentElement = document.createElement('p');
        newTextContentElement.id = `post-content-${postId}`;
        if (!response.ok) {
          newTextContentElement.innerHTML = contentElem.innerHTML;
          newText.replaceWith(newTextContentElement);
          alert('You must be owner of the post to edit');
        } else {
          newTextContentElement.innerHTML = newText.value;
          newText.replaceWith(newTextContentElement);
        }
      })
      .catch((error) => console.error('Error', error));
  };
}
