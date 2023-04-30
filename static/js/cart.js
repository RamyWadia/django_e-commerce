var updateButtons = document.getElementsByClassName("update-cart")

for (i = 0; i < updateButtons.length; i++) {
    updateButtons[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log("productId:", productId, "Action:", action)

        console.log("USER:", user)
        if (user === "AnonymousUser") {
            console.log("user is not authenticated")
        } else {
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...')

    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
        .then((response) => {
            console.log(response)
            return response.json();
        })
        .then((data) => {
            console.log("data:", data)
            location.reload()
        });
}