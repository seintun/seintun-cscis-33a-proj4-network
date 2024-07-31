// Get cookie for crsf token
// https://www.w3schools.com/js/js_cookies.asp
function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function handleEditPost(postId) {
    const updatedContent = document.getElementById(`edit_post_${postId}`).value;
    const contentElement = document.getElementById(`post_content_${postId}`);
    const data = {
        content: updatedContent
    };

    fetch(`/edit_post/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(result => {
            contentElement.textContent = result.data;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

// Function to handle like button
// Toggle like button and icon and update like count
function handleLike(postId, isLiked) {
    const likeButton = document.getElementById(`like_root_${postId}`);
    const likeIcon = document.getElementById(`like_icon_${postId}`);
    const likeCount = parseInt(likeIcon.textContent, 10);

    if (isLiked) {
        fetch(`/unlike_post/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
        })
            .then(response => response.json())
            .then(result => {
                likeButton.innerHTML = `
                    <button 
                        class="btn btn-outline-primary"
                        id="${postId}"
                        onclick="handleLike('${postId}', false)"
                    >
                        <i 
                            class="bi bi-heart"
                            id="like_icon_${postId}"
                        >${likeCount - 1}</i>
                    </button>`;
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    } else {
        fetch(`/like_post/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
        })
            .then(response => response.json())
            .then(result => {
                likeButton.innerHTML = `
                    <button 
                        class="btn btn-primary"
                        id="${postId}"
                        onclick="handleLike('${postId}', true)"
                    >
                        <i 
                            class="bi bi-heart-fill"
                            id="like_icon_${postId}"
                        >${likeCount + 1}</i>
                    </button>`;
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }
}