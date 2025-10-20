document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.feed-card').forEach(card => {
    const likeBtn = card.querySelector('.like-btn');
    const likeCount = card.querySelector('.like-count');
    const commentBtn = card.querySelector('.comment-btn');
    const commentsSection = card.querySelector('.comments-section');
    const addCommentBtn = card.querySelector('.add-comment-btn');
    const commentInput = card.querySelector('.comment-input');
    const commentsList = card.querySelector('.comments-list');

    let liked = false;

    likeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      let count = parseInt(likeCount.textContent);

      if (!liked) {
        liked = true;
        count++;
        likeBtn.classList.add('liked');
        likeBtn.innerHTML = `❤️<span class="like-count">${count}</span>`;
      } else {
        liked = false;
        count = Math.max(0, count - 1); 
        likeBtn.classList.remove('liked');
        likeBtn.innerHTML = `❤️<span class="like-count">${count}</span>`;
      }
    });

    commentBtn.addEventListener('click', (e) => {
      e.preventDefault();
      commentsSection.style.display = commentsSection.style.display === 'none' ? 'flex' : 'none';
      commentInput.focus();
    });

    const addComment = () => {
      const text = commentInput.value.trim();
      if (text) {
        const commentDiv = document.createElement('div');
        commentDiv.classList.add('comment');

        const usernameSpan = document.createElement('span');
        usernameSpan.classList.add('comment-username');
        usernameSpan.textContent = 'You: ';

        const textSpan = document.createElement('span');
        textSpan.classList.add('comment-text');
        textSpan.textContent = text;

        const timeSpan = document.createElement('span');
        timeSpan.classList.add('comment-time');
        timeSpan.textContent = ' • just now';

        commentDiv.appendChild(usernameSpan);
        commentDiv.appendChild(textSpan);
        commentDiv.appendChild(timeSpan);

        commentsList.appendChild(commentDiv);
        commentInput.value = '';
      }
    };

    addCommentBtn.addEventListener('click', (e) => {
      e.preventDefault();
      addComment();
    });

    commentInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addComment();
      }
    });
  });
});
